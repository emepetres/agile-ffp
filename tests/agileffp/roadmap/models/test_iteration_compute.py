from datetime import date

import pytest

from agileffp.roadmap.models.iteration import Iteration

# filepath: /workspaces/agile-ffp/tests/agileffp/roadmap/models/test_iteration_compute.py


@pytest.fixture
def sample_iteration():
    return Iteration(
        name="Iteration 1",
        start=date(2025, 1, 1),
        end=date(2025, 1, 15),
        capacity={"dev1": 12, "dev2": 15},
        closed={
            "dev1": {"epic1": 5, "epic2": 5},
            "dev2": {"epic1": 10, "epic2": 5}
        }
    )


def test_get_developer_velocity(sample_iteration):
    assert sample_iteration.get_developer_velocity("dev1") == 1.2
    assert sample_iteration.get_developer_velocity("dev2") == 1.0


def test_get_dedicated_effort(sample_iteration):
    assert sample_iteration.get_dedicated_effort("epic1", "dev1") == 6.0
    assert sample_iteration.get_dedicated_effort("epic2", "dev1") == 6.0
    assert sample_iteration.get_dedicated_effort("epic1", "dev2") == 10.0
    assert sample_iteration.get_dedicated_effort("epic2", "dev2") == 5.0
