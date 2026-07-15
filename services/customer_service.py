import sqlite3
from typing import Optional

from database import execute_query, fetch_all, fetch_one


def add_customer(
    name: str,
    phone: str = "",
    address: str = "",
    description: str = "",
) -> tuple[bool, str]:
    """
    Yeni müşteri ekler.
    """

    name = name.strip()
    phone = phone.strip()
    address = address.strip()
    description = description.strip()

    if not name:
        return False, "Müşteri adı boş bırakılamaz."

    try:
        execute_query(
            """
            INSERT INTO customers (
                name,
                phone,
                address,
                description
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                phone,
                address,
                description,
            ),
        )

        return True, "Müşteri başarıyla eklendi."

    except sqlite3.Error as error:
        return False, f"Müşteri eklenirken hata oluştu: {error}"


def get_all_customers() -> list[sqlite3.Row]:
    """
    Bütün müşterileri getirir.
    """

    return fetch_all(
        """
        SELECT
            id,
            name,
            phone,
            address,
            description,
            created_at
        FROM customers
        ORDER BY id DESC
        """
    )


def search_customers(
    search_text: str,
) -> list[sqlite3.Row]:
    """
    Müşteri adı, telefon veya adres üzerinden arama yapar.
    """

    search_text = search_text.strip()

    if not search_text:
        return get_all_customers()

    search_value = f"%{search_text}%"

    return fetch_all(
        """
        SELECT
            id,
            name,
            phone,
            address,
            description,
            created_at
        FROM customers
        WHERE
            name LIKE ?
            OR phone LIKE ?
            OR address LIKE ?
        ORDER BY id DESC
        """,
        (
            search_value,
            search_value,
            search_value,
        ),
    )


def get_customer_by_id(
    customer_id: int,
) -> Optional[sqlite3.Row]:
    """
    ID değerine göre tek müşteri getirir.
    """

    return fetch_one(
        """
        SELECT
            id,
            name,
            phone,
            address,
            description,
            created_at
        FROM customers
        WHERE id = ?
        """,
        (customer_id,),
    )


def update_customer(
    customer_id: int,
    name: str,
    phone: str = "",
    address: str = "",
    description: str = "",
) -> tuple[bool, str]:
    """
    Müşteri bilgilerini günceller.
    """

    name = name.strip()
    phone = phone.strip()
    address = address.strip()
    description = description.strip()

    if not name:
        return False, "Müşteri adı boş bırakılamaz."

    customer = get_customer_by_id(customer_id)

    if customer is None:
        return False, "Müşteri bulunamadı."

    try:
        execute_query(
            """
            UPDATE customers
            SET
                name = ?,
                phone = ?,
                address = ?,
                description = ?
            WHERE id = ?
            """,
            (
                name,
                phone,
                address,
                description,
                customer_id,
            ),
        )

        return True, "Müşteri başarıyla güncellendi."

    except sqlite3.Error as error:
        return False, f"Müşteri güncellenirken hata oluştu: {error}"


def delete_customer(
    customer_id: int,
) -> tuple[bool, str]:
    """
    Müşteriyi ve müşteriye bağlı bütün cari hareketleri siler.
    """

    customer = get_customer_by_id(customer_id)

    if customer is None:
        return False, "Müşteri bulunamadı."

    try:
        execute_query(
            """
            DELETE FROM customers
            WHERE id = ?
            """,
            (customer_id,),
        )

        return True, "Müşteri başarıyla silindi."

    except sqlite3.Error as error:
        return False, f"Müşteri silinirken hata oluştu: {error}"


def get_customer_count() -> int:
    """
    Toplam müşteri sayısını döndürür.
    """

    result = fetch_one(
        """
        SELECT COUNT(*) AS total
        FROM customers
        """
    )

    if result is None:
        return 0

    return int(result["total"])


def get_customer_financial_summary(
    customer_id: int,
) -> dict:
    """
    Seçilen müşterinin cari hesap toplamlarını getirir.
    """

    result = fetch_one(
        """
        SELECT
            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'Borçlandırma'
                            THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS total_debt,

            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'Ödeme'
                            THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS total_payment,

            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'İndirim'
                            THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS total_discount,

            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'İade'
                            THEN amount
                        ELSE 0
                    END
                ),
                0
            ) AS total_return

        FROM transactions
        WHERE customer_id = ?
        """,
        (customer_id,),
    )

    if result is None:
        return {
            "total_debt": 0.0,
            "total_payment": 0.0,
            "total_discount": 0.0,
            "total_return": 0.0,
            "remaining": 0.0,
        }

    total_debt = float(result["total_debt"])
    total_payment = float(result["total_payment"])
    total_discount = float(result["total_discount"])
    total_return = float(result["total_return"])

    remaining = (
        total_debt
        - total_payment
        - total_discount
        - total_return
    )

    return {
        "total_debt": round(total_debt, 2),
        "total_payment": round(total_payment, 2),
        "total_discount": round(total_discount, 2),
        "total_return": round(total_return, 2),
        "remaining": round(remaining, 2),
    }


def get_customer_transactions(
    customer_id: int,
) -> list[sqlite3.Row]:
    """
    Seçilen müşterinin bütün cari hareketlerini getirir.
    """

    return fetch_all(
        """
        SELECT
            id,
            customer_id,
            transaction_type,
            amount,
            description,
            transaction_date,
            created_at
        FROM transactions
        WHERE customer_id = ?
        ORDER BY
            transaction_date DESC,
            id DESC
        """,
        (customer_id,),
    )