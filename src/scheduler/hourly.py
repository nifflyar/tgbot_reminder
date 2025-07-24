from datetime import datetime, timedelta
from src.scheduler.scheduler_utils import select_all_hourly_reminder, select_user_id
from src.scheduler.scheduler import send_reminder


def hourly_reminder(reminder_id, user_id, description, start_time, end_time, interval_min, scheduler):
    now = datetime.utcnow()
    today = now.date()

    current = datetime.combine(today, start_time)
    end = datetime.combine(today, end_time)

    if end <= current:
        end += timedelta(days=1)

    interval = timedelta(minutes=interval_min)

    while current <= end:
        run_time = current

        if run_time >= now:
            job_id = f"hourly_{user_id}_{reminder_id}_{run_time.strftime('%Y%m%d%H%M')}"

            if not scheduler.get_job(job_id):

                async def reminder_task(uid=user_id, text=description):
                    await send_reminder(uid, text)

                scheduler.add_job(
                    reminder_task,
                    trigger='date',
                    run_date=run_time,
                    id=job_id,
                    replace_existing=True,
                    max_instances=3
                )

        current += interval


async def schedule_hourly_reminders_job(scheduler):
    reminders = await select_all_hourly_reminder()

    for r in reminders:
        user = await select_user_id(r.user_id)
        hourly_reminder(
            reminder_id=r.id,
            user_id=user.tg_id,
            description=r.description,
            start_time=r.start_time,
            end_time=r.end_time,
            interval_min=r.interval_min,
            scheduler=scheduler
        )


def schedule_hourly_reminders():
    from src.scheduler.scheduler import scheduler

    scheduler.add_job(
        func=schedule_hourly_reminders_job,
        trigger='cron',
        second=0,
        args=[scheduler]
    )
