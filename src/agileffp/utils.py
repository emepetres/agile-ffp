import yaml
from datetime import date, timedelta
import unicodedata


def remove_accents(s: str) -> str:
    return "".join(
        (c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    )


def read_yaml_file(file_path: str) -> dict:
    """Reads a yaml file and returns a dictionary with its content."""
    with open(file_path, "r", encoding="utf-8") as yaml_file:
        try:
            yaml_text = yaml_file.read()
        except yaml.YAMLError as e:
            print(e)
            return None
        clean_text = remove_accents(yaml_text)
        data = yaml.safe_load(remove_accents(clean_text))
    return data


def dayrange(start_date: date, end_date: date) -> list[date]:
    """Returns a generator of day dates between start_date and end_date."""
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(days=n)
