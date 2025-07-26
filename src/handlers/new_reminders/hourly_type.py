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

from src.db.queries.orm import count_hourly_reminders, hourly_reminder_add, select_user, daily_reminder_add
from src.db.schemas import DesciptionSchema, IntervalSchema, TimeSchema
from pydantic import ValidationError

from src.lexicon.lexicon_handlers import lexicon_hdl, reminders_limit
from utils.telegram import safe_delete, safe_edit_text



router = Router()


#                                             #* TYPE REGULAR 
#                                             #! HOURLY

class New_hourly(StatesGroup):
    reg_hourly_name = State()
    reg_hourly_interval = State()
    reg_hourly_start_time = State()
    reg_hourly_end_time = State()

    reg_hourly_edit_name = State()
    reg_hourly_edit_interval = State()
    reg_hourly_edit_start_time = State()
    reg_hourly_edit_end_time = State()


MAX_REMINDERS = 3


@router.callback_query(F.data == "hourly")
async def hourly_title(callback: CallbackQuery, state: FSMContext):

    user = await select_user(callback.from_user.id)

    if await count_hourly_reminders(callback.from_user.id) >= MAX_REMINDERS:
        await callback.answer(
        text=reminders_limit(lang=user.language, max_=MAX_REMINDERS),
        show_alert=True 
        )
        return
    
    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_hourly_title"],
                                     parse_mode="Markdown",
                                     reply_markup=await newkb.regular_type_cancel_button(user.language))

    await state.set_state(New_hourly.reg_hourly_name)


@router.message(New_hourly.reg_hourly_name)
async def hourly_interval(message: Message, state: FSMContext):
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
            text=f"{lexicon_hdl[user.language]['wrong_title']}\n\n{lexicon_hdl[user.language]['ask_hourly_title']}",
            reply_markup=await newkb.regular_type_cancel_button(user.language),
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(reg_hourly_name = message.text)
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[user.language]["ask_hourly_interval"], 
                                reply_markup=await newkb.regular_type_cancel_button(user.language), 
                                parse_mode="Markdown")
    
    await state.set_state(New_hourly.reg_hourly_interval)

    
@router.message(New_hourly.reg_hourly_interval)
async def hourly_start_time(message: Message, state: FSMContext):

    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        
        IntervalSchema.model_validate({"interval": message.text})

    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_interval']}\n\n{lexicon_hdl[user.language]['ask_hourly_interval']}",
            reply_markup=await newkb.regular_type_cancel_button(user.language),
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(reg_hourly_interval=message.text)
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[user.language]["ask_hourly_start_time"], 
                                reply_markup=await newkb.regular_type_cancel_button(user.language), 
                                parse_mode="Markdown")
    
    await state.set_state(New_hourly.reg_hourly_start_time)




    
@router.message(New_hourly.reg_hourly_start_time)
async def hourly_start_time(message: Message, state: FSMContext):

    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        TimeSchema.model_validate({"time": message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time']}\n\n{lexicon_hdl[user.language]['ask_hourly_start_time']}",
            reply_markup=await newkb.regular_type_cancel_button(user.language),
            parse_mode="Markdown"
        )
        return
    

    await state.update_data(reg_hourly_start_time=message.text)
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[user.language]["ask_hourly_end_time"], 
                                reply_markup=await newkb.regular_type_cancel_button(user.language), 
                                parse_mode="Markdown")
    
    await state.set_state(New_hourly.reg_hourly_end_time)



    
@router.message(New_hourly.reg_hourly_end_time)
async def hourly_start_time(message: Message, state: FSMContext):

    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        TimeSchema.model_validate({"time": message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time']}\n\n{lexicon_hdl[user.language]['ask_hourly_end_time']}",
            reply_markup=await newkb.regular_type_cancel_button(user.language),
            parse_mode="Markdown"
        )
        return
    
    await state.update_data(reg_hourly_end_time=message.text)
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[user.language]["check_hourly"], 
                                reply_markup=await newkb.new_hourly_check(
                                    lang=user.language,
                                    name=data["reg_hourly_name"],
                                    interval=data["reg_hourly_interval"],
                                    start_time=data["reg_hourly_start_time"],
                                    end_time=data["reg_hourly_end_time"]
                                ), 
                                parse_mode="Markdown")
    await state.set_state(None)




@router.callback_query(F.data == "editreg_hourly_name")
async def edit_name(callback: CallbackQuery, state: FSMContext):
    
    user = await select_user(callback.from_user.id)
    await state.update_data(first_mes_id = callback.message.message_id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_hourly_name"], 
                                    parse_mode="Markdown",
                                    reply_markup=await newkb.new_hourly_do_not_change(user.language))
    
    await state.set_state(New_hourly.reg_hourly_edit_name)


@router.callback_query(F.data == "editreg_hourly_interval")
async def edit_interval(callback: CallbackQuery, state: FSMContext):

    user = await select_user(callback.from_user.id)
    await state.update_data(first_mes_id = callback.message.message_id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_hourly_interval"], 
                                    parse_mode="Markdown",
                                    reply_markup=await newkb.new_hourly_do_not_change(user.language))
    
    await state.set_state(New_hourly.reg_hourly_edit_interval)


