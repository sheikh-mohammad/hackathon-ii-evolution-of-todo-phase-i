# Reminder Service Architecture Design

**Feature**: Datetime Reminders with Email/SMS Notifications
**Version**: 1.0
**Date**: 2026-02-04
**Status**: Planning

---

## Executive Summary

This document describes the architecture for adding advanced reminder capabilities to Ticklisto, including:
- Full datetime support (date + time)
- Email notifications via SendGrid
- SMS notifications via Twilio
- Background daemon service for monitoring tasks
- Multiple reminder timings (before, at, and after due time)

---

## Current Architecture

### Application Structure
```
src/ticklisto/
├── cli/ticklisto_cli.py          # Main CLI loop (synchronous, blocking)
├── models/task.py                # Task model with due_date (datetime)
├── services/
│   ├── task_service.py           # CRUD operations
│   ├── storage_service.py        # JSON persistence
│   └── notification_manager.py   # UI notifications (console only)
└── utils/date_parser.py          # Date parsing (no time support)
```

### Current Limitations
1. **No time component** - Only dates supported, no specific times
2. **No external notifications** - Console-only notifications
3. **No background monitoring** - CLI must be running
4. **No configuration management** - No .env or settings system
5. **Synchronous architecture** - Blocking CLI loop

---

## Proposed Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Ticklisto CLI                            │
│  - Add/Update tasks with datetime                           │
│  - Daemon management commands                               │
│  - Display tasks with time                                  │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Reads/Writes
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  ticklisto_data.json                         │
│  - Tasks with due_date (datetime)                           │
│  - Reminder records (sent notifications)                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Monitors
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Reminder Daemon (Background Process)            │
│  - Periodic task checking (every 15 min)                    │
│  - Reminder logic (before/at/after due time)                │
│  - Duplicate prevention                                     │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Sends via
                           ▼
┌──────────────────────────┬──────────────────────────────────┐
│   SendGrid API           │      Twilio API                  │
│   (Email Notifications)  │      (SMS Notifications)         │
└──────────────────────────┴──────────────────────────────────┘
```

### Component Architecture

```
src/ticklisto/
├── cli/
│   └── ticklisto_cli.py              # Enhanced with daemon commands
├── config/
│   ├── __init__.py
│   └── settings.py                   # Configuration loader (.env)
├── daemon/
│   ├── __init__.py
│   ├── reminder_daemon.py            # Main daemon loop
│   ├── reminder_service.py           # Reminder checking logic
│   └── notification_sender.py        # Email/SMS sending
├── models/
│   ├── task.py                       # Existing task model
│   └── reminder.py                   # NEW: Reminder record model
├── services/
│   ├── storage_service.py            # Enhanced with reminder_records
│   └── [other services]
├── utils/
│   └── date_parser.py                # Enhanced with time parsing
└── __main_daemon__.py                # Daemon entry point
```

---

## Key Design Decisions

### 1. Separate Daemon Process (Not Threading)

**Decision**: Use independent background daemon process

**Rationale**:
- ✅ Daemon runs even when CLI is closed
- ✅ No thread safety concerns with file I/O
- ✅ Clean separation of concerns
- ✅ Easier to manage lifecycle (start/stop/restart)

**Alternative Considered**: Threading within CLI
- ❌ Daemon stops when CLI exits
- ❌ Thread safety issues with JSON file access
- ❌ Complicates CLI architecture

### 2. Configuration Management

**Decision**: Use `.env` file with `python-dotenv`

**Rationale**:
- ✅ Industry standard for configuration
- ✅ Keeps secrets out of code
- ✅ Easy to modify without code changes
- ✅ Already in `.gitignore`

**Configuration Structure**:
```python
@dataclass
class EmailConfig:
    enabled: bool
    api_key: str
    sender_email: str
    recipient_email: str

@dataclass
class SMSConfig:
    enabled: bool
    account_sid: str
    auth_token: str
    from_number: str
    to_number: str

@dataclass
class ReminderConfig:
    enabled: bool
    check_interval_minutes: int
    advance_notice_minutes: list[int]
    overdue_check_minutes: list[int]
