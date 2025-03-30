from datetime import date

import pytest
import yaml

from agileffp.roadmap.models.developers_team import Team
from agileffp.roadmap.models.epic import Epic
from agileffp.roadmap.models.iteration import DefaultIteration, Iteration
from agileffp.roadmap.models.project import Project


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
def default_iteration():
    return DefaultIteration(
        index=6,
        days_interval=14,
        capacity={"dev1": 3, "dev2": 2, "dev3": 3})


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


def test_gantt_epic_dates(sample_teams, sample_iterations, sample_epics):
    sample_gantt = Project(teams=sample_teams,
                           iterations=sample_iterations, epics=sample_epics)

    closed_epic = next(
        epic for epic in sample_gantt.epics if epic.name == "Closed Epic")
    in_progress_epic = next(
        epic for epic in sample_gantt.epics if epic.name == "In Progress Epic")
    unstarted_epic = next(
        epic for epic in sample_gantt.epics if epic.name == "Unstarted Epic")

    assert closed_epic.start == date(2025, 1, 1)
    assert closed_epic.end == date(2025, 1, 31)
    assert closed_epic.is_closed is True
    assert closed_epic.is_planned is True

    assert in_progress_epic.start == date(2025, 2, 1)
    assert in_progress_epic.end == date(2025, 3, 15)
    assert in_progress_epic.is_closed is False
    assert in_progress_epic.is_planned is True

    assert unstarted_epic.start == date(2025, 2, 16)
    assert unstarted_epic.end == date(2025, 3, 15)
    assert unstarted_epic.is_closed is False
    assert unstarted_epic.is_planned is True


def test_gant_without_enough_iterations(sample_teams, sample_iterations, sample_epics):
    sample_epics = sample_epics[:-1]
    sample_epics.append(
        Epic(
            name="Unstarted Epic",
            items={"team1": 7, "team2": 4},
            planned={"dev2": 1, "dev3": 1}
        ))

    with pytest.raises(ValueError) as exc:
        Project(teams=sample_teams,
                iterations=sample_iterations, epics=sample_epics)
    assert "'team1': 0.0" in str(exc.value)
    assert "'team2': 1.0" in str(exc.value)


def test_gantt_with_default_iterations(sample_teams, sample_iterations, default_iteration, sample_epics):
    sample_epics = sample_epics[:-1]
    sample_epics.append(
        Epic(
            name="Unstarted Epic",
            items={"team1": 7, "team2": 4},
            planned={"dev2": 1, "dev3": 1}
        ))
    sample_gantt = Project(teams=sample_teams,
                           iterations=sample_iterations, default_iteration=default_iteration,
                           epics=sample_epics)
    unstarted_epic = next(
        epic for epic in sample_gantt.epics if epic.name == "Unstarted Epic")

    assert len(sample_gantt.iterations) == 6
    assert unstarted_epic.start == date(2025, 2, 16)
    assert unstarted_epic.end == date(2025, 3, 29)
    assert unstarted_epic.is_closed is False
    assert unstarted_epic.is_planned is True


def test_sample_template():
    with open('./samples/template.yaml', 'r') as file:
        data = file.read()
    yml_data = yaml.safe_load(data)
    gantt = Project(**yml_data)
    assert len(gantt.iterations) == 5
    assert len(gantt.sorted_epics) == 3
    assert gantt.sorted_epics[0].name == 'epic_one'
    assert gantt.sorted_epics[0].start == date(2025, 1, 5)
    assert gantt.sorted_epics[0].end == date(2025, 1, 18)
    assert gantt.sorted_epics[1].start == date(2025, 1, 5)
    assert gantt.sorted_epics[1].end == date(2025, 3, 3)


def test_complex_gantt():
    with open('./samples/adt3.yaml', 'r') as file:
        data = file.read()
    yml_data = yaml.safe_load(data)
    gantt = Project(**yml_data)
    assert len(gantt.iterations) == 17
    assert len(gantt.sorted_epics) == 8
    assert gantt.epics[0].name == 'Mejora arquitectura'
    assert gantt.epics[0].start == date(2024, 11, 20)
    assert gantt.epics[0].end == date(2025, 1, 14)
