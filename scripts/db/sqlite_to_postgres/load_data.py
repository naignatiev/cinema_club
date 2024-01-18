import os
import sqlite3
from dataclasses import fields, astuple
from typing import Any, Type, Generator
from contextlib import closing

from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

from models import TABLE_NAMES, get_table_transfer_model, TableTransferModel
from config import dsl, BATCH_SIZE

load_dotenv()


SQLITE_DB_PATH = os.environ.get('SQLITE_DB_PATH')

FIELDS_TRANSLATE_DICT = {
    'created_at': 'created',
    'updated_at': 'modified',
}
STOP_FIELDS = ['file_path']


def _translate_to_postgres_naming(data: dict[str, Any]) -> None:
    for sqlite3_name, postgres_name in FIELDS_TRANSLATE_DICT.items():
        if sqlite3_name in data:
            data[postgres_name] = data.pop(sqlite3_name)
    for stop_field in STOP_FIELDS:
        if stop_field in data:
            data.pop(stop_field)


def _filter_nones(data: dict[str, Any]) -> None:
    none_fields = []
    for key, value in data.items():
        if value is None:
            none_fields.append(key)
    for key in none_fields:
        data.pop(key)


def _db_row_to_dataclass(row: sqlite3.Row, data_cls: Type[TableTransferModel]):
    row: dict = dict(row)
    _translate_to_postgres_naming(row)
    _filter_nones(row)
    return data_cls(**row)


class PostgresSaver:
    def __init__(self, pg_conn: _connection):
        self._conn = pg_conn
        self._cursor = self._conn.cursor()

    def save_data(self, table_name, data: Generator[list[TableTransferModel], None, None]):
        column_names = [field.name for field in fields(get_table_transfer_model(table_name))]
        col_count = ', '.join(['%s'] * len(column_names))
        for batch in data:
            args = ','.join(
                self._cursor.mogrify(
                    f"({col_count})",
                    astuple(row)
                ).decode('utf-8') for row in batch
            )
            self._cursor.execute(f"""
                INSERT INTO content.{table_name} ({','.join(column_names)})
                VALUES {args} ON CONFLICT DO NOTHING
            """)

    def commit(self):
        self._conn.commit()


class SQLiteExtractor:
    def __init__(self, connection: sqlite3.Connection):
        self._cursor = connection.cursor()

    def extract_table(self, table_name: str) -> Generator[list[TableTransferModel], None, None]:
        self._cursor.execute(f'Select * from {table_name} order by id')
        model_cls: type[TableTransferModel] = get_table_transfer_model(table_name=table_name)
        while batch := self._cursor.fetchmany(BATCH_SIZE):
            instances = map(_db_row_to_dataclass, batch, [model_cls] * len(batch))
            yield instances


def load_from_sqlite(sqlite_conn: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_extractor = SQLiteExtractor(sqlite_conn)
    for table_name in TABLE_NAMES:
        rows_gen = sqlite_extractor.extract_table(table_name)
        postgres_saver.save_data(table_name, rows_gen)
    postgres_saver.commit()


if __name__ == '__main__':
    with closing(sqlite3.connect(SQLITE_DB_PATH)) as sqlite_conn, \
         closing(psycopg2.connect(**dsl, cursor_factory=DictCursor)) as pg_conn:
        sqlite_conn.row_factory = sqlite3.Row
        load_from_sqlite(sqlite_conn, pg_conn)
