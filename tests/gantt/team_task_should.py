from datetime import date
import pytest
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.gantt.team_task import TeamTask


@pytest.fixture
def task1():
    return TeamTask("sample_task", "team1", 10)


@pytest.fixture
def task2():
    return TeamTask("sample_task", "team1", {"effort": 10, "max_capacity": 1})


@pytest.fixture
def capacity1():
    return CapacityTeam("team1", 2, date(2023, 1, 1))


@pytest.fixture
def capacity2():
    return CapacityTeam("team2", 3, date(2023, 1, 1))


def assert_teams_must_match_when_assigning_capacity(task1, capacity2):
    with pytest.raises(ValueError):
        task1.assign_capacity(capacity2)


def assert_duration_according_to_capacity(task1, capacity1):
    task1.assign_capacity(capacity1)
    assert task1.init == date(2023, 1, 2)
    assert task1.end == date(2023, 1, 9)
    assert task1.days == 5


def assert_duration_according_to_max_capacity(task2, capacity1):
    task2.assign_capacity(capacity1)
    assert task2.init == date(2023, 1, 2)
    assert task2.end == date(2023, 1, 16)
    assert task2.days == 10


def assert_task_to_dict(task1, capacity1):
    task1.assign_capacity(capacity1)
    d = task1.to_dict()
    assert d == {
        "name": "team1",
        "init": "2023-01-02",
        "end": "2023-01-09",
        "days": 7,
        "depends_on": "sample_task",
    }
