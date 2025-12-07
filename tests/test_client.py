import os
from unittest.mock import patch


def test_ask_caches_result(mock_client):
    # Call ask twice with same input
    r1 = mock_client.ask("Alice went to Paris.", "Where did she go?")
    r2 = mock_client.ask("Alice went to Paris.", "Where did she go?")

    assert r1 == r2
    mock_client._call_api.assert_called_once()


def test_ask_cache_different_questions(mock_client):
    r1 = mock_client.ask("Alice went to Paris.", "Where did she go?")
    r2 = mock_client.ask("Alice went to Paris.", "When did she go?")

    assert r1 == "mocked-response"
    assert r2 == "mocked-response"
    assert mock_client._call_api.call_count == 2


def test_summarize_caches_result(mock_client):
    text = "Alice went to Paris in 2020 for a research trip."
    r1 = mock_client.summarize(text)
    r2 = mock_client.summarize(text)

    assert r1 == r2
    mock_client._call_api.assert_called_once()

def test_extract_entities_returns_json(mock_client_entities):
    text = "Alice went to Paris in 2020."
    result = mock_client_entities.extract_entities(text)

    # result should be parsed JSON (dict)
    assert isinstance(result, dict)
    assert result["people"] == ["Alice"]
    assert result["dates"] == ["2020"]
    assert result["locations"] == ["Paris"]

    mock_client_entities._call_api.assert_called_once()


def test_extract_entities_caches_result(mock_client_entities):
    text = "Alice went to Paris in 2020."

    r1 = mock_client_entities.extract_entities(text)
  
    mock_client_entities._call_api.assert_called_once()



def test_summarize_large_file(mock_client):
    # Load large text from file
    path =  "tests/data/pytest_file.txt"
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    result = mock_client.summarize(text)
    assert result == "mocked-response"
    mock_client._call_api.assert_called_once()


def test_clear_cache(tmp_path):
    temp_file = tmp_path / "cache.json"

    from smart_qa.client import LLMClient
    client = LLMClient()

    # Force the cache file to point to our temp file
    client._cache_file = str(temp_file)

    # Put something in cache and save
    client.cache["test-prompt"] = "test-response"
    client._save_cache()

    # Clear cache
    client.clear_cache()

    # Reload after clearing
    client._load_cache()

    assert client.cache == {}