@router.callback_query(F.data == "editreg_hourly_start_time")
async def edit_start_time(callback: CallbackQuery, state: FSMContext):

    user = await select_user(callback.from_user.id)
    await state.update_data(first_mes_id = callback.message.message_id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_hourly_start_time"], 
                                    parse_mode="Markdown",
                                    reply_markup=await newkb.new_hourly_do_not_change(user.language))
    
    await state.set_state(New_hourly.reg_hourly_edit_start_time)
     


@router.callback_query(F.data == "editreg_hourly_end_time")
async def edit_end_time(callback: CallbackQuery, state: FSMContext):

    user = await select_user(callback.from_user.id)
    await state.update_data(first_mes_id = callback.message.message_id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_hourly_end_time"], 
                                    parse_mode="Markdown",
                                    reply_markup=await newkb.new_hourly_do_not_change(user.language))
    
    await state.set_state(New_hourly.reg_hourly_edit_end_time)


@router.callback_query(F.data == "reg_hourly_do_not_change")
async def remind_check(callback: CallbackQuery, state: FSMContext):
    user = await select_user(callback.from_user.id)
    data = await state.get_data()

    await callback.message.edit_text(text=lexicon_hdl[user.language]["check_daily"], 
                                    reply_markup=await newkb.new_hourly_check(
                                        lang=user.language,
                                        name=data["reg_hourly_name"],
                                        interval=data["reg_hourly_interval"],
                                        start_time=data["reg_hourly_start_time"],
                                        end_time=data["reg_hourly_end_time"]
                                    ),
                                    parse_mode="Markdown")
    
    await state.set_state(None)


async def update_reminder_field(lang, state: FSMContext, field: str, value: str, message: Message):
    await state.update_data(**{field: value})
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[lang]["check_hourly"], 
                                reply_markup=await newkb.new_hourly_check(
                                        lang=lang,
                                        name=data["reg_hourly_name"],
                                        interval=data["reg_hourly_interval"],
                                        start_time=data["reg_hourly_start_time"],
                                        end_time=data["reg_hourly_end_time"]
                                    ))
    await state.set_state(None)


@router.message(New_hourly.reg_hourly_edit_name)
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
            text=f"{lexicon_hdl[user.language]['wrong_title']}\n\n{lexicon_hdl[user.language]['ask_hourly_title']}",
            reply_markup=await newkb.new_hourly_do_not_change(user.language),
            parse_mode="Markdown"
        )
        return
    
    await update_reminder_field(user.language, state, "reg_hourly_name", message.text, message)

@router.message(New_hourly.reg_hourly_edit_interval)
async def edit_interval(message: Message, state: FSMContext):
    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        IntervalSchema.model_validate({"interval": int(message.text)})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_interval']}\n\n{lexicon_hdl[user.language]['ask_hourly_interval']}",
            reply_markup=await newkb.new_hourly_do_not_change(user.language),
            parse_mode="Markdown"
        )
        return
    
    await update_reminder_field(user.language, state, "reg_hourly_interval", message.text, message)

@router.message(New_hourly.reg_hourly_edit_start_time)
async def edit_starttime(message: Message, state: FSMContext):
    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        TimeSchema.model_validate({"time": message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time']}\n\n{lexicon_hdl[user.language]['ask_hourly_start_time']}",
            reply_markup=await newkb.new_hourly_do_not_change(user.language),
            parse_mode="Markdown"
        )
        return
    
    await update_reminder_field(user.language, state, "reg_hourly_start_time", message.text, message)


@router.message(New_hourly.reg_hourly_edit_end_time)
async def edit_endtime(message: Message, state: FSMContext):
    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        TimeSchema.model_validate({"time": message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
            bot=message.bot,
            message=message,
            chat_id=message.chat.id,
            message_id=data["first_mes_id"],
            text=f"{lexicon_hdl[user.language]['wrong_time']}\n\n{lexicon_hdl[user.language]['ask_hourly_end_time']}",
            reply_markup=await newkb.new_hourly_do_not_change(user.language),
            parse_mode="Markdown"
        )
        return
    
    await update_reminder_field(user.language, state, "reg_hourly_end_time", message.text, message)



@router.callback_query(F.data == "new_hourly_right")
async def create_reg_daily_remind(callback : CallbackQuery, state: FSMContext):
    user = await select_user(callback.from_user.id)

    if await count_hourly_reminders(callback.from_user.id) >= MAX_REMINDERS:
        await callback.answer(
        text=reminders_limit(lang=user.language, max_=MAX_REMINDERS),
        show_alert=True 
        )
        
    else:
        data = await state.get_data()

        start_time = data["reg_hourly_start_time"].split(":")
        end_time = data["reg_hourly_end_time"].split(":")

        await hourly_reminder_add(user_id=user.id,
                                description=data["reg_hourly_name"],
                                interval_min=int(data["reg_hourly_interval"]),
                                start_time=datetime.time(hour=int(start_time[0]), minute=int(start_time[1])),
                                end_time=datetime.time(hour=int(end_time[0]), minute=int(end_time[1])))
    
    await state.clear()
    await callback.message.edit_text(text = lexicon_hdl[user.language]["main_menu"], reply_markup=await mainkb.main_kb(user.language))

