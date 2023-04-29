from src.agileffp.gantt.capacity_team import CapacityTeam
from src.agileffp.gantt.task import Task


class DependencyNode:
    def __init__(self, task: Task):
        self.task = task
        self.processed = False
        self.parent_nodes = []
        self.next_nodes = []

    def dependencies_satisfied(self) -> bool:
        for node in self.parent_nodes:
            if not node.processed:
                return False
        return True

    def __str__(self):
        return str(self.task)

    def __repr__(self):
        return str(self)


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
            list[DependencyNode]: A list of tasks that are ready to be processed
        """
        return [
            n
            for n in self.nodes.values()
            if n.dependencies_satisfied() and not n.processed
        ]

    def build(self, capacity: dict[str, CapacityTeam]) -> None:
        """Builds the gantt chart for the dependency graph

        Args:
            capacity (dict[str, CapacityTeam]): A dictionary with the capacity for each
              team
        """
        ready = self._get_ready_tasks()
        if not ready:
            return

        for root in ready:
            root.task.assign_capacity(capacity)
            root.processed = True

        self.build(capacity)

    def __str__(self):
        s = "Gantt: \n"
        for node in self.nodes.values():
            s += f"\t{node}\n"
        return s

    def __repr__(self):
        return str(self)
