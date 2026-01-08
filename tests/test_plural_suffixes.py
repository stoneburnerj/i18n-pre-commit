"""Unit tests for find_plural_suffix_in_values function."""

import pytest
from i18n_validator.cli import find_plural_suffix_in_values


@pytest.mark.unit
@pytest.mark.parametrize("value,should_fail,description", [
    ("{{count}} item", False, "valid singular"),
    ("{{count}} item_one", True, "suffix _one at end"),
    ("{{count}} items_other", True, "suffix _other at end"),
    ("{{count}} items_few", True, "suffix _few at end"),
    ("{{count}} items_many", True, "suffix _many at end"),
    ("{{count}} items_zero", True, "suffix _zero at end"),
    ("{{count}} items_two", True, "suffix _two at end"),
    ("Choose one option", False, "word 'one' in middle"),
    ("The other day", False, "word 'other' in middle"),
    ("A few items", False, "word 'few' in middle"),
    ("Many thanks", False, "word 'many' in middle"),
    ("Zero tolerance", False, "word 'zero' in middle"),
    ("Two options", False, "word 'two' in middle"),
    ("", False, "empty string (different error type)"),
    ("_one", True, "just the suffix"),
    ("text_one_more", False, "suffix in middle, not at end"),
])
def test_plural_suffix_detection(value, should_fail, description):
    """Test plural suffix detection with various inputs."""
    data = {"test_key": value}
    errors = find_plural_suffix_in_values(data)

    if should_fail:
        assert len(errors) == 1, f"Expected error for: {description} (value: '{value}')"
        assert "_" in errors[0].message
        assert "should be in key" in errors[0].message
    else:
        assert len(errors) == 0, f"Unexpected error for: {description} (value: '{value}')"


def test_plural_suffix_with_fixture(plural_error_data):
    """Test with fixture data containing plural errors."""
    errors = find_plural_suffix_in_values(plural_error_data)

    # Should find 2 plural errors: "count" and "total"
    assert len(errors) == 2

    error_keys = [error.key for error in errors]
    assert "count" in error_keys
    assert "total" in error_keys
    assert "valid" not in error_keys


def test_plural_suffix_valid_data(valid_translation_with_plurals):
    """Test with correctly formatted plural translations."""
    errors = find_plural_suffix_in_values(valid_translation_with_plurals)
    assert len(errors) == 0


@pytest.mark.unit
def test_multiple_suffixes_in_one_value():
    """Test detection when a value contains multiple plural suffixes."""
    data = {"key": "Text with _one and also _other"}
    errors = find_plural_suffix_in_values(data)

    # Should detect the _other at the end
    assert len(errors) == 1
    assert "_other" in errors[0].message


@pytest.mark.unit
def test_case_sensitivity():
    """Test that suffix detection is case-sensitive."""
    data = {
        "lowercase": "{{count}} items_one",
        "uppercase": "{{count}} items_ONE",
        "mixed": "{{count}} items_One"
    }
    errors = find_plural_suffix_in_values(data)

    # Only lowercase should be detected
    assert len(errors) == 1
    assert errors[0].key == "lowercase"


@pytest.mark.unit
def test_suffix_with_special_characters():
    """Test suffix detection with special characters nearby."""
    data = {
        "with_period": "{{count}} items_one.",
        "with_exclamation": "{{count}} items_one!",
        "with_question": "{{count}} items_one?",
        "pure_suffix": "{{count}} items_one"
    }
    errors = find_plural_suffix_in_values(data)

    # Only the pure suffix at the end should be detected
    assert len(errors) == 1
    assert errors[0].key == "pure_suffix"


@pytest.mark.unit
def test_unicode_with_suffix():
    """Test suffix detection with Unicode characters."""
    data = {
        "unicode_valid": "こんにちは",
        "unicode_with_suffix": "Привет_one",
        "emoji_with_suffix": "Hello 👋_other"
    }
    errors = find_plural_suffix_in_values(data)

    assert len(errors) == 2
    error_keys = [error.key for error in errors]
    assert "unicode_with_suffix" in error_keys
    assert "emoji_with_suffix" in error_keys


@pytest.mark.unit
def test_all_plural_forms():
    """Test that all i18next plural forms are detected."""
    data = {
        "form_zero": "text_zero",
        "form_one": "text_one",
        "form_two": "text_two",
        "form_few": "text_few",
        "form_many": "text_many",
        "form_other": "text_other",
        "valid": "text without suffix"
    }
    errors = find_plural_suffix_in_values(data)

    # All 6 plural forms should be detected
    assert len(errors) == 6

    detected_forms = set()
    for error in errors:
        if "_zero" in error.message:
            detected_forms.add("zero")
        elif "_one" in error.message:
            detected_forms.add("one")
        elif "_two" in error.message:
            detected_forms.add("two")
        elif "_few" in error.message:
            detected_forms.add("few")
        elif "_many" in error.message:
            detected_forms.add("many")
        elif "_other" in error.message:
            detected_forms.add("other")

    assert detected_forms == {"zero", "one", "two", "few", "many", "other"}


@pytest.mark.unit
def test_non_dict_input():
    """Test behavior with non-dict input."""
    errors = find_plural_suffix_in_values("not a dict")
    assert len(errors) == 0

