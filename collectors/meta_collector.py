"""
Facebook/Meta data collector using BrightData Web Scraper API.

Collects posts from public Facebook page URLs, normalizes them
to the unified post schema.
"""

import logging
import os
from datetime import datetime, timezone

from collectors.config import (
    BRIGHTDATA_FACEBOOK_DATASET_ID, MAX_POSTS, RAW_DIR,
)
from collectors.brightdata_utils import (
    trigger_collection, poll_snapshot, download_snapshot,
)
from collectors.file_utils import save_json_atomic

logger = logging.getLogger(__name__)


def normalize_meta_post(post):
    """
    Normalize a raw Facebook post from BrightData to the unified post schema.

    BrightData Facebook posts may have varying field names. This function
    maps common fields to our unified format.

    Args:
        post: Dict from BrightData Facebook dataset response.

    Returns:
        Dict in unified post schema format.
    """
    # BrightData Facebook fields vary; handle common patterns
    post_id = (post.get("post_id") or post.get("id") or
               post.get("url", "").split("/")[-1] or "unknown")

    return {
        "id": str(post_id),
        "platform": "meta",
        "author": (post.get("author_name") or post.get("user_name") or
                   post.get("page_name") or "unknown"),
        "text": (post.get("post_text") or post.get("text") or
                 post.get("content") or post.get("description") or ""),
        "url": post.get("url", ""),
        "timestamp": post.get("date") or post.get("post_date") or "",
        "engagement": {
            "likes": post.get("likes") or post.get("reactions") or 0,
            "shares": post.get("shares") or 0,
            "comments": post.get("comments") or post.get("num_comments") or 0,
        },
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def collect_meta(urls):
    """
    Collect Facebook posts from the given page URLs via BrightData.

    Triggers a BrightData collection, polls until ready, downloads results,
    and normalizes to the unified post schema.

    Args:
        urls: List of public Facebook page URL strings.

    Returns:
        List of normalized post dicts (up to MAX_POSTS).
    """
    logger.info("Collecting Facebook posts from %d URLs...", len(urls))

    # Build inputs for BrightData
    inputs = [{"url": url, "num_of_posts": MAX_POSTS} for url in urls]

    # Trigger collection
    snapshot_id = trigger_collection(BRIGHTDATA_FACEBOOK_DATASET_ID, inputs)

    # Poll until ready
    ready = poll_snapshot(snapshot_id)
    if not ready:
        logger.error("BrightData Facebook collection timed out.")
        return []

    # Download results
    raw_data = download_snapshot(snapshot_id)

    # Save raw data
    raw_path = os.path.join(RAW_DIR, 'meta', f'snapshot_{snapshot_id}.json')
    save_json_atomic(raw_data, raw_path)

    # Normalize
    posts = []
    for item in raw_data:
        if len(posts) >= MAX_POSTS:
            break
        posts.append(normalize_meta_post(item))

    logger.info("Collected %d Facebook posts.", len(posts))
    return posts
