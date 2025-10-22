#!/usr/bin/env bash
#
# template-finder.sh - Local template discovery and selection functions
# Part of spec-kit local template feature

# Parse template filename to extract components
# Input: Template filename (basename only, e.g., "spec-kit-template-claude-sh-v0.0.78.zip")
# Output: Space-separated values: "<arg1> <arg2> <version>"
# Return: 0 if valid format, 1 if invalid
parse_template_filename() {
    local filename="$1"

    # Validate pattern: spec-kit-template-{arg1}-{arg2}-v{version}.zip
    if [[ ! "$filename" =~ ^spec-kit-template-[a-zA-Z0-9-]+-[a-zA-Z0-9-]+-v[0-9]+\.[0-9]+\.[0-9]+\.zip$ ]]; then
        echo "Error: Invalid template filename format: $filename" >&2
        return 1
    fi

    # Remove prefix and suffix
    local core="${filename#spec-kit-template-}"
    core="${core%.zip}"

    # Split on last occurrence of "-v" to separate args from version
    local args="${core%-v*}"
    local version="${core##*-v}"

    # Split args on first hyphen to get arg1 and arg2
    local arg1="${args%%-*}"
    local arg2="${args#*-}"

    echo "$arg1 $arg2 $version"
    return 0
}

# Validate template filename pattern
# Input: Template filename
# Return: 0 if valid, 1 if invalid
validate_template_filename() {
    local filename="$1"

    if [[ "$filename" =~ ^spec-kit-template-[a-zA-Z0-9-]+-[a-zA-Z0-9-]+-v[0-9]+\.[0-9]+\.[0-9]+\.zip$ ]]; then
        return 0
    else
        return 1
    fi
}

# Find all local template zip files in current directory
# Input: None (uses $PWD)
# Output: Newline-separated list of matching template filenames (basenames only)
# Return: Always 0
find_local_templates() {
    # Use ls to find matching files, suppress errors if no matches
    ls spec-kit-template-*.zip 2>/dev/null | grep -E '^spec-kit-template-[a-zA-Z0-9-]+-[a-zA-Z0-9-]+-v[0-9]+\.[0-9]+\.[0-9]+\.zip$' || true
}

# Validate zip file integrity
# Input: Path to zip file
# Output: None
# Return: 0 if valid, 1 if invalid/corrupted
validate_zip_integrity() {
    local zip_file="$1"

    if unzip -t "$zip_file" >/dev/null 2>&1; then
        return 0
    else
        echo "Error: Invalid or corrupted zip file: $zip_file" >&2
        return 1
    fi
}

# Extract template zip file to target directory
# Input: zip_file, target_dir
# Output: None (or error message to stderr)
# Return: 0 if successful, 1 if failed
extract_template() {
    local zip_file="$1"
    local target_dir="$2"

    # Create target directory if it doesn't exist
    mkdir -p "$target_dir" 2>/dev/null || {
        echo "Error: Failed to create target directory: $target_dir" >&2
        return 1
    }

    # Extract zip file
    if unzip -q "$zip_file" -d "$target_dir" 2>/dev/null; then
        return 0
    else
        echo "Error: Failed to extract template: $zip_file" >&2
        return 1
    fi
}

# Filter templates by matching arguments
# Input: arg1, arg2, followed by template filenames
# Output: Newline-separated list of matching templates
# Return: Always 0
filter_templates_by_args() {
    local requested_arg1="$1"
    local requested_arg2="$2"
    shift 2

    local matches=()

    for template in "$@"; do
        # Parse template to get its arguments
        local components
        if components=$(parse_template_filename "$template" 2>/dev/null); then
            read -r arg1 arg2 version <<< "$components"

            # Check if arguments match
            if [ "$arg1" = "$requested_arg1" ] && [ "$arg2" = "$requested_arg2" ]; then
                matches+=("$template")
            fi
        fi
    done

    # Output matches (one per line)
    printf '%s\n' "${matches[@]}"
}

