from src.crawler.crawler import fetch_sample_restaurant_news
from src.database.db import init_database


if __name__ == "__main__":
    init_database()
    fetch_sample_restaurant_news()