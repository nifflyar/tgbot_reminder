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



# async def send_reminders():
#     """Отправляет напоминания пользователям ровно в :00 минут."""
#     now = datetime.utcnow()
#     date_today = now.date() # "02/03/2025"
#     time_now = now.time().replace(second=0, microsecond=0)   # "14:00"

#     # Получаем разовые напоминания
#     reminders = await select_now_onetime_reminders(date_today=date_today, time_now=time_now)

#     # Отправляем разовые напоминания
#     for reminder in reminders:
#         user = await select_user_id(user_id=reminder.user_id)
#         await bot.send_message(chat_id=user.tg_id, text=f"{reminder.description}")

#     # Удаляем разовые напоминания после отправки
#     # await session.execute(delete(Reminder).where(
#     #     (Reminder.date == date_today) & (Reminder.time == time_now)
#     # ))

#     # Получаем ежедневные напоминания

    
#     # daily_reminders = await select_now_daily_reminder(time_now=time_now)

#     # # Отправляем ежедневные напоминания
#     # for daily in daily_reminders:
#     #     await bot.send_message(daily.tg_id, f"{daily.description}")


# # Запускаем проверку каждую минуту
# def start_scheduler():
#     scheduler.add_job(send_reminders, "cron", second=0)
