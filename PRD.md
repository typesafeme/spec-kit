# Product Requirements Document (PRD)
# Spec Kit - GitHub Spec Kit

**Version:** 0.0.20
**Last Updated:** 2025-10-28
**Product Owner:** Den Delimarsky, John Lam
**Status:** Active Development

---

## Executive Summary

### Product Vision

Spec Kit is an open-source toolkit that revolutionizes software development by making specifications executable rather than disposable artifacts. It inverts the traditional code-first approach, establishing specifications as the source of truth that directly generate working implementations through AI coding agents.

### Objectives

1. **Enable Spec-Driven Development (SDD)**: Provide a complete workflow where specifications are executable and drive implementation
2. **Agent-Agnostic Platform**: Support 13+ AI coding agents (Claude Code, GitHub Copilot, Cursor, etc.) with consistent workflow
3. **Enterprise-Ready**: Support corporate environments with offline mode, proxy support, and configurable authentication
4. **Technology Independence**: Prove that SDD works across diverse tech stacks, languages, and frameworks
5. **Developer Productivity**: Reduce time from concept to working code by 40-60% through structured workflows

### Target Users

#### Primary Users
- **Individual Developers**: Software engineers using AI coding agents for personal or open-source projects
- **Development Teams**: Small to medium teams (2-20 developers) adopting AI-assisted development
- **Technical Leads**: Architects and senior engineers establishing development standards

#### Secondary Users
- **Enterprise Architects**: Organizations standardizing on AI-native development practices
- **Educators**: Instructors teaching modern software development methodologies
- **Open Source Maintainers**: Projects seeking structured contribution workflows

### Success Metrics

| Metric | Target | Current | Measurement Method |
|--------|--------|---------|-------------------|
| Weekly Active Users | 1,000+ | TBD | CLI telemetry (opt-in) |
| Project Initializations | 200/week | TBD | GitHub release downloads |
| Agent Coverage | 15+ agents | 13 agents | Agent configuration registry |
| Offline Mode Adoption | 20% of users | TBD | Usage analytics |
| Documentation Coverage | 100% of features | 85% | Doc review |
| Average Setup Time | <5 minutes | ~3 minutes | User testing |
| Specification Completion Rate | 80%+ | TBD | Workflow analytics |

---

## Functional Requirements

### FR-1: Project Initialization (Priority: P0 - Critical)

**Description**: Enable developers to bootstrap new Spec-Driven Development projects from templates with minimal configuration.

**User Stories**:
- As a developer, I want to initialize a new project with `specify init <project-name>` so that I can start using SDD immediately
- As a developer, I want to initialize SDD in my existing project with `specify init --here` to adopt SDD without creating a new directory
- As a developer working offline, I want to use local templates without internet access so I can work in restricted environments

**Functional Details**:

**FR-1.1**: CLI Command Interface
- MUST provide `specify init` command with project name argument
- MUST support `--here` flag for current directory initialization
- MUST support `.` shorthand for current directory (equivalent to `--here`)
- MUST prompt for missing required parameters (AI agent, script type)
- MUST provide `--help` documentation for all commands

**FR-1.2**: Agent Selection
- MUST support 13+ AI coding agents through `--ai` flag
- MUST provide interactive selection menu if `--ai` not specified
- MUST use arrow key navigation (↑/↓) with visual indicators (▶)
- MUST validate agent selection against known agents
- MUST check for CLI tool availability (for agents requiring CLI)
- MUST allow bypassing tool checks with `--ignore-agent-tools`

**FR-1.3**: Script Type Selection
- MUST support bash/zsh scripts (`--script sh`) for POSIX systems
- MUST support PowerShell scripts (`--script ps`) for Windows/cross-platform
- MUST auto-detect platform and suggest appropriate default
- MUST provide interactive selection if not specified
- MUST support non-interactive mode for CI/CD pipelines

**FR-1.4**: Template Acquisition
- MUST search for local templates in installation directory first
- MUST fall back to GitHub API for template download if local not found
- MUST support offline mode (`--offline` flag or `SPECIFY_OFFLINE=1` env var)
- MUST fail gracefully in offline mode when no local templates exist
- MUST display clear error messages with resolution steps

**FR-1.5**: Template Extraction
- MUST extract template to target directory (new or current)
- MUST merge with existing content when using `--here` in non-empty directory
- MUST prompt for confirmation before merging (unless `--force` flag used)
- MUST preserve local files when merging (warn on overwrite)
- MUST handle nested template directory structures (flatten if needed)
- MUST set executable permissions on `.sh` scripts (POSIX systems only)
- MUST merge .vscode/settings.json files (deep merge, not overwrite)

**FR-1.6**: Git Integration
- MUST detect existing git repositories
- MUST initialize new git repository (unless `--no-git` flag)
- MUST create initial commit with template files
- MUST skip git operations gracefully if git not installed
- MUST support non-git workflows via `SPECIFY_FEATURE` environment variable

**FR-1.7**: Progress Tracking
- MUST display real-time progress with tree-based UI (similar to Claude Code)
- MUST show step status: pending (○), running (○), done (●), error (●), skipped (○)
- MUST use color coding: green (success), red (error), yellow (warning), cyan (info)
- MUST refresh display during long-running operations
- MUST show final summary with all completed steps

