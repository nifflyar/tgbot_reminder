import calendar
import locale

from aiogram.types import User
from datetime import datetime

from .schemas import CalendarLabels


async def get_user_locale(from_user: User) -> str:
    "Returns user locale in format en_US, accepts User instance from Message, CallbackData etc"
    loc = from_user.language_code
    return locale.locale_alias[loc].split(".")[0]

class GenericCalendar:

    def __init__(
        self,
        locale: str = None,
        labels: CalendarLabels = None,
        cancel_btn: str = None,
        today_btn: str = "",
        tomorrow_btn: str = "",
        show_alerts: bool = False
    ) -> None:
        """
        Parameters:
        - locale: system locale string (e.g., "ru_RU.UTF-8")
        - labels: custom translation labels (CalendarLabels)
        """
        if labels:
            self._labels = labels
        else:
            self._labels = CalendarLabels()
            if locale:
                try:
                    with calendar.different_locale(locale):
                        self._labels.days_of_week = list(calendar.day_abbr)
                        self._labels.months = list(calendar.month_abbr)[1:]
                except locale.Error:
                    self._labels.days_of_week = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
                    self._labels.months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        if cancel_btn:
            self._labels.cancel_caption = cancel_btn
        if today_btn:
            self._labels.today_caption = today_btn
        if tomorrow_btn:
            self._labels.tomorrow_caption = tomorrow_btn

        self.min_date = None
        self.max_date = None
        self.show_alerts = show_alerts



    def set_dates_range(self, min_date: datetime, max_date: datetime):
        """Sets range of minimum & maximum dates"""
        self.min_date = min_date
        self.max_date = max_date

    async def process_day_select(self, data, query):
        """Checks selected date is in allowed range of dates"""
        date = datetime(int(data.year), int(data.month), int(data.day))
        if self.min_date and self.min_date > date:
            await query.answer(
                f'The date have to be later {self.min_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        elif self.max_date and self.max_date < date:
            await query.answer(
                f'The date have to be before {self.max_date.strftime("%d/%m/%Y")}',
                show_alert=self.show_alerts
            )
            return False, None
        await query.message.delete_reply_markup()  # removing inline keyboard
        return True, date