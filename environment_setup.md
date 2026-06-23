# Environment Setup

## 一、开发环境

* 作业系统：Windows
* 编辑器：VS Code
* Python 环境管理：uv
* 后端框架：Flask
* 资料库：SQLite
* 影像处理：OpenCV
* 版本控制：Git / GitHub

---

## 二、环境建立过程

我先建立 `final_demo` 专案资料夹，并使用 VS Code 打开此资料夹。

接着使用 uv 建立 Python 专案环境，并透过 `pyproject.toml` 管理套件。

本系统主要使用以下套件：

```text
flask
requests
opencv-python
```

安装方式：

```bash
uv sync
```

如果缺少套件，可以使用：

```bash
uv add flask
uv add requests
uv add opencv-python
```

---

## 三、专案结构建立

本系统依照期末专题要求，将功能切成不同模组：

```text
src/database/
src/crawler/
src/cleaner/
src/chat/
src/api/
src/auth/
src/ai_vision/
```

其中：

```text
src/database/ 负责 SQLite 资料库与 CRUD
src/crawler/ 负责 requests 资料蒐集
src/cleaner/ 负责 Regular Expression 资料清洗
src/chat/ 负责 Socket 即时客服聊天室
main.py 负责 Flask Web、API、登入、人脸检测
```

完整专案结构如下：

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

## 四、执行方式

执行主系统：

```bash
uv run main.py
```

执行资料蒐集器：

```bash
uv run crawler.py
```

执行资料清洗器：

```bash
uv run cleaner.py
```

执行聊天室服务器：

```bash
uv run chat_server.py
```

执行聊天室客户端：

```bash
uv run chat_client.py
```

---

## 五、系统启动流程

本系统主要执行顺序如下：

```text
1. uv run crawler.py
2. uv run cleaner.py
3. uv run main.py
4. 浏览器打开 http://127.0.0.1:5000/
```

如果要测试即时客服聊天室，则另外开启终端机：

```text
终端机 1：uv run chat_server.py
终端机 2：uv run chat_client.py
终端机 3：uv run chat_client.py
```

---

## 六、测试帐号

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

## 七、AI 使用纪录

在开发过程中，我使用 AI 协助规划系统架构、整理七大模组、检查程式错误，并协助改善 README 文件与报告内容。

AI 协助内容包含：

1. 规划 AI Data Service Platform 七大模组
2. 协助设计 SQLite 资料表
3. 协助建立 `users`、`raw_data`、`clean_data`、`restaurants` 等资料表
4. 协助整理 Flask API 路由
5. 协助设计手动登入功能
6. 协助建立密码 hash 机制
7. 协助修正 `crawler.py` 找不到模组的问题
8. 协助修正 `cleaner.py` 模组路径问题
9. 协助改善 OpenCV 人脸检测误判问题
10. 协助加入眼睛检测、人脸大小过滤与灰阶直方图均衡化
11. 协助建立 Socket 即时客服聊天室
12. 协助整理 README.md 与执行步骤
13. 协助规划展示影片流程
14. 协助整理报告内容与技术涵盖检核表

---

## 八、各模组开发纪录

### M1 开发环境与专案结构

本系统使用 uv 管理 Python 环境，并使用 `pyproject.toml` 记录专案套件。

我将系统切成多个模组资料夹，避免所有程式都写在同一个 `main.py` 中。

主要目录包含：

```text
src/database/
src/crawler/
src/cleaner/
src/chat/
src/api/
src/auth/
src/ai_vision/
```

---

### M2 资料库核心

本系统使用 SQLite 作为资料库。

资料库档案位置：

```text
database/restaurant.db
```

主要资料表：

```text
users
raw_data
clean_data
restaurants
```

其中 `users` 用于登入系统，密码使用 hash 储存，不直接储存明文密码。

`raw_data` 用于储存爬虫抓取到的原始资料。

`clean_data` 用于储存清洗后的资料。

`restaurants` 用于储存餐厅评价资料。

---

### M3 资料蒐集器

资料蒐集器使用 requests 从公开 API 抓取资料。

执行方式：

```bash
uv run crawler.py
```

资料抓取完成后，会将原始资料存入 `raw_data` 资料表。

---

### M4 资料清洗器

资料清洗器使用 Regular Expression 清洗文字资料。

执行方式：

```bash
uv run cleaner.py
```

清洗规则包含：

```text
1. 移除 HTML 标签
2. 移除特殊符号
3. 合并多余空白
4. 简单关键字分类
```

