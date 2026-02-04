# Implementation Tasks: Advanced Ticklisto Enhancements

**Feature**: Advanced Ticklisto Enhancements
**Branch**: `003-advance-ticklisto-enhancements`
**Date**: 2026-02-04
**Status**: Ready for Implementation

This document provides a complete, dependency-ordered task breakdown for implementing advanced time-based task management features following Test-Driven Development (TDD) principles.

## Overview

**Total Tasks**: 87
**User Stories**: 3 (P1: Due Dates, P2: Recurring Tasks, P3: Email Reminders)
**Approach**: TDD with Red-Green-Refactor cycle
**MVP Scope**: User Story 1 (Due Dates & Times) - 28 tasks

## Implementation Strategy

### Incremental Delivery
1. **MVP (User Story 1)**: Due dates and times - delivers immediate value for task scheduling
2. **Enhancement (User Story 2)**: Recurring tasks - automates routine task management
3. **Premium (User Story 3)**: Email reminders - extends value beyond active usage

### Parallel Execution Opportunities
- Tasks marked with `[P]` can be executed in parallel with other `[P]` tasks in the same phase
- Tests can run in parallel with other tests
- Model implementations can run in parallel when they don't depend on each other

### Dependencies Between User Stories
- **US2 depends on US1**: Recurring tasks require due date functionality
- **US3 depends on US1**: Email reminders require due date functionality
- **US3 independent of US2**: Email reminders work without recurring tasks

---

## Phase 1: Setup & Project Initialization

**Goal**: Set up project structure, install dependencies, and configure development environment.

**Tasks**:

- [ ] T001 Install required dependencies using UV: `uv add python-dateutil python-dotenv pydantic portalocker google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-daemon`
- [ ] T002 Install development dependencies: `uv add --dev pytest-cov pytest-mock pytest-asyncio`
- [ ] T003 Create project directory structure per plan.md: src/{models,services,utils,storage,cli}, daemon/, tests/{unit,integration,contract}, config/
- [ ] T004 Create __init__.py files in all Python package directories
- [ ] T005 Create config/.env.example with Gmail API configuration template
- [ ] T006 Add .env to .gitignore to prevent credential exposure
- [ ] T007 Create config/systemd/ticklisto-daemon.service template for Linux
- [ ] T008 Update pyproject.toml with project metadata and entry points

---

## Phase 2: Foundational Infrastructure

**Goal**: Implement shared infrastructure components that all user stories depend on.

**Independent Test**: Infrastructure components can be tested independently before user story implementation.

### Tests (Write First - TDD)

- [ ] T009 [P] Write unit tests for file locking in tests/unit/test_file_lock.py
- [ ] T010 [P] Write unit tests for JSON storage with backup in tests/unit/test_json_storage.py
- [ ] T011 [P] Write contract tests for Task schema validation in tests/contract/test_task_schema.py

### Implementation (After Tests Fail)

- [ ] T012 [P] Implement cross-platform file locking utility in src/utils/file_lock.py using portalocker
- [ ] T013 [P] Implement JSON storage with file locking and backup in src/storage/json_storage.py
- [ ] T014 Enhance existing Task model in src/models/task.py with new fields: due_date, is_recurring, parent_task_id, completion_history, reminders (all optional with defaults)
- [ ] T015 Run tests T009-T011 and verify they pass (Green phase)

---

## Phase 3: User Story 1 - Task Scheduling with Due Dates and Times (P1)

**Story Goal**: Enable users to assign due dates and times to tasks for effective planning.

**Independent Test**: Create tasks with due dates, sort by deadline, verify display and overdue detection.

**Value Delivered**: Transforms Ticklisto from simple list manager to scheduling tool.

### Tests (Write First - TDD)

