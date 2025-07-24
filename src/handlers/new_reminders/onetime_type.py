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
from src.keyboards.aiogram_calendar import DialogCalendar, DialogCalendarCallback

from src.db.queries.orm import count_onetime_reminders, onetime_reminder_add, select_user
from src.db.schemas import DesciptionSchema, TimeSchema

from src.lexicon.lexicon_handlers import lexicon_hdl, reminders_limit
from src.lexicon.lexicon_calendar import lexicon_locale, lexicon_calendar

from pydantic import ValidationError

from utils.telegram import safe_delete, safe_edit_text




router = Router()




class New(StatesGroup):
    name = State()
    day = State()
    time = State()
    
    edit_name = State()
    edit_day = State()
    edit_time = State()

    first_mes_id = State()

    bool_date = State()


MAX_REMINDERS = 7

async def make_calendar(user_data, change_date : bool, cancel_callback : str, dont_change_callback) -> DialogCalendar:
    return DialogCalendar(
        labels=lexicon_locale[user_data.language],
        tz=user_data.timezone,
        lang=user_data.language,
        today_btn=lexicon_calendar[user_data.language]["today"],
        tomorrow_btn=lexicon_calendar[user_data.language]["tomorrow"],
        change_date=change_date,
        cancel_callback=cancel_callback,
        dont_change_callback=dont_change_callback
    )



@router.callback_query(F.data == 'onetime')
async def once_name(callback: CallbackQuery, state: FSMContext):

    if await state.get_state():
        await state.clear()

    user = await select_user(callback.from_user.id)

    if await count_onetime_reminders(callback.from_user.id) >= MAX_REMINDERS:
        await callback.answer(
        text=reminders_limit(lang=user.language, max_=MAX_REMINDERS),
        show_alert=True)
        return


    await state.update_data(first_mes_id = callback.message.message_id)
    await state.set_state(New.name)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_title"], 
                                    parse_mode="Markdown",
                                    reply_markup=await newkb.new_cancel_button(user.language))
    


@router.message(New.name)
async def once_date(message : Message, state: FSMContext):

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
                text=f"{lexicon_hdl[user.language]["wrong_title"]}\n\n{lexicon_hdl[user.language]["ask_title"]}",
                reply_markup=await newkb.new_cancel_button(user.language),
                parse_mode="Markdown"
            )
        return

    await state.update_data(name=message.text, bool_date = False)
    data = await state.get_data()

    await safe_delete(message)

    cal = await make_calendar(user_data=user, change_date=data["bool_date"], cancel_callback="new", dont_change_callback="do_not_change")
    await message.bot.edit_message_text(chat_id=message.chat.id,
                            message_id=data["first_mes_id"],
                            text=lexicon_hdl[user.language]["ask_date"], 
                            reply_markup=await cal.start_calendar(),
                            parse_mode="Markdown")
    



@router.message(New.time)
async def once_time(message : Message, state: FSMContext):

    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        TimeSchema.model_validate({"time" : message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
                bot=message.bot,
                message=message,
                chat_id=message.chat.id,
                message_id=data["first_mes_id"],
                text=f"{lexicon_hdl[user.language]["wrong_time"]} !\n\n{lexicon_hdl[user.language]["ask_time"]}",
                parse_mode= "Markdown",
                reply_markup= await newkb.new_cancel_button(user.language)
            )
        return
    

    await state.update_data(time = message.text)
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[user.language]["check"], 
                                reply_markup=await newkb.new_remind_last(user.language, data["name"], data["day"], data["time"]))
    
    await state.set_state(None)




@router.callback_query(F.data == 'editname')
async def once_edit_name(callback: CallbackQuery, state: FSMContext):
    user = await select_user(callback.from_user.id)
    await state.update_data(first_mes_id = callback.message.message_id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_title"], 
                                    parse_mode="Markdown",
                                    reply_markup=await newkb.new_dont_change(user.language))

    await state.set_state(New.edit_name)


@router.callback_query(F.data == 'editdate')
async def once_edit_date(callback : CallbackQuery, state: FSMContext):
    user = await select_user(callback.from_user.id)

    await state.update_data(bool_date=True)
    data = await state.get_data()

    cal = await make_calendar(user_data=user, change_date=True, cancel_callback="new", dont_change_callback="do_not_change")
    await callback.bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[user.language]["ask_date"], 
                                reply_markup=await cal.start_calendar(), 
                                parse_mode="Markdown")
    
    

@router.callback_query(F.data == 'edittime')
async def once_edit_time(callback: CallbackQuery, state: FSMContext):

    user = await select_user(callback.from_user.id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_time"], 
                                     parse_mode="Markdown", 
                                     reply_markup=await newkb.new_dont_change(user.language))
    
    await state.set_state(New.edit_time)



@router.callback_query(F.data == "do_not_change")
async def remind_check(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    user = await select_user(callback.from_user.id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["check"], 
                                    reply_markup=await newkb.new_remind_last(user.language, data["name"], data["day"], data["time"]))
    await state.set_state(None)



async def update_reminder_field(lang, state: FSMContext, field: str, value: str, message: Message):

    await state.update_data(**{field: value})
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[lang]["check"], 
                                reply_markup=await newkb.new_remind_last(lang, data["name"], data["day"], data["time"]))
    
    await state.set_state(None)


@router.message(New.edit_name)
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
                text=f"{lexicon_hdl[user.language]["wrong_title"]}\n\n{lexicon_hdl[user.language]["ask_title"]}", 
                reply_markup=await newkb.new_dont_change(user.language), 
                parse_mode="Markdown")
        return
        
    await update_reminder_field(user.language, state, "name", message.text, message)


@router.message(New.edit_time)
async def edit_time(message: Message, state: FSMContext):
    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        TimeSchema.model_validate({"time" : message.text})
    except ValidationError as e:
        
        await safe_delete(message)
        await safe_edit_text(
                bot=message.bot,
                message=message,
                chat_id=message.chat.id,
                message_id=data["first_mes_id"],
                text=f"{lexicon_hdl[user.language]["wrong_time"]}!\n\n{lexicon_hdl[user.language]["ask_time"]}",
                parse_mode= "Markdown",
                reply_markup= await newkb.new_dont_change(user.language))
        return
            
    await update_reminder_field(user.language, state, "time", message.text, message)



@router.callback_query(F.data == 'new_onetime_create')
async def create_remind(callback : CallbackQuery, state: FSMContext):
    user = await select_user(tg_id=callback.from_user.id)
    

    if await count_onetime_reminders(callback.from_user.id) >= MAX_REMINDERS:
        await callback.answer(
        text=reminders_limit(lang=user.language, max_=MAX_REMINDERS),
        show_alert=True)

    else:
        data = await state.get_data()

        day, month, year = map(int, data['day'].split('/'))
        hours, minutes = map(int, data['time'].split(':'))

        await onetime_reminder_add(user_id=user.id,
                                description=data["name"],
                                date = datetime.date(year=year, month=month, day=day),
                                remind_at=datetime.time(hour=hours, minute=minutes))
        
    await state.clear()
    await callback.message.edit_text(text = lexicon_hdl[user.language]["main_menu"], reply_markup=await mainkb.main_kb(user.language))
