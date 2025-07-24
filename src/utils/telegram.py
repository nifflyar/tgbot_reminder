

from aiogram.exceptions import TelegramBadRequest

async def safe_edit_text(bot, message, **kwargs):
    try:
        await bot.edit_message_text(**kwargs)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return 
        if "message to edit not found" in str(e).lower():
            return
        raise

async def safe_delete(message):
    try:
        await message.delete()
    except TelegramBadRequest as e:
        if "message to delete not found" in str(e).lower():
            return
        raise