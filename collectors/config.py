"""
Configuration module for social media data collectors.

Loads environment variables from .env file and exposes API keys,
endpoints, and constants used across all collector modules.
Validates that required keys exist at import time.
"""

import os
import sys
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


# --- API Keys ---
TWITTERAPI_KEY = os.getenv("TWITTERAPI_KEY", "")
BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# --- API Endpoints ---
TWITTER_SEARCH_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"
BRIGHTDATA_TRIGGER_URL = "https://api.brightdata.com/datasets/v3/trigger"
BRIGHTDATA_PROGRESS_URL = "https://api.brightdata.com/datasets/v3/progress"
BRIGHTDATA_SNAPSHOT_URL = "https://api.brightdata.com/datasets/v3/snapshot"
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- BrightData Dataset IDs (public, not secrets) ---
BRIGHTDATA_FACEBOOK_DATASET_ID = "gd_lkaxegm826bjpoo9m5"
BRIGHTDATA_TIKTOK_DATASET_ID = "gd_lu702nij2f790tmv9h"

# --- Constants ---
MAX_POSTS = 25
RETRY_MAX_RETRIES = 5
RETRY_INITIAL_BACKOFF = 1.0
RETRY_MULTIPLIER = 2.0
BRIGHTDATA_POLL_INTERVAL = 10  # seconds
BRIGHTDATA_POLL_TIMEOUT = 300  # seconds

# --- Confidence Thresholds ---
CONFIDENCE_AUTO_ACCEPT = 0.85
CONFIDENCE_NEEDS_REVIEW = 0.60

# --- Data Paths ---
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
POSTS_FILE = os.path.join(DATA_DIR, 'posts.json')
CLAIMS_FILE = os.path.join(DATA_DIR, 'claims.json')


def validate_keys(*required_keys):
    """
    Validate that specified API keys are set and non-empty.

    Args:
        *required_keys: Variable number of key name strings to check.
            Valid values: 'twitter', 'brightdata', 'openrouter'

    Raises:
        SystemExit: If any required key is missing or empty.
    """
    key_map = {
        'twitter': ('TWITTERAPI_KEY', TWITTERAPI_KEY),
        'brightdata': ('BRIGHTDATA_API_KEY', BRIGHTDATA_API_KEY),
        'openrouter': ('OPENROUTER_API_KEY', OPENROUTER_API_KEY),
    }
    missing = []
    for key in required_keys:
        name, value = key_map[key]
        if not value:
            missing.append(name)
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Please set them in your .env file.", file=sys.stderr)
        sys.exit(1)
