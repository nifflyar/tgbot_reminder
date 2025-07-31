import datetime
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from scheduler.scheduler_utils import select_timezone_tg_id
import src.keyboards.main_keyboard as mainkb
import src.keyboards.new_remind_keyboard as newkb
from src.keyboards.keyboard_func import merge_keyboards, back_to_main, back_button

from src.db.queries.orm import select_timezone, select_user, insert_users, update_user
from src.lexicon.lexicon_handlers import lexicon_hdl

from src.handlers.new_reminders.onetime_type import router as onetime_router
from src.handlers.new_reminders.daily_type import router as daily_router
from src.handlers.new_reminders.hourly_type import router as hourly_router
from src.handlers.new_reminders.yearly_type import router as yearly_router
from src.handlers.my_reminder import router as my_reminder_rounter
from src.handlers.new_reminders.calendar_type import router as calendar_router


router = Router()
router.include_routers(
    onetime_router,
    daily_router,
    my_reminder_rounter,
    hourly_router,
    calendar_router,
    yearly_router,
)


def settings_text(
    lang: str, timezone: int, hourformat: int, created_at: datetime.datetime) -> str:

    clean_created_at = created_at.replace(microsecond=0, second=0).strftime("%Y-%m-%d")

    text = (
        f"\t*┏━━◥◣    {lexicon_hdl[lang]['settings']}     ◢◤━━┓*\n\n"
        f"   {lexicon_hdl[lang]['settings_language']} - _{lexicon_hdl['languages'][lang]}_\n"
        f"   {lexicon_hdl[lang]['settings_timezone']} - _UTC+{timezone}_\n"
        f"   {lexicon_hdl[lang]['settings_hourformat']} - {hourformat}\n\n\n"
        f"  {lexicon_hdl[lang]['settings_created_at']} - *{clean_created_at}*\n"
    )

    return text


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if await select_user(message.from_user.id):
        user = await select_user(message.from_user.id)
        await message.answer(
            text=lexicon_hdl[user.language]["main_menu"],
            reply_markup=await mainkb.main_kb(user.language),
        )
        if state:
            await state.clear()
    else:
        await message.answer(
            "Выбери язык / Choose a language",
            reply_markup=await mainkb.language_choice(),
        )


@router.callback_query(F.data == "en")
@router.callback_query(F.data == "ru")
async def timezone(callback: CallbackQuery):
    lang = callback.data
    await callback.message.edit_text(
        text=lexicon_hdl[lang]["timezone"],
        reply_markup=await mainkb.timezone_keyboard(lang),
    )


@router.callback_query(F.data.startswith("utc"))
async def tz_confirm(callback: CallbackQuery):
    _, lang, tz = callback.data.split("_")  # utc_{lang}_{i+1}
    await insert_users(tg_id=callback.from_user.id, language=lang, timezone=tz)
    user = await select_user(callback.from_user.id)
    await callback.message.edit_text(
        text=lexicon_hdl[user.language]["main_menu"],
        reply_markup=await mainkb.main_kb(user.language),
    )


@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery):
    user = await select_user(callback.from_user.id)
    await callback.message.edit_text(
        text=settings_text(
            lang=user.language,
            timezone=user.timezone,
            hourformat=user.hour_format,
            created_at=user.created_at,
        ),
        reply_markup=await merge_keyboards(
            (await mainkb.settings_menu(user.language)),
            (await back_to_main(user.language)),
        ),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "more")
async def more(callback: CallbackQuery):
    user = await select_user(callback.from_user.id)
    await callback.message.edit_text(
        text=lexicon_hdl[user.language]["more"],
        reply_markup=await merge_keyboards(
            (await mainkb.more_menu(user.language)), (await back_to_main(user.language))
        ),
    )


@router.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery, state: FSMContext):
    user = await select_user(callback.from_user.id)
    await callback.message.edit_text(
        text=lexicon_hdl[user.language]["main_menu"],
        reply_markup=await mainkb.main_kb(user.language),
    )
    if state:
        await state.clear()


