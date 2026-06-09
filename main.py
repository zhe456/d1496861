from flask import Flask, jsonify, request, redirect, session
import sqlite3
import os

app = Flask(__name__)

# session 需要 secret_key
app.secret_key = "restaurant_platform_secret_key"

DB_PATH = os.path.join(os.path.dirname(__file__), "database", "restaurant.db")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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


def is_login():
    return session.get("login") == True


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
    # 没登入：首页只显示两种登入方式
    if not is_login():
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
                    <h2>管理员登入</h2>
                    <p>
                        本系统为餐厅评价资料分析平台。
                        系统提供两种登入方式：手动帐号密码登入，以及 AI 人脸辨识登入 Demo。
                    </p>
                    <p>
                        登入后可以使用餐厅资料管理、查询、JSON API、资料分析、新增餐厅和删除餐厅等功能。
                    </p>
                    <p class="warning-text">目前尚未登入，请选择一种登入方式。</p>
                </div>

                <div class="menu">
                    <a href="/login">手动登入</a>
                    <a href="/face-login">人脸辨识登入</a>
                </div>
            </div>
        </body>
        </html>
        """

    # 已登入：才显示完整功能
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
                    管理员可以查看餐厅清单、新增餐厅资料、删除错误资料、
                    查看 JSON API，并进行餐厅资料分析。
                </p>
                <p class="success-text">目前已登入管理员模式，可以使用完整功能。</p>
            </div>

            <div class="menu">
                <a href="/restaurants">查看全部餐厅</a>
                <a href="/restaurants?category=火锅">查询火锅餐厅</a>
                <a href="/restaurants?min_rating=4.3">评分 4.3 以上</a>
                <a href="/api/restaurants">查看 JSON API</a>
                <a href="/analysis">查看资料分析</a>
                <a href="/add">新增餐厅资料</a>
                <a href="/logout">登出系统</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["login"] = True
            session["login_method"] = "手动帐号密码登入"
            return redirect("/")
        else:
            error = "帐号或密码错误，请重新输入。"

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>手动登入</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="header">
            <h1>手动登入</h1>
            <p>Manual Login</p>
        </div>

        <div class="container">
            <div class="card">
                <form method="POST">
                    <p>管理员帐号：</p>
                    <input type="text" name="username" placeholder="admin" required>

                    <p>管理员密码：</p>
                    <input type="password" name="password" placeholder="1234" required>

                    <br><br>
                    <button type="submit">登入</button>
                </form>

                <p class="warning-text">{error}</p>

                <p>测试帐号：admin</p>
                <p>测试密码：1234</p>
            </div>

            <a class="back-btn" href="/">回首页</a>
        </div>
    </body>
    </html>
    """


@app.route("/face-login", methods=["GET", "POST"])
def face_login():
    result = ""

    if request.method == "POST":
        face_image = request.files.get("face_image")

        if face_image is None or face_image.filename == "":
            result = "请上传一张图片。"
        else:
            filename = face_image.filename.lower()
            allowed_ext = [".jpg", ".jpeg", ".png", ".webp"]

            if not any(filename.endswith(ext) for ext in allowed_ext):
                result = "上传失败：图片格式只支援 jpg、jpeg、png、webp。"
            else:
                save_path = os.path.join(UPLOAD_FOLDER, face_image.filename)
                face_image.save(save_path)

                file_size = os.path.getsize(save_path)

                if file_size > 0:
                    session["login"] = True
                    session["login_method"] = "AI 人脸辨识登入 Demo"
                    return redirect("/face-result")
                else:
                    result = "影像分析失败：档案内容为空。"

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>人脸辨识登入</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="header">
            <h1>人脸辨识登入</h1>
            <p>AI Face Login Demo</p>
        </div>

        <div class="container">
            <div class="card">
                <h2>AI Vision 登入说明</h2>
                <p>
                    此功能为 AI Vision Demo，主要展示影像上传、影像分析与身份验证流程。
                    上传管理员照片后，系统会检查图片格式与档案内容，并模拟完成管理员身份验证。
                </p>

                <form method="POST" enctype="multipart/form-data">
                    <p>上传管理员人脸图片：</p>
                    <input type="file" name="face_image" accept="image/*" required>

                    <br><br>
                    <button type="submit">开始人脸辨识登入</button>
                </form>

                <p class="warning-text">{result}</p>
            </div>

            <a class="back-btn" href="/">回首页</a>
        </div>
    </body>
    </html>
    """


@app.route("/face-result")
def face_result():
    return """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>人脸辨识结果</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="header">
            <h1>人脸辨识结果</h1>
            <p>AI Vision Analysis Result</p>
        </div>

        <div class="container">
            <div class="card">
                <h2>辨识成功</h2>
                <p>系统已接收上传影像，并完成基础影像分析。</p>
                <p>分析流程包含：图片上传、格式检查、档案内容检查、管理员身份验证 Demo。</p>
                <p class="success-text">目前已进入管理员模式，可以新增与删除餐厅资料。</p>
            </div>

            <div class="menu">
                <a href="/">进入系统首页</a>
                <a href="/add">新增餐厅资料</a>
                <a href="/restaurants">查看餐厅清单</a>
                <a href="/analysis">查看资料分析</a>
                <a href="/logout">登出系统</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/restaurants")
