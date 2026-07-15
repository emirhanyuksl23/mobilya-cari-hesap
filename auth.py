import sqlite3

import bcrypt

from database import execute_query, fetch_one


def login(username: str, password: str) -> bool:
    """
    Kullanıcı adı ve şifreyi kontrol eder.

    Doğruysa True, yanlışsa False döndürür.
    """

    username = username.strip()

    if not username or not password:
        return False

    user = fetch_one(
        """
        SELECT
            id,
            username,
            password_hash
        FROM users
        WHERE username = ?
        """,
        (username,),
    )

    if user is None:
        return False

    stored_password_hash = user["password_hash"].encode("utf-8")
    entered_password = password.encode("utf-8")

    try:
        return bcrypt.checkpw(
            entered_password,
            stored_password_hash,
        )
    except ValueError:
        return False


def change_password(
    username: str,
    old_password: str,
    new_password: str,
    new_password_repeat: str,
) -> tuple[bool, str]:
    """
    Kullanıcının şifresini değiştirir.
    """

    username = username.strip()

    if not old_password:
        return False, "Mevcut şifre boş bırakılamaz."

    if not login(username, old_password):
        return False, "Mevcut şifre yanlış."

    if len(new_password) < 6:
        return False, "Yeni şifre en az 6 karakter olmalıdır."

    if new_password != new_password_repeat:
        return False, "Yeni şifreler birbiriyle eşleşmiyor."

    if old_password == new_password:
        return False, "Yeni şifre mevcut şifreyle aynı olamaz."

    try:
        new_password_hash = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        execute_query(
            """
            UPDATE users
            SET password_hash = ?
            WHERE username = ?
            """,
            (
                new_password_hash,
                username,
            ),
        )

        return True, "Şifre başarıyla değiştirildi."

    except sqlite3.Error as error:
        return False, f"Şifre değiştirilirken hata oluştu: {error}"


def change_username(
    current_username: str,
    new_username: str,
    password: str,
) -> tuple[bool, str]:
    """
    Kullanıcının kullanıcı adını değiştirir.
    """

    current_username = current_username.strip()
    new_username = new_username.strip()

    if not new_username:
        return False, "Yeni kullanıcı adı boş bırakılamaz."

    if len(new_username) < 3:
        return False, "Kullanıcı adı en az 3 karakter olmalıdır."

    if " " in new_username:
        return False, "Kullanıcı adında boşluk bulunamaz."

    if not login(current_username, password):
        return False, "Şifre yanlış."

    existing_user = fetch_one(
        """
        SELECT id
        FROM users
        WHERE username = ?
        AND username != ?
        """,
        (
            new_username,
            current_username,
        ),
    )

    if existing_user is not None:
        return False, "Bu kullanıcı adı zaten kullanılıyor."

    try:
        execute_query(
            """
            UPDATE users
            SET username = ?
            WHERE username = ?
            """,
            (
                new_username,
                current_username,
            ),
        )

        return True, "Kullanıcı adı başarıyla değiştirildi."

    except sqlite3.Error as error:
        return False, f"Kullanıcı adı değiştirilirken hata oluştu: {error}"