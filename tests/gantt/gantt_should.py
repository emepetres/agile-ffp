from datetime import date
import pytest
from agileffp.gantt.gantt import Gantt
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.gantt.estimated_task import EstimatedTask


@pytest.fixture
def sequential2():
    return [
        EstimatedTask(
            "sample_task2", {"team1": 10, "team2": 13}, depends_on=["sample_task1"]
        ),
        EstimatedTask("sample_task1", {"team1": 10, "team2": 13}),
    ]


@pytest.fixture
def two_children_with_priority():
    return [
        EstimatedTask(
            "sample_task3",
            {"team1": 10, "team2": 13},
            depends_on=["sample_task1"],
            priority=3,
            start_all_together=False,
        ),
        EstimatedTask(
            "sample_task2",
            {"team1": 20, "team2": 13},
            depends_on=["sample_task1"],
            priority=2,
            start_all_together=False,
        ),
        EstimatedTask("sample_task1", {"team1": 10, "team2": 13}),
    ]


@pytest.fixture
def mixed_priority():
    return [
        EstimatedTask("sample_task1", {"team1": 10}),
        EstimatedTask(
            "sample_task2",
            {"team1": 20},
            depends_on=["sample_task1"],
            priority=2,
        ),
        EstimatedTask(
            "sample_task3",
            {"team1": 10},
            depends_on=["sample_task2"],
            priority=3,
        ),
        EstimatedTask(
            "sample_task4",
            {"team1": 10},
            depends_on=["sample_task1"],
        ),
    ]


@pytest.fixture
def wrong_tasks_dependencies():
    return [
        EstimatedTask(
            "sample_task2", {"team1": 10, "team2": 13}, depends_on=["sample_task1"]
        ),
        EstimatedTask("sample_task1", {"team1": 10, "team2": 13}),
        EstimatedTask(
            "wrong_task", {"team1": 10, "team3": 13}, depends_on=["sample_task22"]
        ),
    ]


@pytest.fixture
def capacity():
    return {
        "team1": CapacityTeam("team1", 2, date(2023, 1, 1)),
        "team2": CapacityTeam("team2", 3, date(2023, 1, 1)),
    }


@pytest.fixture
def assigned_tasks():
    return {
        "tasks": [
            {
                "name": "Visor",
                "start": "17/04/2023",
                "end": "28/07/2023",
                "price": 195100,
            },
            {
                "name": "SegDent",
                "start": "19/06/2023",
                "end": "01/09/2023",
                "price": 35880,
            },
            {
                "name": "IPRv1",
                "start": "31/07/2023",
                "end": "01/09/2023",
                "price": 44102.5,
            },
        ]
    }


def assert_read_sequential_tasks(sequential2):
    gantt = Gantt(sequential2)
    assert gantt is not None
    assert len(gantt.nodes) == 2

    node1 = gantt.nodes["sample_task1"]
    node2 = gantt.nodes["sample_task2"]
    assert node1.task.name == "sample_task1"

    gantt._compute_dependencies()
    assert node1.parent_nodes == []
    assert node1.next_nodes == [node2]
    assert node2.task.name == "sample_task2"
    assert node2.parent_nodes == [node1]
    assert node2.next_nodes == []


def assert_read_children_tasks(two_children_with_priority):
    gantt = Gantt(two_children_with_priority)
    assert gantt is not None
    assert len(gantt.nodes) == 3

    node1 = gantt.nodes["sample_task1"]
    node2 = gantt.nodes["sample_task2"]
    node3 = gantt.nodes["sample_task3"]

    gantt._compute_dependencies()
    assert node1.task.name == "sample_task1"
    assert node1.parent_nodes == []
    assert sorted(node1.next_nodes) == sorted([node2, node3])
    assert node2.task.name == "sample_task2"
    assert node2.parent_nodes == [node1]
    assert node2.next_nodes == []
    assert node3.task.name == "sample_task3"
    assert node3.parent_nodes == [node1]
    assert node3.next_nodes == []


