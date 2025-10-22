# Data Model: Local Template Zip

**Feature**: 001-local-template-zip
**Date**: 2025-10-22
**Purpose**: Define data structures and state for local template management

## Overview

This feature operates on file system structures and in-memory data representations during script execution. Since this is a bash script implementation, the "data model" consists of file naming conventions, directory structures, and bash variable structures.

## File System Model

### Template Zip File

**Location**: Current working directory (where feature creation command is run)

**Naming Pattern**:
```
spec-kit-template-{arg1}-{arg2}-v{version}.zip
```

**Components**:
- **Prefix**: `spec-kit-template-` (constant, identifies template files)
- **arg1**: First template identifier (e.g., "claude")
- **arg2**: Second template identifier (e.g., "sh", "py")
- **Version**: Semantic version with 'v' prefix (e.g., "v0.0.78")
- **Extension**: `.zip` (constant)

**Examples**:
```
spec-kit-template-claude-sh-v0.0.78.zip
spec-kit-template-claude-py-v0.0.78.zip
spec-kit-template-claude-sh-v0.0.79.zip
```

**Validation Rules**:
1. Must be a valid zip archive (can be extracted without errors)
2. Must match naming pattern exactly
3. Version must be valid semantic version (MAJOR.MINOR.PATCH)
4. Arguments must be non-empty, alphanumeric + hyphens

**Internal Structure** (not validated, but expected):
```
template-contents/
├── spec-template.md
├── plan-template.md
└── [other template files]
```

### Configuration File

**Location**: `.specify/config`

**Format**: Bash-sourceable key-value pairs

**Structure**:
```bash
# .specify/config
# Template configuration for local template selection

# Template arguments (space-separated)
TEMPLATE_ARGS="claude sh"

# Optional: Template version preference (defaults to latest)
# TEMPLATE_VERSION="0.0.78"
```

**Fields**:
- **TEMPLATE_ARGS**: Space-separated template argument identifiers
  - Type: String
  - Required: No (triggers interactive prompt if missing)
  - Format: `"{arg1} {arg2}"`
  - Example: `"claude sh"`
  - Validation: Non-empty words, alphanumeric + hyphens

- **TEMPLATE_VERSION**: Specific version to use (optional)
  - Type: String (semantic version)
  - Required: No (defaults to latest if omitted)
  - Format: `"MAJOR.MINOR.PATCH"` or `"vMAJOR.MINOR.PATCH"`
  - Example: `"0.0.78"` or `"v0.0.78"`
  - Validation: Must match semver pattern

**Lifecycle**:
- Created manually by user or during project initialization
- Read during feature creation
- Never modified by scripts automatically

## Runtime Data Structures

### TemplateMetadata (Bash Associative Array)

Represents parsed information from a template filename.

**Structure**:
```bash
declare -A template_metadata
template_metadata[filename]="spec-kit-template-claude-sh-v0.0.78.zip"
template_metadata[arg1]="claude"
template_metadata[arg2]="sh"
template_metadata[version]="0.0.78"
template_metadata[fullpath]="/current/dir/spec-kit-template-claude-sh-v0.0.78.zip"
```

**Fields**:
- **filename**: Original filename (string)
- **arg1**: First template argument (string)
- **arg2**: Second template argument (string)
- **version**: Semantic version without 'v' prefix (string)
- **fullpath**: Absolute path to template file (string)

**Operations**:
- `parse_template_filename()`: Extract components from filename
- `matches_args()`: Check if template matches requested arguments
- `compare_versions()`: Compare two template versions

### TemplateList (Bash Indexed Array)

Collection of template filenames found in current directory.

**Structure**:
```bash
declare -a template_list
template_list=(
    "spec-kit-template-claude-sh-v0.0.78.zip"
    "spec-kit-template-claude-sh-v0.0.79.zip"
    "spec-kit-template-claude-py-v0.0.78.zip"
)
```

