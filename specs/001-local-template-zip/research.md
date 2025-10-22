# Research: Local Template Zip

**Feature**: 001-local-template-zip
**Date**: 2025-10-22
**Purpose**: Research technical decisions for implementing local template zip file support

## Overview

This document captures research findings and technical decisions for modifying the template download stage to use local zip files instead of GitHub downloads.

## Key Technical Decisions

### 1. Template Naming Pattern & Parsing

**Decision**: Use the pattern `spec-kit-template-{arg1}-{arg2}-v{version}.zip`

**Rationale**:
- Explicit structure enables reliable parsing with bash string manipulation
- Version prefix (`v`) clearly distinguishes version from arguments
- Hyphen-separated arguments allow multiple context identifiers
- Example: `spec-kit-template-claude-sh-v0.0.78.zip`

**Parsing Strategy**:
```bash
# Extract components using parameter expansion and sed
filename="spec-kit-template-claude-sh-v0.0.78.zip"
# Remove prefix and .zip suffix
core="${filename#spec-kit-template-}"
core="${core%.zip}"
# Split on last occurrence of "-v"
args="${core%-v*}"      # "claude-sh"
version="${core##*-v}"   # "0.0.78"
```

**Alternatives Considered**:
- JSON manifest inside zip: Rejected due to overhead of extracting/parsing before selection
- Underscore separators: Rejected due to potential conflicts with argument naming
- No version in filename: Rejected as it prevents multiple versions coexisting

### 2. Semantic Version Comparison in Bash

**Decision**: Implement semantic version comparison using bash built-ins (no external dependencies)

**Rationale**:
- Must work offline without additional tool installation
- Semantic versioning (MAJOR.MINOR.PATCH) is standard and well-defined
- Bash can handle numeric comparison efficiently

**Implementation Approach**:
```bash
# Split version into components and compare numerically
compare_versions() {
    local v1="$1" v2="$2"
    # Split on dots, compare each component
    IFS='.' read -ra V1 <<< "${v1#v}"
    IFS='.' read -ra V2 <<< "${v2#v}"

    for i in 0 1 2; do
        local n1="${V1[$i]:-0}"
        local n2="${V2[$i]:-0}"
        if [ "$n1" -gt "$n2" ]; then echo "1"; return
        elif [ "$n1" -lt "$n2" ]; then echo "-1"; return
        fi
    done
    echo "0"
}
```

**Alternatives Considered**:
- External `semver` tool: Rejected due to offline requirement and dependency bloat
- Lexicographic comparison: Rejected as it fails for versions like "0.9" vs "0.10"
- Python/Node script: Rejected to maintain pure bash implementation

### 3. Configuration File Format for Template Arguments

**Decision**: Read template arguments from `.specify/constitution.md` or a new `.specify/config` file using simple key-value format

**Rationale**:
- Aligns with clarification decision to use .specify configuration
- Simple format allows bash parsing without external tools
- Can extend existing constitution.md or use dedicated config file

**Format Options**:

Option A - Extend constitution.md with frontmatter:
```markdown
---
template_args: claude sh
---
# Project Constitution
...
```

Option B - Create `.specify/config` file:
```bash
# .specify/config
TEMPLATE_ARGS="claude sh"
```

**Recommended**: Option B (dedicated config file)
- Cleaner separation of concerns
- Easier to parse (bash source or grep)
- No risk of breaking existing constitution parsing

**Parsing Implementation**:
```bash
read_template_args() {
    local config_file="$REPO_ROOT/.specify/config"
    if [ -f "$config_file" ]; then
        # Source as bash or grep for TEMPLATE_ARGS
        source "$config_file" 2>/dev/null
        echo "$TEMPLATE_ARGS"
    else
        echo ""  # Empty = trigger interactive prompt
    fi
}
```

**Alternatives Considered**:
- JSON config: Rejected due to parsing complexity in pure bash
- YAML config: Rejected for same reason
- Environment variables: Rejected as not persistent across sessions

### 4. Interactive Template Selection UI

**Decision**: Use bash `select` built-in for interactive prompts

**Rationale**:
- Native bash feature, no external dependencies
- Provides numbered menu automatically
- Handles input validation built-in

**Implementation**:
```bash
prompt_template_selection() {
    local templates=("$@")

    echo "Multiple templates available. Please select one:" >&2
    PS3="Enter number: "
    select template in "${templates[@]}"; do
        if [ -n "$template" ]; then
            echo "$template"
            return 0
        fi
    done
}
```

**Alternatives Considered**:
- `fzf` or `dialog`: Rejected due to external dependency requirement
- Manual prompt loop: Rejected as `select` is more robust and standard

### 5. Zip File Validation Strategy

**Decision**: Validate using `unzip -t` (test integrity)

**Rationale**:
- Standard Unix tool available on all target platforms
- Efficiently tests zip integrity without full extraction
- Provides clear error messages

**Implementation**:
```bash
validate_zip() {
    local zip_file="$1"
    if unzip -t "$zip_file" >/dev/null 2>&1; then
        return 0
    else
        echo "Error: Invalid or corrupted zip file: $zip_file" >&2
        return 1
    fi
}
```

**Alternatives Considered**:
- Structure validation: Rejected per clarification (only validate zip integrity)
- `zipinfo`: Rejected as less portable than `unzip -t`
- Try extraction: Rejected as slower and requires cleanup