**Acceptance Criteria**:
- [ ] Can initialize new project in <5 seconds (local template)
- [ ] Can initialize in existing project without data loss
- [ ] Works offline with pre-installed templates
- [ ] Supports all 13+ configured AI agents
- [ ] Handles network failures gracefully
- [ ] Sets correct file permissions on all platforms

---

### FR-2: Offline Mode Support (Priority: P0 - Critical)

**Description**: Enable developers to work without internet connectivity by using locally-stored template files.

**User Stories**:
- As a corporate developer, I want to use Spec Kit without internet access so I can work in air-gapped environments
- As a developer with unreliable internet, I want templates cached locally so I don't experience interruptions
- As a contributor, I want to test template changes locally before pushing to GitHub

**Functional Details**:

**FR-2.1**: Local Template Discovery
- MUST search `src/specify_cli/spec-kit-templates/` directory for templates
- MUST support naming pattern: `spec-kit-template-{agent}-{script}-v{version}.zip`
- MUST parse semantic versions from filenames (major.minor.patch)
- MUST sort templates by version (descending) and select latest
- MUST support multiple versions of same template

**FR-2.2**: Version Management
- MUST read version from `version.txt` in templates directory
- MUST display version information during initialization
- MUST compare template versions and select latest
- MUST allow manual version selection when multiple exist
- MUST preserve local templates (never delete after use)

**FR-2.3**: Interactive Template Selection
- MUST show selection menu when multiple template versions exist
- MUST display version numbers clearly (e.g., "v1.2.0")
- MUST allow arrow key navigation and Enter to confirm
- MUST auto-select when only one template exists
- MUST show template source (local vs. GitHub)

**FR-2.4**: Offline Mode Activation
- MUST support `--offline` CLI flag
- MUST support `SPECIFY_OFFLINE=1` environment variable
- MUST disable all GitHub API calls in offline mode
- MUST fail fast with helpful error if no local templates found
- MUST display offline mode status during initialization

**FR-2.5**: Error Handling
- MUST show clear error when offline mode enabled but no templates found
- MUST display expected template filename pattern
- MUST show installation directory path for template placement
- MUST provide instructions for enabling online mode
- MUST distinguish between "template not found" and "network error"

**Acceptance Criteria**:
- [ ] Works without internet when local templates exist
- [ ] Never makes network requests in offline mode
- [ ] Finds templates in installation directory
- [ ] Selects latest version automatically
- [ ] Shows clear errors with resolution steps
- [ ] Preserves templates after use (no cleanup)

---

### FR-3: Slash Command Workflow (Priority: P0 - Critical)

**Description**: Provide structured slash commands that guide AI agents through the Spec-Driven Development workflow from requirements to implementation.

**User Stories**:
- As a developer, I want to use `/speckit.constitution` to establish project principles so my AI agent makes consistent decisions
- As a developer, I want to use `/speckit.specify` to create specifications from natural language so I can focus on "what" not "how"
- As a developer, I want to use `/speckit.plan` to define technical architecture so I control technology choices
- As a developer, I want to use `/speckit.tasks` to break down work into actionable steps so I can track progress
- As a developer, I want to use `/speckit.implement` to execute tasks systematically so I get consistent, high-quality code

**Functional Details**:

**FR-3.1**: Constitution Command (`/speckit.constitution`)
- MUST create or update `.specify/memory/constitution.md` file
- MUST accept natural language description of project principles
- MUST structure content: Testing Standards, Architecture Patterns, Code Quality, UX Consistency, Performance
- MUST support versioning and governance process
- MUST be referenced by all subsequent workflow steps

**FR-3.2**: Specify Command (`/speckit.specify`)
- MUST execute `scripts/bash/create-new-feature.sh` (or PowerShell equivalent)
- MUST generate sequential feature numbers (001, 002, 003, ...)
- MUST create git branch named `{number}-{short-name}`
- MUST create spec directory in `specs/{number}-{short-name}/`
- MUST copy `spec-template.md` to spec directory
- MUST accept `$ARGUMENTS` as feature description
- MUST generate structured spec with user stories, requirements, success criteria
- MUST mark unclear requirements with `[NEEDS CLARIFICATION]` tags
- MUST output JSON with `BRANCH_NAME`, `SPEC_FILE`, `FEATURE_NUM`

**FR-3.3**: Clarify Command (`/speckit.clarify`) - Optional
- MUST analyze spec for underspecified areas
- MUST generate up to 5 targeted clarification questions
- MUST record answers in Clarifications section of spec
- MUST run BEFORE `/speckit.plan` for best results
- MUST support free-form refinement after structured questions

**FR-3.4**: Plan Command (`/speckit.plan`)
- MUST execute `scripts/bash/setup-plan.sh` (or PowerShell equivalent)
- MUST create `plan.md` from `plan-template.md`
- MUST accept tech stack and architecture decisions
- MUST generate implementation details in spec directory:
  - `data-model.md` - Entity definitions and relationships
  - `research.md` - Technology research and decisions
  - `quickstart.md` - Setup and run instructions
  - `contracts/` - API specifications, schemas
- MUST update agent context file (CLAUDE.md, copilot-instructions.md, etc.)
- MUST reference constitution for decision-making
- MUST validate prerequisites (constitution, spec exist)

