#!/usr/bin/env bash
#
# config-reader.sh - Configuration file reading functions
# Part of spec-kit local template feature

# Read template arguments from .specify/config file
# Input: None (reads from $REPO_ROOT/.specify/config)
# Output: Template arguments string (e.g., "claude sh") or empty if not found
# Return: 0 if config file exists, 1 if not
read_template_args() {
    local config_file="${REPO_ROOT}/.specify/config"

    if [ ! -f "$config_file" ]; then
        return 1
    fi

    # Source the config file and extract TEMPLATE_ARGS
    # Use a subshell to avoid polluting current environment
    (
        # shellcheck disable=SC1090
        source "$config_file" 2>/dev/null
        echo "$TEMPLATE_ARGS"
    )

    return 0
}

# Validate template arguments format
# Input: Template arguments string (e.g., "claude sh")
# Output: None (or error message to stderr)
# Return: 0 if valid, 1 if invalid
validate_template_args() {
    local args="$1"

    # Must not be empty
    if [ -z "$args" ]; then
        echo "Error: Template arguments cannot be empty" >&2
        return 1
    fi

    # Count words
    local word_count
    word_count=$(echo "$args" | wc -w | tr -d ' ')

    # Must have exactly 2 words
    if [ "$word_count" -ne 2 ]; then
        cat >&2 <<EOF
Error: Invalid template arguments format
Expected: "<arg1> <arg2>" (e.g., "claude sh")
Got: "$args"
EOF
        return 1
    fi

    # Each word must match pattern [a-zA-Z0-9-]+
    for word in $args; do
        if [[ ! "$word" =~ ^[a-zA-Z0-9-]+$ ]]; then
            cat >&2 <<EOF
Error: Invalid characters in template argument: "$word"
Arguments must contain only letters, numbers, and hyphens.
EOF
            return 1
        fi
    done

    return 0
}