@router.callback_query(F.data == "change_timezone")
async def tz_change(callback: CallbackQuery):
    user = await select_user(callback.from_user.id)
    tz_user = int(await select_timezone(user_id=user.id))

    if user.timezone_updated_at is None:
        await callback.message.edit_text(
            text=lexicon_hdl[user.language]["change_timezone"],
            reply_markup=await merge_keyboards(
                await mainkb.change_timezone_keyboard(tz_user),
                await back_button(user.language, "settings"),
            ),
        )

    elif datetime.datetime.utcnow() - user.timezone_updated_at > datetime.timedelta(
        hours=12
    ):
        await callback.message.edit_text(
            text=lexicon_hdl[user.language]["change_timezone"],
            reply_markup=await merge_keyboards(
                await mainkb.change_timezone_keyboard(tz_user),
                await back_button(user.language, "settings"),
            ),
        )

    else:
        await callback.answer(
            text=lexicon_hdl[user.language]["timezone_alert"], show_alert=True
        )


@router.callback_query(F.data.startswith("change_utc_"))
async def tz_confirm(callback: CallbackQuery):
    tz = callback.data.split("_")[2]
    await update_user(
        tg_id=callback.from_user.id,
        new_timezone=tz,
        new_timezone_updated_at=datetime.datetime.utcnow(),
    )
    user = await select_user(callback.from_user.id)
    await callback.message.edit_text(
        text=settings_text(
            lang=user.language,
            timezone=user.timezone,
            hourformat=user.hour_format,
            created_at=user.created_at,
        ),
        reply_markup=await merge_keyboards(
            (await mainkb.settings_menu(user.language)),
            (await back_to_main(user.language)),
        ),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "change_lang")
async def change_lang(callback: CallbackQuery):
    user = await select_user(callback.from_user.id)
    await callback.message.edit_text(
        text=lexicon_hdl[user.language]["choose_language"],
        reply_markup=await merge_keyboards(
            await mainkb.change_language_choice(user.language),
            await back_button(user.language, "settings"),
        ),
    )


@router.callback_query(F.data.startswith("lang_chose_"))
async def changed_lang(callback: CallbackQuery):
    lang = callback.data.split("_")[2]

    await update_user(tg_id=callback.from_user.id, new_language=lang)
    user = await select_user(callback.from_user.id)
    await callback.message.edit_text(
        text=settings_text(
            lang=user.language,
            timezone=user.timezone,
            hourformat=user.hour_format,
            created_at=user.created_at,
        ),
        reply_markup=await merge_keyboards(
            (await mainkb.settings_menu(user.language)),
            (await back_to_main(user.language)),
        ),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "donate")
async def show_popup(callback: CallbackQuery):
    await callback.answer(text="coming soon!", show_alert=True)


@router.callback_query(F.data == "notifications")
async def show_popup(callback: CallbackQuery):
    await callback.answer(text="coming soon!", show_alert=True)


@router.callback_query(F.data == "hour_format")
async def show_popup(callback: CallbackQuery):
    await callback.answer(text="coming soon!", show_alert=True)


@router.callback_query(F.data == "new")
async def new_repeat_type(callback: CallbackQuery, state: FSMContext):

    if await state.get_state():
        await state.clear()

    user = await select_user(callback.from_user.id)
    await callback.message.edit_text(
        text=lexicon_hdl[user.language]["new_reminder_type_menu"],
        reply_markup=await newkb.new_remind_type(user.language),
    )


@router.callback_query(F.data == "regular")
async def type_of_regular(callback: CallbackQuery, state: FSMContext):

    if await state.get_state():
        await state.clear()

    await state.update_data(first_mes_id=callback.message.message_id)

    user = await select_user(callback.from_user.id)
    await callback.message.edit_text(
        text=lexicon_hdl[user.language]["ask_daily_type"],
        parse_mode="Markdown",
        reply_markup=await merge_keyboards(
            await newkb.new_regular_type(user.language),
            await back_button(user.language, "new"),
        ),
    )
