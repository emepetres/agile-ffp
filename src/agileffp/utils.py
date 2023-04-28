import yaml
from datetime import date, timedelta


def read_yaml_file(file_path: str) -> dict:
    """Reads a yaml file and returns a dictionary with its content."""
    with open(file_path, "r") as yaml_file:
        data = yaml.safe_load(yaml_file)
    return data


def daterange(start_date: date, end_date: date):
    """Returns a generator of dates between start_date and end_date."""
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(days=n)
