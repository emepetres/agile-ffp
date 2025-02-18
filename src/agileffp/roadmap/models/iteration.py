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

from collections import defaultdict
from datetime import date, timedelta

from pydantic import BaseModel, ConfigDict

from agileffp.roadmap.models.developers_team import Team


class Iteration(BaseModel):
    """Represents an iteration in the roadmap."""

    model_config = ConfigDict(coerce_numbers_to_str=True)

    name: str
    start: date
    end: date
    capacity: dict[str, float]
    closed: dict[str, dict[str, float]] | None = None
    description: str | None = None

    def model_post_init(self, ctx):
        self._dedicated_effort = defaultdict(lambda: defaultdict(float))
        self._planned = defaultdict(lambda: defaultdict(float))
        # if there are no closed items, the capacity is available
        if not self.closed:
            self._capacity_available = self.capacity.copy()
            return

        self._compute_closed_items_velocity()
        self._compute_closed_items_effort()

    def _compute_closed_items_velocity(self):
        self._velocity = defaultdict(float)
        for dev, epic_closed_items in self.closed.items():
            self._velocity[dev] = float(
                self.capacity[dev]) / sum([count for count in epic_closed_items.values()])

    def _compute_closed_items_effort(self):
        for dev, epic_closed_items in self.closed.items():
            for epic_name, count in epic_closed_items.items():
                self._dedicated_effort[epic_name][dev] += count * \
                    self._velocity[dev]

    def try_to_assign_effort(self, epic: str, dev: str, effort: float) -> float:
        """Tries to assign effort to a team member."""
        if dev not in self._capacity_available or self._capacity_available[dev] == 0:
            return 0

        assigned_effort = min(
            self._capacity_available[dev], effort)
        self._capacity_available[dev] -= assigned_effort
        effort -= assigned_effort
        return assigned_effort

    def register_planned_items(self, epic: str, dev: str, items: float):
        """Registers the assigned effort to a team member."""
        self._planned[dev][epic] += items

    def get_developer_velocity(self, dev: str) -> float:
        """Returns the developer velocity in the iteration."""
        return self._velocity[dev]

    def get_dedicated_effort(self, epic: str, dev: str) -> float:
        """Returns the developer dedicated effort in the iteration for a given epic."""
        return self._dedicated_effort[epic][dev]

    def is_epic_in_this_iteration(self, epic: str) -> bool:
        """Returns True if the epic has items closed in this iteration."""
        return epic in self._dedicated_effort

    def get_dev_velocity(self, dev: str) -> float:
        """Returns the team member velocity in the iteration."""
        return self._velocity[dev]

    @property
    def capacity_available(self) -> bool:
        return not self.closed and any([count > 0 for count in self._capacity_available.values()])

    def to_dict(self, teams: list[Team]) -> dict:
        base = {
            "name": self.name,
            "start": self.start,
            "end": self.end,
        }
        capacity = {f"[Cap] {dev}": self.capacity[dev]
                    if dev in self.capacity else 0 for team in teams for dev in team.members}
        closed_or_planned = self.closed if self.closed else self._planned
        items = {}
        for team in teams:
            for dev in team.members:
                if dev not in closed_or_planned:
                    items[f"[Items] {dev}"] = "-"
                else:
                    items[f"[Items] {dev}"] = ", ".join(
                        f"{epic}: {count}" for epic, count in closed_or_planned[dev].items())

        return base | capacity | items

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


class DefaultIteration(BaseModel):
    """Represents the default iteration when there are no more defined."""

    index: int = 1
    days_interval: int
    capacity: dict[str, float]
    prefix: str = "default"

    def create(self, last_iteration_date: date) -> Iteration:
        """Returns a new iteration."""
        start = last_iteration_date + timedelta(days=1)
        end = start + timedelta(days=self.days_interval-1)
        new_it = Iteration(
            name=f"{self.prefix}{self.index}",
            start=start,
            end=end,
            capacity=self.capacity.copy()
        )
        self.index += 1
        return new_it
