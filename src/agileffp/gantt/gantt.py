from datetime import date
from agileffp.gantt.capacity_team import CapacityTeam
from agileffp.gantt.estimated_task import EstimatedTask
from agileffp.gantt.task import Task
from agileffp.milestone.estimation import parse_estimation
from agileffp.milestone.milestone import Milestone


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
            + f",{self.task.start}"
            + f",{int((self.task.end-self.task.start).days)}"
        )

    def to_dict(self):
        return {
            "name": self.task.name,
            "init": str(self.task.start),
            "end": str(self.task.end),
            "days": int((self.task.end - self.task.start).days)
            if self.task.end and self.task.start
            else None,
            "depends_on": ",".join([n.task.name for n in self.parent_nodes]),
            "teams": [t.to_dict() for _, t in self.task.teams_tasks.items()]
            if issubclass(type(self.task), EstimatedTask)
            else None,
            "price": self.task.price,
            "desc": self.task.description,
        }


class Gantt:
    def __init__(self, tasks: list[Task]):
        self.nodes = {t.name: DependencyNode(t) for t in tasks}
        self.tasks_assigned = not issubclass(type(tasks[0]), EstimatedTask)

    def assign_capacity(self, capacity: dict[str, CapacityTeam]) -> None:
        """Builds the gantt chart for the dependency graph

        Args:
            capacity (dict[str, CapacityTeam]): A dictionary with the capacity for each
              team
        """
        if self.tasks_assigned:
            return

        self._compute_dependencies()
        self._build(capacity)

    def _build(self, capacity: dict[str, CapacityTeam]) -> None:
        """Builds the gantt chart for the dependency graph

        Args:
            capacity (dict[str, CapacityTeam]): A dictionary with the capacity for each
              team
        """
        ready = self._get_ready_tasks()
        if not ready:
            self.tasks_assigned = True
            return

        node = ready[0]
        node.task.assign_capacity(capacity, start_after=node.start_after())
        node.processed = True

        self._build(capacity)

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
                task_node
                for task_node in self.nodes.values()
                if not task_node.processed and task_node.dependencies_satisfied()
            ],
            key=lambda node: node.task.priority,
        )

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
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: n.task.start)
        tasks = [node.to_dict() for node in sorted_nodes]
        return tasks

    def from_dict(data: dict) -> "Gantt":
        if "tasks" in data:
            if "capacity" in data:
                tasks = EstimatedTask.parse(data)
            else:
                tasks = Task.parse(data)
        else:
            estimation = parse_estimation(data)
            milestones = Milestone.parse(data)
            Milestone.compute(milestones.values(), estimation)
            tasks = EstimatedTask.from_milestones(milestones.values())

        return Gantt(tasks)
