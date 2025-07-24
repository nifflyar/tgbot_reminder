import asyncio
import datetime
from sqlalchemy import DateTime, Integer, and_, cast, delete, func, insert, inspect, or_, select, text, update
from sqlalchemy.orm import aliased, contains_eager, joinedload, selectinload


from scheduler.hourly import hourly_reminder
from src.scheduler.scheduler import remove_hourly_reminder_jobs
from src.db.database import Base, async_engine, async_session_factory
from src.db.models import OneTimeNewReminderOrm, DailyReminderTimes, DailyNewReminderOrm, UsersOrm, WeeklyNewReminderOrm, WeeklyReminderDays, YearlyNewReminderOrm, MonthlyNewReminderOrm, MonthlyReminderDays, HourlyNewReminderOrm




async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

# asyncio.run(create_tables())


def get_model_by_type(type_: str):
    match type_:
        case "daily": return DailyNewReminderOrm
        case "hourly": return HourlyNewReminderOrm
        case "onetime": return OneTimeNewReminderOrm
        case "yearly": return YearlyNewReminderOrm
        case _: raise ValueError("Unknown reminder type")


#!                  USER QUERIES

async def insert_users(tg_id : int, language : str, timezone: str, notifications : bool = False, hour_format : str = "24"):
    async with async_session_factory() as session:
        user = UsersOrm(tg_id = tg_id, language = language, timezone=timezone, notifications=notifications, hour_format=hour_format)
        session.add(user)
        await session.commit()

