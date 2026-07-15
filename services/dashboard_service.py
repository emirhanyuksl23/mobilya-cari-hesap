from datetime import datetime

from database import fetch_all, fetch_one


def get_dashboard_summary() -> dict:
    """
    Ana sayfada gösterilecek özet bilgileri getirir.
    """

    customer_result = fetch_one(
        """
        SELECT COUNT(*) AS total_customer
        FROM customers
        """
    )

    transaction_result = fetch_one(
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

    today = datetime.now().strftime("%Y-%m-%d")

    today_payment_result = fetch_one(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS today_payment
        FROM transactions
        WHERE
            transaction_type = 'Ödeme'
            AND transaction_date = ?
        """,
        (today,),
    )

    total_customer = 0

    if customer_result is not None:
        total_customer = int(
            customer_result["total_customer"]
        )

    total_debt = 0.0
    total_payment = 0.0
    total_discount = 0.0
    total_return = 0.0

    if transaction_result is not None:
        total_debt = float(
            transaction_result["total_debt"]
        )
        total_payment = float(
            transaction_result["total_payment"]
        )
        total_discount = float(
            transaction_result["total_discount"]
        )
        total_return = float(
            transaction_result["total_return"]
        )

    today_payment = 0.0

    if today_payment_result is not None:
        today_payment = float(
            today_payment_result["today_payment"]
        )

    remaining_receivable = (
        total_debt
        - total_payment
        - total_discount
        - total_return
    )

    return {
        "total_customer": total_customer,
        "total_debt": round(total_debt, 2),
        "total_payment": round(total_payment, 2),
        "total_discount": round(total_discount, 2),
        "total_return": round(total_return, 2),
        "remaining_receivable": round(
            remaining_receivable,
            2,
        ),
        "today_payment": round(today_payment, 2),
    }


def get_recent_customers(
    limit: int = 5,
) -> list:
    """
    Son eklenen müşterileri getirir.
    """

    return fetch_all(
        """
        SELECT
            id,
            name,
            phone,
            created_at
        FROM customers
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    )


def get_recent_transactions(
    limit: int = 6,
) -> list:
    """
    Son cari hareketleri getirir.
    """

    return fetch_all(
        """
        SELECT
            transactions.id,
            customers.name AS customer_name,
            transactions.transaction_type,
            transactions.amount,
            transactions.transaction_date
        FROM transactions
        INNER JOIN customers
            ON customers.id = transactions.customer_id
        ORDER BY
            transactions.transaction_date DESC,
            transactions.id DESC
        LIMIT ?
        """,
        (limit,),
    )