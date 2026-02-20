"""
TikTok data collector using BrightData Web Scraper API.

Collects posts from public TikTok account URLs, normalizes them
to the unified post schema.
"""

import logging
import os
from datetime import datetime, timezone

from collectors.config import (
    BRIGHTDATA_TIKTOK_DATASET_ID, MAX_POSTS, RAW_DIR,
)
from collectors.brightdata_utils import (
    trigger_collection, poll_snapshot, download_snapshot,
)
from collectors.file_utils import save_json_atomic

logger = logging.getLogger(__name__)


def normalize_tiktok_post(post):
    """
    Normalize a raw TikTok post from BrightData to the unified post schema.

    BrightData TikTok posts may have varying field names. This function
    maps common fields to our unified format.

    Args:
        post: Dict from BrightData TikTok dataset response.

    Returns:
        Dict in unified post schema format.
    """
    post_id = (post.get("id") or post.get("video_id") or
               post.get("url", "").split("/")[-1] or "unknown")

    return {
        "id": str(post_id),
        "platform": "tiktok",
        "author": (post.get("author") or post.get("user_name") or
                   post.get("creator") or "unknown"),
        "text": (post.get("text") or post.get("title") or
                 post.get("description") or post.get("caption") or ""),
        "url": post.get("url", ""),
        "timestamp": post.get("date") or post.get("create_time") or "",
        "engagement": {
            "likes": post.get("likes") or post.get("digg_count") or 0,
            "shares": post.get("shares") or post.get("share_count") or 0,
            "comments": post.get("comments") or post.get("comment_count") or 0,
        },
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def collect_tiktok(urls):
    """
    Collect TikTok posts from the given account URLs via BrightData.

    Triggers a BrightData collection, polls until ready, downloads results,
    and normalizes to the unified post schema.

    Args:
        urls: List of public TikTok account URL strings.

    Returns:
        List of normalized post dicts (up to MAX_POSTS).
    """
    logger.info("Collecting TikTok posts from %d URLs...", len(urls))

    # Build inputs for BrightData (TikTok profiles dataset doesn't accept num_of_posts)
    inputs = [{"url": url} for url in urls]

    # Trigger collection
    snapshot_id = trigger_collection(BRIGHTDATA_TIKTOK_DATASET_ID, inputs)

    # Poll until ready
    ready = poll_snapshot(snapshot_id)
    if not ready:
        logger.error("BrightData TikTok collection timed out.")
        return []

    # Download results
    raw_data = download_snapshot(snapshot_id)

    # Save raw data
    raw_path = os.path.join(RAW_DIR, 'tiktok', f'snapshot_{snapshot_id}.json')
    save_json_atomic(raw_data, raw_path)

    # Normalize
    posts = []
    for item in raw_data:
        if len(posts) >= MAX_POSTS:
            break
        posts.append(normalize_tiktok_post(item))

    logger.info("Collected %d TikTok posts.", len(posts))
    return posts
