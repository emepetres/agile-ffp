from datetime import date
from agileffp.gantt.capacity_team import CapacityTeam


class TeamTask:
    def __init__(self, name: str, team: str, estimate: int | dict[str, int]):
        self.name = name
        self.team = team
        if isinstance(estimate, int | float):
            self.effort = estimate
            self.max_capacity = None
        else:
            self.effort = estimate["effort"]
            self.max_capacity = estimate["max_capacity"]
        self.init, self.end, self.days = None, None, None

    def assign_capacity(self, capacity: CapacityTeam, after: date = None) -> None:
        """Assigns capacity to the task

        Args:
            capacity (CapacityTeam): The capacity of the team
        """
        if capacity.team != self.team:
            raise ValueError(
                f"Team {capacity.team} does not match task's team {self.team}"
            )

        self.init, self.end, self.days = capacity.assign_effort(
            self.name, self.effort, max_capacity=self.max_capacity, after=after
        )

    def next_available_day(self, capacity: CapacityTeam, after: date = None) -> date:
        mc = self.max_capacity if self.max_capacity else capacity.members
        return capacity.next_available_day(self.effort, mc, after=after)

    def __str__(self):
        return f"[{self.team}]{self.name} ({self.init} - {self.end}) - {self.days}"

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "name": self.team,
            "init": str(self.init),
            "end": str(self.end),
            "days": int((self.end - self.init).days)
            if self.init and self.end
            else None,
            "depends_on": self.name,
        }
