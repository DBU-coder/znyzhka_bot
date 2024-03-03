from aiogram import Router, types
from aiogram.filters import CommandStart

from bot.keyboards import select_store_kb

router = Router(name=__name__)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    first_name = message.from_user.first_name  # type: ignore
    msg = f"Вітаю, {first_name or ''}! 👋\nВиберіть торгівельну мережу."
    await message.answer(msg, reply_markup=select_store_kb(input_field_placeholder="Назва мережі"))
