# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Spec Kit** is an open source toolkit for Spec-Driven Development (SDD) - a methodology that inverts the traditional code-first approach by making specifications executable and the source of truth. The project provides a CLI tool (`specify`) and templates that enable AI coding agents to follow a structured workflow from requirements to implementation.

### Core Components

1. **specify-cli** (`src/specify_cli/__init__.py`): Python CLI tool that bootstraps new SDD projects
2. **Templates** (`templates/`): Markdown templates for specifications, plans, tasks, and slash commands
3. **Scripts** (`scripts/bash/` and `scripts/powershell/`): Shell scripts that manage the SDD workflow
4. **Memory** (`memory/`): Project constitution templates that encode development principles

## Development Commands

### Setup & Installation

```bash
# Install dependencies (uses uv for package management)
uv sync

# Verify CLI works
uv run specify --help

# Run locally without installing
uv run python -m specify_cli init <project-name>

# Install for development (editable mode)
pip install -e .
```

### Testing

```bash
# Run all tests
pytest

# Run specific test directory
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v

# Run single test file
pytest tests/unit/test_specific.py
```

### Building & Releasing

```bash
# Create release packages (used by CI)
./.github/workflows/scripts/create-release-packages.sh v1.0.0

# Build wheel package
python -m build

# Check next version number
./.github/workflows/scripts/get-next-version.sh
```

### Local Testing of Templates

When making changes to templates or commands, test them locally:

```bash
# 1. Generate release packages
./.github/workflows/scripts/create-release-packages.sh v1.0.0

# 2. Copy template to installation directory for testing
cp .genreleases/spec-kit-template-claude-sh-v1.0.0.zip \
   src/specify_cli/spec-kit-templates/

# 3. Test with specify init in a test directory
cd /tmp/test-project
specify init --here --ai claude

# OR: Copy template files directly to test project (old method)
cp -r .genreleases/sdd-copilot-package-sh/. <path-to-test-project>/

# 4. Open agent in test project to verify changes
```

## Architecture

### CLI Tool Architecture (`src/specify_cli/__init__.py`)

The CLI is a single-file Python application using Typer for command parsing and Rich for terminal UI. Key design decisions:

- **Agent Configuration** (lines 67-153): Maps AI assistants to their folder structures and CLI requirements
- **Template Discovery** (lines 561-638):
  - `get_installation_templates_dir()`: Returns path to bundled templates directory
  - `find_local_template()`: Searches installation directory first, then falls back to GitHub
  - Supports semantic version comparison for automatic latest selection
- **Interactive Selection** (lines 274-347): Cross-platform arrow-key navigation using `readchar`
- **Step Tracking** (lines 169-252): Tree-based progress display with live refresh
- **Git Integration** (lines 439-492): Detects existing repos and initializes new ones

### Workflow Scripts

Scripts follow a consistent pattern across bash and PowerShell implementations:

1. **create-new-feature.sh** (scripts/bash/create-new-feature.sh):
   - Generates feature numbers by scanning `specs/` directory
   - Creates git branches named `{number}-{short-name}`
   - Outputs JSON with `BRANCH_NAME`, `SPEC_FILE`, `FEATURE_DIR`
   - Handles both git and non-git repositories via `SPECIFY_FEATURE` env var

2. **setup-plan.sh** (scripts/bash/setup-plan.sh):
   - Validates prerequisites (constitution, spec.md)
   - Creates planning directory structure
   - Used by `/speckit.plan` command

3. **check-prerequisites.sh** (scripts/bash/check-prerequisites.sh):
   - Validates all required files exist before tasks/implementation
   - Ensures constitution → spec → plan → tasks dependency chain

4. **update-agent-context.sh** (scripts/bash/update-agent-context.sh):
   - Updates agent-specific context files (CLAUDE.md, copilot-instructions.md, etc.)
   - Called after planning to provide implementation guidance

### Template System

Templates use placeholder syntax that gets replaced by slash commands:

- `[PLACEHOLDER]` - Required replacement fields
- `$ARGUMENTS` - User input from slash command
- `{ARGS}`, `{SCRIPT}` - Command metadata
- `<!--COMMENTS-->` - Guidance that remains in generated files

**Key Templates:**

- `spec-template.md`: Feature specifications with user stories, requirements, success criteria
- `plan-template.md`: Implementation plans with architecture, tech stack, and task breakdown
- `tasks-template.md`: Dependency-ordered task lists with parallel execution markers `[P]`
- `commands/*.md`: Slash command definitions with embedded script invocations

