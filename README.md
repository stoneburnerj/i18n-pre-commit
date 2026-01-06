# i18n Validator Pre-Commit Hook

A pre-commit hook for validating i18next translation JSON files. This hook helps maintain translation quality by detecting common issues before they get committed.

## What It Checks

This hook validates your i18next translation files for two critical issues:

### 1. Empty Translation Strings
Detects translation keys that have been created but not filled in (empty strings).

**Example of what gets flagged:**
```json
{
  "welcome": "Welcome",
  "goodbye": "",  // ❌ Empty translation
  "thank_you": "Thank you"
}
```

### 2. Plural Suffixes in Values
Catches plural suffixes (`_one`, `_other`, `_few`, `_many`, `_zero`, `_two`) that appear **at the end** of translation values instead of in the keys. In i18next, plural forms should be separate keys with the suffix in the key name, not in the value.

**Example of what gets flagged:**
```json
{
  "{{count}} items_one": "{{count}} item",
  "{{count}} items_other": "{{count}} items_other"  // ❌ Suffix at end of value
}
```

**Correct format:**
```json
{
  "{{count}} items_one": "{{count}} item",
  "{{count}} items_other": "{{count}} items"  // ✅ No suffix in value
}
```

**Note:** The hook only flags suffixes that appear at the end of the translation value. Words like "one" or "other" in the middle of a sentence are not flagged.

## Installation

Add this to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/YOUR-USERNAME/i18n-pre-commit
    rev: v0.1.0  # Use the latest release version
    hooks:
      - id: validate-i18n
        args: [--translation-dirs, locales/]
```

Then install the pre-commit hooks:

```bash
pre-commit install
```

## Configuration

### Specifying Translation Directories

Use the `--translation-dirs` argument to specify one or more directories containing your translation files. This ensures the hook only runs on relevant JSON files.

**Single directory:**
```yaml
- id: validate-i18n
  args: [--translation-dirs, locales/]
```

**Multiple directories:**
```yaml
- id: validate-i18n
  args: [--translation-dirs, locales/, public/i18n/, src/translations/]
```

**All JSON files (not recommended):**
```yaml
- id: validate-i18n
  # No args - will check all JSON files
```

## Usage

Once installed, the hook will automatically run when you commit changes to JSON files in your specified translation directories.

### Example Output

When validation issues are found:

```
Validate i18next translations...................................Failed
- hook id: validate-i18n
- exit code: 1

locales/en/common.json:
  - Empty translation: "welcome" - translation value is an empty string
  - Empty translation: "cancel" - translation value is an empty string
  - Plural suffix in value: "{{count}} notifications_one" - contains "_one" (should be in key, not value)

locales/fr/errors.json:
  - Empty translation: "merci" - translation value is an empty string
  - Plural suffix in value: "{{count}} résultats_other" - contains "_other" (should be in key, not value)
```

When all translations are valid:

```
Validate i18next translations...................................Passed
```

### Manual Execution

Run the hook manually on all files:

```bash
pre-commit run validate-i18n --all-files
```

Run on specific files:

```bash
pre-commit run validate-i18n --files locales/en/common.json
```

## Development

### Local Testing

To test the hook locally before publishing:

1. Clone this repository
2. Create sample translation files with intentional errors
3. Use `pre-commit try-repo`:

```bash
pre-commit try-repo /path/to/i18n-pre-commit validate-i18n --files test.json --verbose
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests (if available)
pytest
```

## Requirements

- Python >= 3.8
- No external dependencies (uses Python standard library only)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Author

Created to help maintain i18next translation quality in development workflows.

## Acknowledgments

This hook was built following the [pre-commit hook creation guide](https://pre-commit.com/#creating-new-hooks) and inspired by best practices from the pre-commit community.
