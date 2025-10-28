# Offline Mode Implementation

This document describes the offline mode implementation for the Spec Kit CLI, which allows users to work without internet connectivity by using local template files.

## Overview

The offline mode enables the `specify init` command to work without reaching out to GitHub's API or downloading templates from the internet. Instead, it:

1. Reads version information from a local `version.txt` file
2. Searches for template zip files in the installation directory
3. Allows interactive selection when multiple template versions exist
4. Falls back to the latest version automatically when only one template is available

## Architecture

The implementation is modular and designed for easy upstream syncing. All offline-related functionality is contained in standalone helper functions that can be maintained independently.

### Key Components

#### 1. Template Storage Location

Templates are stored in: `src/specify_cli/spec-kit-templates/`

This directory contains:
- `version.txt` - Contains the current version number (e.g., "0.0.20")
- Template zip files following the pattern: `spec-kit-template-{agent}-{script}-v{version}.zip`

Example:
```
spec-kit-templates/
├── version.txt
├── spec-kit-template-claude-sh-v1.0.0.zip
├── spec-kit-template-claude-ps-v0.0.79.zip
└── README.md
```

#### 2. Helper Functions

Three new modular functions were added to `__init__.py`:

**`read_local_version(templates_dir: Path = None, verbose: bool = False) -> Optional[str]`**
- Reads version from `version.txt` in the templates directory
- Returns version string (e.g., "1.0.0") or None if not found
- Uses installation directory by default

**`find_all_local_templates(ai_assistant: str, script_type: str, search_dir: Path = None, verbose: bool = False) -> list[Tuple[Path, str]]`**
- Finds all local template zip files matching the specified pattern
- Returns list of tuples: `[(file_path, version_string), ...]`
- Sorts templates by semantic version in descending order (latest first)
- Uses installation directory by default

**`select_local_template(templates: list[Tuple[Path, str]], prompt_text: str = "Multiple templates found. Select one:") -> Path`**
- Interactively selects a template when multiple versions exist
- Automatically returns the single template if only one is available
- Uses the existing `select_with_arrows` UI for consistent UX

#### 3. Modified Functions

**`download_and_extract_template(..., offline: bool = False)`**
- Enhanced to use the new helper functions
- First attempts to find local templates
- Shows interactive selection if multiple templates exist
- Reads version from `version.txt` for display purposes
- Only attempts GitHub download if:
  - No local templates found AND
  - `offline` mode is disabled
- In offline mode, fails immediately if no local templates are found

### Workflow

#### Online Mode (Default)

```
1. Check for local templates
   ├─ If found: Use local template (skip GitHub)
   └─ If not found: Download from GitHub
2. Extract template
3. Continue with project setup
```

#### Offline Mode (--offline flag or SPECIFY_OFFLINE=1 env var)

```
1. Check for local templates
   ├─ If found:
   │  ├─ Single template: Use automatically
   │  └─ Multiple templates: Show interactive selection
   └─ If not found: ERROR and exit
2. Read version.txt for display
3. Extract template
4. Continue with project setup
```

## Usage

### Enable Offline Mode

Via command-line flag:
```bash
specify init my-project --ai claude --offline
```

Via environment variable:
```bash
export SPECIFY_OFFLINE=1
specify init my-project --ai claude
```

### Adding Templates for Offline Use

1. Generate or obtain template zip files
2. Place them in `src/specify_cli/spec-kit-templates/`
3. Ensure they follow the naming pattern: `spec-kit-template-{agent}-{script}-v{version}.zip`
4. Update `version.txt` with the current version

Example:
```bash
cd src/specify_cli/spec-kit-templates/
# Copy your template
cp ~/Downloads/spec-kit-template-claude-sh-v1.2.0.zip .
# Update version
echo "1.2.0" > version.txt
```

### Multiple Template Selection

When multiple versions of the same template exist, the user sees an interactive selection:

```
┌─ Multiple templates found. Select one: ─────────────┐
│                                                      │
│  ▶  spec-kit-template-claude-sh-v1.2.0.zip (v1.2.0) │
│     spec-kit-template-claude-sh-v1.1.0.zip (v1.1.0) │
│     spec-kit-template-claude-sh-v1.0.0.zip (v1.0.0) │
│                                                      │
│  Use ↑/↓ to navigate, Enter to select, Esc to cancel│
└──────────────────────────────────────────────────────┘
```

## Code Organization

All offline-related code is organized for modularity:

```python
# Helper functions (lines 573-693)
def read_local_version(...)        # Read version.txt
def find_all_local_templates(...)  # Find all matching templates
def select_local_template(...)     # Interactive selection

# Modified function (lines 872-933)
def download_and_extract_template(..., offline: bool = False)
    # Uses helper functions above
    # Minimal changes to existing logic
```

This organization ensures:
- Easy testing of individual components
- Minimal conflicts when syncing with upstream
- Clear separation of concerns
- Reusable components

## Testing

A test script is available at `/tmp/test_offline_mode.sh` that verifies:

1. ✓ Version reading from `version.txt`
2. ✓ Template discovery (finds all matching templates)
3. ✓ Semantic version sorting (latest first)
4. ✓ Handling of non-existent templates (returns empty list)

Run tests:
```bash
./test_offline_mode.sh
```

## Benefits

1. **No Internet Required**: Work completely offline once templates are installed
2. **Corporate Firewall Friendly**: No need for GitHub API access
3. **Version Control**: Choose specific template versions
4. **Faster Initialization**: No network latency for template downloads
5. **Development Workflow**: Test template changes locally before publishing
6. **Bundled Distribution**: Package templates with the CLI for air-gapped environments

## Backwards Compatibility

The offline mode is fully backwards compatible:

- Default behavior unchanged (tries local, falls back to GitHub)
- Existing flags and options continue to work
- No breaking changes to the API
- GitHub download still works when online

## Future Enhancements

Potential improvements for future versions:

1. Template caching: Download and cache GitHub templates locally for future use
2. Version verification: Compare local version.txt with GitHub releases
3. Auto-update: Optionally download newer templates when online
4. Template signing: Verify template integrity using checksums or signatures
5. Multi-agent bundles: Download all templates for multiple agents at once

## Upstream Sync Strategy

To minimize merge conflicts when syncing with upstream:

1. All new functions are self-contained and added in a single block
2. Modifications to existing functions are minimal and clearly marked
3. No changes to core logic or data structures
4. Feature can be disabled by simply not using `--offline` flag
5. Code follows existing style and conventions

When syncing:
- Cherry-pick commits that add helper functions first
- Then apply commits that modify existing functions
- If conflicts occur, the helper functions can be re-added separately