**FR-3.5**: Analyze Command (`/speckit.analyze`) - Optional
- MUST perform cross-artifact consistency analysis
- MUST check alignment between spec.md, plan.md, tasks.md
- MUST identify gaps, conflicts, or missing details
- MUST run AFTER `/speckit.tasks`, BEFORE `/speckit.implement`
- MUST generate non-destructive analysis report

**FR-3.6**: Tasks Command (`/speckit.tasks`)
- MUST execute prerequisite checks (constitution, spec, plan exist)
- MUST generate `tasks.md` from implementation plan
- MUST organize tasks by user story (priority-based)
- MUST order tasks respecting dependencies (models → services → endpoints)
- MUST mark parallel-executable tasks with `[P]` prefix
- MUST include file paths for each task
- MUST add checkpoint validation after each user story
- MUST support TDD workflow (tests before implementation)

**FR-3.7**: Checklist Command (`/speckit.checklist`) - Optional
- MUST generate custom quality checklists
- MUST validate requirements completeness, clarity, consistency
- MUST act as "unit tests for English" specification
- MUST support running after `/speckit.plan`

**FR-3.8**: Implement Command (`/speckit.implement`)
- MUST validate all prerequisites exist (constitution, spec, plan, tasks)
- MUST parse task breakdown from `tasks.md`
- MUST execute tasks in dependency order
- MUST respect parallel execution markers `[P]`
- MUST follow TDD approach if specified
- MUST provide progress updates
- MUST handle errors and failures gracefully
- MUST support pausing and resuming implementation

**FR-3.9**: Script Execution
- MUST support both bash (`.sh`) and PowerShell (`.ps1`) variants
- MUST execute from repository root
- MUST parse JSON output from scripts
- MUST use absolute paths for all file operations
- MUST handle both git and non-git repositories
- MUST set `SPECIFY_FEATURE` env var for non-git workflows

**Acceptance Criteria**:
- [ ] All commands execute successfully in sequence
- [ ] Scripts work on Linux, macOS, and Windows
- [ ] JSON output parsing is reliable
- [ ] Git integration works (branch creation, commits)
- [ ] Non-git workflows function via `SPECIFY_FEATURE`
- [ ] Agent context files update correctly
- [ ] Prerequisites are validated before each step

---

### FR-4: Multi-Agent Support (Priority: P0 - Critical)

**Description**: Support diverse AI coding agents with agent-specific configurations and workflows while maintaining a consistent SDD process.

**User Stories**:
- As a developer using Claude Code, I want my `.claude/` directory configured automatically so I can use Claude-specific features
- As a developer using GitHub Copilot, I want my `.github/` directory set up so Copilot workflows are enabled
- As a developer switching agents, I want consistent slash commands so my workflow doesn't change

**Functional Details**:

**FR-4.1**: Agent Configuration Registry
- MUST maintain `AGENT_CONFIG` dictionary in CLI tool
- MUST define for each agent:
  - Display name (e.g., "Claude Code")
  - Folder name (e.g., `.claude/`)
  - Install URL (if applicable)
  - CLI requirement flag (requires_cli: true/false)
- MUST support both IDE-based (no CLI) and CLI-based agents

**FR-4.2**: Supported Agents
- MUST support these agents (as of v0.0.20):
  1. Claude Code (`claude`) - CLI required
  2. GitHub Copilot (`copilot`) - IDE-based
  3. Gemini CLI (`gemini`) - CLI required
  4. Cursor (`cursor-agent`) - IDE-based
  5. Qwen Code (`qwen`) - CLI required
  6. opencode (`opencode`) - CLI required
  7. Codex CLI (`codex`) - CLI required
  8. Windsurf (`windsurf`) - IDE-based
  9. Kilo Code (`kilocode`) - IDE-based
  10. Auggie CLI (`auggie`) - CLI required
  11. CodeBuddy (`codebuddy`) - CLI required
  12. Roo Code (`roo`) - IDE-based
  13. Amazon Q Developer CLI (`q`) - CLI required (with limitations)
  14. Amp (`amp`) - CLI required

**FR-4.3**: Agent Detection
- MUST check if agent CLI tool is installed (for CLI-based agents)
- MUST use `shutil.which()` for tool detection
- MUST handle special case for Claude CLI (check `~/.claude/local/claude` after `claude migrate-installer`)
- MUST skip CLI checks for IDE-based agents
- MUST allow bypassing checks with `--ignore-agent-tools`

**FR-4.4**: Agent-Specific Templates
- MUST support agent-specific context files (e.g., `CLAUDE-template.md`)
- MUST copy to project root during initialization (e.g., `CLAUDE.md`)
- MUST populate with project-specific guidance
- MUST update during `/speckit.plan` command execution
- MUST support multiple template formats (Markdown, JSON, YAML)

**FR-4.5**: Security Considerations
- MUST warn users about credential storage in agent folders
- MUST recommend adding agent folders to `.gitignore`
- MUST display security notice after initialization
- MUST document sensitive paths in agent-specific docs

**FR-4.6**: Agent Limitations
- MUST document known limitations (e.g., Amazon Q CLI lacks custom slash command arguments)
- MUST provide workarounds where possible
- MUST clearly communicate unsupported features per agent

