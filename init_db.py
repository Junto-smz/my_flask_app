import sqlite3

with sqlite3.connect("./database/database.db") as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount INTEGER NOT NULL)
            """)
    
    print("データベースを初期化しました")