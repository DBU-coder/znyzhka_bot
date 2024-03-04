from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.handlers.messages import Messages
from bot.keyboards.inline import get_category_buttons
from bot.keyboards.pagination import NavigationCallback, Paginator
from database import Category, Database

router = Router(name=__name__)
pagination = Paginator(buttons_on_page=10)


@router.message(F.text == "ATB")
async def cmd_atb(message: Message, db: Database):
    categories = await db.category.get_many(order_by=Category.title.asc())
    await pagination.add_buttons(buttons=get_category_buttons(categories))
    await message.answer(Messages.category_menu(pagination), reply_markup=await pagination.update_kb())


@router.callback_query(NavigationCallback.filter(F.direction == "next"))
async def next_(query: CallbackQuery) -> None:
    await pagination.on_next()
    await query.message.edit_text(Messages.category_menu(pagination), reply_markup=await pagination.update_kb())  # type: ignore


@router.callback_query(NavigationCallback.filter(F.direction == "previous"))
async def prev_(query: CallbackQuery) -> None:
    await pagination.on_prev()
    await query.message.edit_text(Messages.category_menu(pagination), reply_markup=await pagination.update_kb())  # type: ignore


@router.callback_query(NavigationCallback.filter(F.direction == "first"))
async def first_(query: CallbackQuery) -> None:
    await pagination.on_first()
    await query.message.edit_text(Messages.category_menu(pagination), reply_markup=await pagination.update_kb())  # type: ignore


@router.callback_query(F.data.startswith("category_"))
async def category_(query: CallbackQuery, db: Database) -> None:
    category_id = int(query.data.split("_")[1])  # type: ignore
    category = await db.category.get(ident=category_id)
    await query.message.answer(text=f"{category.products}")  # type: ignore
