# Implementation Plan: Local Template Zip

**Branch**: `001-local-template-zip` | **Date**: 2025-10-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-local-template-zip/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Modify the template download stage in the feature creation workflow to use local template zip files from the current folder instead of downloading from GitHub. The system will infer template arguments from `.specify` configuration files, match them against locally available templates following the pattern `spec-kit-template-{arg1}-{arg2}-v{version}.zip`, and select the latest version when multiple matches exist. This enables offline development and faster feature initialization.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Bash 4.0+ (existing script language)
**Primary Dependencies**: Standard Unix utilities (grep, sed, unzip, sort), existing `.specify` infrastructure
**Storage**: Local filesystem (current working directory for templates, `.specify/` for configuration)
**Testing**: Bash unit tests (bats-core or similar), integration tests with actual template files
**Target Platform**: Unix-like systems (Linux, macOS) where existing scripts run
**Project Type**: Single (CLI tooling extension)
**Performance Goals**: <1 second template selection and extraction (vs. 3-10s GitHub download)
**Constraints**: Must work offline, must integrate with existing create-new-feature.sh workflow, must preserve backward compatibility
**Scale/Scope**: Small modification to existing bash script infrastructure (~200-300 lines of new code)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ✅ PASS (Constitution is template-only, no specific constraints defined)

Since the constitution file is a template without specific project principles, we proceed with general best practices:
- Maintain existing script architecture and patterns
- Preserve backward compatibility with current workflow
- Follow Unix philosophy (text streams, composability)
- Ensure proper error handling and user feedback
- Write testable, modular bash functions

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# Existing structure (modification to bash scripts)
.specify/
├── scripts/
│   └── bash/
│       ├── create-new-feature.sh    # MODIFY: Add local template logic
│       ├── common.sh                 # MAY MODIFY: Add shared functions
│       └── lib/                      # NEW: Template matching functions
│           ├── template-finder.sh   # Find and validate local templates
│           ├── semver.sh             # Semantic version comparison
│           └── config-reader.sh      # Read .specify configuration
├── templates/
│   └── spec-template.md              # Existing (unchanged)
└── memory/
    └── constitution.md               # Existing (template)

tests/                                # NEW: Test infrastructure
├── integration/
│   └── test-local-template.bats     # End-to-end template selection tests
└── unit/
    ├── test-template-finder.bats    # Unit tests for finder functions
    ├── test-semver.bats              # Unit tests for version comparison
    └── test-config-reader.bats       # Unit tests for config reading
```

**Structure Decision**: Extend existing bash script infrastructure with modular library functions. New functionality added as sourced library files to maintain testability and separation of concerns. Tests use bats-core framework following bash testing conventions.

## Complexity Tracking

N/A - No constitution violations. This is a straightforward extension of existing bash script infrastructure.
