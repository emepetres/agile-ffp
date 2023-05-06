import pytest
from agileffp.milestone.estimation import EstimationTask


@pytest.fixture
def estimation_yml():
    return {
        "estimation": [
            {
                "name": "epic1",
                "totals": {"team1": 10, "team2": 13},
                "tasks": [
                    {"name": "task1", "ref": 1.1, "effort": {"team1": 5, "team2": 6}},
                    {"name": "task2", "ref": 1.2, "effort": {"team1": 4, "team2": 5}},
                ],
            },
            {
                "name": "epic2",
                "totals": {"team1": 18, "team3": 90},
                "tasks": [
                    {"name": "task1", "ref": 2.1, "effort": {"team1": 7, "team3": 40}},
                    {"name": "task2", "ref": 2.2, "effort": {"team1": 6, "team3": 40}},
                ],
            },
        ]
    }


def assert_parse_format():
    data = {"wrong": [{"name": "epic1"}]}
    with pytest.raises(ValueError):
        EstimationTask.parse(data)


def assert_parse_list(estimation_yml):
    estimation = EstimationTask.parse(estimation_yml)
    assert len(estimation) == 4

    task_ids = [t.ref for t in estimation]
    assert 1.1 in task_ids
    assert 1.2 in task_ids
    assert 2.1 in task_ids
    assert 2.2 in task_ids
