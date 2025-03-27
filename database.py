from pathlib import Path

import aiosqlite


class Connector:
    def __init__(self):
        self.database = Path(__file__).parent / "commands.db"
        self.connection = None

    async def connect(self):
        self.connection = await aiosqlite.connect(self.database)
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS commands (
                                        key VARCHAR(128),
                                        message text,
                                        PRIMARY KEY(key)
                                    )"""
            )
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS command_history (
                                        user INTEGER,
                                        command VARCHAR(128)
                                        )"""
            )
            await self.connection.commit()

    async def get_commands(self):
        async with self.connection.cursor() as cur:
            query = "SELECT * FROM commands"
            await cur.execute(query)
            return await cur.fetchall()

    async def get_command(self, key):
        async with self.connection.cursor() as cur:
            query = "SELECT * FROM commands WHERE key like ?"
            await cur.execute(query, (key,))
            return await cur.fetchone()

    async def add_command(self, key, message):
        async with self.connection.cursor() as cur:
            query = "INSERT INTO commands(key, message) VALUES(?, ?)"
            await cur.execute(query, (key, message))
            await self.connection.commit()

    async def remove_command(self, key):
        async with self.connection.cursor() as cur:
            query = "DELETE FROM commands WHERE key like ?"
            await cur.execute(query, (key,))
            await self.connection.commit()

    async def add_command_history(self, user, command):
        async with self.connection.cursor() as cur:
            query = "INSERT INTO command_history(user, command) VALUES(?, ?)"
            await cur.execute(query, (user, command))
            await self.connection.commit()

    async def query(self, query):
        async with self.connection.cursor() as cur:
            await cur.execute(query)
            return await cur.fetchall()
