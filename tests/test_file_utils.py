"""Tests for collectors.file_utils module."""

import json
import os
import tempfile
import pytest

from collectors.file_utils import save_json_atomic, load_json_safe


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as d:
        yield d


def test_save_json_atomic_creates_file(tmp_dir):
    """save_json_atomic should create a new JSON file."""
    filepath = os.path.join(tmp_dir, "test.json")
    data = {"key": "value", "number": 42}

    save_json_atomic(data, filepath)

    assert os.path.exists(filepath)
    with open(filepath, 'r') as f:
        loaded = json.load(f)
    assert loaded == data


def test_save_json_atomic_overwrites_existing(tmp_dir):
    """save_json_atomic should overwrite existing files atomically."""
    filepath = os.path.join(tmp_dir, "test.json")

    save_json_atomic({"v": 1}, filepath)
    save_json_atomic({"v": 2}, filepath)

    with open(filepath, 'r') as f:
        loaded = json.load(f)
    assert loaded == {"v": 2}


def test_save_json_atomic_creates_directories(tmp_dir):
    """save_json_atomic should create parent directories if needed."""
    filepath = os.path.join(tmp_dir, "sub", "dir", "test.json")
    data = [1, 2, 3]

    save_json_atomic(data, filepath)

    assert os.path.exists(filepath)
    with open(filepath, 'r') as f:
        loaded = json.load(f)
    assert loaded == data


def test_save_json_atomic_no_temp_file_on_success(tmp_dir):
    """No temporary files should remain after a successful save."""
    filepath = os.path.join(tmp_dir, "test.json")
    save_json_atomic({"ok": True}, filepath)

    files = os.listdir(tmp_dir)
    assert files == ["test.json"]


def test_save_json_atomic_handles_unicode(tmp_dir):
    """save_json_atomic should handle Unicode characters correctly."""
    filepath = os.path.join(tmp_dir, "unicode.json")
    data = {"text": "こんにちは世界 🌍"}

    save_json_atomic(data, filepath)

    with open(filepath, 'r') as f:
        loaded = json.load(f)
    assert loaded == data


def test_load_json_safe_returns_default_for_missing():
    """load_json_safe should return default when file doesn't exist."""
    result = load_json_safe("/nonexistent/path/file.json", default=[])
    assert result == []


def test_load_json_safe_returns_none_by_default():
    """load_json_safe should return None when file doesn't exist and no default."""
    result = load_json_safe("/nonexistent/path/file.json")
    assert result is None


def test_load_json_safe_loads_existing_file(tmp_dir):
    """load_json_safe should load and parse an existing JSON file."""
    filepath = os.path.join(tmp_dir, "test.json")
    data = {"items": [1, 2, 3]}
    with open(filepath, 'w') as f:
        json.dump(data, f)

    result = load_json_safe(filepath)
    assert result == data


def test_load_json_safe_raises_on_invalid_json(tmp_dir):
    """load_json_safe should raise JSONDecodeError on invalid JSON."""
    filepath = os.path.join(tmp_dir, "bad.json")
    with open(filepath, 'w') as f:
        f.write("not valid json {{{")

    with pytest.raises(json.JSONDecodeError):
        load_json_safe(filepath)
