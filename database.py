import sqlite3
from sqlite3 import Connection
from typing import Optional

import bcrypt

from config import DATABASE_PATH, create_application_directories


def get_connection() -> Connection:
   

    create_application_directories()

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables() -> None:
  
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                description TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL CHECK(amount > 0),
                description TEXT,
                transaction_date TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (customer_id)
                    REFERENCES customers(id)
                    ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                business_name TEXT NOT NULL DEFAULT 'Mobilya İşletmesi',
                phone TEXT,
                address TEXT
            )
            """
        )

        connection.commit()

    except sqlite3.Error as error:
        connection.rollback()
        raise RuntimeError(
            f"Veritabanı tabloları oluşturulurken hata oluştu: {error}"
        ) from error

    finally:
        connection.close()


def create_default_admin() -> None:
  

    connection = get_connection()

    try:
        cursor = connection.cursor()

        existing_user = cursor.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            ("admin",),
        ).fetchone()

        if existing_user is not None:
            return

        password_hash = bcrypt.hashpw(
            "1234".encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            ("admin", password_hash),
        )

        connection.commit()

    except sqlite3.Error as error:
        connection.rollback()
        raise RuntimeError(
            f"Admin kullanıcısı oluşturulurken hata oluştu: {error}"
        ) from error

    finally:
        connection.close()


def create_default_settings() -> None:
   

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO settings (
                id,
                business_name,
                phone,
                address
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                1,
                "Mobilya İşletmesi",
                "",
                "",
            ),
        )

        connection.commit()

    except sqlite3.Error as error:
        connection.rollback()
        raise RuntimeError(
            f"İşletme ayarları oluşturulurken hata oluştu: {error}"
        ) from error

    finally:
        connection.close()


def initialize_database() -> None:
   
    create_tables()
    create_default_admin()
    create_default_settings()


def fetch_one(
    query: str,
    parameters: tuple = (),
) -> Optional[sqlite3.Row]:
   

    connection = get_connection()

    try:
        cursor = connection.execute(query, parameters)
        return cursor.fetchone()

    finally:
        connection.close()


def fetch_all(
    query: str,
    parameters: tuple = (),
) -> list[sqlite3.Row]:
 
    connection = get_connection()

    try:
        cursor = connection.execute(query, parameters)
        return cursor.fetchall()

    finally:
        connection.close()


def execute_query(
    query: str,
    parameters: tuple = (),
) -> int:
   

    connection = get_connection()

    try:
        cursor = connection.execute(query, parameters)
        connection.commit()

        return cursor.lastrowid

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()