```

### 3. Notification Providers

**Email**: SendGrid API
- Simple REST API
- Free tier: 100 emails/day
- Well-documented Python SDK
- Industry standard

**SMS**: Twilio API
- Industry standard for SMS
- Free trial credits available
- Reliable delivery
- Global coverage

### 4. Reminder Timing Logic

**Three Reminder Types**:

1. **Before Due** (Advance Notice)
   - Configurable: e.g., 30 minutes, 60 minutes before
   - Helps users prepare for upcoming tasks

2. **At Due** (Exact Time)
   - Sent when task is due (within 1-minute window)
   - Critical notification

3. **After Due** (Overdue)
   - Periodic reminders: e.g., 1 hour, 2 hours after
   - Continues until task is completed
   - Prevents forgotten tasks

**Duplicate Prevention**:
- Track sent reminders in `reminder_records`
- Store: task_id, reminder_type, sent_at
- Check before sending each reminder

### 5. Datetime Support

**Decision**: Extend existing date parser to support time

**Supported Formats**:
- Standard with time: `"YYYY-MM-DD HH:MM"`, `"MM/DD/YYYY HH:MM"`
- Natural language: `"tomorrow at 3pm"`, `"next week at 2:30pm"`
- Time only: `"at 3pm"` (assumes today)
- Date only: `"tomorrow"` (defaults to 23:59 end of day)

**Backward Compatibility**:
- Existing date-only tasks remain valid
- Date-only input defaults to 23:59 (end of day)
- `parse_flexible_date()` kept for compatibility

---

## Data Models

### Task Model (Enhanced)
```python
@dataclass
class Task:
    id: int
    title: str
    description: str
    completed: bool
    priority: Priority
    categories: list[str]
    due_date: Optional[datetime]  # Now includes time
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
```

### Reminder Record Model (NEW)
```python
class ReminderType(Enum):
    ADVANCE_30MIN = "advance_30min"
    ADVANCE_60MIN = "advance_60min"
    AT_DUE_TIME = "at_due_time"
    OVERDUE_60MIN = "overdue_60min"
    OVERDUE_120MIN = "overdue_120min"

@dataclass
class ReminderRecord:
    task_id: int
    reminder_type: ReminderType
    sent_at: datetime
```

### Storage Structure (Enhanced)
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Team meeting",
      "due_date": "2026-02-15T14:30:00",
      ...
    }
  ],
  "next_id": 2,
  "reminder_records": [
    {
      "task_id": 1,
      "reminder_type": "advance_30min",
      "sent_at": "2026-02-15T14:00:00"
    }
  ]
}
```

---

## Daemon Lifecycle

### Process Management

**PID File**: `.ticklisto_daemon.pid`
- Stores daemon process ID
- Used for stop/status commands
- Cleaned up on graceful shutdown

**Signals**:
- `SIGINT` (Ctrl+C): Graceful shutdown
- `SIGTERM`: Graceful shutdown
- Cleanup: Close connections, save state

### Daemon Loop

```python
def start(self):
    self.running = True

    # Schedule periodic checks
    schedule.every(check_interval).minutes.do(self.check_reminders)

    # Main loop
    while self.running:
        schedule.run_pending()
        time.sleep(1)

def check_reminders(self):
    # Load tasks from JSON
    tasks = self.storage.load_tasks()
    sent_reminders = self.storage.load_reminder_records()

    # Check which reminders to send
    reminders_to_send = self.reminder_service.check_tasks(
        tasks, sent_reminders
    )

    # Send reminders
    for task, reminder_type in reminders_to_send:
        success = self.notification_sender.send(task, reminder_type)
        if success:
            self.storage.save_reminder_record(task.id, reminder_type)
```

---

## Reminder Logic Algorithm

```python
def check_tasks_for_reminders(tasks, sent_reminders):
    now = datetime.now()
    reminders_to_send = []

    for task in tasks:
        if task.completed or not task.due_date:
            continue

        # Check advance notices (before due time)
        for minutes in advance_notice_minutes:
            reminder_time = task.due_date - timedelta(minutes=minutes)
            reminder_type = get_advance_type(minutes)

            if now >= reminder_time and not was_sent(task.id, reminder_type):
                reminders_to_send.append((task, reminder_type))

        # Check at due time
        if now >= task.due_date and not was_sent(task.id, AT_DUE_TIME):
            reminders_to_send.append((task, AT_DUE_TIME))

        # Check overdue reminders (after due time)
        if now > task.due_date:
            for minutes in overdue_check_minutes:
                overdue_time = task.due_date + timedelta(minutes=minutes)
                reminder_type = get_overdue_type(minutes)

                if now >= overdue_time and not was_sent(task.id, reminder_type):
                    reminders_to_send.append((task, reminder_type))

    return reminders_to_send
```

---

## Security Considerations

### API Credentials
- **Storage**: `.env` file (never committed to git)
- **Access**: Read-only by daemon process
- **Validation**: Check credentials on daemon start
- **Documentation**: Clear setup instructions in `.env.example`

### File Access
- **JSON File**: Atomic read/write operations
- **PID File**: Proper cleanup on shutdown
- **Permissions**: Standard user permissions

### Rate Limiting
- **SendGrid**: 100 emails/day (free tier)
- **Twilio**: Pay-per-message (monitor usage)
- **Implementation**: Track sent notifications to prevent spam

---

## Error Handling

### Daemon Errors
- **API Failures**: Log error, continue checking other tasks
- **File Read Errors**: Retry with exponential backoff
- **Configuration Errors**: Fail fast on startup