清洗后的资料会存入 `clean_data` 资料表。

---

### M5 API 与 Web 服务

本系统使用 Flask 建立网页与 REST API。

主要页面包含：

```text
/
登录首页

/login
手动登入

/face-login
OpenCV 人脸检测登入

/restaurants
餐厅清单

/add
新增餐厅资料

/analysis
资料分析页面
```

主要 API 包含：

```text
GET /api/restaurants
GET /api/data
POST /api/data
DELETE /api/data/<id>
```

---

### M6 即时客服系统

本系统使用 Socket 建立即时客服聊天室，并使用 Threading 支援多个使用者同时连线。

执行服务器：

```bash
uv run chat_server.py
```

执行客户端：

```bash
uv run chat_client.py
```

聊天室登入会使用资料库中的帐号密码，并透过 hash 机制验证密码。

---

### M7 AI 影像分析服务

本系统使用 OpenCV 建立人脸检测登入功能。

主要技术包含：

```text
OpenCV
Haar Cascade
灰阶转换
detectMultiScale
人脸框选
眼睛检测
人脸 vs 非人脸分类
```

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

如果上传清楚的人脸图片，系统会登入成功，并显示绿色人脸框与蓝色眼睛框。

如果上传动物、风景或没有人脸的图片，系统会判定失败。

---

## 九、遇到的问题与解决方式

### 1. no such table: restaurants

问题原因：

资料库尚未建立资料表，导致 Flask 查询资料时发生错误。

解决方式：

将 `init_database()` 放入 `main.py`，让系统启动时自动建立资料表。

---

### 2. crawler.py 执行失败

问题原因：

一开始直接执行 `src/crawler/crawler.py`，Python 找不到 `src` 模组。

解决方式：

在专案根目录新增外层 `crawler.py`，统一从根目录执行：

```bash
uv run crawler.py
```

---

### 3. cleaner.py 找不到模组

问题原因：

档案名称与资料夹名称混淆，导致 import 路径错误。

解决方式：

统一使用：

```text
src/cleaner/cleaner.py
cleaner.py
```

并从根目录执行：

```bash
uv run cleaner.py
```

---

### 4. 人脸检测误判动物图片

问题原因：

单纯使用 Haar Cascade 有时会把非人脸误判成人脸。

解决方式：

加入以下机制：

```text
1. 眼睛检测
2. 人脸大小比例过滤
3. 灰阶直方图均衡化
```

这样可以降低把动物或其他物品误判成人脸的机率。

---

### 5. 聊天室客户端中断

问题原因：

使用者关闭客户端或按下 Ctrl+C 会造成断线。

解决方式：

在 server 和 client 加入 Exception Handling，让单一使用者离开不会影响整个聊天室服务器。

---

### 6. GitHub 上传时不想上传虚拟环境

问题原因：

`.venv/` 资料夹很大，不应该上传到 GitHub。

解决方式：

在 `.gitignore` 加入：

```text
.venv/
__pycache__/
*.pyc
database/*.db
uploads/
```

---

## 十、目前完成状态

本系统已经完成：

```text
M1 uv 开发环境与专案结构
M2 SQLite 资料库与 CRUD
M3 requests 资料蒐集器
M4 Regular Expression 资料清洗器
M5 Flask Web 与 REST API
M6 Socket 即时客服聊天室
M7 OpenCV 人脸检测服务
```

系统可以正常执行，并提供：

```text
网页首页
手动登入
OpenCV 人脸检测登入
餐厅资料查询
餐厅资料新增
餐厅资料删除
JSON API
clean_data API
资料分析页面
资料蒐集器
资料清洗器
即时客服聊天室
```

---

## 十一、后续可改进方向

虽然目前系统已经完成基础功能，但未来仍可以继续扩充：

```text
1. 加入 Django Admin 后台
2. 加入更完整的人脸身份识别
3. 使用 PCA / Eigenface 做人脸比对
4. 加入更多餐厅资料来源
5. 加入图表化分析
6. 加入使用者权限管理
7. 加入 API client 测试程式
```

---

## 十二、总结

本系统从一开始的餐厅资料查询平台，逐步整合成一个完整的 AI Data Service Platform。

开发过程中，我完成了环境建立、资料库设计、资料蒐集、资料清洗、Web 服务、API、登入系统、Socket 聊天室与 OpenCV 人脸检测功能。

透过本专题，我练习到如何将多个独立技术整合成一个可以运行的系统，而不是只写单一的 `.py` 档案。
