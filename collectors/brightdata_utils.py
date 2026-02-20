"""
Shared BrightData Web Scraper API utilities.

Provides trigger/poll/download functions for the BrightData datasets API,
used by both Meta and TikTok collectors. Implements crash-safe snapshot ID
persistence and polling with timeout.
"""

import logging
import os
import time

import requests

from collectors.config import (
    BRIGHTDATA_API_KEY, BRIGHTDATA_TRIGGER_URL, BRIGHTDATA_PROGRESS_URL,
    BRIGHTDATA_SNAPSHOT_URL, BRIGHTDATA_POLL_INTERVAL, BRIGHTDATA_POLL_TIMEOUT,
    RAW_DIR,
)
from collectors.retry_utils import retry_with_backoff, check_response_retryable
from collectors.file_utils import save_json_atomic

logger = logging.getLogger(__name__)


@retry_with_backoff()
def trigger_collection(dataset_id, inputs):
    """
    Trigger a BrightData data collection.

    Sends a POST request to start collecting data for the given inputs.
    Saves the snapshot_id to disk immediately for crash recovery.

    Args:
        dataset_id: BrightData dataset ID (e.g., 'gd_lkaxegm826bjpoo9m5').
        inputs: List of input dicts (e.g., [{"url": "...", "num_of_posts": 25}]).

    Returns:
        snapshot_id string.

    Raises:
        RetryableError: On transient HTTP errors.
        requests.HTTPError: On non-retryable HTTP errors.
    """
    resp = requests.post(
        BRIGHTDATA_TRIGGER_URL,
        params={"dataset_id": dataset_id, "format": "json"},
        headers={
            "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
            "Content-Type": "application/json",
        },
        json=inputs,
        timeout=30,
    )
    check_response_retryable(resp)
    data = resp.json()
    snapshot_id = data.get("snapshot_id", "")

    if not snapshot_id:
        raise ValueError(f"No snapshot_id in response: {data}")

    logger.info("Triggered collection, snapshot_id: %s", snapshot_id)

    # Save snapshot_id for crash recovery
    recovery_path = os.path.join(RAW_DIR, f'snapshot_{snapshot_id}.json')
    save_json_atomic({"snapshot_id": snapshot_id, "dataset_id": dataset_id}, recovery_path)

    return snapshot_id


def poll_snapshot(snapshot_id, timeout=None, poll_interval=None, sleep_func=time.sleep):
    """
    Poll BrightData until a snapshot is ready or timeout is reached.

    Args:
        snapshot_id: The snapshot ID to poll.
        timeout: Maximum wait time in seconds (default: BRIGHTDATA_POLL_TIMEOUT).
        poll_interval: Seconds between polls (default: BRIGHTDATA_POLL_INTERVAL).
        sleep_func: Sleep function (override in tests).

    Returns:
        True if snapshot is ready, False if timed out.

    Raises:
        RuntimeError: If the snapshot fails.
    """
    if timeout is None:
        timeout = BRIGHTDATA_POLL_TIMEOUT
    if poll_interval is None:
        poll_interval = BRIGHTDATA_POLL_INTERVAL

    elapsed = 0
    while elapsed < timeout:
        status = _check_progress(snapshot_id)
        logger.info("Snapshot %s status: %s (%.0fs elapsed)",
                     snapshot_id, status, elapsed)

        if status == "ready":
            return True
        if status == "failed":
            raise RuntimeError(f"Snapshot {snapshot_id} failed")

        sleep_func(poll_interval)
        elapsed += poll_interval

    logger.error("Polling timed out for snapshot %s after %ds", snapshot_id, timeout)
    return False


@retry_with_backoff()
def _check_progress(snapshot_id):
    """
    Check the progress of a BrightData snapshot.

    Args:
        snapshot_id: The snapshot ID to check.

    Returns:
        Status string (e.g., 'starting', 'running', 'ready', 'failed').
    """
    resp = requests.get(
        f"{BRIGHTDATA_PROGRESS_URL}/{snapshot_id}",
        headers={"Authorization": f"Bearer {BRIGHTDATA_API_KEY}"},
        timeout=30,
    )
    check_response_retryable(resp)
    data = resp.json()
    return data.get("status", "unknown")


@retry_with_backoff()
def download_snapshot(snapshot_id):
    """
    Download the results of a completed BrightData snapshot.

    Args:
        snapshot_id: The snapshot ID to download.

    Returns:
        List of data dicts from the snapshot.

    Raises:
        RetryableError: On transient HTTP errors.
        requests.HTTPError: On non-retryable HTTP errors.
    """
    resp = requests.get(
        f"{BRIGHTDATA_SNAPSHOT_URL}/{snapshot_id}",
        headers={"Authorization": f"Bearer {BRIGHTDATA_API_KEY}"},
        timeout=60,
    )
    check_response_retryable(resp)
    data = resp.json()

    logger.info("Downloaded %d records from snapshot %s", len(data), snapshot_id)
    return data
