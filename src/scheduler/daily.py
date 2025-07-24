from datetime import datetime
from src.scheduler.scheduler_utils import select_now_daily_reminder, select_user_id
from src.scheduler.scheduler import send_reminder


async def daily_reminders():
    now = datetime.utcnow()
    time_now = now.time().replace(second=0, microsecond=0)

    daily_reminders = await select_now_daily_reminder(time_now=time_now)
    for daily in daily_reminders:
        user = await select_user_id(daily.user_id)
        await send_reminder(user_id=user.tg_id, text=daily.description)


def schedule_daily_reminders():
    from src.scheduler.scheduler import scheduler
    scheduler.add_job(daily_reminders, "cron", second=0)
