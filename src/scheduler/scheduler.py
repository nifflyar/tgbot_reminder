from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from aiogram import Bot
import os
from dotenv import load_dotenv

from scheduler.scheduler_utils import archive_expired_onetime_reminders

load_dotenv()
bot = Bot(token=os.getenv("TOKEN"))

scheduler: AsyncIOScheduler | None = None


def set_scheduler(sched: AsyncIOScheduler):
    global scheduler
    scheduler = sched


async def send_reminder(user_id: int, text: str):
    try:
        await bot.send_message(chat_id=user_id, text=f"⏰ {text}")
    except Exception as e:
        print(f"[!] Ошибка при отправке напоминания: {e}")


def remove_hourly_reminder_jobs(user_id: int, reminder_id: int):
    from src.scheduler.scheduler import scheduler 
    prefix = f"hourly_{user_id}_{reminder_id}_"
    jobs = scheduler.get_jobs()

    for job in jobs:
        if job.id.startswith(prefix):
            scheduler.remove_job(job.id)


def schedule_archive_onetime_reminders(scheduler: AsyncIOScheduler):
    scheduler.add_job(
        archive_expired_onetime_reminders,
        trigger="cron",
        hour=0,
        minute=5,
        id="archive_onetime",
        replace_existing=True
    )


