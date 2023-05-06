class Milestone:
    def parse(data: dict) -> dict[str, "Milestone"]:
        if "milestones" not in data:
            raise SyntaxError("Missing 'milestones' key")
        pass
