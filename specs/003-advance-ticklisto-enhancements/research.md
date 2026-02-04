# Research & Technology Decisions

**Feature**: Advanced Ticklisto Enhancements
**Date**: 2026-02-04
**Status**: Complete

This document captures research findings and technology decisions for implementing advanced time-based task management features.

## 1. Python Daemon/Service Implementation

### Decision
Use **python-daemon** library with platform-specific service managers (systemd for Linux, launchd for macOS, Windows Task Scheduler for Windows).

### Rationale
- **python-daemon** provides robust UNIX daemon functionality with proper signal handling, PID file management, and process detachment
- Platform-specific service managers provide native auto-start on boot and crash recovery
- Separates daemon logic from service management, enabling cross-platform support
- Well-established pattern used by production Python services

### Implementation Approach
```python
# Core daemon using python-daemon
import daemon
import daemon.pidfile
import signal
import time

class ReminderDaemon:
    def __init__(self, pidfile_path):
        self.pidfile = daemon.pidfile.PIDLockFile(pidfile_path)
        self.running = True

    def run(self):
        with daemon.DaemonContext(
            pidfile=self.pidfile,
            signal_map={
                signal.SIGTERM: self.shutdown,
                signal.SIGHUP: self.reload_config
            }
        ):
            while self.running:
                self.check_reminders()
                time.sleep(60)  # Check every minute
```

**Service Installation**:
- **Linux**: systemd unit file with `Restart=always` for crash recovery
- **macOS**: launchd plist with `KeepAlive=true`
- **Windows**: Task Scheduler with "Restart on failure" action

### Alternatives Considered
- **supervisord**: Requires separate process manager installation, adds dependency
- **Custom fork/detach**: Error-prone, lacks proper signal handling and PID management
- **APScheduler**: Scheduling library, not a daemon framework

### References
- python-daemon documentation: https://pypi.org/project/python-daemon/
- systemd service best practices
- Cross-platform daemon patterns

---

## 2. Gmail API Integration Best Practices

### Decision
Use **Google's official Python client libraries** with OAuth2 flow, storing credentials in `.env` file and tokens in `~/.ticklisto/gmail_token.json` with file permissions set to 0600.

### Rationale
- Official libraries provide automatic token refresh and error handling
- OAuth2 flow is the recommended authentication method for Gmail API
- Separating credentials (.env) from tokens (user directory) follows security best practices
- File permissions (0600) restrict access to owner only
- Token refresh handled automatically by google-auth library

### Implementation Approach
```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    creds = None
    token_path = Path.home() / '.ticklisto' / 'gmail_token.json'

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv('GMAIL_CREDENTIALS_PATH'), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials with restricted permissions
        token_path.parent.mkdir(exist_ok=True)
        token_path.write_text(creds.to_json())
        token_path.chmod(0o600)

    return build('gmail', 'v1', credentials=creds)
```

**Quota Management**:
- Gmail API free tier: 1 billion quota units/day
- Sending email: 100 quota units per request
- Theoretical limit: ~10 million emails/day (far exceeds needs)
- Implement rate limiting: max 10 emails/minute to be conservative

**Error Handling**:
- 401 Unauthorized: Token expired, trigger re-authentication
- 403 Forbidden: Quota exceeded, log and retry after delay
- 429 Too Many Requests: Implement exponential backoff
- Network errors: Retry with exponential backoff (max 3 attempts)

### Alternatives Considered
- **SMTP with app passwords**: Less secure, no automatic token refresh, deprecated by Google
- **Service account**: Not supported for Gmail API (requires workspace admin)
- **Storing tokens in .env**: Security risk if .env is accidentally committed

### References
- Gmail API Python Quickstart: https://developers.google.com/gmail/api/quickstart/python
- OAuth2 best practices: https://developers.google.com/identity/protocols/oauth2
- Gmail API quotas: https://developers.google.com/gmail/api/reference/quota

---

## 3. Date/Time Parsing Library Evaluation

### Decision
Use **python-dateutil** with custom ambiguity detection wrapper.

