#!/usr/bin/env python3
"""
Utility script to find all test and tests directories in the project.
Excludes virtual environments and other common non-project directories.

Usage:
    python scripts/find_test_dirs.py
"""

from pathlib import Path
import os


def find_test_directories(start_path="."):
    # Convert to absolute path for clearer output
    start_path = Path(start_path).resolve()

    # Lists to store results
    test_dirs = []
    tests_dirs = []

    # Skip virtual environment directories and cache directories
    exclude_dirs = {
        ".venv",
        "venv",
        ".git",
        "__pycache__",
        "node_modules",
        ".mypy_cache",
        ".pytest_cache",
    }

    for root, dirs, _ in os.walk(start_path):
        # Skip if any parent directory is in exclude_dirs
        if any(excluded in Path(root).parts for excluded in exclude_dirs):
            continue

        path = Path(root)

        for dir_name in ["test", "tests"]:
            if dir_name in dirs:
                full_path = path / dir_name
                try:
                    # Check if directory exists and is accessible
                    if full_path.exists() and os.access(full_path, os.R_OK):
                        if dir_name == "test":
                            test_dirs.append(str(full_path))
                        else:
                            tests_dirs.append(str(full_path))
                    else:
                        print(
                            f"\nWarning: Directory exists but may not be accessible: {full_path}"
                        )
                        print(f"Exists: {full_path.exists()}")
                        print(f"Readable: {os.access(str(full_path), os.R_OK)}")
                except Exception as e:
                    print(f"\nError checking directory {full_path}: {e}")

    print(f"\nFound {len(test_dirs)} 'test' directories:")
    for d in test_dirs:
        print(f"- {d}")

    print(f"\nFound {len(tests_dirs)} 'tests' directories:")
    for d in tests_dirs:
        print(f"- {d}")

    return test_dirs, tests_dirs


if __name__ == "__main__":
    find_test_directories()
