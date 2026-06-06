import sqlite3

DB_PATH = "database/restaurant.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

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

    cursor.execute("DELETE FROM restaurants")

    restaurants = [
        ("小火锅店", "台中", "火锅", 4.5, "$$", "台中市西屯区"),
        ("日式拉面店", "台中", "日式料理", 4.2, "$$", "台中市北区"),
        ("平价便当店", "台中", "便当", 4.0, "$", "台中市南区"),
        ("韩式炸鸡店", "台中", "韩式料理", 4.6, "$$", "台中市西区"),
        ("早午餐咖啡厅", "台中", "早午餐", 4.3, "$$", "台中市西屯区"),
    ]

    cursor.executemany("""
    INSERT INTO restaurants 
    (name, area, category, rating, price_level, address)
    VALUES (?, ?, ?, ?, ?, ?)
    """, restaurants)

    conn.commit()
    conn.close()

    print("资料库建立完成，餐厅资料已新增。")

if __name__ == "__main__":
    init_db()