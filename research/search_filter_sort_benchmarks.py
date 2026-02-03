"""
Performance benchmarks for search, filter, and sort patterns on in-memory Python collections.
Target: 1000 tasks, <500ms operations

This script tests various approaches for:
1. Search patterns (case-insensitive keyword search)
2. Filter patterns (multiple criteria with OR/AND logic)
3. Sort patterns (multi-level sorting with None handling)
"""

import time
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Callable
from enum import Enum
from functools import reduce
import operator


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """Sample task model for benchmarking."""
    id: int
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    due_date: Optional[datetime]
    categories: List[str]
    created_at: datetime


def generate_test_data(n: int = 1000) -> List[Task]:
    """Generate n test tasks with realistic data."""
    statuses = list(TaskStatus)
    priorities = list(Priority)
    categories_pool = ["work", "personal", "urgent", "shopping", "health", "finance", "learning"]

    tasks = []
    base_date = datetime.now()

    for i in range(n):
        # 30% of tasks have no due date
        due_date = None if random.random() < 0.3 else base_date + timedelta(days=random.randint(-30, 60))

        # Random 1-3 categories per task
        num_categories = random.randint(1, 3)
        task_categories = random.sample(categories_pool, num_categories)

        task = Task(
            id=i + 1,
            title=f"Task {i + 1}: {random.choice(['Fix', 'Update', 'Review', 'Create', 'Delete'])} {random.choice(['bug', 'feature', 'documentation', 'test', 'deployment'])}",
            description=f"Description for task {i + 1} with some searchable content and keywords",
            status=random.choice(statuses),
            priority=random.choice(priorities),
            due_date=due_date,
            categories=task_categories,
            created_at=base_date - timedelta(days=random.randint(0, 90))
        )
        tasks.append(task)

    return tasks


def benchmark(func: Callable, *args, iterations: int = 100, **kwargs) -> dict:
    """Benchmark a function and return timing statistics."""
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to milliseconds

    return {
        "min_ms": min(times),
        "max_ms": max(times),
        "avg_ms": sum(times) / len(times),
        "total_ms": sum(times),
        "result_count": len(result) if hasattr(result, '__len__') else None
    }


# ============================================================================
# SEARCH PATTERNS
# ============================================================================

def search_list_comprehension(tasks: List[Task], keyword: str) -> List[Task]:
    """Search using list comprehension (most Pythonic)."""
    keyword_lower = keyword.lower()
    return [
        task for task in tasks
        if keyword_lower in task.title.lower() or keyword_lower in task.description.lower()
    ]


def search_filter_function(tasks: List[Task], keyword: str) -> List[Task]:
    """Search using filter() built-in function."""
    keyword_lower = keyword.lower()
    return list(filter(
        lambda task: keyword_lower in task.title.lower() or keyword_lower in task.description.lower(),
        tasks
    ))


def search_generator_expression(tasks: List[Task], keyword: str) -> List[Task]:
    """Search using generator expression (memory efficient)."""
    keyword_lower = keyword.lower()
    return list(
        task for task in tasks
        if keyword_lower in task.title.lower() or keyword_lower in task.description.lower()
    )


def search_explicit_loop(tasks: List[Task], keyword: str) -> List[Task]:
    """Search using explicit for loop."""
    keyword_lower = keyword.lower()
    results = []
    for task in tasks:
        if keyword_lower in task.title.lower() or keyword_lower in task.description.lower():
            results.append(task)
    return results


def search_any_fields(tasks: List[Task], keyword: str) -> List[Task]:
    """Search across multiple fields using any()."""
    keyword_lower = keyword.lower()
    return [
        task for task in tasks
        if any(keyword_lower in str(getattr(task, field)).lower()
               for field in ['title', 'description'])
    ]


# ============================================================================
# FILTER PATTERNS
# ============================================================================

def filter_single_criterion(tasks: List[Task], status: TaskStatus) -> List[Task]:
    """Filter by single criterion."""
    return [task for task in tasks if task.status == status]


def filter_multiple_and(tasks: List[Task], status: TaskStatus, priority: Priority) -> List[Task]:
    """Filter with multiple AND conditions."""
    return [
        task for task in tasks
        if task.status == status and task.priority == priority
    ]


def filter_multiple_or(tasks: List[Task], statuses: List[TaskStatus]) -> List[Task]:
    """Filter with OR logic for multiple values."""
    return [task for task in tasks if task.status in statuses]


def filter_categories_any(tasks: List[Task], target_categories: List[str]) -> List[Task]:
    """Filter tasks that have ANY of the target categories (OR logic)."""
    return [
        task for task in tasks
        if any(cat in task.categories for cat in target_categories)
    ]


