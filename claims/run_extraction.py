"""
CLI entry point for claims extraction.

Reads posts from data/posts.json, extracts factual claims using GPT-4o
via OpenRouter, and saves results to data/claims.json.

Usage:
    python -m claims.run_extraction
"""

import logging
import sys

from collectors.config import validate_keys, POSTS_FILE, CLAIMS_FILE
from collectors.file_utils import load_json_safe
from claims.extractor import extract_all_claims

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """
    Main entry point for claims extraction.

    Validates the OpenRouter API key, loads posts from data/posts.json,
    runs the extraction pipeline, and reports results.
    """
    validate_keys('openrouter')

    posts = load_json_safe(POSTS_FILE, default=[])
    if not posts:
        print(f"Error: No posts found in {POSTS_FILE}. Run data collection first.")
        sys.exit(1)

    logger.info("Loaded %d posts from %s", len(posts), POSTS_FILE)
    logger.info("Extracting claims using GPT-4o via OpenRouter...")

    claims = extract_all_claims(posts, CLAIMS_FILE)

    # Summary
    auto_accepted = sum(1 for c in claims if c.get("status") == "auto_accepted")
    needs_review = sum(1 for c in claims if c.get("status") == "needs_review")
    auto_rejected = sum(1 for c in claims if c.get("status") == "auto_rejected")

    logger.info("Results saved to %s", CLAIMS_FILE)
    logger.info("Summary: %d total claims", len(claims))
    logger.info("  Auto-accepted (>=%.2f): %d", 0.85, auto_accepted)
    logger.info("  Needs review (%.2f-%.2f): %d", 0.60, 0.85, needs_review)
    logger.info("  Auto-rejected (<%.2f): %d", 0.60, auto_rejected)


if __name__ == "__main__":
    main()
