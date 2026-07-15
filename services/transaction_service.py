import sqlite3
from datetime import datetime
from typing import Optional

from database import execute_query, fetch_all, fetch_one


TRANSACTION_TYPES = (
    "Borçlandırma",
    "Ödeme",
    "İndirim",
    "İade",
)


def parse_amount(amount_text: str) -> tuple[bool, float, str]:
    """
    Kullanıcının yazdığı tutarı sayıya dönüştürür.

    Kabul edilen örnekler:
    120000
    120000,50
    120000.50
    120.000,50
    """

    amount_text = amount_text.strip().replace(" ", "")

    if not amount_text:
        return False, 0.0, "Tutar boş bırakılamaz."

    try:
        if "," in amount_text and "." in amount_text:
            amount_text = amount_text.replace(".", "")
            amount_text = amount_text.replace(",", ".")

        elif "," in amount_text:
            amount_text = amount_text.replace(",", ".")

        amount = float(amount_text)

    except ValueError:
        return False, 0.0, "Geçerli bir tutar girin."

    if amount <= 0:
        return False, 0.0, "Tutar sıfırdan büyük olmalıdır."

    return True, round(amount, 2), ""


def parse_date(date_text: str) -> tuple[bool, str, str]:
    """
    GG.AA.YYYY tarihini YYYY-MM-DD biçimine dönüştürür.
    """

    date_text = date_text.strip()

    if not date_text:
        return False, "", "İşlem tarihi boş bırakılamaz."

    try:
        parsed_date = datetime.strptime(
            date_text,
            "%d.%m.%Y",
        )

    except ValueError:
        return False, "", "Tarih GG.AA.YYYY biçiminde olmalıdır."

    return True, parsed_date.strftime("%Y-%m-%d"), ""


def format_date_for_display(database_date: str) -> str:
    """
    YYYY-MM-DD tarihini GG.AA.YYYY biçimine dönüştürür.
    """

    try:
        parsed_date = datetime.strptime(
            database_date,
            "%Y-%m-%d",
        )
        return parsed_date.strftime("%d.%m.%Y")

    except (ValueError, TypeError):
        return database_date or ""


def get_customers_for_combobox() -> list[sqlite3.Row]:
    """
    Cari hareket formundaki müşteri seçim kutusu için
    müşterileri alfabetik olarak getirir.
    """

    return fetch_all(
        """
        SELECT
            id,
            name,
            phone
        FROM customers
        ORDER BY name COLLATE NOCASE ASC
        """
    )


def get_customer_balance(
    customer_id: int,
    excluded_transaction_id: Optional[int] = None,
) -> float:
    """
    Müşterinin kalan borcunu hesaplar.

    Borçlandırma:
        Bakiyeyi artırır.

    Ödeme, İndirim ve İade:
        Bakiyeyi azaltır.

    excluded_transaction_id verilirse düzenlenen hareket
    hesaba katılmaz.
    """

    parameters: list = [customer_id]

    excluded_condition = ""

    if excluded_transaction_id is not None:
        excluded_condition = "AND id != ?"
        parameters.append(excluded_transaction_id)

    result = fetch_one(
        f"""
        SELECT
            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = 'Borçlandırma'
                            THEN amount
                        WHEN transaction_type IN (
                            'Ödeme',
                            'İndirim',
                            'İade'
                        )
                            THEN -amount
                        ELSE 0
                    END
                ),
                0
            ) AS balance
        FROM transactions
        WHERE customer_id = ?
        {excluded_condition}
        """,
        tuple(parameters),
    )

    if result is None:
        return 0.0

    return round(float(result["balance"]), 2)


def validate_transaction(
    customer_id: int,
    transaction_type: str,
    amount_text: str,
    date_text: str,
    excluded_transaction_id: Optional[int] = None,
) -> tuple[bool, float, str, str]:
    """
    Cari hareket formundaki bilgileri doğrular.

    Başarılı sonuç:
        True, amount, database_date, ""

    Başarısız sonuç:
        False, 0, "", hata mesajı
    """

    customer = fetch_one(
        """
        SELECT id
        FROM customers
        WHERE id = ?
        """,
        (customer_id,),
    )

    if customer is None:
        return False, 0.0, "", "Seçilen müşteri bulunamadı."

    if transaction_type not in TRANSACTION_TYPES:
        return False, 0.0, "", "Geçersiz işlem türü."

    amount_success, amount, amount_message = parse_amount(
        amount_text
    )

    if not amount_success:
        return False, 0.0, "", amount_message

    date_success, database_date, date_message = parse_date(
        date_text
    )

    if not date_success:
        return False, 0.0, "", date_message

    if transaction_type in ("Ödeme", "İndirim", "İade"):
        current_balance = get_customer_balance(
            customer_id=customer_id,
            excluded_transaction_id=excluded_transaction_id,
        )

        if amount > current_balance:
            return (
                False,
                0.0,
                "",
                (
                    "Girilen tutar müşterinin mevcut borcundan fazla olamaz.\n\n"
                    f"Mevcut borç: {format_currency(current_balance)}"
                ),
            )

    return True, amount, database_date, ""


