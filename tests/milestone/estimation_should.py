import pytest
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


def assert_parse_format():
    data = {"wrong": [{"name": "epic1"}]}
    with pytest.raises(ValueError):
        parse_estimation(data)


def assert_parse_list(estimation_yml):
    estimation = parse_estimation(estimation_yml)
    assert len(estimation) == 4

    task_ids = [t.ref for t in estimation.values()]
    assert 1.1 in task_ids
    assert 1.2 in task_ids
    assert 2.1 in task_ids
    assert 2.2 in task_ids


def assert_computed_effort(estimation_yml):
    estimation = parse_estimation(estimation_yml)

    assert estimation[1.1].computed_effort["team1"] == pytest.approx(5.55, 0.01)
    assert estimation[1.1].computed_effort["team2"] == pytest.approx(7.09, 0.01)