def assert_dependencies_must_match(wrong_tasks_dependencies):
    with pytest.raises(ValueError):
        gantt = Gantt(wrong_tasks_dependencies)
        gantt._compute_dependencies()


def assert_duration_according_to_capacity(sequential2, capacity):
    gantt = Gantt(sequential2)
    gantt.assign_capacity(capacity)
    task1 = gantt.nodes["sample_task1"].task
    task2 = gantt.nodes["sample_task2"].task
    assert task1.start == date(2023, 1, 2)
    assert task1.end == date(2023, 1, 9)
    assert task1.days == 5
    assert task2.start == date(2023, 1, 10)
    assert task2.end == date(2023, 1, 16)
    assert task2.days == 5


def assert_duration_according_to_priority(two_children_with_priority, capacity):
    gantt = Gantt(two_children_with_priority)
    gantt.assign_capacity(capacity)
    task1 = gantt.nodes["sample_task1"].task
    task2 = gantt.nodes["sample_task2"].task
    task3 = gantt.nodes["sample_task3"].task
    assert task1.start == date(2023, 1, 2)
    assert task1.end == date(2023, 1, 9)
    assert task1.days == 5
    assert task2.start == date(2023, 1, 10)
    assert task2.end == date(2023, 1, 23)
    assert task2.days == 10
    assert task3.start == date(2023, 1, 16)
    assert task3.end == date(2023, 1, 30)
    assert task3.days == 11


def assert_priority_evaluation(mixed_priority, capacity):
    gantt = Gantt(mixed_priority)
    gantt.assign_capacity(capacity)
    task1 = gantt.nodes["sample_task1"].task
    task2 = gantt.nodes["sample_task2"].task
    task3 = gantt.nodes["sample_task3"].task
    task4 = gantt.nodes["sample_task4"].task
    assert task1.start < task2.start
    assert task2.start < task3.start
    assert task3.start < task4.start


def assert_to_list(sequential2, capacity):
    gantt = Gantt(sequential2)
    gantt.assign_capacity(capacity)
    d = gantt.to_list()
    assert len(d) == 2
    assert d[0] == {
        "name": "sample_task1",
        "init": "2023-01-02",
        "end": "2023-01-09",
        "days": 7,
        "depends_on": "",
        "price": 0,
        "desc": "",
        "teams": [
            {
                "name": "team1",
                "init": "2023-01-02",
                "end": "2023-01-09",
                "days": 7,
                "depends_on": "sample_task1",
            },
            {
                "name": "team2",
                "init": "2023-01-02",
                "end": "2023-01-09",
                "days": 7,
                "depends_on": "sample_task1",
            },
        ],
    }
    assert d[1] == {
        "name": "sample_task2",
        "init": "2023-01-10",
        "end": "2023-01-16",
        "days": 6,
        "depends_on": "sample_task1",
        "price": 0,
        "desc": "",
        "teams": [
            {
                "name": "team1",
                "init": "2023-01-10",
                "end": "2023-01-16",
                "days": 6,
                "depends_on": "sample_task2",
            },
            {
                "name": "team2",
                "init": "2023-01-10",
                "end": "2023-01-16",
                "days": 6,
                "depends_on": "sample_task2",
            },
        ],
    }


def assert_assigned_gantt(assigned_tasks):
    gantt = Gantt.from_dict(assigned_tasks)
    assert gantt.tasks_assigned is True
    assert len(gantt.nodes) == 3
    assert gantt.nodes["Visor"].task.start == date(2023, 4, 17)
    assert gantt.nodes["Visor"].task.end == date(2023, 7, 28)
    assert gantt.nodes["SegDent"].task.start == date(2023, 6, 19)
    assert gantt.nodes["SegDent"].task.end == date(2023, 9, 1)
    assert gantt.nodes["IPRv1"].task.start == date(2023, 7, 31)
    assert gantt.nodes["IPRv1"].task.end == date(2023, 9, 1)
