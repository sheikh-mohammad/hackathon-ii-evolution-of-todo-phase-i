from typing import Optional
import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from ..services.task_service import TaskService
from ..services.search_service import SearchService
from ..services.filter_service import FilterService
from ..services.sort_service import SortService
from ..ui.components import create_styled_menu
from ..models.task import Priority


class TickListoCLI:
    """
    Command-line interface for the Tick Listo application.
    Implements all the required commands with Rich formatting.
    """

    def __init__(self):
        """Initialize the CLI with a task service and console."""
        self.task_service = TaskService()
        self.search_service = SearchService()
        self.filter_service = FilterService()
        self.sort_service = SortService()
        self.console = Console()

    def run(self):
        """Main CLI loop that handles user commands."""
        # Display startup message with ASCII art header
        self.task_service.rich_ui.display_startup_message()

        while True:
            try:
                # Use styled menu for command input
                command = Prompt.ask("[bold green]Tick Listo[/bold green]", default="help").strip().lower()

                if command in ['quit', 'q']:
                    self._handle_quit()
                    break
                elif command in ['add', 'a']:
                    self._handle_add()
                elif command in ['view', 'v']:
                    self._handle_view()
                elif command in ['update', 'u']:
                    self._handle_update()
                elif command in ['delete', 'd']:
                    self._handle_delete()
                elif command in ['complete', 'c']:
                    self._handle_complete()
                elif command in ['search', 'find', 'f']:
                    self._handle_search()
                elif command in ['filter', 'fl']:
                    self._handle_filter()
                elif command in ['sort', 'sr']:
                    self._handle_sort()
                elif command in ['clear', 'clr']:
                    self._handle_clear()
                elif command in ['stats', 's']:  # Add stats command
                    self._handle_stats()
                elif command in ['help', 'h']:
                    self._handle_help()
                else:
                    self.task_service.display_error_message(f"Unknown command: {command}")
                    self.console.print("Type 'help' for available commands.\n")

            except KeyboardInterrupt:
                self.task_service.display_error_message("Received interrupt signal. Quitting...")
                self._handle_quit()
                break
            except EOFError:
                self.task_service.display_error_message("End of input received. Quitting...")
                self._handle_quit()
                break

    def _handle_add(self):
        """Handle the add command to create a new task."""
        self.task_service.rich_ui.display_info_message("Adding a new task:")

        title = Prompt.ask("Enter task title")

        # Validate title length
        if not title or len(title.strip()) < 1 or len(title.strip()) > 200:
            self.task_service.display_error_message("Title must be between 1 and 200 characters.")
            return

        description = Prompt.ask("Enter task description (optional)", default="")

        # Validate description length
        if len(description) > 1000:
            self.task_service.display_error_message("Description cannot exceed 1000 characters.")
            return

        # Add the task
        try:
            task = self.task_service.add_task(title.strip(), description)
            self.task_service.display_success_message(f"Task added successfully with ID: {task.id}")
        except ValueError as e:
            self.task_service.display_error_message(f"Failed to add task: {str(e)}")

    def _handle_view(self):
        """Handle the view command to display all tasks."""
        self.task_service.display_all_tasks_enhanced()

    def _handle_update(self):
        """Handle the update command to modify a task."""
        self.task_service.rich_ui.display_info_message("Updating a task:")

        try:
            task_id_str = Prompt.ask("Enter task ID to update")
            task_id = int(task_id_str)
        except ValueError:
            self.task_service.display_error_message("Invalid task ID. Please enter a number.")
            return

        # Check if task exists
        task = self.task_service.get_by_id(task_id)
        if not task:
            self.task_service.display_error_message(f"Task with ID {task_id} not found.")
            return

        self.task_service.rich_ui.display_info_message(f"Current task: {task.title}")

        # Get new values or keep current ones
        new_title = Prompt.ask("Enter new title (or press Enter to keep current)", default=task.title)

        # Validate title length
        if new_title and (len(new_title.strip()) < 1 or len(new_title.strip()) > 200):
            self.task_service.display_error_message("Title must be between 1 and 200 characters.")
            return

        new_description = Prompt.ask("Enter new description (or press Enter to keep current)",
                                   default=task.description)

        # Validate description length
        if len(new_description) > 1000:
            self.task_service.display_error_message("Description cannot exceed 1000 characters.")
            return

        # Update the task
        success = self.task_service.update_task(
            task_id=task_id,
            title=new_title if new_title != task.title else None,
            description=new_description if new_description != task.description else None
        )

        if success:
            self.task_service.display_success_message(f"Task {task_id} updated successfully!")
        else:
            self.task_service.display_error_message(f"Failed to update task {task_id}. Please check your input.")

    def _handle_delete(self):
        """Handle the delete command to remove a task."""
        self.task_service.rich_ui.display_info_message("Deleting a task:")

        try:
            task_id_str = Prompt.ask("Enter task ID to delete")
            task_id = int(task_id_str)
        except ValueError:
            self.task_service.display_error_message("Invalid task ID. Please enter a number.")
            return

        # Check if task exists
        task = self.task_service.get_by_id(task_id)
        if not task:
            self.task_service.display_error_message(f"Task with ID {task_id} not found.")
            return

        self.task_service.rich_ui.display_info_message(f"Task to delete: {task.title}")

        confirm = Confirm.ask("Are you sure you want to delete this task?")

        if confirm:
            success = self.task_service.delete_task(task_id)

            if success:
                self.task_service.display_success_message(f"Task {task_id} deleted successfully!")
            else:
                self.task_service.display_error_message(f"Failed to delete task {task_id}.")
        else:
            self.task_service.rich_ui.display_warning_message("Task deletion cancelled.")

    def _handle_complete(self):
        """Handle the complete command to toggle task completion status."""
        self.task_service.rich_ui.display_info_message("Toggle task completion:")

        try:
            task_id_str = Prompt.ask("Enter task ID to toggle completion status")
            task_id = int(task_id_str)
        except ValueError:
            self.task_service.display_error_message("Invalid task ID. Please enter a number.")
            return

        # Check if task exists
        task = self.task_service.get_by_id(task_id)
        if not task:
            self.task_service.display_error_message(f"Task with ID {task_id} not found.")
            return

        # Toggle completion status
        success = self.task_service.toggle_complete(task_id)

        if success:
            # Get updated task to show current status
            updated_task = self.task_service.get_by_id(task_id)
            new_status = updated_task.status.value
            self.task_service.display_success_message(f"Task {task_id} marked as {new_status}!")
        else:
            self.task_service.display_error_message(f"Failed to toggle completion status for task {task_id}.")

    def _handle_quit(self):
        """Handle the quit command to gracefully shut down the app."""
        self.task_service.rich_ui.display_info_message("Saving tasks and exiting...")
        self.task_service.save_to_file()
        self.task_service.display_success_message("Tasks saved successfully. Goodbye!")

    def _handle_stats(self):
        """Handle the stats command to display progress statistics."""
        self.task_service.display_progress_stats_enhanced()

    def _handle_search(self):
        """Handle the search command to find tasks by keyword."""
        self.task_service.rich_ui.display_info_message("Search tasks:")

        keyword = Prompt.ask("Enter search keyword")

        if not keyword or not keyword.strip():
            self.task_service.display_error_message("Search keyword cannot be empty.")
            return

        # Get all tasks
        all_tasks = self.task_service.list_tasks()

        # Search tasks
        results = self.search_service.search_tasks(all_tasks, keyword.strip())

        if results:
            self.task_service.rich_ui.display_success_message(
                f"Found {len(results)} task(s) matching '{keyword}':"
            )
            self.task_service.rich_ui.display_tasks(results)
        else:
            self.task_service.rich_ui.display_warning_message(
                f"No tasks found matching '{keyword}'."
            )
            self.console.print("\n[dim]Try different keywords or check your spelling.[/dim]\n")

    def _handle_filter(self):
        """Handle the filter command to filter tasks by criteria."""
        self.task_service.rich_ui.display_info_message("Filter tasks:")

        # Get all tasks
        all_tasks = self.task_service.list_tasks()

        if not all_tasks:
            self.task_service.rich_ui.display_warning_message("No tasks to filter.")
            return

        # Ask for filter criteria
        self.console.print("\n[bold]Filter Options:[/bold]")
        self.console.print("1. Status (complete/incomplete)")
        self.console.print("2. Priority (high/medium/low)")
        self.console.print("3. Categories")
        self.console.print("4. All criteria")
        self.console.print("5. Cancel\n")

        choice = Prompt.ask("Select filter option", choices=["1", "2", "3", "4", "5"], default="5")

        if choice == "5":
            self.task_service.rich_ui.display_info_message("Filter cancelled.")
            return

        results = all_tasks

        # Filter by status
        if choice in ["1", "4"]:
            status_choice = Prompt.ask(
                "Filter by status",
                choices=["complete", "incomplete", "all"],
                default="all"
            )
            if status_choice != "all":
                results = self.filter_service.filter_tasks(results, status=status_choice)

        # Filter by priority
        if choice in ["2", "4"]:
            priority_choice = Prompt.ask(
                "Filter by priority",
                choices=["high", "medium", "low", "all"],
                default="all"
            )
            if priority_choice != "all":
                priority_map = {
                    "high": Priority.HIGH,
                    "medium": Priority.MEDIUM,
                    "low": Priority.LOW
                }
                results = self.filter_service.filter_tasks(
                    results,
                    priority=priority_map[priority_choice]
                )

        # Filter by categories
        if choice in ["3", "4"]:
            categories_input = Prompt.ask(
                "Enter categories (comma-separated, or press Enter to skip)",
                default=""
            )
            if categories_input.strip():
                categories = [cat.strip() for cat in categories_input.split(",") if cat.strip()]
                if categories:
                    match_logic = Prompt.ask(
                        "Match logic",
                        choices=["any", "all"],
                        default="any"
                    )
                    results = self.filter_service.filter_tasks(
                        results,
                        categories=categories,
                        category_match=match_logic
                    )

        # Display results
        if results:
            self.task_service.rich_ui.display_success_message(
                f"Found {len(results)} task(s) matching your criteria:"
            )
            self.task_service.rich_ui.display_tasks(results)
        else:
            self.task_service.rich_ui.display_warning_message(
                "No tasks found matching your criteria."
            )
            self.console.print("\n[dim]Try adjusting your filter criteria.[/dim]\n")

    def _handle_sort(self):
        """Handle the sort command to sort tasks by criteria."""
        self.task_service.rich_ui.display_info_message("Sort tasks:")

        # Get all tasks
        all_tasks = self.task_service.list_tasks()

        if not all_tasks:
            self.task_service.rich_ui.display_warning_message("No tasks to sort.")
            return

        # Ask for sort criteria
        self.console.print("\n[bold]Sort Options:[/bold]")
        self.console.print("1. Due Date (earliest first)")
        self.console.print("2. Priority (high to low)")
        self.console.print("3. Title (alphabetically)")
        self.console.print("4. Cancel\n")

        choice = Prompt.ask("Select sort option", choices=["1", "2", "3", "4"], default="4")

        if choice == "4":
            self.task_service.rich_ui.display_info_message("Sort cancelled.")
            return

        # Map choice to sort criteria
        sort_map = {
            "1": "due_date",
            "2": "priority",
            "3": "title"
        }

        sort_by = sort_map[choice]

        # Ask for secondary sort
        secondary = None
        if choice in ["1", "2"]:
            use_secondary = Confirm.ask("Apply secondary sort?", default=False)
            if use_secondary:
                if choice == "1":  # Due date primary
                    secondary_choice = Prompt.ask(
                        "Secondary sort",
                        choices=["priority", "title", "none"],
                        default="priority"
                    )
                else:  # Priority primary
                    secondary_choice = Prompt.ask(
                        "Secondary sort",
                        choices=["due_date", "title", "none"],
                        default="due_date"
                    )
                if secondary_choice != "none":
                    secondary = secondary_choice

        # Sort tasks
        try:
            sorted_tasks = self.sort_service.sort_tasks(all_tasks, sort_by, secondary)

            self.task_service.rich_ui.display_success_message(
                f"Tasks sorted by {sort_by.replace('_', ' ')}" +
                (f" (then by {secondary})" if secondary else "") + ":"
            )
            self.task_service.rich_ui.display_tasks(sorted_tasks)
        except ValueError as e:
            self.task_service.display_error_message(f"Sort failed: {str(e)}")

    def _handle_clear(self):
        """Handle the clear command to clear the console."""
        self.console.clear()
        self.task_service.rich_ui.display_success_message("Console cleared!")

    def _handle_help(self):
        """Display help information with all available commands."""
        # Use the enhanced menu function to display help
        options = [
            "Add a new task",
            "View all tasks",
            "Update a task",
            "Delete a task",
            "Toggle task completion status",
            "Search tasks by keyword",
            "Filter tasks by criteria",
            "Sort tasks by criteria",
            "Clear the console",
            "View task statistics",
            "Show this help message",
            "Exit the application"
        ]

        menu = create_styled_menu([
            "add or a - Add a new task",
            "view or v - View all tasks",
            "update or u - Update a task",
            "delete or d - Delete a task",
            "complete or c - Toggle task completion status",
            "search or find or f - Search tasks by keyword",
            "filter or fl - Filter tasks by criteria",
            "sort or sr - Sort tasks by criteria",
            "clear or clr - Clear the console",
            "stats or s - View task statistics",
            "help or h - Show this help message",
            "quit or q - Exit the application"
        ], "Available Commands")

        self.console.print("\n", menu, "\n")


def main():
    """Main entry point for the application."""
    cli = TickListoCLI()
    try:
        cli.run()
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()