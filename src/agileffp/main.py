import argparse
from src.agileffp.gantt.gantt import Gantt
from src.agileffp.gantt.task import Task
from src.agileffp.gantt.capacity_team import CapacityTeam
from src.agileffp.utils import read_yaml_file


def parse_yaml_file(data: dict):
    """Parses the YAML data into Capacity and Tasks

    Args:
        data (dict): The YAML data

    Returns:
        dict[str, CapacityTeam]: The capacity dictionary
        list[Task]: The list of tasks
    """
    if "capacity" not in data or "tasks" not in data:
        raise ValueError("Invalid YAML file")

    capacity = {
        team: CapacityTeam(team, **kwargs) for team, kwargs in data["capacity"].items()
    }

    tasks = [Task(**kwargs) for kwargs in data["tasks"]]

    return capacity, tasks


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Gantt chart according to YAML information."
    )
    parser.add_argument(
        "-f",
        "--file_path",
        type=str,
        help="The path to the YAML file to read.",
        required=True,
    )
    parser.add_argument("-o", "--output", type=str, help="The csv output file path.")
    args = parser.parse_args()

    data = read_yaml_file(args.file_path)
    capacity, tasks = parse_yaml_file(data)

    chart = Gantt(tasks)
    chart.build(capacity)

    print(chart)

    if args.output:
        chart.to_csv(args.output)


if __name__ == "__main__":
    main()