- [ ] T016 [P] [US1] Write unit tests for date parser with ambiguity detection in tests/unit/test_date_parser.py
- [ ] T017 [P] [US1] Write unit tests for date formatter (UTC to local, time remaining) in tests/unit/test_date_formatter.py
- [ ] T018 [P] [US1] Write unit tests for Task model due date validation in tests/unit/test_task_model.py
- [ ] T019 [P] [US1] Write unit tests for TaskService due date operations in tests/unit/test_task_service.py
- [ ] T020 [P] [US1] Write integration tests for due date workflow in tests/integration/test_due_date_workflow.py

### Implementation (After Tests Fail)

- [ ] T021 [P] [US1] Implement flexible date parser with ambiguity detection in src/utils/date_parser.py using python-dateutil
- [ ] T022 [P] [US1] Implement date formatter for display (UTC to local, time remaining calculation) in src/utils/date_formatter.py
- [ ] T023 [US1] Update Task model validation to support due_date field in src/models/task.py
- [ ] T024 [US1] Implement TaskService methods: add_due_date(), update_due_date(), clear_due_date() in src/services/task_service.py
- [ ] T025 [US1] Implement TaskService methods: get_overdue_tasks(), get_tasks_due_today(), get_tasks_due_this_week() in src/services/task_service.py
- [ ] T026 [US1] Implement TaskService method: sort_by_due_date() in src/services/task_service.py
- [ ] T027 [US1] Add CLI command: `ticklisto add --due <date>` in src/cli/commands.py
- [ ] T028 [US1] Add CLI command: `ticklisto update <id> --due <date>` in src/cli/commands.py
- [ ] T029 [US1] Add CLI command: `ticklisto list --due <today|week|overdue>` in src/cli/commands.py
- [ ] T030 [US1] Add CLI command: `ticklisto list --sort due` in src/cli/commands.py
- [ ] T031 [US1] Implement Rich-formatted display for tasks with due dates (colored text, icons) in src/cli/display.py
- [ ] T032 [US1] Implement Rich-formatted display for overdue tasks (red text, warning icon) in src/cli/display.py
- [ ] T033 [US1] Implement Rich-formatted prompts for date input with format examples in src/cli/prompts.py
- [ ] T034 [US1] Implement ambiguous date clarification prompt in src/cli/prompts.py
- [ ] T035 [US1] Run all US1 tests (T016-T020) and verify they pass (Green phase)

### Integration & Polish

- [ ] T036 [US1] Test complete US1 workflow: create task with due date, update due date, view sorted list, verify overdue detection
- [ ] T037 [US1] Test edge cases: past due dates, timezone handling, invalid date formats
- [ ] T038 [US1] Update JSON storage to persist due_date field with backward compatibility
- [ ] T039 [US1] Verify existing Basic and Intermediate features still work (regression testing)

### User Story 1 Acceptance Criteria

- [x] Users can create tasks with optional due dates and times
- [x] Users can update existing tasks to add/modify/remove due dates
- [x] Tasks can be sorted by due date (earliest first)
- [x] Tasks can be filtered by due date ranges (today, week, overdue)
- [x] Overdue tasks are visually distinct (red text, warning icon)
- [x] Time remaining is displayed (e.g., "Due in 3 hours", "Overdue by 1 day")
- [x] Ambiguous dates prompt for clarification
- [x] Backward compatibility maintained with existing tasks

---

## Phase 4: User Story 2 - Recurring Task Automation (P2)

**Story Goal**: Enable users to create recurring tasks that automatically reschedule after completion.

**Independent Test**: Create recurring task, mark complete, verify new instance created with next due date.

**Value Delivered**: Eliminates repetitive data entry for routine activities.

**Dependencies**: Requires US1 (due dates) to be complete.

### Tests (Write First - TDD)

- [ ] T040 [P] [US2] Write contract tests for RecurrencePattern schema in tests/contract/test_recurrence_schema.py
- [ ] T041 [P] [US2] Write unit tests for RecurrencePattern model validation in tests/unit/test_recurrence_model.py
- [ ] T042 [P] [US2] Write unit tests for recurrence calculation (next occurrence) in tests/unit/test_recurrence_service.py
- [ ] T043 [P] [US2] Write unit tests for recurring task completion logic in tests/unit/test_task_service.py
- [ ] T044 [P] [US2] Write integration tests for recurring task workflow in tests/integration/test_recurring_tasks.py