**Acceptance Criteria**:
- [ ] All 14+ agents initialize successfully
- [ ] Agent-specific folders are created correctly
- [ ] CLI detection works reliably
- [ ] Special handling for Claude CLI migration works
- [ ] Security warnings display appropriately
- [ ] Agent limitations are documented

---

### FR-5: Feature Branching and Versioning (Priority: P1 - High)

**Description**: Manage feature specifications through numbered branches and directories with support for parallel development and non-git workflows.

**User Stories**:
- As a developer, I want features numbered sequentially (001, 002, 003) so I can track feature evolution
- As a developer on a team, I want branches to match spec directories so everyone knows where to find documentation
- As a developer in a non-git project, I want to use `SPECIFY_FEATURE` env var so I can still use SDD workflows

**Functional Details**:

**FR-5.1**: Feature Numbering
- MUST scan `specs/` directory for existing features
- MUST detect highest numeric prefix (e.g., 003 in `003-user-auth`)
- MUST increment by 1 for new features
- MUST format as 3-digit padded number (001, 002, ...)
- MUST check both local branches and remote branches (if git available)
- MUST check spec directories as fallback

**FR-5.2**: Branch Naming
- MUST use format `{number}-{short-name}` (e.g., `001-user-auth`)
- MUST generate short-name from feature description
- MUST filter common stop words (a, an, the, to, for, of, in, on, at, by, with, etc.)
- MUST keep meaningful words (length >= 3 chars)
- MUST preserve technical terms and acronyms (OAuth2, JWT, API, etc.)
- MUST limit to 2-4 words for short-name
- MUST enforce GitHub's 244-byte branch name limit
- MUST truncate at word boundaries if too long

**FR-5.3**: Branch Creation
- MUST create git branch if git repository exists
- MUST skip branch creation if `--no-git` used during init
- MUST warn when git not available
- MUST support manual branch numbering with `--number` flag
- MUST support custom short-name with `--short-name` flag

**FR-5.4**: Spec Directory Management
- MUST create directory in `specs/{number}-{short-name}/`
- MUST copy templates to spec directory
- MUST support multiple branches per spec (same numeric prefix)
- MUST use prefix-based directory lookup (e.g., `004-*` matches any `004-` directory)

**FR-5.5**: Non-Git Workflow Support
- MUST support `SPECIFY_FEATURE` environment variable
- MUST use env var to override branch detection
- MUST set env var automatically after feature creation
- MUST validate env var format (must match `{number}-{name}` pattern)
- MUST document env var in all relevant command docs

**FR-5.6**: Remote Branch Checking
- MUST fetch all remotes before checking branches
- MUST use `git ls-remote` to query remote branches
- MUST prevent duplicate feature numbers across remotes
- MUST handle missing remotes gracefully (offline scenario)

**Acceptance Criteria**:
- [ ] Features numbered sequentially without gaps
- [ ] Branch names are valid and within GitHub limits
- [ ] Short names are meaningful (no stop words)
- [ ] Multiple branches can work on same spec directory
- [ ] Non-git workflows function via `SPECIFY_FEATURE`
- [ ] Remote branches checked before assigning numbers

---

### FR-6: Template System (Priority: P1 - High)

**Description**: Provide a flexible, extensible template system for specifications, plans, tasks, and slash commands that guides AI agents to produce consistent output.

**User Stories**:
- As a developer, I want templates to guide the AI agent so specifications are consistent across features
- As a maintainer, I want to customize templates so they match my project's needs
- As a contributor, I want placeholder syntax to be clear so I can extend templates easily

**Functional Details**:

**FR-6.1**: Template Types
- MUST provide `spec-template.md` for feature specifications
- MUST provide `plan-template.md` for implementation plans
- MUST provide `tasks-template.md` for task breakdowns
- MUST provide agent-specific templates (e.g., `CLAUDE-template.md`)
- MUST provide command templates for slash commands (`.md` files in `templates/commands/`)
- MUST provide `constitution.md` template for project principles

**FR-6.2**: Template Structure
- MUST use Markdown format for all templates
- MUST include placeholder syntax:
  - `[PLACEHOLDER]` - Required replacement fields
  - `$ARGUMENTS` - User input from slash command
  - `{ARGS}`, `{SCRIPT}` - Command metadata
  - `<!--COMMENTS-->` - Guidance that remains in generated files
- MUST include section headers and structure
- MUST include examples and guidance comments
- MUST support conditional sections (optional content)

**FR-6.3**: Spec Template Requirements
- MUST include User Scenarios & Testing section (mandatory)
- MUST support prioritized user stories (P1, P2, P3, ...)
- MUST require independently testable user stories
- MUST include acceptance scenarios (Given/When/Then format)
- MUST include Functional Requirements section (FR-001, FR-002, ...)
- MUST support marking unclear requirements with `[NEEDS CLARIFICATION]`
- MUST include Key Entities section (if data-driven feature)
- MUST include Success Criteria section
- MUST include Review & Acceptance Checklist

**FR-6.4**: Plan Template Requirements
- MUST include Implementation Strategy section
- MUST include Tech Stack & Dependencies section
- MUST include Architecture & Components section
- MUST include Data Flow section
- MUST include Testing Strategy section
- MUST include References to additional docs (research.md, data-model.md, etc.)

