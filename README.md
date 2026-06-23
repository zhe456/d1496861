# 餐厅评价资料 AI 服务平台

## 一、专题名称

餐厅评价资料 AI 服务平台  
Restaurant Review AI Data Service Platform

---

## 二、专题简介

本系统是一个以「餐厅评价资料」为主题的 AI 资料服务平台，整合本学期课程所学的多个技术主题，包含 uv 虚拟环境管理、SQLite 资料库、CRUD 资料操作、requests 资料蒐集、Regular Expression 资料清洗、Flask Web 服务与 REST API、Socket 即时客服聊天室、Threading 多执行绪、Hash/Login 帐号安全，以及 OpenCV 人脸检测。

系统可以让管理员登入后查看餐厅资料、新增餐厅资料、删除错误资料、查看 JSON API，并进行资料分析。

此外，系统也提供资料蒐集器与资料清洗器，可以从外部公开 API 抓取资料，存入 `raw_data`，再使用正则表达式清洗后存入 `clean_data`，最后透过 API 与网页提供查询。

---

## 三、系统功能

1. 手动帐号密码登入
2. OpenCV 人脸检测登入
3. 登入后才显示完整系统功能
4. 查看全部餐厅资料
5. 依照餐厅类型筛选
6. 依照评分筛选
7. 新增餐厅资料
8. 删除餐厅资料
9. 餐厅资料 JSON API
10. clean_data JSON API
11. 资料分析页面
12. requests 资料蒐集器
13. Regular Expression 资料清洗器
14. Socket 即时客服聊天室
15. OpenCV 人脸框选结果图
16. 人脸 vs 非人脸简单分类

---

## 四、管理员测试帐号

### 管理员帐号

```text
帐号：admin
密码：1234
```

### 验收测试帐号

```text
帐号：yungchen
密码：teed6Vu[b)oa
```

---

## 五、专案结构

```text
final_demo/
├── pyproject.toml
├── README.md
├── environment_setup.md
├── main.py
├── crawler.py
├── cleaner.py
├── chat_server.py
├── chat_client.py
├── database/
│   └── restaurant.db
├── static/
│   └── style.css
├── uploads/
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py
│   ├── crawler/
│   │   ├── __init__.py
│   │   └── crawler.py
│   ├── cleaner/
│   │   ├── __init__.py
│   │   └── cleaner.py
│   ├── chat/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── client.py
│   ├── api/
│   ├── auth/
│   └── ai_vision/
├── .gitignore
└── uv.lock
```

---

## 六、各模组对应技术主题

| 模组 | 技术主题 | 使用位置 |
|---|---|---|
| M1 开发环境与专案结构 | uv、pyproject.toml、专案目录结构 | `pyproject.toml`、`src/` |
| M2 资料库核心 | SQLite、CRUD | `src/database/db.py` |
| M3 资料蒐集器 | requests、公开 API 抓取 | `src/crawler/crawler.py`、`crawler.py` |
| M4 资料清洗器 | Regular Expression | `src/cleaner/cleaner.py`、`cleaner.py` |
| M5 API 与 Web 服务 | Flask、REST API | `main.py` |
| M6 即时客服系统 | Socket、Threading、Exception Handling、Hash/Login | `src/chat/server.py`、`src/chat/client.py` |
| M7 AI 影像分析服务 | OpenCV、Haar Cascade、人脸检测 | `main.py` 的 `detect_face()` |

---

## 七、资料库设计

本系统使用 SQLite 资料库，资料库档案位置：

'''text
database/restaurant.db
'''

系统启动时会自动初始化资料库，并建立需要的资料表。

### 1. users

用于储存使用者帐号资料，密码使用 hash 方式储存。

主要栏位：

   text
id
username
password_hash
role


功能：

- 储存登入帐号
- 储存 hash 后的密码
- 提供手动登入与聊天室登入验证

### 2. raw_data

用于储存爬虫抓取到的原始资料。

主要栏位：

   text
id
source
title
content
url
created_at


功能：

- 存放 requests 抓取到的外部资料
- 保留尚未清洗的原始内容

### 3.clean_data

用于储存经过正则表达式清洗后的资料。

主要栏位：

   text
id
raw_id
clean_title
clean_content
keyword
created_at


功能：

