# Bash Function Contracts: Local Template Zip

**Feature**: 001-local-template-zip
**Date**: 2025-10-22
**Purpose**: Define interface contracts for bash functions implementing local template support

## Overview

This document defines the input/output contracts, error codes, and side effects for all bash functions in the local template feature.

## Library: template-finder.sh

### find_local_templates()

**Purpose**: Find all template zip files in the current directory matching the naming pattern

**Signature**:
```bash
find_local_templates()
```

**Inputs**:
- None (uses current working directory via `$PWD`)

**Outputs**:
- **stdout**: Newline-separated list of matching template filenames (basenames only, not full paths)
- **stderr**: None
- **Return Code**:
  - `0`: Success (found 0 or more templates)
  - Never fails

**Example Usage**:
```bash
templates=$(find_local_templates)
if [ -z "$templates" ]; then
    echo "No templates found"
fi
```

**Example Output**:
```
spec-kit-template-claude-sh-v0.0.78.zip
spec-kit-template-claude-py-v0.0.78.zip
```

**Side Effects**: None

**Dependencies**: ls, grep (or bash globbing)

---

### parse_template_filename()

**Purpose**: Extract template components (arg1, arg2, version) from a filename

**Signature**:
```bash
parse_template_filename <filename>
```

**Inputs**:
- `$1`: Template filename (string, basename only)

**Outputs**:
- **stdout**: Space-separated values: `<arg1> <arg2> <version>`
- **stderr**: Error message if filename doesn't match pattern
- **Return Code**:
  - `0`: Success (valid filename)
  - `1`: Invalid filename format

**Example Usage**:
```bash
if components=$(parse_template_filename "spec-kit-template-claude-sh-v0.0.78.zip"); then
    read -r arg1 arg2 version <<< "$components"
    echo "Args: $arg1-$arg2, Version: $version"
else
    echo "Invalid template filename" >&2
    exit 1
fi
```

**Example Output**:
```
claude sh 0.0.78
```

**Side Effects**: None

**Dependencies**: sed, grep

---

### filter_templates_by_args()

**Purpose**: Filter template list to only those matching specified arguments

**Signature**:
```bash
filter_templates_by_args <arg1> <arg2> <template1> [template2...]
```

**Inputs**:
- `$1`: First argument to match (string)
- `$2`: Second argument to match (string)
- `$3...`: Template filenames to filter (strings)

**Outputs**:
- **stdout**: Newline-separated list of matching template filenames
- **stderr**: None
- **Return Code**:
  - `0`: Success (found 0 or more matches)
  - Never fails

**Example Usage**:
```bash
all_templates=(
    "spec-kit-template-claude-sh-v0.0.78.zip"
    "spec-kit-template-claude-py-v0.0.78.zip"
)

matches=$(filter_templates_by_args "claude" "sh" "${all_templates[@]}")
echo "$matches"  # Only claude-sh templates
```

**Example Output**:
```
spec-kit-template-claude-sh-v0.0.78.zip
```

**Side Effects**: None

**Dependencies**: parse_template_filename()

---

### select_latest_template()

**Purpose**: From a list of templates with same arguments, select the one with highest version

**Signature**:
```bash
select_latest_template <template1> [template2...]
```

**Inputs**:
- `$1...`: Template filenames (all should have same arg1/arg2, different versions)

**Outputs**:
- **stdout**: Single template filename with highest version
- **stderr**: None
- **Return Code**:
  - `0`: Success (selected template)
  - `1`: No templates provided

**Example Usage**:
```bash
templates=(
    "spec-kit-template-claude-sh-v0.0.78.zip"
    "spec-kit-template-claude-sh-v0.0.79.zip"
    "spec-kit-template-claude-sh-v0.0.77.zip"
)

latest=$(select_latest_template "${templates[@]}")
echo "$latest"  # v0.0.79
```

**Example Output**:
```
spec-kit-template-claude-sh-v0.0.79.zip
```

**Side Effects**: None

**Dependencies**: parse_template_filename(), compare_versions()

---

### validate_zip_integrity()

**Purpose**: Verify that a zip file is valid and can be extracted

**Signature**:
```bash
validate_zip_integrity <zip_file>
```

**Inputs**:
- `$1`: Path to zip file (string, can be relative or absolute)

**Outputs**:
- **stdout**: None
- **stderr**: Error message if validation fails
- **Return Code**:
  - `0`: Valid zip file
  - `1`: Invalid or corrupted zip file

**Example Usage**:
```bash
if validate_zip_integrity "template.zip"; then
    echo "Valid template"
else
    echo "Corrupted template" >&2
    exit 1
fi
```

**Example Error Output** (stderr):
```
Error: Invalid or corrupted zip file: template.zip
```