**FR-6.5**: Tasks Template Requirements
- MUST organize tasks by user story
- MUST include task numbering (1.1, 1.2, 2.1, ...)
- MUST support parallel execution markers `[P]`
- MUST include file paths for each task
- MUST include checkpoint validation sections
- MUST support TDD task ordering (tests before implementation)

**FR-6.6**: Command Template Structure
- MUST include YAML frontmatter with script execution:
  ```yaml
  scripts:
    sh: scripts/bash/script-name.sh --json "{ARGS}"
    ps: scripts/powershell/script-name.ps1 -Json "{ARGS}"
  ```
- MUST include user input capture section
- MUST include step-by-step execution instructions for AI agent
- MUST document expected outputs and error handling

**FR-6.7**: Template Distribution
- MUST bundle templates with each release
- MUST create platform-specific zips (agent + script type combinations)
- MUST version templates with semantic versioning
- MUST support local template overrides (user customization)

**Acceptance Criteria**:
- [ ] All templates follow consistent structure
- [ ] Placeholders are clearly documented
- [ ] Generated specs pass validation checklist
- [ ] Templates support all workflow phases
- [ ] Agent-specific templates customize correctly
- [ ] Templates can be extended by users

---

### FR-7: Cross-Platform Script Execution (Priority: P1 - High)

**Description**: Execute workflow automation scripts reliably across Linux, macOS, and Windows platforms with consistent behavior.

**User Stories**:
- As a Linux developer, I want to use bash scripts so I work in my native environment
- As a Windows developer, I want to use PowerShell scripts so I work in my native environment
- As a CI/CD pipeline author, I want scripts to work headless so automation doesn't require user input

**Functional Details**:

**FR-7.1**: Script Variants
- MUST maintain bash (`.sh`) versions for POSIX systems (Linux, macOS, WSL)
- MUST maintain PowerShell (`.ps1`) versions for Windows
- MUST keep feature parity between bash and PowerShell versions
- MUST use same JSON output format across variants
- MUST document any platform-specific behaviors

**FR-7.2**: Script Discovery
- MUST locate scripts relative to repository root
- MUST use `git rev-parse --show-toplevel` when git available
- MUST fall back to `.specify` marker search for non-git repos
- MUST load common functions from `common.sh` / `common.ps1`

**FR-7.3**: JSON Output Mode
- MUST support `--json` flag for machine-readable output
- MUST output valid JSON to stdout
- MUST send errors to stderr
- MUST use consistent JSON schema across scripts
- MUST allow human-readable output when `--json` not specified

**FR-7.4**: Script Permissions
- MUST set executable permissions (`chmod +x`) on `.sh` files (POSIX only)
- MUST handle symlinks correctly (skip permission changes)
- MUST check shebang (`#!/usr/bin/env bash`) before setting permissions
- MUST recursively process all scripts in `.specify/scripts/`
- MUST report permission change failures

**FR-7.5**: Error Handling
- MUST use `set -e` to fail on errors (bash)
- MUST use `$ErrorActionPreference = "Stop"` (PowerShell)
- MUST validate required arguments
- MUST provide meaningful error messages
- MUST exit with non-zero codes on failure

**FR-7.6**: Environment Variable Support
- MUST read `SPECIFY_FEATURE` for non-git workflows
- MUST support `GH_TOKEN` / `GITHUB_TOKEN` for GitHub API auth
- MUST support `SPECIFY_OFFLINE` for offline mode
- MUST support `CODEX_HOME` for Codex CLI (if using Codex agent)

**Acceptance Criteria**:
- [ ] Scripts work on Linux, macOS, Windows
- [ ] Both bash and PowerShell variants produce identical results
- [ ] JSON output is valid and parseable
- [ ] Permissions set correctly on POSIX systems
- [ ] Error messages are clear and actionable
- [ ] Environment variables respected consistently

---

### FR-8: Prerequisites Validation (Priority: P2 - Medium)

**Description**: Validate that required files and dependencies exist before executing workflow steps to prevent partial or failed workflows.

**User Stories**:
- As a developer, I want to be blocked from running `/speckit.plan` without a constitution so I don't create inconsistent plans
- As a developer, I want to be blocked from running `/speckit.implement` without tasks so I don't waste time on incomplete setups
- As a developer, I want clear error messages so I know what to fix

**Functional Details**:

**FR-8.1**: Dependency Chain
- MUST enforce this workflow order:
  1. `/speckit.constitution` (creates `.specify/memory/constitution.md`)
  2. `/speckit.specify` (requires constitution, creates `spec.md`)
  3. `/speckit.clarify` (optional, modifies `spec.md`)
  4. `/speckit.plan` (requires constitution + spec, creates `plan.md` + details)
  5. `/speckit.analyze` (optional, requires spec + plan + tasks)
  6. `/speckit.tasks` (requires constitution + spec + plan, creates `tasks.md`)
  7. `/speckit.implement` (requires all of above)

**FR-8.2**: Check Prerequisites Script
- MUST provide `check-prerequisites.sh` / `check-prerequisites.ps1`
- MUST validate feature directory exists
- MUST validate required files exist (constitution, spec, plan)
- MUST support `--require-tasks` flag for implementation phase
- MUST support `--paths-only` for path queries without validation
- MUST output JSON or human-readable format

