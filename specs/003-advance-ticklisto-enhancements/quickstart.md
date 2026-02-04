# Quickstart Guide: Advanced Ticklisto Features

**Feature**: Advanced Ticklisto Enhancements
**Version**: 3.0.0
**Date**: 2026-02-04

This guide helps you get started with advanced time-based task management features including due dates, recurring tasks, and email reminders.

## Prerequisites

- Python 3.13+ installed
- UV package manager installed
- Ticklisto Basic and Intermediate features working (Features 001 & 002)
- Gmail account (optional, for email reminders)

## Installation

### 1. Install Dependencies

```bash
# Install new dependencies
uv add python-dateutil python-dotenv pydantic portalocker
uv add google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
uv add python-daemon  # For reminder daemon service
```

### 2. Configure Environment (Optional - for Email Reminders)

Create a `.env` file in the project root:

```bash
# Copy example configuration
cp config/.env.example .env

# Edit .env with your settings
GMAIL_USER_EMAIL=your-email@gmail.com
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOKEN_PATH=/home/user/.ticklisto/gmail_token.json
GMAIL_ENABLED=true
```

### 3. Set Up Gmail API (Optional - for Email Reminders)

If you want email reminders:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API for the project
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials JSON file
6. Update `GMAIL_CREDENTIALS_PATH` in `.env` to point to the file
7. Run first-time authentication:

```bash
python -m ticklisto auth gmail
```

This will open a browser for OAuth2 authorization. After authorization, a token will be saved to `~/.ticklisto/gmail_token.json`.

### 4. Install Reminder Daemon (Optional - for Email Reminders)

To enable automatic email reminders:

**Linux (systemd)**:
```bash
sudo python daemon/install_service.py --install
sudo systemctl enable ticklisto-daemon
sudo systemctl start ticklisto-daemon
```

**macOS (launchd)**:
```bash
python daemon/install_service.py --install
launchctl load ~/Library/LaunchAgents/com.ticklisto.daemon.plist
```

**Windows (Task Scheduler)**:
```bash
python daemon/install_service.py --install
# Follow prompts to configure Task Scheduler
```

## Quick Start Examples

### Example 1: Create Task with Due Date

```bash
# Create task due tomorrow at 2 PM
ticklisto add "Submit report" --due "2026-02-05 14:00"

# Create task due in 3 days
ticklisto add "Call client" --due "2026-02-07"

# System will prompt if date format is ambiguous
ticklisto add "Review document" --due "02/05/2026"
# Prompt: "Did you mean February 5 or May 2? (1/2)"
```

### Example 2: Create Recurring Task

```bash
# Daily standup at 9 AM
ticklisto add "Daily standup" --due "2026-02-05 09:00" --recur daily

# Weekly team meeting every Monday at 2 PM
ticklisto add "Team meeting" --due "2026-02-05 14:00" --recur weekly --weekdays Mon

# Monthly report on the 1st of each month
ticklisto add "Monthly report" --due "2026-03-01" --recur monthly

# Bi-weekly sprint planning (every 2 weeks)
ticklisto add "Sprint planning" --due "2026-02-05 10:00" --recur weekly --interval 2 --weekdays Mon
```

### Example 3: Create Recurring Task with End Condition

```bash
# Daily task for 30 days
ticklisto add "Morning exercise" --due "2026-02-05 07:00" --recur daily --count 30

# Weekly task until end of year
ticklisto add "Weekly review" --due "2026-02-05 17:00" --recur weekly --until "2026-12-31"
```

### Example 4: Add Reminders to Task

```bash
# Add task with reminder 1 hour before
ticklisto add "Doctor appointment" --due "2026-02-10 14:00" --remind "1h"

# Add multiple reminders
ticklisto add "Important meeting" --due "2026-02-08 10:00" --remind "1d,1h"

# Use predefined reminder options
ticklisto add "Flight departure" --due "2026-02-15 18:00" --remind "1d,2h,30m"

# Custom reminder offset
ticklisto add "Project deadline" --due "2026-02-20 17:00" --remind "3d"
```

### Example 5: View Tasks by Due Date

```bash
# View all tasks due today
ticklisto list --due today

# View overdue tasks
ticklisto list --overdue

# View tasks due this week
ticklisto list --due week

# View upcoming tasks (next 7 days)
ticklisto list --upcoming

# Sort all tasks by due date
ticklisto list --sort due
```

### Example 6: View Recurring Tasks

```bash
# List all recurring tasks
ticklisto list --recurring

# Show next 5 occurrences of a recurring task
ticklisto show <task-id> --occurrences 5

# View completion history
ticklisto show <task-id> --history
```

### Example 7: Manage Recurring Task Instances

```bash
# Complete current instance (creates next instance automatically)
ticklisto complete <task-id>

# Delete only current instance
ticklisto delete <task-id> --instance

# Delete all future instances
ticklisto delete <task-id> --all-future

# Update recurrence pattern
ticklisto update <task-id> --recur weekly --weekdays Mon,Wed,Fri
```

### Example 8: Manage Reminder Daemon

```bash
# Check daemon status
ticklisto daemon status

# Start daemon manually
ticklisto daemon start

# Stop daemon
ticklisto daemon stop

# Restart daemon
ticklisto daemon restart

# View daemon logs
ticklisto daemon logs
```

## Common Workflows

### Workflow 1: Setting Up a New Recurring Task

1. Create task with due date and recurrence:
   ```bash
   ticklisto add "Weekly backup" --due "2026-02-05 23:00" --recur weekly --weekdays Fri
   ```

2. Add reminder:
   ```bash
   ticklisto update <task-id> --remind "1h"
   ```

3. Verify setup:
   ```bash
   ticklisto show <task-id>
   ```