- 存放清洗后的资料
- 提供 `/api/data` 查询
- 支援关键字查询

### 4. restaurants

用于储存餐厅评价资料。

主要栏位：

   text
id
name
area
category
rating
price_level
address


功能：

- 储存餐厅名称
- 储存餐厅地区
- 储存餐厅类型
- 储存评分
- 储存价格区间
- 储存地址

---

## 八、环境安装方式

### 1. 使用 uv 安装环境

```bash
uv sync
```

### 2. 如果缺少套件，可以手动加入

```bash
uv add flask
uv add requests
uv add opencv-python
```

---

## 九、系统执行方式

### 1. 执行主系统

```bash
uv run main.py
```

浏览器打开：

text
http://127.0.0.1:5000/


### 2. 执行资料蒐集器

   bash
uv run crawler.py


功能说明：

- 使用 requests 从公开 API 抓取资料
- 将原始资料存入 `raw_data`
- 完成 M3 资料蒐集器功能

### 3. 执行资料清洗器

bash
uv run cleaner.py


功能说明：

- 从 `raw_data` 读取资料
- 使用 Regular Expression 清洗文字
- 将清洗结果存入 `clean_data`
- 完成 M4 资料清洗器功能

### 4. 执行即时客服聊天室

先开启第一个终端机，启动聊天室服务器：

   bash
uv run chat_server.py


再开启第二个终端机，启动聊天室客户端：

```bash
uv run chat_client.py
```

可以使用以下帐号登入：

```text
admin / 1234
yungchen / teed6Vu[b)oa
```

如需测试多人聊天，可以再开启第三个终端机，再执行一次：

```bash
uv run chat_client.py
```

---

## 十、系统页面

### 首页

```text
http://127.0.0.1:5000/
```

未登入时，首页只显示：

```text
手动登入
人脸辨识登入
```

登入后才会显示完整系统功能。

### 手动登入

```text
http://127.0.0.1:5000/login
```

### 人脸检测登入

```text
http://127.0.0.1:5000/face-login
```

### 餐厅清单

```text
http://127.0.0.1:5000/restaurants
```

### 新增餐厅资料

```text
http://127.0.0.1:5000/add
```

### 餐厅 JSON API

```text
http://127.0.0.1:5000/api/restaurants
```

### clean_data API

```text
http://127.0.0.1:5000/api/data
```

### 资料分析页面

```text
http://127.0.0.1:5000/analysis
```

---

## 十一、API 说明

### 1. 查询餐厅资料

```text
GET /api/restaurants
```

功能：回传餐厅资料 JSON。

### 2. 查询 clean_data

```text
GET /api/data
```

功能：回传清洗后的资料。

### 3. 使用关键字查询 clean_data

```text
GET /api/data?keyword=data
```

功能：依照关键字筛选 `clean_data` 资料。

### 4. 新增 clean_data

```text
POST /api/data
```

JSON 格式：

```json
{
  "raw_id": 1,
  "clean_title": "sample title",
  "clean_content": "sample content",
  "keyword": "sample"
}
```

### 5. 删除 clean_data

```text
DELETE /api/data/<id>
```

例如：

```text
DELETE /api/data/1
```

---

## 十二、OpenCV 人脸检测功能说明

本系统提供 OpenCV 人脸检测登入功能。

流程如下：

```text
上传图片
↓
OpenCV 读取图片
↓
转换为灰阶影像
↓
Haar Cascade 检测人脸
↓
眼睛检测验证
↓
通过则登入系统
↓
输出人脸框选结果图
```

系统使用的 OpenCV 技术包含：

```python
cv2.imread
cv2.cvtColor
cv2.CascadeClassifier
detectMultiScale
cv2.rectangle
cv2.putText
```

为了减少误判，本系统除了使用人脸 Haar Cascade，也加入：

```text
眼睛检测
人脸大小比例过滤
灰阶直方图均衡化
```

如果上传非人脸图片，例如动物或风景，系统会判定失败。  
如果上传清楚的正面人脸图片，系统会登入成功，并显示绿色人脸框与蓝色眼睛框。

目前实现的是：

```text
人脸检测
人脸 vs 非人脸简单分类
```

尚未扩充成完整的人脸身份识别。未来可以使用 PCA、Eigenface、Fisherface 或深度学习模型继续改进。

---

