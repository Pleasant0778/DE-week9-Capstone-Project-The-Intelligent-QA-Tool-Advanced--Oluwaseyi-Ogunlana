import pytest
import os
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def mock_env():
    """Ensure GOOGLE_API_KEY exists BEFORE any LLMClient import happens."""
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "fake-key"}):
        yield


@pytest.fixture
def mock_client():
    """Create client with generic mock API result."""
    from smart_qa.client import LLMClient   # ← import AFTER env patch

    client = LLMClient()
    client._call_api = MagicMock(return_value="mocked-response")
    return client


@pytest.fixture
def mock_client_entities():
    """Client for extract_entities tests."""
    from smart_qa.client import LLMClient   # ← import AFTER env patch

    client = LLMClient()

    def fake_entity_api(prompt):
        return {
            "people": ["Alice"],
            "dates": ["2020"],
            "locations": ["Paris"],
        }

    client._call_api = MagicMock(side_effect=fake_entity_api)
    return client
