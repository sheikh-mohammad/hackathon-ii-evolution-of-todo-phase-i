# Tick Listo

A command-line task management application that stores tasks in memory with temporary file persistence between sessions. Built with Python 3.14+ and Rich for beautiful console formatting.

## Features

### Core Task Management
- Add, view, update, delete, and mark tasks as complete/incomplete
- Auto-generated sequential task IDs
- Rich-formatted console interface with visual status indicators
- Temporary file persistence between sessions
- Sub-second response times for all operations
- Graceful error handling with informative messages

### Advanced Organization (New!)
- **Priority Levels**: Assign high, medium, or low priority to tasks
- **Category Tags**: Organize tasks with multiple category labels
- **Due Dates**: Set deadlines with flexible date parsing (MM/DD/YYYY, natural language like "tomorrow", "next week")
- **Search**: Find tasks by keyword in title or description
- **Filter**: Filter tasks by status, priority, categories, and due dates
- **Sort**: Sort tasks by due date, priority, or alphabetically
- **Clear Console**: Clear the screen for a fresh view

## Prerequisites

- Python 3.14+
- UV package manager

## Installation

1. Clone or download the repository
2. Install dependencies using UV:

```bash
uv sync
```

Or install the required packages directly:

```bash
pip install rich pytest python-dateutil
```

## Usage

Run the application:

```bash
python -m src.ticklisto
```

Or alternatively:

```bash
cd src
python -m todo_app
```

### Available Commands

#### Basic Commands
- `add` or `a` - Add a new task with priority, categories, and due date
- `view` or `v` - View all tasks with enhanced formatting
- `update` or `u` - Update a task's details
- `delete` or `d` - Delete a task
- `complete` or `c` - Mark task as complete/incomplete
- `stats` or `s` - View task statistics

#### Organization Commands (New!)
- `search` or `find` or `f` - Search tasks by keyword
- `filter` or `fl` - Filter tasks by status, priority, categories, or dates
- `sort` or `sr` - Sort tasks by due date, priority, or title
- `clear` or `clr` - Clear the console screen

#### System Commands
- `help` or `h` - Show help information
- `quit` or `q` - Exit the application

### Example Workflow

1. Start the application: `python -m src.ticklisto`
2. Add a task: Enter `add` or `a` and follow the prompts
3. View tasks: Enter `view` or `v` to see all tasks
4. Mark as complete: Enter `complete` or `c` and specify task ID
5. Update task: Enter `update` or `u` and specify task ID
6. Delete task: Enter `delete` or `d` and specify task ID
7. Exit: Enter `quit` or `q` to save and exit

## Usage Examples

### Working with Priorities and Categories

**Adding a task with priority and categories:**
```
> add
Enter task title: Complete project documentation
Enter task description (optional): Write comprehensive docs for the new features
Enter priority (high/medium/low) [medium]: high
Enter categories (comma-separated, optional): work, documentation, urgent
Enter due date (optional, e.g., MM/DD/YYYY, 'tomorrow', 'next week'): tomorrow
```

**Updating task priority:**
```
> update
Enter task ID to update: 5
Enter new priority (high/medium/low) or press Enter to keep current: high
```

**Adding categories to existing task:**
```
> update
Enter task ID to update: 3
Enter new categories (comma-separated) or press Enter to keep current: work, client, urgent
```

### Searching Tasks

**Search by keyword in title or description:**
```
> search
Enter search keyword: documentation

Found 3 task(s) matching 'documentation':
[Displays matching tasks with priority indicators and category tags]
```

**Search is case-insensitive and matches partial words:**
```
> search
Enter search keyword: proj

Found 5 task(s) matching 'proj':
- Complete project documentation
- Project planning meeting
- Review project proposal
...
```

### Filtering Tasks

**Filter by status:**
```
> filter
Select filter option: 1 (Status)
Filter by status: incomplete

Found 12 task(s) matching your criteria:
[Displays all incomplete tasks]
```

**Filter by priority:**
```
> filter
Select filter option: 2 (Priority)
Filter by priority: high

Found 5 task(s) matching your criteria:
[Displays all high-priority tasks]
```

**Filter by categories (OR logic):**
```
> filter
Select filter option: 3 (Categories)
Enter categories (comma-separated): work, urgent
Match logic: any

Found 8 task(s) matching your criteria:
[Displays tasks with either 'work' OR 'urgent' category]
```

**Filter by categories (AND logic):**
```
> filter
Select filter option: 3 (Categories)
Enter categories (comma-separated): work, urgent
Match logic: all

Found 3 task(s) matching your criteria:
[Displays tasks with both 'work' AND 'urgent' categories]
```

