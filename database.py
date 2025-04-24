from pathlib import Path

import aiosqlite


class Connector:
    def __init__(self):
        self.database = Path(__file__).parent / "commands.db"
        self.connection = None
        self.commands_cache = {}

    async def connect(self):
        self.connection = await aiosqlite.connect(self.database)
        async with self.connection.cursor() as cursor:
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS command_keys (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        key VARCHAR(128)
                                    )"""
            )
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS command_responses (
                                        id INTEGER,
                                        response text
                                    )"""
            )
            await self.connection.commit()

    async def populate_cache(self):
        if self.connection is None:
            await self.connect()

        async with self.connection.cursor() as cursor:
            await cursor.execute("SELECT key, response FROM command_keys JOIN command_responses ON command_keys.id = command_responses.id")
            rows = await cursor.fetchall()
            for row in rows:
                key, response = row
                if key not in self.commands_cache:
                    self.commands_cache[key] = [response]
                else:
                    self.commands_cache[key].append(response)

    async def get_command(self, key):
        return self.commands_cache.get(key)
    
    async def add_command(self, key, response):
        async with self.connection.cursor() as cur:
            query = "INSERT INTO command_keys(key) VALUES(?)"
            await cur.execute(query, (key,))
            command_id = cur.lastrowid
            query = "INSERT INTO command_responses(id, response) VALUES(?, ?)"
            await cur.execute(query, (command_id, response))
            await self.connection.commit()
            self.commands_cache[key] = [response]

    async def remove_command(self, key):
        async with self.connection.cursor() as cur:
            query = "DELETE FROM command_responses WHERE id = (SELECT id FROM command_keys WHERE key = ?)"
            await cur.execute(query, (key,))
            query = "DELETE FROM command_keys WHERE key = ?"
            await cur.execute(query, (key,))
            await self.connection.commit()
            if key in self.commands_cache:
                del self.commands_cache[key]

    async def add_command_response(self, key, response):
        async with self.connection.cursor() as cur:
            query = "INSERT INTO command_responses(id, response) VALUES((SELECT id FROM command_keys WHERE key = ?), ?)"
            await cur.execute(query, (key, response))
            await self.connection.commit()
            if key in self.commands_cache:
                self.commands_cache[key].append(response)

    async def remove_command_response(self, key, response):
        async with self.connection.cursor() as cur:
            query = "DELETE FROM command_responses WHERE id = (SELECT id FROM command_keys WHERE key = ?) AND response = ?"
            await cur.execute(query, (key, response))
            if key in self.commands_cache and response in self.commands_cache[key]:
                self.commands_cache[key].remove(response)
            # If the command has no responses left, remove it from the cache and database
            if self.commands_cache[key] == []:
                del self.commands_cache[key]
                query = "DELETE FROM command_keys WHERE key = ?"
                await cur.execute(query, (key,))
            await self.connection.commit()

    async def add_command_history(self, user, command):
        async with self.connection.cursor() as cur:
            query = "INSERT INTO command_history(user, command) VALUES(?, ?)"
            await cur.execute(query, (user, command))
            await self.connection.commit()
