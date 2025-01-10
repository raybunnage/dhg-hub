"""Test module for verifying import functionality and basic setup."""

import pytest
import os
from pathlib import Path


def test_core_imports():
    """Test core module imports."""
    from dhg.core import config
    from dhg.core import exceptions

    assert True


def test_service_imports():
    """Test service module imports."""
    from dhg.services.supabase import service

    assert True


def test_package_structure():
    """Test package structure."""
    base = Path(__file__).parent.parent / "src" / "dhg"
    assert (base / "core").exists()
    assert (base / "services").exists()