**Side Effects**: None (unzip -t doesn't extract files)

**Dependencies**: unzip

---

### extract_template()

**Purpose**: Extract template zip file to target directory

**Signature**:
```bash
extract_template <zip_file> <target_dir>
```

**Inputs**:
- `$1`: Path to zip file (string)
- `$2`: Target extraction directory (string, will be created if doesn't exist)

**Outputs**:
- **stdout**: None
- **stderr**: Error message if extraction fails
- **Return Code**:
  - `0`: Extraction successful
  - `1`: Extraction failed

**Example Usage**:
```bash
if extract_template "template.zip" "/path/to/feature"; then
    echo "Template extracted successfully"
else
    echo "Extraction failed" >&2
    exit 1
fi
```

**Example Error Output** (stderr):
```
Error: Failed to extract template: template.zip
```

**Side Effects**: Creates/modifies files in target directory

**Dependencies**: unzip, mkdir

---

### prompt_template_selection()

**Purpose**: Display interactive menu for user to select from available templates

**Signature**:
```bash
prompt_template_selection <template1> [template2...]
```

**Inputs**:
- `$1...`: Template filenames to display as options
- stdin: User input (number selection)

**Outputs**:
- **stdout**: Selected template filename
- **stderr**: Prompt and menu (displayed to user)
- **Return Code**:
  - `0`: User made valid selection
  - `1`: No templates provided or user cancelled

**Example Usage**:
```bash
templates=(
    "spec-kit-template-claude-sh-v0.0.78.zip"
    "spec-kit-template-claude-py-v0.0.78.zip"
)

selected=$(prompt_template_selection "${templates[@]}")
echo "User selected: $selected"
```

**Example stderr Output** (shown to user):
```
Multiple templates available. Please select one:
1) spec-kit-template-claude-sh-v0.0.78.zip
2) spec-kit-template-claude-py-v0.0.78.zip
Enter number:
```

**Example stdout Output** (after user enters "1"):
```
spec-kit-template-claude-sh-v0.0.78.zip
```

**Side Effects**: None (besides displaying to terminal)

**Dependencies**: bash `select` built-in

---

### show_no_match_error()

**Purpose**: Display error message when no template matches requested arguments

**Signature**:
```bash
show_no_match_error <requested_args> <template1> [template2...]
```

**Inputs**:
- `$1`: Requested arguments (string, e.g., "claude sh")
- `$2...`: Available template filenames to list

**Outputs**:
- **stdout**: None
- **stderr**: Formatted error message with available options
- **Return Code**: `0` (always succeeds at showing error)

**Example Usage**:
```bash
requested="claude sh"
available=(
    "spec-kit-template-claude-py-v0.0.78.zip"
    "spec-kit-template-test-js-v1.0.0.zip"
)

show_no_match_error "$requested" "${available[@]}"
exit 1
```

**Example Output** (stderr):
```
Error: No template found matching arguments: claude sh

Available templates:
  - claude-py (version 0.0.78)
  - test-js (version 1.0.0)

Please update .specify/config with correct TEMPLATE_ARGS
or place the required template in the current directory.
```

**Side Effects**: None

**Dependencies**: parse_template_filename()

---

## Library: semver.sh

### compare_versions()

**Purpose**: Compare two semantic versions

**Signature**:
```bash
compare_versions <version1> <version2>
```

**Inputs**:
- `$1`: First version (string, e.g., "0.0.78" or "v0.0.78")
- `$2`: Second version (string, same format)

**Outputs**:
- **stdout**: Comparison result
  - `"1"`: version1 > version2
  - `"0"`: version1 == version2
  - `"-1"`: version1 < version2
- **stderr**: None
- **Return Code**: `0` (always succeeds)

**Example Usage**:
```bash
result=$(compare_versions "0.0.79" "0.0.78")
if [ "$result" = "1" ]; then
    echo "First version is newer"
elif [ "$result" = "0" ]; then
    echo "Versions are equal"
else
    echo "Second version is newer"
fi
```

**Example Outputs**:
```bash
compare_versions "1.0.0" "0.9.9"   # Output: 1
compare_versions "0.0.78" "0.0.78" # Output: 0
compare_versions "0.0.77" "0.0.78" # Output: -1
compare_versions "v1.2.3" "1.2.3"  # Output: 0 (handles 'v' prefix)
```

**Side Effects**: None

**Dependencies**: None (pure bash)

---

### normalize_version()

**Purpose**: Strip 'v' prefix from version string

**Signature**:
```bash
normalize_version <version>
```

**Inputs**:
- `$1`: Version string (e.g., "v0.0.78" or "0.0.78")

**Outputs**:
- **stdout**: Version without 'v' prefix (e.g., "0.0.78")
- **stderr**: None
- **Return Code**: `0` (always succeeds)

**Example Usage**:
```bash
normalized=$(normalize_version "v0.0.78")
echo "$normalized"  # 0.0.78
```

**Side Effects**: None

**Dependencies**: None (bash parameter expansion)

---

## Library: config-reader.sh

### read_template_args()

**Purpose**: Read template arguments from .specify/config file

**Signature**:
```bash
read_template_args
```

**Inputs**:
- None (reads from `$REPO_ROOT/.specify/config`)

**Outputs**:
- **stdout**: Template arguments (string, e.g., "claude sh") or empty string if not found
- **stderr**: None
- **Return Code**:
  - `0`: Config file exists and was read (args may be empty)
  - `1`: Config file doesn't exist

**Example Usage**:
```bash
if args=$(read_template_args); then
    if [ -n "$args" ]; then
        echo "Using template args: $args"
    else
        echo "Config exists but TEMPLATE_ARGS not set"
    fi
else
    echo "No config file found, will prompt user"
fi
```

**Example Output**:
```
claude sh
```

**Side Effects**: None

**Dependencies**: grep, source (if using bash source method)

---

### validate_template_args()

**Purpose**: Validate that template arguments are in correct format

**Signature**:
```bash
validate_template_args <args>
```

**Inputs**:
- `$1`: Template arguments string (e.g., "claude sh")

**Outputs**:
- **stdout**: None
- **stderr**: Error message if validation fails
- **Return Code**:
  - `0`: Valid arguments
  - `1`: Invalid arguments

**Example Usage**:
```bash
args="claude sh"
if validate_template_args "$args"; then
    echo "Valid args"
else
    echo "Invalid args format" >&2
    exit 1
fi
```

**Validation Rules**:
- Must not be empty
- Must contain exactly 2 space-separated words
- Each word must match pattern: `[a-zA-Z0-9-]+`

**Example Error Output** (stderr):
```
Error: Invalid template arguments format
Expected: "<arg1> <arg2>" (e.g., "claude sh")
Got: "claude"
```

**Side Effects**: None

**Dependencies**: wc, grep

---

## Error Codes

**Standard Exit Codes**:
- `0`: Success
- `1`: General error
- `2`: Misuse of command (invalid arguments)

**Custom Exit Codes** (not used, stick to 0/1 for simplicity in bash):
None

---

## Integration Contract

### Modified create-new-feature.sh

**New section** (inserted before line 194):

```bash
# Source template library
source "$REPO_ROOT/.specify/scripts/bash/lib/template-finder.sh"
source "$REPO_ROOT/.specify/scripts/bash/lib/semver.sh"
source "$REPO_ROOT/.specify/scripts/bash/lib/config-reader.sh"

# Attempt to find and use local template
find_and_use_local_template() {
    local feature_dir="$1"

    # Try to read configured template arguments
    local template_args
    if template_args=$(read_template_args); then
        if [ -n "$template_args" ]; then
            read -r arg1 arg2 <<< "$template_args"
        fi
    fi

    # Find all local templates
    local all_templates
    all_templates=$(find_local_templates)

    if [ -z "$all_templates" ]; then
        echo "Error: No local template files found in current directory" >&2
        echo "Please download a template zip file from GitHub releases" >&2
        echo "and place it in the current directory." >&2
        return 1
    fi

    # Determine which template to use
    local selected_template
    if [ -n "$arg1" ] && [ -n "$arg2" ]; then
        # Filter by arguments
        local matches
        matches=$(filter_templates_by_args "$arg1" "$arg2" $all_templates)

        if [ -z "$matches" ]; then
            show_no_match_error "$arg1 $arg2" $all_templates
            return 1
        fi

        # Select latest version if multiple matches
        selected_template=$(select_latest_template $matches)
    else
        # Interactive selection
        selected_template=$(prompt_template_selection $all_templates)
    fi

    # Validate and extract
    if ! validate_zip_integrity "$selected_template"; then
        return 1
    fi

    if ! extract_template "$selected_template" "$feature_dir"; then
        return 1
    fi

    echo "Using local template: $selected_template" >&2
    return 0
}

# Call the function
if ! find_and_use_local_template "$FEATURE_DIR"; then
    exit 1
fi
```

**Changed behavior**:
- **Before**: Always copies template from `.specify/templates/spec-template.md`
- **After**: Finds and extracts from local zip file in current directory
- **Backward compatibility**: Not preserved (fails if no local template found, per spec)

---

## Testing Contracts

### Unit Test Structure (bats)

**Test file naming**: `test-{library-name}.bats`

**Test naming convention**: `@test "{function_name}: {scenario}"`

**Example**:
```bash
@test "compare_versions: 1.0.0 > 0.9.9" {
    run compare_versions "1.0.0" "0.9.9"
    [ "$status" -eq 0 ]
    [ "$output" = "1" ]
}
```

**Assertions**:
- `[ "$status" -eq N ]`: Check exit code
- `[ "$output" = "expected" ]`: Check stdout
- `[ "${lines[0]}" = "expected" ]`: Check first line of output

**Setup/Teardown**:
- `setup()`: Run before each test
- `teardown()`: Run after each test

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-22 | Initial contract definition |
