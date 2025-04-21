from datetime import date

import pytest

from agileffp.roadmap.models.developers_team import Team
from agileffp.roadmap.models.iteration import Iteration
from agileffp.roadmap.models.milestone import Milestone


@pytest.fixture
def closed_milestone():
    return Milestone(
        name="Closed Milestone",
        items={"team1": 10, "team2": 5},
    )


@pytest.fixture
def in_progress_milestone():
    return Milestone(
        name="In Progress Milestone",
        items={"team1": 10, "team2": 5},
        planned={"dev1": 1, "dev3": 1}
    )


@pytest.fixture
def unstarted_milestone():
    return Milestone(
        name="Unstarted Milestone",
        items={"team1": 7, "team2": 4},
        planned={"dev2": 1, "dev3": 1}
    )


@pytest.fixture
def sample_teams():
    return [
        Team(name="team1", members=["dev1", "dev2"], days=30),
        Team(name="team2", members=["dev3"], days=30)
    ]


@pytest.fixture
def sample_iterations():
    return [
        Iteration(
            name="Iteration 1",
            start=date(2025, 1, 1),
            end=date(2025, 1, 15),
            capacity={"dev1": 3, "dev2": 2, "dev3": 3},
            closed={
                "dev1": {"Closed Milestone": 3},
                "dev2": {"Closed Milestone": 2},
                "dev3": {"Closed Milestone": 3}
            }
        ),
        Iteration(
            name="Iteration 2",
            start=date(2025, 1, 16),
            end=date(2025, 1, 31),
            capacity={"dev1": 2, "dev2": 1, "dev3": 2},
            closed={
                "dev1": {"Closed Milestone": 2},
                "dev2": {"Closed Milestone": 3},
                "dev3": {"Closed Milestone": 2}
            }
        ),
        Iteration(
            name="Iteration 3",
            start=date(2025, 2, 1),
            end=date(2025, 2, 15),
            capacity={"dev1": 3, "dev2": 2, "dev3": 3},
            closed={
                "dev1": {"In Progress Milestone": 3},
                "dev2": {"In Progress Milestone": 2},
                "dev3": {"In Progress Milestone": 2}
            }
        ),
        Iteration(
            name="Iteration 4",
            start=date(2025, 2, 16),
            end=date(2025, 2, 28),
            capacity={"dev1": 3, "dev2": 4, "dev3": 3},
            closed={}
        ),
        Iteration(
            name="Iteration 5",
            start=date(2025, 3, 1),
            end=date(2025, 3, 15),
            capacity={"dev1": 3, "dev2": 4, "dev3": 3},
            closed={}
        )
    ]


def test_plan_closed_milestone(closed_milestone, sample_teams, sample_iterations):
    closed_milestone.compute_work_already_done(sample_iterations, sample_teams)
    closed_milestone.plan_remaining_work(sample_iterations, sample_teams)
    assert closed_milestone.is_closed is True
    assert closed_milestone.is_planned is True
    assert closed_milestone.start == date(2025, 1, 1)
    assert closed_milestone.end == date(2025, 1, 31)
    assert len(closed_milestone.iterations) == 2


def test_plan_inprogress_milestone(in_progress_milestone, sample_teams, sample_iterations):
    in_progress_milestone.compute_work_already_done(sample_iterations, sample_teams)
    in_progress_milestone.plan_remaining_work(sample_iterations, sample_teams)
    assert in_progress_milestone.is_closed is False
    assert in_progress_milestone.is_planned is True
    assert in_progress_milestone.start == date(2025, 2, 1)
    assert in_progress_milestone.end == date(2025, 3, 15)
    assert len(in_progress_milestone.iterations) == 3


def test_plan_unstarted_milestone(unstarted_milestone, sample_teams, sample_iterations):
    unstarted_milestone.compute_work_already_done(sample_iterations, sample_teams)
    unstarted_milestone.plan_remaining_work(sample_iterations, sample_teams)
    assert unstarted_milestone.is_closed is False
    assert unstarted_milestone.is_planned is True
    assert unstarted_milestone.start == date(2025, 2, 16)
    assert unstarted_milestone.end == date(2025, 3, 15)
    assert len(unstarted_milestone.iterations) == 2