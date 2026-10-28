import sqlite3
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "database", "database.db")
with sqlite3.connect(DATABASE) as conn:

    conn.execute(
    """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
    """
    )
    
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            match_date TEXT NOT NULL,
            opponent TEXT NOT NULL,
            stadium TEXT,
            memo TEXT,
            season TEXT,
            photo_filename TEXT
        )
        """
    )
    
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            trip_id INTEGER,
            category TEXT NOT NULL,
            amount INTEGER NOT NULL,
            spent_on TEXT NOT NULL,
            memo TEXT
        )
        """
    )
print("データベースを初期化しました。")
