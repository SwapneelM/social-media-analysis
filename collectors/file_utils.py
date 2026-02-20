"""
File utility functions for crash-safe data persistence.

Provides atomic JSON save operations that write to a temporary file
first, then use os.replace() for an atomic rename. This ensures that
data files are never left in a corrupted state if the process crashes
mid-write.
"""

import json
import os
import tempfile


def save_json_atomic(data, filepath):
    """
    Atomically save data as JSON to the specified filepath.

    Writes to a temporary file in the same directory, then atomically
    replaces the target file using os.replace(). This guarantees that
    the file is either fully written or not modified at all.

    Args:
        data: Any JSON-serializable Python object.
        filepath: Path to the target JSON file.

    Raises:
        OSError: If the directory cannot be created or file cannot be written.
        TypeError: If data is not JSON-serializable.
    """
    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(
        suffix='.tmp',
        dir=dirpath or '.'
    )
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
        os.replace(tmp_path, filepath)
    except Exception:
        # Clean up temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def load_json_safe(filepath, default=None):
    """
    Safely load JSON from a file, returning a default if the file doesn't exist.

    Args:
        filepath: Path to the JSON file.
        default: Value to return if the file doesn't exist (default: None).

    Returns:
        Parsed JSON data, or the default value if file doesn't exist.

    Raises:
        json.JSONDecodeError: If the file exists but contains invalid JSON.
    """
    if not os.path.exists(filepath):
        return default
    with open(filepath, 'r') as f:
        return json.load(f)
