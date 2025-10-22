# Feature Specification: Local Template Zip

**Feature Branch**: `001-local-template-zip`
**Created**: 2025-10-22
**Status**: Draft
**Input**: User description: "make the "download template" stage look for zip file within current folder rather than downloading from github. In a way i want to skip the download template stage and always use the template zip file from local folder"

## Clarifications

### Session 2025-10-22

- Q: How are template arguments specified to the system (e.g., "claude" and "sh")? → A: Template arguments are inferred from project context (e.g., detecting existing files/config)
- Q: What project context signals should the system use to infer template arguments? → A: Detect from existing .specify configuration or constitution file
- Q: What should happen when .specify configuration/constitution is missing or doesn't contain template argument information? → A: Prompt user interactively to select from available templates
- Q: What level of validation should be performed on the local template zip file? → A: Validate only that it's a valid zip file (can be extracted without errors)
- Q: What should happen when no template matches the inferred arguments? → A: Throw error with list of available templates and their arguments

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Use Local Template Without Network Access (Priority: P1)

A developer working offline or in a network-restricted environment needs to create a new feature using a pre-downloaded template zip file stored locally, without requiring internet connectivity to download templates from GitHub.

**Why this priority**: This is the core requirement that enables offline development and faster feature initialization by eliminating network dependency.

**Independent Test**: Can be fully tested by disconnecting from the network, placing a template zip file in the current folder, and running the feature creation command. The system should successfully create the feature using the local template without attempting to download from GitHub.

**Acceptance Scenarios**:

1. **Given** a valid template zip file exists in the current folder, **When** the user initiates feature creation, **Then** the system uses the local zip file without attempting GitHub download
2. **Given** the user is offline and a local template zip exists, **When** the user creates a new feature, **Then** the feature is created successfully without network errors
3. **Given** multiple template zip files exist in the current folder, **When** the system infers template arguments from project context, **Then** the system uses the template zip file matching the pattern "spec-kit-template-{arg1}-{arg2}-v{version}.zip" (e.g., "spec-kit-template-claude-sh-v0.0.78.zip")
4. **Given** a template with arguments "claude" and "sh" exists and project context indicates these arguments, **When** feature creation is initiated, **Then** the system selects the correct template based on the inferred argument match
5. **Given** .specify configuration is missing or doesn't contain template arguments, **When** feature creation is initiated, **Then** the system presents an interactive prompt listing available templates and allows user selection

---

### User Story 2 - Fast Feature Initialization (Priority: P2)

A developer creating multiple features in rapid succession wants to avoid repeated GitHub downloads by reusing a cached local template, reducing feature setup time from seconds to milliseconds.

**Why this priority**: Improves developer productivity by eliminating network latency, though the feature still works with network downloads if local templates aren't available.

**Independent Test**: Can be tested by timing feature creation with and without local templates. With local template, initialization should complete in under 1 second vs. 3-10 seconds for GitHub download.

**Acceptance Scenarios**:

1. **Given** a local template zip exists, **When** the developer creates a new feature, **Then** feature initialization completes in under 1 second
2. **Given** the developer creates 5 features consecutively, **When** using local templates, **Then** all features initialize without redundant downloads
3. **Given** multiple template versions exist (e.g., v0.0.78 and v0.0.79 with same arguments), **When** the developer creates a feature, **Then** the system automatically selects the latest version

---

### User Story 3 - Multiple Template Types with Arguments (Priority: P3)

A developer maintaining projects with different tooling needs wants to store multiple template variants locally (e.g., "claude-sh" for bash scripts, "claude-py" for Python scripts) and select the appropriate one via arguments, enabling flexible template management for diverse projects.

**Why this priority**: Enables multi-tool workflows and template experimentation, though most users will use a single template type consistently.

**Independent Test**: Can be tested by placing multiple templates with different arguments (e.g., "spec-kit-template-claude-sh-v0.0.78.zip" and "spec-kit-template-claude-py-v0.0.78.zip") in the folder, then creating features with different argument combinations and verifying correct template selection.

**Acceptance Scenarios**:

