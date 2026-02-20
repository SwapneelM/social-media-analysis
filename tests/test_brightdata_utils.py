"""Tests for collectors.brightdata_utils module."""

import pytest
from unittest.mock import patch, MagicMock, Mock

from collectors.brightdata_utils import (
    trigger_collection, poll_snapshot, download_snapshot,
)


@patch('collectors.brightdata_utils.save_json_atomic')
@patch('collectors.brightdata_utils.requests.post')
def test_trigger_collection_success(mock_post, mock_save):
    """trigger_collection should return snapshot_id on success."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"snapshot_id": "snap_123"}
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp

    result = trigger_collection("dataset_abc", [{"url": "https://example.com"}])
    assert result == "snap_123"
    mock_save.assert_called_once()


@patch('collectors.brightdata_utils.save_json_atomic')
@patch('collectors.brightdata_utils.requests.post')
def test_trigger_collection_no_snapshot_id(mock_post, mock_save):
    """trigger_collection should raise ValueError if no snapshot_id."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {}
    mock_resp.raise_for_status = MagicMock()
    mock_post.return_value = mock_resp

    with pytest.raises(ValueError, match="No snapshot_id"):
        trigger_collection("dataset_abc", [{"url": "https://example.com"}])


@patch('collectors.brightdata_utils._check_progress')
def test_poll_snapshot_ready(mock_progress):
    """poll_snapshot should return True when snapshot is ready."""
    mock_progress.return_value = "ready"
    mock_sleep = MagicMock()

    result = poll_snapshot("snap_123", timeout=30, poll_interval=5,
                           sleep_func=mock_sleep)
    assert result is True


@patch('collectors.brightdata_utils._check_progress')
def test_poll_snapshot_transitions_to_ready(mock_progress):
    """poll_snapshot should poll until status is ready."""
    mock_progress.side_effect = ["starting", "running", "ready"]
    mock_sleep = MagicMock()

    result = poll_snapshot("snap_123", timeout=60, poll_interval=5,
                           sleep_func=mock_sleep)
    assert result is True
    assert mock_sleep.call_count == 2


@patch('collectors.brightdata_utils._check_progress')
def test_poll_snapshot_timeout(mock_progress):
    """poll_snapshot should return False on timeout."""
    mock_progress.return_value = "running"
    mock_sleep = MagicMock()

    result = poll_snapshot("snap_123", timeout=15, poll_interval=10,
                           sleep_func=mock_sleep)
    assert result is False


@patch('collectors.brightdata_utils._check_progress')
def test_poll_snapshot_failed(mock_progress):
    """poll_snapshot should raise RuntimeError on failure."""
    mock_progress.return_value = "failed"
    mock_sleep = MagicMock()

    with pytest.raises(RuntimeError, match="failed"):
        poll_snapshot("snap_123", timeout=30, poll_interval=5,
                      sleep_func=mock_sleep)


@patch('collectors.brightdata_utils.requests.get')
def test_download_snapshot_success(mock_get):
    """download_snapshot should return parsed data."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [{"id": "1"}, {"id": "2"}]
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    result = download_snapshot("snap_123")
    assert len(result) == 2
    assert result[0]["id"] == "1"
