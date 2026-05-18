# PostgreSQL connection

import psycopg2
import os

conn = psycopg2.connect(
    os.getenv("DATABASE_URL")
)


def get_cursor() -> psycopg2.extensions.cursor:

    return conn.cursor()


def commit() -> None:

    conn.commit()


def rollback() -> None:

    conn.rollback()