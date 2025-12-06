import os
import json
import logging
import time
from typing import Dict, Any
from functools import lru_cache, wraps
from google import genai
from config.config import GOOGLE_API_KEY
from .custom_exceptions import LLMAPIError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def retry(exceptions, tries=3, delay=1, backoff=2):
    """Retry decorator with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"{e}, Retrying in {mdelay} seconds...")
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return func(*args, **kwargs)
        return wrapper
    return decorator


class LLMClient:
    def __init__(self) -> None:
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variable")

        self._client = genai.Client(api_key=GOOGLE_API_KEY)
        self._cache_file = "cache_result/smart_qa_cache.json"
        self._load_cache()

   
    def _load_cache(self):
        if os.path.exists(self._cache_file):
            with open(self._cache_file, "r") as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def _save_cache(self):
        with open(self._cache_file, "w") as f:
            json.dump(self.cache, f, indent=2)

    def clear_cache(self):
        self.cache = {}
        self._save_cache()
        logger.info("Cache cleared successfully.")


    @retry(LLMAPIError, tries=3, delay=2, backoff=2)
    def _call_api(self, prompt: str) -> str:
        logger.info("API call to LLM")

        try:
            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            api_result = response.text  # this is the string from the LLM

            # Save to persistent cache
            self.cache[prompt] = api_result
            self._save_cache()

            return api_result

        except Exception as e:
            raise LLMAPIError(f"LLM API failure: {e}")

 
    @lru_cache()
    def summarize(self, text: str) -> str:
        logger.info("Calling summarize method...")

        prompt = f"Summarize the following text:\n\n{text}"
        
        logging.info('Checking cache for summarize method')
        if prompt in self.cache:
            logger.info("Prompt found in persistent cache result for summarize method")
            return self.cache[prompt]

        logger.info("Prompt not found in the cached result, calling LLM API...")
        return self._call_api(prompt)

   
    @lru_cache()
    def ask(self, context: str, question: str) -> str:
        logger.info("Calling ask method...")

        prompt = (
            f"Context:\n{context}\n\n"
            f"Question: {question}\n"
            f"Answer strictly based on the context."
        )

        logging.info('Checking cache for ask  method')
        if prompt in self.cache:
            logger.info("Prompt found in persistent cache result for ask method")
            return self.cache[prompt]

        logging.info("Prompt not found in the cached result, calling LLM API...")
        return self._call_api(prompt)


    def extract_entities(self, text: str) -> Dict[str, Any]:
        prompt = (
            "Extract entities from this text. Return ONLY a JSON object with keys:\n"
            "People, Dates, Locations.\n\n"
            f"Text:\n{text}"
        )

        raw = self._call_api(prompt)

        
        if isinstance(raw, (dict, list)):
            return raw

        if not isinstance(raw, str):
            raise LLMAPIError("LLM returned unsupported data type.")

        try:
            # Remove code fences like ```json ... ```
            cleaned = raw.strip()
            for fence in ["```json", "```", "`"]:
                if cleaned.startswith(fence):
                    cleaned = cleaned[len(fence):].strip()
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3].strip()

            # Extract JSON between first { and last }
            json_start = cleaned.find("{")
            json_end = cleaned.rfind("}") + 1
            json_text = cleaned[json_start:json_end]

            return json.loads(json_text)

        except Exception as e:
            raise LLMAPIError(f"Failed to parse JSON entities: {e}")
