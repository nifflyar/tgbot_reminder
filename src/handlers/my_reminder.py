import datetime
from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from pydantic import ValidationError

from db.schemas import DateSchema, DesciptionSchema, IntervalSchema, TimeSchema
from handlers.new_reminders.onetime_type import make_calendar
import src.keyboards.main_keyboard as mainkb
import src.keyboards.new_remind_keyboard as newkb
import src.keyboards.my_reminder_keyboard as myrkb
from src.keyboards.keyboard_func import merge_keyboards, back_to_main, back_button


from src.db.queries.orm import (
    activate_reminder,
    deactivate_reminder,
    delete_reminder,
    select_my_active_daily_reminders,
    select_my_active_hourly_reminders,
    select_my_active_one_time_reminders,
    select_my_active_yearly_reminders,
    select_my_archive_daily_reminders,
    select_my_archive_hourly_reminders,
    select_my_archive_one_time_reminders,
    select_my_archive_yearly_reminders,
    select_user,
    insert_users,
    update_daily_reminder,
    update_hourly_reminder,
    update_onetime_reminder,
    update_user,
    update_yearly_reminder,
)

from src.lexicon.lexicon_handlers import lexicon_hdl
from utils.telegram import safe_delete, safe_edit_text


router = Router()


async def no_reminders(
    callback: CallbackQuery, lang: str, active_archive: str, type: str
):

    await callback.message.edit_text(
        text=lexicon_hdl[lang]["no_reminders"],
        reply_markup=await myrkb.my_reminders(
            lang=lang,
            len=0,
            page=0,
            active_archive=active_archive,
            type=type,
            has_reminder=False,
        ),
    )


