from datetime import date, timedelta
from agileffp.gantt.task import Task
from agileffp.milestone.milestone import Milestone
from agileffp.gantt.team_task import TeamTask
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.seville_calendar import Seville


class EstimatedTask(Task):
    def __init__(
        self,
        name: str,
        estimate: dict[str, int | dict[str, int]],
        depends_on: list = [],
        priority: int = 99,
        start_all_together: bool = True,
        description: str = "",
    ):
        super().__init__(name, None, None, 0, description)

        self.depends_on = depends_on
        self.start_all_together = start_all_together
        self.priority = priority

        self.days = None
        self.cal = Seville()

        self.teams_tasks = {
            team: TeamTask(name, team, effort) for team, effort in estimate.items()
        }

    def assign_capacity(
        self, capacity: dict[str, CapacityTeam], start_after: date = None
    ) -> None:
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

        if self.start_all_together:
            start_after = self._next_common_available_day(
                capacity, start_after
            ) - timedelta(days=1)

        for team, team_task in self.teams_tasks.items():
            team_task.assign_capacity(capacity[team], after=start_after)
            if self.start is None or (team_task.init and team_task.init < self.start):
                self.start = team_task.init
            if self.end is None or (team_task.end and team_task.end > self.end):
                self.end = team_task.end
            self.price += capacity[team].price * team_task.effort
        self.days = self.cal.get_working_days_delta(self.start, self.end) + 1

    def _next_common_available_day(
        self, capacity: dict[str, CapacityTeam], start_after: date = None
    ):
        """Returns the next available day for all the teams in the task"""
        current_common_day = None
        while True:
            day: date = None
            for team, team_task in self.teams_tasks.items():
                _next_available_day = team_task.next_available_day(
                    capacity[team], after=start_after
                )
                if day is None or day < _next_available_day:
                    day = _next_available_day
            if current_common_day == day:
                return day
            else:
                current_common_day = day
                start_after = day + timedelta(days=-1)

    def parse(data: dict) -> list["EstimatedTask"]:
        """Parses the YAML data into Tasks

        Args:
            data (dict): The YAML data

        Returns:
            list[Task]: The tasks list
        """
        if "tasks" not in data:
            raise ValueError("Invalid YAML file")

        return [EstimatedTask(**kwargs) for kwargs in data["tasks"]]

    def from_milestones(milestones: list[Milestone]) -> list["EstimatedTask"]:
        """Creates a list of tasks from a list of milestones

        Args:
            milestones (list[Milestone]): The milestones

        Returns:
            list[Task]: The tasks
        """
        tasks = []
        for m in milestones:
            t = EstimatedTask(
                m.name,
                m.estimated,
                m.depends_on,
                m.priority,
                m.start_all_together,
                description=", ".join([str(v) for v in m.tasks]),
            )
            if m.max_capacity:
                for team, max in m.max_capacity.items():
                    t.teams_tasks[team].max_capacity = max
            tasks.append(t)

        return tasks

    def __str__(self):
        return f"{super().__str__()} - {self.days}"
