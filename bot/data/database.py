import sqlite3 as sq

with sq.connect('bot/data/bot_database.db') as db:
    cur = db.cursor()


async def create_tables():
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS user (
        id integer PRIMARY KEY AUTOINCREMENT,
        tg_id integer UNIQUE
    );
    CREATE INDEX IF NOT EXISTS idx_tg_id ON user (tg_id);
    CREATE TABLE IF NOT EXISTS product (
        id integer PRIMARY KEY AUTOINCREMENT,
        title varchar(255) NOT NULL,
        url varchar UNIQUE,
        last_price real NOT NULL,
        with_card_price real NULL
    );
    CREATE TABLE IF NOT EXISTS user_product (
        user_id integer REFERENCES user(id),
        product_id integer REFERENCES product(id),
        CONSTRAINT user_prod_pk PRIMARY KEY (user_id, product_id)
    );
    """)
    db.commit()


async def add_user(tg_id):
    cur.execute("INSERT OR IGNORE INTO user (tg_id) VALUES (?)", (tg_id,))
    db.commit()
    return cur.lastrowid


async def get_user(tg_id):
    return cur.execute("SELECT * FROM user WHERE tg_id = ?", (tg_id,)).fetchone()


async def delete_user(tg_id):
    cur.execute("DELETE FROM user WHERE tg_id = ?", (tg_id,))
    db.commit()


async def get_product_users(product_id):
    cur.execute("""SELECT * FROM user 
    INNER JOIN user_product ON user.id = user_product.user_id 
    WHERE user_product.product_id = ?""", (product_id,))
    return cur.fetchall()


async def get_product(url):
    return cur.execute("SELECT * FROM product WHERE url = ?", (url,)).fetchone()


async def create_product(*, title: str, url: str, price: float, price_with_card: float):
    cur.execute(
        "INSERT INTO product(title, url, last_price, with_card_price) VALUES (?, ?, ?, ?)",
        (title, url, price, price_with_card)
    )
    db.commit()
    return cur.lastrowid


async def add_to_wishlist(user_id, product_id):
    cur.execute("INSERT INTO user_product (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
    db.commit()


async def get_user_wishlist(tg_id):
    user = cur.execute("SELECT id FROM user WHERE tg_id = ?", (tg_id,)).fetchone()
    cur.execute("""SELECT product.* FROM product 
    INNER JOIN user_product ON product.id = user_product.product_id
    WHERE user_product.user_id = ?""", (user[0],))
    return cur.fetchall()


async def remove_from_wishlist(product_id):
    cur.execute("DELETE FROM user_product WHERE product_id = ?", (product_id,))
    await delete_unused_products()
    db.commit()


async def delete_unused_products():
    cur.execute("DELETE FROM product WHERE id NOT IN (SELECT product_id FROM user_product)")
    db.commit()


async def get_all_products():
    return cur.execute("SELECT * FROM product ORDER BY url").fetchall()


async def update_card_price(product_id, new_price):
    cur.execute("UPDATE product SET with_card_price = ? WHERE id = ?", (new_price, product_id))
    db.commit()


async def update_price(product_id, new_price):
    cur.execute("UPDATE product SET last_price = ? WHERE id = ?", (new_price, product_id))
    db.commit()
