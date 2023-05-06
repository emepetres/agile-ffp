from datetime import date
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.gantt.task import Task


class DependencyNode:
    def __init__(self, task: Task):
        self.task = task
        self.processed = False
        self.parent_nodes = []
        self.next_nodes = []

    def dependencies_satisfied(self) -> bool:
        for parent in self.parent_nodes:
            if not parent.processed:
                return False
        return True

    def start_after(self) -> date:
        start_after: date = None
        for parent in self.parent_nodes:
            if parent.processed and (
                start_after is None or parent.task.end > start_after
            ):
                start_after = parent.task.end
        return start_after

    def __str__(self):
        return str(self.task)

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        return self.task.name < other.task.name

    def to_csv(self):
        return (
            f"{self.task.name}"
            + f",{self.task.init}"
            + f",{int((self.task.end-self.task.init).days)}"
        )

    def to_dict(self):
        return {
            "name": self.task.name,
            "init": str(self.task.init),
            "end": str(self.task.end),
            "days": int((self.task.end - self.task.init).days),
            "depends_on": ",".join([n.task.name for n in self.parent_nodes]),
            "teams": [t.to_dict() for _, t in self.task.teams_tasks.items()],
        }


class Gantt:
    def __init__(self, tasks: list[Task]):
        self.nodes = {t.name: DependencyNode(t) for t in tasks}
        self._compute_dependencies()

    def _compute_dependencies(self) -> None:
        """Computes the dependency graph"""
        for name, node in self.nodes.items():
            for parent in node.task.depends_on:
                if parent not in self.nodes:
                    raise ValueError(f"Task {parent} does not exist")
                self.nodes[name].parent_nodes.append(self.nodes[parent])
                self.nodes[parent].next_nodes.append(self.nodes[name])

    def _get_ready_tasks(self) -> list[DependencyNode]:
        """Gets the tasks that are ready to be processed

        Returns:
            list[DependencyNode]: A list of tasks that are ready to be processed,
            ordered by priority
        """
        return sorted(
            [
                n
                for n in self.nodes.values()
                if n.dependencies_satisfied() and not n.processed
            ],
            key=lambda node: node.task.priority,
        )

    def build(self, capacity: dict[str, CapacityTeam]) -> None:
        """Builds the gantt chart for the dependency graph

        Args:
            capacity (dict[str, CapacityTeam]): A dictionary with the capacity for each
              team
        """
        ready = self._get_ready_tasks()
        if not ready:
            return

        for node in ready:
            node.task.assign_capacity(capacity, start_after=node.start_after())
            node.processed = True

        self.build(capacity)

    def __str__(self):
        s = "Gantt: \n"
        for node in self.nodes.values():
            s += f"\t{node}\n"
        return s

    def __repr__(self):
        return str(self)

    def to_csv(self, file_path: str) -> None:
        s = "Task,Start Date,Duration\n"
        for node in self.nodes.values():
            s += f"{node.to_csv()}\n"
        with open(file_path, "w") as f:
            f.write(s)

    def to_list(self) -> list[dict]:
        tasks = [node.to_dict() for node in self.nodes.values()]
        return sorted(tasks, key=lambda task: task["init"])
