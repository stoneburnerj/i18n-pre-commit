"""Shared pytest fixtures for i18n-validator tests."""

import json
import pytest
from pathlib import Path


@pytest.fixture
def valid_translation_data():
    """Sample valid translation data."""
    return {
        "hello": "Hello",
        "goodbye": "Goodbye",
        "welcome": "Welcome to our application"
    }


@pytest.fixture
def valid_translation_with_plurals():
    """Valid translation data with correct plural format."""
    return {
        "{{count}} items_one": "{{count}} item",
        "{{count}} items_other": "{{count}} items",
        "{{count}} users_one": "1 user",
        "{{count}} users_other": "{{count}} users"
    }


@pytest.fixture
def empty_translation_data():
    """Translation data with empty strings."""
    return {
        "welcome": "",
        "hello": "Hello",
        "goodbye": "",
        "thanks": "Thank you"
    }


@pytest.fixture
def plural_error_data():
    """Translation data with plural suffixes in values."""
    return {
        "count": "{{count}} items_one",
        "total": "{{total}} results_other",
        "valid": "This is valid"
    }


@pytest.fixture
def mixed_error_data():
    """Translation data with multiple error types."""
    return {
        "empty": "",
        "plural_error": "{{count}} items_one",
        "another_empty": "",
        "valid": "Valid translation"
    }


@pytest.fixture
def tmp_translation_file(tmp_path):
    """Create a temporary translation JSON file for testing.

    Usage:
        file_path = tmp_translation_file({"hello": "Hello"})
    """
    def _create_file(content, filename="test.json"):
        file_path = tmp_path / filename
        file_path.write_text(json.dumps(content, indent=2))
        return file_path
    return _create_file


@pytest.fixture
def translation_dir_with_files(tmp_path):
    """Create a temporary directory with multiple translation files."""
    trans_dir = tmp_path / "translations"
    trans_dir.mkdir()

    # Create valid file
    valid_file = trans_dir / "valid.json"
    valid_file.write_text(json.dumps({
        "hello": "Hello",
        "goodbye": "Goodbye"
    }, indent=2))

    # Create file with errors
    error_file = trans_dir / "errors.json"
    error_file.write_text(json.dumps({
        "welcome": "",
        "count": "{{count}} items_one"
    }, indent=2))

    # Create another valid file in subdirectory
    en_dir = trans_dir / "en"
    en_dir.mkdir()
    en_file = en_dir / "common.json"
    en_file.write_text(json.dumps({
        "save": "Save",
        "cancel": "Cancel"
    }, indent=2))

    return trans_dir

