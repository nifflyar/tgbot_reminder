import os

import datetime
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData
from aiogram.exceptions import TelegramBadRequest


import src.keyboards.new_remind_keyboard as newkb
import src.keyboards.main_keyboard as mainkb
from src.keyboards.keyboard_func import merge_keyboards, back_button
from src.keyboards.aiogram_calendar import DialogCalendar, DialogCalendarCallback

from src.db.queries.orm import count_daily_reminders, select_user, daily_reminder_add
from src.db.schemas import DesciptionSchema, TimeSchema
from pydantic import ValidationError

from src.lexicon.lexicon_handlers import lexicon_hdl, reminders_limit
from utils.telegram import safe_delete, safe_edit_text



router = Router()


#                                             #* TYPE REGULAR 
#                                             #! DAILY

class New_daily(StatesGroup):
    reg_daily_name = State()
    reg_daily_time = State()
    reg_daily_edit_time = State()
    reg_daily_edit_name = State()
    reg_daily_type = State()


MAX_REMINDERS = 5
MAX_TIMES  = 4

class TimesLimit(Exception):
    pass


class DuplicateTimeError(Exception):
    pass

def parse_and_validate_times(input_list: list) -> list[datetime.time]:
    raw_times = input_list

    seen = set()
    duplicates = set()
    parsed_times = []

    for t in raw_times:
        if t in seen:
            duplicates.add(t)
        else:
            seen.add(t)

        hour, minute = map(int, t.split(":"))
        parsed_times.append(datetime.time(hour=hour, minute=minute))

    if duplicates:
        raise DuplicateTimeError

    parsed_times.sort()
    return parsed_times



@router.callback_query(F.data == "daily")
async def daily_time(callback: CallbackQuery, state: FSMContext):


    if await count_daily_reminders(callback.from_user.id) >= MAX_REMINDERS:
        await callback.answer(
        text=reminders_limit(lang=user.language, max_=MAX_REMINDERS),
        show_alert=True 
        )
        return
    
    user = await select_user(callback.from_user.id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_daily_title"],
                                     parse_mode="Markdown",
                                     reply_markup=await newkb.regular_type_cancel_button(user.language))
    
    await state.set_state(New_daily.reg_daily_name)



@router.message(New_daily.reg_daily_name)
async def daily_mult(message: Message, state: FSMContext):

    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        DesciptionSchema.model_validate({"description": message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_title']}\n\n{lexicon_hdl[user.language]['ask_daily_title']}",
            reply_markup=await newkb.regular_type_cancel_button(user.language),
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(reg_daily_name = message.text)
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[user.language]["ask_daily_time"], 
                                reply_markup=await newkb.regular_type_cancel_button(user.language), 
                                parse_mode="Markdown")
    
    await state.set_state(New_daily.reg_daily_time)

    
@router.message(New_daily.reg_daily_time)
async def daily_name(message: Message, state: FSMContext):

    data = await state.get_data()
    user = await select_user(message.from_user.id)

    times = (message.text).split()
    try:
        for time in times:
            TimeSchema.model_validate({"time": time})

        parse_and_validate_times(times)

        if len(times) > MAX_TIMES:
            raise TimesLimit
        

    except DuplicateTimeError:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time_duplicate']}\n\n{lexicon_hdl[user.language]['ask_daily_time']}",
            reply_markup=await newkb.regular_type_cancel_button(user.language),
            parse_mode="Markdown"
        )
        return

    except TimesLimit:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time_limit']}\n\n{lexicon_hdl[user.language]['ask_daily_time']}",
            reply_markup=await newkb.regular_type_cancel_button(user.language),
            parse_mode="Markdown"
        )
        return

    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time']}\n\n{lexicon_hdl[user.language]['ask_daily_time']}",
            reply_markup=await newkb.regular_type_cancel_button(user.language),
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(reg_daily_time=message.text)
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[user.language]["check_daily"], 
                                reply_markup=await newkb.new_regular_check(user.language, data["reg_daily_name"], data["reg_daily_time"]), 
                                parse_mode="Markdown")
    await state.set_state(None)


