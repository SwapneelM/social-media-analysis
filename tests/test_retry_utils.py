"""Tests for collectors.retry_utils module."""

import pytest
import requests
from unittest.mock import MagicMock, Mock

from collectors.retry_utils import (
    retry_with_backoff, RetryableError, check_response_retryable,
    RETRYABLE_STATUS_CODES,
)


def test_retry_succeeds_first_attempt():
    """Function should return immediately on success."""
    mock_sleep = MagicMock()

    @retry_with_backoff(max_retries=3, sleep_func=mock_sleep)
    def success():
        return "ok"

    assert success() == "ok"
    mock_sleep.assert_not_called()


def test_retry_succeeds_after_failures():
    """Function should retry and eventually succeed."""
    mock_sleep = MagicMock()
    call_count = 0

    @retry_with_backoff(max_retries=3, initial_backoff=1.0, sleep_func=mock_sleep)
    def eventual_success():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RetryableError("temporary failure")
        return "recovered"

    assert eventual_success() == "recovered"
    assert call_count == 3
    assert mock_sleep.call_count == 2


def test_retry_exhausts_all_attempts():
    """Function should raise after exhausting all retries."""
    mock_sleep = MagicMock()

    @retry_with_backoff(max_retries=2, sleep_func=mock_sleep)
    def always_fails():
        raise RetryableError("persistent failure")

    with pytest.raises(RetryableError, match="persistent failure"):
        always_fails()
    assert mock_sleep.call_count == 2


def test_retry_on_connection_error():
    """ConnectionError should trigger retry."""
    mock_sleep = MagicMock()
    call_count = 0

    @retry_with_backoff(max_retries=3, sleep_func=mock_sleep)
    def conn_error_then_ok():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise requests.exceptions.ConnectionError("connection failed")
        return "ok"

    assert conn_error_then_ok() == "ok"
    assert call_count == 2


def test_retry_on_timeout():
    """Timeout should trigger retry."""
    mock_sleep = MagicMock()
    call_count = 0

    @retry_with_backoff(max_retries=3, sleep_func=mock_sleep)
    def timeout_then_ok():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise requests.exceptions.Timeout("timeout")
        return "ok"

    assert timeout_then_ok() == "ok"


def test_retry_on_retryable_http_error():
    """HTTPError with retryable status code should trigger retry."""
    mock_sleep = MagicMock()
    call_count = 0

    @retry_with_backoff(max_retries=3, sleep_func=mock_sleep)
    def http_429_then_ok():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            resp = Mock()
            resp.status_code = 429
            raise requests.exceptions.HTTPError(response=resp)
        return "ok"

    assert http_429_then_ok() == "ok"


def test_no_retry_on_non_retryable_http_error():
    """HTTPError with non-retryable status code should raise immediately."""
    mock_sleep = MagicMock()

    @retry_with_backoff(max_retries=3, sleep_func=mock_sleep)
    def http_404():
        resp = Mock()
        resp.status_code = 404
        raise requests.exceptions.HTTPError(response=resp)

    with pytest.raises(requests.exceptions.HTTPError):
        http_404()
    mock_sleep.assert_not_called()


def test_exponential_backoff_timing():
    """Backoff should double each retry."""
    sleep_times = []
    mock_sleep = MagicMock(side_effect=lambda t: sleep_times.append(t))

    @retry_with_backoff(max_retries=3, initial_backoff=1.0, multiplier=2.0,
                        sleep_func=mock_sleep)
    def always_fails():
        raise RetryableError("fail")

    with pytest.raises(RetryableError):
        always_fails()

    assert sleep_times == [1.0, 2.0, 4.0]


def test_check_response_retryable_raises_on_429():
    """check_response_retryable should raise RetryableError on 429."""
    resp = Mock()
    resp.status_code = 429
    resp.text = "Rate limited"
    with pytest.raises(RetryableError):
        check_response_retryable(resp)


def test_check_response_retryable_raises_on_500():
    """check_response_retryable should raise RetryableError on 500."""
    resp = Mock()
    resp.status_code = 500
    resp.text = "Internal server error"
    with pytest.raises(RetryableError):
        check_response_retryable(resp)


def test_check_response_retryable_passes_on_200():
    """check_response_retryable should not raise on 200."""
    resp = Mock()
    resp.status_code = 200
    resp.raise_for_status = MagicMock()
    check_response_retryable(resp)
    resp.raise_for_status.assert_called_once()


def test_check_response_retryable_raises_http_error_on_400():
    """check_response_retryable should raise HTTPError on 400 (not retryable)."""
    resp = Mock()
    resp.status_code = 400
    resp.raise_for_status.side_effect = requests.exceptions.HTTPError(
        response=resp
    )
    with pytest.raises(requests.exceptions.HTTPError):
        check_response_retryable(resp)
