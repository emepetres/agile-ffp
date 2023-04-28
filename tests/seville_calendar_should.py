from datetime import date
import pytest

from src.agileffp.seville_calendar import Seville


@pytest.fixture
def calendar() -> Seville:
    return Seville()


def assert_knows_workdays_in_different_years(calendar: Seville):
    assert calendar.is_working_day(date(2018, 2, 15))
    assert calendar.is_working_day(date(2023, 2, 15))


def asssert_knows_feria_wednesday(calendar: Seville):
    assert calendar.get_feria_wednesday(year=2018) == date(2018, 4, 18)
    assert calendar.get_feria_wednesday(year=2023) == date(2023, 4, 26)
    assert not calendar.is_working_day(calendar.get_feria_wednesday(year=2018))
    assert not calendar.is_working_day(calendar.get_feria_wednesday(year=2023))


def assert_complete_nonworking_days_for_seville(calendar: Seville):
    assert len(calendar.holidays(2018)) == 14
    assert len(calendar.holidays(2023)) == 14