1. **Given** templates with arguments "claude-sh" and "claude-py" exist locally, **When** the system infers arguments "claude" and "sh" from project context, **Then** the system selects the "claude-sh" template
2. **Given** multiple template types exist, **When** the system infers arguments that don't match any template, **Then** the system provides a clear error listing available template combinations
3. **Given** a specific template version exists locally, **When** creating features with matching arguments, **Then** all features use that exact template version consistently

---

### Edge Cases

- What happens when no local template zip file exists in the current folder? The system throws an error requiring the user to provide a local template file.
- What happens when no template matches the inferred arguments (e.g., system infers "claude" and "sh" but only "claude" and "py" exists)? The system throws an error with a list of available templates and their arguments to help the user identify the correct configuration.
- What happens when the local zip file is corrupted or has an invalid structure? The system validates that the zip can be extracted without errors and provides a clear error message if validation fails.
- What happens when multiple templates with the same arguments exist but different versions (e.g., "spec-kit-template-claude-sh-v0.0.78.zip" and "spec-kit-template-claude-sh-v0.0.79.zip")? The system should use the latest version based on semantic versioning.
- What happens when the current folder contains non-template zip files (e.g., "data-archive.zip")?
- How does the system handle nested directories - should it search recursively or only in the immediate current folder? The system searches only the immediate current folder.
- What happens when the .specify configuration or constitution file is missing or doesn't contain template argument information? The system prompts the user interactively to select from available templates in the current folder.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: System MUST check the current folder for a template zip file before attempting to download from GitHub
- **FR-002**: System MUST use the local template zip file when available in the current folder, skipping the GitHub download stage entirely
- **FR-003**: System MUST validate that the local zip file is a valid zip archive that can be extracted without errors before using it
- **FR-004**: System MUST extract and process the local template zip file in the same manner as a downloaded template
- **FR-005**: System MUST provide clear feedback to the user indicating that a local template is being used, including which template file and version
- **FR-006**: System MUST handle errors when the local zip file is corrupted, providing a clear error message
- **FR-007**: System MUST support template naming convention following the pattern "spec-kit-template-{arg1}-{arg2}-v{version}.zip" (e.g., "spec-kit-template-claude-sh-v0.0.78.zip") in the current folder
- **FR-008**: System MUST infer template arguments by reading the .specify configuration or constitution file to identify which template to use
- **FR-009**: System MUST match template files based on the inferred arguments, selecting only templates that match all inferred arguments
- **FR-010**: System MUST select the latest version when multiple templates with the same arguments exist, using semantic versioning comparison
- **FR-011**: System MUST provide a clear error message when no template matches the inferred arguments, listing all available templates in the current folder with their arguments to help users identify the correct configuration
- **FR-012**: System MUST ignore zip files that don't follow the "spec-kit-template-" naming prefix
- **FR-013**: System MUST prompt the user interactively to select from available templates when .specify configuration or constitution file is missing or doesn't contain template argument information

### Key Entities

- **Local Template Zip File**: A zip archive containing the template structure, stored in the current working directory, following the naming pattern "spec-kit-template-{arg1}-{arg2}-v{version}.zip", with expected internal structure matching GitHub template format
- **Template Arguments**: Context-inferred identifiers (e.g., "claude", "sh") automatically detected from .specify configuration or constitution file, used to select the appropriate template variant, allowing multiple template types to coexist
- **Template Version**: Semantic version number (e.g., "v0.0.78") embedded in the template filename, enabling version-based selection
- **Template Extraction Path**: The destination directory where the local template contents are extracted for feature initialization

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Users can create features successfully using only local template zip files without internet connectivity
- **SC-002**: Feature initialization completes in under 1 second when using local templates (vs. 3-10 seconds for GitHub download)
- **SC-003**: The system correctly identifies and uses local templates in 100% of cases when valid zip files with matching arguments are present
- **SC-004**: The system accurately selects the latest template version in 100% of cases when multiple versions with the same arguments exist
- **SC-005**: Error messages for corrupted, invalid, or non-matching templates are clear and actionable, allowing users to resolve issues within 1 minute
- **SC-006**: Users can successfully manage and switch between multiple template types (with different arguments) with 95% success rate
- **SC-007**: Documentation enables users to set up and use argument-based local templates correctly on first attempt with 90% success rate
