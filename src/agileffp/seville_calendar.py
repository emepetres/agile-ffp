from datetime import timedelta
from workalendar.europe.spain import Andalusia
from workalendar.registry_tools import iso_register


# FIXME: some fixed dates are wrong when they go on sunday
# like Andalusia day on 2021, which was moved to 1 of march
@iso_register("ES-AN-SE")
class Seville(Andalusia):
    "Seville"

    include_corpus_christi = True

    def get_feria_wednesday(self, year):
        easter = self.get_easter_sunday(year)
        return easter + timedelta(days=17)

    def get_variable_days(self, year):
        days = super().get_variable_days(year)
        days.append((self.get_feria_wednesday(year), "Epiphany"))
        return days
