
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from lexicon.lexicon_keyboards import lexicon_kb




async def merge_keyboards(kb1: InlineKeyboardMarkup, kb2: InlineKeyboardMarkup):
    return InlineKeyboardMarkup(inline_keyboard=kb1.inline_keyboard + kb2.inline_keyboard)


async def back_to_main(lang):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text = lexicon_kb[lang]["back_to_main"], callback_data='back_main')]])

async def back_button(lang : str, prev_state: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=lexicon_kb[lang]["get_back"], callback_data=f"{prev_state}")]]
    )