### Implementation (After Tests Fail)

- [ ] T045 [P] [US2] Create RecurrencePattern model with validation in src/models/recurrence.py using Pydantic
- [ ] T046 [US2] Update Task model to include recurrence_pattern field in src/models/task.py
- [ ] T047 [US2] Implement RecurrenceService with calculate_next_occurrence() using dateutil.rrule in src/services/recurrence_service.py
- [ ] T048 [US2] Implement RecurrenceService methods: validate_interval(), handle_monthly_edge_cases() in src/services/recurrence_service.py
- [ ] T049 [US2] Update TaskService.mark_complete() to create new instance for recurring tasks in src/services/task_service.py
- [ ] T050 [US2] Implement TaskService methods: create_recurring_task(), update_recurrence_pattern() in src/services/task_service.py
- [ ] T051 [US2] Implement TaskService method: delete_recurring_task(instance_only=True/False) in src/services/task_service.py
- [ ] T052 [US2] Add CLI command: `ticklisto add --recur <daily|weekly|monthly|yearly> --interval <N>` in src/cli/commands.py
- [ ] T053 [US2] Add CLI command: `ticklisto add --recur weekly --weekdays <Mon,Wed,Fri>` in src/cli/commands.py
- [ ] T054 [US2] Add CLI command: `ticklisto add --recur <pattern> --until <date>` or `--count <N>` in src/cli/commands.py
- [ ] T055 [US2] Add CLI command: `ticklisto update <id> --recur <pattern>` in src/cli/commands.py
- [ ] T056 [US2] Add CLI command: `ticklisto delete <id> --instance` or `--all-future` in src/cli/commands.py
- [ ] T057 [US2] Add CLI command: `ticklisto list --recurring` in src/cli/commands.py
- [ ] T058 [US2] Implement Rich-formatted display for recurring tasks (pattern, next occurrence) in src/cli/display.py
- [ ] T059 [US2] Implement Rich-formatted prompts for recurrence pattern selection in src/cli/prompts.py
- [ ] T060 [US2] Implement Rich-formatted prompts for weekly day selection in src/cli/prompts.py
- [ ] T061 [US2] Implement Rich-formatted prompts for end condition selection in src/cli/prompts.py
- [ ] T062 [US2] Run all US2 tests (T040-T044) and verify they pass (Green phase)

### Integration & Polish

- [ ] T063 [US2] Test complete US2 workflow: create recurring task, mark complete, verify new instance, update pattern, delete options
- [ ] T064 [US2] Test edge cases: monthly day 31, leap years, DST transitions, interval limits, end conditions
- [ ] T065 [US2] Update JSON storage to persist recurrence_pattern and completion_history
- [ ] T066 [US2] Verify US1 features still work with recurring tasks

### User Story 2 Acceptance Criteria

- [x] Users can create recurring tasks with daily/weekly/monthly/yearly patterns
- [x] Users can specify custom intervals (every N days/weeks/months/years)
- [x] Users can select specific weekdays for weekly recurrence
- [x] Users can set end conditions (end date or occurrence count)
- [x] Completing a recurring task automatically creates next instance
- [x] Next due date calculated from original due date (not completion date)
- [x] Users can update recurrence pattern of existing tasks
- [x] Users can delete single instance or all future instances
- [x] Recurrence information displayed clearly
- [x] Monthly edge cases handled (day 29-31)
- [x] Completion history maintained

---

## Phase 5: User Story 3 - Email Reminder Notifications (P3)

**Story Goal**: Enable users to receive email reminders for upcoming tasks.

**Independent Test**: Create task with reminder, wait for trigger, verify email sent.

**Value Delivered**: Proactive notifications prevent missed deadlines.

**Dependencies**: Requires US1 (due dates). Independent of US2 (recurring tasks).

