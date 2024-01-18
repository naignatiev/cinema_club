from dataclasses import astuple
from datetime import datetime, timezone
from contextlib import closing

import pytest
from dotenv import load_dotenv
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor

from load_data import SQLiteExtractor, SQLITE_DB_PATH
from models import TABLE_NAMES, get_table_transfer_model
from config import dsl, BATCH_SIZE


load_dotenv()


@pytest.fixture(scope='module')
def sqlite_conn():
    with closing(sqlite3.connect(SQLITE_DB_PATH)) as sqlite_conn:
        sqlite_conn.row_factory = sqlite3.Row
        yield sqlite_conn


@pytest.fixture(scope='function')
def sqlite_cursor(sqlite_conn):
    yield sqlite_conn.cursor()


@pytest.fixture(scope='module')
def pg_conn():
    with closing(psycopg2.connect(**dsl, cursor_factory=DictCursor)) as pg_conn:
        yield pg_conn


@pytest.fixture(scope='function')
def pg_cursor(pg_conn):
    with pg_conn.cursor() as pg_cursor:
        yield pg_cursor


def _get_postgres_content(cursor, table_name):
    model_cls = get_table_transfer_model(table_name)
    cursor.execute(f'select * from "content"."{table_name}" order by id;')
    while batch := cursor.fetchmany(BATCH_SIZE):
        yield [model_cls(**row) for row in batch]


def _check_equality(sqlite_data, postgres_data):
    for sqlite_batch, postgres_batch in zip(sqlite_data, postgres_data):
        for sqlite_row, postgres_row in zip(sqlite_batch, postgres_batch):
            _check_rows_equality(sqlite_row, postgres_row)


def _check_rows_equality(sqlite_row, postgres_row):
    for sqlite_value, postgres_value in zip(astuple(sqlite_row), astuple(postgres_row)):
        if sqlite_value is None and postgres_value:
            continue
        if isinstance(postgres_value, datetime) and isinstance(sqlite_value, str):
            sqlite_value = datetime.strptime(
                sqlite_value,
                '%Y-%m-%d %H:%M:%S.%f+00'
            ).replace(tzinfo=timezone.utc)
        assert sqlite_value == postgres_value, \
            str(sqlite_value) + '\n' + str(postgres_value) + '\nSqlite Row: ' + str(sqlite_row)


def test_lens(pg_cursor, sqlite_cursor):
    for table_name in set(TABLE_NAMES):
        pg_cursor.execute(f'select count(*) from content.{table_name}')
        pg_table_length = pg_cursor.fetchone()[0]
        sqlite_cursor.execute(f'select count(*) from {table_name}')
        sqlite_table_length = sqlite_cursor.fetchone()[0]
        assert sqlite_table_length == pg_table_length, f'Table {table_name}'


def test_consistency(sqlite_conn, pg_cursor):
    for table_name in TABLE_NAMES:
        sqlite_data_gen = SQLiteExtractor(sqlite_conn).extract_table(table_name)
        postgres_data_gen = _get_postgres_content(pg_cursor, table_name)
        _check_equality(sqlite_data_gen, postgres_data_gen)
