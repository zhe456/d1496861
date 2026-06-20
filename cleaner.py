from src.cleaner.cleaner import clean_raw_data
from src.database.db import init_database


if __name__ == "__main__":
    init_database()
    clean_raw_data()