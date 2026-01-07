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
  - repo: https://github.com/stoneburnerj/i18n-pre-commit
    rev: v0.1.0  # Use the latest release version
    hooks:
      - id: validate-i18n
        types: [json]
        args: [--translation-dir, locales/]
```

Then install the pre-commit hooks:

```bash
pre-commit install
```

## Configuration

### Specifying Translation Directory

Use the `--translation-dir` argument to specify a directory containing your translation files. This ensures the hook only runs on relevant JSON files.

```yaml
- id: validate-i18n
  types: [json]
  args: [--translation-dir, locales/]
```

**All JSON files (not recommended):**
```yaml
- id: validate-i18n
  # No args - will check all JSON files
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.
