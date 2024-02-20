import json
import sqlite3
from asyncio import sleep
from typing import Match

from aiogram import F, Router, types
from aiogram.utils.formatting import Bold, as_numbered_section
from aiogram.utils.markdown import hbold, hide_link, hlink, hstrikethrough

from bot.data import database as db
from bot.filters import UrlFilter
from bot.keyboards import get_add_to_wishlist_ikb
from bot.utils.func import get_category_products, is_datafile_updated
from parsers.atb_parser import config
from parsers.atb_parser import parser as atb_parser

router = Router()


@router.message(F.text.lower().in_({'atb', 'атб'}))
async def select_atb(message: types.Message):
    if is_datafile_updated(config.DATA_FILE):
        await message.reply('ОК! Шукаю акційні товари, зачекайте...', reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.reply('Оновлюю інформацію, зачекайте...', reply_markup=types.ReplyKeyboardRemove())
        await atb_parser.collect_cat_info()
    with open(config.DATA_FILE) as file:
        data = json.load(file)
    categories = [f'{category["name"][:35]} - {category["quantity"]}' for category in data]
    content = as_numbered_section(Bold('Категорії:'), *categories, fmt='[{}] ')
    await message.answer(content.as_html())


@router.message(F.text.regexp(r'^\d{,3}$').as_('index'))
async def category_products(message: types.Message, index: Match[str]):
    with open(config.DATA_FILE) as file:
        data = json.load(file)
    try:
        category = data[int(index.string)-1]
        await message.answer(f"Ви вибрали {hbold(category['name'])}.")
        products = get_category_products(data, int(index.string) - 1)
        for prod_idx, product in enumerate(products):
            card = f"{hide_link(product['img'])}" \
                   f"<b>{hlink(product['title'], product['link'])}</b>\n" \
                   f"Ціна: {hstrikethrough(product['old_price'], 'грн.')} {hbold(product['new_price'], 'грн.')}\n" \
                   f"Знижка: -{product['discount_percent']}%🔥\n"
            with_card_price = product.get('with_card')
            if with_card_price:
                card += f"З картою АТБ 💳: {hbold(with_card_price, 'грн.')}"
            await message.answer(card, reply_markup=get_add_to_wishlist_ikb(product['link']))
            await sleep(1.2)
    except IndexError:
        msg = '''
Нажаль категорії під цим номером не існує.😢
Уважно перевірте номер категорії.
Щоб викликати список категорій надішліть "АТБ".
'''
        await message.answer(msg)


@router.message(UrlFilter(store_url='www.atbmarket'))
async def add_to_wishlist(message: types.Message):
    url = message.text
    product_data = db.get_product(url)
    if not product_data:
        product = await atb_parser.collect_fav_products_info(url=url)
        product_id = db.create_product(title=product.title,
                                             url=product.url,
                                             price=product.price,
                                             price_with_card=product.price_with_card)
    else:
        product_id = product_data[0]
    user = db.get_user(message.from_user.id)
    try:
        db.add_to_wishlist(user[0], product_id)
    except sqlite3.IntegrityError:
        await message.reply('Ви вже слідкуєте за цим товаром.')
    else:
        await message.reply('Товар успішно додано до Обраних. /wishlist')
