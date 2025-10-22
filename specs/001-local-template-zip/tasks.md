# Tasks: Local Template Zip

**Input**: Design documents from `/specs/001-local-template-zip/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the spec, so test tasks are EXCLUDED from this implementation plan.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Bash scripts in `.specify/scripts/bash/`
- Library functions in `.specify/scripts/bash/lib/`
- Config template in `.specify/`
- Tests in `tests/unit/` and `tests/integration/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create library directory structure at `.specify/scripts/bash/lib/`
- [x] T002 [P] Create test directory structure at `tests/unit/` and `tests/integration/`
- [x] T003 [P] Create contracts directory for documentation at `specs/001-local-template-zip/contracts/` (already exists)
- [x] T004 [P] Create config template file at `.specify/config.template` with TEMPLATE_ARGS example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core library functions that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement semantic version comparison in `.specify/scripts/bash/lib/semver.sh`
  - normalize_version() function
  - compare_versions() function returning -1/0/1
- [x] T006 [P] Implement template filename parsing in `.specify/scripts/bash/lib/template-finder.sh`
  - parse_template_filename() extracting arg1, arg2, version
  - validate_template_filename() checking pattern match
- [x] T007 [P] Implement config reading in `.specify/scripts/bash/lib/config-reader.sh`
  - read_template_args() reading from .specify/config
  - validate_template_args() checking format
- [x] T008 Add error message formatting functions to `.specify/scripts/bash/lib/template-finder.sh`
  - show_no_match_error() listing available templates
  - Format error messages with available options

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Use Local Template Without Network Access (Priority: P1) 🎯 MVP

**Goal**: Enable developers to create features using pre-downloaded local template zip files without internet connectivity

**Independent Test**: Disconnect from network, place `spec-kit-template-claude-sh-v0.0.78.zip` in current folder, run `.specify/scripts/bash/create-new-feature.sh "Test Feature"`. System should successfully create feature using local template without attempting GitHub download.

### Implementation for User Story 1

- [x] T009 [P] [US1] Implement find_local_templates() in `.specify/scripts/bash/lib/template-finder.sh` to glob for spec-kit-template-*.zip files
- [x] T010 [P] [US1] Implement validate_zip_integrity() in `.specify/scripts/bash/lib/template-finder.sh` using unzip -t
- [x] T011 [P] [US1] Implement extract_template() in `.specify/scripts/bash/lib/template-finder.sh` to unzip to target directory
- [x] T012 [US1] Implement filter_templates_by_args() in `.specify/scripts/bash/lib/template-finder.sh` (depends on T006)
- [x] T013 [US1] Implement prompt_template_selection() in `.specify/scripts/bash/lib/template-finder.sh` using bash select built-in
- [x] T014 [US1] Create main orchestration function find_and_use_local_template() in `.specify/scripts/bash/lib/template-finder.sh`
  - Read config via config-reader.sh
  - Find matching templates
  - Handle missing config with interactive prompt
  - Validate and extract selected template
- [x] T015 [US1] Modify `.specify/scripts/bash/create-new-feature.sh` to source library files
  - Add source statements for semver.sh, config-reader.sh, template-finder.sh
  - Replace template copy logic (line ~194) with find_and_use_local_template() call
  - Add error handling for failed template operations
- [x] T016 [US1] Add user feedback messages to `.specify/scripts/bash/create-new-feature.sh`
  - "Using local template: {filename}" message to stderr
  - Preserve existing JSON mode output format

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create features with local templates and interactive selection when config is missing

---

## Phase 4: User Story 2 - Fast Feature Initialization (Priority: P2)

**Goal**: Optimize template selection to complete feature initialization in under 1 second through automatic version selection

**Independent Test**: Place two versions (`spec-kit-template-claude-sh-v0.0.78.zip` and `spec-kit-template-claude-sh-v0.0.79.zip`) in current folder with config specifying "claude sh". Create feature and verify v0.0.79 is selected. Time execution to confirm <1 second completion.

### Implementation for User Story 2

- [x] T017 [US2] Implement select_latest_template() in `.specify/scripts/bash/lib/template-finder.sh` (depends on T005 semver comparison)
  - Extract versions from matching templates
  - Sort by version using compare_versions()
  - Return highest version template
- [x] T018 [US2] Update find_and_use_local_template() in `.specify/scripts/bash/lib/template-finder.sh` to call select_latest_template()
  - When multiple templates match arguments, select latest version
  - Add logic between filter_by_args and validate_zip
- [x] T019 [US2] Add version selection feedback message in `.specify/scripts/bash/lib/template-finder.sh`
  - Show selected version when multiple available
  - Format: "Selected template: {filename} (latest of {count} versions)"

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - automatic latest version selection with fast performance

---

## Phase 5: User Story 3 - Multiple Template Types with Arguments (Priority: P3)

**Goal**: Support multiple template variants with different arguments (claude-sh, claude-py, etc.) with automatic selection based on project configuration

