
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


from lexicon.lexicon_keyboards import lexicon_kb


async def new_cancel_button(lang: str):
    return InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text = lexicon_kb[lang]["cancel"], callback_data="new")]])

async def regular_type_cancel_button(lang : str):
    return InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text = lexicon_kb[lang]["cancel"], callback_data="regular")]])


#!                              one time type



async def new_remind_type(lang):
    return InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text = lexicon_kb[lang]["onetime_type"], callback_data="onetime"),
                                                          InlineKeyboardButton(text=lexicon_kb[lang]["regular_type"], callback_data="regular")],
                                                          [InlineKeyboardButton(text = lexicon_kb[lang]["back_to_main"], callback_data='back_main')]])


async def new_remind_first(lang):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text = lexicon_kb[lang]["back_to_main"], callback_data='back_main')]])


async def new_dont_change(lang):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text = lexicon_kb[lang]["dont_change"], callback_data='do_not_change')]])

async def new_remind_last(lang, name, day, time):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text = f"{lexicon_kb[lang]['title']}: {name}", callback_data='editname')],
                                                        [InlineKeyboardButton(text = f"{lexicon_kb[lang]['date']}: {day}", callback_data='editdate')],
                                                        [InlineKeyboardButton(text=f"{lexicon_kb[lang]['time']}: {time}", callback_data='edittime')],
                                                        [InlineKeyboardButton(text=f"{lexicon_kb[lang]['cancel']}", callback_data="new"),
                                                         InlineKeyboardButton(text = f"{lexicon_kb[lang]['create']}", callback_data='new_onetime_create')]])




#!                              daily type



async def new_regular_check(lang, name: str, time: str):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text = f"{lexicon_kb[lang]['title']}: {name}", callback_data='editreg_daily_name')],
                                                        [InlineKeyboardButton(text=f"{lexicon_kb[lang]['time']}: {time}", callback_data='editreg_daily_time')],
                                                        [InlineKeyboardButton(text=f"{lexicon_kb[lang]['cancel']}", callback_data="regular"),
                                                         InlineKeyboardButton(text = f"{lexicon_kb[lang]['create']}", callback_data='new_daily_right')]])


async def new_regular_type(lang):
    return InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text = lexicon_kb[lang]["hourly_type"],
                                                                                 callback_data="hourly")],
                                                    [InlineKeyboardButton(text = lexicon_kb[lang]["daily_type"],
                                                                                 callback_data="daily")],
                                                    [InlineKeyboardButton(text = lexicon_kb[lang]["yearly_type"],
                                                                                 callback_data="yearly")]])

                                                    # [InlineKeyboardButton(text = lexicon_kb[lang]["weekly_type"],
                                                    #                              callback_data="weekly")],
                                                    # [InlineKeyboardButton(text = lexicon_kb[lang]["monthly_type"],
                                                    #                              callback_data="monthly")],
                                                    #                              ]

                                                        #    [InlineKeyboardButton(text = "ежемесячное",
                                                        #                          callback_data="monthly")],
                                                        #    )


async def new_daily(lang):
    return InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text = lexicon_kb[lang]["once_daily"],
                                                                                 callback_data="daily_once")],
                                                    [InlineKeyboardButton(text = lexicon_kb[lang]["many_daily"],
                                                                                 callback_data="daily_mult")]])

                                                    # [InlineKeyboardButton(text = "каждые x минут",
                                                    #                              callback_data="daily_everyxmin")],
                                                    # [InlineKeyboardButton(text = "каждые x часов",
                                                    #                              callback_data="daily_everyxhour")],
                                                    # [InlineKeyboardButton(text = "каждый час в x минуты",
                                                    #                              callback_data="daily_xmin_perhour")]])


async def new_reg_daily_do_not_change(lang):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text=lexicon_kb[lang]["cancel"],callback_data="regular"),
                                                   InlineKeyboardButton(text = lexicon_kb[lang]["dont_change"], callback_data='reg_daily_do_not_change')]])




#!                      HOURLY


async def new_hourly_check(lang, name: str, interval: str, start_time: str, end_time: str):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text = f"{lexicon_kb[lang]['title']}: {name}", callback_data='editreg_hourly_name')],
                                                        [InlineKeyboardButton(text=f"{lexicon_kb[lang]['interval']}: {interval}", callback_data='editreg_hourly_interval')],
                                                        [InlineKeyboardButton(text=f"{lexicon_kb[lang]['start_time']}: {start_time}", callback_data='editreg_hourly_start_time')],
                                                        [InlineKeyboardButton(text=f"{lexicon_kb[lang]['end_time']}: {end_time}", callback_data='editreg_hourly_end_time')],
                                                        [InlineKeyboardButton(text=f"{lexicon_kb[lang]['cancel']}", callback_data="regular"),
                                                         InlineKeyboardButton(text = f"{lexicon_kb[lang]['create']}", callback_data='new_hourly_right')]])


async def new_hourly_do_not_change(lang):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text=lexicon_kb[lang]["cancel"],callback_data="regular"),
                                                   InlineKeyboardButton(text = lexicon_kb[lang]["dont_change"], callback_data='reg_hourly_do_not_change')]])


#!                      YEARLY




async def new_yearly_check(lang, name: str, date: str):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text = f"{lexicon_kb[lang]['title']}: {name}", callback_data='editreg_yearly_name')],
                                                        [InlineKeyboardButton(text=f"{lexicon_kb[lang]['date']}: {date}", callback_data='editreg_yearly_date')],
                                                        [InlineKeyboardButton(text=f"{lexicon_kb[lang]['cancel']}", callback_data="regular"),
                                                         InlineKeyboardButton(text = f"{lexicon_kb[lang]['create']}", callback_data='new_yearly_create')]])


async def new_yearly_do_not_change(lang):
    return InlineKeyboardMarkup(inline_keyboard= [[InlineKeyboardButton(text=lexicon_kb[lang]["cancel"],callback_data="regular"),
                                                   InlineKeyboardButton(text = lexicon_kb[lang]["dont_change"], callback_data='reg_yearly_do_not_change')]])
