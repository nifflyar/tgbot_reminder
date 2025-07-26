
import datetime
from sqlalchemy import and_, select, update
from sqlalchemy.orm import aliased

from src.db.database import async_session_factory
from src.db.models import DailyNewReminderOrm, DailyReminderTimes, OneTimeNewReminderOrm, UsersOrm, HourlyNewReminderOrm, YearlyNewReminderOrm



async def select_user(tg_id : int):
    async with async_session_factory() as session:
        stmt = select(UsersOrm).where(UsersOrm.tg_id == tg_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    

async def select_timezone(user_id : int):
    async with async_session_factory() as session:
        stmt = select(UsersOrm.timezone).where(UsersOrm.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
async def select_timezone_tg_id(tg_id : int):
    async with async_session_factory() as session:
        stmt = select(UsersOrm.timezone).where(UsersOrm.tg_id == tg_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    



async def select_all_hourly_reminder():
    async with async_session_factory() as session:
        stmt = (select(HourlyNewReminderOrm).where(HourlyNewReminderOrm.is_active == True))
        result = await session.execute(stmt)
        return result.scalars().all()
    


async def select_now_onetime_reminders(date_today : datetime.date , time_now : datetime.time):
    async with async_session_factory() as session:
        stmt = select(OneTimeNewReminderOrm).where(
            (OneTimeNewReminderOrm.date == date_today) &
            (OneTimeNewReminderOrm.remind_at == time_now))
        
        result = await session.execute(stmt)
        return result.scalars().all()



async def select_now_daily_reminder(time_now):
    async with async_session_factory() as session:

        dr = aliased(DailyReminderTimes)
        dn = aliased(DailyNewReminderOrm)
        stmt = (select(dn.user_id, dn.description)
        .join(dr, dr.reminder_id == dn.id)
        .where(and_(dr.time == time_now, dn.is_active == True)))
        result = await session.execute(stmt)
        return result.all()


async def select_now_yearly_reminder():
    async with async_session_factory() as session:

        yn = aliased(YearlyNewReminderOrm)

        stmt = (select(yn)
        .where(yn.is_active == True))

        result = await session.execute(stmt)
        return result.scalars().all()


async def select_user_id(user_id : int):
    async with async_session_factory() as session:
        stmt = select(UsersOrm).where(UsersOrm.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    


async def mark_onetime_reminder_as_sent(reminder_id: int):
    async with async_session_factory() as session:
        stmt = (
            update(OneTimeNewReminderOrm)
            .where(OneTimeNewReminderOrm.id == reminder_id)
            .values(is_active=False)
        )
        await session.execute(stmt)
        await session.commit()


async def archive_expired_onetime_reminders():
    async with async_session_factory() as session:
        now_utc = datetime.utcnow()

        stmt = (
            update(OneTimeNewReminderOrm)
            .where(
                OneTimeNewReminderOrm.is_active == True,
                datetime.combine(
                    OneTimeNewReminderOrm.date,
                    OneTimeNewReminderOrm.remind_at
                ) <= now_utc
            )
            .values(is_active=False)
        )

        await session.execute(stmt)
        await session.commit()

        