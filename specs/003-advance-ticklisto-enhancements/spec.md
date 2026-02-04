# Feature Specification: Advanced Ticklisto Enhancements

**Feature Branch**: `003-advance-ticklisto-enhancements`
**Created**: 2026-02-04
**Status**: Draft
**Input**: User description: "Advanced Level features: Recurring Tasks, Due Dates & Time Reminders with Gmail API notifications"

## Clarifications

### Session 2026-02-04

- Q: How should Gmail API credentials and tokens be stored to ensure security? → A: Store credentials in .env file with paths in .gitignore
- Q: How should the reminder checking mechanism work? → A: Background daemon/service that runs separately from the main CLI application
- Q: For weekly recurring tasks, how should the day of the week be determined? → A: Prompt user to explicitly select which day of week for weekly recurrence
- Q: For monthly recurring tasks, how should the system handle months with fewer days than the original due date? → A: Use the last day of the month when the specific day doesn't exist
- Q: What format should users enter for dates and times when creating or updating tasks? → A: Flexible parsing supporting multiple formats
- Q: How should the reminder daemon handle startup, crashes, and system restarts? → A: Auto-start on system boot with crash recovery and automatic restart
- Q: What reminder time offset options should be available to users? → A: Predefined common options with ability to enter custom offset
- Q: How should the system handle ambiguous date inputs like "02/03/2026"? → A: Always prompt user to clarify when format is ambiguous
- Q: Should the system support custom recurrence intervals (e.g., "every 2 weeks", "every 3 days")? → A: Support intervals for all patterns (every N days/weeks/months/years) with reasonable limits
- Q: Should users be able to set end conditions for recurring tasks? → A: Support both end date and occurrence count as optional end conditions

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Scheduling with Due Dates and Times (Priority: P1)

As a Ticklisto user, I want to assign due dates and specific times to my tasks so that I can plan my work effectively and know when tasks need to be completed.

**Why this priority**: This is the foundation for time-based task management. Without due dates and times, users cannot effectively plan or prioritize time-sensitive work. This feature delivers immediate value by transforming Ticklisto from a simple list manager into a scheduling tool.

**Independent Test**: Can be fully tested by creating tasks with various due dates/times, viewing them sorted by deadline, and verifying that tasks display their scheduled information correctly. Delivers value by enabling users to see "what's due when" at a glance.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I provide a title, description, and optionally specify a due date and time, **Then** the task is created with the scheduled information stored and displayed
2. **Given** I have an existing task without a due date, **When** I update it to add a due date and time, **Then** the task shows the new deadline information
3. **Given** I have tasks with different due dates, **When** I view my task list sorted by due date, **Then** tasks appear in chronological order with overdue tasks highlighted
4. **Given** I am viewing a task, **When** the task has a due date and time, **Then** I can see how much time remains until the deadline (e.g., "Due in 2 hours", "Overdue by 1 day")
5. **Given** I have a task with a due date, **When** I mark it complete, **Then** the completion is recorded with timestamp and the task no longer appears in "upcoming" views

---

### User Story 2 - Recurring Task Automation (Priority: P2)

As a Ticklisto user, I want to create recurring tasks that automatically reschedule themselves after completion so that I don't have to manually recreate routine tasks like "weekly team meeting" or "monthly report".

**Why this priority**: Recurring tasks eliminate repetitive data entry for routine activities. This builds on P1 (due dates) and significantly improves productivity for users with regular responsibilities. It's P2 because it requires due date functionality to work properly.

**Independent Test**: Can be fully tested by creating a recurring task (e.g., "daily standup"), marking it complete, and verifying that a new instance is automatically created with the next scheduled date. Delivers value by automating routine task management.

**Acceptance Scenarios**:

1. **Given** I am creating a new task, **When** I specify a recurrence pattern (daily, weekly, monthly, yearly) and a due date, **Then** the task is created with recurrence information stored
2. **Given** I have a recurring task that is due, **When** I mark it as complete, **Then** a new instance of the task is automatically created with the next scheduled due date based on the recurrence pattern
3. **Given** I have a recurring task, **When** I view its details, **Then** I can see the recurrence pattern (e.g., "Repeats: Every Monday") and the next scheduled occurrence
4. **Given** I have a recurring task, **When** I update its recurrence pattern, **Then** future instances follow the new pattern while preserving the completion history
5. **Given** I have a recurring task, **When** I delete it, **Then** I am asked whether to delete only this instance or all future instances, and the system acts accordingly

