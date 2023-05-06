class EstimationTask:
    def __init__(self, epic: str, totals: dict, name: str, ref: float, effort: dict):
        self.epic_name = epic
        self.totals = totals
        self.name = name
        self.ref = ref
        self.effort = effort

    def parse(data: dict) -> dict[str, "EstimationTask"]:
        """Parses a dictionary into a dict of epic estimations

        Raises:
            ValueError: If the dictionary doesn't have the 'estimation' key
        Args:
            data (dict): The dictionary to parse
        Returns:
            list[EstimationTask]: A list with the estimated tasks
        """
        if "estimation" not in data:
            raise ValueError("Missing 'estimation' key")

        epics_tasks = [
            EstimationTask._parse_epic(e["name"], e["totals"], e["tasks"])
            for e in data["estimation"]
        ]

        return [t for tasks in epics_tasks for t in tasks]

    def _parse_epic(
        name: str, totals: dict[str, int], tasks: list
    ) -> list["EstimationTask"]:
        """Parses an epic

        Args:
            name (str): The name of the epic
            global (dict[str, int]): The global estimation
            tasks (): The tasks of the epic
        Returns:
            list[EstimationTask]: A list of estimated tasks
        """
        return [EstimationTask(name, totals, **t) for t in tasks]