def length_of_reminders(len: int) -> int:
    len_of_reminders = 1 if (len // 5) == 0 else (len // 5)
    len_of_reminders = (
        len_of_reminders + 1
        if ((len // 5) >= 1) and ((len % 5) >= 1)
        else len_of_reminders
    )
    return len_of_reminders


async def select_my_reminders(tg_id, type: str, active_archive: str):
    if type == "onetime":
        if active_archive == "active":
            return await select_my_active_one_time_reminders(tg_id)
        elif active_archive == "archive":
            return await select_my_archive_one_time_reminders(tg_id)

    elif type == "daily":
        if active_archive == "active":
            return await select_my_active_daily_reminders(tg_id)
        elif active_archive == "archive":
            return await select_my_archive_daily_reminders(tg_id)

    elif type == "hourly":
        if active_archive == "active":
            return await select_my_active_hourly_reminders(tg_id)
        elif active_archive == "archive":
            return await select_my_archive_hourly_reminders(tg_id)

    elif type == "yearly":
        if active_archive == "active":
            return await select_my_active_yearly_reminders(tg_id)
        elif active_archive == "archive":
            return await select_my_archive_yearly_reminders(tg_id)


def texts_of_reminders(lang: str, type: str, reminders):
    if type == "onetime":
        texts = [
            f"""{lexicon_hdl[lang]['my_title']}: {reminder.description} \n"""
            f"""{lexicon_hdl[lang]['my_date']}: {reminder.date} \n"""
            f"""{lexicon_hdl[lang]['my_time']}: {local_time.time()}"""
            for reminder, local_time in reminders
        ]

    elif type == "daily":
        texts = [
            f"""{lexicon_hdl[lang]['my_title']}: {reminder.description} \n"""
            f"""{lexicon_hdl[lang]['my_time']}: {", ".join(str(t.local_time) for t in reminder.times)}"""
            for reminder in reminders
        ]

    elif type == "hourly":
        texts = [
            f"""{lexicon_hdl[lang]['my_title']}: {reminder.description} \n"""
            f"""{lexicon_hdl[lang]['interval']}: {reminder.interval_min} \n"""
            f"""{lexicon_hdl[lang]['my_start_time']}: {reminder.start_time_local} \n"""
            f"""{lexicon_hdl[lang]['my_end_time']}: {reminder.end_time_local}"""
            for reminder in reminders
        ]

    elif type == "yearly":
        texts = [
            f"""{lexicon_hdl[lang]['my_title']}: {reminder.description} \n"""
            f"""{lexicon_hdl[lang]['my_date']}: {reminder.day}/{reminder.month}"""
            for reminder in reminders
        ]

    return texts


def text_of_reminders_number(lang: str, type: str, reminders, number: int):

    reminders = reminders[number]

    if type == "onetime":
        texts = f"""{lexicon_hdl[lang]['my_title']}: {reminders[0].description} \n{lexicon_hdl[lang]['my_date']}: {reminders[0].date} \n{lexicon_hdl[lang]['my_time']}: {reminders[1].time()}\n"""

    elif type == "daily":
        texts = f"""{lexicon_hdl[lang]['my_title']}: {reminders.description} \n{lexicon_hdl[lang]['my_time']}: {", ".join(str(t.local_time) for t in reminders.times)}\n"""

    elif type == "hourly":
        texts = f"""{lexicon_hdl[lang]['my_title']}: {reminders.description} \n{lexicon_hdl[lang]['interval']}: {reminders.interval_min} \n{lexicon_hdl[lang]['my_start_time']}: {reminders.start_time_local} \n{lexicon_hdl[lang]['my_end_time']}: {reminders.end_time_local}\n"""

    elif type == "yearly":
        texts = f"""{lexicon_hdl[lang]['my_title']}: {reminders.description} \n{lexicon_hdl[lang]['my_date']}: {reminders.day}/{reminders.month} \n"""

    return texts


def texts_of_reminders_with_numbers(lang: str, type: str, reminders, page: int = 0):
    start = 5 * page
    end = min(5 * (page + 1), len(reminders))

    texts = []

    if type == "onetime":
        for idx, (reminder, local_time) in enumerate(
            reminders[start:end], start=start + 1
        ):
            text = (
                f"{idx}) {lexicon_hdl[lang]['my_title']}: {reminder.description} \n"
                f"{lexicon_hdl[lang]['my_date']}: {reminder.date} \n"
                f"{lexicon_hdl[lang]['my_time']}: {local_time.time()}"
            )
            texts.append(text)

    elif type == "daily":
        for idx, reminder in enumerate(reminders[start:end], start=start + 1):
            times_str = ", ".join(str(t.local_time) for t in reminder.times)
            text = (
                f"{idx}) {lexicon_hdl[lang]['my_title']}: {reminder.description} \n"
                f"{lexicon_hdl[lang]['my_time']}: {times_str}"
            )
            texts.append(text)

    elif type == "hourly":
        for idx, reminder in enumerate(reminders[start:end], start=start + 1):
            text = (
                f"{idx}) {lexicon_hdl[lang]['my_title']}: {reminder.description} \n"
                f"{lexicon_hdl[lang]['interval']}: {reminder.interval_min} \n"
                f"{lexicon_hdl[lang]['my_start_time']}: {reminder.start_time_local} \n"
                f"{lexicon_hdl[lang]['my_end_time']}: {reminder.end_time_local}"
            )
            texts.append(text)

    elif type == "yearly":

        for idx, reminder in enumerate(reminders[start:end], start=start + 1):
            text = (
                f"""{idx}) {lexicon_hdl[lang]['my_title']}: {reminder.description} \n"""
                f"""{lexicon_hdl[lang]['my_date']}: {reminder.day}/{reminder.month}"""
            )
            texts.append(text)

    return texts


def headline_text(lang: str, type: str, active_archive: str):

    if type == "onetime":
        if active_archive == "active":
            texts = f"₊✧ ━⊱ {lexicon_hdl[lang]['active']} / {lexicon_hdl[lang]['onetime_type']} ⊰━ ✧₊\n\n"
        else:
            texts = f"₊✧ ━⊱ {lexicon_hdl[lang]['archive']} / {lexicon_hdl[lang]['onetime_type']} ⊰━ ✧₊\n\n"

    elif type == "daily":
        if active_archive == "active":
            texts = f"₊✧ ━⊱ {lexicon_hdl[lang]['active']} / {lexicon_hdl[lang]['daily_type']} ⊰━ ✧₊\n\n"
        else:
            texts = f"₊✧ ━⊱ {lexicon_hdl[lang]['archive']} / {lexicon_hdl[lang]['daily_type']} ⊰━ ✧₊\n\n"

    elif type == "hourly":
        if active_archive == "active":
            texts = f"₊✧ ━⊱ {lexicon_hdl[lang]['active']} / {lexicon_hdl[lang]['hourly_type']} ⊰━ ✧₊\n\n"
        else:
            texts = f"₊✧ ━⊱ {lexicon_hdl[lang]['archive']} / {lexicon_hdl[lang]['hourly_type']} ⊰━ ✧₊\n\n"

    elif type == "yearly":
        if active_archive == "active":
            texts = f"₊✧ ━⊱ {lexicon_hdl[lang]['active']} / {lexicon_hdl[lang]['yearly_type']} ⊰━ ✧₊\n\n"
        else:
            texts = f"₊✧ ━⊱ {lexicon_hdl[lang]['archive']} / {lexicon_hdl[lang]['yearly_type']} ⊰━ ✧₊\n\n"

    return texts


@router.callback_query(F.data == "mine")
@router.callback_query(F.data == "my_onetime")
async def my_reminders(callback: CallbackQuery):
    user = await select_user(callback.from_user.id)
    reminders = await select_my_active_one_time_reminders(callback.from_user.id)

    if not reminders:
        await no_reminders(
            callback=callback,
            lang=user.language,
            active_archive="active",
            type="onetime",
        )
        return

    texts = texts_of_reminders(user.language, type="onetime", reminders=reminders)
    reminder_text = "\n\n".join(texts[:5])
    len_of_reminders = length_of_reminders(len=len(reminders))

    headline = headline_text(
        lang=user.language, type="onetime", active_archive="active"
    )

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        parse_mode="Markdown",
        reply_markup=await myrkb.my_reminders(
            lang=user.language,
            len=len_of_reminders,
            page=1,
            active_archive="active",
            type="onetime",
        ),
    )


@router.callback_query(F.data == "my_regular")
async def mine(callback: CallbackQuery):
    user = await select_user(callback.from_user.id)
    reminders = await select_my_active_hourly_reminders(callback.from_user.id)

    if not reminders:
        await no_reminders(
            callback=callback,
            lang=user.language,
            active_archive="active",
            type="hourly",
        )
        return

    texts = texts_of_reminders(lang=user.language, type="hourly", reminders=reminders)
    reminder_text = "\n\n".join(texts[:5])

    len_of_reminders = length_of_reminders(len(reminders))

    headline = headline_text(lang=user.language, type="hourly", active_archive="active")

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.my_reminders(
            lang=user.language,
            len=len_of_reminders,
            page=1,
            active_archive="active",
            type="hourly",
        ),
    )


@router.callback_query(F.data == "my_hourly")
async def mine(callback: CallbackQuery):
    user = await select_user(callback.from_user.id)
    reminders = await select_my_active_hourly_reminders(callback.from_user.id)

    if not reminders:
        await no_reminders(
            callback=callback,
            lang=user.language,
            active_archive="active",
            type="hourly",
        )
        return

    texts = texts_of_reminders(lang=user.language, type="hourly", reminders=reminders)
    reminder_text = "\n\n".join(texts[:5])

    len_of_reminders = length_of_reminders(len(reminders))

    headline = headline_text(lang=user.language, type="hourly", active_archive="active")

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.my_reminders(
            lang=user.language,
            len=len_of_reminders,
            page=1,
            active_archive="active",
            type="hourly",
        ),
    )


