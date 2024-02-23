import asyncio
import os
from datetime import datetime

from aiogram.utils.markdown import hbold, hlink, hstrikethrough

import bot.data.database as db
from parser.atbparser import ATBFavoriteProductParser


def is_datafile_updated(filename):
    """
    Returns True if file exists and updated.
    :param str filename: Path to datafile.
    :return: bool
    """
    if not os.path.exists(filename):
        return False
    mod_time_stamp = os.path.getmtime(filename)
    mod_date = datetime.fromtimestamp(mod_time_stamp).date()
    if mod_date != datetime.today().date():
        return False
    return True


def get_category_products(data, cat_index):
    """
    Creates a sorted category products generator.
    :param list data: List of categories data.
    :param int cat_index: Index of category list element.
    :return:
    """
    category = data[cat_index]
    category['products'].sort(key=lambda x: x['discount_percent'], reverse=True)
    for product in category['products']:
        yield product


def get_slug(link: str) -> str:
    slug = link.split('/')[-1]
    return slug


async def notify_price_change(bot, product, new_price):
    users = db.get_product_users(product.id)
    message = (f'‼️Ціна на товар: <b>{hlink(product.title, product.url)}</b> змінилась‼️\n'
               f'Стара: {hstrikethrough(product.last_price, "грн.")} Нова: {hbold(new_price, "грн.")}')
    await send_notifications(bot, users, message)


async def notify_card_price_change(bot, product, new_price_with_card):
    users = db.get_product_users(product.id)
    message = (f'‼️Ціна на товар: <b>{hlink(product.title, product.url)}</b> при оплаті картою АТБ змінилась‼️\n'
               f'Стара💳: {hstrikethrough(product.price_with_card, "грн.")} Нова💳: {hbold(new_price_with_card, "грн.")}')
    await send_notifications(bot, users, message)


async def send_notifications(bot, users, message):
    for user in users:
        await bot.send_message(chat_id=user.tg_id, text=message)


async def check_price(bot):
    while True:
        db.delete_unused_products()
        old_products = db.get_all_products()
        parser = ATBFavoriteProductParser(urls=[product.url for product in old_products])
        new_products = await parser.get_data_from_all_urls()
        new_products.sort(key=lambda x: x.url)
        for old_product, new_product in zip(old_products, new_products):
            if old_product.last_price != new_product.price:
                await notify_price_change(bot, old_product, new_product.price)
                db.update_price(product_id=old_product.id, column_name='last_price', new_price=new_product.price)
            if old_product.price_with_card != new_product.price_with_card:
                await notify_card_price_change(bot, old_product, new_product.price_with_card)
                db.update_price(product_id=old_product.id, column_name='price_with_card',
                                new_price=new_product.price_with_card)
        await asyncio.sleep(20)