### Notification Errors
- **Email Send Failure**: Log error, mark as failed (don't retry immediately)
- **SMS Send Failure**: Log error, mark as failed
- **Network Errors**: Retry once, then log and continue

### Recovery Strategy
- **Daemon Crash**: User must manually restart
- **Missed Reminders**: Next check cycle will catch them
- **Duplicate Prevention**: Reminder records prevent re-sending

---

## Performance Considerations

### Check Interval
- **Default**: 15 minutes
- **Configurable**: Via `.env` file
- **Trade-off**: Shorter interval = more accurate, higher CPU usage

### File I/O
- **Read Frequency**: Every check interval (15 min)
- **Write Frequency**: Only when sending reminders
- **Optimization**: Atomic operations, minimal locking

### Memory Usage
- **Task List**: Loaded into memory each check
- **Reminder Records**: Loaded into memory each check
- **Cleanup**: Old reminder records can be purged periodically

---

## Testing Strategy

### Unit Tests
- Date/time parsing (all formats)
- Reminder logic (before/at/after)
- Duplicate prevention
- Configuration loading
- Notification formatting

### Integration Tests
- Daemon lifecycle (start/stop/restart)
- End-to-end reminder flow (mock APIs)
- File I/O operations
- Error recovery

### Manual Testing
- Real email sending (SendGrid)
- Real SMS sending (Twilio)
- Daemon running for extended periods
- Multiple concurrent reminders

---

## Future Enhancements (Out of Scope)

1. **Snooze Functionality**: Delay reminders by X minutes
2. **Custom Reminder Times**: Per-task reminder schedules
3. **Recurring Tasks**: Daily/weekly/monthly tasks
4. **Multiple Recipients**: Send to multiple email/phone numbers
5. **Notification Templates**: Customizable message formats
6. **Web Dashboard**: Browser-based task management
7. **Push Notifications**: Browser push notifications
8. **Database**: Replace JSON with SQLite/PostgreSQL

---

## Dependencies

### New Dependencies
```toml
python-dotenv = ">=1.0.0"    # Configuration management
schedule = ">=1.2.0"          # Periodic task scheduling
sendgrid = ">=6.11.0"         # Email notifications
twilio = ">=9.0.0"            # SMS notifications
```

### Existing Dependencies
```toml
rich = ">=14.3.1"             # UI formatting
python-dateutil = ">=2.8.0"   # Date parsing
```

---

## Risk Analysis

### High-Impact Risks

**Risk 1: API Rate Limits**
- **Impact**: High (notifications stop working)
- **Mitigation**: Track sent count, warn user, implement rate limiting

**Risk 2: API Credentials Security**
- **Impact**: High (credential exposure)
- **Mitigation**: Never commit .env, clear documentation, validate on startup

### Medium-Impact Risks

**Risk 3: Daemon Process Management**
- **Impact**: Medium (daemon crashes or hangs)
- **Mitigation**: Robust PID handling, graceful shutdown, error recovery

**Risk 4: Time Zone Handling**
- **Impact**: Medium (wrong reminder times)
- **Mitigation**: Use timezone-aware datetimes, store in UTC, display in local

**Risk 5: File Locking**
- **Impact**: Medium (concurrent access issues)
- **Mitigation**: Atomic operations, read-only daemon access, file locking if needed

### Low-Impact Risks

**Risk 6: Missed Reminders**
- **Impact**: Low (next check cycle catches them)
- **Mitigation**: Reasonable check interval (15 min), duplicate prevention

---

## Implementation Phases

### Phase 1: Configuration Management
- Create config module
- Implement .env loading
- Add validation

### Phase 2: Datetime Support
- Extend date parser
- Update CLI prompts
- Update UI display

### Phase 3: Notification Sender
- Implement SendGrid integration
- Implement Twilio integration
- Create message templates

### Phase 4: Reminder Service Logic
- Implement reminder checking
- Add duplicate prevention
- Create reminder history

### Phase 5: Background Daemon
- Create daemon process
- Implement main loop
- Add PID management

### Phase 6: CLI Daemon Management
- Add daemon commands
- Implement process control
- Add status checking

### Phase 7: Documentation & Testing
- Write user guides
- Create setup instructions
- Add comprehensive tests

---

## Success Criteria

1. ✅ Users can enter date and time for tasks
2. ✅ Daemon runs independently in background
3. ✅ Email notifications sent via SendGrid
4. ✅ SMS notifications sent via Twilio
5. ✅ Multiple reminder timings (before/at/after)
6. ✅ No duplicate notifications
7. ✅ CLI commands to manage daemon
8. ✅ Comprehensive documentation
9. ✅ Test coverage > 85%
10. ✅ Backward compatible with existing tasks

---

## References

- [SendGrid API Documentation](https://docs.sendgrid.com/)
- [Twilio API Documentation](https://www.twilio.com/docs/)
- [python-dotenv Documentation](https://pypi.org/project/python-dotenv/)
- [schedule Library Documentation](https://schedule.readthedocs.io/)
- [dateutil Parser Documentation](https://dateutil.readthedocs.io/)

---

**Document Version**: 1.0
**Last Updated**: 2026-02-04
**Author**: Claude Sonnet 4.5
**Status**: Planning Phase
