class EstimatedEpic:
    def __init__(
        self,
        name: str,
        totals: dict[str, int],
        tasks: list,
        management_team: str = "management",
    ):
        self.name = name
        self.totals = totals
        self.tasks = [EstimatedTask(name, totals, **t) for t in tasks]
        self.management_team = management_team
        self._compute_tasks_effort()
        self._add_management_effort()

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

    def _add_management_effort(self):
        total_except_management = 0
        for k, v in self.totals.items():
            if k != self.management_team:
                total_except_management += v

        for t in self.tasks:
            raw_totals = sum(t.computed_effort.values())
            t.computed_effort[self.management_team] = (
                raw_totals * self.totals.get(self.management_team, 0)
            ) / total_except_management


class EstimatedTask:
    def __init__(self, epic: str, totals: dict, name: str, ref: float, estimated: dict):
        self.epic_name = epic
        self.totals = totals
        self.name = name
        self.ref = ref
        self.estimated = estimated
        self.computed_effort = {}


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
