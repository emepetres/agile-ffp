from datetime import date
import pytest
import yaml

from src.agileffp.utils import dayrange, read_yaml_file


@pytest.fixture
def example_yaml_file(tmpdir):
    data = {"name": "John", "age": 30, "city": "New York"}
    file_path = tmpdir.join("example.yml")
    with open(file_path, "w") as f:
        yaml.dump(data, f)
    return file_path


def assert_get_dict_from_yaml(example_yaml_file):
    data = read_yaml_file(example_yaml_file)
    expected = {"name": "John", "age": 30, "city": "New York"}
    assert data == expected


def assert_failure_reading_nonexistent_yaml_file():
    with pytest.raises(FileNotFoundError):
        read_yaml_file("nonexistent.yml")


def assert_day_iteration_over_two_dates():
    dates = [d for d in dayrange(date(2023, 1, 1), date(2023, 12, 31))]
    assert len(dates) == 364


def assert_week_iteration_over_two_dates():
    dates = [d for d in weekrange(date(2023, 1, 1), date(2023, 12, 31))]
    assert len(dates) == 52
