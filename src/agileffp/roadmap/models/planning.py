"""AgileFFP - Build agile charts for firm fixed price projects.

Copyright (C) 2025  Javier Carnero

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from pydantic import BaseModel

from agileffp.roadmap.models.developers_team import Team
from agileffp.roadmap.models.iteration import DefaultIteration, Iteration
from agileffp.roadmap.models.milestone import Milestone


class Planning(BaseModel):
    teams: list[Team]
    iterations: list[Iteration]
    default_iteration: DefaultIteration | None = None
    milestones: list[Milestone]

    def model_post_init(self, ctx):
        self.iterations = sorted(self.iterations, key=lambda it: it.start)

        # build milestones depencency tree
        milestones_lookup_table = {e.name: e for e in self.milestones}
        for milestone in self.milestones:
            milestone.reference_parents(milestones_lookup_table)

        for milestone in self.milestones:
            milestone.compute_work_already_done(self.iterations, self.teams)

        while True:
            next_milestone = self._next_ready_milestone()
            if not next_milestone:
                break
            next_milestone.plan_remaining_work(self.iterations, self.teams)
            if not next_milestone.is_planned:
                if not self.default_iteration:
                    self._raise_imposible_to_plan(next_milestone)
                self._plan_remaining_work_on_new_iterations(next_milestone)

    @property
    def sorted_milestones(self) -> list[Milestone]:
        return sorted(self.milestones, key=lambda t: t.start)

    def _plan_remaining_work_on_new_iterations(self, next_milestone: Milestone) -> None:
        """Plans the remaining work for an milestone on new iterations."""
        while True:
            it = self.default_iteration.create(self.iterations[-1].end)
            if not next_milestone.plan_remaining_work([it], self.teams):
                self._raise_imposible_to_plan(next_milestone)
            self.iterations.append(it)
            if next_milestone.is_planned:
                break

    def _raise_imposible_to_plan(self, milestone: Milestone) -> bool:
        raise ValueError(
            f"Milestone {milestone.name} could not be fully planned for all iterations.\n{milestone}")

    def _next_ready_milestone(self) -> Milestone | None:
        """Gets the next milestone that is ready to be computed."""
        ready_milestones_sorted = sorted(
            [
                milestone
                for milestone in self.milestones
                if not milestone.is_closed and not milestone.is_planned and milestone.dependencies_satisfied
            ],
            key=lambda milestone: milestone.priority,
        )

        return ready_milestones_sorted[0] if ready_milestones_sorted else None
