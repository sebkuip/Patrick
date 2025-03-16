import sqlite3
from pathlib import Path


class Connector:
    def __init__(self):
        self.database = Path(__file__).parent / "commands.db"
        with sqlite3.connect(self.database) as con:
            cursor = con.cursor()
            query = """CREATE TABLE IF NOT EXISTS commands (
                            key VARCHAR(128),
                            message text,
                            PRIMARY KEY(key)
                        )"""
            cursor.execute(query)
            con.commit()

    def get_commands(self):
        with sqlite3.connect(self.database) as con:
            cursor = con.cursor()
            query = "SELECT * FROM commands"
            cursor.execute(query)
            return cursor.fetchall()

    def get_command(self, key):
        with sqlite3.connect(self.database) as con:
            cursor = con.cursor()
            query = "SELECT * FROM commands WHERE key like ?"
            cursor.execute(query, (key,))
            return cursor.fetchone()

    def add_command(self, key, message):
        with sqlite3.connect(self.database) as con:
            cursor = con.cursor()
            query = "INSERT INTO commands(key, message) VALUES(?, ?)"
            cursor.execute(query, (key, message))
            con.commit()

    def remove_command(self, key):
        with sqlite3.connect(self.database) as con:
            cursor = con.cursor()
            query = "DELETE FROM commands WHERE key like ?"
            cursor.execute(query, (key,))
            con.commit()
