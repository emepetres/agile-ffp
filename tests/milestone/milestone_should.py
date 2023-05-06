import pytest
from agileffp.milestone.milestone import Milestone


@pytest.fixture
def milestones_yml():
    return {
        "milestones": [
            {"name": "milestone1", "tasks": [1.1, 1.2], "priority": 1},
            {"name": "milestone2", "tasks": [2.1, 2.2], "depends_on": ["milestone1"]},
        ]
    }


def assert_parse_format():
    data = {"wrong": [{"name": "milestone1", "tasks": [1.1, 1.2], "priority": 1}]}

    with pytest.raises(SyntaxError):
        Milestone.parse(data)


def assert_parse_list(milestones_yml):
    milestones = Milestone.parse(milestones_yml)
    assert len(milestones) == 2

    m1 = milestones["milestone1"]
    assert m1.name == "milestone1"
    assert m1.priority == 1
    assert m1.tasks == [1.1, 1.2]

    m2 = milestones["milestone2"]
    assert m2.name == "milestone2"
    assert m2.priority == 99
    assert m2.tasks == [2.1, 2.2]
    assert m2.depends_on == ["milestone1"]