---

### User Story 3 - Email Reminder Notifications (Priority: P3)

As a Ticklisto user, I want to receive email reminders for upcoming tasks so that I don't miss important deadlines even when I'm not actively using the application.

**Why this priority**: Email reminders extend Ticklisto's value beyond active usage sessions. This is P3 because it requires external service integration (Gmail API) and depends on P1 (due dates/times). It enhances the experience but the core functionality works without it.

**Independent Test**: Can be fully tested by creating a task with a due date and reminder time, waiting for the reminder trigger, and verifying that an email is sent to the configured address. Delivers value by proactively notifying users of upcoming deadlines.

**Acceptance Scenarios**:

1. **Given** I have configured my Gmail account for reminders, **When** I create a task with a due date, **Then** I can optionally set when to receive a reminder (e.g., "15 minutes before", "1 hour before", "1 day before")
2. **Given** I have a task with a reminder configured, **When** the reminder time is reached, **Then** an email is sent to my configured email address with task details and due date
3. **Given** I have multiple tasks with reminders due at similar times, **When** the reminder time arrives, **Then** I receive a single consolidated email listing all upcoming tasks
4. **Given** I have a recurring task with reminders, **When** each new instance is created, **Then** the reminder is automatically scheduled for the new due date
5. **Given** the Gmail API is unavailable or authentication fails, **When** a reminder should be sent, **Then** the system logs the error and displays a warning in the console without crashing

---

### Edge Cases

- **Past due dates**: What happens when a user creates a task with a due date in the past? System should accept it but mark it as overdue immediately.
- **Recurring task completion timing**: If a user completes a recurring task early (before its due date), should the next instance be scheduled from the original due date or from the completion date? Default: schedule from original due date to maintain consistent intervals.
- **Recurring task deletion**: When deleting a recurring task, should it delete only the current instance or all future instances? Require user confirmation with clear options.
- **Gmail API authentication failure**: How does the system handle expired tokens or revoked access? System should gracefully degrade, log errors, and prompt user to re-authenticate.
- **Timezone handling**: How are due dates and times stored and displayed across different timezones? Store in UTC, display in system local time.
- **Concurrent task modifications**: What happens if a recurring task is modified while the system is auto-creating the next instance? Use file locking or atomic operations to prevent data corruption.
- **Email delivery failures**: What happens if Gmail API returns an error when sending a reminder? Log the failure, retry once after 5 minutes, then mark as failed and notify user in console.
- **Reminder timing precision**: How precise should reminder timing be? Background daemon checks for due reminders every minute and sends within 60 seconds of scheduled time.
- **Multiple recurrence patterns**: Can a task have multiple recurrence patterns (e.g., "every Monday and Friday")? Initial implementation supports single pattern only; document as future enhancement.
- **Task completion without due date**: What happens when a recurring task without a due date is marked complete? System should prevent creating recurring tasks without due dates.
- **Weekly recurrence day selection**: For weekly recurring tasks, user explicitly selects which day(s) of the week during task creation.
- **Monthly recurrence edge cases**: For monthly recurring tasks on day 29-31, system uses the last day of months with fewer days (e.g., Jan 31 → Feb 28/29, Mar 31).
- **Ambiguous date input**: When user enters ambiguous dates (e.g., "02/03/2026" could be Feb 3 or Mar 2), system must prompt user to clarify the intended date before accepting the input.
- **Daemon crash recovery**: If the reminder daemon crashes, it must automatically restart and resume checking for due reminders without losing state.
- **Recurring task end condition reached**: When a recurring task reaches its end date or occurrence count limit, system must mark it as completed and stop creating new instances.
- **Custom interval validation**: System must validate custom recurrence intervals are within reasonable limits and reject invalid values (e.g., "every 0 days" or "every 1000 weeks").

