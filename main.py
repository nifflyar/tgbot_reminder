import sys
import os
sys.path.insert(0, os.path.abspath('./src'))


import pytz
import asyncio
from aiogram import Bot, Dispatcher
from handlers import start_menu

from src.scheduler import setup_all_schedulers
from src.scheduler.scheduler import schedule_archive_onetime_reminders, set_scheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dotenv import load_dotenv
load_dotenv() 
# import logging #for debugging

bot = Bot(token = os.getenv("TOKEN"))
dp = Dispatcher()
dp.include_router(start_menu.router)


async def shutdown():
    await bot.session.close()

async def main():
    loop = asyncio.get_running_loop()

    sched = AsyncIOScheduler(timezone=pytz.UTC, event_loop=loop)
    set_scheduler(sched)

    setup_all_schedulers()
    schedule_archive_onetime_reminders(sched)
    sched.start()

    await dp.start_polling(bot)



if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")