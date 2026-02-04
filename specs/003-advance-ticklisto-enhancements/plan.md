# Implementation Plan: Advanced Ticklisto Enhancements

**Branch**: `003-advance-ticklisto-enhancements` | **Date**: 2026-02-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-advance-ticklisto-enhancements/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature adds advanced time-based task management capabilities to Ticklisto, including due dates with flexible parsing, recurring tasks with custom intervals and end conditions, and email reminders via Gmail API. The implementation introduces a background daemon service for reliable reminder delivery, comprehensive date/time handling with timezone support, and sophisticated recurrence logic supporting daily, weekly, monthly, and yearly patterns with custom intervals. The system maintains backward compatibility with existing Basic and Intermediate level features while adding optional reminder functionality that gracefully degrades when Gmail API is unavailable.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**:
- Rich (CLI formatting and styling)
- python-dateutil (flexible date/time parsing)
- python-dotenv (environment variable management)
- google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client (Gmail API)
- pytest (testing framework)

**Storage**: JSON file (ticklisto_data.json) with backward compatibility for existing task data
**Testing**: pytest with unit, integration, and contract tests
**Target Platform**: Console application on local machine (Windows/Linux/macOS)
**Project Type**: Single project (console application with background daemon service)
**Performance Goals**:
- Handle 100+ tasks without degradation
- List/filter operations complete in under 2 seconds
- Recurring task instance creation within 1 second
- Email reminders sent within 60 seconds of scheduled time

**Constraints**:
- Daemon must check for reminders at least once per minute
- 95% email delivery success rate when Gmail API is configured
- Store dates in UTC, display in local timezone
- Maintain backward compatibility with existing features
- Graceful degradation when Gmail API unavailable

**Scale/Scope**:
- Single user application
- JSON data file under 10MB
- Support 100+ recurring task instances per task
- Multiple reminder times per task

## Dependencies Installation

### Required Packages

Install all required dependencies using UV:

```bash
# Core dependencies (already installed from Features 001 & 002)
uv add rich pytest

# Date/Time handling
uv add python-dateutil

# Environment configuration
uv add python-dotenv

# Data validation and serialization
uv add pydantic

# File locking (cross-platform)
uv add portalocker

# Gmail API client libraries
uv add google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Daemon service (for background reminder checking)
uv add python-daemon
```

### Installation Command (All at Once)

```bash
uv add python-dateutil python-dotenv pydantic portalocker google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-daemon
```

### Dependency Purpose

| Package | Purpose | Used For |
|---------|---------|----------|
| `python-dateutil` | Flexible date/time parsing | Parsing user date input, recurrence calculations |
| `python-dotenv` | Environment variable management | Loading Gmail API credentials from .env |
| `pydantic` | Data validation and serialization | Task/Reminder/Recurrence model validation |
| `portalocker` | Cross-platform file locking | Preventing JSON file corruption |
| `google-auth` | Google authentication library | Gmail API OAuth2 authentication |
| `google-auth-oauthlib` | OAuth2 flow for installed apps | Gmail API authorization flow |
| `google-auth-httplib2` | HTTP transport for Google APIs | Gmail API requests |
| `google-api-python-client` | Gmail API client | Sending reminder emails |
| `python-daemon` | UNIX daemon functionality | Background reminder service |

### Optional Development Dependencies

```bash
# For testing
uv add --dev pytest-cov pytest-mock pytest-asyncio

# For code quality
uv add --dev black flake8 mypy

# For documentation
uv add --dev sphinx sphinx-rtd-theme
```

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development (NON-NEGOTIABLE)
**Status**: PASS
**Evidence**: Complete specification exists at `specs/003-advance-ticklisto-enhancements/spec.md` with 47 functional requirements, 10 clarifications, and comprehensive edge case documentation.

### ✅ AI-Agent Driven Implementation
**Status**: PASS
**Evidence**: Implementation will be generated using Claude Code following Agentic Dev Stack workflow with Spec-Kit Plus.

### ✅ Progressive Complexity Evolution
**Status**: PASS
**Evidence**: Building on Phase I console application foundation (Features 001 and 002). Adds time-based functionality while maintaining console-only interface. No web/mobile components introduced.

### ✅ Reusable Intelligence & Modularity
**Status**: PASS
**Evidence**: Design will separate concerns into reusable modules: date/time handling, recurrence logic, reminder service, Gmail integration. Each component can be independently tested and potentially reused.

### ✅ Test-First (NON-NEGOTIABLE)
**Status**: PASS
**Evidence**: TDD workflow will be followed. Tests will be written for all 47 functional requirements before implementation. Comprehensive test coverage for recurrence logic, date parsing, and daemon reliability.

### ✅ Atomic Commits
**Status**: PASS
**Evidence**: Implementation will follow atomic commit principles with each logical change committed separately.

### ✅ Co-authoring with Claude Code
**Status**: PASS
**Evidence**: All commits will include "Co-authored-by: Claude Code <claude-code@anthropic.com>".