### Slash Command Architecture

Slash commands (`templates/commands/*.md`) follow a three-part structure:

1. **Frontmatter** (YAML): Defines script execution per platform
2. **User Input Section**: Captures `$ARGUMENTS` from command invocation
3. **Execution Instructions**: Step-by-step workflow for AI agent

Commands form a dependency chain:
```
/speckit.constitution → /speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement
                            ↓
                      /speckit.clarify (optional, before planning)
                            ↓
                      /speckit.analyze (optional, after tasks)
                      /speckit.checklist (optional, quality validation)
```

### Git Workflow Integration

The toolkit assumes a branch-per-feature workflow:

1. Feature specs live in `specs/{number}-{short-name}/`
2. Each feature gets its own git branch (same name as spec directory)
3. For non-git repos, `SPECIFY_FEATURE` env var overrides branch detection
4. Scripts use `git rev-parse` to find repo root, falling back to `.specify` marker

### Multi-Agent Support

The project supports 13+ AI coding agents through configuration:

- **IDE-based agents** (Copilot, Cursor, Windsurf, etc.): No CLI check required
- **CLI-based agents** (Claude, Gemini, Codex, etc.): Requires tool verification
- **Agent folders**: Each agent stores config in `.{agent-name}/` directory

Configuration allows different script types (bash `.sh` vs PowerShell `.ps1`) and platform-specific handling.

## Code Organization

```
spec-kit/
├── src/specify_cli/          # CLI tool source (single-file architecture)
├── scripts/
│   ├── bash/                 # POSIX shell scripts (primary)
│   └── powershell/           # Windows PowerShell scripts (mirrors bash)
├── templates/
│   ├── commands/             # Slash command definitions
│   ├── spec-template.md      # Feature specification template
│   ├── plan-template.md      # Implementation plan template
│   └── tasks-template.md     # Task breakdown template
├── memory/
│   └── constitution.md       # Project principles template
├── tests/
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
└── .github/workflows/        # CI/CD pipelines

Generated in user projects:
.specify/                     # Created by specify init
├── memory/constitution.md    # Project-specific principles
├── scripts/                  # Copied from spec-kit templates
├── specs/                    # Feature specifications
│   └── {num}-{name}/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── data-model.md
│       ├── research.md
│       ├── quickstart.md
│       └── contracts/
└── templates/                # Templates for future features
```

## Key Patterns & Conventions

### Script Execution from Slash Commands

When a slash command invokes a script, it follows this pattern:

```markdown
scripts:
  sh: scripts/bash/create-new-feature.sh --json "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 -Json "{ARGS}"
```

The AI agent:
1. Determines platform (sh vs ps)
2. Runs script from repo root
3. Parses JSON output to get file paths
4. Uses absolute paths for all file operations

### Feature Numbering

Features are numbered sequentially starting from 001:
- Scripts scan `specs/` directory for highest `{number}-` prefix
- New features increment by 1
- Branch names are `{number}-{short-name}` (e.g., `001-user-auth`)

### Short Name Generation

When creating features, the AI generates 2-4 word short names:
- Action-noun format preferred (e.g., `add-oauth2`, `fix-payment-bug`)
- Preserves technical terms (OAuth2, JWT, API, etc.)
- Used in both branch names and directory names

### Template Placeholder Replacement

Templates should never be edited directly by AI. Instead:
1. Load template
2. Replace placeholders with concrete values
3. Write to target location (usually `specs/{feature}/`)

### Constitution-First Development

Every generated project should have a constitution before specs/plans:
- Encodes development principles (testing standards, architecture patterns)
- Referenced by planning commands to ensure consistency
- Versioned and amended through governance process

### Independent User Stories

Specifications must structure user stories as independently testable slices:
- Each story should be Priority-tagged (P1, P2, P3...)
- Stories deliver value even if implemented alone
- Enables incremental delivery and testing

### Task Parallelization

The `tasks.md` format supports parallel execution:
- Tasks marked `[P]` can run in parallel
- Tasks are grouped by user story
- Dependencies are explicitly ordered within each story
- Checkpoints validate independent functionality

## Common Development Scenarios

### Adding a New AI Agent

1. Update `AGENT_CONFIG` in `src/specify_cli/__init__.py`
2. Add agent folder, install URL, and CLI requirements
3. Create agent-specific template if needed (`templates/agent-file-template.md`)
4. Update README.md with agent in supported list
5. Test with `specify init --ai <new-agent>`

