"""
Integration tests for CLI commands with Rich formatting.
Following TDD approach - these tests are written FIRST and should FAIL initially.
"""
import pytest
from io import StringIO
from ticklisto.models.task import Task, Priority
from ticklisto.services.task_service import TaskService
from ticklisto.cli.ticklisto_cli import TickListoCLI
from ticklisto.ui.rich_ui import RichUI


class TestCLICommandsWithEnhancements:
    """Integration tests for CLI commands with priority and categories display."""

    def test_display_task_with_priority_indicator(self):
        """Test that tasks display with priority indicators."""
        service = TaskService(data_file="test_cli_priority_display.json")
        ui = RichUI()

        # Create tasks with different priorities
        task1 = service.add_task(title="High Priority", priority=Priority.HIGH)
        task2 = service.add_task(title="Medium Priority", priority=Priority.MEDIUM)
        task3 = service.add_task(title="Low Priority", priority=Priority.LOW)

        tasks = service.list_tasks()

        # Test that display method can handle priority field
        # This should not raise an error
        try:
            ui.display_tasks(tasks)
            display_success = True
        except Exception:
            display_success = False

        assert display_success is True

    def test_display_task_with_categories(self):
        """Test that tasks display with category tags."""
        service = TaskService(data_file="test_cli_categories_display.json")
        ui = RichUI()

        task = service.add_task(
            title="Work Task",
            categories=["work", "urgent", "client"]
        )

        tasks = service.list_tasks()

        # Test that display method can handle categories field
        try:
            ui.display_tasks(tasks)
            display_success = True
        except Exception:
            display_success = False

        assert display_success is True

    def test_display_task_with_due_date(self):
        """Test that tasks display with due date."""
        from datetime import datetime
        service = TaskService(data_file="test_cli_due_date_display.json")
        ui = RichUI()

        task = service.add_task(
            title="Task with deadline",
            due_date=datetime(2026, 2, 15)
        )

        tasks = service.list_tasks()

        # Test that display method can handle due_date field
        try:
            ui.display_tasks(tasks)
            display_success = True
        except Exception:
            display_success = False

        assert display_success is True

    def test_display_empty_task_list(self):
        """Test displaying empty task list."""
        service = TaskService(data_file="test_cli_empty_list.json")
        ui = RichUI()

        tasks = service.list_tasks()
        assert len(tasks) == 0

        # Should handle empty list gracefully
        try:
            ui.display_tasks(tasks)
            display_success = True
        except Exception:
            display_success = False

        assert display_success is True

    def test_display_task_with_all_fields(self):
        """Test displaying task with all enhanced fields."""
        from datetime import datetime
        service = TaskService(data_file="test_cli_all_fields_display.json")
        ui = RichUI()

        task = service.add_task(
            title="Complete Task",
            description="Full task with all fields",
            priority=Priority.HIGH,
            categories=["work", "urgent"],
            due_date=datetime(2026, 2, 15)
        )

        tasks = service.list_tasks()

        # Test that display handles all fields
        try:
            ui.display_tasks(tasks)
            display_success = True
        except Exception:
            display_success = False

        assert display_success is True

    def test_priority_color_coding(self):
        """Test that priority levels have appropriate color coding."""
        ui = RichUI()

        # Test that UI has methods for priority styling
        assert hasattr(ui, 'get_priority_style') or hasattr(ui, 'format_priority')

    def test_category_display_formatting(self):
        """Test that categories are formatted appropriately."""
        ui = RichUI()

        # Test that UI has methods for category formatting
        assert hasattr(ui, 'format_categories') or hasattr(ui, 'get_category_display')