@router.callback_query(F.data == "editreg_daily_time")
async def edit_reg_daily_time(callback: CallbackQuery, state: FSMContext):

    user = await select_user(callback.from_user.id)
    await state.update_data(first_mes_id = callback.message.message_id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_daily_time"], 
                                    parse_mode="Markdown",
                                    reply_markup=await newkb.new_reg_daily_do_not_change(user.language))
    
    await state.set_state(New_daily.reg_daily_edit_time)


@router.callback_query(F.data == "editreg_daily_name")
async def edit_reg_daily_name(callback: CallbackQuery, state: FSMContext):
    user = await select_user(callback.from_user.id)
    await state.update_data(first_mes_id = callback.message.message_id)
    
    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_daily_title"], 
                                    parse_mode="Markdown",
                                    reply_markup=await newkb.new_reg_daily_do_not_change(user.language))
    
    await state.set_state(New_daily.reg_daily_edit_name)
    

@router.callback_query(F.data == "reg_daily_do_not_change")
async def remind_check(callback: CallbackQuery, state: FSMContext):

    user = await select_user(callback.from_user.id)
    data = await state.get_data()

    await callback.message.edit_text(text=lexicon_hdl[user.language]["check_daily"], 
                                    reply_markup=await newkb.new_regular_check(user.language, data["reg_daily_name"], data["reg_daily_time"]),
                                    parse_mode="Markdown")
    
    await state.set_state(None)


async def update_reminder_field(lang, state: FSMContext, field: str, value: str, message: Message):

    await state.update_data(**{field: value})
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[lang]["check_daily"], 
                                reply_markup=await newkb.new_regular_check(lang, data["reg_daily_name"], data["reg_daily_time"]),
                                parse_mode="Markdown")

    await state.set_state(None)


@router.message(New_daily.reg_daily_edit_name)
async def edit_name(message: Message, state: FSMContext):

    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        DesciptionSchema.model_validate({"description": message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_title']}\n\n{lexicon_hdl[user.language]['ask_daily_title']}",
            reply_markup=await newkb.new_reg_daily_do_not_change(user.language),
            parse_mode="Markdown"
        )
        return
    
    await update_reminder_field(user.language, state, "reg_daily_name", message.text, message)



@router.message(New_daily.reg_daily_edit_time)
async def edit_time(message: Message, state: FSMContext):

    user = await select_user(message.from_user.id)
    data = await state.get_data()

    times = (message.text).split()
    try:
        for time in times:
            TimeSchema.model_validate({"time": time})

        parse_and_validate_times(times)

        if len(times) > MAX_TIMES:
            raise TimesLimit
        
    except DuplicateTimeError:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time_duplicate']}\n\n{lexicon_hdl[user.language]['ask_daily_time']}",
            reply_markup=await newkb.new_reg_daily_do_not_change(user.language),
            parse_mode="Markdown"
        )
        return
            
    except TimesLimit:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time_limit']}\n\n{lexicon_hdl[user.language]['ask_daily_time']}",
            reply_markup=await newkb.new_reg_daily_do_not_change(user.language),
            parse_mode="Markdown"
        )
        return
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time']}\n\n{lexicon_hdl[user.language]['ask_daily_time']}",
            reply_markup=await newkb.new_reg_daily_do_not_change(user.language),
            parse_mode="Markdown"
        )
        return
    await update_reminder_field(user.language, state, "reg_daily_time", message.text, message)



@router.callback_query(F.data == "new_daily_right")
async def create_reg_daily_remind(callback : CallbackQuery, state: FSMContext):
    user = await select_user(callback.from_user.id)

    if await count_daily_reminders(callback.from_user.id) >= MAX_REMINDERS:
        await callback.answer(
        text=reminders_limit(lang=user.language, max_=MAX_REMINDERS),
        show_alert=True 
        )

    else:
        data = await state.get_data()
        times = [datetime.time(hour = int(m), minute = int(k)) for m, k in [i.split(":") for i in data["reg_daily_time"].split()]]
        await daily_reminder_add(user.id, data["reg_daily_name"], times)

    await state.clear()
    await callback.message.edit_text(text = lexicon_hdl[user.language]["main_menu"], reply_markup=await mainkb.main_kb(user.language))

