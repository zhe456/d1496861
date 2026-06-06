from flask import Flask, jsonify, request
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "restaurant.db")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

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

    cursor.execute("SELECT COUNT(*) FROM restaurants")
    count = cursor.fetchone()[0]

    if count == 0:
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

    conn.commit()
    conn.close()


def get_restaurants(category=None, min_rating=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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


@app.route("/")
def home():
    return """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>餐厅评价资料分析平台</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="header">
            <h1>餐厅评价资料分析平台</h1>
            <p>Restaurant Review Data Analysis Platform</p>
        </div>

        <div class="container">
            <div class="card">
                <h2>系统简介</h2>
                <p>
                    本系统用于收集、查询和分析餐厅评价资料。
                    使用者可以查看餐厅清单、依照餐厅类型筛选、
                    依照评分查询，并透过 API 取得 JSON 格式资料。
                </p>
            </div>

            <div class="menu">
                <a href="/restaurants">查看全部餐厅</a>
                <a href="/restaurants?category=火锅">查询火锅餐厅</a>
                <a href="/restaurants?min_rating=4.3">评分 4.3 以上</a>
                <a href="/api/restaurants">查看 JSON API</a>
                <a href="/analysis">查看资料分析</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/restaurants")
def restaurants():
    category = request.args.get("category")
    min_rating = request.args.get("min_rating")

    rows = get_restaurants(category, min_rating)

    title = "餐厅清单"
    if category:
        title = f"{category} 餐厅查询结果"
    if min_rating:
        title = f"评分 {min_rating} 以上餐厅"

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="header">
            <h1>{title}</h1>
            <p>依照评分由高到低排序</p>
        </div>

        <div class="container">
            <ul class="restaurant-list">
    """

    for r in rows:
        html += f"""
            <li>
                <h3>{r['name']} <span class="tag">{r['category']}</span></h3>
                <p>地区：{r['area']}</p>
                <p>评分：{r['rating']} 分</p>
                <p>价格：{r['price_level']}</p>
                <p>地址：{r['address']}</p>
            </li>
        """

    html += """
            </ul>
            <a class="back-btn" href="/">回首页</a>
        </div>
    </body>
    </html>
    """

    return html


@app.route("/api/restaurants")
def api_restaurants():
    category = request.args.get("category")
    min_rating = request.args.get("min_rating")

    rows = get_restaurants(category, min_rating)

    data = []
    for r in rows:
        data.append({
            "id": r["id"],
            "name": r["name"],
            "area": r["area"],
            "category": r["category"],
            "rating": r["rating"],
            "price_level": r["price_level"],
            "address": r["address"]
        })

    return jsonify(data)


@app.route("/analysis")
def analysis():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM restaurants")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(rating) FROM restaurants")
    avg_rating = cursor.fetchone()[0]

    cursor.execute("SELECT name, rating FROM restaurants ORDER BY rating DESC LIMIT 1")
    top_restaurant = cursor.fetchone()

    cursor.execute("""
    SELECT category, COUNT(*) 
    FROM restaurants 
    GROUP BY category
    """)
    category_counts = cursor.fetchall()

    conn.close()

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>餐厅资料分析</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="header">
            <h1>餐厅资料分析</h1>
            <p>Restaurant Data Analysis</p>
        </div>

        <div class="container">
            <div class="analysis-box">
                <div class="analysis-item">
                    <h2>{total}</h2>
                    <p>餐厅总数量</p>
                </div>

                <div class="analysis-item">
                    <h2>{avg_rating:.2f}</h2>
                    <p>平均评分</p>
                </div>

                <div class="analysis-item">
                    <h2>{top_restaurant[1]}</h2>
                    <p>最高评分：{top_restaurant[0]}</p>
                </div>
            </div>

            <div class="card">
                <h2>各类型餐厅数量</h2>
                <ul>
    """

    for category, count in category_counts:
        html += f"<li>{category}：{count} 间</li>"

    html += """
                </ul>
            </div>

            <a class="back-btn" href="/">回首页</a>
        </div>
    </body>
    </html>
    """

    return html


if __name__ == "__main__":
    init_db()
    app.run(debug=True)