**FR-8.3**: File Validation
- MUST check for `.specify/memory/constitution.md`
- MUST check for `specs/{feature}/spec.md`
- MUST check for `specs/{feature}/plan.md`
- MUST check for `specs/{feature}/tasks.md` (if required)
- MUST detect optional files (research.md, data-model.md, contracts/, quickstart.md)

**FR-8.4**: Error Reporting
- MUST display clear error message for missing constitution
- MUST display clear error message for missing spec
- MUST display clear error message for missing plan
- MUST display clear error message for missing tasks (when required)
- MUST suggest next command to run (e.g., "Run /speckit.plan first")

**FR-8.5**: Available Documents List
- MUST enumerate optional documents that exist
- MUST show checkmarks (✓) for existing files
- MUST show X marks (✗) for missing files
- MUST include in JSON output for agent consumption

**Acceptance Criteria**:
- [ ] Cannot run plan without constitution
- [ ] Cannot run tasks without plan
- [ ] Cannot run implement without tasks
- [ ] Error messages clearly state what's missing
- [ ] Scripts exit with non-zero code on validation failure

---

## Non-Functional Requirements

### NFR-1: Performance

**NFR-1.1**: Initialization Speed
- MUST initialize project in <5 seconds with local template
- MUST initialize project in <30 seconds with GitHub download (typical network)
- MUST download templates with progress indication
- SHOULD use streaming downloads (no in-memory buffering of entire file)

**NFR-1.2**: Script Execution
- MUST execute feature creation in <2 seconds (local filesystem)
- MUST execute prerequisite checks in <500ms
- MUST cache git branch queries (avoid repeated `git ls-remote` calls)

**NFR-1.3**: Template Processing
- MUST extract ZIP templates in <3 seconds
- MUST support templates up to 50MB in size
- SHOULD handle large templates (100MB+) without memory issues

### NFR-2: Reliability

**NFR-2.1**: Error Handling
- MUST handle network failures gracefully (retry with exponential backoff)
- MUST handle missing tools gracefully (clear error messages)
- MUST handle filesystem permission errors (suggest fixes)
- MUST validate JSON parsing (fail fast on malformed output)
- MUST clean up temporary files on failure

**NFR-2.2**: Data Integrity
- MUST never corrupt existing files during merge operations
- MUST never delete user data during initialization
- MUST preserve git history (no force pushes or rewriting)
- MUST validate JSON output from scripts before parsing

**NFR-2.3**: Rollback and Recovery
- MUST delete project directory on initialization failure (new projects only)
- MUST preserve existing content on --here initialization failure
- MUST provide clear recovery instructions in error messages

### NFR-3: Usability

**NFR-3.1**: Command Line Interface
- MUST provide --help for all commands and flags
- MUST use consistent flag naming (--flag-name, not --flagName)
- MUST show progress indicators for long operations
- MUST use color coding for better readability (green=success, red=error, yellow=warning)
- MUST support non-interactive mode (all flags provided via CLI)

**NFR-3.2**: Error Messages
- MUST provide actionable error messages (what went wrong + how to fix)
- MUST include relevant context (file paths, command syntax)
- MUST avoid technical jargon where possible
- MUST link to documentation for complex issues

**NFR-3.3**: Documentation
- MUST provide README with quick start guide
- MUST document all CLI flags and options
- MUST provide examples for common scenarios
- MUST document troubleshooting steps for known issues
- MUST maintain CLAUDE.md with development guidelines

### NFR-4: Compatibility

**NFR-4.1**: Platform Support
- MUST work on Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+)
- MUST work on macOS (Monterey 12+, Ventura 13+, Sonoma 14+)
- MUST work on Windows (Windows 10 21H2+, Windows 11)
- MUST work on WSL (Windows Subsystem for Linux)

**NFR-4.2**: Python Compatibility
- MUST require Python 3.11 or higher
- MUST use modern type hints (PEP 604 union syntax)
- MUST use pattern matching (match statements) where appropriate
- SHOULD avoid deprecated APIs

**NFR-4.3**: Dependency Management
- MUST use uv for package management (preferred)
- MUST support pip as fallback
- MUST pin critical dependencies (truststore>=0.10.4)
- MUST support editable installs (pip install -e .)

**NFR-4.4**: Git Compatibility
- MUST work with Git 2.20+
- MUST support repositories with multiple remotes
- MUST work with repositories without remotes (offline)
- MUST work with repositories using Git LFS
- MUST work in non-git projects (via SPECIFY_FEATURE)

### NFR-5: Security

**NFR-5.1**: Credential Handling
- MUST support GitHub tokens via CLI flag or environment variables
- MUST NOT log tokens or secrets
- MUST use HTTPS for all GitHub API calls
- MUST support SSL/TLS verification (with --skip-tls escape hatch)
- MUST use truststore for certificate validation

**NFR-5.2**: File System Security
- MUST respect file permissions (no chmod 777)
- MUST warn about credential storage in agent folders
- MUST recommend .gitignore for sensitive folders
- MUST validate file paths (prevent directory traversal)

