from .yearly import schedule_yearly_reminders
from .daily import schedule_daily_reminders
from .hourly import schedule_hourly_reminders
from .onetime import schedule_onetime_reminders

def setup_all_schedulers():
    schedule_onetime_reminders()
    schedule_hourly_reminders()
    schedule_daily_reminders()
    schedule_yearly_reminders()
    