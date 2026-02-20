"""Tests for collectors.twitter_collector module."""

import pytest
from unittest.mock import patch, MagicMock

from collectors.twitter_collector import normalize_tweet, collect_twitter


SAMPLE_TWEET = {
    "id": "12345",
    "text": "AI is transforming healthcare with new diagnostic tools.",
    "url": "https://twitter.com/user/status/12345",
    "createdAt": "2026-02-19T10:00:00Z",
    "likeCount": 150,
    "retweetCount": 42,
    "replyCount": 8,
    "author": {"userName": "techreporter", "name": "Tech Reporter"},
}


def test_normalize_tweet_basic():
    """normalize_tweet should map tweet fields to unified schema."""
    result = normalize_tweet(SAMPLE_TWEET)
    assert result["id"] == "12345"
    assert result["platform"] == "twitter"
    assert result["author"] == "techreporter"
    assert result["text"] == "AI is transforming healthcare with new diagnostic tools."
    assert result["url"] == "https://twitter.com/user/status/12345"
    assert result["timestamp"] == "2026-02-19T10:00:00Z"
    assert result["engagement"]["likes"] == 150
    assert result["engagement"]["shares"] == 42
    assert result["engagement"]["comments"] == 8
    assert "collected_at" in result


def test_normalize_tweet_missing_fields():
    """normalize_tweet should handle missing fields gracefully."""
    result = normalize_tweet({})
    assert result["id"] == ""
    assert result["platform"] == "twitter"
    assert result["author"] == "unknown"
    assert result["text"] == ""
    assert result["engagement"]["likes"] == 0


@patch('collectors.twitter_collector.save_json_atomic')
@patch('collectors.twitter_collector._search_page')
def test_collect_twitter_single_page(mock_search, mock_save):
    """collect_twitter should collect tweets from a single page."""
    mock_search.return_value = {
        "tweets": [SAMPLE_TWEET] * 5,
        "has_next_page": False,
    }

    results = collect_twitter(["AI"])
    assert len(results) == 5
    assert all(r["platform"] == "twitter" for r in results)
    mock_search.assert_called_once()


@patch('collectors.twitter_collector.save_json_atomic')
@patch('collectors.twitter_collector._search_page')
def test_collect_twitter_pagination(mock_search, mock_save):
    """collect_twitter should paginate until MAX_POSTS reached."""
    # Page 1: 15 tweets with next page
    page1 = {
        "tweets": [SAMPLE_TWEET] * 15,
        "has_next_page": True,
        "next_cursor": "cursor_abc",
    }
    # Page 2: 15 more tweets (should only take 10 to hit MAX_POSTS=25)
    page2 = {
        "tweets": [SAMPLE_TWEET] * 15,
        "has_next_page": False,
    }
    mock_search.side_effect = [page1, page2]

    results = collect_twitter(["AI"])
    assert len(results) == 25
    assert mock_search.call_count == 2


@patch('collectors.twitter_collector.save_json_atomic')
@patch('collectors.twitter_collector._search_page')
def test_collect_twitter_empty_results(mock_search, mock_save):
    """collect_twitter should handle empty results gracefully."""
    mock_search.return_value = {"tweets": []}

    results = collect_twitter(["nonexistent_topic_xyz"])
    assert results == []


@patch('collectors.twitter_collector.save_json_atomic')
@patch('collectors.twitter_collector._search_page')
def test_collect_twitter_multiple_keywords(mock_search, mock_save):
    """collect_twitter should combine multiple keywords with OR."""
    mock_search.return_value = {"tweets": [SAMPLE_TWEET], "has_next_page": False}

    collect_twitter(["AI", "machine learning"])

    call_args = mock_search.call_args
    query = call_args[0][0]
    assert "AI" in query
    assert "machine learning" in query
    assert "OR" in query
