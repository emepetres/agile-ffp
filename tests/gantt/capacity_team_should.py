import pytest

from src.agileffp.gantt.capacity_team import CapacityTeam
from src.agileffp.gantt.task import Task
from datetime import date


@pytest.fixture
def task():
    return Task("example", 10)


@pytest.fixture
def capacity():
    return CapacityTeam("team1", 2, date(2023, 1, 1))


def return_max_capacity_at_free_workday(capacity):
    assert capacity.capacity_at(date(2023, 1, 1)) == 2


def return_no_capacity_before_start_day(capacity):
    assert capacity.capacity_at(date(2022, 12, 31)) == 0


def return_no_capacity_at_assigned_workday(capacity, task):
    capacity.reserve_capacity_at(date(2023, 1, 1), 2, task)
    assert capacity.capacity_at(date(2023, 1, 1)) == 0
