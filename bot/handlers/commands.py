from aiogram import Router, types
from aiogram.filters import Command, CommandStart

from bot.handlers.messages import Message
from bot.keyboards import select_store_kb

router = Router(name=__name__)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    first_name = message.from_user.first_name  # type: ignore
    await message.answer(Message.greeting(first_name), reply_markup=select_store_kb())


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(Message.ABOUT_BOT)


@router.message(Command("watchlist"))
async def cmd_watchlist(message: types.Message):
    await message.answer("My Watchlist")
