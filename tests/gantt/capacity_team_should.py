import pytest
from datetime import date


from src.agileffp.gantt.capacity_team import CapacityTeam
from src.agileffp.gantt.task import Task


@pytest.fixture
def task():
    return Task("example", 10)


@pytest.fixture
def capacity():
    return CapacityTeam("team1", 2, date(2023, 1, 1))


def assert_no_capacity_before_start_day(capacity):
    assert capacity.capacity_at(date(2022, 12, 31)) == 0


def assert_no_capacity_after_end_day(capacity):
    assert capacity.capacity_at(date(2024, 1, 1)) == 0


def return_no_capacity_at_non_workday(capacity):
    assert capacity.capacity_at(date(2023, 1, 1)) == 0
    # # assert capacity.capacity_at(date(2023, 1, 2)) == 0
    assert capacity.capacity_at(date(2023, 4, 26)) == 0


def assert_full_capacity_at_unassigned_workday(capacity, task):
    assert capacity.capacity_at(date(2023, 1, 4)) == 2


def assert_never_assign_more_than_available_capacity(capacity):
    assert capacity.reserve_capacity_at(date(2023, 6, 28), 3) == 2


def assert_never_assign_less_than_available_capacity(capacity):
    assert capacity.reserve_capacity_at(date(2023, 6, 28), 1) == 1


def assert_no_capacity_at_assigned_workday(capacity):
    workday = date(2023, 5, 4)
    assert capacity.capacity_at(workday) == 2
    capacity.reserve_capacity_at(workday, 2)
    assert capacity.capacity_at(workday) == 0