## Requirements *(mandatory)*

### Functional Requirements

#### Due Dates & Times
- **FR-001**: System MUST allow users to optionally specify a due date when creating or updating a task
- **FR-002**: System MUST allow users to optionally specify a due time (hour and minute) when a due date is set
- **FR-003**: System MUST store due dates and times in ISO 8601 format (UTC) in the JSON data file
- **FR-004**: System MUST display due dates and times in the user's local timezone
- **FR-005**: System MUST calculate and display time remaining until due date (e.g., "Due in 3 hours", "Due tomorrow at 2:00 PM")
- **FR-006**: System MUST mark tasks as "overdue" when the current time exceeds the due date/time
- **FR-007**: System MUST support sorting tasks by due date (earliest first)
- **FR-008**: System MUST support filtering tasks by due date ranges (e.g., "due today", "due this week", "overdue")
- **FR-009**: System MUST allow users to clear/remove due dates from existing tasks

#### Recurring Tasks
- **FR-010**: System MUST allow users to specify a recurrence pattern when creating or updating a task with a due date
- **FR-011**: System MUST support the following recurrence patterns: daily, weekly (with explicit day-of-week selection), monthly, yearly, with custom intervals (e.g., every 2 days, every 3 weeks, every 6 months)
- **FR-011a**: System MUST enforce reasonable interval limits: daily (1-365 days), weekly (1-52 weeks), monthly (1-24 months), yearly (1-10 years)
- **FR-011b**: System MUST allow users to optionally set end conditions for recurring tasks: end date (repeat until specific date) or occurrence count (repeat N times), or no end condition (repeat indefinitely)
- **FR-012**: System MUST prevent creating recurring tasks without a due date
- **FR-013**: System MUST automatically create a new task instance when a recurring task is marked complete
- **FR-013a**: System MUST stop creating new instances when a recurring task reaches its end date or occurrence count limit
- **FR-014**: System MUST calculate the next due date based on the recurrence pattern and the original due date (not completion date)
- **FR-015**: System MUST preserve task properties (title, description, priority, tags, recurrence pattern) when creating the next instance
- **FR-016**: System MUST maintain a completion history showing when each instance was completed
- **FR-017**: System MUST allow users to update the recurrence pattern of existing recurring tasks
- **FR-018**: System MUST allow users to delete a single instance or all future instances of a recurring task
- **FR-019**: System MUST display recurrence information clearly (e.g., "Repeats: Daily", "Next: 2026-02-05 09:00")
- **FR-020**: System MUST allow users to convert a non-recurring task to recurring and vice versa
- **FR-021**: System MUST handle monthly recurrence edge cases by using the last day of the month when the original day doesn't exist (e.g., Jan 31 → Feb 28/29)

#### Email Reminders
- **FR-021**: System MUST allow users to configure Gmail API credentials for sending reminder emails, stored in .env file with credential file paths excluded via .gitignore
- **FR-022**: System MUST allow users to specify their email address for receiving reminders in .env configuration
- **FR-023**: System MUST allow users to optionally set reminder times for tasks with due dates, offering predefined common options (15 minutes, 30 minutes, 1 hour, 2 hours, 1 day, 1 week before) with ability to enter custom time offsets
- **FR-024**: System MUST support multiple reminder times per task (e.g., "1 day before" and "1 hour before")
- **FR-025**: System MUST provide a background daemon/service that checks for due reminders at least once per minute, running independently of the CLI application, with auto-start on system boot, crash recovery, and automatic restart capabilities
- **FR-026**: System MUST send reminder emails via Gmail API when the reminder time is reached
- **FR-027**: System MUST include task title, description, due date/time, and priority in reminder emails
- **FR-028**: System MUST consolidate multiple reminders due within the same minute into a single email
- **FR-029**: System MUST handle Gmail API authentication errors gracefully without crashing
- **FR-030**: System MUST log all reminder sending attempts (success and failure) with timestamps
- **FR-031**: System MUST retry failed reminder sends once after 5 minutes, then mark as failed
- **FR-032**: System MUST allow users to disable reminders globally or per-task
- **FR-033**: System MUST automatically schedule reminders for new instances of recurring tasks
- **FR-034**: System MUST provide commands to start, stop, restart, and check status of the reminder daemon service

