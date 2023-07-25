from datetime import date
import pytest
from agileffp.gantt.task import Task


@pytest.fixture
def data():
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


def assert_parse_data(data):
    tasks = Task.parse(data)
    assert len(tasks) == 3
    assert tasks[0].name == "Visor"
    assert tasks[0].start == date(2023, 4, 17)
    assert tasks[0].end == date(2023, 7, 28)
    assert tasks[0].price == 195100
    assert tasks[1].name == "SegDent"
    assert tasks[1].start == date(2023, 6, 19)
    assert tasks[1].end == date(2023, 9, 1)
    assert tasks[1].price == 35880
    assert tasks[2].name == "IPRv1"
    assert tasks[2].start == date(2023, 7, 31)
    assert tasks[2].end == date(2023, 9, 1)
    assert tasks[2].price == 44102.5
