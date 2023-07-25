from datetime import date
import pytest
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.gantt.estimated_task import EstimatedTask
from agileffp.milestone.estimation import parse_estimation
from agileffp.milestone.milestone import Milestone


@pytest.fixture
def task1():
    return EstimatedTask(
        "sample_task1", {"team1": 10, "team2": 13}, start_all_together=False
    )


@pytest.fixture
def task2():
    return EstimatedTask(
        "sample_task2", {"team1": 10, "team2": 13}, start_all_together=False
    )


@pytest.fixture
def task3():
    return EstimatedTask("sample_task3", {"team3": 10}, start_all_together=False)


@pytest.fixture
def wrong_task():
    return EstimatedTask("wrong_task", {"team1": 10, "wrong_team": 13})


@pytest.fixture
def capacity():
    return {
        "team1": CapacityTeam("team1", 2, date(2023, 1, 1), price=520),
        "team2": CapacityTeam("team2", 3, date(2023, 1, 1), price=480),
        "team3": CapacityTeam("team3", 2, date(2023, 1, 1), price=520),
    }


@pytest.fixture
def milestones():
    milestones = Milestone.parse(
        {
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
    )
    estimation = parse_estimation(
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
    Milestone.compute(milestones.values(), estimation)
    return milestones


def assert_teams_must_match_when_assigning_capacity(wrong_task, capacity):
    with pytest.raises(ValueError):
        wrong_task.assign_capacity(capacity)


def assert_duration_according_to_capacity(task1, task2, capacity):
    task1.assign_capacity(capacity)
    assert task1.init == date(2023, 1, 2)
    assert task1.end == date(2023, 1, 9)
    assert task1.days == 5
    task2.assign_capacity(capacity)
    assert task2.init == date(2023, 1, 9)
    assert task2.end == date(2023, 1, 16)
    assert task2.days == 6


def assert_force_init_date(task1, task3, capacity):
    task1.assign_capacity(capacity)
    assert task1.init == date(2023, 1, 2)
    assert task1.end == date(2023, 1, 9)
    assert task1.days == 5
    task3.assign_capacity(capacity, start_after=task1.end)
    assert task3.init == date(2023, 1, 10)
    assert task3.end == date(2023, 1, 16)
    assert task3.days == 5


def assert_start_all_together(task1, task2, capacity):
    task1.assign_capacity(capacity)
    assert task1.init == date(2023, 1, 2)
    assert task1.end == date(2023, 1, 9)
    assert task1.days == 5
    task2.start_all_together = True
    task2.assign_capacity(capacity)
    assert task2.init == date(2023, 1, 10)
    assert task2.end == date(2023, 1, 16)
    assert task2.days == 5


def assert_from_milestones(milestones):
    tasks = EstimatedTask.from_milestones(milestones.values())
    assert len(tasks) == 2

    dt = {t.name: t for t in tasks}
    assert dt["milestone1"].priority == 1
    assert dt["milestone1"].depends_on == []
    assert dt["milestone1"].teams_tasks["team1"].effort == 10
    assert dt["milestone1"].teams_tasks["team2"].effort == 13
    assert dt["milestone1"].description == "1.1, 1.2"

    assert dt["milestone2"].priority == 99
    assert dt["milestone2"].depends_on == ["milestone1"]
    assert dt["milestone2"].teams_tasks["team1"].effort == 18
    assert dt["milestone2"].teams_tasks["team1"].max_capacity == 1
    assert dt["milestone2"].teams_tasks["team3"].effort == 90
    assert dt["milestone2"].description == "2.1, 2.2"


def assert_price(task1, capacity):
    task1.assign_capacity(capacity)
    assert task1.price == 11440


def assert_common_available_day():
    c = {
        "team1": CapacityTeam("team1", 2, date(2023, 5, 8)),
        "team2": CapacityTeam("team2", 2, date(2023, 5, 8)),
    }
    t1 = EstimatedTask("t1", {"team1": 10})
    t2 = EstimatedTask("t2", {"team2": 10})
    t1.assign_capacity(c)
    t2.assign_capacity(c, start_after=date(2023, 5, 12))
    t3 = EstimatedTask("t3", {"team1": 10, "team2": 10})
    t3.assign_capacity(c)
    assert t3.init == date(2023, 5, 22)
    assert t3.days == 5
