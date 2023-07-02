from typing import List
from agileffp.gantt.capacity_team import CapacityTeam


class EstimatedEpic:
    def __init__(
        self,
        name: str,
        totals: dict[str, int],
        tasks: list,
    ):
        self.name = name
        self.totals = totals
        self.tasks = [EstimatedTask(name, totals, **t) for t in tasks]
        self._compute_tasks_effort()

    def _compute_tasks_effort(self):
        raw_totals = {}
        for t in self.tasks:
            for k, v in t.estimated.items():
                raw_totals[k] = raw_totals.get(k, 0) + v

        for t in self.tasks:
            for k, v in t.estimated.items():
                t.computed_effort[k] = (self.totals.get(k, 0) * v) / raw_totals.get(
                    k, 0
                )

        # compute teams that appear in totals but not in tasks
        # (for example, a management team)
        other_teams = [
            team for team in self.totals.keys() if team not in raw_totals.keys()
        ]
        tasks_teams_total = 0
        for k, v in self.totals.items():
            if k not in other_teams:
                tasks_teams_total += v

        for t in self.tasks:
            for team in other_teams:
                task_raw_totals = sum(t.computed_effort.values())
                t.computed_effort[team] = (
                    task_raw_totals * self.totals[team] / tasks_teams_total
                )


class EstimatedTask:
    def __init__(
        self, epic: str, totals: dict, name: str, ref: str | float, estimated: dict
    ):
        self.epic_name = epic
        self.totals = totals
        self.name = name
        self.ref = str(ref)
        self.estimated = estimated
        self.computed_effort = {}
        self.price = 0

    def compute_price(self, capacity: List[CapacityTeam]):
        for team in capacity:
            self.price += team.price * self.computed_effort.get(team.team, 0)
        self.price = round(self.price)


def parse_estimation(data: dict) -> dict[float, "EstimatedTask"]:
    """Parses a dictionary into a dict of estimated tasks

    Raises:
        ValueError: If the dictionary doesn't have the 'estimation' key
    Args:
        data (dict): The dictionary to parse
    Returns:
        dict[float, EstimatedTask]: A dictionary with the estimated tasks
    """
    if "estimation" not in data:
        raise ValueError("Missing 'estimation' key")

    epics = [
        EstimatedEpic(e["name"], e["totals"], e["tasks"]) for e in data["estimation"]
    ]

    return {t.ref: t for epic in epics for t in epic.tasks}
