from datetime import date, timedelta
from agileffp.utils import dayrange

from agileffp.seville_calendar import Seville


class CapacityTeam:
    def __init__(
        self,
        team: str,
        members: int,
        starts: date,
        ends: date = None,
        exceptions: list[dict] = [],
        vacation_months=[6, 12],
        max_gap: int = 4,
    ) -> None:
        """If ends is None, it is set as the end of current year, or the same year as
        starts occurs above current year."""
        self.team = team
        self.members = members
        self.starts = starts
        self.ends = ends
        self.vacation_months = vacation_months
        self.max_gap = max_gap
        if self.ends is None:
            current_year = date.today().year
            year = current_year if current_year >= starts.year else starts.year
            self.ends = date(year, 12, 31)

        self.cal = Seville()
        self.timeline = []
        self._build_capacity_calendar()
        self._correct_capacity_with_exceptions(exceptions)

    def _build_capacity_calendar(self):
        self.capacity = [
            self._get_max_capacity(d)
            for d in dayrange(self.starts, self.ends + timedelta(days=1))
        ]

    def _correct_capacity_with_exceptions(self, exceptions: list[dict]):
        for e in exceptions:
            start = (e["starts"] - self.starts).days
            end = (e["ends"] - self.starts).days + 1
            for i, c in enumerate(self.capacity[start:end], start=start):
                if c > 0:
                    self.capacity[i] = e["members"]

    def _get_max_capacity(self, date: date) -> int:
        if not self.cal.is_working_day(date):
            return 0

        if date.month not in self.vacation_months:
            return self.members
        else:
            return self.members / 2

    def _next_available_day(self, after: date = None, start: int = None) -> int:
        if start is None:
            start = (after - self.starts).days + 1 if after else 0
        for i, c in enumerate(self.capacity[start:], start=start):
            if c > 0:
                return i

        raise ValueError("No available day")

    def next_available_day(self, after: date = None) -> date:
        return self.starts + timedelta(days=self._next_available_day(after=after))

    def assign_effort(
        self, task: str, effort: int, max_capacity: int = None, after: date = None
    ) -> tuple[date, date]:
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
        init_day_idx = self._get_init_date_according_to_max_gap(
            self._next_available_day(after=after), max_capacity, effort
        )
        for i in range(init_day_idx, len(self.capacity)):
            assigned += CapacityTeam._reserve_effort_at(
                self.capacity, i, min(max_capacity, effort - assigned)
            )

            if assigned == effort:
                end_date = self.starts + timedelta(days=i)
                break

        init_date = self.starts + timedelta(days=init_day_idx)
        self.timeline.append(
            {
                "team": self.team,
                "task": task,
                "max": max_capacity,
                "start": str(init_date),
                "end": str(end_date),
            }
        )

        return (
            init_date,
            end_date,
            self.cal.get_working_days_delta(init_date, end_date) + 1,
        )

    def _get_init_date_according_to_max_gap(
        self, init_idx: int, max_capacity: int, effort: int
    ) -> int:
        assignation, assigned, gap = 0, 0, 0
        capacity_copy = self.capacity.copy()
        for i in range(init_idx, len(self.capacity)):
            assignation = CapacityTeam._reserve_effort_at(
                capacity_copy, i, min(max_capacity, effort - assigned)
            )
            assigned += assignation
            gap = 0 if assignation != 0 else gap + 1

            if gap > self.max_gap:
                return self._get_init_date_according_to_max_gap(
                    self._next_available_day(start=i), max_capacity, effort
                )

            if assigned == effort:
                return init_idx

    def capacity_at(self, date: date) -> int:
        if date < self.starts or date > self.ends:
            return 0

        idx = (date - self.starts).days
        return self.capacity[idx]

    def _reserve_effort_at(capacity: list[int], idx: int, effort: int) -> int:
        capacity_available = capacity[idx]

        if capacity_available == 0:
            return 0

        assignable = min(capacity_available, effort)
        capacity[idx] -= assignable

        return assignable

    def __str__(self):
        return f"{self.team}: {self.members} ({self.starts} - {self.ends})"

    def __repr__(self):
        return str(self)

    def parse(data: dict) -> dict[str, "CapacityTeam"]:
        """Parses the YAML data into Capacity

        Args:
            data (dict): The YAML data

        Returns:
            dict[str, CapacityTeam]: The capacity dictionary
        """
        if "capacity" not in data:
            raise ValueError("Invalid YAML file")

        capacity = {
            team: CapacityTeam(team, **kwargs)
            for team, kwargs in data["capacity"].items()
        }

        return capacity

    def to_timeline(self) -> list[dict[str, any]]:
        return self.timeline