**NFR-5.3**: Network Security
- MUST use TLS 1.2+ for GitHub API calls
- MUST verify SSL certificates by default
- MUST support proxy environments (via httpx[socks])
- MUST handle redirects safely (follow_redirects with limits)

### NFR-6: Maintainability

**NFR-6.1**: Code Organization
- MUST use single-file CLI architecture for easy distribution
- MUST keep __init__.py monolithic (no multi-file refactoring)
- MUST use clear function names and docstrings
- MUST use type hints throughout codebase

**NFR-6.2**: Testing
- SHOULD provide unit tests for core functions
- SHOULD provide integration tests for CLI commands
- SHOULD provide end-to-end tests for workflows
- MUST test both bash and PowerShell script variants

**NFR-6.3**: Version Control
- MUST use semantic versioning (major.minor.patch)
- MUST maintain CHANGELOG.md with all changes
- MUST tag releases in git
- MUST create GitHub releases with assets

**NFR-6.4**: Documentation Maintenance
- MUST keep README.md in sync with features
- MUST update CLAUDE.md with development practices
- MUST document breaking changes in CHANGELOG
- MUST provide migration guides for major versions

### NFR-7: Scalability

**NFR-7.1**: Feature Scale
- MUST support 1,000+ features in single repository
- MUST handle feature numbers up to 999 (3-digit limit)
- MUST perform efficiently with large specs/ directories

**NFR-7.2**: Template Scale
- MUST support templates with 100+ files
- MUST handle deeply nested directory structures (10+ levels)
- MUST merge large .vscode/settings.json files (10,000+ lines)

**NFR-7.3**: Concurrent Usage
- SHOULD handle multiple `specify init` processes safely (no race conditions)
- SHOULD handle concurrent git operations (feature branch creation)

### NFR-8: Extensibility

**NFR-8.1**: Agent Plugins
- MUST support adding new agents via AGENT_CONFIG
- MUST support custom agent folder names
- MUST support custom install URLs per agent
- MUST support agent-specific template files

**NFR-8.2**: Template Customization
- MUST allow users to override default templates
- MUST support custom slash commands (user-defined .md files)
- MUST support custom script hooks (pre/post init)

**NFR-8.3**: Script Extension
- MUST provide common.sh / common.ps1 with reusable functions
- MUST allow custom scripts in .specify/scripts/
- MUST document script extension points

---

## Technical Constraints

### TC-1: Development Stack
- **Language**: Python 3.11+ (required for modern type hints and match statements)
- **CLI Framework**: Typer (command parsing, argument handling)
- **UI Framework**: Rich (terminal formatting, progress indicators, panels)
- **HTTP Client**: httpx with truststore (SSL/TLS, proxies, streaming)
- **Keyboard Input**: readchar (cross-platform arrow key detection)
- **Package Management**: uv (preferred), pip (fallback)

### TC-2: External Dependencies
- **Git**: Optional (workflows degrade gracefully if not installed)
- **GitHub API**: Optional (offline mode for air-gapped environments)
- **AI Agent CLIs**: Optional (can skip with --ignore-agent-tools)

### TC-3: File System Requirements
- **Writable directory**: Must have write permissions for project initialization
- **Execute permissions**: Must support setting +x on shell scripts (POSIX)
- **Case sensitivity**: Must handle case-sensitive (Linux) and case-insensitive (Windows/macOS) filesystems

### TC-4: Network Requirements
- **GitHub API**: https://api.github.com/repos/github/spec-kit/releases/latest
- **GitHub Assets**: https://github.com/github/spec-kit/releases/download/{tag}/{file}
- **Proxy Support**: Must work behind corporate proxies (via httpx[socks])
- **Offline Mode**: Must work without network (local templates)

### TC-5: Repository Constraints
- **Directory Structure**: Must create `.specify/` directory
- **Branch Naming**: Must follow `{number}-{short-name}` pattern (if using git)
- **File Naming**: Must follow lowercase-with-hyphens convention

---

## Known Limitations

### L-1: Amazon Q Developer CLI Limitation
**Issue**: Amazon Q Developer CLI does not support custom arguments for slash commands (as of 2025-10-28)
**Impact**: Cannot pass `$ARGUMENTS` to scripts, limiting workflow functionality
**Workaround**: Use environment variables or interactive prompts
**Reference**: https://github.com/aws/amazon-q-developer-cli/issues/3064

### L-2: Windows PowerShell Execution Policy
**Issue**: Windows may block PowerShell script execution due to execution policy
**Impact**: Scripts fail with "cannot be loaded because running scripts is disabled"
**Workaround**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### L-3: Claude CLI Migration
**Issue**: After `claude migrate-installer`, Claude CLI is removed from PATH
**Impact**: CLI detection fails with standard `shutil.which("claude")`
**Workaround**: Check `~/.claude/local/claude` path explicitly (implemented)

### L-4: Git Branch Name Length
**Issue**: GitHub enforces 244-byte limit on branch names
**Impact**: Long feature descriptions generate branches that exceed limit
**Workaround**: Automatic truncation at word boundaries (implemented)

### L-5: Non-Git Feature Numbering
**Issue**: In non-git repos, cannot check remote branches for numbers
**Impact**: Risk of duplicate feature numbers if multiple developers create features simultaneously
**Workaround**: Manual coordination or use git repository

---

## Future Enhancements