async def select_user(tg_id : int):
    async with async_session_factory() as session:
        stmt = select(UsersOrm).where(UsersOrm.tg_id == tg_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

async def select_user_id(user_id : int):
    async with async_session_factory() as session:
        stmt = select(UsersOrm).where(UsersOrm.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    

async def select_timezone(user_id : int):
    async with async_session_factory() as session:
        stmt = select(UsersOrm.timezone).where(UsersOrm.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

async def update_user(tg_id : int, 
                      new_timezone : str = None, 
                      new_language : str = None, 
                      new_notifications : bool = None, 
                      new_hour_format : str = None,
                      new_timezone_updated_at: datetime.datetime = None):
    
    async with async_session_factory() as session:
        sub = await select_user(tg_id=tg_id)
        user = await session.get(UsersOrm, sub.id)

        if new_timezone is not None:
            user.timezone = new_timezone

        if new_language is not None:
            user.language = new_language

        if new_notifications is not None:
            user.notifications = new_notifications
        
        if new_hour_format is not None:
            user.hour_format = new_hour_format

        if new_timezone_updated_at is not None:
            user.timezone_updated_at = new_timezone_updated_at
        
        await session.commit()



#!                      NUMBER OF REMINDERS

async def count_onetime_reminders(tg_id: int) -> int:
    async with async_session_factory() as session:
        user = await select_user(tg_id)

        stmt = select(func.count()).where(and_(OneTimeNewReminderOrm.user_id == user.id, OneTimeNewReminderOrm.is_active == True))

        result = await session.execute(stmt)
        return result.scalar_one()
    

async def count_daily_reminders(tg_id: int) -> int:
    async with async_session_factory() as session:
        user = await select_user(tg_id)
        stmt = select(func.count()).where(DailyNewReminderOrm.user_id == user.id)
        result = await session.execute(stmt)
        return result.scalar_one()


async def count_hourly_reminders(tg_id: int) -> int:
    async with async_session_factory() as session:
        user = await select_user(tg_id)
        stmt = select(func.count()).where(HourlyNewReminderOrm.user_id == user.id)
        result = await session.execute(stmt)
        return result.scalar_one()
    
async def count_yearly_reminders(tg_id: int) -> int:
    async with async_session_factory() as session:
        user = await select_user(tg_id)
        stmt = select(func.count()).where(YearlyNewReminderOrm.user_id == user.id)
        result = await session.execute(stmt)
        return result.scalar_one()
    



#!                  INSERT REMINDERS


async def onetime_reminder_add(user_id: int, description: str, date: datetime.date, remind_at: datetime.time):
    async with async_session_factory() as session:
        tz = await select_timezone(user_id=user_id)

        user_remind_dt = datetime.datetime.combine(date, remind_at)

        now_user = datetime.datetime.utcnow() + datetime.timedelta(hours=int(tz))

        is_active = user_remind_dt >= now_user

        shifted_dt = user_remind_dt - datetime.timedelta(hours=int(tz))

        reminder = OneTimeNewReminderOrm(
            user_id=user_id,
            description=description,
            date=shifted_dt.date(),
            remind_at=shifted_dt.time(),
            is_active=is_active
        )
        session.add(reminder)
        await session.commit()
        


async def daily_reminder_add(user_id : int, description: str, times: list[datetime.time]):
    async with async_session_factory() as session:
        tz = await select_timezone(user_id=user_id)
        shifted_times = [
            (datetime.datetime.combine(datetime.datetime.today(), t) - datetime.timedelta(hours=int(tz))).time()
            for t in times
            ]
        reminder = DailyNewReminderOrm(
            user_id = user_id,
            description = description,
        )

        reminder.times = [
            DailyReminderTimes(time=t) for t in shifted_times
        ]

        session.add(reminder)
        await session.commit()
        # await session.refresh(reminder)


async def hourly_reminder_add(user_id : int, 
                              description: str, 
                              interval_min: int,
                              start_time: datetime.time,
                              end_time: datetime.time,):
    async with async_session_factory() as session:
        tz = await select_timezone(user_id=user_id)
        dt_st = datetime.datetime.combine(datetime.datetime.today(), start_time)
        dt_et = datetime.datetime.combine(datetime.datetime.today(), end_time)
        shifted_start_time = (dt_st - datetime.timedelta(hours=int(tz))).time()
        shifted_end_time = (dt_et - datetime.timedelta(hours=int(tz))).time()

        reminder = HourlyNewReminderOrm(
            user_id = user_id,
            description = description,
            interval_min = interval_min,
            start_time = shifted_start_time,
            end_time = shifted_end_time
        )

        
        session.add(reminder)
        await session.commit()
        await session.refresh(reminder)

        user = await select_user_id(user_id)  # чтобы получить tg_id
        
        from src.scheduler.scheduler import scheduler

        await hourly_reminder(
            reminder_id=reminder.id,
            user_id=user.tg_id,
            description=description,
            start_time=start_time,
            end_time=end_time,
            interval_min=interval_min,
            scheduler=scheduler,
        )


# async def weekly_reminder_add(user_id : int, 
#                               description: str, 
#                               days: list[int]):
#     async with async_session_factory() as session:
#         reminder = WeeklyNewReminderOrm(
#             user_id = user_id,
#             description = description,
#         )

#         reminder.days = [
#             WeeklyReminderDays(days=d) for d in days
#         ]

#         session.add(reminder)
#         await session.commit()
#         # await session.refresh(reminder)


# async def monthly_reminder_add(user_id : int, 
#                               description: str, 
#                               days: list[int]):
#     async with async_session_factory() as session:
#         reminder = MonthlyNewReminderOrm(
#             user_id = user_id,
#             description = description,
#         )

#         reminder.days = [
#             MonthlyReminderDays(days=d) for d in days
#         ]

#         session.add(reminder)
#         await session.commit()
#         # await session.refresh(reminder)


async def yearly_reminder_add(user_id : int, 
                              description: str, 
                              day: int,
                              month: int):
    async with async_session_factory() as session:
        reminder = YearlyNewReminderOrm(
            user_id = user_id,
            description = description,
            day = day,
            month = month
        )
        session.add(reminder)
        await session.commit()
        # await session.refresh(reminder)




#!                      SELECT REMINDERS
    

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
        .where(dr.time == time_now))
        result = await session.execute(stmt)
        return result.all()


async def select_all_hourly_reminder():
    async with async_session_factory() as session:
        stmt = (select(HourlyNewReminderOrm))
        result = await session.execute(stmt)
        return result.scalars().all()






#!                          SELECT USER's REMINDERS

async def select_my_active_one_time_reminders(tg_id):
    async with async_session_factory() as session:
        user = await select_user(tg_id=tg_id)

        ot = aliased(OneTimeNewReminderOrm)

        combined_datetime = cast(func.concat(ot.date, ' ', ot.remind_at), DateTime)
        local_datetime = combined_datetime + text(f"INTERVAL '{int(user.timezone)} hours'")

        stmt = (
            select(ot, local_datetime.label("remind_at"))
            .where(
                and_(
                    ot.user_id == user.id,
                    ot.is_active == True
                )
            )
            .order_by(ot.date, ot.remind_at)
        )
        result = await session.execute(stmt)
        return result.all()  # вернётся список [(reminder, local_time), ...]


async def select_my_archive_one_time_reminders(tg_id):
    async with async_session_factory() as session:
        user = await select_user(tg_id=tg_id)


        ot = aliased(OneTimeNewReminderOrm)

        combined_datetime = cast(func.concat(ot.date, ' ', ot.remind_at), DateTime)
        local_datetime = combined_datetime + text(f"INTERVAL '{int(user.timezone)} hours'")

        stmt = (
            select(ot, local_datetime.label("remind_at"))
            .where(
                and_(
                    ot.user_id == user.id,
                    ot.is_active == False
                )
            )
            .order_by(ot.date, ot.remind_at)
        )
        result = await session.execute(stmt)
        return result.all() 






async def select_my_active_daily_reminders(tg_id):
     async with async_session_factory() as session:
        user = await select_user(tg_id=tg_id)

        stmt = (
            select(DailyNewReminderOrm)
            .options(joinedload(DailyNewReminderOrm.times))
            .where(
                and_(DailyNewReminderOrm.user_id == user.id, DailyNewReminderOrm.is_active == True))
            .order_by(DailyNewReminderOrm.description)
        )

        result = await session.execute(stmt)
        reminders = result.unique().scalars().all()

        for r in reminders:
            for t in r.times:
                shifted = (datetime.datetime.combine(datetime.date.today(), t.time) + datetime.timedelta(hours=int(user.timezone))).time()
                t.local_time = shifted  
        return reminders




async def select_my_archive_daily_reminders(tg_id):
     async with async_session_factory() as session:
        user = await select_user(tg_id=tg_id)

        stmt = (
            select(DailyNewReminderOrm)
            .options(joinedload(DailyNewReminderOrm.times))
            .where(
                and_(DailyNewReminderOrm.user_id == user.id, DailyNewReminderOrm.is_active == False))
            .order_by(DailyNewReminderOrm.description)
        )

        result = await session.execute(stmt)
        reminders = result.unique().scalars().all()

        # Сдвигаем время в каждой time
        for r in reminders:
            for t in r.times:
                shifted = (datetime.datetime.combine(datetime.date.today(), t.time) + datetime.timedelta(hours=int(user.timezone))).time()
                t.local_time = shifted  
        return reminders


async def select_my_active_hourly_reminders(tg_id):
    async with async_session_factory() as session:
        user = await select_user(tg_id=tg_id)

        hn = aliased(HourlyNewReminderOrm)

        stmt = (
            select(hn)
            .where(and_(hn.user_id == user.id, hn.is_active == True))
            .order_by(hn.interval_min)
        )

        result = await session.execute(stmt)
        reminders = result.scalars().all()

        for r in reminders:
            r.start_time_local = (datetime.datetime.combine(datetime.date.today(), r.start_time) + datetime.timedelta(hours=int(user.timezone))).time()
            r.end_time_local = (datetime.datetime.combine(datetime.date.today(), r.end_time) + datetime.timedelta(hours=int(user.timezone))).time()

        return reminders


async def select_my_archive_hourly_reminders(tg_id):
    async with async_session_factory() as session:
        user = await select_user(tg_id=tg_id)

        hn = aliased(HourlyNewReminderOrm)

        stmt = (
            select(hn)
            .where(and_(hn.user_id == user.id, hn.is_active == False))
            .order_by(hn.interval_min)
        )

        result = await session.execute(stmt)
        reminders = result.scalars().all()

        for r in reminders:
            r.start_time_local = (datetime.datetime.combine(datetime.date.today(), r.start_time) + datetime.timedelta(hours=int(user.timezone))).time()
            r.end_time_local = (datetime.datetime.combine(datetime.date.today(), r.end_time) + datetime.timedelta(hours=int(user.timezone))).time()

        return reminders
    



async def select_my_active_yearly_reminders(tg_id):
    async with async_session_factory() as session:
        user = await select_user(tg_id=tg_id)

        yn = aliased(YearlyNewReminderOrm)

        stmt = (
            select(yn)
            .where(and_(yn.user_id == user.id, yn.is_active == True))
            .order_by(yn.month, yn.day)
        )

        result = await session.execute(stmt)
        reminders = result.scalars().all()

        return reminders


async def select_my_archive_yearly_reminders(tg_id):
    async with async_session_factory() as session:
        user = await select_user(tg_id=tg_id)

        yn = aliased(YearlyNewReminderOrm)

        stmt = (
            select(yn)
            .where(and_(yn.user_id == user.id, yn.is_active == False))
            .order_by(yn.month, yn.day)
        )

        result = await session.execute(stmt)
        reminders = result.scalars().all()

        return reminders



#!                              REMINDERS CONTROL

async def deactivate_reminder(reminder_id: int, type_: str):
    async with async_session_factory() as session:
        model = get_model_by_type(type_)
        reminder = await session.get(model, reminder_id)
        user = await select_user_id(reminder.user_id)
        if reminder:
            reminder.is_active = False
            if type_ == "hourly":
                remove_hourly_reminder_jobs(user_id=user.tg_id, reminder_id=reminder.id)
            await session.commit()

async def activate_reminder(reminder_id: int, type_: str):
    async with async_session_factory() as session:
        model = get_model_by_type(type_)
        reminder = await session.get(model, reminder_id)
        if reminder:
            reminder.is_active = True
            await session.commit()



async def delete_reminder(reminder_id: int, type_: str):
    async with async_session_factory() as session:
        model = get_model_by_type(type_)
        reminder = await session.get(model, reminder_id)
        user = await select_user_id(reminder.user_id)
        if reminder:
            await session.delete(reminder)
            if type_ == "hourly":
                remove_hourly_reminder_jobs(user_id=user.tg_id, reminder_id=reminder.id)
            await session.commit()
    





#!                          UPDATE REMINDERS


async def update_onetime_reminder(reminder_id: int, **kwargs):
    async with async_session_factory() as session:

        stmt = select(OneTimeNewReminderOrm).where(OneTimeNewReminderOrm.id == reminder_id)
        result = await session.execute(stmt)
        reminder = result.scalar_one()

        if "description" in kwargs:
            reminder.description = kwargs["description"]
        
        if "date" in kwargs:

            tz = await select_timezone(user_id=reminder.user_id)
            remind_at = kwargs.get("remind_at") if kwargs.get("remind_at") is not None else reminder.remind_at

            year_, month_, day_ = map(int, kwargs["date"].split("-"))
            dt_combined = datetime.datetime.combine(datetime.date(year=year_, month=month_, day=day_), remind_at)
            shifted_dt = dt_combined - datetime.timedelta(hours=int(tz))

            stmt = (
                update(OneTimeNewReminderOrm)
                .where(OneTimeNewReminderOrm.id == reminder_id)
                .values(date=shifted_dt.date())
            )
            await session.execute(stmt)


        if "remind_at" in kwargs:
            tz = await select_timezone(user_id=reminder.user_id)
            date = kwargs.get("date") if kwargs.get("date") is not None else reminder.date

            if isinstance(date, str):
                year_, month_, day_ = map(int, date.split("-"))
                date = datetime.date(year_, month_, day_)

            dt_combined = datetime.datetime.combine(date, kwargs["remind_at"])
            shifted_dt = dt_combined - datetime.timedelta(hours=int(tz))

            stmt = (
                update(OneTimeNewReminderOrm)
                .where(OneTimeNewReminderOrm.id == reminder_id)
                .values(remind_at=shifted_dt.time())
            )
            await session.execute(stmt)

        await session.commit()



async def update_daily_reminder(reminder_id: int, **kwargs):
    async with async_session_factory() as session:

        stmt = select(DailyNewReminderOrm).where(DailyNewReminderOrm.id == reminder_id)
        result = await session.execute(stmt)
        reminder = result.scalar_one()


        if "description" in kwargs:
            reminder.description = kwargs["description"]

        if "times" in kwargs:
            new_times: list[datetime.time] = kwargs["times"]

            await session.execute(
                delete(DailyReminderTimes).where(DailyReminderTimes.reminder_id == reminder_id)
            )

            tz = await select_timezone(user_id=reminder.user_id)

            shifted_times = [
                (datetime.datetime.combine(datetime.date.today(), t) - datetime.timedelta(hours=int(tz))).time()
                for t in new_times
            ]

            for t in shifted_times:
                session.add(DailyReminderTimes(reminder_id=reminder_id, time=t))

        await session.commit()



async def update_hourly_reminder(reminder_id: int, **kwargs):
    async with async_session_factory() as session:
        stmt = select(HourlyNewReminderOrm).where(HourlyNewReminderOrm.id == reminder_id)
        result = await session.execute(stmt)
        reminder = result.scalar_one()

        if "description" in kwargs:
            reminder.description = kwargs["description"]

        if "interval_min" in kwargs:
            reminder.interval_min = kwargs["interval_min"]

        if "start_time" in kwargs and "end_time" in kwargs:
            tz = await select_timezone(user_id=reminder.user_id)
            dt_st = datetime.datetime.combine(datetime.datetime.today(), kwargs["start_time"])
            dt_et = datetime.datetime.combine(datetime.datetime.today(), kwargs["end_time"])

            shifted_start_time = (dt_st - datetime.timedelta(hours=int(tz))).time()
            shifted_end_time = (dt_et - datetime.timedelta(hours=int(tz))).time()
        
            stmt = (
                update(HourlyNewReminderOrm)
                .where(HourlyNewReminderOrm.id == reminder_id)
                .values(start_time= shifted_start_time,
                    end_time=shifted_end_time)
            )
            await session.execute(stmt)

        await session.commit()





async def update_yearly_reminder(reminder_id: int, **kwargs):
    async with async_session_factory() as session:
        stmt = select(YearlyNewReminderOrm).where(YearlyNewReminderOrm.id == reminder_id)
        result = await session.execute(stmt)
        reminder = result.scalar_one()

        if "description" in kwargs:
            reminder.description = kwargs["description"]

        if "day" in kwargs:
            reminder.day = kwargs["day"]

        if "month" in kwargs:
            reminder.month = kwargs["month"]


        await session.commit()


    




