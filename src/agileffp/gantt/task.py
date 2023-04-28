from src.agileffp.seville_calendar import Seville
from src.agileffp.gantt.team_task import TeamTask
from src.agileffp.gantt.capacity_team import CapacityTeam


class Task:
    def __init__(self, name: str, teams_effort: dict[str, int | dict[str, int]]):
        self.name = name
        self.init, self.end, self.days = None, None, None
        self.cal = Seville()

        self.teams_tasks = {
            team: TeamTask(name, team, effort) for team, effort in teams_effort.items()
        }

    def assign_capacity(self, capacity: dict[str, CapacityTeam]) -> None:
        """Assigns capacity to each team in the task

        Args:
            capacity (dict[str, CapacityTeam]):
            A dictionary with the capacity for each team
        """
        unavailable_teams = [k for k in self.teams_tasks.keys() if k not in capacity]
        if unavailable_teams:
            raise ValueError(
                f"Teams {unavailable_teams} don't appear on the capacity teams list"
            )

        for team, team_task in self.teams_tasks.items():
            team_task.assign_capacity(capacity[team])
            if self.init is None or team_task.init < self.init:
                self.init = team_task.init
            if self.end is None or team_task.end > self.end:
                self.end = team_task.end
        self.days = self.cal.get_working_days_delta(self.init, self.end) + 1

    def __str__(self):
        return f"{self.name} ({self.start} - {self.end}) - {self.days}"

    def __repr__(self):
        return str(self)
