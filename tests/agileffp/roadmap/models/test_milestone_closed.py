from datetime import date

import pytest

from agileffp.roadmap.models.developers_team import Team
from agileffp.roadmap.models.iteration import Iteration
from agileffp.roadmap.models.milestone import Milestone


@pytest.fixture
def sample_milestone():
    return Milestone(
        name="Sample Milestone",
        items={"team1": 10, "team2": 5},
    )


@pytest.fixture
def unplanned_milestone():
    return Milestone(
        name="Sample Milestone 2",
        items={"team1": 10, "team2": 5},
    )


@pytest.fixture
def sample_milestones(sample_milestone, unplanned_milestone):
    return {
        sample_milestone.name: sample_milestone,
        unplanned_milestone.name: unplanned_milestone
    }


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
            closed={"dev1": {"Sample Milestone": 3}, "dev2": {
                "Sample Milestone": 2}, "dev3": {"Sample Milestone": 3}}
        ),
        Iteration(
            name="Iteration 2",
            start=date(2025, 1, 16),
            end=date(2025, 1, 31),
            capacity={"dev1": 2, "dev2": 1, "dev3": 2},
            closed={"dev1": {"Sample Milestone": 2}, "dev2": {
                "Sample Milestone": 1}, "dev3": {"Sample Milestone": 2}}
        )
    ]


def test_milestones_parents(sample_milestone, unplanned_milestone, sample_milestones):
    unplanned_milestone.depends_on = ["Sample Milestone"]
    sample_milestone.reference_parents(sample_milestones)
    unplanned_milestone.reference_parents(sample_milestones)
    assert sample_milestone._parents == []
    assert unplanned_milestone._parents == [sample_milestone]


def test_team_effort_done(sample_milestone, sample_teams, sample_iterations):
    sample_milestone.compute_work_already_done(sample_iterations, sample_teams)
    assert sample_milestone.team_effort_done(
        sample_teams[0]) == 8  # 3+2+2+1 for team1
    assert sample_milestone.team_effort_done(sample_teams[1]) == 5  # 3+2 for team2


def test_team_with_no_work(sample_milestone, sample_teams, sample_iterations):
    sample_teams.append(Team(name="team3", members=["dev4"], days=30))
    sample_milestone.compute_work_already_done(sample_iterations, sample_teams)
    assert sample_milestone.team_effort_done(
        sample_teams[0]) == 8  # 3+2+2+1 for team1
    assert sample_milestone.team_effort_done(sample_teams[1]) == 5  # 3+2 for team2


def test_team_remaining_items(sample_milestone, sample_teams, sample_iterations):
    sample_milestone.compute_work_already_done(sample_iterations, sample_teams)
    assert sample_milestone.team_remaining_items(
        sample_teams[0]) == 2  # Two items remaining
    assert sample_milestone.team_remaining_items(
        sample_teams[1]) == 0  # All items completed


def test_is_closed(sample_milestone, sample_teams, sample_iterations):
    sample_milestone.compute_work_already_done(sample_iterations, sample_teams)
    assert sample_milestone.is_closed is False  # Two items remaining


def test_iterations_list(sample_milestone, sample_teams, sample_iterations):
    sample_milestone.compute_work_already_done(sample_iterations, sample_teams)
    assert len(sample_milestone.iterations) == 2
    assert sample_milestone.iterations[0].name == "Iteration 1"
    assert sample_milestone.iterations[1].name == "Iteration 2"


def test_unplanned_milestone(unplanned_milestone, sample_teams, sample_iterations):
    unplanned_milestone.compute_work_already_done(sample_iterations, sample_teams)
    assert unplanned_milestone.team_effort_done(sample_teams[0]) == 0
    assert unplanned_milestone.team_remaining_items(sample_teams[0]) == 10
    assert unplanned_milestone.is_closed is False


def test_unplanned_milestone_iterations(unplanned_milestone, sample_teams, sample_iterations):
    unplanned_milestone.compute_work_already_done(sample_iterations, sample_teams)
    assert unplanned_milestone.iterations == []
