from src.agileffp.gantt.capacity_team import CapacityTeam


class TeamTask:
    def __init__(self, name: str, team: str, effort: int | dict[str, int]):
        self.name = name
        self.team = team
        if isinstance(effort, int):
            self.effort = effort
            self.max_capacity = None
        else:
            self.effort = effort["effort"]
            self.max_capacity = effort["max_capacity"]
        self.init, self.end, self.days = None, None, None

    def assign_capacity(self, capacity: CapacityTeam) -> None:
        """Assigns capacity to the task

        Args:
            capacity (CapacityTeam): The capacity of the team
        """
        if capacity.team != self.team:
            raise ValueError(
                f"Team {capacity.team} does not match task's team {self.team}"
            )

        self.init, self.end, self.days = capacity.assign_effort(
            self.effort, self.max_capacity
        )

    def __str__(self):
        return f"[{self.team}]{self.name} ({self.start} - {self.end}) - {self.days}"

    def __repr__(self):
        return str(self)
