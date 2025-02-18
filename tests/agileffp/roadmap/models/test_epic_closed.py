from datetime import date

import pytest

from agileffp.roadmap.models.developers_team import Team
from agileffp.roadmap.models.epic import Epic
from agileffp.roadmap.models.iteration import Iteration


@pytest.fixture
def sample_epic():
    return Epic(
        name="Sample Epic",
        items={"team1": 10, "team2": 5},
    )


@pytest.fixture
def unplanned_epic():
    return Epic(
        name="Sample Epic 2",
        items={"team1": 10, "team2": 5},
    )


@pytest.fixture
def sample_epics(sample_epic, unplanned_epic):
    return {
        sample_epic.name: sample_epic,
        unplanned_epic.name: unplanned_epic
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
            closed={"dev1": {"Sample Epic": 3}, "dev2": {
                "Sample Epic": 2}, "dev3": {"Sample Epic": 3}}
        ),
        Iteration(
            name="Iteration 2",
            start=date(2025, 1, 16),
            end=date(2025, 1, 31),
            capacity={"dev1": 2, "dev2": 1, "dev3": 2},
            closed={"dev1": {"Sample Epic": 2}, "dev2": {
                "Sample Epic": 1}, "dev3": {"Sample Epic": 2}}
        )
    ]


def test_epics_parents(sample_epic, unplanned_epic, sample_epics):
    unplanned_epic.depends_on = ["Sample Epic"]
    sample_epic.reference_parents(sample_epics)
    unplanned_epic.reference_parents(sample_epics)
    assert sample_epic._parents == []
    assert unplanned_epic._parents == [sample_epic]


def test_team_effort_done(sample_epic, sample_teams, sample_iterations):
    sample_epic.compute_work_already_done(sample_iterations, sample_teams)
    assert sample_epic.team_effort_done(
        sample_teams[0]) == 8  # 3+2+2+1 for team1
    assert sample_epic.team_effort_done(sample_teams[1]) == 5  # 3+2 for team2


def test_team_with_no_work(sample_epic, sample_teams, sample_iterations):
    sample_teams.append(Team(name="team3", members=["dev4"], days=30))
    sample_epic.compute_work_already_done(sample_iterations, sample_teams)
    assert sample_epic.team_effort_done(
        sample_teams[0]) == 8  # 3+2+2+1 for team1
    assert sample_epic.team_effort_done(sample_teams[1]) == 5  # 3+2 for team2


def test_team_remaining_items(sample_epic, sample_teams, sample_iterations):
    sample_epic.compute_work_already_done(sample_iterations, sample_teams)
    assert sample_epic.team_remaining_items(
        sample_teams[0]) == 2  # Two items remaining
    assert sample_epic.team_remaining_items(
        sample_teams[1]) == 0  # All items completed


def test_is_closed(sample_epic, sample_teams, sample_iterations):
    sample_epic.compute_work_already_done(sample_iterations, sample_teams)
    assert sample_epic.is_closed is False  # Two items remaining


def test_iterations_list(sample_epic, sample_teams, sample_iterations):
    sample_epic.compute_work_already_done(sample_iterations, sample_teams)
    assert len(sample_epic.iterations) == 2
    assert sample_epic.iterations[0].name == "Iteration 1"
    assert sample_epic.iterations[1].name == "Iteration 2"


def test_unplanned_epic(unplanned_epic, sample_teams, sample_iterations):
    unplanned_epic.compute_work_already_done(sample_iterations, sample_teams)
    assert unplanned_epic.team_effort_done(sample_teams[0]) == 0
    assert unplanned_epic.team_remaining_items(sample_teams[0]) == 10
    assert unplanned_epic.is_closed is False


def test_unplanned_epic_iterations(unplanned_epic, sample_teams, sample_iterations):
    unplanned_epic.compute_work_already_done(sample_iterations, sample_teams)
    assert unplanned_epic.iterations == []
