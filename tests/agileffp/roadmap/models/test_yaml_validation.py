from datetime import date
from textwrap import dedent

import pytest
import yaml

from agileffp.roadmap.models.developers_team import Team
from agileffp.roadmap.models.iteration import Iteration
from agileffp.roadmap.models.milestone import Milestone


@pytest.fixture
def team_yaml() -> str:
    return dedent("""
        name: AI
        members:
            - Gabriel
            - Iker
        days: 20
    """)


@pytest.fixture
def milestone_yaml() -> str:
    return dedent("""
        name: Mejora arquitectura
        items:
            AI: 7
        description: >
            Se debe mejorar la arquitectura de la aplicación
            para soportar la nueva funcionalidad.
        priority: 30
        depends_on:
            - Habilitar trabajo paralelo
            - PoC 2D Alta calidad
        expected_cycle_time:
            Gabriel: 3
            Iker: 3
    """)


@pytest.fixture
def past_iteration_yaml():
    return dedent("""
        name: 11
        start: 2024-11-20
        end: 2024-12-03
        capacity:
            Gabriel: 9
            Iker: 8
        closed:
            Gabriel:
                Mejora arquitectura: 1
                Habilitar trabajo paralelo: 2
            Iker:
                PoC 2D Alta calidad: 1
    """)


@pytest.fixture
def future_iteration_yaml() -> str:
    return dedent("""
        name: 17
        start: 2025-03-12
        end: 2025-03-25
        capacity:
            Gabriel: 10
    """)


def test_team_yaml_validation(team_yaml: str):
    data = yaml.safe_load(team_yaml)
    team = Team(**data)

    assert team.name == "AI"
    assert team.members == ["Gabriel", "Iker"]
    assert team.days == 20


def test_milestone_yaml_validation(milestone_yaml: str):
    data = yaml.safe_load(milestone_yaml)
    milestone = Milestone(**data)

    assert milestone.name == "Mejora arquitectura"
    assert milestone.items == {"AI": 7}
    assert milestone.priority == 30
    assert milestone.depends_on == [
        "Habilitar trabajo paralelo",
        "PoC 2D Alta calidad",
    ]
    assert milestone.planned == {"Gabriel": 3, "Iker": 3}


def test_past_iteration_yaml_validation(past_iteration_yaml: str):
    data = yaml.safe_load(past_iteration_yaml)
    iteration = Iteration(**data)

    assert iteration.name == "11"
    assert iteration.start == date(2024, 11, 20)
    assert iteration.end == date(2024, 12, 3)
    assert iteration.capacity == {
        "Gabriel": 9,
        "Iker": 8,
    }
    assert iteration.closed == {
        "Gabriel": {
            "Mejora arquitectura": 1,
            "Habilitar trabajo paralelo": 2,
        },
        "Iker": {
            "PoC 2D Alta calidad": 1,
        },
    }


def test_future_iteration_yaml_validation(future_iteration_yaml: str):
    data = yaml.safe_load(future_iteration_yaml)
    iteration = Iteration(**data)

    assert iteration.name == "17"
    assert iteration.start == date(2025, 3, 12)
    assert iteration.end == date(2025, 3, 25)
    assert iteration.capacity == {
        "Gabriel": 10,
    }
    assert iteration.closed is None
