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