def filter_categories_all(tasks: List[Task], target_categories: List[str]) -> List[Task]:
    """Filter tasks that have ALL of the target categories (AND logic)."""
    return [
        task for task in tasks
        if all(cat in task.categories for cat in target_categories)
    ]


def filter_date_range(tasks: List[Task], start_date: datetime, end_date: datetime) -> List[Task]:
    """Filter tasks within a date range, handling None values."""
    return [
        task for task in tasks
        if task.due_date is not None and start_date <= task.due_date <= end_date
    ]


def filter_composite(tasks: List[Task],
                     statuses: Optional[List[TaskStatus]] = None,
                     priorities: Optional[List[Priority]] = None,
                     categories: Optional[List[str]] = None,
                     has_due_date: Optional[bool] = None) -> List[Task]:
    """Composite filter with multiple optional criteria."""
    results = tasks

    if statuses:
        results = [t for t in results if t.status in statuses]

    if priorities:
        results = [t for t in results if t.priority in priorities]

    if categories:
        results = [t for t in results if any(cat in t.categories for cat in categories)]

    if has_due_date is not None:
        if has_due_date:
            results = [t for t in results if t.due_date is not None]
        else:
            results = [t for t in results if t.due_date is None]

    return results


def filter_chained(tasks: List[Task],
                   statuses: Optional[List[TaskStatus]] = None,
                   priorities: Optional[List[Priority]] = None) -> List[Task]:
    """Chained filtering approach (functional style)."""
    result = tasks

    if statuses:
        result = filter(lambda t: t.status in statuses, result)

    if priorities:
        result = filter(lambda t: t.priority in priorities, result)

    return list(result)


# ============================================================================
# SORT PATTERNS
# ============================================================================

def sort_single_key(tasks: List[Task]) -> List[Task]:
    """Sort by single key (priority)."""
    return sorted(tasks, key=lambda t: t.priority.value, reverse=True)


def sort_multi_level(tasks: List[Task]) -> List[Task]:
    """Multi-level sort: primary by due_date, secondary by priority."""
    return sorted(
        tasks,
        key=lambda t: (
            t.due_date if t.due_date is not None else datetime.max,  # None values last
            -t.priority.value  # Higher priority first (negative for reverse)
        )
    )


def sort_none_first(tasks: List[Task]) -> List[Task]:
    """Sort with None values first."""
    return sorted(
        tasks,
        key=lambda t: (t.due_date is not None, t.due_date)
    )


def sort_none_last(tasks: List[Task]) -> List[Task]:
    """Sort with None values last."""
    return sorted(
        tasks,
        key=lambda t: (t.due_date if t.due_date is not None else datetime.max)
    )


def sort_complex_multi_level(tasks: List[Task]) -> List[Task]:
    """Complex multi-level sort with multiple criteria."""
    return sorted(
        tasks,
        key=lambda t: (
            t.status.value,  # Group by status
            t.due_date if t.due_date is not None else datetime.max,  # Then by due date
            -t.priority.value,  # Then by priority (high to low)
            t.title.lower()  # Finally by title alphabetically
        )
    )


def sort_with_operator_itemgetter(tasks: List[Task]) -> List[Task]:
    """Sort using operator.attrgetter (slightly faster for simple cases)."""
    from operator import attrgetter
    return sorted(tasks, key=attrgetter('priority'))


# ============================================================================
# COMBINED OPERATIONS
# ============================================================================

def search_filter_sort_combined(tasks: List[Task],
                                 keyword: str,
                                 statuses: List[TaskStatus],
                                 categories: List[str]) -> List[Task]:
    """Realistic combined operation: search + filter + sort."""
    keyword_lower = keyword.lower()

    # Search
    results = [
        task for task in tasks
        if keyword_lower in task.title.lower() or keyword_lower in task.description.lower()
    ]

    # Filter by status
    results = [task for task in results if task.status in statuses]

    # Filter by categories (any match)
    results = [
        task for task in results
        if any(cat in task.categories for cat in categories)
    ]

    # Sort by due date (None last) then priority
    results = sorted(
        results,
        key=lambda t: (
            t.due_date if t.due_date is not None else datetime.max,
            -t.priority.value
        )
    )

    return results


def search_filter_sort_optimized(tasks: List[Task],
                                  keyword: str,
                                  statuses: List[TaskStatus],
                                  categories: List[str]) -> List[Task]:
    """Optimized version with early filtering."""
    keyword_lower = keyword.lower()
    status_set = set(statuses)  # Set lookup is O(1)
    category_set = set(categories)

    # Combined filter in single pass
    results = [
        task for task in tasks
        if (keyword_lower in task.title.lower() or keyword_lower in task.description.lower())
        and task.status in status_set
        and any(cat in category_set for cat in task.categories)
    ]

    # Sort
    results.sort(
        key=lambda t: (
            t.due_date if t.due_date is not None else datetime.max,
            -t.priority.value
        )
    )

    return results


