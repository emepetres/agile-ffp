import pytest

from src.agileffp.gantt.task import Task


@pytest.fixture
def task():
    return Task("example", 10)


@pytest.fixture
def capacity():
    return 2


def compute_duration(task, capacity):
    assert task.compute_duration(capacity) == 5