### Rationale
- **python-dateutil** is the most mature and widely-used date parsing library in Python
- Excellent support for ISO 8601, multiple formats, and timezone handling
- Part of standard Python ecosystem (used by pandas, arrow, etc.)
- Provides `parser.parse()` with flexible format detection
- Can detect ambiguous dates by attempting multiple parse strategies

### Implementation Approach
```python
from dateutil import parser
from datetime import datetime
import re

class DateParser:
    def parse_with_ambiguity_check(self, date_string):
        """Parse date string, detecting ambiguity."""
        # Check if format is ambiguous (e.g., "02/03/2026")
        if self._is_ambiguous(date_string):
            return None, "AMBIGUOUS"

        try:
            # Try parsing with dayfirst=False (MM/DD/YYYY)
            dt = parser.parse(date_string, dayfirst=False)
            return dt, None
        except parser.ParserError as e:
            return None, str(e)

    def _is_ambiguous(self, date_string):
        """Detect ambiguous date formats."""
        # Pattern: XX/YY/ZZZZ where XX and YY are both <= 12
        pattern = r'^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$'
        match = re.match(pattern, date_string)
        if match:
            first, second, year = match.groups()
            # Ambiguous if both parts could be month or day
            if int(first) <= 12 and int(second) <= 12 and first != second:
                return True
        return False
```

**Supported Formats**:
- ISO 8601: `2026-02-04`, `2026-02-04T14:30:00`
- US format: `02/04/2026`, `2/4/2026`
- European format: `04/02/2026` (with dayfirst=True)
- Natural: `Feb 4, 2026`, `February 4, 2026`
- Time: `14:30`, `2:30 PM`, `14:30:00`

### Alternatives Considered
- **dateparser**: More features but heavier dependency, slower performance
- **arrow**: Good API but less flexible parsing than dateutil
- **Custom regex parsing**: Error-prone, doesn't handle edge cases

### References
- python-dateutil documentation: https://dateutil.readthedocs.io/
- Date parsing best practices

---

## 4. Recurrence Calculation Algorithms

### Decision
Use **dateutil.rrule** for recurrence calculations with custom wrappers for interval support and end conditions.

### Rationale
- **dateutil.rrule** implements RFC 5545 (iCalendar) recurrence rules
- Handles all edge cases: month boundaries, leap years, DST transitions
- Battle-tested in calendar applications (Google Calendar, Outlook use iCalendar format)
- Supports complex recurrence patterns with minimal code
- Provides `rrule.after()` method for calculating next occurrence

### Implementation Approach
```python
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY
from datetime import datetime

class RecurrenceCalculator:
    FREQ_MAP = {
        'daily': DAILY,
        'weekly': WEEKLY,
        'monthly': MONTHLY,
        'yearly': YEARLY
    }

    def calculate_next_occurrence(self, task):
        """Calculate next occurrence for recurring task."""
        freq = self.FREQ_MAP[task.recurrence_pattern.pattern_type]
        interval = task.recurrence_pattern.interval or 1

        rule = rrule(
            freq=freq,
            interval=interval,
            dtstart=task.due_date,
            count=task.recurrence_pattern.occurrences_count,
            until=task.recurrence_pattern.end_date,
            byweekday=task.recurrence_pattern.weekdays  # For weekly
        )

        # Get next occurrence after current due date
        next_date = rule.after(task.due_date)
        return next_date
```

**Edge Case Handling**:
- **Monthly on day 31**: rrule automatically adjusts to last day of month
- **Leap years**: rrule handles Feb 29 correctly
- **DST transitions**: rrule preserves local time across DST changes
- **End conditions**: rrule supports both `count` and `until` parameters

### Alternatives Considered
- **Custom date arithmetic**: Error-prone, doesn't handle edge cases
- **APScheduler**: Scheduling library, not a recurrence calculator
- **Manual calculation with relativedelta**: More code, less reliable

### References
- RFC 5545 (iCalendar): https://tools.ietf.org/html/rfc5545
- dateutil.rrule documentation: https://dateutil.readthedocs.io/en/stable/rrule.html

---

## 5. File Locking Mechanisms

### Decision
Use **portalocker** for cross-platform file locking.

