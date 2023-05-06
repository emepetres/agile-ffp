import pytest
from agileffp.milestone.estimation import Estimation


@pytest.fixture
def estimation_yml():
    return {
        "estimation": [
            {
                "name": "epic1",
                "global": {"team1": 10, "team2": 13},
                "tasks": [
                    {"name": "task1", "id": 1.1, "effort": {"team1": 5, "team2": 6}},
                    {"name": "task2", "id": 1.2, "effort": {"team1": 4, "team2": 5}},
                ],
            },
            {
                "name": "epic2",
                "global": {"team1": 18, "team3": 90},
                "tasks": [
                    {"name": "task1", "id": 2.1, "effort": {"team1": 7, "team3": 40}},
                    {"name": "task2", "id": 2.2, "effort": {"team1": 6, "team3": 40}},
                ],
            },
        ]
    }


def assert_parse_format():
    data = {"wrong": [{"name": "epic1"}]}
    with pytest.raises(ValueError):
        Estimation.parse(data)


def assert_parse_list(estimation_yml):
    estimation = Estimation.parse(estimation_yml)
    assert len(estimation) == 2

    e1 = estimation["epic1"]
    assert e1.name == "epic1"

    e2 = estimation["epic2"]
    assert e2.name == "epic2"
