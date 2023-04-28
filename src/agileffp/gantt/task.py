class Task:
    def __init__(self, name, effort: int):
        self.name = name
        self.effort = effort

    def compute_duration(self, capacity: int):
        return self.effort / capacity

    # # def __str__(self):
    # #     return f"{self.name} ({self.start} - {self.end})"

    # # def __repr__(self):
    # #     return str(self)

    # # def __eq__(self, other):
    # #     return self.name == other.name and self.start == other.start and self.end == other.end and self.color == other.color

    # # def __hash__(self):
    # #     return hash(self.name, self.start, self.end)
