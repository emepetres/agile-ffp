
from pydantic import BaseModel

from agileffp.roadmap.models.developers_team import Team
from agileffp.roadmap.models.epic import Epic
from agileffp.roadmap.models.iteration import DefaultIteration, Iteration


class Planning(BaseModel):
    # # project_name: str
    # # project_version: datetime
    teams: list[Team]
    iterations: list[Iteration]
    default_iteration: DefaultIteration | None = None
    epics: list[Epic]

    def model_post_init(self, ctx):
        self.iterations = sorted(self.iterations, key=lambda it: it.start)

        # build epics depencency tree
        epics_lookup_table = {e.name: e for e in self.epics}
        for epic in self.epics:
            epic.reference_parents(epics_lookup_table)

        for epic in self.epics:
            epic.compute_work_already_done(self.iterations, self.teams)

        while True:
            next_epic = self._next_ready_epic()
            if not next_epic:
                break
            next_epic.plan_remaining_work(self.iterations, self.teams)
            if not next_epic.is_planned:
                if not self.default_iteration:
                    self._raise_imposible_to_plan(next_epic)
                self._plan_remaining_work_on_new_iterations(next_epic)

    @property
    def sorted_epics(self) -> list[Epic]:
        return sorted(self.epics, key=lambda t: t.start)

    def _plan_remaining_work_on_new_iterations(self, next_epic: Epic) -> None:
        """Plans the remaining work for an epic on new iterations."""
        while True:
            it = self.default_iteration.create(self.iterations[-1].end)
            if not next_epic.plan_remaining_work([it], self.teams):
                self._raise_imposible_to_plan(next_epic)
            self.iterations.append(it)
            if next_epic.is_planned:
                break

    def _raise_imposible_to_plan(self, epic: Epic) -> bool:
        raise ValueError(
            f"Epic {epic.name} could not be fully planned for all iterations.\n{epic}")

    def _next_ready_epic(self) -> Epic | None:
        """Gets the next epic that is ready to be computed."""
        ready_epics_sorted = sorted(
            [
                epic
                for epic in self.epics
                if not epic.is_closed and not epic.is_planned and epic.dependencies_satisfied
            ],
            key=lambda epic: epic.priority,
        )

        return ready_epics_sorted[0] if ready_epics_sorted else None
