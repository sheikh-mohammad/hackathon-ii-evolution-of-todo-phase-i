# Data Model: Advanced Ticklisto Enhancements

**Feature**: Advanced Ticklisto Enhancements
**Date**: 2026-02-04
**Status**: Complete

This document defines the data model for advanced time-based task management features, including entities, attributes, relationships, validation rules, and state transitions.

## Entity Overview

```
┌─────────────────┐
│      Task       │
│  (Enhanced)     │
└────────┬────────┘
         │
         │ 1:N
         ├──────────────┐
         │              │
         ▼              ▼
┌─────────────────┐  ┌─────────────────┐
│  Reminder       │  │ RecurrencePattern│
│                 │  │                 │
└─────────────────┘  └─────────────────┘

┌─────────────────┐
│  GmailConfig    │
│  (Singleton)    │
└─────────────────┘
```

## Entity Definitions

### 1. Task (Enhanced)

**Description**: Represents a single task or to-do item with optional due dates, recurrence, and reminders.

**Attributes**:

| Field | Type | Required | Default | Validation | Description |
|-------|------|----------|---------|------------|-------------|
| `id` | string (UUID) | Yes | Generated | Unique | Task identifier |
| `title` | string | Yes | - | 1-200 chars | Task title |
| `description` | string | No | null | 0-2000 chars | Task description |
| `status` | enum | Yes | "incomplete" | "incomplete" \| "complete" | Task completion status |
| `priority` | enum | No | null | "high" \| "medium" \| "low" | Task priority (from Feature 002) |
| `tags` | array[string] | No | [] | Each tag 1-50 chars | Task categories (from Feature 002) |
| `due_date` | datetime (ISO 8601) | No | null | Valid datetime in UTC | When task is due |
| `recurrence_pattern` | RecurrencePattern | No | null | Valid pattern if is_recurring=true | How task repeats |
| `is_recurring` | boolean | Yes | false | - | Whether task recurs |
| `parent_task_id` | string (UUID) | No | null | Valid task ID or null | Original task for recurring instances |
| `completion_history` | array[datetime] | No | [] | ISO 8601 datetimes | When each instance was completed |
| `reminders` | array[Reminder] | No | [] | Valid reminder objects | Scheduled reminders |
| `created_at` | datetime (ISO 8601) | Yes | Now (UTC) | Valid datetime | When task was created |
| `updated_at` | datetime (ISO 8601) | Yes | Now (UTC) | Valid datetime | When task was last modified |

**Validation Rules**:
- If `is_recurring` is true, `due_date` MUST be set (FR-012)
- If `is_recurring` is true, `recurrence_pattern` MUST be set
- If `parent_task_id` is set, task is a recurring instance
- `completion_history` only populated for recurring tasks
- `reminders` can only be set if `due_date` is set

**State Transitions**:
```
┌──────────────┐
│  incomplete  │
└──────┬───────┘
       │ mark_complete()
       ▼
┌──────────────┐
│   complete   │
└──────┬───────┘
       │ mark_incomplete()
       ▼
┌──────────────┐
│  incomplete  │
└──────────────┘

Special case for recurring tasks:
┌──────────────┐
│  incomplete  │
│ (recurring)  │
└──────┬───────┘
       │ mark_complete()
       ├─────────────────────┐
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│   complete   │      │  incomplete  │
│  (current)   │      │   (new)      │
└──────────────┘      └──────────────┘
                      New instance created
                      with next due_date
```

**Lifecycle**:
1. **Creation**: Task created with optional due_date and recurrence_pattern
2. **Active**: Task exists with status="incomplete"
3. **Completion**:
   - Non-recurring: Status set to "complete", updated_at set
   - Recurring: Current instance marked complete, new instance created with next due_date
4. **Deletion**:
   - Non-recurring: Task removed from storage
   - Recurring: User chooses to delete current instance or all future instances

**Backward Compatibility**:
- All new fields are optional
- Existing tasks without due_date/recurrence load successfully
- Default values ensure compatibility

---

### 2. RecurrencePattern

**Description**: Defines how a recurring task repeats.

**Attributes**:

| Field | Type | Required | Default | Validation | Description |
|-------|------|----------|---------|------------|-------------|
| `pattern_type` | enum | Yes | - | "daily" \| "weekly" \| "monthly" \| "yearly" | Recurrence frequency |
| `interval` | integer | Yes | 1 | 1-365 (daily), 1-52 (weekly), 1-24 (monthly), 1-10 (yearly) | Repeat every N units |
| `weekdays` | array[integer] | No | null | 0-6 (0=Monday, 6=Sunday) | Days of week for weekly recurrence |
| `end_date` | datetime (ISO 8601) | No | null | Valid datetime >= task.due_date | When recurrence stops |
| `occurrences_count` | integer | No | null | >= 1 | Number of occurrences before stopping |

**Validation Rules**:
- `interval` limits enforced based on `pattern_type` (FR-011a)
- For `pattern_type="weekly"`, `weekdays` MUST be set and non-empty
- Either `end_date` OR `occurrences_count` OR neither (infinite), but not both
- If `end_date` is set, it must be >= task's `due_date`
- `weekdays` only valid for `pattern_type="weekly"`

**Examples**:
```json
// Daily, every 2 days, 10 occurrences
{
  "pattern_type": "daily",
  "interval": 2,
  "occurrences_count": 10
}

// Weekly, every Monday and Friday
{
  "pattern_type": "weekly",
  "interval": 1,
  "weekdays": [0, 4]
}

// Monthly, every 3 months, until end of year
{
  "pattern_type": "monthly",
  "interval": 3,
  "end_date": "2026-12-31T23:59:59Z"
}

// Yearly, every year, indefinitely
{
  "pattern_type": "yearly",
  "interval": 1
}
```

**Edge Case Handling**:
- **Monthly on day 29-31**: Use last day of month if day doesn't exist (FR-021)
- **Leap years**: Feb 29 handled correctly by dateutil.rrule
- **DST transitions**: Local time preserved across transitions

---

### 3. Reminder

**Description**: Represents a scheduled reminder for a task.

**Attributes**:

| Field | Type | Required | Default | Validation | Description |
|-------|------|----------|---------|------------|-------------|
| `id` | string (UUID) | Yes | Generated | Unique | Reminder identifier |
| `task_id` | string (UUID) | Yes | - | Valid task ID | Associated task |
| `reminder_time` | datetime (ISO 8601) | Yes | - | Valid datetime in UTC | When to send reminder |
| `offset_from_due` | string | Yes | - | Valid offset (e.g., "-1h", "-1d") | Time before due date |
| `status` | enum | Yes | "pending" | "pending" \| "sent" \| "failed" | Reminder status |
| `sent_at` | datetime (ISO 8601) | No | null | Valid datetime | When reminder was sent |
| `error_message` | string | No | null | 0-500 chars | Error if sending failed |
| `retry_count` | integer | Yes | 0 | 0-1 | Number of retry attempts |

**Validation Rules**:
- `reminder_time` must be < task's `due_date`
- `offset_from_due` format: `-{number}{unit}` where unit is m (minutes), h (hours), d (days), w (weeks)
- `status="sent"` requires `sent_at` to be set
- `status="failed"` requires `error_message` to be set
- `retry_count` max is 1 (FR-031)

**State Transitions**:
```
┌──────────────┐
│   pending    │
└──────┬───────┘
       │ reminder_time reached
       ▼
┌──────────────┐
│   sending    │
└──────┬───────┘
       │
       ├─────────────┐
       │ success     │ failure
       ▼             ▼
┌──────────────┐  ┌──────────────┐
│     sent     │  │    failed    │
└──────────────┘  └──────┬───────┘
                         │ retry_count < 1
                         ▼
                  ┌──────────────┐
                  │   pending    │
                  │ (retry in 5m)│
                  └──────────────┘
```

**Predefined Offset Options**:
- "15m" - 15 minutes before
- "30m" - 30 minutes before
- "1h" - 1 hour before
- "2h" - 2 hours before
- "1d" - 1 day before
- "1w" - 1 week before
- Custom: User can enter any valid offset

---

### 4. GmailConfig

**Description**: Stores Gmail API configuration (singleton, one per user).

**Attributes**:

| Field | Type | Required | Default | Validation | Description |
|-------|------|----------|---------|------------|-------------|
| `user_email` | string | Yes | - | Valid email format | User's email address |
| `credentials_path` | string | Yes | - | Valid file path | Path to OAuth2 credentials JSON |
| `token_path` | string | Yes | - | Valid file path | Path to stored access token |
| `enabled` | boolean | Yes | false | - | Whether reminders are enabled |
| `last_auth_at` | datetime (ISO 8601) | No | null | Valid datetime | When last authenticated |
| `quota_remaining` | integer | No | null | >= 0 | Remaining API quota (if tracked) |