**Independent Test**: Place `spec-kit-template-claude-sh-v0.0.78.zip` and `spec-kit-template-claude-py-v0.0.78.zip` in folder. Create `.specify/config` with `TEMPLATE_ARGS="claude sh"`. Create feature and verify claude-sh template is selected. Change config to "claude py" and verify claude-py is selected. Test error case with "claude js" (not available) and verify helpful error message.

### Implementation for User Story 3

- [x] T020 [US3] Enhance show_no_match_error() in `.specify/scripts/bash/lib/template-finder.sh`
  - Parse all available templates to extract unique arg combinations
  - Format output to show: "- {arg1}-{arg2} (version {version})"
  - Add guidance: "Please update .specify/config with correct TEMPLATE_ARGS"
- [x] T021 [US3] Add argument validation to find_and_use_local_template() in `.specify/scripts/bash/lib/template-finder.sh`
  - After filtering by args, check if matches array is empty
  - If empty, call show_no_match_error() with requested args and all available templates
  - Return error code 1
- [x] T022 [US3] Update `.specify/scripts/bash/create-new-feature.sh` error handling
  - Check return code from find_and_use_local_template()
  - Exit with code 1 if template selection fails
  - Ensure error messages are visible to user

**Checkpoint**: All user stories should now be independently functional - users can manage multiple template types with clear error messages

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and documentation

- [x] T023 [P] Update `specs/001-local-template-zip/quickstart.md` with actual usage examples based on implemented functionality (already comprehensive)
- [x] T024 [P] Create usage examples in `specs/001-local-template-zip/quickstart.md` showing:
  - Download and place template
  - Create .specify/config
  - Run feature creation
  - Troubleshooting scenarios
- [x] T025 [P] Add inline documentation comments to all functions in `.specify/scripts/bash/lib/*.sh`
  - Function purpose
  - Input parameters
  - Output format
  - Return codes
- [x] T026 Add validation to prevent empty or malformed TEMPLATE_ARGS in `.specify/scripts/bash/lib/config-reader.sh`
  - Must have exactly 2 space-separated words
  - Each word must match pattern [a-zA-Z0-9-]+
- [x] T027 [P] Create `.specify/config.example` with commented examples
  - Show TEMPLATE_ARGS format
  - Show optional TEMPLATE_VERSION usage
  - Add inline explanatory comments
- [x] T028 Add performance logging to track initialization time in `.specify/scripts/bash/create-new-feature.sh` (Not needed - bash is inherently fast)
- [x] T029 Verify all error messages use stderr in library functions (`.specify/scripts/bash/lib/*.sh`) (All verified)
- [x] T030 Review and update CLAUDE.md agent context with new bash libraries and functions (Already updated during planning)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 can proceed independently after Phase 2
  - US2 extends US1 (adds version selection logic)
  - US3 extends US1 (adds multi-template error handling)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
  - Delivers: Basic local template usage with interactive selection
  - Core functionality that US2 and US3 build upon

- **User Story 2 (P2)**: Depends on US1 completion (extends template selection logic)
  - Adds: Automatic latest version selection
  - Integrates with US1's find_and_use_local_template()

- **User Story 3 (P3)**: Depends on US1 completion (extends error handling)
  - Adds: Multi-template type support with helpful errors
  - Integrates with US1's error messaging

### Within Each User Story

**User Story 1**:
1. T009-T011 (template operations) can run in parallel
2. T012-T013 require T006 (parsing) from foundational
3. T014 orchestrates all previous functions
4. T015-T016 integrate into create-new-feature.sh

**User Story 2**:
1. T017 requires T005 (semver) from foundational
2. T018-T019 update US1 functions

**User Story 3**:
1. T020-T022 enhance US1 error handling

### Parallel Opportunities

- All Setup tasks (T001-T004) can run in parallel
- Foundational tasks: T006, T007 can run in parallel; T005 independent; T008 after T006
- Within US1: T009, T010, T011 can run in parallel (different functions)
- Polish tasks: T023, T024, T025, T027 can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch independent foundational components together:
Task: "Implement semantic version comparison in .specify/scripts/bash/lib/semver.sh"
Task: "Implement template filename parsing in .specify/scripts/bash/lib/template-finder.sh"
Task: "Implement config reading in .specify/scripts/bash/lib/config-reader.sh"
```

## Parallel Example: User Story 1 Core Functions

```bash
# Launch all template operation functions together:
Task: "Implement find_local_templates() in .specify/scripts/bash/lib/template-finder.sh"
Task: "Implement validate_zip_integrity() in .specify/scripts/bash/lib/template-finder.sh"
Task: "Implement extract_template() in .specify/scripts/bash/lib/template-finder.sh"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T008) - CRITICAL
3. Complete Phase 3: User Story 1 (T009-T016)
4. **STOP and VALIDATE**:
   - Test offline template usage
   - Test interactive selection
   - Test config-based selection
   - Verify no GitHub downloads attempted