# Interactive template selection prompt
# Input: Template filenames as arguments
# Output: Selected template filename
# Return: 0 if selection made, 1 if no templates or cancelled
prompt_template_selection() {
    if [ $# -eq 0 ]; then
        echo "Error: No templates provided for selection" >&2
        return 1
    fi

    echo "Multiple templates available. Please select one:" >&2
    PS3="Enter number: "
    select template in "$@"; do
        if [ -n "$template" ]; then
            echo "$template"
            return 0
        fi
    done

    return 1
}

# Show error message when no template matches requested arguments
# Input: requested_args (string), followed by available template filenames
# Output: Formatted error message to stderr
# Return: Always 0
show_no_match_error() {
    local requested_args="$1"
    shift
    local available_templates=("$@")

    cat >&2 <<EOF
Error: No template found matching arguments: $requested_args

Available templates:
EOF

    # Parse and display each available template
    for template in "${available_templates[@]}"; do
        local components
        if components=$(parse_template_filename "$template" 2>/dev/null); then
            read -r arg1 arg2 version <<< "$components"
            echo "  - $arg1-$arg2 (version $version)" >&2
        fi
    done

    cat >&2 <<EOF

Please update .specify/config with correct TEMPLATE_ARGS
or place the required template in the current directory.
EOF

    return 0
}

# Select latest template from list of matching templates
# Input: Template filenames (all should have same args, different versions)
# Output: Single template filename with highest version
# Return: 0 if selected, 1 if no templates provided
select_latest_template() {
    if [ $# -eq 0 ]; then
        echo "Error: No templates provided for version selection" >&2
        return 1
    fi

    # If only one template, return it
    if [ $# -eq 1 ]; then
        echo "$1"
        return 0
    fi

    # Source semver functions
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # shellcheck disable=SC1091
    source "$script_dir/semver.sh"

    local latest_template="$1"
    local latest_version

    # Extract version from first template
    local components
    if components=$(parse_template_filename "$latest_template" 2>/dev/null); then
        read -r _ _ latest_version <<< "$components"
    else
        echo "$latest_template"
        return 0
    fi

    # Compare with remaining templates
    shift
    for template in "$@"; do
        if components=$(parse_template_filename "$template" 2>/dev/null); then
            read -r _ _ version <<< "$components"

            # Compare versions
            local result
            result=$(compare_versions "$version" "$latest_version")

            if [ "$result" = "1" ]; then
                # This version is newer
                latest_template="$template"
                latest_version="$version"
            fi
        fi
    done

    echo "$latest_template"
    return 0
}

# Main orchestration function: find and use local template
# Input: feature_dir (directory where template should be extracted)
# Output: None (error messages to stderr, success messages to stderr)
# Return: 0 if successful, 1 if failed
find_and_use_local_template() {
    local feature_dir="$1"

    # Source required libraries
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # shellcheck disable=SC1091
    source "$script_dir/config-reader.sh"

    # Try to read configured template arguments
    local template_args=""
    local arg1="" arg2=""

    if template_args=$(read_template_args 2>/dev/null); then
        if [ -n "$template_args" ]; then
            # Validate args
            if ! validate_template_args "$template_args"; then
                return 1
            fi
            read -r arg1 arg2 <<< "$template_args"
        fi
    fi

    # Find all local templates
    local all_templates
    all_templates=$(find_local_templates)

    if [ -z "$all_templates" ]; then
        cat >&2 <<EOF
Error: No local template files found in current directory

Please download a template zip file and place it in the current directory.
Template filename must follow the pattern:
  spec-kit-template-{arg1}-{arg2}-v{version}.zip

Example: spec-kit-template-claude-sh-v0.0.78.zip
EOF
        return 1
    fi

    # Convert to array
    local templates_array=()
    while IFS= read -r template; do
        templates_array+=("$template")
    done <<< "$all_templates"

    # Determine which template to use
    local selected_template

    if [ -n "$arg1" ] && [ -n "$arg2" ]; then
        # Filter by arguments
        local matches
        matches=$(filter_templates_by_args "$arg1" "$arg2" "${templates_array[@]}")

        if [ -z "$matches" ]; then
            show_no_match_error "$arg1 $arg2" "${templates_array[@]}"
            return 1
        fi

        # Convert matches to array
        local matches_array=()
        while IFS= read -r match; do
            matches_array+=("$match")
        done <<< "$matches"

        # Select latest version if multiple matches
        selected_template=$(select_latest_template "${matches_array[@]}")

        # Show which template was selected if multiple versions available
        if [ "${#matches_array[@]}" -gt 1 ]; then
            echo "Selected template: $selected_template (latest of ${#matches_array[@]} versions)" >&2
        fi
    else
        # Interactive selection
        selected_template=$(prompt_template_selection "${templates_array[@]}")
        if [ $? -ne 0 ] || [ -z "$selected_template" ]; then
            echo "Error: No template selected" >&2
            return 1
        fi
    fi

    # Validate and extract selected template
    if ! validate_zip_integrity "$selected_template"; then
        return 1
    fi

    if ! extract_template "$selected_template" "$feature_dir"; then
        return 1
    fi

    echo "Using local template: $selected_template" >&2
    return 0
}
