import pytest
from datetime import date


from agileffp.gantt.capacity_team import CapacityTeam


@pytest.fixture
def capacity():
    return CapacityTeam("team1", 2, date(2023, 1, 1))


@pytest.fixture
def summer_capacity():
    return CapacityTeam("team1", 2, date(2023, 6, 1))


def assert_no_capacity_before_start_day(capacity):
    assert capacity.capacity_at(date(2022, 12, 31)) == 0


def assert_no_capacity_after_end_day(capacity):
    assert capacity.capacity_at(date(2024, 1, 1)) == 0


def return_no_capacity_at_non_workday(capacity):
    assert capacity.capacity_at(date(2023, 1, 1)) == 0
    # # assert capacity.capacity_at(date(2023, 1, 2)) == 0
    assert capacity.capacity_at(date(2023, 4, 26)) == 0


def assert_full_capacity_at_unassigned_workday(capacity):
    assert capacity.capacity_at(date(2023, 1, 4)) == 2


def assert_no_capacity_at_assigned_workday(capacity):
    workday = date(2023, 1, 4)
    assert capacity.capacity_at(workday) == 2
    capacity.assign_effort("task1", 10)
    assert capacity.capacity_at(workday) == 0


def assert_capacity_on_partially_assigned_workday(capacity):
    workday = date(2023, 1, 4)
    assert capacity.capacity_at(workday) == 2
    capacity.assign_effort("task1", 10, max_capacity=1)
    assert capacity.capacity_at(workday) == 1


def assert_max_effort_init_end_dates(capacity):
    init, end, days = capacity.assign_effort("task1", 10)
    assert init == date(2023, 1, 2)
    assert end == date(2023, 1, 9)
    assert days == 5


def assert_half_effort_init_end_dates(capacity):
    init, end, days = capacity.assign_effort("task1", 10, 1)
    assert init == date(2023, 1, 2)
    assert end == date(2023, 1, 16)
    assert days == 10


def assert_half_effort_on_vacation_months(summer_capacity):
    init, end, days = summer_capacity.assign_effort("task1", 10)
    assert init == date(2023, 6, 1)
    assert end == date(2023, 6, 15)
    assert days == 10


def assert_timeline_empty_if_no_assigned(capacity):
    tl = capacity.to_timeline()
    assert len(tl) == 0


def assert_timeline(capacity):
    capacity.assign_effort("task1", 10)
    tl = capacity.to_timeline()
    assert len(tl) == 1
    assert tl[0] == {
        "team": "team1",
        "task": "task1",
        "start": "2023-01-02",
        "end": "2023-01-09",
    }


def assert_max_effort_sequential_timeline(capacity):
    capacity.assign_effort("task1", 10)
    capacity.assign_effort("task2", 5)
    tl = capacity.to_timeline()
    assert len(tl) == 2
    assert tl[0] == {
        "team": "team1",
        "task": "task1",
        "start": "2023-01-02",
        "end": "2023-01-09",
    }
    assert tl[1] == {
        "team": "team1",
        "task": "task2",
        "start": "2023-01-10",
        "end": "2023-01-12",
    }


def assert_half_effort_overlapped_timeline(capacity):
    capacity.assign_effort("task1", 10, 1)
    capacity.assign_effort("task2", 15, 1)
    tl = capacity.to_timeline()
    assert len(tl) == 2
    assert tl[0] == {
        "team": "team1",
        "task": "task1",
        "start": "2023-01-02",
        "end": "2023-01-16",
    }
    assert tl[1] == {
        "team": "team1",
        "task": "task2",
        "start": "2023-01-02",
        "end": "2023-01-23",
    }
