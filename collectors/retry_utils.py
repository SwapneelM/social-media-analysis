"""
Retry utilities with exponential backoff for API calls.

Provides a decorator that retries functions on transient HTTP errors
(429, 500, 502, 503, 504) and ConnectionError, with configurable
backoff parameters.
"""

import functools
import logging
import time

import requests

logger = logging.getLogger(__name__)

# HTTP status codes that should trigger a retry
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class RetryableError(Exception):
    """Raised when a retryable error occurs during an API call."""
    pass


def retry_with_backoff(max_retries=5, initial_backoff=1.0, multiplier=2.0,
                       sleep_func=time.sleep):
    """
    Decorator that retries a function with exponential backoff.

    Retries on:
    - requests.exceptions.ConnectionError
    - requests.exceptions.Timeout
    - RetryableError (raised manually for retryable HTTP status codes)
    - requests.HTTPError with retryable status codes

    Args:
        max_retries: Maximum number of retry attempts (default: 5).
        initial_backoff: Initial wait time in seconds (default: 1.0).
        multiplier: Backoff multiplier per retry (default: 2.0).
        sleep_func: Function to call for sleeping (default: time.sleep).
            Override with a mock in tests to avoid actual delays.

    Returns:
        Decorated function with retry behavior.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            backoff = initial_backoff
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout,
                        RetryableError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            "Attempt %d/%d failed for %s: %s. "
                            "Retrying in %.1fs...",
                            attempt + 1, max_retries + 1,
                            func.__name__, str(e), backoff
                        )
                        sleep_func(backoff)
                        backoff *= multiplier
                    else:
                        logger.error(
                            "All %d attempts failed for %s: %s",
                            max_retries + 1, func.__name__, str(e)
                        )
                except requests.exceptions.HTTPError as e:
                    if (e.response is not None and
                            e.response.status_code in RETRYABLE_STATUS_CODES):
                        last_exception = e
                        if attempt < max_retries:
                            logger.warning(
                                "Attempt %d/%d failed for %s: HTTP %d. "
                                "Retrying in %.1fs...",
                                attempt + 1, max_retries + 1,
                                func.__name__,
                                e.response.status_code, backoff
                            )
                            sleep_func(backoff)
                            backoff *= multiplier
                        else:
                            logger.error(
                                "All %d attempts failed for %s: HTTP %d",
                                max_retries + 1, func.__name__,
                                e.response.status_code
                            )
                    else:
                        raise

            raise last_exception
        return wrapper
    return decorator


def check_response_retryable(response):
    """
    Check if an HTTP response has a retryable status code and raise accordingly.

    Call this after requests.get/post to handle retryable errors consistently.

    Args:
        response: A requests.Response object.

    Raises:
        RetryableError: If the status code is in RETRYABLE_STATUS_CODES.
        requests.HTTPError: If the status code indicates a non-retryable error.
    """
    if response.status_code in RETRYABLE_STATUS_CODES:
        raise RetryableError(
            f"HTTP {response.status_code}: {response.text[:200]}"
        )
    response.raise_for_status()
