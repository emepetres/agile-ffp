from agileffp.milestone.estimation import EstimatedTask


class Milestone:
    def __init__(
        self,
        name: str,
        tasks: list[str],
        priority: int = 99,
        depends_on: list = [],
        max_capacity: dict[str, int] = {},
        start_all_together: bool = True,
    ):
        self.name = name
        self.tasks = [str(t) for t in tasks]
        self.priority = priority
        self.depends_on = depends_on
        self.max_capacity = max_capacity
        self.start_all_together = start_all_together
        self.estimated = {}

    def _compute_estimation(self, estimation: list[EstimatedTask]):
        for t in self.tasks:
            for k, v in estimation[t].computed_effort.items():
                self.estimated[k] = self.estimated.get(k, 0) + v
        for k, v in self.estimated.items():
            self.estimated[k] = round(v)

    def parse(data: dict) -> dict[str, "Milestone"]:
        """Parses a dictionary into a list of milestones

        Raises:
            SyntaxError: If the dictionary doesn't have the 'milestones' key
        Args:
            data (dict): The dictionary to parse
        Returns:
            dict[str, Milestone]: A dictionary with the milestones
        """
        if "milestones" not in data:
            raise SyntaxError("Missing 'milestones' key")

        return {m.name: m for m in [Milestone(**m) for m in data["milestones"]]}

    def compute(milestones: list["Milestone"], estimation: dict[str, EstimatedTask]):
        """Computes the milestones estimations

        Args:
            milestones (list[&quot;Milestone&quot;]): The milestones to compute
            estimation (dict[float, EstimatedTask]): The estimation to use
        """
        for m in milestones:
            m._compute_estimation(estimation)
