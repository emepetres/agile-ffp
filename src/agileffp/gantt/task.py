from datetime import date
from dateutil.parser import parse as parse_date


class Task:
    def __init__(
        self,
        name: str,
        start: date | str,
        end: date | str,
        price: float = 0,
        description: str = "",
    ):
        self.name = name
        self.description = description
        self.start, self.end = start, end
        self.price = price

        if isinstance(self.start, str):
            self.start = parse_date(self.start, dayfirst=True).date()
        if isinstance(self.end, str):
            self.end = parse_date(self.end, dayfirst=True).date()

    def __str__(self):
        return f"{self.name} ({self.start} - {self.end})"

    def __repr__(self):
        return str(self)

    def parse(data: dict) -> list["Task"]:
        """Parses the YAML data into Tasks

        Args:
            data (dict): The YAML data

        Returns:
            list[Task]: The tasks list
        """
        if "tasks" not in data:
            raise ValueError("Invalid YAML file")

        return [Task(**kwargs) for kwargs in data["tasks"]]
