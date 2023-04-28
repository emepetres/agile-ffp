from datetime import date, timedelta
from src.agileffp.utils import daterange

from src.agileffp.seville_calendar import Seville


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
            for d in daterange(self.starts, self.ends + timedelta(days=1))
        ]

    def capacity_at(self, date: date) -> int:
        if date < self.starts or date > self.ends:
            return 0

        idx = (date - self.starts).days
        return self.capacity[idx]

    def reserve_capacity_at(self, date: date, capacity: int) -> int:
        """Returns capacity that was able to assign to date."""
        if date < self.starts or date > self.ends:
            return 0

        idx = (date - self.starts).days
        capacity_available = self.capacity[idx]

        if capacity_available == 0:
            return 0

        assignable = min(capacity_available, capacity)
        self.capacity[idx] -= assignable

        return assignable
