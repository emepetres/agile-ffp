import pytest
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.gantt.gantt import Gantt

from agileffp.utils import read_yaml_file


@pytest.fixture
def tasks_data():
    return read_yaml_file("tasks_gantt_sample.yml")


@pytest.fixture
def milestones_data():
    return read_yaml_file("milestones_sample.yml")


def assert_gantt_from_tasks_file(tasks_data):
    g = Gantt.from_dict(tasks_data)
    capacity = CapacityTeam.parse(tasks_data)
    g.assign_capacity(capacity)
    assert len(g.to_list()) == 3


def assert_gantt_from_milestones_file(milestones_data):
    g = Gantt.from_dict(milestones_data)
    capacity = CapacityTeam.parse(milestones_data)
    g.assign_capacity(capacity)
    assert len(g.to_list()) == 13