## 十三、资料流程 Pipeline

本系统资料流程如下：

```text
外部公开 API
↓
crawler.py 使用 requests 抓取资料
↓
存入 raw_data
↓
cleaner.py 使用 Regular Expression 清洗资料
↓
存入 clean_data
↓
Flask REST API 提供查询
↓
网页分析页面显示统计结果
```

---

## 十四、即时客服聊天室说明

本系统提供 Socket 即时客服聊天室功能。

### 服务器

```text
src/chat/server.py
chat_server.py
```

功能：

- 建立 socket server
- 等待多个 client 连线
- 使用 threading 支援多人同时聊天
- 使用 exception handling 避免单一使用者断线导致服务器崩溃

### 客户端

```text
src/chat/client.py
chat_client.py
```

功能：

- 使用帐号密码登入
- 登入成功后连接聊天室
- 可以传送讯息
- 可以接收其他使用者讯息
- 输入 exit 可以离开聊天室

---

## 十五、遇到的问题与解决方法

### 1. no such table: restaurants

问题原因：资料库尚未初始化。  
解决方法：将 `init_database()` 整合到 `main.py`，系统启动时自动建立资料表。

### 2. crawler.py 找不到 src 模组

问题原因：直接执行 `src/crawler/crawler.py` 时，Python 找不到根目录。  
解决方法：新增外层 `crawler.py`，统一从根目录执行：

```bash
uv run crawler.py
```

### 3. cleaner.py 找不到模组

问题原因：档案名称与资料夹名称不一致。  
解决方法：统一使用：

```text
src/cleaner/cleaner.py
cleaner.py
```

执行：

```bash
uv run cleaner.py
```

### 4. 人脸检测误判动物图片

问题原因：单纯使用 Haar Cascade 可能会误判。  
解决方法：加入眼睛检测、大小比例过滤和灰阶直方图均衡化，提高判断准确度。

### 5. 聊天室客户端中断

问题原因：使用者关闭客户端或按下 Ctrl+C。  
解决方法：服务器端使用 Exception Handling，避免单一使用者断线造成服务器崩溃。

---

## 十六、技术涵盖检核表

| 技术主题 | 是否使用 | 使用位置 |
|---|---|---|
| uv | 已使用 | `pyproject.toml`、`uv run` |
| pyproject.toml | 已使用 | `pyproject.toml` |
| SQLite | 已使用 | `src/database/db.py` |
| CRUD | 已使用 | 餐厅新增、查询、删除；clean_data 新增、查询、删除 |
| requests | 已使用 | `src/crawler/crawler.py` |
| Regular Expression | 已使用 | `src/cleaner/cleaner.py` |
| Flask | 已使用 | `main.py` |
| REST API | 已使用 | `/api/restaurants`、`/api/data` |
| Socket | 已使用 | `src/chat/server.py`、`src/chat/client.py` |
| Threading | 已使用 | 聊天室多人连线 |
| Exception Handling | 已使用 | crawler、chat server、chat client、OpenCV 读取图片 |
| Hash/Login | 已使用 | `src/database/db.py`、登入系统、聊天室登入 |
| OpenCV | 已使用 | `main.py` |
| Haar Cascade | 已使用 | `detect_face()` |
| 人脸检测 | 已使用 | 人脸登入功能 |
| 人脸 vs 非人脸 | 已使用 | 上传图片判断 |

---

## 十七、GitHub 与版本管理

本专案使用 Git 进行版本管理。

常用指令：

```bash
git add .
git commit -m "更新内容"
git push
```

`.gitignore` 已排除：

```text
.venv/
__pycache__/
*.pyc
database/*.db
uploads/
```

---

## 十八、总结

本专题完成一个可运行的餐厅评价资料 AI 服务平台。

系统整合了：

```text
uv
SQLite
CRUD
requests
Regular Expression
Flask REST API
Socket
Threading
Exception Handling
Hash/Login
OpenCV
Haar Cascade
```

平台可以从外部公开 API 蒐集资料，使用正则表达式清洗资料，储存到 SQLite 资料库，并透过 Flask 网页与 REST API 提供查询服务。

系统也加入了登入管理、即时客服聊天室，以及 OpenCV 人脸检测登入功能，形成一个可以展示完整资料流程与 AI 影像分析的 Mini Software Product。