### FE-1: Cloud Storage for Templates (Planned for v0.1.0)
- Support S3, Azure Blob Storage, GCS for template distribution
- Enable corporate template registries
- Support private template repositories

### FE-2: Template Marketplace (Planned for v0.2.0)
- Community-contributed templates for common stacks
- Rating and review system
- One-click template installation

### FE-3: Workflow Analytics (Planned for v0.3.0)
- Track workflow completion rates
- Identify bottlenecks in SDD process
- Measure time from spec to implementation
- Aggregate insights across projects (opt-in, anonymous)

### FE-4: VS Code Extension (Planned for v0.4.0)
- Integrated slash commands in VS Code
- Syntax highlighting for spec templates
- Real-time validation of specifications
- Diff view for plan vs. implementation

### FE-5: Multi-Repo Support (Planned for v0.5.0)
- Manage specs across multiple repositories
- Cross-repo dependency tracking
- Monorepo support with sub-project specs

### FE-6: Spec Versioning and History (Planned for v0.6.0)
- Version control for specifications (independent of git)
- Diff view for spec changes over time
- Rollback to previous spec versions
- Change impact analysis

### FE-7: AI Model Selection (Planned for v0.7.0)
- Support multiple AI models per agent (e.g., Claude Sonnet vs. Opus)
- Model-specific optimizations
- Cost tracking per model

### FE-8: Collaboration Features (Planned for v0.8.0)
- Multi-user spec editing with conflict resolution
- Comments and discussions on spec sections
- Approval workflows for specs and plans
- Integration with GitHub Issues/PRs

---

## Appendix

### A: Glossary

| Term | Definition |
|------|------------|
| **SDD** | Spec-Driven Development - methodology where specifications are executable and drive implementation |
| **Feature** | A unit of work represented by a numbered branch and spec directory (e.g., `001-user-auth`) |
| **Slash Command** | AI agent command starting with `/` (e.g., `/speckit.specify`) |
| **Constitution** | Project-level principles and guidelines stored in `.specify/memory/constitution.md` |
| **Agent** | AI coding assistant (Claude Code, GitHub Copilot, etc.) |
| **Template** | Markdown file with placeholders used to generate specs, plans, tasks |
| **Spec Directory** | Directory under `specs/` containing all artifacts for a feature |
| **Prerequisites** | Required files that must exist before running a workflow step |
| **Offline Mode** | Operation mode using local templates without GitHub API calls |

### B: File Structure

```
project-root/
├── .specify/                          # SDD toolkit directory
│   ├── memory/
│   │   └── constitution.md            # Project principles
│   ├── scripts/
│   │   ├── bash/                      # POSIX shell scripts
│   │   │   ├── create-new-feature.sh
│   │   │   ├── setup-plan.sh
│   │   │   ├── check-prerequisites.sh
│   │   │   ├── update-agent-context.sh
│   │   │   └── common.sh
│   │   └── powershell/                # PowerShell scripts (mirrors bash/)
│   ├── specs/                         # Feature specifications
│   │   └── {number}-{short-name}/     # e.g., 001-user-auth
│   │       ├── spec.md                # Feature specification
│   │       ├── plan.md                # Implementation plan
│   │       ├── tasks.md               # Task breakdown
│   │       ├── research.md            # Technology research
│   │       ├── data-model.md          # Entity definitions
│   │       ├── quickstart.md          # Setup instructions
│   │       └── contracts/             # API specs, schemas
│   └── templates/                     # Template files
│       ├── spec-template.md
│       ├── plan-template.md
│       ├── tasks-template.md
│       ├── constitution-template.md
│       ├── {AGENT}-template.md        # Agent-specific templates
│       └── commands/                  # Slash command definitions
│           ├── constitution.md
│           ├── specify.md
│           ├── clarify.md
│           ├── plan.md
│           ├── analyze.md
│           ├── tasks.md
│           ├── checklist.md
│           └── implement.md
├── .{agent}/                          # Agent-specific directory (e.g., .claude/, .github/)
├── {AGENT}.md                         # Agent context file (e.g., CLAUDE.md)
└── .gitignore                         # Recommended: exclude agent folders
```

### C: Workflow Diagram

```
┌─────────────────────┐
│  specify init       │ ─→ Initialize project with templates
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ /speckit.constitution │ ─→ Create project principles
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ /speckit.specify    │ ─→ Create feature spec (what & why)
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ /speckit.clarify    │ ─→ (Optional) Clarify requirements
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ /speckit.plan       │ ─→ Create implementation plan (how)
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ /speckit.tasks      │ ─→ Break down into actionable tasks
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ /speckit.analyze    │ ─→ (Optional) Validate consistency
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ /speckit.implement  │ ─→ Execute tasks and build feature
└─────────────────────┘
```

### D: Related Documents

- [README.md](./README.md) - User-facing documentation
- [CLAUDE.md](./CLAUDE.md) - Developer guidelines for contributing
- [CHANGELOG.md](./CHANGELOG.md) - Version history
- [OFFLINE_MODE.md](./OFFLINE_MODE.md) - Offline mode detailed documentation
- [spec-driven.md](./spec-driven.md) - Spec-Driven Development methodology

---

**Document History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-28 | Claude Code | Initial PRD generated from codebase analysis |
