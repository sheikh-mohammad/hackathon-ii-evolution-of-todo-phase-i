import pytest
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch
from src.ticklisto.services.task_service import TaskService
from src.ticklisto.models.task import Task


class TestTaskService:
    """Unit tests for the TaskService class."""

    def setup_method(self):
        """Set up a temporary file for testing."""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.service = TaskService(data_file=self.temp_file.name)

    def teardown_method(self):
        """Clean up the temporary file."""
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_initialization(self):
        """Test that TaskService initializes with empty task list and next_id=1."""
        assert len(self.service.tasks) == 0
        assert self.service.next_id == 1

    def test_add_task_success(self):
        """Test adding a valid task."""
        task = self.service.add("Test Task", "Test Description")

        assert task is not None
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.completed is False
        assert task.id in self.service.tasks
        assert self.service.next_id == 2

    def test_add_task_with_minimal_params(self):
        """Test adding a task with only required parameters."""
        task = self.service.add("Test Task")

        assert task is not None
        assert task.id == 1
        assert task.title == "Test Task"
        assert task.description == ""
        assert task.completed is False

    def test_add_task_invalid_title(self):
        """Test adding a task with invalid title."""
        task = self.service.add("", "Test Description")

        assert task is None
        assert len(self.service.tasks) == 0

    def test_add_task_invalid_title_length(self):
        """Test adding a task with title too long."""
        long_title = "A" * 201
        task = self.service.add(long_title, "Test Description")

        assert task is None
        assert len(self.service.tasks) == 0

    def test_add_task_invalid_description_length(self):
        """Test adding a task with description too long."""
        long_description = "A" * 1001
        task = self.service.add("Test Task", long_description)

        assert task is None
        assert len(self.service.tasks) == 0

    def test_get_all_empty_list(self):
        """Test getting all tasks when list is empty."""
        tasks = self.service.get_all()

        assert tasks == []

    def test_get_all_with_tasks(self):
        """Test getting all tasks when list has tasks."""
        self.service.add("Task 1", "Description 1")
        self.service.add("Task 2", "Description 2")

        tasks = self.service.get_all()

        assert len(tasks) == 2
        assert tasks[0].id == 1
        assert tasks[1].id == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"

    def test_get_by_id_exists(self):
        """Test getting a task by ID that exists."""
        added_task = self.service.add("Test Task", "Description")
        retrieved_task = self.service.get_by_id(added_task.id)

        assert retrieved_task is not None
        assert retrieved_task.id == added_task.id
        assert retrieved_task.title == "Test Task"

    def test_get_by_id_not_exists(self):
        """Test getting a task by ID that doesn't exist."""
        retrieved_task = self.service.get_by_id(999)

        assert retrieved_task is None

    def test_update_task_success(self):
        """Test updating a task successfully."""
        task = self.service.add("Original Task", "Original Description")

        success = self.service.update(task.id, title="Updated Task", description="Updated Description")

        assert success is True
        updated_task = self.service.get_by_id(task.id)
        assert updated_task.title == "Updated Task"
        assert updated_task.description == "Updated Description"

    def test_update_task_partial(self):
        """Test updating only some fields of a task."""
        task = self.service.add("Original Task", "Original Description")

        success = self.service.update(task.id, title="Updated Task")

        assert success is True
        updated_task = self.service.get_by_id(task.id)
        assert updated_task.title == "Updated Task"
        assert updated_task.description == "Original Description"  # Should remain unchanged

    def test_update_task_not_exists(self):
        """Test updating a task that doesn't exist."""
        success = self.service.update(999, title="Updated Task")

        assert success is False

    def test_update_task_invalid_data(self):
        """Test updating a task with invalid data."""
        task = self.service.add("Original Task", "Original Description")

        success = self.service.update(task.id, title="")  # Invalid title

        assert success is False
        # Original task should remain unchanged
        original_task = self.service.get_by_id(task.id)
        assert original_task.title == "Original Task"

    def test_delete_task_success(self):
        """Test deleting a task successfully."""
        task = self.service.add("Test Task", "Description")

        success = self.service.delete(task.id)

        assert success is True
        assert len(self.service.tasks) == 0
        assert self.service.get_by_id(task.id) is None

    def test_delete_task_not_exists(self):
        """Test deleting a task that doesn't exist."""
        success = self.service.delete(999)

        assert success is False

    def test_toggle_complete_success(self):
        """Test toggling completion status successfully."""
        task = self.service.add("Test Task", "Description")

        # Initially should be False
        assert task.completed is False

        # Toggle to True
        success = self.service.toggle_complete(task.id)
        assert success is True
        toggled_task = self.service.get_by_id(task.id)
        assert toggled_task.completed is True

        # Toggle back to False
        success = self.service.toggle_complete(task.id)
        assert success is True
        toggled_task = self.service.get_by_id(task.id)
        assert toggled_task.completed is False

    def test_toggle_complete_not_exists(self):
        """Test toggling completion status for a task that doesn't exist."""
        success = self.service.toggle_complete(999)

        assert success is False