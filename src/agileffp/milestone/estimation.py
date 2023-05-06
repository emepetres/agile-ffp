class Estimation:
    def __init__(self, name: str, **kwargs):
        self.name = name

    def parse(data: dict) -> dict[str, "Estimation"]:
        """Parses a dictionary into a dict of epic estimations

        Raises:
            ValueError: If the dictionary doesn't have the 'estimation' key
        Args:
            data (dict): The dictionary to parse
        Returns:
            dict[str, Estimation]: A dictionary with the milestones
        """
        if "estimation" not in data:
            raise ValueError("Missing 'estimation' key")

        return {e.name: e for e in [Estimation(**m) for m in data["estimation"]]}
