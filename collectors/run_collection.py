"""
CLI entry point for data collection from social media platforms.

Runs selected collectors (Twitter, Meta, TikTok) based on provided
arguments, merges results into data/posts.json.

Usage:
    python -m collectors.run_collection \\
        --twitter-keywords "AI" "machine learning" \\
        --meta-urls "https://facebook.com/page" \\
        --tiktok-urls "https://tiktok.com/@user"
"""

import argparse
import logging
import sys

from collectors.config import validate_keys, POSTS_FILE
from collectors.file_utils import save_json_atomic, load_json_safe
from collectors.twitter_collector import collect_twitter
from collectors.meta_collector import collect_meta
from collectors.tiktok_collector import collect_tiktok

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args(argv=None):
    """
    Parse command-line arguments for data collection.

    Args:
        argv: Optional list of argument strings (default: sys.argv[1:]).

    Returns:
        Parsed argparse.Namespace object.
    """
    parser = argparse.ArgumentParser(
        description="Collect social media posts from Twitter, Facebook, and TikTok."
    )
    parser.add_argument(
        "--twitter-keywords", nargs="+", default=[],
        help="Keywords to search on Twitter (e.g., 'AI' 'deep learning')"
    )
    parser.add_argument(
        "--meta-urls", nargs="+", default=[],
        help="Facebook page URLs to collect from"
    )
    parser.add_argument(
        "--tiktok-urls", nargs="+", default=[],
        help="TikTok account URLs to collect from"
    )
    return parser.parse_args(argv)


def main(argv=None):
    """
    Main entry point for data collection.

    Validates required API keys, runs selected collectors, and merges
    all results into data/posts.json.

    Args:
        argv: Optional list of argument strings for testing.
    """
    args = parse_args(argv)

    if not args.twitter_keywords and not args.meta_urls and not args.tiktok_urls:
        print("Error: Provide at least one of --twitter-keywords, --meta-urls, or --tiktok-urls")
        sys.exit(1)

    all_posts = []

    # Twitter collection
    if args.twitter_keywords:
        validate_keys('twitter')
        logger.info("Starting Twitter collection...")
        tweets = collect_twitter(args.twitter_keywords)
        all_posts.extend(tweets)
        logger.info("Twitter: collected %d posts", len(tweets))

    # Meta/Facebook collection
    if args.meta_urls:
        validate_keys('brightdata')
        logger.info("Starting Facebook collection...")
        meta_posts = collect_meta(args.meta_urls)
        all_posts.extend(meta_posts)
        logger.info("Facebook: collected %d posts", len(meta_posts))

    # TikTok collection
    if args.tiktok_urls:
        validate_keys('brightdata')
        logger.info("Starting TikTok collection...")
        tiktok_posts = collect_tiktok(args.tiktok_urls)
        all_posts.extend(tiktok_posts)
        logger.info("TikTok: collected %d posts", len(tiktok_posts))

    # Save merged results
    save_json_atomic(all_posts, POSTS_FILE)
    logger.info("Saved %d total posts to %s", len(all_posts), POSTS_FILE)


if __name__ == "__main__":
    main()
