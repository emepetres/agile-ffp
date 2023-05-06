from agileffp.milestone.estimation import EstimatedTask


class Milestone:
    def __init__(
        self, name: str, tasks: list[float], priority: int = 99, depends_on: list = []
    ):
        self.name = name
        self.tasks = tasks
        self.priority = priority
        self.depends_on = depends_on
        self.estimated = {}

    def _compute_estimation(self, estimation: list[EstimatedTask]):
        pass

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

    def compute(milestones: list["Milestone"], estimation: dict[float, EstimatedTask]):
        """Computes the milestones estimations

        Args:
            milestones (list[&quot;Milestone&quot;]): The milestones to compute
            estimation (dict[float, EstimatedTask]): The estimation to use
        """
        pass