def add_transaction(
    customer_id: int,
    transaction_type: str,
    amount_text: str,
    date_text: str,
    description: str = "",
) -> tuple[bool, str]:
    """
    Yeni cari hareket ekler.
    """

    description = description.strip()

    success, amount, database_date, message = validate_transaction(
        customer_id=customer_id,
        transaction_type=transaction_type,
        amount_text=amount_text,
        date_text=date_text,
    )

    if not success:
        return False, message

    try:
        execute_query(
            """
            INSERT INTO transactions (
                customer_id,
                transaction_type,
                amount,
                description,
                transaction_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                customer_id,
                transaction_type,
                amount,
                description,
                database_date,
            ),
        )

        return True, "Cari hareket başarıyla kaydedildi."

    except sqlite3.Error as error:
        return False, f"Cari hareket kaydedilirken hata oluştu: {error}"


def get_all_transactions() -> list[sqlite3.Row]:
    """
    Bütün cari hareketleri en yeni tarih üstte olacak şekilde getirir.
    """

    return fetch_all(
        """
        SELECT
            transactions.id,
            transactions.customer_id,
            customers.name AS customer_name,
            transactions.transaction_type,
            transactions.amount,
            transactions.description,
            transactions.transaction_date,
            transactions.created_at
        FROM transactions
        INNER JOIN customers
            ON customers.id = transactions.customer_id
        ORDER BY
            transactions.transaction_date DESC,
            transactions.id DESC
        """
    )


def search_transactions(search_text: str) -> list[sqlite3.Row]:
    """
    Müşteri adı, işlem türü veya açıklama üzerinden arama yapar.
    """

    search_text = search_text.strip()

    if not search_text:
        return get_all_transactions()

    search_value = f"%{search_text}%"

    return fetch_all(
        """
        SELECT
            transactions.id,
            transactions.customer_id,
            customers.name AS customer_name,
            transactions.transaction_type,
            transactions.amount,
            transactions.description,
            transactions.transaction_date,
            transactions.created_at
        FROM transactions
        INNER JOIN customers
            ON customers.id = transactions.customer_id
        WHERE
            customers.name LIKE ?
            OR transactions.transaction_type LIKE ?
            OR transactions.description LIKE ?
        ORDER BY
            transactions.transaction_date DESC,
            transactions.id DESC
        """,
        (
            search_value,
            search_value,
            search_value,
        ),
    )


def get_transaction_by_id(
    transaction_id: int,
) -> Optional[sqlite3.Row]:
    """
    ID değerine göre tek cari hareket getirir.
    """

    return fetch_one(
        """
        SELECT
            transactions.id,
            transactions.customer_id,
            customers.name AS customer_name,
            transactions.transaction_type,
            transactions.amount,
            transactions.description,
            transactions.transaction_date
        FROM transactions
        INNER JOIN customers
            ON customers.id = transactions.customer_id
        WHERE transactions.id = ?
        """,
        (transaction_id,),
    )


def update_transaction(
    transaction_id: int,
    customer_id: int,
    transaction_type: str,
    amount_text: str,
    date_text: str,
    description: str = "",
) -> tuple[bool, str]:
    """
    Seçilen cari hareketi günceller.
    """

    existing_transaction = get_transaction_by_id(
        transaction_id
    )

    if existing_transaction is None:
        return False, "Güncellenecek cari hareket bulunamadı."

    description = description.strip()

    success, amount, database_date, message = validate_transaction(
        customer_id=customer_id,
        transaction_type=transaction_type,
        amount_text=amount_text,
        date_text=date_text,
        excluded_transaction_id=transaction_id,
    )

    if not success:
        return False, message

    try:
        execute_query(
            """
            UPDATE transactions
            SET
                customer_id = ?,
                transaction_type = ?,
                amount = ?,
                description = ?,
                transaction_date = ?
            WHERE id = ?
            """,
            (
                customer_id,
                transaction_type,
                amount,
                description,
                database_date,
                transaction_id,
            ),
        )

        return True, "Cari hareket başarıyla güncellendi."

    except sqlite3.Error as error:
        return False, f"Cari hareket güncellenirken hata oluştu: {error}"


def delete_transaction(
    transaction_id: int,
) -> tuple[bool, str]:
    """
    Seçilen cari hareketi siler.
    """

    transaction = get_transaction_by_id(
        transaction_id
    )

    if transaction is None:
        return False, "Silinecek cari hareket bulunamadı."

    try:
        execute_query(
            """
            DELETE FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        )

        return True, "Cari hareket başarıyla silindi."

    except sqlite3.Error as error:
        return False, f"Cari hareket silinirken hata oluştu: {error}"


def get_transaction_totals() -> dict:
    """
    Uygulamadaki genel cari toplamları getirir.
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
        """
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


def format_currency(amount: float) -> str:
    """
    Sayıyı Türk Lirası biçiminde gösterir.

    Örnek:
        120000 -> 120.000,00 TL
    """

    formatted = f"{amount:,.2f}"

    formatted = (
        formatted
        .replace(",", "TEMP")
        .replace(".", ",")
        .replace("TEMP", ".")
    )

    return f"{formatted} TL"