@router.callback_query(F.data == "my_daily")
async def mine(callback: CallbackQuery):
    user = await select_user(callback.from_user.id)
    reminders = await select_my_active_daily_reminders(callback.from_user.id)

    if not reminders:
        await no_reminders(
            callback=callback, lang=user.language, active_archive="active", type="daily"
        )
        return

    texts = texts_of_reminders(lang=user.language, type="daily", reminders=reminders)
    reminder_text = "\n\n".join(texts[:5])

    len_of_reminders = length_of_reminders(len(reminders))

    headline = headline_text(lang=user.language, type="daily", active_archive="active")

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.my_reminders(
            lang=user.language,
            len=len_of_reminders,
            page=1,
            active_archive="active",
            type="daily",
        ),
    )


@router.callback_query(F.data == "my_yearly")
async def mine(callback: CallbackQuery):
    user = await select_user(callback.from_user.id)
    reminders = await select_my_active_yearly_reminders(callback.from_user.id)

    if not reminders:
        await no_reminders(
            callback=callback,
            lang=user.language,
            active_archive="active",
            type="yearly",
        )
        return

    texts = texts_of_reminders(lang=user.language, type="yearly", reminders=reminders)
    reminder_text = "\n\n".join(texts[:5])

    len_of_reminders = length_of_reminders(len(reminders))

    headline = headline_text(lang=user.language, type="yearly", active_archive="active")

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.my_reminders(
            lang=user.language,
            len=len_of_reminders,
            page=1,
            active_archive="active",
            type="yearly",
        ),
    )


@router.callback_query(F.data.startswith("nextpage_"))
async def next_page(callback: CallbackQuery):

    _, page, type_, active_archive = callback.data.split(
        "_"
    )  # nextpage_{page}_{type}_{active_archive}
    page = int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    if not reminders:
        await no_reminders(
            callback=callback,
            lang=user.language,
            active_archive=active_archive,
            type=type_,
        )
        return

    texts = texts_of_reminders(lang=user.language, type=type_, reminders=reminders)
    reminder_text = "\n\n".join(texts[5 * (page) : (page + 1) * 5])

    len_of_reminders = length_of_reminders(len(reminders))

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.my_reminders(
            lang=user.language,
            len=len_of_reminders,
            page=page + 1,
            active_archive=active_archive,
            type=type_,
        ),
    )


@router.callback_query(F.data.startswith("previouspage_"))
async def previous_page(callback: CallbackQuery):

    _, page, type_, active_archive = callback.data.split(
        "_"
    )  # next_page_{page}_{type}_{active_archive}
    page = int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    if not reminders:
        await no_reminders(
            callback=callback,
            lang=user.language,
            active_archive=active_archive,
            type=type_,
        )
        return

    texts = texts_of_reminders(lang=user.language, type=type_, reminders=reminders)
    reminder_text = "\n\n".join(texts[5 * (page - 2) : (page - 1) * 5])

    len_of_reminders = length_of_reminders(len(reminders))

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.my_reminders(
            lang=user.language,
            len=len_of_reminders,
            page=page - 1,
            active_archive=active_archive,
            type=type_,
        ),
    )


@router.callback_query(F.data.startswith("archive_"))
async def active_reminders(callback: CallbackQuery):

    _, type_, active_archive = callback.data.split(
        "_"
    )  # active_{type}_{active_archive}
    user = await select_user(callback.from_user.id)

    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive="archive"
    )

    if not reminders:
        await no_reminders(
            callback=callback, lang=user.language, active_archive="archive", type=type_
        )
        return

    texts = texts_of_reminders(lang=user.language, type=type_, reminders=reminders)
    reminder_text = "\n\n".join(texts[:5])

    len_of_reminders = length_of_reminders(len(reminders))

    headline = headline_text(lang=user.language, type=type_, active_archive="archive")

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.my_reminders(
            lang=user.language,
            len=len_of_reminders,
            page=1,
            active_archive="archive",
            type=type_,
        ),
    )


@router.callback_query(F.data.startswith("active_"))
async def active_reminders(callback: CallbackQuery):

    _, type_, active_archive = callback.data.split(
        "_"
    )  # active_{type}_{active_archive}

    user = await select_user(callback.from_user.id)

    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive="active"
    )

    if not reminders:
        await no_reminders(
            callback=callback, lang=user.language, active_archive="active", type=type_
        )
        return

    texts = texts_of_reminders(lang=user.language, type=type_, reminders=reminders)
    reminder_text = "\n\n".join(texts[:5])

    len_of_reminders = length_of_reminders(len(reminders))

    headline = headline_text(lang=user.language, type=type_, active_archive="active")

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.my_reminders(
            lang=user.language,
            len=len_of_reminders,
            page=1,
            active_archive="active",
            type=type_,
        ),
    )


@router.callback_query(F.data.startswith("edit_"))
async def edit_reminder(callback: CallbackQuery):

    _, page, type_, active_archive = callback.data.split(
        "_"
    )  # edit_1_{type}_{active_archive}
    page = int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    texts = texts_of_reminders_with_numbers(
        lang=user.language, type=type_, reminders=reminders, page=page - 1
    )
    reminder_text = "\n\n".join(texts[:5])

    len_of_reminders = length_of_reminders(len(reminders))

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.edit_reminder(
            lang=user.language,
            quantity=len(reminders),
            len=len_of_reminders,
            page=page,
            active_archive=active_archive,
            type=type_,
        ),
    )


@router.callback_query(F.data.startswith("editnextpage_"))
async def next_page(callback: CallbackQuery):
    _, page, type_, active_archive = callback.data.split(
        "_"
    )  # editnextpage_{page}_{type}_{active_archive}"
    page = int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    texts = texts_of_reminders_with_numbers(
        lang=user.language, type=type_, reminders=reminders, page=page
    )
    reminder_text = "\n\n".join(texts[:5])
    len_of_reminders = length_of_reminders(len(reminders))

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.edit_reminder(
            lang=user.language,
            quantity=len(reminders),
            len=len_of_reminders,
            page=page + 1,
            active_archive=active_archive,
            type=type_,
        ),
    )


