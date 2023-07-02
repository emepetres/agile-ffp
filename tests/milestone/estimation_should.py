from datetime import date
import pytest
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.milestone.estimation import parse_estimation


@pytest.fixture
def estimation_yml():
    return {
        "estimation": [
            {
                "name": "epic1",
                "totals": {"team1": 10, "team2": 13},
                "tasks": [
                    {
                        "name": "task1",
                        "ref": 1.1,
                        "estimated": {"team1": 5, "team2": 6},
                    },
                    {
                        "name": "task2",
                        "ref": 1.2,
                        "estimated": {"team1": 4, "team2": 5},
                    },
                ],
            },
            {
                "name": "epic2",
                "totals": {"team1": 18, "team3": 90},
                "tasks": [
                    {
                        "name": "task1",
                        "ref": 2.1,
                        "estimated": {"team1": 7, "team3": 40},
                    },
                    {
                        "name": "task2",
                        "ref": 2.2,
                        "estimated": {"team1": 6, "team3": 40},
                    },
                ],
            },
        ]
    }


@pytest.fixture
def capacity():
    return {
        "team1": CapacityTeam("team1", 2, date(2023, 1, 1), price=520),
        "team2": CapacityTeam("team2", 3, date(2023, 1, 1), price=480),
        "team3": CapacityTeam("team3", 2, date(2023, 1, 1), price=520),
    }


def assert_parse_format():
    data = {"wrong": [{"name": "epic1"}]}
    with pytest.raises(ValueError):
        parse_estimation(data)


def assert_parse_list(estimation_yml):
    estimation = parse_estimation(estimation_yml)
    assert len(estimation) == 4

    task_ids = [t.ref for t in estimation.values()]
    assert "1.1" in task_ids
    assert "1.2" in task_ids
    assert "2.1" in task_ids
    assert "2.2" in task_ids


def assert_computed_effort(estimation_yml):
    estimation = parse_estimation(estimation_yml)

    assert estimation["1.1"].computed_effort["team1"] == pytest.approx(5.55, 0.01)
    assert estimation["1.1"].computed_effort["team2"] == pytest.approx(7.09, 0.01)


def assert_computed_price(estimation_yml, capacity):
    estimation = parse_estimation(estimation_yml)
    for task in estimation.values():
        task.compute_price(capacity.values())

    assert estimation["1.1"].price == 6293
    assert estimation["1.2"].price == 5147
    assert estimation["2.1"].price == 28440
    assert estimation["2.2"].price == 27720