### Adding a New Slash Command

1. Create `templates/commands/{command-name}.md`
2. Add frontmatter with script execution
3. Write execution instructions for AI agent
4. If new script needed, create in `scripts/bash/` and `scripts/powershell/`
5. Update README.md documentation

### Modifying Templates

Templates are distributed with each release, so changes require:
1. Edit template in `templates/`
2. Test locally using create-release-packages.sh workflow
3. Verify in test project with actual AI agent
4. Release creates new template zips with changes

### Debugging Script Issues

Scripts output JSON for parsing by AI agents:
- Use `--debug` flag on CLI for verbose output
- Check script exits with code 0 on success
- Verify JSON is valid (use `jq` to test)
- Test both bash and PowerShell versions

### Handling Non-Git Repositories

For projects initialized with `--no-git`:
- Scripts fall back to scanning for `.specify` marker
- `SPECIFY_FEATURE` env var overrides branch detection
- Must be set before running `/speckit.plan` or later commands
- Format: `export SPECIFY_FEATURE=001-feature-name`

## Release Process

Releases are automated via GitHub Actions (`.github/workflows/release.yml`):

1. **Version Bump**: Update `pyproject.toml` version
2. **Generate Packages**: Creates template zips for each agent/script combination
3. **Create Release**: GitHub release with all template assets
4. **PyPI Publish**: (if configured) Publishes package to PyPI

Manual release creation:
```bash
# Update version in pyproject.toml first
./.github/workflows/scripts/get-next-version.sh
./.github/workflows/scripts/create-release-packages.sh v1.0.0
./.github/workflows/scripts/create-github-release.sh v1.0.0
```

## Testing Philosophy

- **Unit tests**: Test individual functions and utilities
- **Integration tests**: Test CLI commands end-to-end
- **Template validation**: Ensure templates have required sections
- **Script testing**: Verify JSON output format and error handling

The project emphasizes testing the CLI tool and scripts. Generated projects test their own code through the SDD workflow.

## Important Implementation Notes

### Offline Template Support

The CLI supports offline development via local template zips:
- Searches `src/specify_cli/spec-kit-templates/` directory for `spec-kit-template-{agent}-{script}-v{version}.zip`
- Templates are bundled with the package installation
- Uses latest version if multiple found (semantic versioning)
- Falls back to GitHub download if no local template found
- Does not delete local templates after use (only GitHub downloads)

Template storage location:
- **Installation directory**: `src/specify_cli/spec-kit-templates/` (primary location)
- Templates in this directory are preserved across installations when using `pip install -e .`

This is critical for:
- Corporate environments without GitHub access
- Development of template changes
- Offline demonstrations and workshops
- Bundling templates with package distributions

### Claude CLI Migration Issue

Special handling exists for Claude CLI after `claude migrate-installer`:
- Migration removes executable from PATH
- Creates alias at `~/.claude/local/claude`
- CLI checks this path first before falling back to PATH
- See issue #123 for details

### Cross-Platform Considerations

- Scripts exist in both bash and PowerShell
- Bash is primary, PowerShell mirrors functionality
- Execute permissions set automatically on POSIX systems
- Windows uses PowerShell by default, others use bash
- File paths always use absolute paths from repo root

### JSON Mode for Script Output

Scripts invoked by slash commands use `--json` flag:
- Outputs structured JSON instead of human-readable text
- AI agents parse JSON to extract file paths and metadata
- Errors go to stderr, JSON goes to stdout
- Enables reliable automation without parsing human text

### Security Considerations

- Agent folders (`.claude/`, `.github/`, etc.) may contain credentials
- Users warned to add to `.gitignore` to prevent leakage
- GitHub tokens supported via `--github-token` or env vars
- SSL/TLS verification can be skipped with `--skip-tls` (not recommended)

## Repository-Specific Guidelines

- Python 3.11+ required (uses modern type hints and match statements)
- Use `uv` for package management (preferred over pip)
- Single-file CLI design: keep `__init__.py` monolithic for easy distribution
- Rich terminal UI: leverage Rich library for progress, panels, and trees
- Cross-platform: test on Linux, macOS, and Windows
- No emoji in output unless user explicitly requests (keep professional)

When making changes:
1. Update both bash and PowerShell scripts if modifying workflow
2. Test with multiple AI agents if changing templates/commands
3. Verify offline template support still works
4. Update CHANGELOG.md following existing format
5. Ensure README.md reflects any new features or changed behavior