4. Complete first instance:
   ```bash
   ticklisto complete <task-id>
   ```

5. Verify next instance was created:
   ```bash
   ticklisto list --recurring
   ```

### Workflow 2: Managing Overdue Tasks

1. View overdue tasks:
   ```bash
   ticklisto list --overdue
   ```

2. Reschedule task:
   ```bash
   ticklisto update <task-id> --due "2026-02-06 10:00"
   ```

3. Or mark complete if done:
   ```bash
   ticklisto complete <task-id>
   ```

### Workflow 3: Setting Up Email Reminders

1. Configure Gmail API (one-time setup):
   ```bash
   python -m ticklisto auth gmail
   ```

2. Install and start daemon:
   ```bash
   sudo python daemon/install_service.py --install
   sudo systemctl start ticklisto-daemon
   ```

3. Add tasks with reminders:
   ```bash
   ticklisto add "Important deadline" --due "2026-02-10 17:00" --remind "1d,1h"
   ```

4. Verify reminders are scheduled:
   ```bash
   ticklisto show <task-id>
   ```

5. Check daemon is running:
   ```bash
   ticklisto daemon status
   ```

## Date/Time Input Formats

Ticklisto accepts flexible date/time formats:

### Supported Formats

**ISO 8601** (recommended, unambiguous):
- `2026-02-05`
- `2026-02-05T14:30:00`
- `2026-02-05 14:30`

**US Format**:
- `02/05/2026`
- `2/5/2026`
- `02/05/2026 2:30 PM`

**European Format**:
- `05/02/2026` (will prompt for clarification if ambiguous)

**Natural Language**:
- `Feb 5, 2026`
- `February 5, 2026`
- `5 Feb 2026`

**Time Formats**:
- `14:30` (24-hour)
- `2:30 PM` (12-hour)
- `14:30:00` (with seconds)

### Ambiguity Handling

If you enter an ambiguous date like `02/05/2026`, Ticklisto will prompt:

```
Ambiguous date format detected: 02/05/2026
Did you mean:
  1. February 5, 2026
  2. May 2, 2026
Enter choice (1 or 2):
```

## Recurrence Patterns

### Pattern Types

- **daily**: Every N days
- **weekly**: Every N weeks on specific days
- **monthly**: Every N months on same day
- **yearly**: Every N years on same date

### Interval Limits

- Daily: 1-365 days
- Weekly: 1-52 weeks
- Monthly: 1-24 months
- Yearly: 1-10 years

### End Conditions

Choose one:
- **No end**: Task repeats indefinitely
- **End date**: Repeat until specific date (`--until`)
- **Occurrence count**: Repeat N times (`--count`)

### Weekly Recurrence Days

Specify days using abbreviations:
- `Mon`, `Tue`, `Wed`, `Thu`, `Fri`, `Sat`, `Sun`
- Multiple days: `--weekdays Mon,Wed,Fri`

## Reminder Options

### Predefined Offsets

- `15m` - 15 minutes before
- `30m` - 30 minutes before
- `1h` - 1 hour before
- `2h` - 2 hours before
- `1d` - 1 day before
- `1w` - 1 week before

### Custom Offsets

Format: `{number}{unit}` where unit is:
- `m` - minutes
- `h` - hours
- `d` - days
- `w` - weeks

Examples: `45m`, `3h`, `2d`, `2w`

### Multiple Reminders

Separate with commas: `--remind "1d,1h,15m"`

## Troubleshooting

### Issue: Daemon not starting

**Solution**:
```bash
# Check daemon status
ticklisto daemon status

# View daemon logs
ticklisto daemon logs

# Restart daemon
ticklisto daemon restart
```

### Issue: Gmail authentication failed

**Solution**:
1. Verify credentials file exists at path in `.env`
2. Re-run authentication:
   ```bash
   python -m ticklisto auth gmail --force
   ```
3. Check token file permissions:
   ```bash
   ls -la ~/.ticklisto/gmail_token.json
   # Should be -rw------- (0600)
   ```

### Issue: Reminders not being sent

**Solution**:
1. Check daemon is running: `ticklisto daemon status`
2. Verify Gmail API is enabled in `.env`: `GMAIL_ENABLED=true`
3. Check daemon logs for errors: `ticklisto daemon logs`
4. Verify reminder time is in the future: `ticklisto show <task-id>`

### Issue: Recurring task not creating next instance

**Solution**:
1. Verify task is marked as recurring: `ticklisto show <task-id>`
2. Check if end condition reached (count or until date)
3. View completion history: `ticklisto show <task-id> --history`
4. Check for errors in application logs

### Issue: Ambiguous date keeps prompting

**Solution**:
Use ISO 8601 format to avoid ambiguity:
```bash
# Instead of: 02/05/2026
# Use: 2026-02-05
ticklisto add "Task" --due "2026-02-05"
```

## Best Practices

1. **Use ISO 8601 dates** for unambiguous date entry
2. **Set reminders for important tasks** to avoid missing deadlines
3. **Use recurring tasks** for routine activities to save time
4. **Review overdue tasks daily** to stay on track
5. **Keep daemon running** for reliable email reminders
6. **Backup your data** regularly (JSON file at `ticklisto_data.json`)
7. **Use tags and priorities** (from Feature 002) with due dates for better organization
8. **Set end conditions** for recurring tasks that shouldn't repeat forever

## Next Steps

- Explore advanced filtering: `ticklisto help filter`
- Learn about task priorities: `ticklisto help priority`
- Set up custom reminder templates (coming in future release)
- Integrate with calendar apps (coming in future release)

## Support

For issues or questions:
- Check documentation: `ticklisto help`
- View command help: `ticklisto <command> --help`
- Report bugs: [GitHub Issues](https://github.com/your-repo/ticklisto/issues)
