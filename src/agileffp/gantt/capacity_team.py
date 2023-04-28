from datetime import date

from src.agileffp.gantt.task import Task


class CapacityTeam:
    def __init__(self, name: str, members: int, starts: date) -> None:
        self.capacity = members
        self.starts = starts

    def capacity_at(self, date: date) -> int:
        return self.capacity

    def reserve_capacity_at(self, date: date, capacity: int, task: Task) -> None:
        pass
