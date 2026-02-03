"""
SearchService for task search functionality.
Provides keyword-based search across task titles and descriptions.
"""
from typing import List
from ..models.task import Task


class SearchService:
    """Service for searching tasks by keyword."""

    def search_tasks(self, tasks: List[Task], keyword: str) -> List[Task]:
        """
        Search tasks by keyword in title and description.

        Args:
            tasks: List of tasks to search
            keyword: Search keyword (case-insensitive)

        Returns:
            List of tasks matching the keyword
        """
        # Handle empty or whitespace-only keyword
        if not keyword or not keyword.strip():
            return tasks

        keyword_lower = keyword.lower()
        results = []

        for task in tasks:
            if self._task_matches_keyword(task, keyword_lower):
                results.append(task)

        return results

    def _task_matches_keyword(self, task: Task, keyword_lower: str) -> bool:
        """
        Check if a task matches the search keyword.

        Args:
            task: Task to check
            keyword_lower: Lowercase keyword to search for

        Returns:
            True if task matches keyword, False otherwise
        """
        # Search in title
        if keyword_lower in task.title.lower():
            return True

        # Search in description if it exists
        if task.description and keyword_lower in task.description.lower():
            return True

        return False
