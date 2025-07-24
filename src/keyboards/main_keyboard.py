
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


from lexicon.lexicon_keyboards import lexicon_kb



#!                                  FIRST TIME KEYBOARDS

async def language_choice():
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text = f"русский{lexicon_kb["flags"]["ru"]}", callback_data='ru'),
                                                   InlineKeyboardButton(text = f"english{lexicon_kb["flags"]["en"]}", callback_data='en')]])


async def timezone_keyboard(lang):
    kb = InlineKeyboardBuilder()
    for i in range(2, 7):
        kb.add(InlineKeyboardButton(text=f'UTC+{i+1}', callback_data=f'utc_{lang}_{i+1}'))

    return kb.adjust(3).as_markup()



# !                                          MAIN KEYBOARDS


async def main_kb(lang):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text = lexicon_kb[lang]["new_reminder"], callback_data='new')],
                                                [InlineKeyboardButton(text = lexicon_kb[lang]["my_reminders"], callback_data='mine')],
                                                [InlineKeyboardButton(text = lexicon_kb[lang]["settings"], callback_data='settings'),
                                                InlineKeyboardButton(text = lexicon_kb[lang]["more"], callback_data='more')]])




async def settings_menu(lang : str):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text = lexicon_kb[lang]["notifications"], callback_data='notifications')],
                                                  [InlineKeyboardButton(text = lexicon_kb[lang]["hour_format"], callback_data='hour_format'),
                                                  InlineKeyboardButton(text = lexicon_kb[lang]["change_lang"] + lexicon_kb["flags"][lang], callback_data='change_lang')],
                                                  [InlineKeyboardButton(text = lexicon_kb[lang]["change_timezone"], callback_data='change_timezone')]])


async def more_menu(lang : str):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text = lexicon_kb[lang]["contacts"], url='https://t.me/nifflyar'),
                                                   InlineKeyboardButton(text = lexicon_kb[lang]["donate"], callback_data='donate')]])



#!                                      SETTINGS KEYBOARD


async def change_language_choice(picked : str):
    kb = InlineKeyboardBuilder()
    for i in lexicon_kb["languages"].keys():
        if i != picked:
            kb.add(InlineKeyboardButton(text = lexicon_kb["languages"][i] + lexicon_kb["flags"][i], callback_data=f"lang_chose_{i}"))
        else:
            kb.add(InlineKeyboardButton(text = f'[{lexicon_kb["languages"][i]}{lexicon_kb["flags"][i]}]', callback_data=f"lang_chose_{i}"))

    return kb.adjust(2).as_markup()

async def change_timezone_keyboard(picked : int):
    kb = InlineKeyboardBuilder()
    for i in range(2, 7):
        if i != picked:
            kb.add(InlineKeyboardButton(text=f'UTC+{i+1}', callback_data=f'change_utc_+{i+1}'))
        else:
            kb.add(InlineKeyboardButton(text=f'[UTC+{i+1}]', callback_data=f'change_utc_+{i+1}'))

    return kb.adjust(3).as_markup()