### Rationale
- **portalocker** provides cross-platform file locking (Windows, Linux, macOS)
- Uses native OS locking mechanisms (fcntl on Unix, msvcrt on Windows)
- Simple API with context manager support
- Handles lock acquisition timeout and retry logic
- Prevents concurrent access corruption in JSON file

### Implementation Approach
```python
import portalocker
import json
from pathlib import Path

class LockedJSONStorage:
    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def read(self):
        """Read JSON with exclusive lock."""
        with portalocker.Lock(self.file_path, 'r', timeout=5) as f:
            return json.load(f)

    def write(self, data):
        """Write JSON with exclusive lock."""
        # Create backup before writing
        if self.file_path.exists():
            backup_path = self.file_path.with_suffix('.json.bak')
            self.file_path.replace(backup_path)

        with portalocker.Lock(self.file_path, 'w', timeout=5) as f:
            json.dump(data, f, indent=2)
```

**Lock Strategy**:
- **Read operations**: Shared lock (multiple readers allowed)
- **Write operations**: Exclusive lock (no other access allowed)
- **Timeout**: 5 seconds (prevents deadlock)
- **Backup**: Create backup before write (recovery on corruption)

### Alternatives Considered
- **fcntl (Unix only)**: Not cross-platform
- **filelock**: Similar to portalocker but less mature
- **Database with transactions**: Overkill for Phase I JSON storage

### References
- portalocker documentation: https://pypi.org/project/portalocker/
- File locking best practices

---

## 6. JSON Schema Validation

### Decision
Use **Pydantic** for data validation and serialization.

### Rationale
- **Pydantic** provides runtime type checking and validation
- Excellent JSON serialization/deserialization support
- Clear error messages for validation failures
- Supports optional fields and default values (backward compatibility)
- Type hints improve code quality and IDE support
- Can generate JSON schema for documentation

### Implementation Approach
```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class RecurrenceType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    NONE = "none"

class RecurrencePattern(BaseModel):
    pattern_type: RecurrenceType
    interval: int = Field(default=1, ge=1)
    weekdays: Optional[List[int]] = None  # 0=Monday, 6=Sunday
    end_date: Optional[datetime] = None
    occurrences_count: Optional[int] = Field(default=None, ge=1)

    @validator('interval')
    def validate_interval(cls, v, values):
        """Enforce interval limits based on pattern type."""
        pattern = values.get('pattern_type')
        limits = {
            RecurrenceType.DAILY: 365,
            RecurrenceType.WEEKLY: 52,
            RecurrenceType.MONTHLY: 24,
            RecurrenceType.YEARLY: 10
        }
        if pattern and v > limits.get(pattern, 365):
            raise ValueError(f"Interval {v} exceeds limit for {pattern}")
        return v

class Task(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: str = "incomplete"
    priority: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePattern] = None
    is_recurring: bool = False
    parent_task_id: Optional[str] = None
    completion_history: List[datetime] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Backward Compatibility**:
- All new fields are optional with defaults
- Existing tasks without due_date/recurrence will load successfully
- Pydantic handles missing fields gracefully

### Alternatives Considered
- **jsonschema**: More verbose, less Pythonic, no type hints
- **marshmallow**: Good but more boilerplate than Pydantic
- **Manual validation**: Error-prone, no type safety

### References
- Pydantic documentation: https://docs.pydantic.dev/
- JSON Schema specification: https://json-schema.org/

---

## Summary of Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Daemon Service | python-daemon + systemd/launchd/Task Scheduler | Cross-platform, robust, native auto-start |
| Gmail API | google-api-python-client | Official library, automatic token refresh |
| Date Parsing | python-dateutil | Mature, flexible, handles ambiguity |
| Recurrence | dateutil.rrule | RFC 5545 compliant, handles edge cases |
| File Locking | portalocker | Cross-platform, simple API |
| Validation | Pydantic | Type-safe, excellent JSON support |

## Next Steps

Phase 1 will use these technology decisions to:
1. Create detailed data model (data-model.md)
2. Generate JSON schema contracts (contracts/)
3. Write quickstart guide (quickstart.md)
4. Update agent context with new technologies
