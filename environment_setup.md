## 最终成功方式

我将资料库初始化功能整合到 main.py 中，
所以只要执行：

uv run main.py

系统就会自动检查 database 资料夹和 restaurant.db，
如果资料表不存在，会自动建立 restaurants 表格，
如果没有资料，会自动加入预设餐厅资料。

这样老师或助教在执行时，不需要额外执行 init_db.py，
可以减少 no such table: restaurants 的错误。
```md
# Environment Setup

## 一、开发环境

- 作业系统：Windows
- 编辑器：VS Code
- Python 执行方式：uv run
- 后端框架：Flask
- 资料库：SQLite
- 版本控制：Git / GitHub

## 二、环境建立过程

我先建立 final_demo 专案资料夹，并在 VS Code 中打开此资料夹。

接着建立以下资料夹：

```text
app/
api/
database/
utils/
static/

## 新增功能纪录

本次系统新增了餐厅资料新增功能与删除功能。

新增功能使用 Flask 的 POST 表单，将使用者输入的餐厅资料写入 SQLite 资料库。

删除功能使用餐厅 id 删除指定资料，并在删除前加入确认提示，避免误删资料。

完成后系统已经具备新增、查询、删除、API 回传和资料分析功能。

## AI 使用纪录补充

我询问 AI 如何美化系统背景，让网页更符合餐厅评价平台主题。

AI 建议使用多种餐厅风格融合的设计概念，例如火锅、日式、韩式、烧肉、咖啡厅与义大利料理的色彩元素。

我理解后将背景改为多层渐层、圆形光影与玻璃卡片风格，让系统画面不再单调，并更符合餐厅资料分析平台的主题。