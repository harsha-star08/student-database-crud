import sqlite3

DATABASE_NAME = "students.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            course TEXT
        )
    """)

    connection.commit()

    connection.close()
    