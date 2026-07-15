from datetime import datetime
from typing import Callable

import customtkinter as ctk
from tkinter import messagebox, ttk

from services.transaction_service import (
    TRANSACTION_TYPES,
    add_transaction,
    delete_transaction,
    format_currency,
    format_date_for_display,
    get_all_transactions,
    get_customers_for_combobox,
    get_transaction_by_id,
    get_transaction_totals,
    search_transactions,
    update_transaction,
)


class TransactionsPage(ctk.CTkFrame):
    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            fg_color="transparent",
        )

        self.selected_transaction_id: int | None = None

        self.create_widgets()
        self.refresh_page()

    def create_widgets(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text="Cari Hareketler",
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=30,
            pady=(25, 15),
        )

        self.create_summary_cards()
        self.create_action_area()
        self.create_transaction_table()
        self.create_bottom_area()

    def create_summary_cards(self) -> None:
        cards_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        cards_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 20),
        )

        cards_frame.grid_columnconfigure(
            (0, 1, 2),
            weight=1,
        )

        debt_card, self.total_debt_label = self.create_info_card(
            cards_frame,
            "Toplam Borçlandırma",
        )
        debt_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )

        payment_card, self.total_payment_label = self.create_info_card(
            cards_frame,
            "Toplam Tahsilat",
        )
        payment_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=8,
        )

        remaining_card, self.remaining_label = self.create_info_card(
            cards_frame,
            "Kalan Alacak",
        )
        remaining_card.grid(
            row=0,
            column=2,
            sticky="nsew",
            padx=(8, 0),
        )

    def create_info_card(
        self,
        parent,
        title: str,
    ) -> tuple[ctk.CTkFrame, ctk.CTkLabel]:

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
            pady=(22, 8),
        )

        value_label = ctk.CTkLabel(
            card,
            text="0,00 TL",
            font=ctk.CTkFont(
                size=24,
                weight="bold",
            ),
        )
        value_label.grid(
            row=1,
            column=0,
            pady=8,
        )

        return card, value_label

    def create_action_area(self) -> None:
        actions_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        actions_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 15),
        )

        actions_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            actions_frame,
            height=42,
            placeholder_text="Müşteri, işlem türü veya açıklama ile ara...",
        )
        self.search_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 10),
        )

        self.search_entry.bind(
            "<KeyRelease>",
            lambda event: self.handle_search(),
        )

        add_button = ctk.CTkButton(
            actions_frame,
            text="Yeni Cari Hareket",
            width=175,
            height=42,
            command=self.open_add_transaction_window,
        )
        add_button.grid(
            row=0,
            column=1,
        )

    def create_transaction_table(self) -> None:
        table_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        table_frame.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 15),
        )

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columns = (
            "id",
            "customer",
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
        self.transaction_table.heading("customer", text="Müşteri")
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
            "customer",
            width=200,
        )
        self.transaction_table.column(
            "transaction_type",
            width=130,
            anchor="center",
        )
        self.transaction_table.column(
            "amount",
            width=140,
            anchor="e",
        )
        self.transaction_table.column(
            "date",
            width=120,
            anchor="center",
        )
        self.transaction_table.column(
            "description",
            width=300,
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
            row=4,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 25),
        )

        bottom_frame.grid_columnconfigure(0, weight=1)

        self.transaction_count_label = ctk.CTkLabel(
            bottom_frame,
            text="Gösterilen hareket: 0",
            text_color="gray",
        )
        self.transaction_count_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        edit_button = ctk.CTkButton(
            bottom_frame,
            text="Düzenle",
            width=120,
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
            text="Sil",
            width=120,
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
        self.search_entry.delete(0, "end")
        self.load_transactions()
        self.load_summary_cards()

    def load_transactions(self, transactions=None) -> None:
        for item in self.transaction_table.get_children():
            self.transaction_table.delete(item)

        if transactions is None:
            transactions = get_all_transactions()

        for transaction in transactions:
            self.transaction_table.insert(
                "",
                "end",
                values=(
                    transaction["id"],
                    transaction["customer_name"],
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
            text=f"Gösterilen hareket: {len(transactions)}",
        )

        self.selected_transaction_id = None

    def load_summary_cards(self) -> None:
        totals = get_transaction_totals()

        self.total_debt_label.configure(
            text=format_currency(totals["total_debt"]),
        )
        self.total_payment_label.configure(
            text=format_currency(totals["total_payment"]),
        )
        self.remaining_label.configure(
            text=format_currency(totals["remaining"]),
        )

    def handle_search(self) -> None:
        transactions = search_transactions(
            self.search_entry.get()
        )
        self.load_transactions(transactions)

    def handle_transaction_select(self, event=None) -> None:
        selected_items = self.transaction_table.selection()

        if not selected_items:
            self.selected_transaction_id = None
            return

        values = self.transaction_table.item(
            selected_items[0],
            "values",
        )

        if not values:
            self.selected_transaction_id = None
            return

        self.selected_transaction_id = int(values[0])

    def open_add_transaction_window(self) -> None:
        customers = get_customers_for_combobox()

        if not customers:
            messagebox.showwarning(
                "Müşteri Bulunamadı",
                "Önce en az bir müşteri eklemelisiniz.",
            )
            return

        TransactionFormWindow(
            parent=self,
            window_title="Yeni Cari Hareket",
            on_save=self.save_new_transaction,
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
            messagebox.showerror(
                "Hata",
                "Cari hareket bulunamadı.",
            )
            return

        answer = messagebox.askyesno(
            "Cari Hareketi Sil",
            (
                f"Müşteri: {transaction['customer_name']}\n"
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


class TransactionFormWindow(ctk.CTkToplevel):
    def __init__(
        self,
        parent,
        window_title: str,
        on_save: Callable,
        transaction=None,
        fixed_customer_id: int | None = None,
    ) -> None:
        super().__init__(parent)

        self.on_save = on_save
        self.transaction = transaction
        self.fixed_customer_id = fixed_customer_id

        self.customers = get_customers_for_combobox()
        self.customer_name_to_id: dict[str, int] = {}

        self.title(window_title)
        self.geometry("550x690")
        self.resizable(False, False)

        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self.create_customer_mapping()
        self.create_widgets()

        if self.transaction is not None:
            self.fill_transaction_data()

    def create_customer_mapping(self) -> None:
        for customer in self.customers:
            display_name = customer["name"]

            if customer["phone"]:
                display_name += f" - {customer['phone']}"

            self.customer_name_to_id[display_name] = customer["id"]

    def create_widgets(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text=self.title(),
            font=ctk.CTkFont(
                size=26,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            pady=(28, 22),
        )

        self.create_field_label("Müşteri *", 1)

        customer_values = list(
            self.customer_name_to_id.keys()
        )

        self.customer_combobox = ctk.CTkComboBox(
            self,
            width=430,
            height=44,
            values=customer_values,
            state="readonly",
        )
        self.customer_combobox.grid(
            row=2,
            column=0,
            pady=(0, 14),
        )

        if customer_values:
            self.customer_combobox.set(
                customer_values[0]
            )

        if self.fixed_customer_id is not None:
            for display_name, customer_id in (
                self.customer_name_to_id.items()
            ):
                if customer_id == self.fixed_customer_id:
                    self.customer_combobox.set(display_name)
                    self.customer_combobox.configure(
                        state="disabled",
                    )
                    break

        self.create_field_label("İşlem Türü *", 3)

        self.transaction_type_combobox = ctk.CTkComboBox(
            self,
            width=430,
            height=44,
            values=list(TRANSACTION_TYPES),
            state="readonly",
        )
        self.transaction_type_combobox.grid(
            row=4,
            column=0,
            pady=(0, 14),
        )
        self.transaction_type_combobox.set(
            "Borçlandırma"
        )

        self.create_field_label("Tutar *", 5)

        amount_validation = (
            self.register(
                self.allow_only_amount_characters
            ),
            "%P",
        )

        self.amount_entry = ctk.CTkEntry(
            self,
            width=430,
            height=44,
            placeholder_text="Örnek: 120.000,50",
            validate="key",
            validatecommand=amount_validation,
        )
        self.amount_entry.grid(
            row=6,
            column=0,
            pady=(0, 14),
        )

        self.amount_entry.bind(
            "<KeyRelease>",
            self.format_amount_entry,
        )

        self.create_field_label("İşlem Tarihi *", 7)

        self.date_entry = ctk.CTkEntry(
            self,
            width=430,
            height=44,
            placeholder_text="GG.AA.YYYY",
        )
        self.date_entry.grid(
            row=8,
            column=0,
            pady=(0, 14),
        )

        self.date_entry.insert(
            0,
            datetime.now().strftime("%d.%m.%Y"),
        )

        self.create_field_label("Açıklama", 9)

        self.description_textbox = ctk.CTkTextbox(
            self,
            width=430,
            height=110,
            wrap="word",
        )
        self.description_textbox.grid(
            row=10,
            column=0,
            pady=(0, 20),
        )

        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        button_frame.grid(
            row=11,
            column=0,
            pady=(5, 30),
        )

        cancel_button = ctk.CTkButton(
            button_frame,
            text="İptal",
            width=190,
            height=44,
            fg_color="#8e8e8e",
            hover_color="#707070",
            command=self.destroy,
        )
        cancel_button.grid(
            row=0,
            column=0,
            padx=(0, 7),
        )

        save_button = ctk.CTkButton(
            button_frame,
            text="Kaydet",
            width=190,
            height=44,
            command=self.handle_save,
        )
        save_button.grid(
            row=0,
            column=1,
            padx=(7, 0),
        )

        self.bind(
            "<Escape>",
            lambda event: self.destroy(),
        )

    def create_field_label(
        self,
        text: str,
        row: int,
    ) -> None:

        label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        label.grid(
            row=row,
            column=0,
            sticky="w",
            padx=60,
            pady=(0, 5),
        )

    def allow_only_amount_characters(
        self,
        proposed_value: str,
    ) -> bool:
        """
        Tutar alanında yalnızca rakam, nokta ve virgüle izin verir.
        """

        if proposed_value == "":
            return True

        allowed_characters = "0123456789.,"

        return all(
            character in allowed_characters
            for character in proposed_value
        )

    def format_amount_entry(self, event=None) -> None:
        """
        Girilen tutara otomatik binlik nokta ekler.

        Örnek:
            1200 -> 1.200
            120000 -> 120.000
            120000,50 -> 120.000,50
        """

        current_value = self.amount_entry.get()

        if not current_value:
            return

        current_value = current_value.replace(".", "")

        cleaned_value = ""
        comma_used = False

        for character in current_value:
            if character.isdigit():
                cleaned_value += character

            elif character == "," and not comma_used:
                cleaned_value += character
                comma_used = True

        if not cleaned_value:
            self.amount_entry.delete(0, "end")
            return

        if "," in cleaned_value:
            integer_part, decimal_part = cleaned_value.split(
                ",",
                1,
            )

            decimal_part = decimal_part[:2]

        else:
            integer_part = cleaned_value
            decimal_part = None

        integer_part = integer_part.lstrip("0")

        if not integer_part:
            integer_part = "0"

        try:
            formatted_integer = f"{int(integer_part):,}".replace(
                ",",
                ".",
            )
        except ValueError:
            formatted_integer = "0"

        if decimal_part is not None:
            formatted_value = (
                f"{formatted_integer},{decimal_part}"
            )
        else:
            formatted_value = formatted_integer

        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(0, formatted_value)
        self.amount_entry.icursor("end")

    def fill_transaction_data(self) -> None:
        customer_id = self.transaction["customer_id"]

        for display_name, mapped_id in (
            self.customer_name_to_id.items()
        ):
            if mapped_id == customer_id:
                self.customer_combobox.set(display_name)
                break

        self.transaction_type_combobox.set(
            self.transaction["transaction_type"]
        )

        amount = float(self.transaction["amount"])

        formatted_amount = f"{amount:,.2f}"

        formatted_amount = (
            formatted_amount
            .replace(",", "TEMP")
            .replace(".", ",")
            .replace("TEMP", ".")
        )

        if formatted_amount.endswith(",00"):
            formatted_amount = formatted_amount[:-3]

        self.amount_entry.delete(0, "end")
        self.amount_entry.insert(
            0,
            formatted_amount,
        )

        self.date_entry.delete(0, "end")
        self.date_entry.insert(
            0,
            format_date_for_display(
                self.transaction["transaction_date"]
            ),
        )

        self.description_textbox.insert(
            "1.0",
            self.transaction["description"] or "",
        )

    def handle_save(self) -> None:
        selected_customer = self.customer_combobox.get()

        customer_id = self.customer_name_to_id.get(
            selected_customer
        )

        if customer_id is None:
            messagebox.showwarning(
                "Eksik Bilgi",
                "Geçerli bir müşteri seçin.",
                parent=self,
            )
            return

        success, message = self.on_save(
            customer_id,
            self.transaction_type_combobox.get(),
            self.amount_entry.get(),
            self.date_entry.get(),
            self.description_textbox.get(
                "1.0",
                "end-1c",
            ).strip(),
        )

        if success:
            messagebox.showinfo(
                "Başarılı",
                message,
                parent=self,
            )
            self.destroy()
        else:
            messagebox.showerror(
                "Kayıt Hatası",
                message,
                parent=self,
            )