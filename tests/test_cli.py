"""Integration tests for CLI main function."""

import pytest
from pathlib import Path
from i18n_validator.cli import main


@pytest.mark.integration
def test_cli_with_valid_files(tmp_translation_file, valid_translation_data):
    """Test CLI with valid translation files returns exit code 0."""
    file_path = tmp_translation_file(valid_translation_data)

    exit_code = main([str(file_path)])

    assert exit_code == 0


@pytest.mark.integration
def test_cli_with_invalid_files(tmp_translation_file, empty_translation_data):
    """Test CLI with invalid files returns exit code 1."""
    file_path = tmp_translation_file(empty_translation_data)

    exit_code = main([str(file_path)])

    assert exit_code == 1


@pytest.mark.integration
def test_cli_no_files_provided():
    """Test CLI with no files returns exit code 0."""
    exit_code = main([])
    assert exit_code == 0


@pytest.mark.integration
def test_cli_with_translation_dir_filter(translation_dir_with_files):
    """Test CLI with --translation-dir filter."""
    # Get all JSON files in the directory
    files = list(translation_dir_with_files.rglob("*.json"))
    file_paths = [str(f) for f in files]

    # Run with translation dir filter
    exit_code = main([
        '--translation-dir', str(translation_dir_with_files)
    ] + file_paths)

    # Should fail because errors.json has errors
    assert exit_code == 1


@pytest.mark.integration
def test_cli_without_translation_dir_processes_all(tmp_path):
    """Test that CLI processes all files when no --translation-dir is specified."""
    # Create files in different locations
    trans_file = tmp_path / "translations" / "en.json"
    trans_file.parent.mkdir()
    trans_file.write_text('{"hello": ""}')  # Has error

    other_file = tmp_path / "config.json"
    other_file.write_text('{"setting": "value"}')  # Valid

    # Run without --translation-dir
    exit_code = main([str(trans_file), str(other_file)])

    # Should fail because trans_file has an error
    assert exit_code == 1


@pytest.mark.integration
def test_cli_filters_non_json_files(tmp_path):
    """Test that CLI only processes JSON files."""
    json_file = tmp_path / "test.json"
    json_file.write_text('{"hello": ""}')  # Has error

    txt_file = tmp_path / "test.txt"
    txt_file.write_text('{"hello": ""}')  # Would have error if processed

    # Should only fail due to JSON file
    exit_code = main([str(json_file), str(txt_file)])
    assert exit_code == 1


@pytest.mark.integration
def test_cli_multiple_valid_files(tmp_translation_file):
    """Test CLI with multiple valid files."""
    file1 = tmp_translation_file({"hello": "Hello"}, "file1.json")
    file2 = tmp_translation_file({"bye": "Goodbye"}, "file2.json")
    file3 = tmp_translation_file({"thanks": "Thanks"}, "file3.json")

    exit_code = main([str(file1), str(file2), str(file3)])

    assert exit_code == 0


@pytest.mark.integration
def test_cli_multiple_files_some_invalid(tmp_translation_file):
    """Test CLI with mix of valid and invalid files."""
    valid_file = tmp_translation_file({"hello": "Hello"}, "valid.json")
    invalid_file = tmp_translation_file({"bye": ""}, "invalid.json")

    exit_code = main([str(valid_file), str(invalid_file)])

    # Should fail due to invalid file
    assert exit_code == 1


@pytest.mark.integration
def test_cli_with_nonexistent_file(tmp_path):
    """Test CLI handles nonexistent files gracefully."""
    nonexistent = tmp_path / "does_not_exist.json"

    exit_code = main([str(nonexistent)])

    # Should fail gracefully
    assert exit_code == 1


@pytest.mark.integration
def test_cli_output_format(tmp_translation_file, capsys):
    """Test CLI output format for errors."""
    file_with_errors = tmp_translation_file({
        "empty": "",
        "plural_error": "text_one"
    }, "errors.json")

    exit_code = main([str(file_with_errors)])

    captured = capsys.readouterr()
    output = captured.out

    # Check output contains filename
    assert "errors.json" in output

    # Check output contains error types
    assert "Empty translation" in output
    assert "Plural suffix in value" in output

    # Check output contains the problematic keys
    assert "empty" in output
    assert "plural_error" in output

    assert exit_code == 1


@pytest.mark.integration
def test_cli_with_argv_parameter(tmp_translation_file):
    """Test CLI with explicit argv parameter."""
    file_path = tmp_translation_file({"hello": ""})

    # Call with explicit argv
    exit_code = main([str(file_path)])

    assert exit_code == 1


@pytest.mark.integration
def test_cli_directory_filtering_excludes_files(tmp_path):
    """Test that --translation-dir properly filters files."""
    # Create translation directory
    trans_dir = tmp_path / "translations"
    trans_dir.mkdir()
    trans_file = trans_dir / "en.json"
    trans_file.write_text('{"hello": ""}')  # Has error

    # Create file outside translations
    other_file = tmp_path / "other.json"
    other_file.write_text('{"bye": ""}')  # Has error

    # Run with filter for translations only
    exit_code = main([
        '--translation-dir', str(trans_dir),
        str(trans_file),
        str(other_file)
    ])

    # Should fail because trans_file has error
    # other_file should be ignored
    assert exit_code == 1


@pytest.mark.integration
def test_cli_with_nested_directories(translation_dir_with_files):
    """Test CLI processes files in nested directories."""
    # translation_dir_with_files has files in subdirectories
    all_files = list(translation_dir_with_files.rglob("*.json"))
    file_paths = [str(f) for f in all_files]

    exit_code = main([
        '--translation-dir', str(translation_dir_with_files)
    ] + file_paths)

    # Should find errors in errors.json
    assert exit_code == 1


@pytest.mark.integration
def test_cli_with_unicode_in_errors(tmp_translation_file, capsys):
    """Test CLI handles Unicode characters in output."""
    file_with_unicode = tmp_translation_file({
        "greeting": "",
        "emoji_error": "Hello 👋_one"
    }, "unicode.json")

    exit_code = main([str(file_with_unicode)])

    captured = capsys.readouterr()
    output = captured.out

    # Should handle Unicode in output
    assert "greeting" in output
    assert "emoji_error" in output

    assert exit_code == 1


@pytest.mark.integration
@pytest.mark.slow
def test_cli_with_many_files(tmp_path):
    """Test CLI performance with many files."""
    import json

    # Create 50 files
    files = []
    for i in range(50):
        file_path = tmp_path / f"file_{i}.json"
        if i % 10 == 0:
            # Every 10th file has an error
            file_path.write_text(json.dumps({"key": ""}))
        else:
            file_path.write_text(json.dumps({"key": "value"}))
        files.append(str(file_path))

    exit_code = main(files)

    # Should fail due to files with errors
    assert exit_code == 1


@pytest.mark.integration
def test_cli_argument_parsing():
    """Test that CLI properly parses arguments."""
    # Test with no arguments
    exit_code = main([])
    assert exit_code == 0

    # Test with --translation-dir but no files
    exit_code = main(['--translation-dir', 'some/path'])
    assert exit_code == 0

