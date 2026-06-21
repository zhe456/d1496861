from flask import Flask, jsonify, request, redirect, session, send_from_directory
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np

from src.database.db import (
    init_database,
    check_login,
    get_connection,
    get_restaurants,
    insert_restaurant,
    delete_restaurant,
)

app = Flask(__name__)

# session 需要 secret_key
app.secret_key = "restaurant_platform_secret_key"

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")


def is_login():
    return session.get("login") == True


def read_image(image_path):
    """
    解决 Windows 中文路径或特殊档名导致 cv2.imread 读取失败的问题。
    """
    try:
        data = np.fromfile(image_path, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return cv2.imread(image_path)


def save_image(image_path, img):
    """
    解决 Windows 中文路径或特殊档名导致 cv2.imwrite 储存失败的问题。
    """
    ext = os.path.splitext(image_path)[1]

    if ext == "":
        ext = ".png"
        image_path = image_path + ext

    success, encoded_img = cv2.imencode(ext, img)

    if success:
        encoded_img.tofile(image_path)
        return True

    return False


def detect_face(image_path):
    """
    OpenCV 人脸侦测加强版：
    1. 使用 Haar Cascade 找人脸
    2. 使用眼睛侦测验证是否像真正人脸
    3. 过滤太小或太大的错误框
    4. 只有通过验证才算登入成功
    5. 成功后会输出绿色人脸框与蓝色眼睛框
    """

    img = read_image(image_path)

    if img is None:
        return False, 0, None

    height, width = img.shape[:2]
    image_area = width * height

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 让亮度平均一点，提升侦测稳定度
    gray = cv2.equalizeHist(gray)

    face_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    eye_cascade_path = cv2.data.haarcascades + "haarcascade_eye.xml"

    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

    if face_cascade.empty() or eye_cascade.empty():
        return False, 0, None

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.08,
        minNeighbors=8,
        minSize=(80, 80),
    )

    valid_faces = []

    for (x, y, w, h) in faces:
        face_area = w * h
        face_ratio = face_area / image_area

        # 过滤明显不合理的框
        # 太小通常是误判，太大也可能不是正常人脸
        if face_ratio < 0.01 or face_ratio > 0.45:
            continue

        # 取出脸部区域
        face_gray = gray[y:y + h, x:x + w]

        eyes = eye_cascade.detectMultiScale(
            face_gray,
            scaleFactor=1.08,
            minNeighbors=6,
            minSize=(15, 15),
        )

        # 至少侦测到 1 个眼睛，才比较像真正人脸
        if len(eyes) < 1:
            continue

        valid_faces.append((x, y, w, h, eyes))

    # 只画通过验证的人脸
    for (x, y, w, h, eyes) in valid_faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)

        cv2.putText(
            img,
            "Human Face",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        face_img = img[y:y + h, x:x + w]

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(
                face_img,
                (ex, ey),
                (ex + ew, ey + eh),
                (255, 0, 0),
                2,
            )

    face_count = len(valid_faces)

    if face_count > 0:
        result_filename = "result_" + os.path.basename(image_path)
        result_path = os.path.join(UPLOAD_FOLDER, result_filename)

        save_image(result_path, img)

        return True, face_count, result_filename

    return False, 0, None


@app.route("/")
def home():
    # 未登入：首页只显示两种登入方式
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
                        系统提供两种登入方式：手动帐号密码登入，以及 OpenCV 人脸侦测登入。
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

    login_method = session.get("login_method", "管理员登入")
    username = session.get("username", "admin")

    return f"""
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
                <p><strong>登入帐号：</strong>{username}</p>
                <p><strong>登入方式：</strong>{login_method}</p>
            </div>

            <div class="menu">
                <a href="/restaurants">查看全部餐厅</a>
                <a href="/restaurants?category=火锅">查询火锅餐厅</a>
                <a href="/restaurants?min_rating=4.3">评分 4.3 以上</a>
                <a href="/api/restaurants">查看 JSON API</a>
                <a href="/api/data">查看 clean_data API</a>
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

        if check_login(username, password):
            session["login"] = True
            session["username"] = username
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

                <h3>测试帐号</h3>
                <p>帐号：admin</p>
                <p>密码：1234</p>
                <hr>
                <p>帐号：yungchen</p>
                <p>密码：teed6Vu[b)oa</p>
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
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)

                safe_name = secure_filename(face_image.filename)
                save_path = os.path.join(UPLOAD_FOLDER, safe_name)
                face_image.save(save_path)

                has_face, face_count, result_filename = detect_face(save_path)

                if has_face:
                    session["login"] = True
                    session["username"] = "face_admin"
                    session["login_method"] = "OpenCV 人脸侦测登入"
                    session["face_count"] = face_count
                    session["face_result_image"] = result_filename
                    return redirect("/face-result")
                else:
                    result = "人脸辨识失败：系统没有侦测到通过验证的人脸，请换一张清楚的正面照片。"

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
            <p>OpenCV Face Detection Login</p>
        </div>

        <div class="container">
            <div class="card">
                <h2>OpenCV 人脸侦测登入说明</h2>
                <p>
                    此功能使用 OpenCV Haar Cascade 人脸侦测。
                    系统会读取上传图片、转换为灰阶影像，并侦测图片中是否有人脸。
                </p>
                <p>
                    为了减少误判，系统会再使用眼睛侦测进行验证。
                    只有侦测到类似人脸与眼睛特征时，才会登入成功。
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
    if not is_login():
        return redirect("/login-required")

    face_count = session.get("face_count", 0)
    result_image = session.get("face_result_image", "")

    image_html = ""
    if result_image:
        image_html = f"""
        <div class="card">
            <h2>人脸框选结果图</h2>
            <img class="result-img" src="/uploads/{result_image}" alt="人脸侦测结果">
        </div>
        """

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>人脸辨识结果</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="header">
            <h1>人脸辨识结果</h1>
            <p>OpenCV Face Detection Result</p>
        </div>

        <div class="container">
            <div class="card">
                <h2>辨识成功</h2>
                <p>系统已成功读取上传图片，并使用 OpenCV Haar Cascade 完成人脸侦测。</p>
                <p>侦测到的人脸数量：{face_count}</p>
                <p>绿色框代表人脸位置，蓝色框代表眼睛位置。</p>
                <p class="success-text">目前已进入管理员模式，可以新增与删除餐厅资料。</p>
            </div>

            {image_html}

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


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


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

        insert_restaurant(
            name=name,
            area=area,
            category=category,
            rating=rating,
            price_level=price_level,
            address=address,
        )

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
def delete_restaurant_route(restaurant_id):
    if not is_login():
        return redirect("/login-required")

    delete_restaurant(restaurant_id)

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
            "address": r["address"],
        })

    return jsonify(data)


@app.route("/api/data", methods=["GET"])
def api_get_clean_data():
    if not is_login():
        return redirect("/login-required")

    keyword = request.args.get("keyword")

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

    data = []
    for r in rows:
        data.append({
            "id": r["id"],
            "raw_id": r["raw_id"],
            "clean_title": r["clean_title"],
            "clean_content": r["clean_content"],
            "keyword": r["keyword"],
            "created_at": r["created_at"],
        })

    return jsonify(data)


@app.route("/api/data", methods=["POST"])
def api_post_clean_data():
    if not is_login():
        return redirect("/login-required")

    data = request.get_json()

    clean_title = data.get("clean_title")
    clean_content = data.get("clean_content")
    keyword = data.get("keyword")
    raw_id = data.get("raw_id", None)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO clean_data (raw_id, clean_title, clean_content, keyword)
    VALUES (?, ?, ?, ?)
    """, (raw_id, clean_title, clean_content, keyword))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "新增 clean_data 成功",
        "clean_title": clean_title,
        "keyword": keyword,
    })


@app.route("/api/data/<int:clean_id>", methods=["DELETE"])
def api_delete_clean_data(clean_id):
    if not is_login():
        return redirect("/login-required")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clean_data WHERE id = ?", (clean_id,))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "删除 clean_data 成功",
        "id": clean_id,
    })


@app.route("/analysis")
def analysis():
    if not is_login():
        return redirect("/login-required")

    conn = get_connection()
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

    cursor.execute("SELECT COUNT(*) FROM raw_data")
    raw_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM clean_data")
    clean_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

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

                <div class="analysis-item">
                    <h2>{raw_count}</h2>
                    <p>原始资料数量</p>
                </div>

                <div class="analysis-item">
                    <h2>{clean_count}</h2>
                    <p>清洗后资料数量</p>
                </div>

                <div class="analysis-item">
                    <h2>{user_count}</h2>
                    <p>使用者数量</p>
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
    init_database()
    app.run(debug=True)