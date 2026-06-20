import re

from src.database.db import (
    init_database,
    get_all_raw_data,
    insert_clean_data,
)


def clean_text(text):
    """
    使用 Regular Expression 清洗文字。
    至少包含 3 种清洗规则：
    1. 移除 HTML 标签
    2. 移除特殊符号
    3. 合并多余空白
    """

    if text is None:
        return ""

    # 规则 1：移除 HTML 标签，例如 <p>...</p>
    text = re.sub(r"<.*?>", "", text)

    # 规则 2：移除特殊符号，只保留中英文、数字、空白
    text = re.sub(r"[^a-zA-Z0-9\u4e00-\u9fff\s]", " ", text)

    # 规则 3：合并多个空白
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_keyword(title, content):
    """
    简单关键字分类：
    依据文字内容判断资料类别。
    """

    text = f"{title} {content}".lower()

    if "restaurant" in text or "food" in text:
        return "restaurant"
    if "data" in text:
        return "data"
    if "service" in text:
        return "service"

    return "general"


def clean_raw_data():
    """
    从 raw_data 读取资料，
    使用正则表达式清洗后，
    存入 clean_data。
    """

    raw_rows = get_all_raw_data()

    count = 0

    for row in raw_rows:
        raw_id = row["id"]
        title = row["title"]
        content = row["content"]

        clean_title = clean_text(title)
        clean_content = clean_text(content)
        keyword = extract_keyword(clean_title, clean_content)

        insert_clean_data(
            raw_id=raw_id,
            clean_title=clean_title,
            clean_content=clean_content,
            keyword=keyword,
        )

        count += 1

    print(f"资料清洗完成，共新增 {count} 笔 clean_data。")


if __name__ == "__main__":
    init_database()
    clean_raw_data()