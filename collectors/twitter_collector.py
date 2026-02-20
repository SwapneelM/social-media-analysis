"""
Twitter/X data collector using twitterapi.io.

Searches for tweets by keyword using the advanced search endpoint,
paginates through results until MAX_POSTS tweets are collected,
and normalizes them to the unified post schema.
"""

import logging
import os
from datetime import datetime, timezone

import requests

from collectors.config import (
    TWITTERAPI_KEY, TWITTER_SEARCH_URL, MAX_POSTS, RAW_DIR,
)
from collectors.retry_utils import retry_with_backoff, check_response_retryable
from collectors.file_utils import save_json_atomic

logger = logging.getLogger(__name__)


def normalize_tweet(tweet):
    """
    Normalize a raw tweet from twitterapi.io to the unified post schema.

    Args:
        tweet: Dict from twitterapi.io API response.

    Returns:
        Dict in unified post schema format.
    """
    return {
        "id": tweet.get("id", ""),
        "platform": "twitter",
        "author": tweet.get("author", {}).get("userName", "unknown"),
        "text": tweet.get("text", ""),
        "url": tweet.get("url", ""),
        "timestamp": tweet.get("createdAt", ""),
        "engagement": {
            "likes": tweet.get("likeCount", 0),
            "shares": tweet.get("retweetCount", 0),
            "comments": tweet.get("replyCount", 0),
        },
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


@retry_with_backoff()
def _search_page(query, cursor=None):
    """
    Fetch a single page of Twitter search results.

    Args:
        query: Search query string.
        cursor: Pagination cursor from previous response (None for first page).

    Returns:
        Parsed JSON response dict.

    Raises:
        RetryableError: On transient HTTP errors (429, 5xx).
        requests.HTTPError: On non-retryable HTTP errors.
    """
    params = {"query": query, "queryType": "Latest"}
    if cursor:
        params["cursor"] = cursor

    resp = requests.get(
        TWITTER_SEARCH_URL,
        headers={"x-api-key": TWITTERAPI_KEY},
        params=params,
        timeout=30,
    )
    check_response_retryable(resp)
    return resp.json()


def collect_twitter(keywords):
    """
    Collect tweets matching the given keywords.

    Searches Twitter using twitterapi.io advanced search, paginates
    through results until MAX_POSTS tweets are collected, and saves
    raw responses incrementally to data/raw/twitter/.

    Args:
        keywords: List of keyword strings to search for.

    Returns:
        List of normalized post dicts in unified schema.
    """
    all_posts = []
    query = " OR ".join(keywords)
    cursor = None
    page = 0

    logger.info("Searching Twitter for: %s", query)

    while len(all_posts) < MAX_POSTS:
        page += 1
        logger.info("Fetching page %d (collected %d/%d)...",
                     page, len(all_posts), MAX_POSTS)

        data = _search_page(query, cursor)

        # Save raw response incrementally
        raw_path = os.path.join(RAW_DIR, 'twitter', f'page_{page}.json')
        save_json_atomic(data, raw_path)

        tweets = data.get("tweets", [])
        if not tweets:
            logger.info("No more tweets found.")
            break

        for tweet in tweets:
            if len(all_posts) >= MAX_POSTS:
                break
            all_posts.append(normalize_tweet(tweet))

        # Check for next page
        if data.get("has_next_page") and data.get("next_cursor"):
            cursor = data["next_cursor"]
        else:
            break

    logger.info("Collected %d tweets.", len(all_posts))
    return all_posts
