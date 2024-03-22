from asyncio import sleep

from aiogram import Router, types
from aiogram.filters import Command, CommandStart

from src.bot.handlers.messages import Messages
from src.bot.keyboards.inline import remove_from_watchlist_ikb
from src.bot.keyboards.reply import select_store_kb
from src.database import Database

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
    trackable_products = await user.awaitable_attrs.tracks_products  # type: ignore
    if not trackable_products:
        await message.answer(Messages.EMPTY_WATCHLIST)
        return
    for product in trackable_products:
        await message.answer(
            Messages.product_card(product),
            reply_markup=remove_from_watchlist_ikb(product.id),
        )
        await sleep(1)
