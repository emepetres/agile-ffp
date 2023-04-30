from datetime import date
import pytest
from agileffp.gantt.gantt import Gantt
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.gantt.task import Task


@pytest.fixture
def sequential2():
    return Gantt(
        [
            Task(
                "sample_task2", {"team1": 10, "team2": 13}, depends_on=["sample_task1"]
            ),
            Task("sample_task1", {"team1": 10, "team2": 13}),
        ]
    )


@pytest.fixture
def two_children_with_priority():
    return Gantt(
        [
            Task(
                "sample_task3",
                {"team1": 10, "team2": 13},
                depends_on=["sample_task1"],
                priority=3,
            ),
            Task(
                "sample_task2",
                {"team1": 20, "team2": 13},
                depends_on=["sample_task1"],
                priority=2,
            ),
            Task("sample_task1", {"team1": 10, "team2": 13}),
        ]
    )


@pytest.fixture
def wrong_tasks_dependencies():
    return [
        Task("sample_task2", {"team1": 10, "team2": 13}, depends_on=["sample_task1"]),
        Task("sample_task1", {"team1": 10, "team2": 13}),
        Task("wrong_task", {"team1": 10, "team3": 13}, depends_on=["sample_task22"]),
    ]


@pytest.fixture
def capacity():
    return {
        "team1": CapacityTeam("team1", 2, date(2023, 1, 1)),
        "team2": CapacityTeam("team2", 3, date(2023, 1, 1)),
    }


def assert_dependencies_must_match(wrong_tasks_dependencies):
    with pytest.raises(ValueError):
        Gantt(wrong_tasks_dependencies)


def assert_duration_according_to_capacity(sequential2, capacity):
    sequential2.build(capacity)
    task1 = sequential2.nodes["sample_task1"].task
    task2 = sequential2.nodes["sample_task2"].task
    assert task1.init == date(2023, 1, 2)
    assert task1.end == date(2023, 1, 9)
    assert task1.days == 5
    assert task2.init == date(2023, 1, 9)
    assert task2.end == date(2023, 1, 16)
    assert task2.days == 6


def assert_duration_according_to_priority(two_children_with_priority, capacity):
    two_children_with_priority.build(capacity)
    task1 = two_children_with_priority.nodes["sample_task1"].task
    task2 = two_children_with_priority.nodes["sample_task2"].task
    task3 = two_children_with_priority.nodes["sample_task3"].task
    assert task1.init == date(2023, 1, 2)
    assert task1.end == date(2023, 1, 9)
    assert task1.days == 5
    assert task2.init == date(2023, 1, 9)
    assert task2.end == date(2023, 1, 23)
    assert task2.days == 11
    assert task3.init == date(2023, 1, 13)
    assert task3.end == date(2023, 1, 30)
    assert task3.days == 12
