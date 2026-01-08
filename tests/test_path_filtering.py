"""Unit tests for should_process_file function."""

import pytest
from pathlib import Path
from i18n_validator.cli import should_process_file


@pytest.mark.unit
@pytest.mark.parametrize("filepath,translation_dir,should_match,description", [
    ("translations/en/common.json", "translations/", True, "relative path in translations"),
    ("translations/fr/errors.json", "translations/", True, "another file in translations"),
    ("src/config.json", "translations/", False, "file outside translations"),
    ("locales/en.json", "locales/", True, "different directory name"),
    ("locales/en-US/translation.json", "locales/", True, "nested directory"),
    ("translations/locales/en/common.json", "translations/", True, "deeply nested"),
    ("my_translations/en.json", "translations/", False, "similar but different dir name"),
    ("config/translations.json", "translations/", False, "dir name in filename"),
    ("/abs/path/translations/en.json", "translations/", True, "absolute path"),
    ("translations/en/common.json", "translations", True, "dir without trailing slash"),
    ("public/i18n/en.json", "public/i18n/", True, "nested dir path"),
])
def test_should_process_file(filepath, translation_dir, should_match, description):
    """Test path filtering with various file paths."""
    result = should_process_file(Path(filepath), [translation_dir])
    assert result == should_match, f"Failed for: {description}"


@pytest.mark.unit
def test_process_all_when_no_dirs():
    """Test that all files are processed when no translation_dirs specified."""
    # Empty list should process all files
    assert should_process_file(Path("any/path/file.json"), []) is True
    assert should_process_file(Path("another/file.json"), []) is True


@pytest.mark.unit
def test_windows_paths():
    """Test path filtering with Windows-style backslashes."""
    test_cases = [
        (r"translations\en\common.json", "translations/", True),
        (r"translations\fr\errors.json", "translations/", True),
        (r"src\config.json", "translations/", False),
    ]

    for filepath, trans_dir, expected in test_cases:
        result = should_process_file(Path(filepath), [trans_dir])
        assert result == expected


@pytest.mark.unit
def test_multiple_translation_dirs():
    """Test with multiple translation directories."""
    translation_dirs = ["translations/", "locales/", "i18n/"]

    # Files in any of these dirs should match
    assert should_process_file(Path("translations/en.json"), translation_dirs) is True
    assert should_process_file(Path("locales/fr.json"), translation_dirs) is True
    assert should_process_file(Path("i18n/de.json"), translation_dirs) is True

    # Files outside all dirs should not match
    assert should_process_file(Path("src/config.json"), translation_dirs) is False


@pytest.mark.unit
def test_paths_with_special_characters():
    """Test path filtering with special characters in paths."""
    test_cases = [
        ("translations/en-US/common.json", "translations/", True),
        ("translations/zh_CN/errors.json", "translations/", True),
        ("translations/pt-BR/messages.json", "translations/", True),
        ("translations (copy)/en.json", "translations/", False),  # Different dir
    ]

    for filepath, trans_dir, expected in test_cases:
        result = should_process_file(Path(filepath), [trans_dir])
        assert result == expected, f"Failed for path: {filepath}"


@pytest.mark.unit
def test_edge_case_paths():
    """Test edge cases in path matching."""
    # File at root of translation dir
    assert should_process_file(Path("translations/en.json"), ["translations/"]) is True

    # Very deeply nested
    assert should_process_file(
        Path("translations/v1/locales/en-US/common.json"),
        ["translations/"]
    ) is True

    # Path with dots
    assert should_process_file(Path("translations/en/v1.0.0.json"), ["translations/"]) is True


@pytest.mark.unit
def test_case_sensitivity():
    """Test that path matching is case-sensitive."""
    # These should not match due to case differences
    assert should_process_file(Path("Translations/en.json"), ["translations/"]) is False
    assert should_process_file(Path("translations/en.json"), ["Translations/"]) is False

    # Exact match should work
    assert should_process_file(Path("translations/en.json"), ["translations/"]) is True


@pytest.mark.unit
def test_partial_directory_name_matching():
    """Test that partial directory name matches are handled correctly."""
    # "trans" should not match "translations"
    assert should_process_file(Path("translations/en.json"), ["trans/"]) is False

    # "translations_old" should not match "translations"
    assert should_process_file(Path("translations_old/en.json"), ["translations/"]) is False

    # Exact match should work
    assert should_process_file(Path("translations/en.json"), ["translations/"]) is True


@pytest.mark.unit
def test_empty_path():
    """Test behavior with empty paths."""
    result = should_process_file(Path(""), ["translations/"])
    assert result is False


@pytest.mark.unit
def test_relative_vs_absolute_paths():
    """Test mixing relative and absolute paths."""
    # Relative file path with relative trans_dir
    assert should_process_file(Path("translations/en.json"), ["translations/"]) is True

    # Absolute file path with relative trans_dir
    assert should_process_file(
        Path("/home/user/project/translations/en.json"),
        ["translations/"]
    ) is True

