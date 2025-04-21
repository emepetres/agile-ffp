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

import pprint
from collections import defaultdict

from pydantic import BaseModel

from agileffp.roadmap.models.developers_team import Team
from agileffp.roadmap.models.iteration import Iteration


class Milestone(BaseModel):
    """Represents an milestone in the roadmap."""

    name: str
    items: dict[str, int]
    description: str | None = None
    priority: int = 50
    depends_on: list[str] = []
    expected_cycle_time: dict[str, float] | None = None

    def model_post_init(self, ctx):
        self._parents = []
        self._effort_done = defaultdict(float)
        self._effort_planned = defaultdict(float)
        self._remaining_items = self.items.copy()
        self._start = None
        self._end = None
        self._dev_velocities = defaultdict(list)
        self._iterations = set()
        self._is_closed = False

    def reference_parents(self, milestones: dict[str, "Milestone"]) -> None:
        """Sets the parent milestones."""
        for parent in self.depends_on:
            if parent not in milestones:
                raise ValueError(f"Parent milestone {parent} not found")
            self._parents.append(milestones[parent])

    def compute_work_already_done(self, iterations: list[Iteration], teams: list[Team]):
        """Computes the milestone effort in each iteration."""
        for it in iterations:
            self._compute_closed_items(it, teams)
        self._is_closed = all(
            [round(count, 1) == 0 for count in self._remaining_items.values()])

    def plan_remaining_work(self, iterations: list[Iteration], teams: list[Team]) -> bool:
        """Plans the remaining work for the milestone."""
        could_plan_work = False
        for it in iterations:
            if it.capacity_available:
                if self._assign_remaining_effort(it, teams):
                    could_plan_work = True
                if self.is_planned:
                    break
        return could_plan_work

    def _compute_closed_items(self, it: Iteration, teams: list[Team]) -> None:
        if it.capacity_available:
            return

        if not it.is_milestone_in_this_iteration(self.name):
            return

        for team in teams:
            if team.name not in self._remaining_items:
                continue
            for dev in team.members:
                if dev not in it.closed:
                    continue
                self._iterations.add(it)
                self._effort_done[team.name] += it.get_dedicated_effort(
                    self.name, dev)
                self._remaining_items[team.name] -= it.closed[dev].get(
                    self.name, 0)
                it_dev_velocity = it.get_dev_velocity(dev)
                self._dev_velocities[dev].append(it_dev_velocity)

        if self._start is None or it.start < self._start:
            self._start = it.start
        if self._end is None or it.end > self._end:
            self._end = it.end

    def _assign_remaining_effort(self, it: Iteration, teams: list[Team]) -> bool:
        """Assigns the remaining items to the iteration when possible."""
        could_assign_effort = False
        for team in teams:
            remaining_items = self.team_remaining_items(team)
            if remaining_items == 0:
                continue

            for dev in team.members:
                dev_velocity = self._get_dev_planned_velocity(dev)
                if dev_velocity == 0:
                    continue
                remaining_effort = remaining_items * \
                    dev_velocity
                assigned_effort = it.try_to_assign_effort(self.name,
                                                          dev, remaining_effort)
                if assigned_effort > 0:
                    could_assign_effort = True
                    items = assigned_effort / dev_velocity
                    self._iterations.add(it)
                    self._remaining_items[team.name] = max(
                        0.0, self._remaining_items[team.name] - items)
                    self._effort_planned[team.name] += assigned_effort
                    it.register_planned_items(self.name, dev, round(items, 1))

                    if self._start is None or it.start < self._start:
                        self._start = it.start
                    if self._end is None or it.end > self._end:
                        self._end = it.end
        return could_assign_effort

    def _get_dev_planned_velocity(self, dev: str) -> float:
        """Returns the developer planned velocity or 0 if not planned."""
        if self.expected_cycle_time and dev not in self.expected_cycle_time:
            return 0  # no planned effort for this developer

        if self.expected_cycle_time and self.expected_cycle_time[dev] != -1:
            # use planned velocity
            return self.expected_cycle_time[dev]

        # get planned velocity based on previous velocities on the milestone
        return sum(self._dev_velocities[dev]) / max(len(self._dev_velocities[dev]), 1)

    def team_effort_done(self, team: Team) -> float:
        """Returns the effort for an specific team."""
        return self._effort_done[team.name]

    @property
    def is_closed(self) -> bool:
        """Returns True if the milestone is closed."""
        return self._is_closed

    @property
    def is_planned(self) -> bool:
        """Returns True if the milestone is estimated."""
        return all([round(count, 1) == 0 for count in self._remaining_items.values()])

    @property
    def start(self) -> str:
        """Returns the start date of the milestone."""
        return self._start

    @property
    def end(self) -> str:
        """Returns the end date of the milestone."""
        return self._end

    def team_remaining_items(self, team: Team) -> float:
        """Returns the rounded estimated effort for an specific team."""
        if team.name not in self._remaining_items:
            return 0
        return round(
            self._remaining_items[team.name], 1)

    @property
    def iterations(self) -> list[Iteration]:
        """Returns the iterations where the milestone is planned."""
        return sorted(self._iterations, key=lambda it: it.start)

    @property
    def dependencies_satisfied(self) -> bool:
        """Returns True if all dependencies are satisfied."""
        return all([parent.is_closed or parent.is_planned for parent in self._parents])

    def to_dict(self, teams: list[Team] | None = None) -> dict:
        base = {
            "name": self.name,
            "start": str(self.start),
            "end": str(self.end),
        }

        effort = {}
        if teams:
            effort = {team.name: int(round(self.team_effort_done(
                team) + self._effort_planned[team.name])) for team in teams}

        iterations = {"iterations": ", ".join(
            [it.name for it in self.iterations])}

        return base | effort | iterations

    def __str__(self):
        base = self.to_dict()

        items = {team_name: round(
            items, 1) for team_name, items in self._remaining_items.items()}

        return str(pprint.pformat(base | items))