### 6. Error Message Formatting

**Decision**: Use consistent error format with available template listing

**Rationale**:
- Helps users quickly identify and fix configuration issues
- Lists available options for self-service resolution
- Follows existing script error patterns

**Format Template**:
```bash
show_template_mismatch_error() {
    local requested_args="$1"
    shift
    local available_templates=("$@")

    cat >&2 <<EOF
Error: No template found matching arguments: $requested_args

Available templates:
$(for t in "${available_templates[@]}"; do
    # Parse and display args + version
    echo "  - $t"
done)

Please update .specify/config with correct TEMPLATE_ARGS
or place the required template in the current directory.
EOF
}
```

### 7. Integration Point in create-new-feature.sh

**Decision**: Insert local template logic before line 194 (template copy logic)

**Current Line 192-194**:
```bash
TEMPLATE="$REPO_ROOT/.specify/templates/spec-template.md"
SPEC_FILE="$FEATURE_DIR/spec.md"
if [ -f "$TEMPLATE" ]; then cp "$TEMPLATE" "$SPEC_FILE"; else touch "$SPEC_FILE"; fi
```

**New Logic**:
```bash
# Source template library functions
source "$REPO_ROOT/.specify/scripts/bash/lib/template-finder.sh"

# Try to find and use local template
LOCAL_TEMPLATE=$(find_local_template "$PWD")
if [ -n "$LOCAL_TEMPLATE" ]; then
    extract_template "$LOCAL_TEMPLATE" "$FEATURE_DIR"
else
    # Fallback to existing logic (or error per spec)
    echo "Error: No local template found" >&2
    exit 1
fi

SPEC_FILE="$FEATURE_DIR/spec.md"
```

**Rationale**:
- Minimal disruption to existing workflow
- Clear separation between template acquisition and spec file setup
- Allows for error handling before feature directory is fully initialized

## Testing Strategy

### Unit Tests (bats-core)

**Test Coverage**:
1. **template-finder.sh**:
   - Find templates by pattern
   - Parse template filename components
   - Match templates to arguments
   - Handle no templates found
   - Handle multiple versions (select latest)

2. **semver.sh**:
   - Compare equal versions
   - Compare major/minor/patch differences
   - Handle version prefixes (v0.1.0)
   - Handle missing patch versions (0.1 vs 0.1.0)

3. **config-reader.sh**:
   - Read template args from config
   - Handle missing config file
   - Handle malformed config

**Test Framework Setup**:
```bash
# Install bats-core for testing
# tests/unit/test-semver.bats
@test "compare equal versions" {
    run compare_versions "1.0.0" "1.0.0"
    [ "$output" = "0" ]
}

@test "1.0.1 > 1.0.0" {
    run compare_versions "1.0.1" "1.0.0"
    [ "$output" = "1" ]
}
```

### Integration Tests

**Test Scenarios**:
1. Happy path: Single template matches configuration
2. Version selection: Multiple versions, latest selected
3. Interactive fallback: No config, prompt user
4. No match error: Args don't match any template
5. Corrupted zip: Validation fails with clear error

**Test Data Structure**:
```
tests/fixtures/
├── spec-kit-template-claude-sh-v0.0.78.zip
├── spec-kit-template-claude-sh-v0.0.79.zip
├── spec-kit-template-claude-py-v0.0.78.zip
└── corrupted-template.zip
```

## Best Practices from Existing Code

From analysis of `create-new-feature.sh`:

1. **JSON Mode Support**: Maintain `--json` flag for programmatic usage
2. **Error Handling**: Use `set -e` and explicit error messages to stderr
3. **Path Resolution**: Use absolute paths, resolve via `REPO_ROOT`
4. **Git Detection**: Check for git and gracefully degrade when absent
5. **Parameter Expansion**: Prefer bash built-ins over external commands

## Dependencies

**Required (already present)**:
- bash 4.0+
- grep, sed, sort
- unzip

**New (for testing only)**:
- bats-core (bash testing framework)

**Not Required** (explicitly avoided):
- jq, yq (JSON/YAML parsers)
- Python, Node.js (external scripting)
- External semver tools

## Performance Considerations

**Expected Timeline**:
- Template file search: <10ms (glob pattern in current dir)
- Version comparison: <5ms per comparison (pure bash arithmetic)
- Zip validation: <50ms (unzip -t on small template)
- Extraction: <100ms (unzip operation)

**Total**: <200ms typical case, well under 1-second goal

**Comparison to GitHub Download**:
- Current: 3-10 seconds (network latency + download)
- Local: <1 second (disk I/O only)
- Improvement: 3-10x faster

## Migration Path

**Backward Compatibility**:
- If no local templates found, system errors (per spec requirement)
- Users must explicitly download and place templates
- No automatic fallback to GitHub (offline-first design)

**User Onboarding**:
1. Download template zip from GitHub releases
2. Place in project root or specify in `.specify/config`
3. Run feature creation as normal

**Documentation Needs**:
- quickstart.md: How to download and configure local templates
- Error messages: Guide users to quickstart when templates missing

## Open Questions

None - all clarifications resolved in specification phase.

## References

- Bash Parameter Expansion: https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html
- Semantic Versioning 2.0.0: https://semver.org/
- Bats-core Testing: https://bats-core.readthedocs.io/
- Unzip Command: man unzip (test mode `-t`)
