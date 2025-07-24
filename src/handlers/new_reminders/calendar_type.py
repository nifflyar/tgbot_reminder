




from aiogram import Router
from handlers.new_reminders.onetime_type import New, make_calendar
from keyboards.aiogram_calendar.schemas import DialogCalendarCallback

import os

import datetime
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters.callback_data import CallbackData


from handlers.my_reminder import update_my_reminder_field_callback
from src.db.queries.orm import select_user
import src.keyboards.new_remind_keyboard as newkb

from src.keyboards.aiogram_calendar import DialogCalendarCallback

from src.lexicon.lexicon_handlers import lexicon_hdl



router = Router()





@router.callback_query(DialogCalendarCallback.filter())
async def process_dialog_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    user = await select_user(callback_query.from_user.id)
    state_data = await state.get_data()

    if state_data.get("my_data") is True or state_data.get("my_data") is not None:

        _, __ , ___, number, type_, active_archive, page = state_data.get("my_data").split("_")
        cancel_callback=f"edit-remind_{number}_{type_}_{active_archive}_{page}"
        dont_change_callback=f"my_dont_change_{number}_{type_}_{active_archive}_{page}"
      
    else:
        cancel_callback = "new"
        dont_change_callback = "do_not_change"

    cal =  await make_calendar(user_data=user, change_date=state_data.get("bool_date"), cancel_callback=cancel_callback, dont_change_callback=dont_change_callback)
    selected, date = await cal.process_selection(callback_query, callback_data, state)

    if selected:
        
        if state_data.get("day") is not None:
            await state.update_data(day = date.strftime("%d/%m/%Y"))
            state_data = await state.get_data()
            await callback_query.bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=state_data["first_mes_id"],
                                    text=lexicon_hdl[user.language]["check"], 
                                    reply_markup=await newkb.new_remind_last(user.language, state_data["name"], state_data["day"], state_data["time"]))
            
            
        elif state_data.get("my_date_bool") is True or state_data.get("my_date_bool") is not None:
            await state.update_data(my_date = date.strftime("%d/%m/%Y"))
            state_data = await state.get_data()
            await update_my_reminder_field_callback(lang=user.language, tg_id=callback_query.from_user.id, state=state, field="my_date", value=date.strftime("%Y-%m-%d"), callback=callback_query)

        else:
            await state.update_data(day = date.strftime("%d/%m/%Y"))
            await callback_query.message.edit_text(text=lexicon_hdl[user.language]["ask_time"], parse_mode="Markdown",reply_markup= await newkb.new_cancel_button(user.language))
            await state.set_state(New.time)
