from src.agileffp.gantt.capacity_team import CapacityTeam


class TeamTask:
    def __init__(self, name: str, team: str, effort: int, max_capacity: int = None):
        self.name = name
        self.team = team
        self.effort = effort
        self.init, self.end, self.days = None, None, None

    def assign_capacity(self, capacity: CapacityTeam) -> None:
        if capacity.team != self.team:
            raise ValueError(
                f"Team {capacity.team} does not match task's team {self.team}"
            )

        self.init, self.end, self.days = capacity.assign_effort(self.effort)

    def __str__(self):
        return f"[{self.team}]{self.name} ({self.start} - {self.end}) - {self.team}"

    def __repr__(self):
        return str(self)
