from datetime import date, timedelta
from agileffp.utils import dayrange

from agileffp.seville_calendar import Seville


class CapacityTeam:
    def __init__(
        self, team: str, members: int, starts: date, ends: date = None
    ) -> None:
        """If ends is None, it is set as the end of current year, or the same year as
        starts occurs above current year."""
        self.team = team
        self.members = members
        self.starts = starts
        self.ends = ends
        if self.ends is None:
            current_year = date.today().year
            year = current_year if current_year >= starts.year else starts.year
            self.ends = date(year, 12, 31)

        self.cal = Seville()
        self._build_capacity_calendar()

    def _build_capacity_calendar(self):
        self.capacity = [
            self.members if self.cal.is_working_day(d) else 0
            for d in dayrange(self.starts, self.ends + timedelta(days=1))
        ]

    def _next_available_day(self) -> date:
        for i, c in enumerate(self.capacity):
            if c > 0:
                return i

        raise ValueError("No available day")

    def assign_effort(self, effort: int, max_capacity: int = None) -> tuple[date, date]:
        """Assigns effort to team's capacity.

        Args:
            effort (int): effort to assign
            max_capacity (int), optional): maximum capacity to assign.
                Defaults to member's team.
        Returns:
            init_date: first date when effort was assigned
            end_date: latest date when effort was assigned
            days: working days between init_date and end_date
        """
        if max_capacity is None:
            max_capacity = self.members

        if max_capacity <= 0:
            raise ValueError("max_capacity must be greater than 0")

        if effort <= 0:
            raise ValueError("effort must be greater than 0")

        assigned = 0
        init_day_idx = self._next_available_day()
        init_date = self.starts + timedelta(days=init_day_idx)
        end_date = init_date
        for i in range(init_day_idx, len(self.capacity)):
            assigned += self._reserve_effort_at(i, min(max_capacity, effort - assigned))

            if assigned == effort:
                end_date = self.starts + timedelta(days=i)
                break

        return (
            init_date,
            end_date,
            self.cal.get_working_days_delta(init_date, end_date) + 1,
        )

    def capacity_at(self, date: date) -> int:
        if date < self.starts or date > self.ends:
            return 0

        idx = (date - self.starts).days
        return self.capacity[idx]

    def _reserve_effort_at(self, idx: int, capacity: int) -> int:
        capacity_available = self.capacity[idx]

        if capacity_available == 0:
            return 0

        assignable = min(capacity_available, capacity)
        self.capacity[idx] -= assignable

        return assignable

    def __str__(self):
        return f"{self.team}: {self.members} ({self.starts} - {self.ends})"

    def __repr__(self):
        return str(self)
