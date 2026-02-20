"""
TikTok data collector using BrightData Web Scraper API.

Collects individual TikTok video posts by URL via BrightData's TikTok Posts
dataset. Requires specific video URLs (tiktok.com/@user/video/ID), NOT
profile URLs. Video URLs are found via web search or manual browsing.

The TikTok Posts dataset does NOT support num_of_posts or profile-level
scraping — each input must be a direct video URL.
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

    BrightData TikTok Posts dataset returns fields like 'id', 'author',
    'text', 'digg_count', etc. This function maps them to our unified format.

    Args:
        post: Dict from BrightData TikTok Posts dataset response.

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


def collect_tiktok(video_urls):
    """
    Collect TikTok posts by individual video URL via BrightData.

    Each URL must be a direct video link (tiktok.com/@user/video/ID).
    The BrightData TikTok Posts dataset does NOT support profile URLs
    or num_of_posts — it scrapes one video per input URL.

    Args:
        video_urls: List of TikTok video URL strings.
            Format: https://www.tiktok.com/@username/video/1234567890

    Returns:
        List of normalized post dicts (up to MAX_POSTS).
    """
    logger.info("Collecting %d TikTok video(s)...", len(video_urls))

    # Each URL is a separate input — no num_of_posts field allowed
    inputs = [{"url": url} for url in video_urls[:MAX_POSTS]]

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

    # Normalize — filter out non-dict items
    posts = []
    for item in raw_data:
        if not isinstance(item, dict):
            logger.warning("Skipping non-dict item in TikTok response: %s", type(item))
            continue
        if len(posts) >= MAX_POSTS:
            break
        posts.append(normalize_tiktok_post(item))

    logger.info("Collected %d TikTok posts.", len(posts))
    return posts