**Validation Rules**:
- `credentials_path` must point to valid OAuth2 credentials file
- `token_path` directory must be writable
- `user_email` must match email in OAuth2 credentials

**Storage Location**:
- Configuration stored in `.env` file (FR-021)
- Token stored in `~/.ticklisto/gmail_token.json` with 0600 permissions
- Credentials file path referenced in `.env`, actual file excluded via .gitignore

**Example .env**:
```
GMAIL_USER_EMAIL=user@example.com
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOKEN_PATH=/home/user/.ticklisto/gmail_token.json
GMAIL_ENABLED=true
```

---

## Relationships

### Task → RecurrencePattern (1:1, optional)
- A task MAY have one recurrence pattern
- Recurrence pattern is embedded in task document
- If task is recurring, pattern MUST be present

### Task → Task (1:N, parent-child)
- A recurring task MAY have multiple child instances
- Child instances reference parent via `parent_task_id`
- Parent task is the original recurring task definition

### Task → Reminder (1:N)
- A task MAY have multiple reminders
- Reminders are embedded in task document
- Reminders only valid if task has `due_date`

### GmailConfig (Singleton)
- Only one configuration per user
- Stored separately from tasks
- Referenced by reminder service

---

## JSON Storage Schema

### File Structure
```json
{
  "version": "3.0.0",
  "tasks": [
    {
      "id": "uuid",
      "title": "string",
      "description": "string | null",
      "status": "incomplete | complete",
      "priority": "high | medium | low | null",
      "tags": ["string"],
      "due_date": "ISO 8601 datetime | null",
      "recurrence_pattern": {
        "pattern_type": "daily | weekly | monthly | yearly",
        "interval": 1,
        "weekdays": [0, 1, 2, 3, 4, 5, 6] | null,
        "end_date": "ISO 8601 datetime | null",
        "occurrences_count": 10 | null
      } | null,
      "is_recurring": false,
      "parent_task_id": "uuid | null",
      "completion_history": ["ISO 8601 datetime"],
      "reminders": [
        {
          "id": "uuid",
          "task_id": "uuid",
          "reminder_time": "ISO 8601 datetime",
          "offset_from_due": "-1h",
          "status": "pending | sent | failed",
          "sent_at": "ISO 8601 datetime | null",
          "error_message": "string | null",
          "retry_count": 0
        }
      ],
      "created_at": "ISO 8601 datetime",
      "updated_at": "ISO 8601 datetime"
    }
  ],
  "gmail_config": {
    "user_email": "user@example.com",
    "credentials_path": "/path/to/credentials.json",
    "token_path": "/home/user/.ticklisto/gmail_token.json",
    "enabled": true,
    "last_auth_at": "ISO 8601 datetime | null",
    "quota_remaining": 1000000 | null
  }
}
```

### Migration from v2.0.0 to v3.0.0
- Add `due_date`, `recurrence_pattern`, `is_recurring`, `parent_task_id`, `completion_history`, `reminders` fields to existing tasks
- All new fields default to null/false/[]
- Existing tasks remain valid without modification
- Add `gmail_config` object at root level

---

## Indexes and Query Patterns

### Common Queries
1. **Get tasks due today**: Filter by `due_date` between start and end of today
2. **Get overdue tasks**: Filter by `due_date` < now AND `status` = "incomplete"
3. **Get recurring tasks**: Filter by `is_recurring` = true
4. **Get pending reminders**: Filter reminders by `status` = "pending" AND `reminder_time` <= now
5. **Get task completion history**: Access `completion_history` array for recurring tasks

### Performance Considerations
- For 100+ tasks, consider in-memory indexing by due_date
- Daemon service maintains separate index of pending reminders
- Completion history limited to 100 entries per task (configurable)

---

## Validation Summary

| Entity | Validation Library | Schema Location |
|--------|-------------------|-----------------|
| Task | Pydantic | `contracts/task-schema.json` |
| RecurrencePattern | Pydantic | `contracts/recurrence-schema.json` |
| Reminder | Pydantic | `contracts/reminder-schema.json` |
| GmailConfig | Pydantic | `contracts/gmail-config-schema.json` |

All entities use Pydantic for runtime validation with JSON schema generation for documentation.