@router.callback_query(F.data.startswith("editpreviouspage_"))
async def previous_page(callback: CallbackQuery):
    _, page, type_, active_archive = callback.data.split(
        "_"
    )  # editpreviouspage__{page}_{type}_{active_archive}"
    page = int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    texts = texts_of_reminders_with_numbers(
        lang=user.language, type=type_, reminders=reminders, page=(page - 2)
    )

    reminder_text = "\n\n".join(texts[:5])
    len_of_reminders = length_of_reminders(len(reminders))

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.edit_reminder(
            lang=user.language,
            quantity=len(reminders),
            len=len_of_reminders,
            page=page - 1,
            active_archive=active_archive,
            type=type_,
        ),
    )


@router.callback_query(F.data.startswith("edit-remind_"))
async def edit_remind(callback: CallbackQuery):
    _, number, type_, active_archive, page = callback.data.split(
        "_"
    )  # edit-remind_{i}__{type}_{active_archive}_{page}
    number, page = int(number), int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )
    texts = text_of_reminders_number(
        lang=user.language, type=type_, reminders=reminders, number=number
    )

    reminder_text = texts

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.editing_reminder(
            lang=user.language,
            active_archive=active_archive,
            page=page,
            type=type_,
            number=number,
        ),
    )


@router.callback_query(F.data.startswith("deletereminder_"))
async def edit_remind(callback: CallbackQuery):
    _, number, page, type_, active_archive = callback.data.split(
        "_"
    )  # deletereminder_{number}_{page}_{type}_{active_archive}'
    number, page = int(number), int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )
    texts = text_of_reminders_number(
        lang=user.language, type=type_, reminders=reminders, number=number
    )

    reminder_text = texts

    await callback.message.edit_text(
        text=f"{lexicon_hdl[user.language]['are_you_sure']}\n\n{reminder_text}",
        reply_markup=await myrkb.delete_reminder(
            lang=user.language,
            active_archive=active_archive,
            page=page,
            type=type_,
            number=number,
        ),
    )


@router.callback_query(F.data.startswith("confirmdeletereminder_"))
async def confirm_delete(callback: CallbackQuery):
    _, number, page, type_, active_archive = callback.data.split(
        "_"
    )  # confirmdelete_{number}_{page}_{type}_{active_archive}'
    number, page = int(number), int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    if type_ == "onetime":
        await delete_reminder((reminders[number][0]).id, type_=type_)
    else:
        await delete_reminder((reminders[number]).id, type_=type_)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    texts = texts_of_reminders_with_numbers(
        lang=user.language, type=type_, reminders=reminders
    )
    reminder_text = "\n\n".join(texts[:5])

    len_of_reminders = length_of_reminders(len(reminders))

    if not reminders:
        reminder_text = lexicon_hdl[user.language]["no_reminders"]

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.edit_reminder(
            lang=user.language,
            quantity=len(reminders),
            len=len_of_reminders,
            page=1,
            active_archive=active_archive,
            type=type_,
        ),
    )


@router.callback_query(F.data.startswith("deactivatereminder_"))
async def edit_remind(callback: CallbackQuery):

    _, number, page, type_, active_archive = callback.data.split(
        "_"
    )  # deactivate_{number}_{page}_{type}_{active_archive}'
    number, page = int(number), int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )
    texts = text_of_reminders_number(
        lang=user.language, type=type_, reminders=reminders, number=number
    )

    reminder_text = texts

    await callback.message.edit_text(
        text=f"{lexicon_hdl[user.language]['are_you_sure']}\n\n{reminder_text}",
        reply_markup=await myrkb.deactivate_reminder(
            lang=user.language,
            active_archive=active_archive,
            page=page,
            type=type_,
            number=number,
        ),
    )


@router.callback_query(F.data.startswith("confirmdeactivatereminder_"))
async def confirm_delete(callback: CallbackQuery):

    _, number, page, type_, active_archive = callback.data.split(
        "_"
    )  # confirmdeact_{number}_{page}_{type}_{active_archive}'
    number, page = int(number), int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    await deactivate_reminder(reminders[number].id, type_=type_)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    texts = texts_of_reminders_with_numbers(
        lang=user.language, type=type_, reminders=reminders
    )
    reminder_text = "\n\n".join(texts[:5])

    len_of_reminders = length_of_reminders(len(reminders))

    if not reminders:
        reminder_text = lexicon_hdl[user.language]["no_reminders"]

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.edit_reminder(
            lang=user.language,
            quantity=len(reminders),
            len=len_of_reminders,
            page=1,
            active_archive=active_archive,
            type=type_,
        ),
    )


@router.callback_query(F.data.startswith("activatereminder_"))
async def edit_remind(callback: CallbackQuery):

    _, number, page, type_, active_archive = callback.data.split(
        "_"
    )  # activate_{number}_{page}_{type}_{active_archive}'
    number, page = int(number), int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )
    texts = text_of_reminders_number(
        lang=user.language, type=type_, reminders=reminders, number=number
    )

    reminder_text = texts

    await callback.message.edit_text(
        text=f"{lexicon_hdl[user.language]['are_you_sure']}\n\n{reminder_text}",
        reply_markup=await myrkb.activate_reminder(
            lang=user.language,
            active_archive=active_archive,
            page=page,
            type=type_,
            number=number,
        ),
    )


@router.callback_query(F.data.startswith("confirmactivatereminder_"))
async def confirm_delete(callback: CallbackQuery):

    _, number, page, type_, active_archive = callback.data.split(
        "_"
    )  # activate_{number}_{page}_{type}_{active_archive}'
    number, page = int(number), int(page)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    await activate_reminder(reminders[number].id, type_=type_)

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    texts = texts_of_reminders_with_numbers(
        lang=user.language, type=type_, reminders=reminders
    )
    reminder_text = "\n\n".join(texts[:5])

    len_of_reminders = length_of_reminders(len(reminders))

    if not reminders:
        reminder_text = lexicon_hdl[user.language]["no_reminders"]

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        reply_markup=await myrkb.edit_reminder(
            lang=user.language,
            quantity=len(reminders),
            len=len_of_reminders,
            page=1,
            active_archive=active_archive,
            type=type_,
        ),
    )


