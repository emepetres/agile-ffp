from datetime import date

import pytest

from agileffp.roadmap.models.developers_team import Team
from agileffp.roadmap.models.iteration import Iteration


@pytest.fixture
def sample_team():
    return Team(name="devs", members=["dev1", "dev2"], days=30)


@pytest.fixture
def iteration_with_capacity():
    return Iteration(
        name="Iteration 1",
        start=date(2025, 1, 1),
        end=date(2025, 1, 15),
        capacity={"dev1": 12, "dev2": 15},
        closed=None
    )


@pytest.fixture
def iteration_no_capacity():
    return Iteration(
        name="Iteration 2",
        start=date(2025, 1, 1),
        end=date(2025, 1, 15),
        capacity={"dev1": 9, "dev2": 8},
        closed={
            "dev1": {"epic1": 5, "epic2": 5},
            "dev2": {"epic1": 10, "epic2": 5}
        }
    )


@pytest.fixture
def iteration_partial_capacity():
    return Iteration(
        name="Iteration 3",
        start=date(2025, 1, 1),
        end=date(2025, 1, 15),
        capacity={"dev1": 5, "dev2": 10},
        closed=None
    )


def test_try_to_assign_effort_no_capacity(iteration_no_capacity):
    assigned_effort = 0
    if iteration_no_capacity.capacity_available:
        assigned_effort = iteration_no_capacity.try_to_assign_effort(
            "dev1", 5)
    assert assigned_effort == 0


def test_try_to_assign_effort_with_capacity(iteration_with_capacity):
    if iteration_with_capacity.capacity_available:
        assigned_effort = iteration_with_capacity.try_to_assign_effort(
            "sample epic", "dev1", 10)
    assert assigned_effort == 10
    assert iteration_with_capacity._capacity_available["dev1"] == 2
    assert iteration_with_capacity._capacity_available["dev2"] == 15


def test_register_planned_items(iteration_with_capacity):
    iteration_with_capacity.register_planned_items("sample epic", "dev1", 10)
    assert len(iteration_with_capacity._planned) == 1
    assert iteration_with_capacity._planned["dev1"]["sample epic"] == 10


def test_try_to_assign_effort_partial_capacity(iteration_partial_capacity):
    if iteration_partial_capacity.capacity_available:
        assigned_effort = iteration_partial_capacity.try_to_assign_effort(
            "sample epic", "dev1", 10)
        assigned_effort += iteration_partial_capacity.try_to_assign_effort(
            "sample epic", "dev2", 7)
    assert assigned_effort == 12
    assert iteration_partial_capacity._capacity_available["dev1"] == 0
    assert iteration_partial_capacity._capacity_available["dev2"] == 3


def test_try_to_assign_effort_exceed_capacity(iteration_partial_capacity, sample_team):
    if iteration_partial_capacity.capacity_available:
        assigned_effort = iteration_partial_capacity.try_to_assign_effort(
            "sample epic", "dev1", 20)
        assigned_effort += iteration_partial_capacity.try_to_assign_effort(
            "sample epic", "dev2", 10)
    assert assigned_effort == 15
    assert iteration_partial_capacity._capacity_available["dev1"] == 0
    assert iteration_partial_capacity._capacity_available["dev2"] == 0
