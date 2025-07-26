
import datetime
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


import src.keyboards.new_remind_keyboard as newkb
import src.keyboards.main_keyboard as mainkb


from src.db.queries.orm import count_yearly_reminders, select_user, yearly_reminder_add
from src.db.schemas import DateSchema, DesciptionSchema

from src.lexicon.lexicon_handlers import lexicon_hdl, reminders_limit

from pydantic import ValidationError

from utils.telegram import safe_delete, safe_edit_text




router = Router()




class Yearly(StatesGroup):
    yearly_name = State()
    yearly_date = State()
    
    yearly_edit_name = State()
    yearly_edit_date = State()

    first_mes_id = State()


MAX_REMINDERS = 4




@router.callback_query(F.data == 'yearly')
async def once_name(callback: CallbackQuery, state: FSMContext):

    if await state.get_state():
        await state.clear()

    user = await select_user(callback.from_user.id)

    if await count_yearly_reminders(callback.from_user.id) >= MAX_REMINDERS:
        await callback.answer(
        text=reminders_limit(lang=user.language, max_=MAX_REMINDERS),
        show_alert=True)
        return

    await state.update_data(first_mes_id = callback.message.message_id)


    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_title"], 
                                    parse_mode="Markdown",
                                    reply_markup=await newkb.new_cancel_button(user.language))
    
    await state.set_state(Yearly.yearly_name)




@router.message(Yearly.yearly_name)
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
                text=f"{lexicon_hdl[user.language]['wrong_title']}\n\n{lexicon_hdl[user.language]['ask_title']}",
                reply_markup=await newkb.new_cancel_button(user.language),
                parse_mode="Markdown"
            )
        return

    await state.update_data(yearly_name=message.text)

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=f"{lexicon_hdl[user.language]['ask_date']} dd/mm", 
                                reply_markup=await newkb.new_cancel_button(user.language))
    
    await state.set_state(Yearly.yearly_date)

    
    


@router.message(Yearly.yearly_date)
async def once_time(message : Message, state: FSMContext):

    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        DateSchema.model_validate({"date_" : message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
                bot=message.bot,
                message=message,
                chat_id=message.chat.id,
                message_id=data["first_mes_id"],
                text=f"{lexicon_hdl[user.language]['wrong_date']} !\n\n{lexicon_hdl[user.language]['ask_date']}",
                parse_mode= "Markdown",
                reply_markup= await newkb.new_cancel_button(user.language)
            )
        return
    

    await state.update_data(yearly_date = message.text)
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[user.language]["check"], 
                                reply_markup=await newkb.new_yearly_check(user.language, data["yearly_name"], data["yearly_date"]))
    
    await state.set_state(None)




@router.callback_query(F.data == 'editreg_yearly_name')
async def once_edit_name(callback: CallbackQuery, state: FSMContext):
    user = await select_user(callback.from_user.id)
    await state.update_data(first_mes_id = callback.message.message_id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_title"], 
                                    parse_mode="Markdown",
                                    reply_markup=await newkb.new_hourly_do_not_change(user.language))

    await state.set_state(Yearly.yearly_edit_name)



@router.callback_query(F.data == 'editreg_yearly_date')
async def once_edit_date(callback : CallbackQuery, state: FSMContext):
    user = await select_user(callback.from_user.id)
    await state.update_data(first_mes_id = callback.message.message_id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["ask_date"], 
                                    parse_mode="Markdown",
                                    reply_markup=await newkb.new_hourly_do_not_change(user.language))

    await state.set_state(Yearly.yearly_edit_date)

    
 


@router.callback_query(F.data == "reg_yearly_do_not_change")
async def remind_check(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    user = await select_user(callback.from_user.id)

    await callback.message.edit_text(text=lexicon_hdl[user.language]["check"], 
                                reply_markup=await newkb.new_yearly_check(user.language, data["yearly_name"], data["yearly_date"]))
    

    await state.set_state(None)




async def update_yearly_reminder_field(lang, state: FSMContext, field: str, value: str, message: Message):

    await state.update_data(**{field: value})
    data = await state.get_data()

    await safe_delete(message)

    await message.bot.edit_message_text(chat_id=message.chat.id,
                                message_id=data["first_mes_id"],
                                text=lexicon_hdl[lang]["check"], 
                                reply_markup=await newkb.new_yearly_check(lang, data["yearly_name"], data["yearly_date"]))
    
    await state.set_state(None)


@router.message(Yearly.yearly_edit_name)
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
                text=f"{lexicon_hdl[user.language]['wrong_title']}\n\n{lexicon_hdl[user.language]['ask_title']}",
                reply_markup=await newkb.new_hourly_do_not_change(user.language),
                parse_mode="Markdown"
            )
        return


    await update_yearly_reminder_field(user.language, state, "yearly_name", message.text, message)




@router.message(Yearly.yearly_edit_date)
async def edit_time(message: Message, state: FSMContext):
    
    user = await select_user(message.from_user.id)
    data = await state.get_data()

    try:
        DateSchema.model_validate({"date_" : message.text})
    except ValidationError as e:
        await safe_delete(message)
        await safe_edit_text(
                bot=message.bot,
                message=message,
                chat_id=message.chat.id,
                message_id=data["first_mes_id"],
                text=f"{lexicon_hdl[user.language]['wrong_date']} !\n\n{lexicon_hdl[user.language]['ask_date']}",
                parse_mode= "Markdown",
                reply_markup=await newkb.new_hourly_do_not_change(user.language)
            )
        return
    
            
    await update_yearly_reminder_field(user.language, state, "yearly_date", message.text, message)



@router.callback_query(F.data == 'new_yearly_create')
async def create_remind(callback : CallbackQuery, state: FSMContext):
    user = await select_user(tg_id=callback.from_user.id)
    

    if await count_yearly_reminders(callback.from_user.id) >= MAX_REMINDERS:
        await callback.answer(
        text=reminders_limit(lang=user.language, max_=MAX_REMINDERS),
        show_alert=True)

    else:
        data = await state.get_data()

        day, month = data["yearly_date"].split("/")

        await yearly_reminder_add(user_id=user.id,
                                description=data["yearly_name"],
                                day=int(day),
                                month=int(month))
        
    await state.clear()
    await callback.message.edit_text(text = lexicon_hdl[user.language]["main_menu"], reply_markup=await mainkb.main_kb(user.language))
