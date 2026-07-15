from typing import Callable

import customtkinter as ctk
from tkinter import messagebox, ttk

from pages.customers import CustomerFormWindow
from pages.transactions import TransactionFormWindow
from services.customer_service import (
    get_customer_by_id,
    get_customer_financial_summary,
    get_customer_transactions,
    update_customer,
)
from services.transaction_service import (
    add_transaction,
    delete_transaction,
    format_currency,
    format_date_for_display,
    get_transaction_by_id,
    update_transaction,
)


class CustomerDetailPage(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        customer_id: int,
        on_back: Callable,
    ) -> None:
        super().__init__(
            parent,
            fg_color="transparent",
        )

        self.customer_id = customer_id
        self.on_back = on_back

        self.customer = None
        self.selected_transaction_id: int | None = None

        self.create_widgets()
        self.refresh_page()

    def create_widgets(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.create_top_area()
        self.create_customer_info_area()
        self.create_summary_cards()
        self.create_actions_area()
        self.create_transactions_table()
        self.create_bottom_area()

    def create_top_area(self) -> None:
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

        top_frame.grid_columnconfigure(1, weight=1)

        back_button = ctk.CTkButton(
            top_frame,
            text="← Müşterilere Dön",
            width=155,
            height=38,
            fg_color="#5d6d7e",
            hover_color="#485460",
            command=self.on_back,
        )
        back_button.grid(
            row=0,
            column=0,
        )

        self.title_label = ctk.CTkLabel(
            top_frame,
            text="Müşteri Detayı",
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )
        self.title_label.grid(
            row=0,
            column=1,
            sticky="w",
            padx=20,
        )

        edit_button = ctk.CTkButton(
            top_frame,
            text="Müşteriyi Düzenle",
            width=165,
            height=38,
            fg_color="#d68910",
            hover_color="#b9770e",
            command=self.open_edit_customer_window,
        )
        edit_button.grid(
            row=0,
            column=2,
        )

    def create_customer_info_area(self) -> None:
        info_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        info_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 15),
        )

        info_frame.grid_columnconfigure(
            (0, 1, 2),
            weight=1,
        )

        self.name_info_label = self.create_info_item(
            info_frame,
            "Müşteri",
            0,
        )

        self.phone_info_label = self.create_info_item(
            info_frame,
            "Telefon",
            1,
        )

        self.address_info_label = self.create_info_item(
            info_frame,
            "Adres",
            2,
        )

        self.description_info_label = ctk.CTkLabel(
            info_frame,
            text="Açıklama: -",
            text_color="gray",
            wraplength=900,
            justify="left",
        )
        self.description_info_label.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="w",
            padx=22,
            pady=(0, 18),
        )

    def create_info_item(
        self,
        parent,
        title: str,
        column: int,
    ) -> ctk.CTkLabel:

        title_label = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(
                size=13,
                weight="bold",
            ),
            text_color="gray",
        )
        title_label.grid(
            row=0,
            column=column,
            sticky="w",
            padx=22,
            pady=(18, 4),
        )

        value_label = ctk.CTkLabel(
            parent,
            text="-",
            font=ctk.CTkFont(
                size=16,
                weight="bold",
            ),
            wraplength=300,
            justify="left",
        )
        value_label.grid(
            row=1,
            column=column,
            sticky="w",
            padx=22,
            pady=(0, 12),
        )

        return value_label

    def create_summary_cards(self) -> None:
        cards_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        cards_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 15),
        )

        cards_frame.grid_columnconfigure(
            (0, 1, 2, 3, 4),
            weight=1,
        )

        values = [
            ("Toplam Borç", "total_debt_label"),
            ("Toplam Ödeme", "total_payment_label"),
            ("Toplam İndirim", "total_discount_label"),
            ("Toplam İade", "total_return_label"),
            ("Kalan Borç", "remaining_label"),
        ]

        for column, (title, attribute_name) in enumerate(values):
            card, value_label = self.create_card(
                cards_frame,
                title,
            )

            card.grid(
                row=0,
                column=column,
                sticky="nsew",
                padx=5,
            )

            setattr(
                self,
                attribute_name,
                value_label,
            )

    def create_card(
        self,
        parent,
        title: str,
    ) -> tuple[ctk.CTkFrame, ctk.CTkLabel]:

        card = ctk.CTkFrame(
            parent,
            height=105,
            corner_radius=15,
        )

        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        title_label.grid(
            row=0,
            column=0,
            pady=(18, 6),
        )

        value_label = ctk.CTkLabel(
            card,
            text="0,00 TL",
            font=ctk.CTkFont(
                size=18,
                weight="bold",
            ),
        )
        value_label.grid(
            row=1,
            column=0,
        )

        return card, value_label

    def create_actions_area(self) -> None:
        actions_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        actions_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 12),
        )

        actions_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            actions_frame,
            text="Cari Hareket Geçmişi",
            font=ctk.CTkFont(
                size=20,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        add_button = ctk.CTkButton(
            actions_frame,
            text="Yeni Cari Hareket",
            width=170,
            height=40,
            command=self.open_add_transaction_window,
        )
        add_button.grid(
            row=0,
            column=1,
        )

    def create_transactions_table(self) -> None:
        table_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        table_frame.grid(
            row=4,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 15),
        )

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columns = (
            "id",
            "transaction_type",
            "amount",
            "date",
            "description",
        )

        self.transaction_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self.transaction_table.heading("id", text="ID")
        self.transaction_table.heading(
            "transaction_type",
            text="İşlem Türü",
        )
        self.transaction_table.heading("amount", text="Tutar")
        self.transaction_table.heading("date", text="Tarih")
        self.transaction_table.heading(
            "description",
            text="Açıklama",
        )

        self.transaction_table.column(
            "id",
            width=55,
            anchor="center",
            stretch=False,
        )
        self.transaction_table.column(
            "transaction_type",
            width=150,
            anchor="center",
        )
        self.transaction_table.column(
            "amount",
            width=160,
            anchor="e",
        )
        self.transaction_table.column(
            "date",
            width=130,
            anchor="center",
        )
        self.transaction_table.column(
            "description",
            width=400,
        )

        self.transaction_table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(15, 0),
            pady=15,
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.transaction_table.yview,
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(0, 15),
            pady=15,
        )

        self.transaction_table.configure(
            yscrollcommand=scrollbar.set,
        )

        self.transaction_table.bind(
            "<<TreeviewSelect>>",
            self.handle_transaction_select,
        )

        self.transaction_table.bind(
            "<Double-1>",
            lambda event: self.open_edit_transaction_window(),
        )

    def create_bottom_area(self) -> None:
        bottom_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        bottom_frame.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 25),
        )

        bottom_frame.grid_columnconfigure(0, weight=1)

        self.transaction_count_label = ctk.CTkLabel(
            bottom_frame,
            text="Toplam hareket: 0",
            text_color="gray",
        )
        self.transaction_count_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        edit_button = ctk.CTkButton(
            bottom_frame,
            text="Hareketi Düzenle",
            width=155,
            height=40,
            fg_color="#d68910",
            hover_color="#b9770e",
            command=self.open_edit_transaction_window,
        )
        edit_button.grid(
            row=0,
            column=1,
            padx=5,
        )

        delete_button = ctk.CTkButton(
            bottom_frame,
            text="Hareketi Sil",
            width=140,
            height=40,
            fg_color="#c0392b",
            hover_color="#922b21",
            command=self.handle_delete_transaction,
        )
        delete_button.grid(
            row=0,
            column=2,
            padx=(5, 0),
        )

    def refresh_page(self) -> None:
        self.load_customer()
        self.load_summary()
        self.load_transactions()

    def load_customer(self) -> None:
        self.customer = get_customer_by_id(
            self.customer_id
        )

        if self.customer is None:
            messagebox.showerror(
                "Hata",
                "Müşteri bulunamadı.",
            )
            self.on_back()
            return

        self.title_label.configure(
            text=f"Müşteri Detayı: {self.customer['name']}",
        )
        self.name_info_label.configure(
            text=self.customer["name"],
        )
        self.phone_info_label.configure(
            text=self.customer["phone"] or "-",
        )
        self.address_info_label.configure(
            text=self.customer["address"] or "-",
        )
        self.description_info_label.configure(
            text=(
                f"Açıklama: "
                f"{self.customer['description'] or '-'}"
            ),
        )

    def load_summary(self) -> None:
        summary = get_customer_financial_summary(
            self.customer_id
        )

        self.total_debt_label.configure(
            text=format_currency(summary["total_debt"]),
        )
        self.total_payment_label.configure(
            text=format_currency(summary["total_payment"]),
        )
        self.total_discount_label.configure(
            text=format_currency(summary["total_discount"]),
        )
        self.total_return_label.configure(
            text=format_currency(summary["total_return"]),
        )
        self.remaining_label.configure(
            text=format_currency(summary["remaining"]),
        )

    def load_transactions(self) -> None:
        for item in self.transaction_table.get_children():
            self.transaction_table.delete(item)

        transactions = get_customer_transactions(
            self.customer_id
        )

        for transaction in transactions:
            self.transaction_table.insert(
                "",
                "end",
                values=(
                    transaction["id"],
                    transaction["transaction_type"],
                    format_currency(
                        float(transaction["amount"])
                    ),
                    format_date_for_display(
                        transaction["transaction_date"]
                    ),
                    transaction["description"] or "-",
                ),
            )

        self.transaction_count_label.configure(
            text=f"Toplam hareket: {len(transactions)}",
        )

        self.selected_transaction_id = None

    def open_edit_customer_window(self) -> None:
        if self.customer is None:
            return

        CustomerFormWindow(
            parent=self,
            window_title="Müşteriyi Düzenle",
            customer=self.customer,
            on_save=self.save_edited_customer,
        )

    def save_edited_customer(
        self,
        name: str,
        phone: str,
        address: str,
        description: str,
    ) -> tuple[bool, str]:

        success, message = update_customer(
            customer_id=self.customer_id,
            name=name,
            phone=phone,
            address=address,
            description=description,
        )

        if success:
            self.refresh_page()

        return success, message

    def open_add_transaction_window(self) -> None:
        TransactionFormWindow(
            parent=self,
            window_title="Yeni Cari Hareket",
            on_save=self.save_new_transaction,
            fixed_customer_id=self.customer_id,
        )

    def save_new_transaction(
        self,
        customer_id: int,
        transaction_type: str,
        amount: str,
        date: str,
        description: str,
    ) -> tuple[bool, str]:

        success, message = add_transaction(
            customer_id=customer_id,
            transaction_type=transaction_type,
            amount_text=amount,
            date_text=date,
            description=description,
        )

        if success:
            self.refresh_page()

        return success, message

    def handle_transaction_select(self, event=None) -> None:
        selected_items = self.transaction_table.selection()

        if not selected_items:
            self.selected_transaction_id = None
            return

        values = self.transaction_table.item(
            selected_items[0],
            "values",
        )

        if values:
            self.selected_transaction_id = int(values[0])

    def open_edit_transaction_window(self) -> None:
        if self.selected_transaction_id is None:
            messagebox.showwarning(
                "Hareket Seçilmedi",
                "Önce düzenlemek istediğiniz hareketi seçin.",
            )
            return

        transaction = get_transaction_by_id(
            self.selected_transaction_id
        )

        if transaction is None:
            messagebox.showerror(
                "Hata",
                "Cari hareket bulunamadı.",
            )
            return

        transaction_id = self.selected_transaction_id

        TransactionFormWindow(
            parent=self,
            window_title="Cari Hareketi Düzenle",
            transaction=transaction,
            fixed_customer_id=self.customer_id,
            on_save=lambda customer_id, transaction_type, amount, date, description: (
                self.save_edited_transaction(
                    transaction_id,
                    customer_id,
                    transaction_type,
                    amount,
                    date,
                    description,
                )
            ),
        )

    def save_edited_transaction(
        self,
        transaction_id: int,
        customer_id: int,
        transaction_type: str,
        amount: str,
        date: str,
        description: str,
    ) -> tuple[bool, str]:

        success, message = update_transaction(
            transaction_id=transaction_id,
            customer_id=customer_id,
            transaction_type=transaction_type,
            amount_text=amount,
            date_text=date,
            description=description,
        )

        if success:
            self.refresh_page()

        return success, message

    def handle_delete_transaction(self) -> None:
        if self.selected_transaction_id is None:
            messagebox.showwarning(
                "Hareket Seçilmedi",
                "Önce silmek istediğiniz hareketi seçin.",
            )
            return

        transaction = get_transaction_by_id(
            self.selected_transaction_id
        )

        if transaction is None:
            return

        answer = messagebox.askyesno(
            "Cari Hareketi Sil",
            (
                f"İşlem: {transaction['transaction_type']}\n"
                f"Tutar: {format_currency(transaction['amount'])}\n\n"
                "Bu hareketi silmek istediğinize emin misiniz?"
            ),
        )

        if not answer:
            return

        success, message = delete_transaction(
            self.selected_transaction_id
        )

        if success:
            messagebox.showinfo(
                "Başarılı",
                message,
            )
            self.refresh_page()
        else:
            messagebox.showerror(
                "Hata",
                message,
            )