**Operations**:
- `find_templates()`: Glob for matching files in current directory
- `filter_by_args()`: Filter list to only matching arguments
- `sort_by_version()`: Sort templates by version (descending)
- `select_latest()`: Get the first item after version sort

## State Transitions

### Template Selection Flow

```
┌─────────────────────────┐
│  Feature Creation       │
│  Command Initiated      │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Read Configuration     │
│  (.specify/config)      │
└───────────┬─────────────┘
            │
            ▼
      ┌─────────────┐
      │ Config      │
      │ Found?      │
      └──┬──────┬───┘
         │ No   │ Yes
         │      │
         │      ▼
         │  ┌─────────────────────────┐
         │  │ Extract TEMPLATE_ARGS   │
         │  └───────────┬─────────────┘
         │              │
         │              ▼
         │  ┌─────────────────────────┐
         │  │ Find Matching Templates │
         │  │ in Current Directory    │
         │  └───────────┬─────────────┘
         │              │
         │              ▼
         │          ┌─────────────┐
         │          │ Templates   │
         │          │ Found?      │
         │          └──┬──────┬───┘
         │             │ No   │ Yes
         │             │      │
         │             │      ▼
         │             │  ┌─────────────────────────┐
         │             │  │ Multiple Versions?      │
         │             │  └──┬──────────────────┬───┘
         │             │     │ No               │ Yes
         │             │     │                  │
         │             │     │                  ▼
         │             │     │  ┌─────────────────────────┐
         │             │     │  │ Sort by Version (desc)  │
         │             │     │  │ Select Latest (first)   │
         │             │     │  └───────────┬─────────────┘
         │             │     │              │
         │             │     ▼              ▼
         │             │  ┌─────────────────────────┐
         │             │  │ Selected Template       │
         │             │  └───────────┬─────────────┘
         │             │              │
         │             │              ▼
         │             │  ┌─────────────────────────┐
         │             │  │ Validate Zip Integrity  │
         │             │  └───────────┬─────────────┘
         │             │              │
         │             │              ▼
         │             │          ┌─────────────┐
         │             │          │ Valid?      │
         │             │          └──┬──────┬───┘
         │             │             │ No   │ Yes
         │             │             │      │
         │             │             │      ▼
         │             │             │  ┌─────────────────────────┐
         │             │             │  │ Extract Template        │
         │             │             │  │ to Feature Directory    │
         │             │             │  └───────────┬─────────────┘
         │             │             │              │
         │             │             │              ▼
         │             │             │  ┌─────────────────────────┐
         │             │             │  │ SUCCESS: Template Used  │
         │             │             │  └─────────────────────────┘
         │             │             │
         │             │             ▼
         │             │  ┌─────────────────────────┐
         │             │  │ ERROR: Corrupted Zip    │
         │             │  └─────────────────────────┘
         │             │
         │             ▼
         │  ┌─────────────────────────┐
         │  │ ERROR: No Match         │
         │  │ List Available Templates│
         │  └─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Find All Templates      │
│ in Current Directory    │
└───────────┬─────────────┘
            │
            ▼
        ┌─────────────┐
        │ Templates   │
        │ Found?      │
        └──┬──────┬───┘
           │ No   │ Yes
           │      │
           │      ▼
           │  ┌─────────────────────────┐
           │  │ Interactive Prompt      │
           │  │ Show Template List      │
           │  │ User Selects Number     │
           │  └───────────┬─────────────┘
           │              │
           │              ▼
           │  ┌─────────────────────────┐
           │  │ Validate + Extract      │
           │  │ (same as above)         │
           │  └─────────────────────────┘
           │
           ▼
┌─────────────────────────┐
│ ERROR: No Templates     │
│ Provide Setup Guide     │
└─────────────────────────┘
```

## Data Validation

### Filename Validation Rules

