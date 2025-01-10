#!/usr/bin/env python
import subprocess
import sys


def run_tests():
    # Run pytest tests
    pytest_result = subprocess.run(["pytest"], capture_output=True, text=True)
    print(pytest_result.stdout)

    # Run unittest tests
    unittest_result = subprocess.run(
        [
            "python",
            "-m",
            "unittest",
            "discover",
            "-s",
            "backend/tests",
            "-p",
            "test_*.py",
        ],
        capture_output=True,
        text=True,
    )
    print(unittest_result.stdout)

    # Return non-zero if either test suite failed
    return pytest_result.returncode or unittest_result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
