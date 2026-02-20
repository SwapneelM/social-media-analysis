"""Tests for collectors.meta_collector module."""

import pytest
from unittest.mock import patch, MagicMock

from collectors.meta_collector import normalize_meta_post, collect_meta


SAMPLE_FB_POST = {
    "post_id": "fb_001",
    "author_name": "AI News Page",
    "post_text": "India AI Impact Summit brings together top researchers.",
    "url": "https://facebook.com/ainews/posts/123",
    "date": "2026-02-18T14:00:00Z",
    "likes": 200,
    "shares": 50,
    "comments": 30,
}


def test_normalize_meta_post_basic():
    """normalize_meta_post should map Facebook fields to unified schema."""
    result = normalize_meta_post(SAMPLE_FB_POST)
    assert result["id"] == "fb_001"
    assert result["platform"] == "meta"
    assert result["author"] == "AI News Page"
    assert "India AI" in result["text"]
    assert result["engagement"]["likes"] == 200
    assert result["engagement"]["shares"] == 50
    assert result["engagement"]["comments"] == 30


def test_normalize_meta_post_alt_fields():
    """normalize_meta_post should handle alternative field names."""
    post = {
        "id": "alt_id",
        "page_name": "Alt Page",
        "content": "Some content here",
        "url": "https://facebook.com/page/posts/456",
        "post_date": "2026-02-17T10:00:00Z",
        "reactions": 100,
        "num_comments": 15,
    }
    result = normalize_meta_post(post)
    assert result["id"] == "alt_id"
    assert result["author"] == "Alt Page"
    assert result["text"] == "Some content here"
    assert result["engagement"]["likes"] == 100
    assert result["engagement"]["comments"] == 15


def test_normalize_meta_post_missing_fields():
    """normalize_meta_post should handle missing fields gracefully."""
    result = normalize_meta_post({})
    assert result["platform"] == "meta"
    assert result["author"] == "unknown"
    assert result["text"] == ""
    assert result["engagement"]["likes"] == 0


@patch('collectors.meta_collector.save_json_atomic')
@patch('collectors.meta_collector.download_snapshot')
@patch('collectors.meta_collector.poll_snapshot')
@patch('collectors.meta_collector.trigger_collection')
def test_collect_meta_success(mock_trigger, mock_poll, mock_download, mock_save):
    """collect_meta should return normalized posts on success."""
    mock_trigger.return_value = "snap_fb_001"
    mock_poll.return_value = True
    mock_download.return_value = [SAMPLE_FB_POST] * 5

    results = collect_meta(["https://facebook.com/ainews"])
    assert len(results) == 5
    assert all(r["platform"] == "meta" for r in results)


@patch('collectors.meta_collector.save_json_atomic')
@patch('collectors.meta_collector.poll_snapshot')
@patch('collectors.meta_collector.trigger_collection')
def test_collect_meta_timeout(mock_trigger, mock_poll, mock_save):
    """collect_meta should return empty list on timeout."""
    mock_trigger.return_value = "snap_fb_002"
    mock_poll.return_value = False

    results = collect_meta(["https://facebook.com/page"])
    assert results == []
