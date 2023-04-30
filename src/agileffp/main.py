import argparse
from agileffp.gantt.gantt import Gantt
from agileffp.gantt.task import Task
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.utils import read_yaml_file


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
    capacity = CapacityTeam.parse(data)
    tasks = Task.parse(data)

    chart = Gantt(tasks)
    chart.build(capacity)

    print(chart)

    if args.output:
        chart.to_csv(args.output)


if __name__ == "__main__":
    main()
