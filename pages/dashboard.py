import customtkinter as ctk
from tkinter import ttk

from services.dashboard_service import (
    get_dashboard_summary,
    get_recent_customers,
    get_recent_transactions,
)
from services.transaction_service import (
    format_currency,
    format_date_for_display,
)


class DashboardPage(ctk.CTkFrame):
    """
    Uygulamanın ana sayfası.

    Bu sayfada:
    - Toplam müşteri
    - Toplam alacak
    - Bugünkü tahsilat
    - Toplam tahsilat
    - Son müşteriler
    - Son cari hareketler

    gösterilir.
    """

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            fg_color="transparent",
        )

        self.create_widgets()
        self.refresh_dashboard()

    def create_widgets(self) -> None:
        """
        Ana sayfadaki bütün arayüz elemanlarını oluşturur.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        top_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        top_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(25, 15),
        )

        top_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            top_frame,
            text="Ana Sayfa",
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        refresh_button = ctk.CTkButton(
            top_frame,
            text="Yenile",
            width=100,
            height=38,
            fg_color="#5d6d7e",
            hover_color="#485460",
            command=self.refresh_dashboard,
        )
        refresh_button.grid(
            row=0,
            column=1,
            sticky="e",
        )

        self.create_summary_cards()
        self.create_recent_customers_section()
        self.create_recent_transactions_section()

    def create_summary_cards(self) -> None:
        """
        Üst bilgi kartlarını oluşturur.
        """

        cards_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        cards_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 18),
        )

        cards_frame.grid_columnconfigure(
            (0, 1, 2, 3),
            weight=1,
        )

        customer_card, self.customer_value_label = (
            self.create_info_card(
                parent=cards_frame,
                title="Toplam Müşteri",
            )
        )
        customer_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7),
        )

        receivable_card, self.receivable_value_label = (
            self.create_info_card(
                parent=cards_frame,
                title="Toplam Alacak",
            )
        )
        receivable_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=7,
        )

        today_payment_card, self.today_payment_value_label = (
            self.create_info_card(
                parent=cards_frame,
                title="Bugünkü Tahsilat",
            )
        )
        today_payment_card.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=7,
        )

        total_payment_card, self.total_payment_value_label = (
            self.create_info_card(
                parent=cards_frame,
                title="Toplam Tahsilat",
            )
        )
        total_payment_card.grid(
            row=0,
            column=3,
            sticky="nsew",
            padx=(7, 0),
        )

    def create_info_card(
        self,
        parent,
        title: str,
    ) -> tuple[ctk.CTkFrame, ctk.CTkLabel]:
        """
        Tek bir bilgi kartı oluşturur.
        """

        card = ctk.CTkFrame(
            parent,
            height=125,
            corner_radius=15,
        )

        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=15),
            text_color="gray",
        )
        title_label.grid(
            row=0,
            column=0,
            padx=15,
            pady=(22, 8),
        )

        value_label = ctk.CTkLabel(
            card,
            text="0",
            font=ctk.CTkFont(
                size=22,
                weight="bold",
            ),
        )
        value_label.grid(
            row=1,
            column=0,
            padx=15,
            pady=8,
        )

        return card, value_label

    def create_recent_customers_section(self) -> None:
        """
        Son eklenen müşteriler tablosunu oluşturur.
        """

        customers_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        customers_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 18),
        )

        customers_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            customers_frame,
            text="Son Eklenen Müşteriler",
            font=ctk.CTkFont(
                size=19,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(18, 10),
        )

        columns = (
            "name",
            "phone",
            "created_at",
        )

        self.customer_table = ttk.Treeview(
            customers_frame,
            columns=columns,
            show="headings",
            height=5,
        )

        self.customer_table.heading(
            "name",
            text="Müşteri",
        )
        self.customer_table.heading(
            "phone",
            text="Telefon",
        )
        self.customer_table.heading(
            "created_at",
            text="Kayıt Tarihi",
        )

        self.customer_table.column(
            "name",
            width=260,
        )
        self.customer_table.column(
            "phone",
            width=170,
            anchor="center",
        )
        self.customer_table.column(
            "created_at",
            width=170,
            anchor="center",
        )

        self.customer_table.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 20),
        )

    def create_recent_transactions_section(self) -> None:
        """
        Son cari hareketler tablosunu oluşturur.
        """

        transactions_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        transactions_frame.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 30),
        )

        transactions_frame.grid_columnconfigure(0, weight=1)
        transactions_frame.grid_rowconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            transactions_frame,
            text="Son Cari Hareketler",
            font=ctk.CTkFont(
                size=19,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(18, 10),
        )

        columns = (
            "customer",
            "transaction_type",
            "amount",
            "date",
        )

        self.transaction_table = ttk.Treeview(
            transactions_frame,
            columns=columns,
            show="headings",
            height=6,
        )

        self.transaction_table.heading(
            "customer",
            text="Müşteri",
        )
        self.transaction_table.heading(
            "transaction_type",
            text="İşlem Türü",
        )
        self.transaction_table.heading(
            "amount",
            text="Tutar",
        )
        self.transaction_table.heading(
            "date",
            text="Tarih",
        )

        self.transaction_table.column(
            "customer",
            width=260,
        )
        self.transaction_table.column(
            "transaction_type",
            width=170,
            anchor="center",
        )
        self.transaction_table.column(
            "amount",
            width=170,
            anchor="e",
        )
        self.transaction_table.column(
            "date",
            width=150,
            anchor="center",
        )

        self.transaction_table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(20, 0),
            pady=(0, 20),
        )

        scrollbar = ttk.Scrollbar(
            transactions_frame,
            orient="vertical",
            command=self.transaction_table.yview,
        )
        scrollbar.grid(
            row=1,
            column=1,
            sticky="ns",
            padx=(0, 20),
            pady=(0, 20),
        )

        self.transaction_table.configure(
            yscrollcommand=scrollbar.set,
        )

    def refresh_dashboard(self) -> None:
        """
        Ana sayfadaki bütün verileri yeniler.
        """

        self.load_summary()
        self.load_recent_customers()
        self.load_recent_transactions()

    def load_summary(self) -> None:
        """
        Bilgi kartlarını gerçek verilerle günceller.
        """

        summary = get_dashboard_summary()

        self.customer_value_label.configure(
            text=str(summary["total_customer"]),
        )

        self.receivable_value_label.configure(
            text=format_currency(
                summary["remaining_receivable"]
            ),
        )

        self.today_payment_value_label.configure(
            text=format_currency(
                summary["today_payment"]
            ),
        )

        self.total_payment_value_label.configure(
            text=format_currency(
                summary["total_payment"]
            ),
        )

    def load_recent_customers(self) -> None:
        """
        Son müşterileri tabloya yükler.
        """

        for item in self.customer_table.get_children():
            self.customer_table.delete(item)

        customers = get_recent_customers(limit=5)

        for customer in customers:
            created_at = customer["created_at"] or ""

            if created_at:
                created_at = created_at[:16]

            self.customer_table.insert(
                "",
                "end",
                values=(
                    customer["name"],
                    customer["phone"] or "-",
                    created_at,
                ),
            )

    def load_recent_transactions(self) -> None:
        """
        Son cari hareketleri tabloya yükler.
        """

        for item in self.transaction_table.get_children():
            self.transaction_table.delete(item)

        transactions = get_recent_transactions(limit=6)

        for transaction in transactions:
            self.transaction_table.insert(
                "",
                "end",
                values=(
                    transaction["customer_name"],
                    transaction["transaction_type"],
                    format_currency(
                        float(transaction["amount"])
                    ),
                    format_date_for_display(
                        transaction["transaction_date"]
                    ),
                ),
            )