"""Integration tests for task persistence across application restarts."""

import json
import os
import tempfile
from datetime import datetime

import pytest

from src.ticklisto.models.task import Priority, Task
from src.ticklisto.services.id_manager import IDManager
from src.ticklisto.services.storage_service import StorageService
from src.ticklisto.services.task_service import TaskService


class TestTaskPersistenceAcrossRestarts:
    """Test that tasks persist across application restarts."""

    def test_tasks_persist_after_save_and_reload(self):
        """Test that tasks are saved and can be loaded after restart."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create and save tasks
            storage = StorageService()
            id_manager = IDManager()
            task_manager = TaskService(storage_service=storage, id_manager=id_manager)

            # Create tasks
            task1_id = id_manager.generate_id()
            task1 = Task(
                id=task1_id,
                title="Task 1",
                description="Description 1",
                priority=Priority.HIGH,
                categories=["work"],
            )

            task2_id = id_manager.generate_id()
            task2 = Task(
                id=task2_id,
                title="Task 2",
                description="Description 2",
                priority=Priority.MEDIUM,
                categories=["home", "personal"],
            )

            task_manager.add_task(task1)
            task_manager.add_task(task2)

            # Save to storage
            task_manager.save_to_file(file_path)

            # Session 2: Load tasks (simulating app restart)
            storage2 = StorageService()
            id_manager2 = IDManager()
            task_manager2 = TaskService(storage_service=storage2, id_manager=id_manager2)

            task_manager2.load_from_file(file_path)

            # Verify tasks were loaded
            loaded_tasks = task_manager2.get_all()
            assert len(loaded_tasks) == 2

            # Verify task 1
            loaded_task1 = next(t for t in loaded_tasks if t.id == task1_id)
            assert loaded_task1.title == "Task 1"
            assert loaded_task1.description == "Description 1"
            assert loaded_task1.priority == Priority.HIGH
            assert loaded_task1.categories == ["work"]

            # Verify task 2
            loaded_task2 = next(t for t in loaded_tasks if t.id == task2_id)
            assert loaded_task2.title == "Task 2"
            assert loaded_task2.description == "Description 2"
            assert loaded_task2.priority == Priority.MEDIUM
            assert set(loaded_task2.categories) == {"home", "personal"}

    def test_task_modifications_persist(self):
        """Test that task modifications are persisted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create task
            storage = StorageService()
            id_manager = IDManager()
            task_manager = TaskService(storage_service=storage, id_manager=id_manager)

            task_id = id_manager.generate_id()
            task = Task(
                id=task_id,
                title="Original Title",
                description="Original Description",
                priority=Priority.LOW,
                categories=["work"],
                completed=False,
            )

            task_manager.add_task(task)
            task_manager.save_to_file(file_path)

            # Session 2: Modify task
            storage2 = StorageService()
            id_manager2 = IDManager()
            task_manager2 = TaskService(storage_service=storage2, id_manager=id_manager2)

            task_manager2.load_from_file(file_path)

            # Modify the task
            task_manager2.update_task(
                task_id,
                title="Updated Title",
                description="Updated Description",
                priority=Priority.HIGH,
                categories=["home", "urgent"],
                completed=True,
            )

            task_manager2.save_to_file(file_path)

            # Session 3: Verify modifications persisted
            storage3 = StorageService()
            id_manager3 = IDManager()
            task_manager3 = TaskService(storage_service=storage3, id_manager=id_manager3)

            task_manager3.load_from_file(file_path)

            loaded_task = task_manager3.get_by_id(task_id)
            assert loaded_task.title == "Updated Title"
            assert loaded_task.description == "Updated Description"
            assert loaded_task.priority == Priority.HIGH
            assert set(loaded_task.categories) == {"home", "urgent"}
            assert loaded_task.completed is True

    def test_task_deletion_persists(self):
        """Test that task deletions are persisted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create tasks
            storage = StorageService()
            id_manager = IDManager()
            task_manager = TaskService(storage_service=storage, id_manager=id_manager)

            task1_id = id_manager.generate_id()
            task2_id = id_manager.generate_id()
            task3_id = id_manager.generate_id()

            task_manager.add_task(Task(id=task1_id, title="Task 1", priority=Priority.HIGH, categories=["work"]))
            task_manager.add_task(Task(id=task2_id, title="Task 2", priority=Priority.MEDIUM, categories=["home"]))
            task_manager.add_task(Task(id=task3_id, title="Task 3", priority=Priority.LOW, categories=["personal"]))

            task_manager.save_to_file(file_path)

            # Session 2: Delete task 2
            storage2 = StorageService()
            id_manager2 = IDManager()
            task_manager2 = TaskService(storage_service=storage2, id_manager=id_manager2)

            task_manager2.load_from_file(file_path)
            task_manager2.delete_task(task2_id)
            task_manager2.save_to_file(file_path)

            # Session 3: Verify deletion persisted
            storage3 = StorageService()
            id_manager3 = IDManager()
            task_manager3 = TaskService(storage_service=storage3, id_manager=id_manager3)

            task_manager3.load_from_file(file_path)

            loaded_tasks = task_manager3.get_all()
            assert len(loaded_tasks) == 2

            task_ids = [t.id for t in loaded_tasks]
            assert task1_id in task_ids
            assert task2_id not in task_ids
            assert task3_id in task_ids

    def test_empty_task_list_persists(self):
        """Test that empty task list is persisted correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Save empty task list
            storage = StorageService()
            id_manager = IDManager()
            task_manager = TaskService(storage_service=storage, id_manager=id_manager)

            task_manager.save_to_file(file_path)

            # Session 2: Load and verify
            storage2 = StorageService()
            id_manager2 = IDManager()
            task_manager2 = TaskService(storage_service=storage2, id_manager=id_manager2)

            task_manager2.load_from_file(file_path)

            loaded_tasks = task_manager2.get_all()
            assert len(loaded_tasks) == 0

    def test_large_number_of_tasks_persist(self):
        """Test that large number of tasks (1000) persist correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create 1000 tasks
            storage = StorageService()
            id_manager = IDManager()
            task_manager = TaskService(storage_service=storage, id_manager=id_manager)

            for i in range(1, 1001):
                task_id = id_manager.generate_id()
                task = Task(
                    id=task_id,
                    title=f"Task {i}",
                    description=f"Description {i}",
                    priority=[Priority.HIGH, Priority.MEDIUM, Priority.LOW][i % 3],
                    categories=[["work"], ["home"], ["personal"]][i % 3],
                    completed=i % 2 == 0,
                )
                task_manager.add_task(task)

            task_manager.save_to_file(file_path)

            # Session 2: Load and verify
            storage2 = StorageService()
            id_manager2 = IDManager()
            task_manager2 = TaskService(storage_service=storage2, id_manager=id_manager2)

            task_manager2.load_from_file(file_path)

            loaded_tasks = task_manager2.get_all()
            assert len(loaded_tasks) == 1000

            # Verify some random tasks
            task_100 = task_manager2.get_by_id(100)
            assert task_100.title == "Task 100"

            task_500 = task_manager2.get_by_id(500)
            assert task_500.title == "Task 500"

            task_1000 = task_manager2.get_by_id(1000)
            assert task_1000.title == "Task 1000"


class TestIDUniqueness:
    """Test that IDs remain unique across application restarts."""

    def test_id_counter_persists_across_restarts(self):
        """Test that ID counter persists and continues from correct value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create tasks with IDs 1, 2, 3
            storage = StorageService()
            id_manager = IDManager()
            task_manager = TaskService(storage_service=storage, id_manager=id_manager)

            for i in range(3):
                task_id = id_manager.generate_id()
                task = Task(
                    id=task_id,
                    title=f"Task {task_id}",
                    priority=Priority.MEDIUM,
                    categories=["work"],
                )
                task_manager.add_task(task)

            task_manager.save_to_file(file_path)

            # Session 2: Load and create new task (should get ID 4)
            storage2 = StorageService()
            id_manager2 = IDManager()
            task_manager2 = TaskService(storage_service=storage2, id_manager=id_manager2)

            task_manager2.load_from_file(file_path)

            # Create new task
            new_task_id = id_manager2.generate_id()
            new_task = Task(
                id=new_task_id,
                title="New Task",
                priority=Priority.HIGH,
                categories=["home"],
            )
            task_manager2.add_task(new_task)

            # Verify new task has ID 4
            assert new_task_id == 4

            # Verify all task IDs are unique
            all_tasks = task_manager2.get_all()
            task_ids = [t.id for t in all_tasks]
            assert len(task_ids) == len(set(task_ids))  # All unique
            assert task_ids == [1, 2, 3, 4]

    def test_ids_never_reused_after_deletion(self):
        """Test that deleted task IDs are never reused."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create tasks 1, 2, 3
            storage = StorageService()
            id_manager = IDManager()
            task_manager = TaskService(storage_service=storage, id_manager=id_manager)

            task1_id = id_manager.generate_id()  # 1
            task2_id = id_manager.generate_id()  # 2
            task3_id = id_manager.generate_id()  # 3

            task_manager.add_task(Task(id=task1_id, title="Task 1", priority=Priority.HIGH, categories=["work"]))
            task_manager.add_task(Task(id=task2_id, title="Task 2", priority=Priority.MEDIUM, categories=["home"]))
            task_manager.add_task(Task(id=task3_id, title="Task 3", priority=Priority.LOW, categories=["personal"]))

            # Delete task 2
            task_manager.delete_task(task2_id)

            task_manager.save_to_file(file_path)

            # Session 2: Load and create new task
            storage2 = StorageService()
            id_manager2 = IDManager()
            task_manager2 = TaskService(storage_service=storage2, id_manager=id_manager2)

            task_manager2.load_from_file(file_path)

            # Create new task (should get ID 4, NOT 2)
            new_task_id = id_manager2.generate_id()
            assert new_task_id == 4  # Not 2!

            new_task = Task(
                id=new_task_id,
                title="New Task",
                priority=Priority.HIGH,
                categories=["work"],
            )
            task_manager2.add_task(new_task)

            # Verify task IDs
            all_tasks = task_manager2.get_all()
            task_ids = [t.id for t in all_tasks]
            assert set(task_ids) == {1, 3, 4}  # 2 is not reused

    def test_id_counter_resets_after_delete_all(self):
        """Test that ID counter resets to 1 after delete all."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create tasks
            storage = StorageService()
            id_manager = IDManager()
            task_manager = TaskService(storage_service=storage, id_manager=id_manager)

            for i in range(5):
                task_id = id_manager.generate_id()
                task = Task(
                    id=task_id,
                    title=f"Task {task_id}",
                    priority=Priority.MEDIUM,
                    categories=["work"],
                )
                task_manager.add_task(task)

            # Delete all tasks
            task_manager.delete_all()
            id_manager.reset_counter()

            task_manager.save_to_file(file_path)

            # Session 2: Load and create new task (should get ID 1)
            storage2 = StorageService()
            id_manager2 = IDManager()
            task_manager2 = TaskService(storage_service=storage2, id_manager=id_manager2)

            task_manager2.load_from_file(file_path)

            # Create new task
            new_task_id = id_manager2.generate_id()
            assert new_task_id == 1  # Fresh start!

            new_task = Task(
                id=new_task_id,
                title="New Task",
                priority=Priority.HIGH,
                categories=["work"],
            )
            task_manager2.add_task(new_task)

            # Verify only one task with ID 1
            all_tasks = task_manager2.get_all()
            assert len(all_tasks) == 1
            assert all_tasks[0].id == 1

    def test_concurrent_sessions_maintain_id_uniqueness(self):
        """Test that ID uniqueness is maintained even with multiple sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test_tasks.json")

            # Session 1: Create initial tasks
            storage1 = StorageService()
            id_manager1 = IDManager()
            task_manager1 = TaskService(storage_service=storage1, id_manager=id_manager1)

            for i in range(3):
                task_id = id_manager1.generate_id()
                task_manager1.add_task(
                    Task(id=task_id, title=f"Task {task_id}", priority=Priority.MEDIUM, categories=["work"])
                )

            task_manager1.save_to_file(file_path)

            # Session 2: Load and add more tasks
            storage2 = StorageService()
            id_manager2 = IDManager()
            task_manager2 = TaskService(storage_service=storage2, id_manager=id_manager2)

            task_manager2.load_from_file(file_path)

            for i in range(2):
                task_id = id_manager2.generate_id()
                task_manager2.add_task(
                    Task(id=task_id, title=f"Task {task_id}", priority=Priority.HIGH, categories=["home"])
                )

            task_manager2.save_to_file(file_path)

            # Session 3: Load and verify all IDs are unique
            storage3 = StorageService()
            id_manager3 = IDManager()
            task_manager3 = TaskService(storage_service=storage3, id_manager=id_manager3)

            task_manager3.load_from_file(file_path)

            all_tasks = task_manager3.get_all()
            task_ids = [t.id for t in all_tasks]

            # Verify all IDs are unique
            assert len(task_ids) == len(set(task_ids))
            assert task_ids == [1, 2, 3, 4, 5]
