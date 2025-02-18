from datetime import date

import pytest

from agileffp.roadmap.gantt import Gantt
from agileffp.roadmap.models.developers_team import Team
from agileffp.roadmap.models.epic import Epic
from agileffp.roadmap.models.iteration import Iteration


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
                "dev1": {"Closed Epic": 3},
                "dev2": {"Closed Epic": 2},
                "dev3": {"Closed Epic": 3}
            }
        ),
        Iteration(
            name="Iteration 2",
            start=date(2025, 1, 16),
            end=date(2025, 1, 31),
            capacity={"dev1": 2, "dev2": 1, "dev3": 2},
            closed={
                "dev1": {"Closed Epic": 2},
                "dev2": {"Closed Epic": 3},
                "dev3": {"Closed Epic": 2}
            }
        ),
        Iteration(
            name="Iteration 3",
            start=date(2025, 2, 1),
            end=date(2025, 2, 15),
            capacity={"dev1": 3, "dev2": 2, "dev3": 3},
            closed={
                "dev1": {"In Progress Epic": 3},
                "dev2": {"In Progress Epic": 2},
                "dev3": {"In Progress Epic": 2}
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


@pytest.fixture
def sample_epics():
    return [
        Epic(
            name="Closed Epic",
            items={"team1": 10, "team2": 5},
        ),
        Epic(
            name="In Progress Epic",
            items={"team1": 10, "team2": 5},
            planned={"dev1": 1, "dev3": 1}
        ),
        Epic(
            name="Unstarted Epic",
            items={"team1": 7, "team2": 3},
            planned={"dev2": 1, "dev3": 1}
        )
    ]


def test_planned_effort_in_iterations(sample_teams, sample_iterations, sample_epics):
    sample_gantt = Gantt(teams=sample_teams,
                         iterations=sample_iterations, epics=sample_epics)

    iteration_1 = sample_gantt.iterations[0].to_dict(sample_teams)
    iteration_2 = sample_gantt.iterations[1].to_dict(sample_teams)
    iteration_3 = sample_gantt.iterations[2].to_dict(sample_teams)
    iteration_4 = sample_gantt.iterations[3].to_dict(sample_teams)
    iteration_5 = sample_gantt.iterations[4].to_dict(sample_teams)

    assert iteration_1["[Items] dev1"] == "Closed Epic: 3.0"
    assert iteration_1["[Items] dev2"] == "Closed Epic: 2.0"
    assert iteration_1["[Items] dev3"] == "Closed Epic: 3.0"

    assert iteration_2["[Items] dev1"] == "Closed Epic: 2.0"
    assert iteration_2["[Items] dev2"] == "Closed Epic: 3.0"
    assert iteration_2["[Items] dev3"] == "Closed Epic: 2.0"

    assert iteration_3["[Items] dev1"] == "In Progress Epic: 3.0"
    assert iteration_3["[Items] dev2"] == "In Progress Epic: 2.0"
    assert iteration_3["[Items] dev3"] == "In Progress Epic: 2.0"

    assert iteration_4["[Items] dev1"] == "In Progress Epic: 3.0"
    assert iteration_4["[Items] dev2"] == "Unstarted Epic: 4.0"
    assert iteration_4["[Items] dev3"] == "In Progress Epic: 3.0"

    assert iteration_5["[Items] dev1"] == "In Progress Epic: 2.0"
    assert iteration_5["[Items] dev2"] == "Unstarted Epic: 3.0"
    assert iteration_5["[Items] dev3"] == "Unstarted Epic: 3.0"
