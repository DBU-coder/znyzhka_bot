from aiogram import Router, types
from aiogram.filters import Command, CommandStart

from bot.handlers.messages import Messages
from bot.keyboards.reply import select_store_kb
from database import Database

router = Router(name=__name__)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    first_name = message.from_user.first_name  # type: ignore
    await message.answer(Messages.greeting(first_name), reply_markup=select_store_kb())


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(Messages.ABOUT_BOT)


@router.message(Command("watchlist"))
async def cmd_watchlist(message: types.Message, db: Database):
    user = await db.user.get(ident=message.from_user.id)  # type: ignore
    liked_products = await user.awaitable_attrs.liked_products  # type: ignore
    await message.answer(Messages.get_watchlist(liked_products), disable_web_page_preview=True)