class My(StatesGroup):
    my_name = State()
    my_date = State()
    my_time = State()

    my_yearly_date = State()

    my_interval = State()
    my_start_time = State()
    my_end_time = State()

    my_first_mes_id = State()

    my_data = State()

    my_date_bool = State

    my_bool_date = State()


def edit_texts_of_reminders(
    lang: str,
    type: str,
    reminders,
    number: int,
    desc=None,
    date=None,
    time=None,
    interval=None,
    start_time=None,
    end_time=None,
    yearly_date=None,
):

    if type == "onetime":
        for reminder, local_time in [reminders[number]]:
            description = reminder.description if desc is None else desc
            date_ = reminder.date if date is None or date is True else date
            time_ = local_time.time() if time is None else time

        texts = f"""{lexicon_hdl[lang]['my_title']}: {description} \n{lexicon_hdl[lang]['my_date']}: {date_} \n{lexicon_hdl[lang]['my_time']}: {time_}"""

    elif type == "daily":
        reminder = reminders[number]
        description = reminder.description if desc is None else desc
        time_ = (
            ", ".join(str(t.local_time) for t in reminder.times)
            if time is None
            else time
        )

        texts = f"""{lexicon_hdl[lang]['my_title']}: {description} \n{lexicon_hdl[lang]['my_time']}: {time_}"""

    elif type == "hourly":
        reminder = reminders[number]
        description = reminder.description if desc is None else desc
        interval_ = reminder.interval_min if interval is None else interval
        start_time_ = reminder.start_time_local if start_time is None else start_time
        end_time_ = reminder.end_time_local if end_time is None else end_time

        texts = f"""{lexicon_hdl[lang]['my_title']}: {description} \n{lexicon_hdl[lang]['interval']}: {interval_}\n{lexicon_hdl[lang]['my_start_time']}: {start_time_} \n{lexicon_hdl[lang]['my_end_time']}: {end_time_}"""

    elif type == "yearly":

        reminder = reminders[number]
        description = reminder.description if desc is None else desc

        day = reminder.day if yearly_date is None else yearly_date.split("/")[0]
        month = reminder.month if yearly_date is None else yearly_date.split("/")[1]

        texts = f"""{lexicon_hdl[lang]['my_title']}: {description} \n{lexicon_hdl[lang]['my_date']}: {day}/{month}"""

    return texts


@router.callback_query(F.data.startswith("editreminder_"))
async def edit_remind(callback: CallbackQuery, state: FSMContext):
    _, number, page, type_, active_archive = callback.data.split(
        "_"
    )  # editreminder_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    if await state.get_data():
        await state.clear()

    user = await select_user(callback.from_user.id)
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    texts = text_of_reminders_number(
        lang=user.language, type=type_, reminders=reminders, number=number
    )
    reminder_text = texts

    await state.update_data(
        my_first_mes_id=callback.message.message_id, my_data=callback.data
    )

    if not reminders:
        reminder_text = lexicon_hdl[user.language]["no_reminders"]

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f"{headline}{lexicon_hdl[user.language]['choose_edit']}\n\n{reminder_text}",
        reply_markup=await myrkb.edit_info_reminder(
            lang=user.language,
            active_archive=active_archive,
            page=page,
            type=type_,
            number=number,
        ),
    )


@router.callback_query(F.data.startswith("my_edit_date_"))
async def edit_date(callback: CallbackQuery, state: FSMContext):

    user = await select_user(tg_id=callback.from_user.id)
    await state.update_data(my_date_bool=True, my_data=callback.data)

    _, __, ___, number, page, type_, active_archive = callback.data.split(
        "_"
    )  # my_edit_name_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    cal = await make_calendar(
        user_data=user,
        change_date=True,
        cancel_callback=f"edit-remind_{number}_{type_}_{active_archive}_{page}",
        # edit-remind_{number}_{type}_{active_archive}_{page}
        dont_change_callback=f"my_dont_change_{number}_{type_}_{active_archive}_{page}",
    )
    # my_dont_change_{number}_{type}_{active_archive}_{page}

    state_data = await state.get_data()
    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )
    reminder_text = edit_texts_of_reminders(
        lang=user.language,
        type=type_,
        reminders=reminders,
        number=number,
        desc=state_data.get("my_name"),
        date=state_data.get("my_date"),
        time=state_data.get("my_time"),
        interval=state_data.get("my_interval"),
        start_time=state_data.get("my_start_time"),
        end_time=state_data.get("my_end_time"),
        yearly_date=state_data.get("my_yearly_date"),
    )

    await callback.message.edit_text(
        text=f"{lexicon_hdl[user.language]['my_ask_date']}\n\n{reminder_text}",
        reply_markup=await cal.start_calendar(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data.startswith("my_edit_"))
async def edit_info(callback: CallbackQuery, state: FSMContext):

    _, __, state_name, number, page, type_, active_archive = callback.data.split(
        "_"
    )  # my_edit_name_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    state_data = await state.get_data()

    await state.update_data(
        my_first_mes_id=callback.message.message_id,
        my_data=callback.data,
        my_date_bool=True,
    )

    user = await select_user(callback.from_user.id)

    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    reminder_text = edit_texts_of_reminders(
        lang=user.language,
        type=type_,
        reminders=reminders,
        number=number,
        desc=state_data.get("my_name"),
        date=state_data.get("my_date"),
        time=state_data.get("my_time"),
        interval=state_data.get("my_interval"),
        start_time=state_data.get("my_start_time"),
        end_time=state_data.get("my_end_time"),
        yearly_date=state_data.get("my_yearly_date"),
    )

    ask_text = ""

    match state_name:
        case "name":
            if type_ == "onetime":
                ask_text = lexicon_hdl[user.language]["my_ask_title"]
            else:
                ask_text = lexicon_hdl[user.language]["my_ask_daily_title"]
            await state.set_state(My.my_name)

        case "time":
            if type_ == "onetime":
                ask_text = lexicon_hdl[user.language]["my_ask_time"]
            elif type_ == "daily":
                ask_text = lexicon_hdl[user.language]["my_ask_daily_time"]
            await state.set_state(My.my_time)

        case "yearlydate":
            ask_text = lexicon_hdl[user.language]["my_ask_date"]
            await state.set_state(My.my_yearly_date)

        case "interval":
            ask_text = lexicon_hdl[user.language]["my_ask_hourly_interval"]
            await state.set_state(My.my_interval)
        case "starttime":
            ask_text = lexicon_hdl[user.language]["my_ask_hourly_start_time"]
            await state.set_state(My.my_start_time)
        case "endtime":
            ask_text = lexicon_hdl[user.language]["my_ask_hourly_end_time"]
            await state.set_state(My.my_end_time)

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f"{headline}{ask_text}\n\n{reminder_text}",
        parse_mode="Markdown",
        reply_markup=await myrkb.editing_info(
            lang=user.language,
            active_archive=active_archive,
            page=page,
            type=type_,
            number=number,
        ),
    )


