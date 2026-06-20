import os
import sqlite3
import hashlib


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "restaurant.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_database():
    """
    建立期末专题需要的资料表：
    1. users：使用者帐号，密码使用 hash
    2. raw_data：爬虫抓到的原始资料
    3. clean_data：清洗后的资料
    4. restaurants：餐厅资料
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        title TEXT,
        content TEXT,
        url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clean_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        raw_id INTEGER,
        clean_title TEXT,
        clean_content TEXT,
        keyword TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (raw_id) REFERENCES raw_data(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restaurants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        area TEXT NOT NULL,
        category TEXT NOT NULL,
        rating REAL NOT NULL,
        price_level TEXT NOT NULL,
        address TEXT
    )
    """)

    conn.commit()

    create_default_users(cursor)
    create_default_restaurants(cursor)

    conn.commit()
    conn.close()


def create_default_users(cursor):
    """
    建立预设帐号。
    老师要求要有：
    帐号：yungchen
    密码：teed6Vu[b)oa
    """

    users = [
        ("admin", "1234", "admin"),
        ("yungchen", "teed6Vu[b)oa", "user"),
    ]

    for username, password, role in users:
        password_hash = hash_password(password)

        cursor.execute("""
        INSERT OR IGNORE INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
        """, (username, password_hash, role))


def create_default_restaurants(cursor):
    cursor.execute("SELECT COUNT(*) FROM restaurants")
    count = cursor.fetchone()[0]

    if count > 0:
        return

    restaurants = [
        ("小火锅店", "台中", "火锅", 4.5, "$$", "台中市西屯区"),
        ("日式拉面店", "台中", "日式料理", 4.2, "$$", "台中市北区"),
        ("平价便当店", "台中", "便当", 4.0, "$", "台中市南区"),
        ("韩式炸鸡店", "台中", "韩式料理", 4.6, "$$", "台中市西区"),
        ("早午餐咖啡厅", "台中", "早午餐", 4.3, "$$", "台中市西屯区"),
        ("烧肉店", "台中", "烧肉", 4.7, "$$$", "台中市南屯区"),
        ("义大利面店", "台中", "义式料理", 4.1, "$$", "台中市西区"),
        ("牛肉面店", "台中", "面食", 4.4, "$", "台中市北屯区"),
    ]

    cursor.executemany("""
    INSERT INTO restaurants
    (name, area, category, rating, price_level, address)
    VALUES (?, ?, ?, ?, ?, ?)
    """, restaurants)


# -------------------------
# users CRUD
# -------------------------

def create_user(username, password, role="user"):
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    cursor.execute("""
    INSERT INTO users (username, password_hash, role)
    VALUES (?, ?, ?)
    """, (username, password_hash, role))

    conn.commit()
    conn.close()


def check_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    cursor.execute("""
    SELECT * FROM users
    WHERE username = ? AND password_hash = ?
    """, (username, password_hash))

    user = cursor.fetchone()
    conn.close()

    return user is not None


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    conn.close()
    return users


# -------------------------
# raw_data CRUD
# -------------------------

def insert_raw_data(source, title, content, url):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO raw_data (source, title, content, url)
    VALUES (?, ?, ?, ?)
    """, (source, title, content, url))

    conn.commit()
    conn.close()


def get_all_raw_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM raw_data ORDER BY id DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows


# -------------------------
# clean_data CRUD
# -------------------------

def insert_clean_data(raw_id, clean_title, clean_content, keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO clean_data (raw_id, clean_title, clean_content, keyword)
    VALUES (?, ?, ?, ?)
    """, (raw_id, clean_title, clean_content, keyword))

    conn.commit()
    conn.close()


def get_all_clean_data(keyword=None):
    conn = get_connection()
    cursor = conn.cursor()

    if keyword:
        cursor.execute("""
        SELECT * FROM clean_data
        WHERE clean_title LIKE ? OR clean_content LIKE ? OR keyword LIKE ?
        ORDER BY id DESC
        """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    else:
        cursor.execute("SELECT * FROM clean_data ORDER BY id DESC")

    rows = cursor.fetchall()

    conn.close()
    return rows


def update_clean_data(clean_id, clean_title, clean_content, keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE clean_data
    SET clean_title = ?, clean_content = ?, keyword = ?
    WHERE id = ?
    """, (clean_title, clean_content, keyword, clean_id))

    conn.commit()
    conn.close()


def delete_clean_data(clean_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clean_data WHERE id = ?", (clean_id,))

    conn.commit()
    conn.close()


# -------------------------
# restaurants CRUD
# -------------------------

def get_restaurants(category=None, min_rating=None):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM restaurants WHERE 1=1"
    params = []

    if category:
        sql += " AND category = ?"
        params.append(category)

    if min_rating:
        sql += " AND rating >= ?"
        params.append(float(min_rating))

    sql += " ORDER BY rating DESC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    conn.close()
    return rows


def insert_restaurant(name, area, category, rating, price_level, address):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO restaurants
    (name, area, category, rating, price_level, address)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (name, area, category, float(rating), price_level, address))

    conn.commit()
    conn.close()


def update_restaurant(restaurant_id, name, area, category, rating, price_level, address):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE restaurants
    SET name = ?, area = ?, category = ?, rating = ?, price_level = ?, address = ?
    WHERE id = ?
    """, (name, area, category, float(rating), price_level, address, restaurant_id))

    conn.commit()
    conn.close()


def delete_restaurant(restaurant_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM restaurants WHERE id = ?", (restaurant_id,))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    print("资料库初始化完成")