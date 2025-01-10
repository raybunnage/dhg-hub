"""Test module for verifying import functionality and basic setup."""

import sys
import os
from pathlib import Path

# Adjust the path to point to backend from the new location
backend_path = Path(__file__).parent.parent
sys.path.append(str(backend_path))


def test_imports():
    """Test that we can import our main package and its submodules."""
    try:
        import flask
        import flask_cors
        import flask_sqlalchemy
        import sqlalchemy
        import pytest
        import dotenv

        assert True
    except ImportError as e:
        assert False, f"Failed to import required package: {str(e)}"


def test_basic_math():
    """A simple test to verify pytest is working."""
    assert 1 + 1 == 2, "Basic math test failed"