async def update_my_reminder_field(
    lang,
    tg_id,
    state: FSMContext,
    message: Message,
    field: str = None,
    value: str = None,
):

    if field:
        await state.update_data(**{field: value})

    await safe_delete(message)

    state_data = await state.get_data()

    _, __, state_name, number, page, type_, active_archive = state_data[
        "my_data"
    ].split(
        "_"
    )  # my_edit_name_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    reminders = await select_my_reminders(
        tg_id=tg_id, type=type_, active_archive=active_archive
    )

    reminder_text = edit_texts_of_reminders(
        lang=lang,
        type=type_,
        reminders=reminders,
        number=number,
        desc=state_data.get("my_name"),
        date=state_data.get("my_date"),
        yearly_date=state_data.get("my_yearly_date"),
        time=state_data.get("my_time"),
        interval=state_data.get("my_interval"),
        start_time=state_data.get("my_start_time"),
        end_time=state_data.get("my_end_time"),
    )

    headline = headline_text(lang=lang, type=type_, active_archive=active_archive)

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=state_data["my_first_mes_id"],
        text=f'{headline}{lexicon_hdl[lang]["choose_edit"]}\n\n{reminder_text}',
        reply_markup=await myrkb.edit_info_reminder(
            lang=lang,
            active_archive=active_archive,
            page=page,
            type=type_,
            number=number,
        ),
    )

    await state.set_state(None)


async def update_my_reminder_field_callback(
    lang,
    tg_id,
    state: FSMContext,
    callback: CallbackQuery,
    field: str = None,
    value: str = None,
):

    if field:
        await state.update_data(**{field: value})

    state_data = await state.get_data()

    _, __, state_name, number, page, type_, active_archive = state_data[
        "my_data"
    ].split(
        "_"
    )  # my_edit_name_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    reminders = await select_my_reminders(
        tg_id=tg_id, type=type_, active_archive=active_archive
    )

    reminder_text = edit_texts_of_reminders(
        lang=lang,
        type=type_,
        reminders=reminders,
        number=number,
        desc=state_data.get("my_name"),
        date=state_data.get("my_date"),
        yearly_date=state_data.get("my_yearly_date"),
        time=state_data.get("my_time"),
        interval=state_data.get("my_interval"),
        start_time=state_data.get("my_start_time"),
        end_time=state_data.get("my_end_time"),
    )

    headline = headline_text(lang=lang, type=type_, active_archive=active_archive)

    await callback.message.edit_text(
        text=f'{headline}{lexicon_hdl[lang]["choose_edit"]}\n\n{reminder_text}',
        reply_markup=await myrkb.edit_info_reminder(
            lang=lang,
            active_archive=active_archive,
            page=page,
            type=type_,
            number=number,
        ),
    )

    await state.set_state(None)


