



from aiogram.types import MessageEntity
from aiogram.enums import MessageEntityType

# @router.message(Command("emoji"))
# async def send_premium_emoji(message: Message):
#     emoji_id = "5389102131527556772"  # замените на настоящий custom_emoji_id

#     await message.answer(
#         text='🚀',  # Этот символ не будет показан, просто заглушка
#         entities=[
#             MessageEntity(
#                 type=MessageEntityType.CUSTOM_EMOJI,
#                 offset=0,
#                 length=2,
#                 custom_emoji_id=emoji_id
#             )
#         ]
#     )

entities=[
        MessageEntity(
            type="custom_emoji",
            offset=0,
            length=4,
            custom_emoji_id="5305280351482962172"
        )
    ]