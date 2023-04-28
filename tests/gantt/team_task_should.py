from datetime import date
import pytest
from src.agileffp.gantt.capacity_team import CapacityTeam
from src.agileffp.gantt.team_task import TeamTask


@pytest.fixture
def task1():
    return TeamTask("sample_task", "team1", 10)


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
