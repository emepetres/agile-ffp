import yaml


def read_yaml_file(file_path: str) -> dict:
    """Reads a yaml file and returns a dictionary with its content."""
    with open(file_path, "r") as yaml_file:
        data = yaml.safe_load(yaml_file)
    return data