@router.message(My.my_name)
async def edit_name(message: Message, state: FSMContext):
    user = await select_user(message.from_user.id)

    state_data = await state.get_data()
    _, __, state_name, number, page, type_, active_archive = state_data[
        "my_data"
    ].split(
        "_"
    )  # my_edit_name_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    reminders = await select_my_reminders(
        tg_id=message.from_user.id, type=type_, active_archive=active_archive
    )
    reminder_text = edit_texts_of_reminders(
        lang=user.language,
        type=type_,
        reminders=reminders,
        number=number,
        desc=state_data.get("my_name"),
        date=state_data.get("my_date"),
        time=state_data.get("my_time"),
        interval=state_data.get("my_interval"),
        start_time=state_data.get("my_start_time"),
        end_time=state_data.get("my_end_time"),
        yearly_date=state_data.get("my_yearly_date"),
    )

    try:
        DesciptionSchema.model_validate({"description": message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=state_data["my_first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_title']}\n\n{reminder_text}",
            reply_markup=await myrkb.editing_info(
                lang=user.language,
                active_archive=active_archive,
                page=page,
                type=type_,
                number=number,
            ),
            parse_mode="Markdown",
        )
        return
    await state.update_data(my_name=message.text)
    await update_my_reminder_field(
        lang=user.language,
        tg_id=message.from_user.id,
        state=state,
        field="my_name",
        value=message.text,
        message=message,
    )


@router.message(My.my_yearly_date)
async def edit_date(message: Message, state: FSMContext):
    user = await select_user(message.from_user.id)

    state_data = await state.get_data()
    _, __, state_name, number, page, type_, active_archive = state_data[
        "my_data"
    ].split(
        "_"
    )  # my_edit_name_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    reminders = await select_my_reminders(
        tg_id=message.from_user.id, type=type_, active_archive=active_archive
    )
    reminder_text = edit_texts_of_reminders(
        lang=user.language,
        type=type_,
        reminders=reminders,
        number=number,
        desc=state_data.get("my_name"),
        date=state_data.get("my_date"),
        time=state_data.get("my_time"),
        interval=state_data.get("my_interval"),
        start_time=state_data.get("my_start_time"),
        end_time=state_data.get("my_end_time"),
        yearly_date=state_data.get("my_yearly_date"),
    )

    try:
        DateSchema.model_validate({"date_": message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=state_data["my_first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_date']} !\n\n{reminder_text}",
            parse_mode="Markdown",
            reply_markup=await myrkb.editing_info(
                lang=user.language,
                active_archive=active_archive,
                page=page,
                type=type_,
                number=number,
            ),
        )
        return

    await update_my_reminder_field(
        lang=user.language,
        tg_id=message.from_user.id,
        state=state,
        field="my_yearly_date",
        value=message.text,
        message=message,
    )


@router.message(My.my_time)
async def edit_time(message: Message, state: FSMContext):
    user = await select_user(message.from_user.id)
    state_data = await state.get_data()

    _, __, state_name, number, page, type_, active_archive = state_data[
        "my_data"
    ].split(
        "_"
    )  # my_edit_name_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    reminders = await select_my_reminders(
        tg_id=message.from_user.id, type=type_, active_archive=active_archive
    )
    reminder_text = edit_texts_of_reminders(
        lang=user.language,
        type=type_,
        reminders=reminders,
        number=number,
        desc=state_data.get("my_name"),
        date=state_data.get("my_date"),
        time=state_data.get("my_time"),
        interval=state_data.get("my_interval"),
        start_time=state_data.get("my_start_time"),
        end_time=state_data.get("my_end_time"),
        yearly_date=state_data.get("my_yearly_date"),
    )

    if type_ == "onetime":
        try:
            TimeSchema.model_validate({"time": message.text})
        except ValidationError as e:

            await safe_delete(message)
            await safe_edit_text(
                bot=message.bot,
                message=message,
                chat_id=message.chat.id,
                message_id=state_data["my_first_mes_id"],
                text=f"{lexicon_hdl[user.language]['wrong_time']}!\n\n{lexicon_hdl[user.language]['my_ask_time']}\n\n{reminder_text}",
                parse_mode="Markdown",
                reply_markup=await myrkb.editing_info(
                    lang=user.language,
                    active_archive=active_archive,
                    page=page,
                    type=type_,
                    number=number,
                ),
            )
            return

    if type_ == "daily":
        times = (message.text).split()

        try:
            for time in times:
                TimeSchema.model_validate({"time": time})
        except ValidationError as e:
            await safe_delete(message)
            await safe_edit_text(
                bot=message.bot,
                message=message,
                chat_id=message.chat.id,
                message_id=state_data["my_first_mes_id"],
                text=f"{lexicon_hdl[user.language]['wrong_time']}\n\n{lexicon_hdl[user.language]['my_ask_daily_time']}\n\n{reminder_text}",
                reply_markup=await myrkb.editing_info(
                    lang=user.language,
                    active_archive=active_archive,
                    page=page,
                    type=type_,
                    number=number,
                ),
                parse_mode="Markdown",
            )
            return

    await update_my_reminder_field(
        lang=user.language,
        tg_id=message.from_user.id,
        state=state,
        field="my_time",
        value=message.text,
        message=message,
    )


@router.message(My.my_interval)
async def edit_interval(message: Message, state: FSMContext):

    user = await select_user(message.from_user.id)

    state_data = await state.get_data()
    _, __, state_name, number, page, type_, active_archive = state_data[
        "my_data"
    ].split(
        "_"
    )  # my_edit_name_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    reminders = await select_my_reminders(
        tg_id=message.from_user.id, type=type_, active_archive=active_archive
    )
    reminder_text = edit_texts_of_reminders(
        lang=user.language,
        type=type_,
        reminders=reminders,
        number=number,
        desc=state_data.get("my_name"),
        date=state_data.get("my_date"),
        time=state_data.get("my_time"),
        interval=state_data.get("my_interval"),
        start_time=state_data.get("my_start_time"),
        end_time=state_data.get("my_end_time"),
        yearly_date=state_data.get("my_yearly_date"),
    )

    try:
        IntervalSchema.model_validate({"interval": message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=state_data["my_first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_interval']}\n\n{lexicon_hdl[user.language]['my_ask_hourly_interval']}\n\n{reminder_text}",
            reply_markup=await myrkb.editing_info(
                lang=user.language,
                active_archive=active_archive,
                page=page,
                type=type_,
                number=number,
            ),
            parse_mode="Markdown",
        )
        return
    await update_my_reminder_field(
        lang=user.language,
        tg_id=message.from_user.id,
        state=state,
        field="my_interval",
        value=message.text,
        message=message,
    )


@router.message(My.my_start_time)
async def edit_start_time(message: Message, state: FSMContext):
    user = await select_user(message.from_user.id)

    state_data = await state.get_data()
    _, __, state_name, number, page, type_, active_archive = state_data[
        "my_data"
    ].split(
        "_"
    )  # my_edit_name_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    reminders = await select_my_reminders(
        tg_id=message.from_user.id, type=type_, active_archive=active_archive
    )
    reminder_text = edit_texts_of_reminders(
        lang=user.language,
        type=type_,
        reminders=reminders,
        number=number,
        desc=state_data.get("my_name"),
        date=state_data.get("my_date"),
        time=state_data.get("my_time"),
        interval=state_data.get("my_interval"),
        start_time=state_data.get("my_start_time"),
        end_time=state_data.get("my_end_time"),
        yearly_date=state_data.get("my_yearly_date"),
    )

    try:
        TimeSchema.model_validate({"time": message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=state_data["my_first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time']}\n\n{lexicon_hdl[user.language]['my_ask_hourly_start_time']}\n\n{reminder_text}",
            reply_markup=await myrkb.editing_info(
                lang=user.language,
                active_archive=active_archive,
                page=page,
                type=type_,
                number=number,
            ),
            parse_mode="Markdown",
        )
        return
    await update_my_reminder_field(
        lang=user.language,
        tg_id=message.from_user.id,
        state=state,
        field="my_start_time",
        value=message.text,
        message=message,
    )


@router.message(My.my_end_time)
async def edit_end_time(message: Message, state: FSMContext):
    user = await select_user(message.from_user.id)

    state_data = await state.get_data()
    _, __, state_name, number, page, type_, active_archive = state_data[
        "my_data"
    ].split(
        "_"
    )  # my_edit_name_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    state_data = await state.get_data()
    reminders = await select_my_reminders(
        tg_id=message.from_user.id, type=type_, active_archive=active_archive
    )
    reminder_text = edit_texts_of_reminders(
        lang=user.language,
        type=type_,
        reminders=reminders,
        number=number,
        desc=state_data.get("my_name"),
        date=state_data.get("my_date"),
        time=state_data.get("my_time"),
        interval=state_data.get("my_interval"),
        start_time=state_data.get("my_start_time"),
        end_time=state_data.get("my_end_time"),
        yearly_date=state_data.get("my_yearly_date"),
    )

    try:
        TimeSchema.model_validate({"time": message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=state_data["my_first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time']}\n\n{lexicon_hdl[user.language]['my_ask_hourly_start_time']}\n\n{reminder_text}",
            reply_markup=await myrkb.editing_info(
                lang=user.language,
                active_archive=active_archive,
                page=page,
                type=type_,
                number=number,
            ),
            parse_mode="Markdown",
        )
        return
    await update_my_reminder_field(
        lang=user.language,
        tg_id=message.from_user.id,
        state=state,
        field="my_end_time",
        value=message.text,
        message=message,
    )


@router.callback_query(F.data.startswith("my_dont_change_"))
async def remind_check(callback: CallbackQuery, state: FSMContext):

    user = await select_user(tg_id=callback.from_user.id)

    state_data = await state.get_data()
    _, __, state_name, number, page, type_, active_archive = state_data[
        "my_data"
    ].split(
        "_"
    )  # my_edit_name_{number}_{page}_{type}_{active_archive}
    number, page = int(number), int(page)

    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    reminder_text = edit_texts_of_reminders(
        lang=user.language,
        type=type_,
        reminders=reminders,
        number=number,
        desc=state_data.get("my_name"),
        date=state_data.get("my_date"),
        time=state_data.get("my_time"),
        interval=state_data.get("my_interval"),
        start_time=state_data.get("my_start_time"),
        end_time=state_data.get("my_end_time"),
    )

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    await callback.message.edit_text(
        text=f'{headline}{lexicon_hdl[user.language]["choose_edit"]}\n\n{reminder_text}',
        reply_markup=await myrkb.edit_info_reminder(
            lang=user.language,
            active_archive=active_archive,
            page=page,
            type=type_,
            number=number,
        ),
    )
    await state.set_state(None)


@router.callback_query(F.data.startswith("my_new_save_"))
async def save_changes(callback: CallbackQuery, state: FSMContext):

    state_data = await state.get_data()
    _, __, ___, number, page, type_, active_archive = state_data["my_data"].split(
        "_"
    )  # 'my_new_save_{number}_{page}_{type}_{active_archive}'
    number, page = int(number), int(page)

    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )

    update_fields = {}

    for key, value in state_data.items():

        if value is not None:
            match key:
                case "my_name":
                    update_fields["description"] = value
                case "my_date":
                    update_fields["date"] = value
                case "my_time":
                    if type_ == "onetime":
                        update_fields["remind_at"] = datetime.datetime.strptime(
                            value, "%H:%M"
                        ).time()
                    if type_ == "daily":
                        times = [
                            datetime.time(hour=int(m), minute=int(k))
                            for m, k in [i.split(":") for i in value.split()]
                        ]
                        update_fields["times"] = times

                case "my_interval":
                    update_fields["interval_min"] = int(value)
                case "my_starttime":
                    update_fields["start_time"] = value
                case "my_endtime":
                    update_fields["end_time"] = value
                case "my_yearly_date":
                    update_fields["day"] = int(value.split("/")[0])
                    update_fields["month"] = int(value.split("/")[1])

    match type_:
        case "onetime":
            reminder = reminders[number][0]
            await update_onetime_reminder(reminder_id=reminder.id, **update_fields)

        case "daily":
            reminder = reminders[number]
            await update_daily_reminder(reminder_id=reminder.id, **update_fields)

        case "hourly":
            reminder = reminders[number]
            await update_hourly_reminder(reminder_id=reminder.id, **update_fields)

        case "yearly":
            reminder = reminders[number]
            await update_yearly_reminder(reminder_id=reminder.id, **update_fields)

    user = await select_user(tg_id=callback.from_user.id)

    reminders = await select_my_reminders(
        tg_id=callback.from_user.id, type=type_, active_archive=active_archive
    )
    texts = texts_of_reminders(lang=user.language, type=type_, reminders=reminders)
    reminder_text = "\n\n".join(texts[:5])

    if not reminders:
        reminder_text = lexicon_hdl[user.language]["no_reminders"]

    headline = headline_text(
        lang=user.language, type=type_, active_archive=active_archive
    )

    len_of_reminders = length_of_reminders(len=len(reminders))

    await callback.message.edit_text(
        text=f"{headline}{reminder_text}",
        parse_mode="Markdown",
        reply_markup=await myrkb.my_reminders(
            lang=user.language,
            len=len_of_reminders,
            page=1,
            active_archive=active_archive,
            type=type_,
        ),
    )
