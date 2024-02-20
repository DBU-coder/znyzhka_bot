from asyncio import sleep
from collections import namedtuple

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import hlink

import bot.data.database as db
from bot.keyboards import get_choice_store_kb, get_delete_from_wishlist_ikb

Product = namedtuple('Product', 'id title url price price_with_card')

router = Router(name=__name__)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    db.add_user(message.from_user.id)
    first_name = message.from_user.first_name
    msg = f'Вітаю, {first_name}! 👋\nВиберіть торгівельну мережу.'

    await message.answer(msg, reply_markup=get_choice_store_kb(input_field_placeholder='Назва мережі'))


@router.message(Command('addwish'))
async def cmd_add_wishlist(message: types.Message):
    msg = 'Надішліть посилання на товар і я буду його відслідковувати🕵️‍♀️.\nЯкщо ціна зміниться, я вам повідомлю.'
    await message.answer(msg)


@router.message(Command('wishlist'))
@router.message(F.text.lower() == 'обрані товари')
async def cmd_wishlist(message: types.Message):
    wishlist = db.get_user_wishlist(message.from_user.id)
    if wishlist:
        for product_data in wishlist:
            product = Product(*product_data)
            card = f'<b>{hlink(product.title, product.url)}</>\n<i>Ціна: {product.price:.2f} грн.</>'
            if product.price_with_card:
                card += f'\n<i>Ціна з картою АТБ: {product.price_with_card:.2f} грн.</>'
            await message.answer(card, reply_markup=get_delete_from_wishlist_ikb(product.id))
            await sleep(1)
    else:
        await message.answer('Наразі список обраних товарів порожній.\nЩоб додати товар надішліть посилання.')
