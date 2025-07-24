import datetime
import enum
from typing import Annotated, Optional

from sqlalchemy import (
    ARRAY,
    TIMESTAMP,
    CheckConstraint,
    Column,
    Enum,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    PrimaryKeyConstraint,
    String,
    Table,
    text,
    BIGINT,
    TIME
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import Base, str_256


intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=datetime.datetime.utcnow,
    )]




class UsersOrm(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    tg_id: Mapped[int] = mapped_column(unique=True)
    language: Mapped[str]
    timezone: Mapped[str] = mapped_column(nullable=False)
    notifications: Mapped[bool]
    hour_format: Mapped[str]
    timezone_updated_at: Mapped[datetime.datetime] = mapped_column(nullable=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    one_time_reminders: Mapped[list["OneTimeNewReminderOrm"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    hourly_reminders: Mapped[list["HourlyNewReminderOrm"]] = relationship(
    back_populates="user", cascade="all, delete-orphan"
    )
    daily_reminders: Mapped[list["DailyNewReminderOrm"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    weekly_reminders: Mapped[list["WeeklyNewReminderOrm"]] = relationship(
    back_populates="user", cascade="all, delete-orphan"
    )
    monthly_reminders: Mapped[list["MonthlyNewReminderOrm"]] = relationship(
    back_populates="user", cascade="all, delete-orphan"
    )
    yearly_reminders: Mapped[list["YearlyNewReminderOrm"]] = relationship(
    back_populates="user", cascade="all, delete-orphan"
    )



class OneTimeNewReminderOrm(Base):
    __tablename__ = "onetime_new_reminder"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    description: Mapped[str_256]
    date: Mapped[datetime.date]
    remind_at: Mapped[datetime.time]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


    user: Mapped["UsersOrm"] = relationship(back_populates="one_time_reminders")


class DailyReminderTimes(Base):
    __tablename__ = "daily_reminder_times"

    id: Mapped[intpk]
    reminder_id: Mapped[int] = mapped_column(
        ForeignKey("daily_new_reminder.id", ondelete="CASCADE")
    )
    time: Mapped[datetime.time]
    reminder: Mapped["DailyNewReminderOrm"] = relationship(back_populates="times")


class DailyNewReminderOrm(Base):
    __tablename__ = "daily_new_reminder"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    description: Mapped[str_256]
    times: Mapped[list["DailyReminderTimes"]] = relationship(
        back_populates="reminder", cascade="all, delete-orphan"
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UsersOrm"] = relationship(back_populates="daily_reminders")
    


class HourlyNewReminderOrm(Base):
    __tablename__  = "hourly_new_reminder"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    description: Mapped[str_256]
    interval_min: Mapped[int]
    start_time: Mapped[datetime.time]
    end_time: Mapped[datetime.time]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    
    user: Mapped["UsersOrm"] = relationship(back_populates="hourly_reminders")





class YearlyNewReminderOrm(Base):
    __tablename__ = "yearly_new_reminder"
    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    description: Mapped[str_256]
    day: Mapped[int]
    month: Mapped[int]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UsersOrm"] = relationship(back_populates="yearly_reminders")






class WeeklyReminderDays(Base):
    __tablename__ = "weekly_reminder_days"

    id: Mapped[intpk]
    reminder_id: Mapped[int] = mapped_column(
        ForeignKey("weekly_new_reminder.id", ondelete="CASCADE")
    )
    days: Mapped[int] # 0 - sunday, 1 - monday, ... 
    reminder: Mapped["WeeklyNewReminderOrm"] = relationship(back_populates="days")


class WeeklyNewReminderOrm(Base):
    __tablename__ = "weekly_new_reminder"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    description: Mapped[str_256]
    days: Mapped[list["WeeklyReminderDays"]] = relationship(
        back_populates="reminder", cascade="all, delete-orphan"
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UsersOrm"] = relationship(back_populates="weekly_reminders")



class MonthlyReminderDays(Base):
    __tablename__ = "monthly_reminder_days"

    id: Mapped[intpk]
    reminder_id: Mapped[int] = mapped_column(
        ForeignKey("monthly_new_reminder.id", ondelete="CASCADE")
    )
    days: Mapped[int] # a number/s of the day/s
    reminder: Mapped["MonthlyNewReminderOrm"] = relationship(back_populates="days")


class MonthlyNewReminderOrm(Base):
    __tablename__ = "monthly_new_reminder"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    description: Mapped[str_256]
    days: Mapped[list["MonthlyReminderDays"]] = relationship(
        back_populates="reminder", cascade="all, delete-orphan"
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped["UsersOrm"] = relationship(back_populates="monthly_reminders")

