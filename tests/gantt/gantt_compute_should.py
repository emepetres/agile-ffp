import pytest
import yaml

from src.agileffp.gantt.compute import read_yaml_file


@pytest.fixture
def example_yaml_file(tmpdir):
    data = {"name": "John", "age": 30, "city": "New York"}
    file_path = tmpdir.join("example.yml")
    with open(file_path, "w") as f:
        yaml.dump(data, f)
    return file_path


def get_dict_from_yaml(example_yaml_file):
    data = read_yaml_file(example_yaml_file)
    expected = {"name": "John", "age": 30, "city": "New York"}
    assert data == expected


def fail_nonexistent_yaml_file():
    with pytest.raises(FileNotFoundError):
        read_yaml_file("nonexistent.yml")
