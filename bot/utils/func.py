import asyncio
import os
from datetime import datetime

from aiogram.utils.markdown import hbold, hlink, hstrikethrough

import bot.data.database as db
from parsers.atb_parser.parser import collect_price


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


async def notify_price_change(bot, old_data, new_price):
    users = await db.get_product_users(old_data[0])
    message = (f'‼️Ціна на товар: <b>{hlink(old_data[1], old_data[2])}</b> змінилась‼️\n'
               f'Стара: {hstrikethrough(old_data[3], "грн.")} Нова: {hbold(new_price, "грн.")}')
    await send_notifications(bot, users, message)


async def notify_card_price_change(bot, old_data, new_price_with_card):
    users = await db.get_product_users(old_data[0])
    message = (f'‼️Ціна на товар: <b>{hlink(old_data[1], old_data[2])}</b> при оплаті картою АТБ змінилась‼️\n'
               f'Стара💳: {hstrikethrough(old_data[4], "грн.")} Нова💳: {hbold(new_price_with_card, "грн.")}')
    await send_notifications(bot, users, message)


async def send_notifications(bot, users, message):
    for user in users:
        await bot.send_message(chat_id=user[1], text=message)


async def check_price(bot):
    while True:
        old_products_data = await db.get_all_products()
        links = [product[2] for product in old_products_data]
        new_products_data = await collect_price(links)
        new_products_data.sort(key=lambda x: x.url)

        for old_data, new_data in zip(old_products_data, new_products_data):
            old_price_with_card = old_data[4]
            if old_data[3] != new_data.price:
                await notify_price_change(bot, old_data, new_data.price)
                await db.update_price(product_id=old_data[0], new_price=new_data.price)
            if old_price_with_card != new_data.price_with_card:
                await notify_card_price_change(bot, old_data, new_data.price_with_card)
                await db.update_card_price(product_id=old_data[0], new_price=new_data.price_with_card)
        await asyncio.sleep(3600)