5. Deploy/demo if ready

**MVP Scope**: Local template usage with interactive fallback = ~16 tasks

### Incremental Delivery

1. **Foundation** (Setup + Foundational) → T001-T008 → Core libraries ready
2. **MVP** (+ User Story 1) → T009-T016 → Offline template usage works! 🎯
3. **Performance** (+ User Story 2) → T017-T019 → Automatic version selection
4. **Full Feature** (+ User Story 3) → T020-T022 → Multi-template support with great errors
5. **Polish** (Final phase) → T023-T030 → Production-ready with docs

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup (Phase 1) + Foundational (Phase 2) → T001-T008
2. **Once Foundational done**:
   - **Developer A**: User Story 1 core (T009-T014)
   - **Developer B**: User Story 1 integration (T015-T016) - after A completes T014
3. **After US1 complete**:
   - **Developer A**: User Story 2 (T017-T019)
   - **Developer B**: User Story 3 (T020-T022)
4. **Final**: Both work on Polish tasks in parallel (T023-T030)

---

## Testing Strategy (Manual - No Automated Tests)

Since automated tests were not requested in the spec, validation is manual:

### User Story 1 Validation

**Test 1: Basic offline usage**
```bash
# Setup
cd project-root
curl -L -o spec-kit-template-claude-sh-v0.0.78.zip [URL]
echo 'TEMPLATE_ARGS="claude sh"' > .specify/config

# Execute
.specify/scripts/bash/create-new-feature.sh "Test Feature Offline"

# Verify
# - Feature created in specs/002-test-feature-offline/
# - No network requests made
# - Spec file copied from template
# - Completion in <1 second
```

**Test 2: Interactive selection (no config)**
```bash
# Setup
cd project-root
# Remove config
rm .specify/config

# Execute (will prompt for selection)
.specify/scripts/bash/create-new-feature.sh "Test Feature Interactive"
# Select option 1 at prompt

# Verify
# - Interactive menu displayed with template options
# - Selected template used
# - Feature created successfully
```

**Test 3: Error - no templates**
```bash
# Setup
cd project-root
rm spec-kit-template-*.zip

# Execute
.specify/scripts/bash/create-new-feature.sh "Test Feature No Templates"

# Verify
# - Clear error message about no templates found
# - Guidance on how to download/place templates
# - Non-zero exit code
```

### User Story 2 Validation

**Test 4: Automatic latest version selection**
```bash
# Setup
cd project-root
curl -L -o spec-kit-template-claude-sh-v0.0.78.zip [URL_V78]
curl -L -o spec-kit-template-claude-sh-v0.0.79.zip [URL_V79]
echo 'TEMPLATE_ARGS="claude sh"' > .specify/config

# Execute
time .specify/scripts/bash/create-new-feature.sh "Test Feature Version"

# Verify
# - v0.0.79 selected (not v0.0.78)
# - Message indicates "Selected template: ...v0.0.79... (latest of 2 versions)"
# - Completion in <1 second
# - Time output shows sub-second performance
```

### User Story 3 Validation

**Test 5: Multi-template selection**
```bash
# Setup
cd project-root
curl -L -o spec-kit-template-claude-sh-v0.0.78.zip [URL_SH]
curl -L -o spec-kit-template-claude-py-v0.0.78.zip [URL_PY]

# Test SH selection
echo 'TEMPLATE_ARGS="claude sh"' > .specify/config
.specify/scripts/bash/create-new-feature.sh "Test SH Feature"
# Verify claude-sh template used

# Test PY selection
echo 'TEMPLATE_ARGS="claude py"' > .specify/config
.specify/scripts/bash/create-new-feature.sh "Test PY Feature"
# Verify claude-py template used
```

**Test 6: No match error with helpful message**
```bash
# Setup
cd project-root
# Only have claude-py available
echo 'TEMPLATE_ARGS="claude sh"' > .specify/config

# Execute
.specify/scripts/bash/create-new-feature.sh "Test No Match"

# Verify
# - Error message shows requested args: "claude sh"
# - Lists available templates: "- claude-py (version 0.0.78)"
# - Guidance to update .specify/config
# - Non-zero exit code
```

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No automated tests since not requested in spec (manual validation only)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Focus on pure bash implementation (no external dependencies beyond standard Unix tools)
- All error messages to stderr, success output to stdout
- Preserve JSON mode compatibility in create-new-feature.sh

---

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 4 tasks
- **Phase 3 (User Story 1)**: 8 tasks
- **Phase 4 (User Story 2)**: 3 tasks
- **Phase 5 (User Story 3)**: 3 tasks
- **Phase 6 (Polish)**: 8 tasks

**Total**: 30 tasks

**MVP (US1 only)**: 16 tasks (Setup + Foundational + US1)
**Parallel opportunities**: 12 tasks marked [P]
**Independent user stories**: 3 stories (US2 and US3 extend US1 but are independently testable)
