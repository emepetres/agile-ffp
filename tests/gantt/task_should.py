from datetime import date
import pytest
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.gantt.task import Task


@pytest.fixture
def task1():
    return Task("sample_task1", {"team1": 10, "team2": 13})


@pytest.fixture
def task2():
    return Task("sample_task2", {"team1": 10, "team2": 13})


@pytest.fixture
def task3():
    return Task("sample_task3", {"team3": 10})


@pytest.fixture
def wrong_task():
    return Task("wrong_task", {"team1": 10, "team3": 13})


@pytest.fixture
def capacity():
    return {
        "team1": CapacityTeam("team1", 2, date(2023, 1, 1)),
        "team2": CapacityTeam("team2", 3, date(2023, 1, 1)),
        "team3": CapacityTeam("team3", 2, date(2023, 1, 1)),
    }


def assert_teams_must_match_when_assigning_capacity(wrong_task, capacity):
    with pytest.raises(ValueError):
        wrong_task.assign_capacity(capacity)


def assert_duration_according_to_capacity(task1, task2, capacity):
    task1.assign_capacity(capacity)
    assert task1.init == date(2023, 1, 2)
    assert task1.end == date(2023, 1, 9)
    assert task1.days == 5
    task2.assign_capacity(capacity)
    assert task2.init == date(2023, 1, 9)
    assert task2.end == date(2023, 1, 16)
    assert task2.days == 6


def assert_force_init_date(task1, task3, capacity):
    task1.assign_capacity(capacity)
    assert task1.init == date(2023, 1, 2)
    assert task1.end == date(2023, 1, 9)
    assert task1.days == 5
    task3.assign_capacity(capacity, start_after=task1.end)
    assert task3.init == date(2023, 1, 10)
    assert task3.end == date(2023, 1, 16)
    assert task3.days == 5