# ============================================================================
# BENCHMARK RUNNER
# ============================================================================

def run_benchmarks():
    """Run all benchmarks and display results."""
    print("=" * 80)
    print("SEARCH, FILTER, SORT PERFORMANCE BENCHMARKS")
    print("=" * 80)
    print(f"Dataset size: 1000 tasks")
    print(f"Iterations per test: 100")
    print(f"Target: <500ms per operation")
    print("=" * 80)
    print()

    # Generate test data
    tasks = generate_test_data(1000)

    # ========================================================================
    # SEARCH BENCHMARKS
    # ========================================================================
    print("SEARCH PATTERNS (keyword: 'bug')")
    print("-" * 80)

    search_tests = [
        ("List Comprehension", search_list_comprehension),
        ("filter() Function", search_filter_function),
        ("Generator Expression", search_generator_expression),
        ("Explicit Loop", search_explicit_loop),
        ("any() with Fields", search_any_fields),
    ]

    for name, func in search_tests:
        result = benchmark(func, tasks, "bug")
        print(f"{name:25} | Avg: {result['avg_ms']:6.3f}ms | Min: {result['min_ms']:6.3f}ms | Max: {result['max_ms']:6.3f}ms | Results: {result['result_count']}")

    print()

    # ========================================================================
    # FILTER BENCHMARKS
    # ========================================================================
    print("FILTER PATTERNS")
    print("-" * 80)

    filter_tests = [
        ("Single Criterion", lambda t: filter_single_criterion(t, TaskStatus.PENDING)),
        ("Multiple AND", lambda t: filter_multiple_and(t, TaskStatus.PENDING, Priority.HIGH)),
        ("Multiple OR", lambda t: filter_multiple_or(t, [TaskStatus.PENDING, TaskStatus.IN_PROGRESS])),
        ("Categories ANY", lambda t: filter_categories_any(t, ["work", "urgent"])),
        ("Categories ALL", lambda t: filter_categories_all(t, ["work", "urgent"])),
        ("Date Range", lambda t: filter_date_range(t, datetime.now(), datetime.now() + timedelta(days=30))),
        ("Composite Filter", lambda t: filter_composite(t,
                                                         statuses=[TaskStatus.PENDING],
                                                         priorities=[Priority.HIGH, Priority.CRITICAL],
                                                         categories=["work", "urgent"])),
        ("Chained Filter", lambda t: filter_chained(t,
                                                     statuses=[TaskStatus.PENDING],
                                                     priorities=[Priority.HIGH, Priority.CRITICAL])),
    ]

    for name, func in filter_tests:
        result = benchmark(func, tasks)
        print(f"{name:25} | Avg: {result['avg_ms']:6.3f}ms | Min: {result['min_ms']:6.3f}ms | Max: {result['max_ms']:6.3f}ms | Results: {result['result_count']}")

    print()

    # ========================================================================
    # SORT BENCHMARKS
    # ========================================================================
    print("SORT PATTERNS")
    print("-" * 80)

    sort_tests = [
        ("Single Key", sort_single_key),
        ("Multi-level (2 keys)", sort_multi_level),
        ("None First", sort_none_first),
        ("None Last", sort_none_last),
        ("Complex Multi-level", sort_complex_multi_level),
    ]

    for name, func in sort_tests:
        result = benchmark(func, tasks)
        print(f"{name:25} | Avg: {result['avg_ms']:6.3f}ms | Min: {result['min_ms']:6.3f}ms | Max: {result['max_ms']:6.3f}ms")

    print()

    # ========================================================================
    # COMBINED OPERATIONS
    # ========================================================================
    print("COMBINED OPERATIONS (Search + Filter + Sort)")
    print("-" * 80)

    combined_tests = [
        ("Standard Approach", lambda t: search_filter_sort_combined(
            t, "bug", [TaskStatus.PENDING, TaskStatus.IN_PROGRESS], ["work", "urgent"]
        )),
        ("Optimized Approach", lambda t: search_filter_sort_optimized(
            t, "bug", [TaskStatus.PENDING, TaskStatus.IN_PROGRESS], ["work", "urgent"]
        )),
    ]

    for name, func in combined_tests:
        result = benchmark(func, tasks)
        print(f"{name:25} | Avg: {result['avg_ms']:6.3f}ms | Min: {result['min_ms']:6.3f}ms | Max: {result['max_ms']:6.3f}ms | Results: {result['result_count']}")

    print()
    print("=" * 80)
    print("BENCHMARK COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmarks()
