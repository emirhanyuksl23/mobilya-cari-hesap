import sqlite3

from database import execute_query, fetch_one


def get_business_settings() -> dict:
    """
    Veritabanındaki işletme bilgilerini getirir.
    """

    settings = fetch_one(
        """
        SELECT
            business_name,
            phone,
            address
        FROM settings
        WHERE id = 1
        """
    )

    if settings is None:
        return {
            "business_name": "Mobilya İşletmesi",
            "phone": "",
            "address": "",
        }

    return {
        "business_name": settings["business_name"] or "",
        "phone": settings["phone"] or "",
        "address": settings["address"] or "",
    }


def update_business_settings(
    business_name: str,
    phone: str,
    address: str,
) -> tuple[bool, str]:
    """
    İşletme bilgilerini günceller.
    """

    business_name = business_name.strip()
    phone = phone.strip()
    address = address.strip()

    if not business_name:
        return False, "İşletme adı boş bırakılamaz."

    try:
        execute_query(
            """
            UPDATE settings
            SET
                business_name = ?,
                phone = ?,
                address = ?
            WHERE id = 1
            """,
            (
                business_name,
                phone,
                address,
            ),
        )

        return True, "İşletme bilgileri başarıyla kaydedildi."

    except sqlite3.Error as error:
        return False, f"Ayarlar kaydedilirken hata oluştu: {error}"