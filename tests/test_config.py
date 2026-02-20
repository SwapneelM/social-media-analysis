"""Tests for collectors.config module."""

import os
import pytest
from unittest.mock import patch


def test_config_constants():
    """Verify that key constants are set to expected values."""
    from collectors.config import (
        MAX_POSTS, RETRY_MAX_RETRIES, CONFIDENCE_AUTO_ACCEPT,
        CONFIDENCE_NEEDS_REVIEW, BRIGHTDATA_FACEBOOK_DATASET_ID,
        BRIGHTDATA_TIKTOK_DATASET_ID,
    )
    assert MAX_POSTS == 25
    assert RETRY_MAX_RETRIES == 5
    assert CONFIDENCE_AUTO_ACCEPT == 0.85
    assert CONFIDENCE_NEEDS_REVIEW == 0.60
    assert BRIGHTDATA_FACEBOOK_DATASET_ID == "gd_lkaxegm826bjpoo9m5"
    assert BRIGHTDATA_TIKTOK_DATASET_ID == "gd_lu702nij2f790tmv9h"


def test_config_endpoints():
    """Verify that API endpoint URLs are well-formed."""
    from collectors.config import (
        TWITTER_SEARCH_URL, BRIGHTDATA_TRIGGER_URL,
        OPENROUTER_CHAT_URL,
    )
    assert TWITTER_SEARCH_URL.startswith("https://")
    assert BRIGHTDATA_TRIGGER_URL.startswith("https://")
    assert OPENROUTER_CHAT_URL.startswith("https://")


def test_validate_keys_passes_with_values(monkeypatch):
    """validate_keys should not raise when keys are set."""
    monkeypatch.setattr('collectors.config.TWITTERAPI_KEY', 'test_key')
    monkeypatch.setattr('collectors.config.BRIGHTDATA_API_KEY', 'test_key')
    monkeypatch.setattr('collectors.config.OPENROUTER_API_KEY', 'test_key')
    from collectors.config import validate_keys
    # Should not raise
    validate_keys('twitter', 'brightdata', 'openrouter')


def test_validate_keys_exits_on_missing(monkeypatch):
    """validate_keys should sys.exit when a required key is empty."""
    monkeypatch.setattr('collectors.config.TWITTERAPI_KEY', '')
    from collectors.config import validate_keys
    with pytest.raises(SystemExit):
        validate_keys('twitter')


def test_data_paths_exist():
    """Verify that data path constants point to expected locations."""
    from collectors.config import DATA_DIR, POSTS_FILE, CLAIMS_FILE
    assert DATA_DIR.endswith('data')
    assert POSTS_FILE.endswith('posts.json')
    assert CLAIMS_FILE.endswith('claims.json')
