from datetime import datetime
from src.scheduler.scheduler_utils import mark_onetime_reminder_as_sent, select_now_onetime_reminders, select_user_id
from src.scheduler.scheduler import send_reminder


async def onetime_reminders():
    now = datetime.utcnow()
    date_today = now.date()
    time_now = now.time().replace(second=0, microsecond=0)

    reminders = await select_now_onetime_reminders(date_today, time_now)

    for reminder in reminders:
        user = await select_user_id(reminder.user_id)
        await send_reminder(user_id=user.tg_id, text=reminder.description)
        await mark_onetime_reminder_as_sent(reminder.id) 


def schedule_onetime_reminders():
    from src.scheduler.scheduler import scheduler
    scheduler.add_job(onetime_reminders, "cron", second=0)
