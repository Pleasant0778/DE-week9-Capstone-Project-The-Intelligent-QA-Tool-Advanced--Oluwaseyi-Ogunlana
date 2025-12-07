# Smart Q&A Tool (Advanced) - Capstone Project

## Overview

**Smart Q&A Tool** is a production-ready Python library designed to work with Google Gemini LLM. It enables:

* Summarization of large text documents.
* Context-based question answering.
* Structured entity extraction (People, Dates, Locations).

This project implements caching, retry logic, CLI support, and structured JSON output for easy integration into downstream applications.

**Role:** Senior AI Engineer at Data Epic Solutions
**Goal:** Build a robust, cost-effective, and "bulletproof" AI client.

---

## Features

1. **Summarization**

   * Quickly summarize large texts.
   * Returns concise output with caching to avoid repeated API calls.

2. **Question Answering**

   * Ask questions based strictly on the provided context.
   * Uses caching to save costs and improve response speed.

3. **Entity Extraction**

   * Extract People, Dates, and Locations in **JSON format**.
   * Automatically cleans Markdown or other formatting returned by the API.

4. **Caching**

   * Persistent JSON cache to store previous API responses.
   * In-memory `lru_cache` to optimize repeated function calls.

5. **Retry & Resilience**

   * Automatic retry on API failures using **exponential backoff**.
   * Custom exception handling (`LLMAPIError`).

6. **CLI Support**

   * Load text from file.
   * Save output to file.
   * Clear cache.
   * Run `summarize`, `ask`, or `extract-entities` directly from terminal.

---

---

## Workflow Diagram

**Flow of operations:**

```text
User Input (text/file)
        |
        v
   Check Persistent Cache
        |
  +-----+-----+
  |           |
Cache Hit   Cache Miss
  |           |
Return      Call Gemini LLM API
Cached       |
Result       v
        Save Response to Cache
             |
             v
          Return Result
```

* **Step 1:** User provides text or file input.
* **Step 2:** Library checks persistent JSON cache.
* **Step 3a:** If cache hit → Return cached result instantly.
* **Step 3b:** If cache miss → Make API call to Gemini.
* **Step 4:** Save result to persistent cache for future calls.
* **Step 5:** Return result to user.

---


## Installation

**Using Poetry:**

```bash
# Install poetry if not already installed
pip install poetry


# Activate virtual environment
poetry env activate
```

---

## Configuration

1. Create a `.env` file in the config folder root:

```
GOOGLE_API_KEY=<your_google_gemini_api_key>
```

2. The API key will be automatically loaded by `LLMClient`.

---

## Usage

### Command-Line Interface

```bash
# To summarize a file
(smartqavenv) PS C:\Users\Personal\data_epic\week9_capstone_project\smart_qa_project> poetry run python main.py --file data\test_file.txt --summarize                                     
2025-12-07 14:46:42,235 - INFO - Calling summarize method...
2025-12-07 14:46:42,236 - INFO - Checking cache for summarize method
2025-12-07 14:46:42,236 - INFO - Prompt not found in the cached result, calling LLM API...
2025-12-07 14:46:42,236 - INFO - API call to LLM
2025-12-07 14:46:42,236 - INFO - AFC is enabled with max remote calls: 10.
2025-12-07 14:46:47,085 - INFO - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"

=== OUTPUT ===
In July 2020, Alice Johnson traveled to Paris for a business conference where she met with Thomas Okafor and Dr. Emily Brown. Their discussions focused on global health research, vaccine development, and AI diagnostic tools. The group also discussed future partnerships planned for 2021-2022, ultimately deeming the trip a success for the entire research team.

# To ask a question
(smartqavenv) PS C:\Users\Personal\data_epic\week9_capstone_project\smart_qa_project> poetry run  python main.py --ask "Alice went to Paris in 2020." "Where did Alice go?"
2025-12-07 14:44:37,028 - INFO - Calling ask method...
2025-12-07 14:44:37,030 - INFO - Checking cache for ask  method
2025-12-07 14:44:37,030 - INFO - Prompt found in persistent cache result for ask method

=== OUTPUT ===
Paris

# To extract entities and save
(smartqavenv) PS C:\Users\Personal\data_epic\week9_capstone_project\smart_qa_project> poetry run python main.py --file data\test_file.txt --extract-entities --save test_entity_result.txt
2025-12-07 14:45:34,207 - INFO - API call to LLM
2025-12-07 14:45:34,207 - INFO - AFC is enabled with max remote calls: 10.
2025-12-07 14:45:37,393 - INFO - HTTP Request: POST https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent "HTTP/1.1 200 OK"

=== OUTPUT ===
{'People': ['Alice Johnson', 'Thomas Okafor', 'Dr. Emily Brown'], 'Dates': ['July 2020', '2021', '2022'], 'Locations': ['Paris', 'Nigeria', 'University of London', 'Eiffel Tower']}

Output saved to test_entity_result.txt

 
# Clear cache
(smartqavenv) PS C:\Users\Personal\data_epic\week9_capstone_project\smart_qa_project> poetry run python main.py --clear-cache
2025-12-07 14:46:08,245 - INFO - Cache cleared successfully.
Cache cleared successfully.
```


## Testing

* Unit tests use `pytest` and `pytest-mock`.
* Sample test data stored in `tests/data/`.
* Ensure **100% test coverage** using:

```bash
(smartqavenv) PS C:\Users\Personal\data_epic\week9_capstone_project\smart_qa_project> pytest --cov=smart_qa
======================================================================================================= test session starts ========================================================================================================
platform win32 -- Python 3.13.6, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Users\Personal\data_epic\week9_capstone_project\smart_qa_project
configfile: pyproject.toml
plugins: anyio-4.12.0, cov-7.0.0, mock-3.15.1
collected 7 items                                                                                                                                                                                                                   

tests\test_client.py .......                                                                                                                                                                                                  [100%]

========================================================================================================== tests coverage ========================================================================================================== 
_________________________________________________________________________________________ coverage: platform win32, python 3.13.6-final-0 __________________________________________________________________________________________ 

Name                            Stmts   Miss  Cover
---------------------------------------------------
smart_qa\__init__.py                0      0   100%
smart_qa\client.py                 97     40    59%
smart_qa\custom_exceptions.py       2      0   100%
---------------------------------------------------
TOTAL                              99     40    60%
======================================================================================================== 7 passed in 7.52s ========================================================================================================= 
(smartqavenv) PS C:\Users\Personal\data_epic\week9_capstone_project\smart_qa_project> 
```

---

## Dependencies

* `google-generativeai` (main API client)
* `pytest`, `pytest-mock`, `pytest-cov` (development)
* `poetry` (dependency management)

---

## Logging & Observability

* Logs every API hit and cache hit.
* Provides info on retries and API failures.
* Helps monitor cost and debug API interactions.

---

## Error Handling

* `LLMAPIError` handles API failures.
* Automatic retries with exponential backoff for network/API issues.
* Ensures robustness for production-grade applications.

---

## Notes

* **Caching** is implemented using both `lru_cache` for memory and JSON for persistent storage.
* API responses are sanitized to ensure **valid JSON** for structured entity extraction.
* CLI is designed for **ease of use** without touching Python code.

---

