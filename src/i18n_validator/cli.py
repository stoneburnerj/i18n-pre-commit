"""CLI for validating i18next translation files."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple


# Regex pattern to detect plural suffixes at the end of translation values
PLURAL_SUFFIXES = re.compile(r'_(zero|one|two|few|many|other)$')

# Exit codes
PASS = 0
FAIL = 1


class ValidationError:
    """Represents a validation error in a translation file."""

    def __init__(self, key: str, error_type: str, message: str):
        self.key = key
        self.error_type = error_type
        self.message = message

    def __str__(self) -> str:
        return f"  - {self.error_type}: \"{self.key}\" - {self.message}"


def find_empty_translations(data: Dict[str, str]) -> List[ValidationError]:
    """
    Find empty translation strings in flat i18next JSON structure.


        data: The JSON data (flat dict of translation keys to values)

    Returns:
        List of ValidationError objects for empty translations
    """
    errors = []

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and value == "":
                errors.append(ValidationError(
                    key=key,
                    error_type="Empty translation",
                    message="translation value is an empty string"
                ))

    return errors


def find_plural_suffix_in_values(data: Dict[str, str]) -> List[ValidationError]:
    """
    Find plural suffixes (_one, _other, etc.) in translation values.

    These suffixes should be in the key name, not the value.
    For example:
        BAD:  "count": "{{count}} item found_one"
        GOOD: "count_one": "{{count}} item found"

    Args:
        data: The JSON data (flat dict of translation keys to values)

    Returns:
        List of ValidationError objects for misplaced plural suffixes
    """
    errors = []

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                match = PLURAL_SUFFIXES.search(value)
                if match:
                    suffix = match.group(0)
                    errors.append(ValidationError(
                        key=key,
                        error_type="Plural suffix in value",
                        message=f"contains \"{suffix}\" (should be in key, not value)"
                    ))

    return errors


def validate_translation_file(filepath: Path) -> Tuple[bool, List[ValidationError]]:
    """
    Validate a single translation JSON file.

    Args:
        filepath: Path to the JSON file to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Run all validation checks
        errors.extend(find_empty_translations(data))
        errors.extend(find_plural_suffix_in_values(data))

    except json.JSONDecodeError as e:
        errors.append(ValidationError(
            key="FILE",
            error_type="JSON Parse Error",
            message=f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}"
        ))
    except Exception as e:
        errors.append(ValidationError(
            key="FILE",
            error_type="Error",
            message=f"Failed to read file: {str(e)}"
        ))

    return (len(errors) == 0, errors)


def should_process_file(filepath: Path, translation_dirs: List[str]) -> bool:
    """
    Determine if a file should be processed based on translation directories.

    Args:
        filepath: Path to the file
        translation_dirs: List of directory paths to check against

    Returns:
        True if the file is within any of the translation directories
    """
    if not translation_dirs:
        # If no directories specified, process all JSON files
        return True

    # Convert filepath to Path object for better comparison
    file_path_obj = Path(filepath).resolve()

    for trans_dir in translation_dirs:
        # Convert translation dir to Path and resolve it
        trans_dir_path = Path(trans_dir).resolve()

        # Check if file is in this directory or its subdirectories
        try:
            # This will raise ValueError if file_path is not relative to trans_dir_path
            file_path_obj.relative_to(trans_dir_path)
            return True
        except ValueError:
            # Not in this directory, continue to next
            continue

    return False


def main(argv: Sequence[str] | None = None) -> int:
    """
    Main entry point for the i18n validator CLI.

    Args:
        argv: Command line arguments (defaults to sys.argv)

    Returns:
        Exit code (0 for success, 1 for validation failures)
    """
    parser = argparse.ArgumentParser(
        prog='validate-i18n',
        description='Validate i18next translation JSON files for common issues.'
    )
    parser.add_argument(
        'filenames',
        nargs='*',
        help='Filenames to process (provided by pre-commit).',
    )
    parser.add_argument(
        '--translation-dirs',
        nargs='+',
        default=[],
        help='One or more directory paths containing translation files.',
    )

    args = parser.parse_args(argv)

    if not args.filenames:
        # No files to check
        return PASS

    exit_code = PASS
    files_with_errors = {}

    for filename in args.filenames:
        filepath = Path(filename)

        # Skip non-JSON files
        if filepath.suffix.lower() != '.json':
            continue

        # Check if file is in translation directories
        if not should_process_file(filepath, args.translation_dirs):
            continue

        # Validate the file
        is_valid, errors = validate_translation_file(filepath)

        if not is_valid:
            exit_code = FAIL
            files_with_errors[filename] = errors

    # Print results
    if files_with_errors:
        print()
        for filename, errors in files_with_errors.items():
            print(f"{filename}:")
            for error in errors:
                print(error)
            print()

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

