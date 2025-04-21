from datetime import date

import pytest
import yaml

from agileffp.roadmap.models.developers_team import Team
from agileffp.roadmap.models.iteration import DefaultIteration, Iteration
from agileffp.roadmap.models.milestone import Milestone
from agileffp.roadmap.models.planning import Planning


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


@pytest.fixture
def default_iteration():
    return DefaultIteration(
        index=6,
        days_interval=14,
        capacity={"dev1": 3, "dev2": 2, "dev3": 3})


@pytest.fixture
def sample_milestones():
    return [
        Milestone(
            name="Closed Milestone",
            items={"team1": 10, "team2": 5},
        ),
        Milestone(
            name="In Progress Milestone",
            items={"team1": 10, "team2": 5},
            planned={"dev1": 1, "dev3": 1}
        ),
        Milestone(
            name="Unstarted Milestone",
            items={"team1": 7, "team2": 3},
            planned={"dev2": 1, "dev3": 1}
        )
    ]


def test_planning_milestone_dates(sample_teams, sample_iterations, sample_milestones):
    sample_planning = Planning(teams=sample_teams,
                            iterations=sample_iterations, milestones=sample_milestones)

    closed_milestone = next(
        milestone for milestone in sample_planning.milestones if milestone.name == "Closed Milestone")
    in_progress_milestone = next(
        milestone for milestone in sample_planning.milestones if milestone.name == "In Progress Milestone")
    unstarted_milestone = next(
        milestone for milestone in sample_planning.milestones if milestone.name == "Unstarted Milestone")

    assert closed_milestone.start == date(2025, 1, 1)
    assert closed_milestone.end == date(2025, 1, 31)
    assert closed_milestone.is_closed is True
    assert closed_milestone.is_planned is True

    assert in_progress_milestone.start == date(2025, 2, 1)
    assert in_progress_milestone.end == date(2025, 3, 15)
    assert in_progress_milestone.is_closed is False
    assert in_progress_milestone.is_planned is True

    assert unstarted_milestone.start == date(2025, 2, 16)
    assert unstarted_milestone.end == date(2025, 3, 15)
    assert unstarted_milestone.is_closed is False
    assert unstarted_milestone.is_planned is True


def test_gant_without_enough_iterations(sample_teams, sample_iterations, sample_milestones):
    sample_milestones = sample_milestones[:-1]
    sample_milestones.append(
        Milestone(
            name="Unstarted Milestone",
            items={"team1": 7, "team2": 4},
            planned={"dev2": 1, "dev3": 1}
        ))

    with pytest.raises(ValueError) as exc:
        Planning(teams=sample_teams,
                 iterations=sample_iterations, milestones=sample_milestones)
    assert "'team1': 0.0" in str(exc.value)
    assert "'team2': 1.0" in str(exc.value)


def test_planning_with_default_iterations(sample_teams, sample_iterations, default_iteration, sample_milestones):
    sample_milestones = sample_milestones[:-1]
    sample_milestones.append(
        Milestone(
            name="Unstarted Milestone",
            items={"team1": 7, "team2": 4},
            planned={"dev2": 1, "dev3": 1}
        ))
    sample_planning = Planning(teams=sample_teams,
                            iterations=sample_iterations, default_iteration=default_iteration,
                            milestones=sample_milestones)
    unstarted_milestone = next(
        milestone for milestone in sample_planning.milestones if milestone.name == "Unstarted Milestone")

    assert len(sample_planning.iterations) == 6
    assert unstarted_milestone.start == date(2025, 2, 16)
    assert unstarted_milestone.end == date(2025, 3, 29)
    assert unstarted_milestone.is_closed is False
    assert unstarted_milestone.is_planned is True


def test_sample_template():
    with open('./samples/template.yaml', 'r') as file:
        data = file.read()
    yml_data = yaml.safe_load(data)
    planning = Planning(**yml_data)
    assert len(planning.iterations) == 5
    assert len(planning.sorted_milestones) == 3
    assert planning.sorted_milestones[0].name == 'milestone_one'
    assert planning.sorted_milestones[0].start == date(2025, 1, 5)
    assert planning.sorted_milestones[0].end == date(2025, 1, 18)
    assert planning.sorted_milestones[1].start == date(2025, 1, 5)
    assert planning.sorted_milestones[1].end == date(2025, 3, 3)


def test_complex_planning():
    with open('./samples/adt3.yaml', 'r') as file:
        data = file.read()
    yml_data = yaml.safe_load(data)
    planning = Planning(**yml_data)
    assert len(planning.iterations) == 17
    assert len(planning.sorted_milestones) == 8
    assert planning.milestones[0].name == 'Mejora arquitectura'
    assert planning.milestones[0].start == date(2024, 11, 20)
    assert planning.milestones[0].end == date(2025, 1, 14)
