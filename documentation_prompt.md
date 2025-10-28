# Python Project Documentation Generator

I have an existing Python project that I need to document. Please analyze the codebase and create the following documents:

## Project Context
- **Project Name**: [PROJECT_NAME]
- **Primary Purpose**: [BRIEF_DESCRIPTION]
- **Technology Stack**: Python [VERSION], [LIST_KEY_DEPENDENCIES]

## Files to Analyze
[Upload your Python files or paste directory structure]

---

## Required Documents

### 1. Product Requirements Document (PRD)

Please create a PRD with:

**Executive Summary**
- Product vision and objectives
- Target users/stakeholders
- Success metrics

**Functional Requirements**
- Core features and capabilities (extracted from code)
- User workflows and use cases
- Input/output specifications
- Data models and schemas

**Non-Functional Requirements**
- Performance requirements
- Scalability considerations
- Security requirements
- Reliability and availability

**Technical Constraints**
- Dependencies and integrations
- Platform requirements
- Known limitations

**Future Enhancements**
- Potential features (based on TODO comments or incomplete code)
- Scalability roadmap

---

### 2. Clean Architecture Analysis

Please analyze the project against Clean Architecture principles:

**Current Architecture Assessment**
- Identify existing layers (Entities, Use Cases, Interface Adapters, Frameworks)
- Dependency flow analysis
- Violations of Clean Architecture principles

**Layer Breakdown**
- **Entities/Domain Layer**: Core business logic and domain models
- **Use Cases/Application Layer**: Business rules and application-specific logic
- **Interface Adapters**: Controllers, presenters, gateways
- **Frameworks & Drivers**: External libraries, databases, UI

**Dependency Inversion**
- How dependencies point inward
- Areas where dependency inversion is violated
- Interfaces and abstractions used

**Recommendations**
- Refactoring suggestions to improve architecture
- Separation of concerns improvements
- Suggested package/module restructuring

---

### 3. High-Level Design (HLD)

Create an HLD covering:

**System Overview**
- System purpose and scope
- Key components and their responsibilities
- System boundaries and interfaces

**Architecture Diagram** (describe in text/ASCII or request mermaid)
- Component interaction flow
- Data flow between components
- External system integrations

**Component Descriptions**
- Major modules/packages
- Responsibility of each component
- Inter-component communication patterns

**Data Architecture**
- Data models and entities
- Database schema (if applicable)
- Data flow and transformations
- Caching strategy (if present)

**Technology Stack**
- Frameworks and libraries used
- Infrastructure requirements
- Third-party integrations

**Scalability & Performance**
- Bottlenecks identification
- Horizontal/vertical scaling approach
- Performance optimization strategies

**Security Architecture**
- Authentication/authorization mechanisms
- Data protection measures
- Security vulnerabilities to address

---

### 4. Low-Level Design (LLD)

Provide detailed LLD including:

**Module-Level Design**
For each major module/package:
- Purpose and responsibilities
- Public interfaces and APIs
- Key classes and their relationships
- Design patterns used

**Class Diagrams** (describe or use mermaid)
- Class hierarchies
- Relationships (inheritance, composition, aggregation)
- Key methods and attributes

**Sequence Diagrams** (for critical flows)
- User authentication flow
- Main business logic flows
- Error handling flows
- Data processing pipelines

**Detailed Component Specifications**
For each significant class/function:
- Input parameters and types
- Return values and types
- Exceptions handled
- Algorithm complexity
- Dependencies

**Data Structures**
- Custom data structures used
- Data validation rules
- Transformation logic

**API Specifications**
- REST endpoints (if applicable)
- Request/response formats
- Error codes and messages
- Rate limiting and throttling

**Database Design** (if applicable)
- Table schemas
- Indexes and constraints
- Relationships and foreign keys
- Query patterns

**Error Handling Strategy**
- Exception hierarchy
- Error propagation
- Logging strategy
- Recovery mechanisms

**Testing Strategy**
- Unit test coverage
- Integration test approach
- Test fixtures and mocks
- Edge cases covered

---

## Output Format

Please provide:

1. **PRD.md** - Complete Product Requirements Document
2. **CLEAN_ARCHITECTURE.md** - Clean Architecture analysis and recommendations
3. **HLD.md** - High-Level Design document with diagrams (mermaid format)
4. **LLD.md** - Low-Level Design with detailed specifications

For diagrams, use Mermaid syntax where applicable:
- Architecture diagrams
- Component diagrams
- Sequence diagrams
- Class diagrams

## Analysis Instructions

1. **Read and understand** the entire codebase structure
2. **Identify** the main entry points and core functionality
3. **Trace** data flow and control flow through the system
4. **Extract** business logic and domain concepts
5. **Document** patterns, anti-patterns, and architectural decisions
6. **Suggest** improvements where current design deviates from best practices

Please be thorough and specific, using actual class names, function names, and code examples from the project where relevant.