#### Data Persistence
- **FR-035**: System MUST persist all due date, time, recurrence, and reminder data in the JSON data file
- **FR-036**: System MUST maintain backward compatibility with existing task data (tasks without due dates/recurrence)
- **FR-037**: System MUST support flexible date/time input parsing, accepting multiple formats (ISO 8601, US format MM/DD/YYYY, European format DD/MM/YYYY, and common variations) and validate with clear error messages for invalid inputs
- **FR-038**: System MUST handle JSON file corruption gracefully with backup and recovery options

#### User Interface
- **FR-039**: System MUST provide clear, intuitive prompts for entering due dates and times using Rich library formatting, accepting flexible input formats (ISO 8601, US, European, and common variations)
- **FR-040**: System MUST display tasks with due dates in a visually distinct format (e.g., colored text, icons)
- **FR-040**: System MUST show overdue tasks prominently (e.g., red text, warning icon)
- **FR-041**: System MUST provide a command to view all recurring tasks and their next scheduled dates
- **FR-042**: System MUST provide a command to view upcoming tasks grouped by time period (today, tomorrow, this week)
- **FR-043**: System MUST display reminder configuration status and next scheduled reminder times

### Key Entities

- **Task**: Represents a single task or to-do item
  - Core attributes: id, title, description, status (complete/incomplete), created_at, updated_at
  - Existing attributes: priority (high/medium/low), tags/categories
  - New attributes: due_date (ISO 8601 datetime in UTC), recurrence_pattern (daily/weekly/monthly/yearly/none), is_recurring (boolean), parent_task_id (for tracking recurring instances), completion_history (list of completion timestamps)

- **Reminder**: Represents a scheduled reminder for a task
  - Attributes: task_id, reminder_time (ISO 8601 datetime in UTC), offset_from_due (e.g., "-1 hour", "-1 day"), status (pending/sent/failed), sent_at, error_message

- **RecurrencePattern**: Defines how a task repeats
  - Attributes: pattern_type (daily/weekly/monthly/yearly), interval (e.g., every 2 weeks), end_date (optional), occurrences_count (optional limit)

- **GmailConfig**: Stores Gmail API configuration
  - Attributes: user_email, credentials_path, token_path, enabled (boolean)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task with a due date and time in under 30 seconds using intuitive prompts
- **SC-002**: Users can set up a recurring task (e.g., "daily standup at 9 AM") in under 45 seconds
- **SC-003**: System automatically creates the next instance of a recurring task within 1 second of marking the current instance complete
- **SC-004**: Email reminders are sent within 60 seconds of the scheduled reminder time
- **SC-005**: System handles 100+ tasks with due dates and reminders without performance degradation (list/filter operations complete in under 2 seconds)
- **SC-006**: 95% of reminder emails are successfully delivered when Gmail API is properly configured
- **SC-007**: System gracefully handles Gmail API failures without data loss or application crashes
- **SC-008**: Users can view all tasks due today or overdue in a single command with clear visual indicators
- **SC-009**: Recurring task completion history is accurately maintained for at least 100 instances per task
- **SC-010**: All existing Basic and Intermediate level features continue to work without modification after implementing Advanced features

### User Experience Goals

- **SC-011**: Users report that recurring tasks save them at least 5 minutes per day by eliminating manual task recreation
- **SC-012**: Users can understand the recurrence pattern of any task by reading its display information without consulting documentation
- **SC-013**: Overdue tasks are immediately visible when viewing the task list (no scrolling or filtering required)
- **SC-014**: Email reminders contain all necessary information to act on the task without opening the application

## Assumptions *(optional)*

- Users have Python 3.13+ installed and can run console applications
- Users have access to a Gmail account and can create/authorize API credentials
- Users operate in a single timezone (system local time)
- Tasks are managed by a single user (no multi-user collaboration)
- The application runs on the user's local machine with file system access
- Users are comfortable with command-line interfaces enhanced with Rich formatting
- Internet connectivity is available for Gmail API operations (graceful degradation when offline)
- The JSON data file size remains manageable (under 10MB for typical usage)

