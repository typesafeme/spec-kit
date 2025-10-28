# Clean Architecture Analysis
# Spec Kit (specify-cli)

**Version:** 0.0.20
**Analysis Date:** 2025-10-28
**Analyzed By:** Claude Code

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Clean Architecture Overview](#clean-architecture-overview)
3. [Current Architecture Assessment](#current-architecture-assessment)
4. [Layer Breakdown](#layer-breakdown)
5. [Dependency Analysis](#dependency-analysis)
6. [Violations and Trade-offs](#violations-and-trade-offs)
7. [Recommendations](#recommendations)
8. [Refactoring Roadmap](#refactoring-roadmap)

---

## Executive Summary

### Overall Assessment

**Clean Architecture Compliance: 45/100**

Spec Kit currently exhibits a **pragmatic, monolithic CLI architecture** that prioritizes distribution simplicity and developer experience over strict architectural boundaries. While this violates several Clean Architecture principles, the design choices are **intentional and justified** for the project's goals.

### Key Findings

| Aspect | Status | Score | Notes |
|--------|--------|-------|-------|
| **Entities/Domain Layer** | ❌ Missing | 0/25 | No domain models or business entities |
| **Use Cases Layer** | ⚠️ Partial | 15/25 | Commands exist but mixed with infrastructure |
| **Interface Adapters** | ⚠️ Partial | 15/25 | UI and adapters not abstracted |
| **Frameworks & Drivers** | ✅ Present | 15/25 | External dependencies well-chosen |
| **Dependency Inversion** | ❌ Violated | 0/25 | Direct dependencies throughout |
| **Overall Testability** | ⚠️ Low | - | Tightly coupled to CLI framework |

### Strategic Recommendation

**Continue with pragmatic monolithic design** for CLI tool, but introduce **lightweight abstractions** for:
1. Template acquisition (local vs. GitHub)
2. Script execution (bash vs. PowerShell)
3. Progress tracking (console output)
4. Configuration management

These changes would improve testability and maintainability **without sacrificing** the single-file distribution model.

---

## Clean Architecture Overview

### The Four Layers

Clean Architecture organizes code into concentric circles with a strict dependency rule: **dependencies point inward**. Outer layers depend on inner layers, never the reverse.

```
┌────────────────────────────────────────────────────┐
│  Frameworks & Drivers (UI, DB, External APIs)     │ ← Outermost
├────────────────────────────────────────────────────┤
│  Interface Adapters (Controllers, Presenters)      │
├────────────────────────────────────────────────────┤
│  Use Cases (Application Business Rules)            │
├────────────────────────────────────────────────────┤
│  Entities (Enterprise Business Rules)              │ ← Innermost
└────────────────────────────────────────────────────┘
```

### Dependency Rule

> Source code dependencies must point only inward, toward higher-level policies.

### Benefits of Clean Architecture

1. **Independent of Frameworks**: Business logic doesn't depend on external libraries
2. **Testable**: Business rules testable without UI, database, or external services
3. **Independent of UI**: UI can change without affecting business logic
4. **Independent of Database**: Can swap data sources without affecting business logic
5. **Independent of External Services**: Business logic isolated from external APIs

---

## Current Architecture Assessment

### File Structure

**Primary Implementation**: `src/specify_cli/__init__.py` (1,520 lines)
- Single monolithic file containing all CLI logic
- Direct imports of external frameworks (Typer, Rich, httpx)
- Business logic intertwined with presentation and infrastructure

**Supporting Files**:
- `scripts/bash/*.sh` - Workflow automation (separate process execution)
- `scripts/powershell/*.ps1` - Windows equivalent
- `templates/*.md` - Template files (data, not code)

### Architecture Diagram (Current State)

```
┌─────────────────────────────────────────────────────────────────┐
│                         __init__.py                             │
│  ┌────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Typer CLI  │  │ Rich UI      │  │ httpx HTTP Client       │ │
│  │ Commands   │  │ Components   │  │ GitHub API              │ │
│  └────┬───────┘  └──────┬───────┘  └────────┬───────────────┘ │
│       │                 │                    │                  │
│       └─────────────────┴────────────────────┘                  │
│                         │                                        │
│                         ↓                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Mixed Business Logic + Infrastructure                   │   │
│  │  - Project initialization                                │   │
│  │  - Template download/extraction                          │   │
│  │  - Git operations                                        │   │
│  │  - Agent configuration                                   │   │
│  │  - Progress tracking                                     │   │
│  │  - File system operations                                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ↓
                    ┌────────────────────────┐
                    │  External Scripts       │
                    │  (.sh, .ps1)            │
                    │  - Feature creation     │
                    │  - Prerequisite checks  │
                    └────────────────────────┘
```

### Design Philosophy

From CLAUDE.md lines 540-550:
> "Single-file CLI design: keep `__init__.py` monolithic for easy distribution"

This is an **explicit architectural decision** trading Clean Architecture principles for:
- **Ease of Distribution**: Single file can be run with `uvx` or distributed as wheel
- **Developer Experience**: No need to navigate complex module hierarchies
- **Reduced Cognitive Load**: All code in one place for contributors
- **Simplified Packaging**: Fewer build complexities

---

## Layer Breakdown

### Layer 1: Entities (Domain Layer) - MISSING ❌

**Expected**: Core business entities representing fundamental business concepts.

**Current State**: No domain entities exist. The project operates directly on:
- File paths (strings)
- Configuration dictionaries (`AGENT_CONFIG`)
- JSON objects (parsed from scripts)
- Template files (external)

**Missing Domain Concepts**:

1. **Project**: Represents a Spec Kit project
   ```python
   # Should exist but doesn't:
   @dataclass
   class Project:
       root_path: Path
       has_git: bool
       current_feature: Optional[str]
       constitution: Optional[Constitution]
       specs: List[Specification]
   ```

2. **Specification**: Represents a feature specification
   ```python
   # Should exist but doesn't:
   @dataclass
   class Specification:
       number: int
       short_name: str
       description: str
       user_stories: List[UserStory]
       requirements: List[Requirement]
       status: SpecStatus
   ```

3. **Agent**: Represents an AI coding agent
   ```python
   # Should exist but doesn't:
   @dataclass
   class Agent:
       key: str
       name: str
       folder: Path
       requires_cli: bool
       install_url: Optional[str]
   ```

4. **Template**: Represents a template file
   ```python
   # Should exist but doesn't:
   @dataclass
   class Template:
       path: Path
       version: str
       agent: str
       script_type: str
       source: TemplateSource  # Local or GitHub
   ```

**Impact**:
- Business logic scattered throughout CLI commands
- Difficult to test domain concepts in isolation
- No single source of truth for business rules

**Severity**: **Medium** (acceptable for CLI tool, but limits testability)

---

### Layer 2: Use Cases (Application Layer) - PARTIAL ⚠️

**Expected**: Application-specific business rules independent of UI or infrastructure.

**Current State**: Use cases exist as Typer commands but are tightly coupled to infrastructure.

#### Existing Use Cases

**UC-1: Initialize Project** (`init` command, lines 1161-1462)
- **Location**: `src/specify_cli/__init__.py:init()`
- **Coupling**: HIGH - Directly uses Typer, Rich, httpx, git, filesystem
- **Status**: ⚠️ Exists but violates dependency inversion

**Code Structure**:
```python
@app.command()  # ← Framework coupling
def init(
    project_name: str = typer.Argument(...),  # ← Framework coupling
    ai_assistant: str = typer.Option(...),     # ← Framework coupling
    # ... more framework-coupled parameters
):
    # UI logic mixed with business logic
    show_banner()  # ← Presentation
    console.print(...)  # ← Presentation

    # Business logic mixed with infrastructure
    if not here and not project_name:
        console.print("[red]Error:[/red] ...")  # ← Presentation
        raise typer.Exit(1)  # ← Framework coupling

    # Direct HTTP calls
    download_and_extract_template(...)  # ← Infrastructure

    # Direct git operations
    init_git_repo(project_path)  # ← Infrastructure
```

**Should Be** (Clean Architecture):
```python
# Domain/Use Case Layer (no framework dependencies)
class InitializeProjectUseCase:
    def __init__(
        self,
        template_repository: TemplateRepository,  # ← Interface
        project_repository: ProjectRepository,    # ← Interface
        presenter: InitProjectPresenter,          # ← Interface
    ):
        self.template_repo = template_repository
        self.project_repo = project_repository
        self.presenter = presenter

    def execute(self, request: InitProjectRequest) -> None:
        # Pure business logic
        if not request.project_name and not request.use_current_dir:
            self.presenter.show_error("Must specify project name or use --here")
            return

        template = self.template_repo.get_latest(request.agent, request.script_type)
        project = self.project_repo.create(request.project_name, template)

        if request.initialize_git:
            project.initialize_git()

        self.presenter.show_success(project)

# Adapter Layer (framework-specific)
@app.command()
def init(project_name: str = typer.Argument(...)):
    # Thin adapter delegates to use case
    use_case = InitializeProjectUseCase(
        template_repository=GitHubTemplateRepository(),
        project_repository=FileSystemProjectRepository(),
        presenter=RichConsolePresenter(),
    )

    request = InitProjectRequest(project_name=project_name, ...)
    use_case.execute(request)
```

**UC-2: Check Tools** (`check` command, lines 1474-1514)
- **Location**: `src/specify_cli/__init__.py:check()`
- **Coupling**: HIGH - Direct tool checking, no abstraction
- **Status**: ⚠️ Exists but could benefit from abstraction

**UC-3: Template Acquisition** (lines 872-1113)
- **Location**: `download_and_extract_template()` function
- **Coupling**: VERY HIGH - Mixed template discovery, HTTP, ZIP, filesystem
- **Status**: ⚠️ Critical use case but monolithic implementation

**UC-4: Script Execution** (lines 390-406)
- **Location**: `run_command()` function
- **Coupling**: MEDIUM - Direct subprocess calls
- **Status**: ⚠️ Could be abstracted for testing

#### Missing Use Case Abstractions

1. **Template Acquisition Strategy** (local vs. GitHub)
   - Currently: Complex if/else logic in `download_and_extract_template()`
   - Should: Strategy pattern with `LocalTemplateSource` vs. `GitHubTemplateSource`

2. **Project Structure Validation**
   - Currently: Scattered checks in various functions
   - Should: Dedicated use case for validation

3. **Agent Configuration Management**
   - Currently: Global dictionary `AGENT_CONFIG`
   - Should: Use case for querying/managing agents

---

### Layer 3: Interface Adapters - PARTIAL ⚠️

**Expected**: Adapters that convert data between use cases and external interfaces (UI, DB, APIs).

**Current State**: Adapters exist but are not properly abstracted.

#### Existing Adapters (Not Abstracted)

**Adapter 1: Rich Console UI** (throughout `__init__.py`)
- **Purpose**: Present information to user via terminal
- **Coupling**: Direct Rich API calls scattered throughout
- **Examples**:
  - `console.print()` - Direct presentation calls (100+ occurrences)
  - `Panel()` - Direct UI component usage
  - `Progress()` - Direct progress bar usage
  - `StepTracker` class (lines 169-252) - Mixed presenter and view logic

**Should Be**:
```python
# Interface (Use Case Layer)
class ProjectPresenter(ABC):
    @abstractmethod
    def show_banner(self) -> None: ...

    @abstractmethod
    def show_error(self, message: str) -> None: ...

    @abstractmethod
    def show_success(self, project: Project) -> None: ...

    @abstractmethod
    def show_progress(self, step: str, status: StepStatus) -> None: ...

# Implementation (Adapter Layer)
class RichConsolePresenter(ProjectPresenter):
    def __init__(self):
        self.console = Console()
        self.tracker = StepTracker()

    def show_banner(self) -> None:
        # Rich-specific implementation
        self.console.print(...)

    def show_error(self, message: str) -> None:
        self.console.print(f"[red]Error:[/red] {message}")
```

**Adapter 2: GitHub API Client** (lines 762-870)
- **Purpose**: Fetch templates from GitHub releases
- **Coupling**: Direct httpx calls in `download_template_from_github()`
- **Issues**: No interface, hard to mock for testing

**Should Be**:
```python
# Interface (Use Case Layer)
class TemplateRepository(ABC):
    @abstractmethod
    def get_latest(self, agent: str, script_type: str) -> Template: ...

    @abstractmethod
    def list_versions(self, agent: str, script_type: str) -> List[str]: ...

# Implementations (Adapter Layer)
class GitHubTemplateRepository(TemplateRepository):
    def __init__(self, client: httpx.Client):
        self.client = client

    def get_latest(self, agent: str, script_type: str) -> Template:
        # GitHub API implementation
        ...

class LocalTemplateRepository(TemplateRepository):
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir

    def get_latest(self, agent: str, script_type: str) -> Template:
        # Local filesystem implementation
        ...
```

**Adapter 3: Git Integration** (lines 439-492)
- **Purpose**: Initialize git repositories, create branches
- **Coupling**: Direct subprocess git calls
- **Issues**: No abstraction, difficult to test without actual git

**Should Be**:
```python
# Interface (Use Case Layer)
class VersionControlSystem(ABC):
    @abstractmethod
    def is_repository(self, path: Path) -> bool: ...

    @abstractmethod
    def initialize(self, path: Path) -> None: ...

    @abstractmethod
    def create_branch(self, name: str) -> None: ...

    @abstractmethod
    def commit(self, message: str) -> None: ...

# Implementations (Adapter Layer)
class GitVersionControl(VersionControlSystem):
    def is_repository(self, path: Path) -> bool:
        result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], ...)
        return result.returncode == 0

    # ... other git-specific implementations

class NoVersionControl(VersionControlSystem):
    # Null object pattern for --no-git scenarios
    def is_repository(self, path: Path) -> bool:
        return False

    def initialize(self, path: Path) -> None:
        pass  # No-op
```

**Adapter 4: File System Operations** (throughout)
- **Purpose**: Read/write files, extract zips, manage directories
- **Coupling**: Direct Path and shutil operations
- **Issues**: Hard to test without real filesystem

---

### Layer 4: Frameworks & Drivers - PRESENT ✅

**Expected**: External tools, libraries, and frameworks. Outermost layer.

**Current State**: Well-chosen dependencies with appropriate functionality.

#### Framework Dependencies

| Framework | Purpose | Usage | Assessment |
|-----------|---------|-------|-----------|
| **Typer** | CLI framework | Command parsing, argument handling | ✅ Appropriate choice |
| **Rich** | Terminal UI | Colors, panels, progress bars, trees | ✅ Excellent UX |
| **httpx** | HTTP client | GitHub API, template downloads | ✅ Modern, async-capable |
| **truststore** | SSL/TLS | Certificate validation | ✅ Security best practice |
| **readchar** | Keyboard input | Arrow key navigation | ✅ Cross-platform |
| **platformdirs** | Directory paths | Platform-specific paths (currently unused) | ⚠️ Imported but not used |

#### External Services

1. **GitHub API**
   - Endpoint: `https://api.github.com/repos/github/spec-kit/releases/latest`
   - Purpose: Fetch latest release metadata and templates
   - Coupling: Direct in `download_template_from_github()` (lines 762-870)

2. **Git CLI**
   - Commands: `git init`, `git add`, `git commit`, `git checkout`, `git branch`, `git ls-remote`
   - Purpose: Repository management, branch operations
   - Coupling: Direct subprocess calls via `run_command()` (lines 390-406)

3. **File System**
   - Operations: Read, write, extract ZIP, set permissions
   - Purpose: Project structure management, template processing
   - Coupling: Direct Path and shutil operations throughout

---

## Dependency Analysis

### Dependency Flow Diagram

```
┌─────────────────────────────────────────────────┐
│           CLI Entry Point (Typer)               │
│                  app.command()                  │
└────────────────────┬────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────┐
│         Command Handlers (Use Cases)            │
│  init(), check(), download_and_extract_...()    │
└────────────┬───────────────────┬────────────────┘
             │                   │
             ↓                   ↓
┌──────────────────────┐  ┌────────────────────────┐
│  UI Layer (Rich)     │  │ Infrastructure         │
│  - Console           │  │  - httpx (GitHub API)  │
│  - Panel             │  │  - subprocess (git)    │
│  - Progress          │  │  - Path (filesystem)   │
│  - StepTracker       │  │  - zipfile             │
└──────────────────────┘  └────────────────────────┘
```

**Issue**: All dependencies point **outward** from business logic to frameworks/infrastructure. This violates the Dependency Inversion Principle.

**Should Be** (Clean Architecture):

```
┌─────────────────────────────────────────────────┐
│           CLI Entry Point (Typer)               │ ← Adapter Layer
└────────────────────┬────────────────────────────┘
                     │ implements
                     ↓
┌─────────────────────────────────────────────────┐
│         Use Case Interfaces (Ports)             │ ← Use Case Layer
│  ProjectPresenter, TemplateRepository, etc.     │
└────────────────────┬────────────────────────────┘
                     │ uses
                     ↓
┌─────────────────────────────────────────────────┐
│         Business Logic (Use Cases)              │ ← Use Case Layer
│  InitializeProject, CheckTools, etc.            │
└────────────────────┬────────────────────────────┘
                     │ uses
                     ↓
┌─────────────────────────────────────────────────┐
│         Domain Entities                         │ ← Entity Layer
│  Project, Template, Agent, Specification        │
└─────────────────────────────────────────────────┘

┌──────────────────────┐  ┌────────────────────────┐
│  Rich Adapter        │  │ GitHub Adapter         │ ← Adapter Layer
│  (implements         │  │ (implements            │   (implements
│   ProjectPresenter)  │  │  TemplateRepository)   │    interfaces)
└──────────────────────┘  └────────────────────────┘
```

### Current Dependency Violations

#### Violation 1: Direct Framework Dependencies in Business Logic

**Location**: Throughout `init()` command (lines 1161-1462)

```python
# VIOLATION: Business logic depends on Rich framework
if offline:
    console.print(f"[cyan]Offline mode enabled[/cyan] ...")  # ← Direct coupling

# VIOLATION: Business logic depends on Typer framework
if not here and not project_name:
    console.print("[red]Error:[/red] ...")
    raise typer.Exit(1)  # ← Framework exception
```

**Impact**: Cannot test business logic without Rich and Typer installed.

#### Violation 2: No Abstraction for Template Acquisition

**Location**: `download_and_extract_template()` (lines 872-1113)

```python
# VIOLATION: Use case directly implements infrastructure
def download_and_extract_template(...):
    # Direct filesystem access
    templates_dir = get_installation_templates_dir()

    # Direct GitHub API call
    zip_path, meta = download_template_from_github(...)

    # Direct ZIP extraction
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(project_path)
```

**Should Have**: `TemplateRepository` interface with `LocalTemplateSource` and `GitHubTemplateSource` implementations.

#### Violation 3: Global Configuration State

**Location**: `AGENT_CONFIG` dictionary (lines 67-153)

```python
# VIOLATION: Global mutable state
AGENT_CONFIG = {
    "copilot": {
        "name": "GitHub Copilot",
        "folder": ".github/",
        # ...
    },
    # ... more agents
}
```

**Issues**:
- Cannot have multiple configurations simultaneously (testing scenarios)
- No type safety (dictionary keys/values are strings)
- No validation of configuration structure

**Should Be**: `AgentRegistry` class with type-safe agent configuration.

#### Violation 4: Hard-Coded Claude CLI Special Case

**Location**: `check_tool()` function (lines 408-437)

```python
# VIOLATION: Business logic contains infrastructure details
if tool == "claude":
    if CLAUDE_LOCAL_PATH.exists() and CLAUDE_LOCAL_PATH.is_file():
        if tracker:
            tracker.complete(tool, "available")
        return True

found = shutil.which(tool) is not None
```

**Issue**: Use case knows about specific tool's installation quirks.

**Should Have**: `ToolDetector` interface with agent-specific implementations.

---

## Violations and Trade-offs

### Major Violations

#### V-1: No Domain Layer

**Violation**: No domain entities, everything operates on primitives and dictionaries.

**Clean Architecture Principle**: "Entities encapsulate Enterprise-wide business rules"

**Trade-off Justification**:
- **Benefit**: Simpler code, fewer abstractions, faster development
- **Cost**: Business logic scattered, difficult to test domain concepts, no type safety
- **Verdict**: **Acceptable for CLI tool**, but introduces risk as complexity grows

**Mitigation**: Introduce lightweight domain models (dataclasses) without full DDD overhead.

#### V-2: Direct Framework Coupling

**Violation**: Business logic directly calls Rich, Typer, httpx throughout.

**Clean Architecture Principle**: "Source code dependencies point only inward"

**Trade-off Justification**:
- **Benefit**: Straightforward code, no indirection, easier for new contributors
- **Cost**: Cannot test business logic without frameworks, hard to change UI/HTTP library
- **Verdict**: **Problematic** - reduces testability significantly

**Mitigation**: Extract interfaces for UI (presenter) and external services (repositories).

#### V-3: Monolithic Function Design

**Violation**: Large functions mixing business logic, UI, and infrastructure (e.g., `download_and_extract_template()` at 241 lines).

**Clean Architecture Principle**: "Separate concerns into layers"

**Trade-off Justification**:
- **Benefit**: All related code in one place, easier to understand flow
- **Cost**: Difficult to test individual steps, hard to reuse logic, violates SRP
- **Verdict**: **Problematic** - maintainability suffers at this scale

**Mitigation**: Refactor into smaller, composable functions or use case methods.

#### V-4: Global State

**Violation**: Global `AGENT_CONFIG`, `CLAUDE_LOCAL_PATH`, `console` objects.

**Clean Architecture Principle**: "Avoid global state that prevents testing"

**Trade-off Justification**:
- **Benefit**: Easy access throughout code, no dependency injection needed
- **Cost**: Difficult to test with different configurations, potential race conditions
- **Verdict**: **Acceptable for CLI tool**, but limits advanced usage patterns

**Mitigation**: Encapsulate in configuration object, inject where needed.

### Minor Violations

#### V-5: No Repository Pattern

**Violation**: Direct filesystem and HTTP operations, no abstraction.

**Impact**: Low (but would improve testability)

#### V-6: Mixed Presentation and Business Logic

**Violation**: `console.print()` calls interspersed with business logic.

**Impact**: Medium (hard to test logic without UI)

#### V-7: No Dependency Injection

**Violation**: Dependencies created within functions, not injected.

**Impact**: Medium (prevents mocking for tests)

---

## Recommendations

### Priority 1: High-Value, Low-Effort Improvements

#### R-1: Introduce Domain Models (Effort: Low, Value: High)

**Goal**: Add type-safe domain models using dataclasses without restructuring code.

**Implementation**:

```python
# Add to __init__.py (or separate models.py within same file)
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

@dataclass
class AgentConfig:
    """Domain model for AI agent configuration"""
    key: str
    name: str
    folder: str
    install_url: Optional[str]
    requires_cli: bool

    @staticmethod
    def from_dict(key: str, data: dict) -> 'AgentConfig':
        return AgentConfig(
            key=key,
            name=data['name'],
            folder=data['folder'],
            install_url=data.get('install_url'),
            requires_cli=data['requires_cli']
        )

@dataclass
class Template:
    """Domain model for template file"""
    path: Path
    agent: str
    script_type: str
    version: str
    source: str  # 'local' or 'github'
    size: int

@dataclass
class ProjectConfig:
    """Domain model for project configuration"""
    name: str
    path: Path
    agent: AgentConfig
    script_type: str
    has_git: bool
    is_current_dir: bool

# Replace AGENT_CONFIG dictionary usage
class AgentRegistry:
    """Registry for managing agent configurations"""
    def __init__(self, config_dict: dict):
        self._agents = {
            key: AgentConfig.from_dict(key, data)
            for key, data in config_dict.items()
        }

    def get(self, key: str) -> Optional[AgentConfig]:
        return self._agents.get(key)

    def list_all(self) -> List[AgentConfig]:
        return list(self._agents.values())

    def keys(self) -> List[str]:
        return list(self._agents.keys())

# Usage:
agent_registry = AgentRegistry(AGENT_CONFIG)
```

**Benefits**:
- Type safety (IDE autocomplete, type checking)
- Self-documenting code
- Easier to test
- No architectural restructuring required

**Estimated Effort**: 4-6 hours

---

#### R-2: Extract Template Repository Interface (Effort: Medium, Value: High)

**Goal**: Abstract template acquisition behind interface for testability.

**Implementation**:

```python
from abc import ABC, abstractmethod

# Interface (can live in __init__.py)
class TemplateRepository(ABC):
    """Interface for acquiring project templates"""

    @abstractmethod
    def get_latest_template(
        self,
        agent: str,
        script_type: str,
        verbose: bool = False
    ) -> Optional[Template]:
        """Get latest template matching criteria"""
        pass

    @abstractmethod
    def list_available_templates(
        self,
        agent: str,
        script_type: str
    ) -> List[Template]:
        """List all available templates matching criteria"""
        pass


# Implementation 1: Local filesystem
class LocalTemplateRepository(TemplateRepository):
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir

    def get_latest_template(self, agent: str, script_type: str, verbose: bool = False) -> Optional[Template]:
        # Extract from find_local_template() function
        templates = self.list_available_templates(agent, script_type)
        return templates[0] if templates else None

    def list_available_templates(self, agent: str, script_type: str) -> List[Template]:
        # Extract from find_all_local_templates() function
        ...


# Implementation 2: GitHub API
class GitHubTemplateRepository(TemplateRepository):
    def __init__(self, client: httpx.Client, owner: str, repo: str):
        self.client = client
        self.owner = owner
        self.repo = repo

    def get_latest_template(self, agent: str, script_type: str, verbose: bool = False) -> Optional[Template]:
        # Extract from download_template_from_github() function
        ...


# Composite for fallback behavior
class CompositeTemplateRepository(TemplateRepository):
    """Try local first, fallback to GitHub"""
    def __init__(
        self,
        local: LocalTemplateRepository,
        remote: GitHubTemplateRepository,
        offline: bool = False
    ):
        self.local = local
        self.remote = remote
        self.offline = offline

    def get_latest_template(self, agent: str, script_type: str, verbose: bool = False) -> Optional[Template]:
        # Try local first
        template = self.local.get_latest_template(agent, script_type, verbose)
        if template:
            return template

        # Fallback to remote if not offline
        if not self.offline:
            return self.remote.get_latest_template(agent, script_type, verbose)

        return None


# Usage in init() command:
def init(...):
    # Create repository
    local_repo = LocalTemplateRepository(get_installation_templates_dir())
    remote_repo = GitHubTemplateRepository(client, "github", "spec-kit")
    template_repo = CompositeTemplateRepository(local_repo, remote_repo, offline=offline)

    # Get template
    template = template_repo.get_latest_template(selected_ai, selected_script, verbose=True)
    if not template:
        console.print("[red]Error: No template found[/red]")
        raise typer.Exit(1)
```

**Benefits**:
- Easy to mock for testing (`MockTemplateRepository`)
- Can add new sources (S3, Azure Blob, etc.) without changing init logic
- Cleaner separation of concerns
- Testable without network access

**Estimated Effort**: 8-12 hours

---

#### R-3: Extract Presenter Interface (Effort: Medium, Value: Medium)

**Goal**: Abstract Rich console output behind interface for testability and flexibility.

**Implementation**:

```python
from abc import ABC, abstractmethod

# Interface
class ProjectPresenter(ABC):
    """Interface for presenting project initialization progress"""

    @abstractmethod
    def show_banner(self) -> None:
        pass

    @abstractmethod
    def show_error(self, message: str, title: str = "Error") -> None:
        pass

    @abstractmethod
    def show_warning(self, message: str) -> None:
        pass

    @abstractmethod
    def show_info(self, message: str) -> None:
        pass

    @abstractmethod
    def show_panel(self, content: str, title: str, style: str = "cyan") -> None:
        pass

    @abstractmethod
    def create_step_tracker(self, title: str) -> StepTracker:
        pass

    @abstractmethod
    def show_selection_menu(
        self,
        options: dict,
        prompt: str,
        default: Optional[str] = None
    ) -> str:
        pass


# Implementation
class RichConsolePresenter(ProjectPresenter):
    def __init__(self):
        self.console = Console()

    def show_banner(self) -> None:
        banner_lines = BANNER.strip().split('\n')
        colors = ["bright_blue", "blue", "cyan", "bright_cyan", "white", "bright_white"]
        styled_banner = Text()
        for i, line in enumerate(banner_lines):
            color = colors[i % len(colors)]
            styled_banner.append(line + "\n", style=color)
        self.console.print(Align.center(styled_banner))
        self.console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
        self.console.print()

    def show_error(self, message: str, title: str = "Error") -> None:
        panel = Panel(message, title=f"[red]{title}[/red]", border_style="red", padding=(1, 2))
        self.console.print(panel)

    # ... other methods


# Mock implementation for testing
class MockPresenter(ProjectPresenter):
    def __init__(self):
        self.shown_errors = []
        self.shown_info = []
        self.shown_warnings = []

    def show_error(self, message: str, title: str = "Error") -> None:
        self.shown_errors.append((message, title))

    # ... other methods


# Usage in commands:
def init(...):
    presenter = RichConsolePresenter()
    presenter.show_banner()

    if not here and not project_name:
        presenter.show_error("Must specify project name or use --here flag")
        raise typer.Exit(1)
```

**Benefits**:
- Easy to test with `MockPresenter`
- Could support alternative outputs (JSON, plain text, GUI)
- Separates presentation from business logic
- Could generate reports/logs without Rich

**Estimated Effort**: 8-12 hours

---

### Priority 2: Medium-Value Improvements

#### R-4: Introduce Use Case Classes (Effort: High, Value: Medium)

**Goal**: Extract command logic into use case classes.

**Example**:

```python
class InitializeProjectUseCase:
    """Use case for initializing a new Spec Kit project"""

    def __init__(
        self,
        template_repository: TemplateRepository,
        presenter: ProjectPresenter,
        vcs: VersionControlSystem,
        agent_registry: AgentRegistry,
    ):
        self.template_repo = template_repository
        self.presenter = presenter
        self.vcs = vcs
        self.agent_registry = agent_registry

    def execute(self, request: InitProjectRequest) -> None:
        # Validate inputs
        if not request.project_name and not request.use_current_dir:
            self.presenter.show_error("Must specify project name or use --here")
            return

        # Resolve project configuration
        project_config = self._resolve_project_config(request)

        # Acquire template
        template = self.template_repo.get_latest_template(
            project_config.agent.key,
            project_config.script_type
        )
        if not template:
            self.presenter.show_error("No template found")
            return

        # Extract template
        self._extract_template(template, project_config)

        # Initialize version control if requested
        if request.initialize_git and not self.vcs.is_repository(project_config.path):
            self.vcs.initialize(project_config.path)

        # Show success
        self.presenter.show_success(project_config)

    # ... private helper methods


# Adapter (thin wrapper)
@app.command()
def init(
    project_name: str = typer.Argument(None),
    ai_assistant: str = typer.Option(None, "--ai"),
    # ... other options
):
    # Construct dependencies
    presenter = RichConsolePresenter()
    template_repo = CompositeTemplateRepository(...)
    vcs = GitVersionControl() if not no_git else NoVersionControl()
    agent_registry = AgentRegistry(AGENT_CONFIG)

    # Execute use case
    use_case = InitializeProjectUseCase(
        template_repository=template_repo,
        presenter=presenter,
        vcs=vcs,
        agent_registry=agent_registry,
    )

    request = InitProjectRequest(
        project_name=project_name,
        agent_key=ai_assistant,
        script_type=script_type,
        use_current_dir=here,
        initialize_git=not no_git,
        force_merge=force,
        offline=offline,
    )

    use_case.execute(request)
```

**Benefits**:
- Testable business logic (no Typer/Rich dependencies)
- Clear separation of concerns
- Easier to reason about and maintain
- Reusable in different contexts (API, GUI, tests)

**Challenges**:
- Significant refactoring required
- More indirection (may reduce readability for simple CLI)
- Need to manage dependency injection

**Estimated Effort**: 20-30 hours

---

#### R-5: Add Integration Tests with Mocks (Effort: Medium, Value: High)

**Goal**: Test commands end-to-end using mocked dependencies.

**Example**:

```python
# tests/test_init_command.py
import pytest
from unittest.mock import Mock
from specify_cli import InitializeProjectUseCase, InitProjectRequest

def test_init_project_success():
    # Arrange
    mock_template_repo = Mock(spec=TemplateRepository)
    mock_presenter = Mock(spec=ProjectPresenter)
    mock_vcs = Mock(spec=VersionControlSystem)
    mock_agent_registry = Mock(spec=AgentRegistry)

    mock_template_repo.get_latest_template.return_value = Template(
        path=Path("/tmp/template.zip"),
        agent="claude",
        script_type="sh",
        version="1.0.0",
        source="local",
        size=1024,
    )

    use_case = InitializeProjectUseCase(
        template_repository=mock_template_repo,
        presenter=mock_presenter,
        vcs=mock_vcs,
        agent_registry=mock_agent_registry,
    )

    request = InitProjectRequest(
        project_name="test-project",
        agent_key="claude",
        script_type="sh",
        use_current_dir=False,
        initialize_git=True,
        force_merge=False,
        offline=False,
    )

    # Act
    use_case.execute(request)

    # Assert
    mock_template_repo.get_latest_template.assert_called_once_with("claude", "sh")
    mock_vcs.initialize.assert_called_once()
    mock_presenter.show_success.assert_called_once()
    assert len(mock_presenter.show_error.call_args_list) == 0


def test_init_project_no_template_found():
    # Arrange
    mock_template_repo = Mock(spec=TemplateRepository)
    mock_presenter = Mock(spec=ProjectPresenter)

    mock_template_repo.get_latest_template.return_value = None

    use_case = InitializeProjectUseCase(
        template_repository=mock_template_repo,
        presenter=mock_presenter,
        vcs=Mock(),
        agent_registry=Mock(),
    )

    request = InitProjectRequest(...)

    # Act
    use_case.execute(request)

    # Assert
    mock_presenter.show_error.assert_called_once_with("No template found")
```

**Estimated Effort**: 12-16 hours (depends on refactoring progress)

---

### Priority 3: Future Architectural Improvements

#### R-6: Migrate to Multi-Module Architecture (Effort: Very High, Value: Low)

**Note**: This recommendation is **NOT advised** given the project's explicit goal of single-file distribution.

**If pursued**, structure would be:

```
src/specify_cli/
├── __init__.py              # Entry point, thin adapter
├── domain/
│   ├── entities.py          # Project, Template, Agent, Spec
│   └── value_objects.py     # Version, FeatureNumber
├── use_cases/
│   ├── init_project.py      # InitializeProjectUseCase
│   ├── check_tools.py       # CheckToolsUseCase
│   └── interfaces.py        # TemplateRepository, ProjectPresenter, etc.
├── adapters/
│   ├── cli.py               # Typer commands (thin wrappers)
│   ├── presenters.py        # RichConsolePresenter
│   ├── repositories.py      # LocalTemplateRepository, GitHubTemplateRepository
│   └── vcs.py               # GitVersionControl
└── infrastructure/
    ├── http_client.py       # httpx wrapper
    ├── filesystem.py        # Path operations
    └── config.py            # AgentRegistry, configuration management
```

**Trade-off**: **Loses single-file distribution benefit** - not recommended unless distributing as full package becomes the norm.

---

## Refactoring Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goal**: Introduce domain models and basic abstractions without breaking changes.

#### Week 1: Domain Models
- [ ] Add `AgentConfig` dataclass
- [ ] Add `Template` dataclass
- [ ] Add `ProjectConfig` dataclass
- [ ] Add `AgentRegistry` class
- [ ] Update code to use models instead of dictionaries
- [ ] Add type hints throughout

#### Week 2: Basic Interfaces
- [ ] Extract `TemplateRepository` interface
- [ ] Implement `LocalTemplateRepository`
- [ ] Implement `GitHubTemplateRepository`
- [ ] Implement `CompositeTemplateRepository`
- [ ] Update `download_and_extract_template()` to use repositories

**Deliverables**:
- Type-safe domain models
- Template acquisition abstracted
- Existing functionality unchanged

---

### Phase 2: Testing Infrastructure (Weeks 3-4)

**Goal**: Make code testable without changing external behavior.

#### Week 3: Presenter Interface
- [ ] Extract `ProjectPresenter` interface
- [ ] Implement `RichConsolePresenter`
- [ ] Implement `MockPresenter` for testing
- [ ] Update `init()` command to use presenter

#### Week 4: Test Suite
- [ ] Write unit tests for domain models
- [ ] Write integration tests for template acquisition
- [ ] Write tests for script execution
- [ ] Set up CI/CD for test automation

**Deliverables**:
- Testable presentation layer
- Comprehensive test suite
- CI/CD pipeline

---

### Phase 3: Use Case Extraction (Weeks 5-7) - Optional

**Goal**: Extract business logic into use case classes (only if needed for complexity management).

#### Week 5: Init Use Case
- [ ] Extract `InitializeProjectUseCase`
- [ ] Extract `InitProjectRequest` / `InitProjectResponse`
- [ ] Update `init()` command to delegate to use case
- [ ] Write tests for use case

#### Week 6: Other Use Cases
- [ ] Extract `CheckToolsUseCase`
- [ ] Extract `DownloadTemplateUseCase`
- [ ] Extract `ExtractTemplateUseCase`
- [ ] Write tests for all use cases

#### Week 7: Polish & Documentation
- [ ] Update CLAUDE.md with new architecture
- [ ] Update README with testing instructions
- [ ] Add architecture diagrams
- [ ] Document extension points

**Deliverables**:
- Clean separation of concerns
- Fully testable business logic
- Maintainable architecture

---

### Phase 4: Advanced Improvements (Future)

**Goal**: Address remaining architectural concerns (only if complexity demands it).

- [ ] Extract `VersionControlSystem` interface
- [ ] Implement `GitVersionControl` and `NoVersionControl`
- [ ] Extract `FileSystem` interface for testing
- [ ] Implement plugin system for custom agents
- [ ] Add telemetry infrastructure (opt-in)

---

## Summary

### Current State

Spec Kit exhibits a **pragmatic, monolithic architecture** optimized for:
- Single-file distribution
- Developer experience
- Simplicity for contributors
- Rapid development

This design **intentionally sacrifices** Clean Architecture principles for practical benefits, which is **acceptable for a CLI tool** of this scale.

### Recommended Path Forward

**Short Term (Next Release)**:
1. ✅ Introduce domain models (dataclasses) - **High value, low effort**
2. ✅ Extract TemplateRepository interface - **Enables testing, future flexibility**
3. ✅ Extract ProjectPresenter interface - **Improves testability**

**Medium Term (Next 3-6 Months)**:
4. ⚠️ Add comprehensive test suite - **Requires interfaces above**
5. ⚠️ Consider use case extraction **only if** complexity becomes unmanageable

**Long Term**:
6. ❌ **Do NOT** migrate to multi-module architecture - **Violates distribution goals**
7. ✅ Maintain single-file design but with better internal structure

### Key Principle

> "Perfect is the enemy of good. Clean Architecture is a tool, not a religion. Apply principles where they provide clear value, and pragmatically violate them when constraints demand it."

Spec Kit's current architecture is **fit for purpose**. Recommended improvements target **testability and maintainability** without sacrificing the project's core design goals.

---

**Document Version:** 1.0
**Last Updated:** 2025-10-28
**Next Review:** After Phase 1 completion (domain models + basic interfaces)