**Filter by multiple criteria:**
```
> filter
Select filter option: 4 (All criteria)
Filter by status: incomplete
Filter by priority: high
Enter categories: work
Match logic: any

Found 2 task(s) matching your criteria:
[Displays incomplete, high-priority tasks in 'work' category]
```

### Sorting Tasks

**Sort by due date (earliest first):**
```
> sort
Select sort option: 1 (Due Date)
Apply secondary sort? Yes
Secondary sort: priority

Tasks sorted by due date (then by priority):
[Displays tasks ordered by due date, with high priority first for same dates]
```

**Sort by priority (high to low):**
```
> sort
Select sort option: 2 (Priority)
Apply secondary sort? No

Tasks sorted by priority:
[Displays all high priority tasks first, then medium, then low]
```

**Sort alphabetically by title:**
```
> sort
Select sort option: 3 (Title)

Tasks sorted by title:
[Displays tasks in alphabetical order]
```

### Clearing the Console

**Clear the screen for a fresh view:**
```
> clear
Console cleared!
```

Or use the shorter alias:
```
> clr
Console cleared!
```

## Project Structure

```
src/
├── ticklisto/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py              # Enhanced Task data model with priority, categories, due_date
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_service.py      # Core task CRUD operations
│   │   ├── search_service.py    # Search functionality
│   │   ├── filter_service.py    # Filter functionality
│   │   ├── sort_service.py      # Sort functionality
│   │   └── validation_service.py # Input validation
│   ├── cli/
│   │   ├── __init__.py
│   │   └── ticklisto_cli.py     # Command-line interface with all commands
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── rich_ui.py           # Rich formatting and display
│   │   └── components.py        # Reusable UI components
│   └── utils/
│       ├── __init__.py
│       ├── file_handler.py      # File persistence logic
│       └── date_parser.py       # Flexible date parsing utility
│
tests/
├── unit/
│   ├── test_task.py             # Unit tests for Task model
│   ├── test_task_model.py       # Enhanced Task model tests
│   ├── test_task_service.py     # Unit tests for task service
│   ├── test_search_service.py   # Search service tests
│   ├── test_filter_service.py   # Filter service tests
│   ├── test_sort_service.py     # Sort service tests
│   ├── test_validation_service.py # Validation tests
│   └── test_date_parser.py      # Date parser tests
├── integration/
│   ├── test_cli_integration.py  # CLI integration tests
│   ├── test_cli_commands.py     # Enhanced CLI command tests
│   ├── test_task_operations.py  # Task operations with new fields
│   └── test_search_filter_integration.py # Combined search/filter tests
└── contract/
    ├── test_api_contract.py     # Contract tests for CLI interface
    └── test_backward_compatibility.py # Backward compatibility tests
```

## Testing

Run the tests using pytest:

```bash
pytest
```

To run tests with verbose output:

```bash
pytest -v
```

To run specific test files:

```bash
# Unit tests
pytest tests/unit/test_task_model.py
pytest tests/unit/test_search_service.py
pytest tests/unit/test_filter_service.py
pytest tests/unit/test_sort_service.py

# Integration tests
pytest tests/integration/test_task_operations.py
pytest tests/integration/test_cli_commands.py
pytest tests/integration/test_search_filter_integration.py

# Contract tests
pytest tests/contract/test_backward_compatibility.py
```

To run tests with coverage:

```bash
pytest --cov=src/ticklisto --cov-report=html
```

### Test Coverage

The project maintains comprehensive test coverage:
- **Unit Tests**: 75+ tests covering all services and models
- **Integration Tests**: End-to-end testing of CLI commands and workflows
- **Contract Tests**: Backward compatibility verification
- **Total Coverage**: 163+ passing tests

## Performance

The application is optimized for responsive performance:

- **Search**: < 500ms for up to 10,000 tasks
- **Filter**: < 300ms for up to 10,000 tasks
- **Sort**: < 500ms for up to 10,000 tasks
- **Task Operations**: Sub-second response for all CRUD operations

## Data Persistence

The application stores tasks in memory during runtime and persists them to a file named `ticklisto_data.json` when exiting. The file is automatically loaded when the application starts.

### Data Format

Tasks are stored with the following fields:
- `id`: Unique task identifier
- `title`: Task title (max 200 characters)
- `description`: Optional description (max 1000 characters)
- `completed`: Boolean completion status
- `priority`: Priority level (high/medium/low)
- `categories`: List of category tags
- `due_date`: Optional due date (ISO format)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Backward Compatibility

The application maintains full backward compatibility with existing task data. Tasks created without priority, categories, or due dates will automatically receive default values:
- Priority: `medium`
- Categories: `[]` (empty list)
- Due date: `None`

## License

This project is part of a hackathon and is provided as-is for educational purposes.
