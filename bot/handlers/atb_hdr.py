import asyncio

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from bot.handlers.messages import Messages
from bot.keyboards.inline import (
    WatchlistCallback,
    add_to_watchlist_ikb,
    get_category_buttons,
)
from bot.keyboards.pagination import NavigationCallback, Paginator
from database import Category, Database

router = Router(name=__name__)
pagination = Paginator(buttons_on_page=10)


@router.message(F.text == "ATB")
async def cmd_atb(message: Message, db: Database):
    categories = await db.category.get_many(order_by=Category.title.asc())
    pagination.buttons = get_category_buttons(categories)
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
    await query.message.edit_text(  # type: ignore
        text=Messages.category_menu(pagination), reply_markup=await pagination.update_kb()
    )


@router.callback_query(F.data.startswith("category_"))
async def category_products(query: CallbackQuery, db: Database) -> None:
    category_id = int(query.data.split("_")[1])  # type: ignore
    category = await db.category.get(ident=category_id)
    products = await category.awaitable_attrs.products  # type: ignore
    if not products:
        await query.message.answer(text=Messages.PRODUCTS_NOT_FOUND)  # type: ignore
        return
    for product in sorted(products, key=lambda x: x.discount_percent, reverse=True):
        await query.message.answer(text=Messages.product_card(product), reply_markup=add_to_watchlist_ikb(product.id))  # type: ignore
        await asyncio.sleep(1)


@router.callback_query(WatchlistCallback.filter(F.action == "add"))
async def add_to_watchlist(query: CallbackQuery, callback_data: WatchlistCallback, db: Database) -> None:
    product = await db.product.get(ident=callback_data.product_id)
    user = await db.user.get(ident=query.from_user.id)
    trackable_products = await user.awaitable_attrs.tracks_products  # type: ignore
    trackable_urls = [trackable_product.url for trackable_product in trackable_products]
    if product.url in trackable_urls:
        await query.answer(text=Messages.ALREADY_IN_WATCHLIST)
        return
    new_trackable_product = await db.trackable_product.new_from_product(product)  # type: ignore
    trackable_products.append(new_trackable_product)
    await query.answer(text=Messages.ADDED_TO_WATCHLIST)
