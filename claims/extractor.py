"""
Claims extractor using GPT-4o via OpenRouter.

Processes social media posts one at a time, extracts factual claims,
classifies them by confidence threshold, and saves results incrementally
for crash safety.
"""

import json
import logging

import requests

from collectors.config import (
    OPENROUTER_API_KEY, OPENROUTER_CHAT_URL,
    CONFIDENCE_AUTO_ACCEPT, CONFIDENCE_NEEDS_REVIEW,
    CLAIMS_FILE,
)
from collectors.retry_utils import retry_with_backoff, check_response_retryable
from collectors.file_utils import save_json_atomic, load_json_safe
from claims.prompts import build_extraction_prompt

logger = logging.getLogger(__name__)

OPENROUTER_MODEL = "openai/gpt-4o"


def classify_claim(claim):
    """
    Classify a claim based on its confidence score.

    Args:
        claim: Dict with a 'confidence' key (float 0-1).

    Returns:
        Status string: 'auto_accepted', 'needs_review', or 'auto_rejected'.
    """
    confidence = claim.get("confidence", 0)
    if confidence >= CONFIDENCE_AUTO_ACCEPT:
        return "auto_accepted"
    elif confidence >= CONFIDENCE_NEEDS_REVIEW:
        return "needs_review"
    else:
        return "auto_rejected"


@retry_with_backoff()
def _call_openrouter(messages):
    """
    Call the OpenRouter chat completions API.

    Args:
        messages: List of message dicts for the API.

    Returns:
        Parsed response content string.

    Raises:
        RetryableError: On transient HTTP errors.
        requests.HTTPError: On non-retryable HTTP errors.
    """
    resp = requests.post(
        OPENROUTER_CHAT_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": messages,
            "temperature": 0.1,
        },
        timeout=60,
    )
    check_response_retryable(resp)
    data = resp.json()

    content = data["choices"][0]["message"]["content"]
    return content


def extract_claims_from_post(post):
    """
    Extract factual claims from a single post using GPT-4o.

    Builds the prompt, calls the API, parses the JSON response,
    and classifies each claim by confidence threshold.

    Args:
        post: Dict in unified post schema format.

    Returns:
        List of claim dicts, each with added 'status', 'post_id',
        and 'platform' fields. Returns empty list on failure.
    """
    post_text = post.get("text", "")
    if not post_text.strip():
        logger.warning("Skipping post %s: empty text", post.get("id", "?"))
        return []

    messages = build_extraction_prompt(post_text)

    try:
        content = _call_openrouter(messages)
        parsed = json.loads(content)
        raw_claims = parsed.get("claims", [])
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error("Failed to parse claims for post %s: %s",
                      post.get("id", "?"), str(e))
        return []

    # Enrich each claim with metadata
    claims = []
    for claim in raw_claims:
        claim["status"] = classify_claim(claim)
        claim["post_id"] = post.get("id", "")
        claim["platform"] = post.get("platform", "")
        claim["post_url"] = post.get("url", "")
        claims.append(claim)

    return claims


def extract_all_claims(posts, output_path=None):
    """
    Extract claims from all posts, saving incrementally after each.

    Processes posts one at a time for reliability. If a post fails,
    logs the error and continues with the next post. Saves the
    accumulated claims to disk after each successful extraction.

    Args:
        posts: List of post dicts in unified schema.
        output_path: Path to save claims JSON (default: CLAIMS_FILE).

    Returns:
        List of all extracted claim dicts.
    """
    if output_path is None:
        output_path = CLAIMS_FILE

    all_claims = []
    total = len(posts)

    for i, post in enumerate(posts, 1):
        logger.info("Processing post %d/%d (id: %s, platform: %s)...",
                     i, total, post.get("id", "?"), post.get("platform", "?"))

        try:
            claims = extract_claims_from_post(post)
            all_claims.extend(claims)
            logger.info("  Found %d claims", len(claims))
        except Exception as e:
            logger.error("  Failed to process post %s: %s",
                          post.get("id", "?"), str(e))
            continue

        # Save incrementally after each post
        save_json_atomic(all_claims, output_path)

    logger.info("Extraction complete: %d claims from %d posts", len(all_claims), total)
    return all_claims
