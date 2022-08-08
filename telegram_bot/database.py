import sqlite3
from itertools import chain
from typing import List
from telebot import types

from telegram_bot import config as cfg
from telegram_bot import exceptions as ex


class Planner:

    def __init__(self, db_name: str = cfg.DB_NAME) -> None:
        self.db_name = db_name
        self.__create_table()

    def __create_table(self):
        with sqlite3.connect(self.db_name) as conn:
            query = """
                CREATE TABLE IF NOT EXISTS planner(
                    userid INT,
                    plan TEXT
                )
            """
            conn.execute(query)

    def add(self, message: types.Message):
        with sqlite3.connect(self.db_name) as conn:
            query = """
                INSERT INTO planner VALUES (?,?);
            """
            value = (message.chat.id, message.text)
            conn.execute(query, value)

    def get_tasks(self, message: types.Message) -> List[str]:
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT plan FROM planner WHERE userid=?;",
                (message.chat.id,)
            )
            tasks = cur.fetchall()
            tasks = list(chain.from_iterable(tasks))

            if len(tasks) == 0:
                raise ex.TaskNotExists

            return tasks

    def show(self, message: types.Message):
        tasks = self.get_tasks(message=message)
        prepared = self.prepare_tasks(tasks=tasks)
        return prepared

    def delete(self, message: types.Message):
        with sqlite3.connect(self.db_name) as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM planner WHERE userid==? AND plan==?",
                (message.chat.id, message.text)
            )
            conn.commit()

    def delete_all(self, message: types.Message):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM planner WHERE userid==?',
                (message.chat.id,)
            )
            conn.commit()

    @staticmethod
    def prepare_tasks(tasks: List[str]):
        prepare = '\n'.join([f'{i + 1}. {task}' for i, task in enumerate(tasks)])
        return prepare