**Pattern Matching**:
```bash
validate_template_filename() {
    local filename="$1"

    # Must match pattern
    if [[ ! "$filename" =~ ^spec-kit-template-[a-zA-Z0-9-]+-[a-zA-Z0-9-]+-v[0-9]+\.[0-9]+\.[0-9]+\.zip$ ]]; then
        return 1
    fi

    # Extract and validate version
    local version=$(echo "$filename" | sed -n 's/.*-v\([0-9.]*\)\.zip$/\1/p')
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        return 1
    fi

    return 0
}
```

### Configuration Validation

```bash
validate_template_args() {
    local args="$1"

    # Must not be empty
    if [ -z "$args" ]; then
        return 1
    fi

    # Must contain exactly 2 words
    local word_count=$(echo "$args" | wc -w)
    if [ "$word_count" -ne 2 ]; then
        return 1
    fi

    # Each word must be alphanumeric + hyphens
    for word in $args; do
        if [[ ! "$word" =~ ^[a-zA-Z0-9-]+$ ]]; then
            return 1
        fi
    done

    return 0
}
```

## Error States

### Error Types

1. **No Templates Found**
   - Trigger: No files matching `spec-kit-template-*.zip` in current directory
   - Message: "Error: No local template files found in current directory"
   - Resolution: User must download and place template

2. **No Matching Arguments**
   - Trigger: Config specifies args that don't match any available template
   - Message: "Error: No template found matching arguments: {args}"
   - Resolution: Update config or add matching template

3. **Corrupted Zip File**
   - Trigger: `unzip -t` fails on selected template
   - Message: "Error: Invalid or corrupted zip file: {filename}"
   - Resolution: Re-download template file

4. **Invalid Configuration**
   - Trigger: Config file has syntax errors or invalid format
   - Message: "Error: Invalid configuration in .specify/config"
   - Resolution: Fix config file syntax

5. **Missing Config (not an error)**
   - Trigger: No `.specify/config` file found
   - Behavior: Trigger interactive selection
   - No error message (expected flow)

## Relationships

### Template to Configuration

```
.specify/config (TEMPLATE_ARGS) ──matches──> spec-kit-template-{arg1}-{arg2}-v{version}.zip
                                   1:N relationship
                                   (one config matches multiple versions)
```

### Template Versions

```
spec-kit-template-claude-sh-v0.0.78.zip ──same args──> spec-kit-template-claude-sh-v0.0.79.zip
                                         superseded by
                                         (latest version selected)
```

## Persistence

**No Persistent State**:
- All operations are read-only on templates
- No state stored between executions
- Each feature creation is independent

**Immutable Data**:
- Template zip files are never modified
- Configuration file only read, never written by scripts
- Feature directory is created fresh each time

## Concurrency

**No Concurrency Issues**:
- Scripts run sequentially in single bash process
- No shared state between script invocations
- File system operations are atomic (zip extraction)

**Safe Operations**:
- Reading zip files: Read-only, safe for concurrent reads
- Extracting zips: Each extraction to unique feature directory
- Reading config: Read-only, no write conflicts

## Performance Characteristics

**File System Operations**:
- Glob pattern matching: O(n) where n = files in directory
- Version sorting: O(n log n) where n = matching templates
- Zip validation: O(1) per file (unzip -t)
- Zip extraction: O(m) where m = template size

**Expected File Counts**:
- Templates in directory: 1-10 (typical)
- Matching a specific arg combination: 1-3 versions
- Sort + select: Negligible overhead

**Memory Usage**:
- Bash arrays for template list: <1KB (filenames only)
- Associative arrays for metadata: <1KB per template
- Total: <10KB for typical usage

## Future Extensibility

**Potential Extensions** (not implemented):
1. Template caching in `.specify/cache/`
2. Template signature verification (GPG)
3. Template update checking (compare local vs remote versions)
4. Multi-argument templates (>2 arguments)
5. Template aliases/shortcuts in config

**Backward Compatibility Considerations**:
- Naming pattern allows adding metadata without breaking existing parsers
- Config file can be extended with new optional fields
- Validation can be strengthened without breaking existing templates
