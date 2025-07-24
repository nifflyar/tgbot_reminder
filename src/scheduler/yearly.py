from datetime import datetime, timedelta, timezone
from src.scheduler.scheduler_utils import select_now_yearly_reminder, select_user_id
from src.scheduler.scheduler import send_reminder


async def yearly_reminders():
    now_utc = datetime.utcnow()

    reminders = await select_now_yearly_reminder()

    for yearly in reminders:
        user = await select_user_id(yearly.user_id)

        try:
            offset = int(user.timezone)
        except (ValueError, TypeError):
            continue  

        user_tz = timezone(timedelta(hours=offset))
        now_local = now_utc.replace(tzinfo=timezone.utc).astimezone(user_tz)

        if yearly.day == now_local.day and yearly.month == now_local.month and now_local.hour == 0 and now_local.minute == 0:
            await send_reminder(user_id=user.tg_id, text=yearly.description)


def schedule_yearly_reminders():
    from src.scheduler.scheduler import scheduler
    scheduler.add_job(yearly_reminders, "cron", second=0)
