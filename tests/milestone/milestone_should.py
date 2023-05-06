import pytest
from agileffp.milestone.milestone import Milestone
from agileffp.milestone.estimation import parse_estimation


@pytest.fixture
def milestones_yml():
    return {
        "milestones": [
            {"name": "milestone1", "tasks": [1.1, 1.2], "priority": 1},
            {
                "name": "milestone2",
                "tasks": [2.1, 2.2],
                "depends_on": ["milestone1"],
                "max_capacity": {"team1": 1},
            },
        ]
    }


@pytest.fixture
def estimation():
    return parse_estimation(
        {
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
    )


def assert_invalid_parse_format():
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
    assert m1.depends_on == []
    assert m1.max_capacity == {}

    m2 = milestones["milestone2"]
    assert m2.name == "milestone2"
    assert m2.priority == 99
    assert m2.tasks == [2.1, 2.2]
    assert m2.depends_on == ["milestone1"]
    assert m2.max_capacity == {"team1": 1}


def assert_compute_estimation(milestones_yml, estimation):
    milestones = Milestone.parse(milestones_yml)
    Milestone.compute(milestones.values(), estimation)

    assert milestones["milestone1"].estimated == {"team1": 10, "team2": 13}
    assert milestones["milestone2"].estimated == {"team1": 18, "team3": 90}


def assert_round_estimation(estimation):
    data = {"milestones": [{"name": "milestone1", "tasks": [1.1], "priority": 1}]}
    milestones = Milestone.parse(data)
    Milestone.compute(milestones.values(), estimation)

    assert milestones["milestone1"].estimated == {"team1": 6, "team2": 7}
