"""Tests for collectors.tiktok_collector module."""

import pytest
from unittest.mock import patch, MagicMock

from collectors.tiktok_collector import normalize_tiktok_post, collect_tiktok


SAMPLE_TIKTOK_POST = {
    "id": "tt_001",
    "author": "techcreator",
    "text": "How AI is changing education in India #AIImpact",
    "url": "https://tiktok.com/@techcreator/video/123",
    "date": "2026-02-18T16:00:00Z",
    "likes": 5000,
    "shares": 800,
    "comments": 120,
}


def test_normalize_tiktok_post_basic():
    """normalize_tiktok_post should map TikTok fields to unified schema."""
    result = normalize_tiktok_post(SAMPLE_TIKTOK_POST)
    assert result["id"] == "tt_001"
    assert result["platform"] == "tiktok"
    assert result["author"] == "techcreator"
    assert "AI is changing education" in result["text"]
    assert result["engagement"]["likes"] == 5000
    assert result["engagement"]["shares"] == 800
    assert result["engagement"]["comments"] == 120


def test_normalize_tiktok_post_alt_fields():
    """normalize_tiktok_post should handle alternative field names."""
    post = {
        "video_id": "v_789",
        "creator": "creator_name",
        "caption": "Caption text here",
        "url": "https://tiktok.com/@user/video/789",
        "create_time": "2026-02-17T12:00:00Z",
        "digg_count": 3000,
        "share_count": 500,
        "comment_count": 75,
    }
    result = normalize_tiktok_post(post)
    assert result["id"] == "v_789"
    assert result["author"] == "creator_name"
    assert result["text"] == "Caption text here"
    assert result["engagement"]["likes"] == 3000
    assert result["engagement"]["shares"] == 500
    assert result["engagement"]["comments"] == 75


def test_normalize_tiktok_post_missing_fields():
    """normalize_tiktok_post should handle missing fields gracefully."""
    result = normalize_tiktok_post({})
    assert result["platform"] == "tiktok"
    assert result["author"] == "unknown"
    assert result["text"] == ""
    assert result["engagement"]["likes"] == 0


@patch('collectors.tiktok_collector.save_json_atomic')
@patch('collectors.tiktok_collector.download_snapshot')
@patch('collectors.tiktok_collector.poll_snapshot')
@patch('collectors.tiktok_collector.trigger_collection')
def test_collect_tiktok_success(mock_trigger, mock_poll, mock_download, mock_save):
    """collect_tiktok should return normalized posts on success."""
    mock_trigger.return_value = "snap_tt_001"
    mock_poll.return_value = True
    mock_download.return_value = [SAMPLE_TIKTOK_POST] * 5

    results = collect_tiktok(["https://tiktok.com/@techcreator"])
    assert len(results) == 5
    assert all(r["platform"] == "tiktok" for r in results)


@patch('collectors.tiktok_collector.save_json_atomic')
@patch('collectors.tiktok_collector.poll_snapshot')
@patch('collectors.tiktok_collector.trigger_collection')
def test_collect_tiktok_timeout(mock_trigger, mock_poll, mock_save):
    """collect_tiktok should return empty list on timeout."""
    mock_trigger.return_value = "snap_tt_002"
    mock_poll.return_value = False

    results = collect_tiktok(["https://tiktok.com/@user"])
    assert results == []