### Tests (Write First - TDD)

- [ ] T067 [P] [US3] Write contract tests for Reminder schema in tests/contract/test_reminder_schema.py
- [ ] T068 [P] [US3] Write contract tests for GmailConfig schema in tests/contract/test_gmail_config_schema.py
- [ ] T069 [P] [US3] Write unit tests for Reminder model validation in tests/unit/test_reminder_model.py
- [ ] T070 [P] [US3] Write unit tests for GmailService OAuth2 flow in tests/unit/test_gmail_service.py (mocked)
- [ ] T071 [P] [US3] Write unit tests for ReminderService scheduling logic in tests/unit/test_reminder_service.py
- [ ] T072 [P] [US3] Write unit tests for daemon service reminder checking in tests/unit/test_daemon_service.py
- [ ] T073 [P] [US3] Write integration tests for reminder workflow in tests/integration/test_reminder_workflow.py

### Implementation (After Tests Fail)

- [ ] T074 [P] [US3] Create Reminder model with validation in src/models/reminder.py using Pydantic
- [ ] T075 [P] [US3] Create GmailConfig model in src/models/config.py using Pydantic
- [ ] T076 [US3] Update Task model to include reminders field in src/models/task.py
- [ ] T077 [US3] Implement GmailService with OAuth2 authentication in src/services/gmail_service.py
- [ ] T078 [US3] Implement GmailService.send_email() with retry logic in src/services/gmail_service.py
- [ ] T079 [US3] Implement GmailService.send_consolidated_email() for multiple reminders in src/services/gmail_service.py
- [ ] T080 [US3] Implement ReminderService with schedule_reminder(), get_due_reminders() in src/services/reminder_service.py
- [ ] T081 [US3] Implement ReminderService.calculate_reminder_time() from offset in src/services/reminder_service.py
- [ ] T082 [US3] Implement daemon main loop in daemon/reminder_daemon.py using python-daemon
- [ ] T083 [US3] Implement daemon manager (start/stop/status/restart) in daemon/daemon_manager.py
- [ ] T084 [US3] Implement daemon service installer for systemd/launchd/Task Scheduler in daemon/install_service.py
- [ ] T085 [US3] Add CLI command: `ticklisto auth gmail` for OAuth2 setup in src/cli/commands.py
- [ ] T086 [US3] Add CLI command: `ticklisto add --due <date> --remind <offset>` in src/cli/commands.py
- [ ] T087 [US3] Add CLI command: `ticklisto daemon <start|stop|status|restart>` in src/cli/commands.py
- [ ] T088 [US3] Implement Rich-formatted prompts for reminder offset selection in src/cli/prompts.py
- [ ] T089 [US3] Implement Rich-formatted display for reminder status in src/cli/display.py
- [ ] T090 [US3] Load Gmail configuration from .env using python-dotenv in src/services/gmail_service.py
- [ ] T091 [US3] Run all US3 tests (T067-T073) and verify they pass (Green phase)

### Integration & Polish

- [ ] T092 [US3] Test complete US3 workflow: configure Gmail, create task with reminder, verify email sent
- [ ] T093 [US3] Test edge cases: Gmail API failures, token expiration, quota limits, offline mode
- [ ] T094 [US3] Test daemon crash recovery and auto-restart
- [ ] T095 [US3] Update JSON storage to persist reminders and Gmail config
- [ ] T096 [US3] Verify US1 and US2 features work with reminders

### User Story 3 Acceptance Criteria

- [x] Users can configure Gmail API credentials via .env
- [x] Users can authenticate with Gmail using OAuth2 flow
- [x] Users can add reminders to tasks with due dates
- [x] Predefined reminder offsets available (15m, 30m, 1h, 2h, 1d, 1w)
- [x] Custom reminder offsets supported
- [x] Multiple reminders per task supported
- [x] Background daemon checks for due reminders every minute
- [x] Email sent within 60 seconds of reminder time
- [x] Multiple reminders consolidated into single email
- [x] Daemon auto-starts on system boot
- [x] Daemon recovers from crashes automatically
- [x] Gmail API errors handled gracefully
- [x] Failed reminders retried once after 5 minutes
- [x] Reminders can be disabled globally or per-task

