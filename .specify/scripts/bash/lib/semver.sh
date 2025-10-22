#!/usr/bin/env bash
#
# semver.sh - Semantic version comparison functions
# Part of spec-kit local template feature

# Normalize version string by removing 'v' prefix
# Input: Version string (e.g., "v0.0.78" or "0.0.78")
# Output: Version without 'v' prefix (e.g., "0.0.78")
normalize_version() {
    local version="$1"
    # Remove 'v' prefix if present
    echo "${version#v}"
}

# Compare two semantic versions
# Input: version1, version2 (e.g., "0.0.78", "0.0.79" or "v0.0.78", "v0.0.79")
# Output: "1" if v1 > v2, "0" if v1 == v2, "-1" if v1 < v2
# Return: Always 0 (success)
compare_versions() {
    local v1="$1"
    local v2="$2"

    # Normalize versions (remove 'v' prefix)
    v1=$(normalize_version "$v1")
    v2=$(normalize_version "$v2")

    # Split versions into array components
    IFS='.' read -ra V1 <<< "$v1"
    IFS='.' read -ra V2 <<< "$v2"

    # Compare major, minor, patch (indices 0, 1, 2)
    for i in 0 1 2; do
        local n1="${V1[$i]:-0}"
        local n2="${V2[$i]:-0}"

        # Remove leading zeros for numeric comparison
        n1=$((10#$n1))
        n2=$((10#$n2))

        if [ "$n1" -gt "$n2" ]; then
            echo "1"
            return 0
        elif [ "$n1" -lt "$n2" ]; then
            echo "-1"
            return 0
        fi
    done

    # Versions are equal
    echo "0"
    return 0
}