def restaurants():
    if not is_login():
        return redirect("/login-required")

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

    if len(rows) == 0:
        html += """
            <li>
                <h3>没有符合条件的餐厅资料</h3>
                <p>可以回首页新增餐厅资料，或重新选择查询条件。</p>
            </li>
        """

    for r in rows:
        html += f"""
            <li>
                <h3>{r['name']} <span class="tag">{r['category']}</span></h3>
                <p>地区：{r['area']}</p>
                <p>评分：{r['rating']} 分</p>
                <p>价格：{r['price_level']}</p>
                <p>地址：{r['address']}</p>

                <a class="delete-btn"
                   href="/delete/{r['id']}"
                   onclick="return confirm('确定要删除这间餐厅吗？')">
                   删除
                </a>
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


@app.route("/add", methods=["GET", "POST"])
def add_restaurant():
    if not is_login():
        return redirect("/login-required")

    if request.method == "POST":
        name = request.form.get("name")
        area = request.form.get("area")
        category = request.form.get("category")
        rating = request.form.get("rating")
        price_level = request.form.get("price_level")
        address = request.form.get("address")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO restaurants
        (name, area, category, rating, price_level, address)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (name, area, category, float(rating), price_level, address))

        conn.commit()
        conn.close()

        return redirect("/restaurants")

    return """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>新增餐厅资料</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="header">
            <h1>新增餐厅资料</h1>
            <p>Add New Restaurant</p>
        </div>

        <div class="container">
            <div class="card">
                <form method="POST">
                    <p>餐厅名称：</p>
                    <input type="text" name="name" placeholder="例如：逢甲炒饭店" required>

                    <p>地区：</p>
                    <input type="text" name="area" placeholder="例如：台中" required>

                    <p>餐厅类型：</p>
                    <input type="text" name="category" placeholder="例如：中式料理" required>

                    <p>评分：</p>
                    <input type="number" step="0.1" min="0" max="5" name="rating" placeholder="例如：4.5" required>

                    <p>价格区间：</p>
                    <select name="price_level" required>
                        <option value="$">$</option>
                        <option value="$$">$$</option>
                        <option value="$$$">$$$</option>
                    </select>

                    <p>地址：</p>
                    <input type="text" name="address" placeholder="例如：台中市西屯区" required>

                    <br><br>
                    <button type="submit">新增餐厅</button>
                </form>
            </div>

            <a class="back-btn" href="/">回首页</a>
        </div>
    </body>
    </html>
    """


@app.route("/delete/<int:restaurant_id>")
def delete_restaurant(restaurant_id):
    if not is_login():
        return redirect("/login-required")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM restaurants WHERE id = ?", (restaurant_id,))

    conn.commit()
    conn.close()

    return redirect("/restaurants")


@app.route("/login-required")
def login_required():
    return """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>需要登入</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="header">
            <h1>需要管理员登入</h1>
            <p>Login Required</p>
        </div>

        <div class="container">
            <div class="card">
                <h2>权限不足</h2>
                <p>系统功能需要先登入管理员模式。</p>
                <p class="warning-text">请先选择手动登入或人脸辨识登入。</p>
            </div>

            <div class="menu">
                <a href="/login">手动登入</a>
                <a href="/face-login">人脸辨识登入</a>
                <a href="/">回首页</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/api/restaurants")
def api_restaurants():
    if not is_login():
        return redirect("/login-required")

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
    if not is_login():
        return redirect("/login-required")

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

    if avg_rating is None:
        avg_rating = 0

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
    """

    if top_restaurant:
        html += f"""
                <div class="analysis-item">
                    <h2>{top_restaurant[1]}</h2>
                    <p>最高评分：{top_restaurant[0]}</p>
                </div>
        """
    else:
        html += """
                <div class="analysis-item">
                    <h2>无</h2>
                    <p>目前没有餐厅资料</p>
                </div>
        """

    html += """
            </div>

            <div class="card">
                <h2>各类型餐厅数量</h2>
                <ul>
    """

    if len(category_counts) == 0:
        html += "<li>目前没有资料</li>"

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