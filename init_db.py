import sqlite3

with sqlite3.connect("./database/database.db") as conn:

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
            title TEXT NOT NULL,
            match_date TEXT NOT NULL,
            opponent TEXT NOT NULL,
            stadium TEXT,
            memo TEXT
        )
        """
    )
    
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER,
            category TEXT NOT NULL,
            amount INTEGER NOT NULL,
            spent_on TEXT NOT NULL,
            memo TEXT
        )
        """
    )
print("データベースを初期化しました。")
