"""Unit tests for find_empty_translations function."""

import pytest
from i18n_validator.cli import find_empty_translations


@pytest.mark.unit
@pytest.mark.parametrize("data,expected_count,description", [
    ({"hello": "Hello", "bye": "Goodbye"}, 0, "no empty strings"),
    ({"hello": "", "bye": "Goodbye"}, 1, "one empty string"),
    ({"hello": "", "bye": ""}, 2, "all empty strings"),
    ({}, 0, "empty dict"),
    ({"a": "", "b": "", "c": "", "d": "valid"}, 3, "mostly empty"),
    ({"key": "value", "another": "text", "more": "data"}, 0, "all valid"),
])
def test_find_empty_translations(data, expected_count, description):
    """Test find_empty_translations with various data structures."""
    errors = find_empty_translations(data)
    assert len(errors) == expected_count, f"Failed for: {description}"

    # Verify error messages are appropriate
    for error in errors:
        assert error.error_type == "Empty translation"
        assert "empty string" in error.message


def test_find_empty_translations_with_fixture(empty_translation_data):
    """Test with fixture data containing empty strings."""
    errors = find_empty_translations(empty_translation_data)

    # Should find 2 empty strings: "welcome" and "goodbye"
    assert len(errors) == 2

    # Check that the correct keys are identified
    error_keys = [error.key for error in errors]
    assert "welcome" in error_keys
    assert "goodbye" in error_keys
    assert "hello" not in error_keys  # This one has a value


def test_find_empty_translations_valid_data(valid_translation_data):
    """Test with completely valid translation data."""
    errors = find_empty_translations(valid_translation_data)
    assert len(errors) == 0


def test_find_empty_translations_with_plurals(valid_translation_with_plurals):
    """Test that plural translations are not flagged as errors."""
    errors = find_empty_translations(valid_translation_with_plurals)
    assert len(errors) == 0


@pytest.mark.unit
def test_find_empty_translations_non_dict():
    """Test behavior with non-dict input."""
    # Should handle gracefully
    errors = find_empty_translations("not a dict")
    assert len(errors) == 0


@pytest.mark.unit
def test_find_empty_translations_whitespace():
    """Test that whitespace-only strings are not flagged as empty."""
    # Only truly empty strings ("") should be flagged
    data = {
        "truly_empty": "",
        "spaces": "   ",
        "newline": "\n",
        "tab": "\t"
    }
    errors = find_empty_translations(data)

    # Only the truly empty one should be flagged
    assert len(errors) == 1
    assert errors[0].key == "truly_empty"


@pytest.mark.unit
def test_find_empty_translations_unicode():
    """Test with Unicode characters."""
    data = {
        "greeting": "こんにちは",
        "empty": "",
        "emoji": "👋",
        "another_empty": ""
    }
    errors = find_empty_translations(data)

    assert len(errors) == 2
    error_keys = [error.key for error in errors]
    assert "empty" in error_keys
    assert "another_empty" in error_keys
    assert "greeting" not in error_keys
    assert "emoji" not in error_keys

