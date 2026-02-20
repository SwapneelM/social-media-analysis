"""Tests for claims.extractor module."""

import json
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from claims.extractor import (
    classify_claim, extract_claims_from_post, extract_all_claims,
)


def test_classify_claim_auto_accepted():
    """Claims with confidence >= 0.85 should be auto_accepted."""
    assert classify_claim({"confidence": 0.95}) == "auto_accepted"
    assert classify_claim({"confidence": 0.85}) == "auto_accepted"


def test_classify_claim_needs_review():
    """Claims with confidence 0.60-0.85 should need review."""
    assert classify_claim({"confidence": 0.75}) == "needs_review"
    assert classify_claim({"confidence": 0.60}) == "needs_review"


def test_classify_claim_auto_rejected():
    """Claims with confidence < 0.60 should be auto_rejected."""
    assert classify_claim({"confidence": 0.50}) == "auto_rejected"
    assert classify_claim({"confidence": 0.0}) == "auto_rejected"


def test_classify_claim_missing_confidence():
    """Claims without confidence field should be auto_rejected."""
    assert classify_claim({}) == "auto_rejected"


MOCK_API_RESPONSE = json.dumps({
    "claims": [
        {
            "claim_text": "AI market will reach $17B by 2027",
            "confidence": 0.92,
            "category": "technology",
            "reasoning": "Specific verifiable prediction",
            "source_quote": "AI market is expected to reach $17B by 2027",
        },
        {
            "claim_text": "Government invested 10000 crore",
            "confidence": 0.70,
            "category": "politics",
            "reasoning": "Specific financial claim",
            "source_quote": "invested ₹10,000 crore",
        },
    ]
})

SAMPLE_POST = {
    "id": "post_001",
    "platform": "twitter",
    "text": "AI market will reach $17B by 2027. Government invested 10000 crore.",
    "url": "https://twitter.com/user/status/001",
}


@patch('claims.extractor._call_openrouter')
def test_extract_claims_from_post_success(mock_call):
    """extract_claims_from_post should return classified claims."""
    mock_call.return_value = MOCK_API_RESPONSE

    claims = extract_claims_from_post(SAMPLE_POST)
    assert len(claims) == 2
    assert claims[0]["status"] == "auto_accepted"
    assert claims[0]["post_id"] == "post_001"
    assert claims[0]["platform"] == "twitter"
    assert claims[1]["status"] == "needs_review"


@patch('claims.extractor._call_openrouter')
def test_extract_claims_from_post_no_claims(mock_call):
    """extract_claims_from_post should return empty list for opinion posts."""
    mock_call.return_value = '{"claims": []}'

    claims = extract_claims_from_post({
        "id": "post_002",
        "platform": "twitter",
        "text": "I love AI! So exciting!",
    })
    assert claims == []


@patch('claims.extractor._call_openrouter')
def test_extract_claims_from_post_empty_text(mock_call):
    """extract_claims_from_post should skip posts with empty text."""
    claims = extract_claims_from_post({"id": "post_003", "text": ""})
    assert claims == []
    mock_call.assert_not_called()


@patch('claims.extractor._call_openrouter')
def test_extract_claims_from_post_invalid_json(mock_call):
    """extract_claims_from_post should return empty list on invalid JSON."""
    mock_call.return_value = "not valid json at all"

    claims = extract_claims_from_post(SAMPLE_POST)
    assert claims == []


@patch('claims.extractor._call_openrouter')
def test_extract_all_claims_saves_incrementally(mock_call):
    """extract_all_claims should save after each post."""
    mock_call.return_value = MOCK_API_RESPONSE

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = os.path.join(tmp_dir, "claims.json")
        posts = [SAMPLE_POST, SAMPLE_POST]

        claims = extract_all_claims(posts, output_path)
        assert len(claims) == 4  # 2 claims per post * 2 posts
        assert os.path.exists(output_path)

        # Verify file contains all claims
        with open(output_path, 'r') as f:
            saved = json.load(f)
        assert len(saved) == 4


@patch('claims.extractor._call_openrouter')
def test_extract_all_claims_continues_on_failure(mock_call):
    """extract_all_claims should continue when a single post fails."""
    mock_call.side_effect = [
        Exception("API error"),  # First post fails
        MOCK_API_RESPONSE,       # Second post succeeds
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = os.path.join(tmp_dir, "claims.json")
        posts = [SAMPLE_POST, SAMPLE_POST]

        claims = extract_all_claims(posts, output_path)
        assert len(claims) == 2  # Only second post's claims


@patch('claims.extractor._call_openrouter')
def test_extract_claims_adds_metadata(mock_call):
    """Extracted claims should include post_id, platform, and post_url."""
    mock_call.return_value = MOCK_API_RESPONSE

    claims = extract_claims_from_post(SAMPLE_POST)
    for claim in claims:
        assert "post_id" in claim
        assert "platform" in claim
        assert "post_url" in claim
        assert "status" in claim
