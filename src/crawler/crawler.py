import requests

from src.database.db import init_database, insert_raw_data


def fetch_sample_restaurant_news():
    """
    M3 资料蒐集器：
    使用 requests 从公开 API 抓取资料。
    这里先使用 JSONPlaceholder 当作示范资料来源，
    模拟餐厅平台从外部取得文章/评论资料。
    """

    url = "https://jsonplaceholder.typicode.com/posts"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        posts = response.json()

        count = 0

        for post in posts[:10]:
            title = post.get("title", "")
            content = post.get("body", "")

            insert_raw_data(
                source="JSONPlaceholder",
                title=title,
                content=content,
                url=url
            )

            count += 1

        print(f"资料蒐集完成，共新增 {count} 笔 raw_data。")

    except requests.exceptions.RequestException as e:
        print("资料蒐集失败：", e)


if __name__ == "__main__":
    init_database()
    fetch_sample_restaurant_news()