### ✅ Clean Architecture & Separation of Concerns
**Status**: PASS
**Evidence**: Architecture separates:
- Data layer (JSON persistence, Task/Reminder/RecurrencePattern models)
- Business logic (recurrence calculation, date parsing, reminder scheduling)
- Service layer (Gmail API integration, daemon service)
- Presentation layer (Rich CLI formatting, user prompts)
- Each layer has well-defined interfaces and responsibilities

### Technology Stack Compliance
**Status**: PASS
**Evidence**:
- ✅ Python 3.13+
- ✅ UV for package management
- ✅ pytest for testing
- ✅ Rich for CLI interfaces
- ✅ Git for version control
- ✅ JSON file storage (Phase I requirement)
- ✅ Console-based UI (Phase I requirement)

## Project Structure

### Documentation (this feature)

```text
specs/003-advance-ticklisto-enhancements/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── task-schema.json
│   ├── reminder-schema.json
│   └── recurrence-schema.json
├── checklists/
│   └── requirements.md  # Quality validation checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── __init__.py
│   ├── task.py              # Task entity with due dates and recurrence
│   ├── reminder.py          # Reminder entity
│   ├── recurrence.py        # RecurrencePattern entity
│   └── config.py            # GmailConfig entity
├── services/
│   ├── __init__.py
│   ├── task_service.py      # Task CRUD operations
│   ├── recurrence_service.py # Recurrence calculation logic
│   ├── reminder_service.py  # Reminder scheduling and management
│   ├── gmail_service.py     # Gmail API integration
│   └── daemon_service.py    # Background daemon for reminder checking
├── utils/
│   ├── __init__.py
│   ├── date_parser.py       # Flexible date/time parsing
│   ├── date_formatter.py    # Date/time display formatting
│   └── file_lock.py         # JSON file locking mechanism
├── storage/
│   ├── __init__.py
│   └── json_storage.py      # JSON persistence with backup/recovery
├── cli/
│   ├── __init__.py
│   ├── commands.py          # CLI command handlers
│   ├── prompts.py           # Rich-formatted user prompts
│   └── display.py           # Rich-formatted task display
└── main.py                  # Application entry point

daemon/
├── __init__.py
├── reminder_daemon.py       # Daemon main process
├── daemon_manager.py        # Start/stop/status management
└── install_service.py       # System service installation script

tests/
├── unit/
│   ├── test_task_model.py
│   ├── test_recurrence_service.py
│   ├── test_date_parser.py
│   ├── test_reminder_service.py
│   └── test_gmail_service.py
├── integration/
│   ├── test_task_workflow.py
│   ├── test_recurring_tasks.py
│   └── test_reminder_workflow.py
└── contract/
    ├── test_task_schema.py
    ├── test_reminder_schema.py
    └── test_recurrence_schema.py

config/
├── .env.example             # Example environment configuration
└── systemd/                 # Service installation files
    ├── ticklisto-daemon.service  # Linux systemd service
    └── install.sh           # Service installation script
```

**Structure Decision**: Single project structure selected as this is a Phase I console application. The daemon service is implemented as a separate process within the same project rather than a separate service project. This maintains simplicity while providing the required background reminder functionality. The structure separates concerns into clear layers (models, services, utils, storage, cli, daemon) enabling independent development and testing of each component.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected. All principles are satisfied by the proposed architecture.

## Phase 0: Research & Technology Decisions

### Research Tasks

The following areas require research to resolve implementation unknowns and establish best practices:

1. **Python Daemon/Service Implementation**
   - Research: Cross-platform daemon implementation patterns
   - Questions: How to implement auto-start on boot for Windows/Linux/macOS? How to handle crash recovery and automatic restart?
   - Output: Recommended approach for daemon service with platform-specific installation

2. **Gmail API Integration Best Practices**
   - Research: OAuth2 flow, credential storage, token refresh, error handling
   - Questions: How to securely store credentials? How to handle token expiration? What are quota limits?
   - Output: Gmail API integration pattern with security best practices

3. **Date/Time Parsing Library Evaluation**
   - Research: python-dateutil vs alternatives (dateparser, arrow)
   - Questions: Which library best supports flexible parsing with ambiguity detection?
   - Output: Selected library with rationale

4. **Recurrence Calculation Algorithms**
   - Research: Best practices for calculating next occurrence dates
   - Questions: How to handle edge cases (month boundaries, leap years, DST transitions)?
   - Output: Recurrence calculation algorithm with edge case handling

5. **File Locking Mechanisms**
   - Research: Python file locking libraries (fcntl, portalocker)
   - Questions: How to prevent concurrent JSON file access corruption?
   - Output: Selected file locking approach

6. **JSON Schema Validation**
   - Research: JSON schema validation libraries (jsonschema, pydantic)
   - Questions: How to validate task data structure and maintain backward compatibility?
   - Output: Validation approach for JSON data

### Next Steps

Phase 0 will generate `research.md` with findings and decisions for each research task. This will resolve all "NEEDS CLARIFICATION" items and establish the technical foundation for Phase 1 design.