---

## Phase 6: Polish & Cross-Cutting Concerns

**Goal**: Final integration, documentation, and quality assurance.

### Documentation

- [ ] T097 Update README.md with new features, installation instructions, and examples
- [ ] T098 Create user guide for due dates and recurring tasks
- [ ] T099 Create Gmail API setup guide with screenshots
- [ ] T100 Document daemon installation for all platforms

### Testing & Quality

- [ ] T101 Run full test suite and achieve >90% code coverage
- [ ] T102 Perform end-to-end testing of all three user stories together
- [ ] T103 Test backward compatibility with existing task data
- [ ] T104 Performance testing with 100+ tasks
- [ ] T105 Security audit of Gmail credential storage

### Deployment

- [ ] T106 Create release notes for version 3.0.0
- [ ] T107 Tag release and push to GitHub

---

## Dependency Graph

### User Story Completion Order

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
Phase 3 (US1: Due Dates) ← MVP Scope
    ↓
    ├─→ Phase 4 (US2: Recurring Tasks)
    └─→ Phase 5 (US3: Email Reminders)
         ↓
    Phase 6 (Polish)
```

### Critical Path
1. Setup → Foundational → US1 (28 tasks) = **MVP**
2. US1 → US2 (27 tasks) = **Enhancement**
3. US1 → US3 (30 tasks) = **Premium**

### Parallel Opportunities

**Phase 2 (Foundational)**:
- T009, T010, T011 can run in parallel (different test files)
- T012, T013 can run in parallel (different modules)

**Phase 3 (US1)**:
- T016, T017, T018, T019, T020 can run in parallel (different test files)
- T021, T022 can run in parallel (different utility modules)

**Phase 4 (US2)**:
- T040, T041, T042, T043, T044 can run in parallel (different test files)
- T045, T046 can run in parallel (different model files)

**Phase 5 (US3)**:
- T067, T068, T069, T070, T071, T072, T073 can run in parallel (different test files)
- T074, T075 can run in parallel (different model files)

---

## Task Execution Guidelines

### TDD Workflow (Red-Green-Refactor)

1. **Red**: Write test first, run it, watch it fail
2. **Green**: Write minimal code to make test pass
3. **Refactor**: Improve code quality while keeping tests green

### Task Format

Every task follows this format:
- `- [ ]` Checkbox for tracking completion
- `T###` Sequential task ID
- `[P]` Parallel execution marker (optional)
- `[US#]` User story label (for story phases only)
- Description with specific file path

### Atomic Commits

Each task should result in one atomic commit:
```bash
git add <files>
git commit -m "T###: <description>

Co-authored-by: Claude Code <claude-code@anthropic.com>"
```

### Test Execution

Run tests after each implementation task:
```bash
# Run specific test file
pytest tests/unit/test_date_parser.py -v

# Run all tests for a user story
pytest tests/ -k "US1" -v

# Run full test suite
pytest tests/ --cov=src --cov-report=html
```

---

## MVP Scope Recommendation

**Minimum Viable Product**: User Story 1 (Due Dates & Times)
- **Tasks**: T001-T039 (39 tasks including setup and foundational)
- **Value**: Transforms Ticklisto into a scheduling tool
- **Time Estimate**: Focus on core functionality first
- **Deliverable**: Users can create, update, and view tasks with due dates

**Rationale**: US1 provides immediate value and is the foundation for US2 and US3. Delivering US1 first allows users to start benefiting from time-based task management while US2 and US3 are developed.

---

## Notes

- All tasks follow TDD principles (tests before implementation)
- Each user story is independently testable
- Backward compatibility maintained throughout
- Gmail API integration is optional (graceful degradation)
- Daemon service provides reliable reminder delivery
- Cross-platform support (Windows, Linux, macOS)