## Dependencies *(optional)*

### Internal Dependencies
- Feature 001 (Basic Level): Add, Delete, Update, View, Mark Complete functionality
- Feature 002 (Intermediate Level): Priorities, Tags/Categories, Search, Filter, Sort functionality
- Existing JSON data structure and file storage mechanism
- Rich library integration for CLI formatting

### External Dependencies
- Gmail API Python library (google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client)
- OAuth2 authentication flow for Gmail API access
- Google Cloud Console project with Gmail API enabled
- User's Gmail account with API access permissions

### Technical Dependencies
- Python datetime and timezone handling libraries (datetime, pytz, or zoneinfo)
- Flexible date parsing library (python-dateutil or similar) for accepting multiple date/time input formats
- JSON serialization/deserialization for complex date/time objects
- File locking mechanism for concurrent access protection (if needed)
- Background daemon/service implementation for reminder checking (separate process management)
- Environment variable management library (python-dotenv) for .env file handling

## Out of Scope *(optional)*

- Web or mobile user interface (Phase I is console-only)
- Multi-user collaboration or task sharing
- Calendar integration (Google Calendar, Outlook, etc.)
- Advanced recurrence patterns (e.g., "every 2nd Tuesday", "last day of month")
- Custom reminder messages or templates
- SMS or push notification reminders (email only)
- Task dependencies or subtasks
- Time tracking or task duration estimation
- Attachment support for tasks
- Natural language date parsing (e.g., "tomorrow", "next Friday")
- Timezone conversion or multi-timezone support
- Offline reminder queuing (reminders only sent when online)
- Reminder snooze functionality
- Task delegation or assignment to others

## Risks & Mitigations *(optional)*

### Risk 1: Gmail API Quota Limits
**Impact**: Users may hit daily sending limits for Gmail API, preventing reminders from being sent.

**Mitigation**:
- Document Gmail API quota limits clearly in README
- Implement rate limiting to prevent excessive API calls
- Provide clear error messages when quota is exceeded
- Consider batching reminders to reduce API calls

### Risk 2: OAuth2 Authentication Complexity
**Impact**: Users may struggle with Gmail API setup and OAuth2 authentication flow.

**Mitigation**:
- Provide detailed step-by-step setup instructions with screenshots
- Implement clear error messages for authentication failures
- Allow the application to work fully without Gmail integration (reminders are optional)
- Consider providing a setup wizard or helper script

### Risk 3: Recurring Task Data Corruption
**Impact**: Bugs in recurring task logic could create duplicate tasks or lose completion history.

**Mitigation**:
- Implement comprehensive unit tests for recurring task creation logic
- Add data validation and integrity checks on JSON file load
- Maintain backup of JSON file before modifications
- Log all recurring task operations for debugging

### Risk 4: Timezone Confusion
**Impact**: Users may be confused by due dates/times displayed in different timezones or daylight saving time changes.

**Mitigation**:
- Always display timezone information with dates/times
- Store all dates in UTC internally
- Document timezone behavior clearly
- Test thoroughly around daylight saving time transitions

### Risk 5: Performance Degradation with Many Tasks
**Impact**: Checking for due reminders every minute could slow down the application with hundreds of tasks.

**Mitigation**:
- Implement efficient indexing for due dates and reminder times
- Only check tasks with future reminders (skip completed tasks)
- Consider background process or separate reminder service for large task lists
- Set reasonable limits and document performance characteristics

## Notes *(optional)*

- This feature significantly increases the complexity of Ticklisto by adding time-based functionality and external API integration
- The Gmail API integration is optional - all other features should work without it
- Consider creating a separate configuration file for Gmail credentials rather than storing in the main JSON data file
- The recurrence logic should be thoroughly tested with edge cases (month boundaries, leap years, etc.)
- Future enhancements could include more sophisticated recurrence patterns, calendar integration, and alternative notification channels
- The implementation should maintain the clean separation between data storage, business logic, and UI presentation established in previous features
