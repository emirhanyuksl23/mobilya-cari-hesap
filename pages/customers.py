from typing import Callable

import customtkinter as ctk
from tkinter import messagebox, ttk

from services.customer_service import (
    add_customer,
    delete_customer,
    get_all_customers,
    get_customer_by_id,
    search_customers,
    update_customer,
)


class CustomersPage(ctk.CTkFrame):
    """
    Müşterilerin listelendiği ve yönetildiği sayfa.
    """

    def __init__(
        self,
        parent,
        on_customer_open: Callable[[int], None] | None = None,
    ) -> None:
        super().__init__(
            parent,
            fg_color="transparent",
        )

        self.selected_customer_id: int | None = None
        self.on_customer_open = on_customer_open

        self.create_widgets()
        self.load_customers()

    def create_widgets(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text="Müşteriler",
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

        top_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        top_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 15),
        )

        top_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            top_frame,
            height=42,
            placeholder_text="İsim, telefon veya adres ile ara...",
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
            top_frame,
            text="Yeni Müşteri Ekle",
            width=170,
            height=42,
            command=self.open_add_customer_window,
        )
        add_button.grid(
            row=0,
            column=1,
        )

        table_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        table_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 15),
        )

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        columns = (
            "id",
            "name",
            "phone",
            "address",
            "created_at",
        )

        self.customer_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self.customer_table.heading("id", text="ID")
        self.customer_table.heading("name", text="Müşteri Adı")
        self.customer_table.heading("phone", text="Telefon")
        self.customer_table.heading("address", text="Adres")
        self.customer_table.heading("created_at", text="Kayıt Tarihi")

        self.customer_table.column(
            "id",
            width=60,
            anchor="center",
            stretch=False,
        )
        self.customer_table.column(
            "name",
            width=220,
        )
        self.customer_table.column(
            "phone",
            width=150,
        )
        self.customer_table.column(
            "address",
            width=350,
        )
        self.customer_table.column(
            "created_at",
            width=160,
            anchor="center",
        )

        self.customer_table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(15, 0),
            pady=15,
        )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.customer_table.yview,
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(0, 15),
            pady=15,
        )

        self.customer_table.configure(
            yscrollcommand=scrollbar.set,
        )

        self.customer_table.bind(
            "<<TreeviewSelect>>",
            self.handle_customer_select,
        )

        self.customer_table.bind(
            "<Double-1>",
            lambda event: self.open_customer_detail(),
        )

        bottom_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        bottom_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 25),
        )

        bottom_frame.grid_columnconfigure(0, weight=1)

        self.customer_count_label = ctk.CTkLabel(
            bottom_frame,
            text="Gösterilen müşteri: 0",
            text_color="gray",
        )
        self.customer_count_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        detail_button = ctk.CTkButton(
            bottom_frame,
            text="Detay",
            width=120,
            height=40,
            command=self.open_customer_detail,
        )
        detail_button.grid(
            row=0,
            column=1,
            padx=5,
        )

        edit_button = ctk.CTkButton(
            bottom_frame,
            text="Düzenle",
            width=120,
            height=40,
            fg_color="#d68910",
            hover_color="#b9770e",
            command=self.open_edit_customer_window,
        )
        edit_button.grid(
            row=0,
            column=2,
            padx=5,
        )

        delete_button = ctk.CTkButton(
            bottom_frame,
            text="Sil",
            width=120,
            height=40,
            fg_color="#c0392b",
            hover_color="#922b21",
            command=self.handle_delete_customer,
        )
        delete_button.grid(
            row=0,
            column=3,
            padx=(5, 0),
        )

    def load_customers(self, customers=None) -> None:
        for item in self.customer_table.get_children():
            self.customer_table.delete(item)

        if customers is None:
            customers = get_all_customers()

        for customer in customers:
            created_at = customer["created_at"] or ""

            if created_at:
                created_at = created_at[:16]

            self.customer_table.insert(
                "",
                "end",
                values=(
                    customer["id"],
                    customer["name"],
                    customer["phone"] or "-",
                    customer["address"] or "-",
                    created_at,
                ),
            )

        self.customer_count_label.configure(
            text=f"Gösterilen müşteri: {len(customers)}",
        )

        self.selected_customer_id = None

    def handle_search(self) -> None:
        customers = search_customers(
            self.search_entry.get()
        )
        self.load_customers(customers)

    def handle_customer_select(self, event=None) -> None:
        selected_items = self.customer_table.selection()

        if not selected_items:
            self.selected_customer_id = None
            return

        values = self.customer_table.item(
            selected_items[0],
            "values",
        )

        if not values:
            self.selected_customer_id = None
            return

        self.selected_customer_id = int(values[0])

    def open_customer_detail(self) -> None:
        if self.selected_customer_id is None:
            messagebox.showwarning(
                "Müşteri Seçilmedi",
                "Önce detayını görmek istediğiniz müşteriyi seçin.",
            )
            return

        if self.on_customer_open is not None:
            self.on_customer_open(
                self.selected_customer_id
            )

    def open_add_customer_window(self) -> None:
        CustomerFormWindow(
            parent=self,
            window_title="Yeni Müşteri Ekle",
            on_save=self.save_new_customer,
        )

    def save_new_customer(
        self,
        name: str,
        phone: str,
        address: str,
        description: str,
    ) -> tuple[bool, str]:

        success, message = add_customer(
            name=name,
            phone=phone,
            address=address,
            description=description,
        )

        if success:
            self.search_entry.delete(0, "end")
            self.load_customers()

        return success, message

    def open_edit_customer_window(self) -> None:
        if self.selected_customer_id is None:
            messagebox.showwarning(
                "Müşteri Seçilmedi",
                "Önce düzenlemek istediğiniz müşteriyi seçin.",
            )
            return

        customer = get_customer_by_id(
            self.selected_customer_id
        )

        if customer is None:
            messagebox.showerror(
                "Hata",
                "Müşteri bulunamadı.",
            )
            self.load_customers()
            return

        customer_id = self.selected_customer_id

        CustomerFormWindow(
            parent=self,
            window_title="Müşteriyi Düzenle",
            customer=customer,
            on_save=lambda name, phone, address, description: (
                self.save_edited_customer(
                    customer_id,
                    name,
                    phone,
                    address,
                    description,
                )
            ),
        )

    def save_edited_customer(
        self,
        customer_id: int,
        name: str,
        phone: str,
        address: str,
        description: str,
    ) -> tuple[bool, str]:

        success, message = update_customer(
            customer_id=customer_id,
            name=name,
            phone=phone,
            address=address,
            description=description,
        )

        if success:
            self.search_entry.delete(0, "end")
            self.load_customers()

        return success, message

    def handle_delete_customer(self) -> None:
        if self.selected_customer_id is None:
            messagebox.showwarning(
                "Müşteri Seçilmedi",
                "Önce silmek istediğiniz müşteriyi seçin.",
            )
            return

        customer = get_customer_by_id(
            self.selected_customer_id
        )

        if customer is None:
            messagebox.showerror(
                "Hata",
                "Müşteri bulunamadı.",
            )
            return

        answer = messagebox.askyesno(
            "Müşteriyi Sil",
            (
                f"{customer['name']} isimli müşteriyi silmek "
                "istediğinize emin misiniz?\n\n"
                "Bu müşterinin bütün cari hareketleri de silinecektir."
            ),
        )

        if not answer:
            return

        success, message = delete_customer(
            self.selected_customer_id
        )

        if success:
            messagebox.showinfo(
                "Başarılı",
                message,
            )
            self.load_customers()
        else:
            messagebox.showerror(
                "Hata",
                message,
            )


class CustomerFormWindow(ctk.CTkToplevel):
    """
    Müşteri ekleme ve düzenleme penceresi.
    """

    def __init__(
        self,
        parent,
        window_title: str,
        on_save: Callable,
        customer=None,
    ) -> None:
        super().__init__(parent)

        self.on_save = on_save
        self.customer = customer
        self.window_title = window_title

        self.title(window_title)
        self.geometry("540x730")
        self.resizable(False, False)

        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self.create_widgets()

        self.after(
            150,
            self.name_entry.focus_set,
        )

    def create_widgets(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text=self.window_title,
            font=ctk.CTkFont(
                size=26,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            padx=40,
            pady=(28, 22),
        )

        self.create_label(
            text="Müşteri Adı Soyadı *",
            row=1,
        )

        self.name_entry = ctk.CTkEntry(
            self,
            width=420,
            height=44,
            placeholder_text="Örnek: Ahmet Yılmaz",
        )
        self.name_entry.grid(
            row=2,
            column=0,
            padx=60,
            pady=(0, 14),
        )

        self.create_label(
            text="Telefon",
            row=3,
        )

        self.phone_entry = ctk.CTkEntry(
            self,
            width=420,
            height=44,
            placeholder_text="Örnek: 0532 111 22 33",
        )
        self.phone_entry.grid(
            row=4,
            column=0,
            padx=60,
            pady=(0, 14),
        )

        self.create_label(
            text="Adres",
            row=5,
        )

        self.address_textbox = ctk.CTkTextbox(
            self,
            width=420,
            height=110,
            wrap="word",
        )
        self.address_textbox.grid(
            row=6,
            column=0,
            padx=60,
            pady=(0, 14),
        )

        self.create_label(
            text="Açıklama",
            row=7,
        )

        self.description_textbox = ctk.CTkTextbox(
            self,
            width=420,
            height=120,
            wrap="word",
        )
        self.description_textbox.grid(
            row=8,
            column=0,
            padx=60,
            pady=(0, 20),
        )

        button_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        button_frame.grid(
            row=9,
            column=0,
            padx=60,
            pady=(5, 30),
        )

        cancel_button = ctk.CTkButton(
            button_frame,
            text="İptal",
            width=185,
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
            width=185,
            height=44,
            command=self.handle_save,
        )
        save_button.grid(
            row=0,
            column=1,
            padx=(7, 0),
        )

        if self.customer is not None:
            self.fill_customer_data()

        self.bind(
            "<Escape>",
            lambda event: self.destroy(),
        )

    def create_label(
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

    def fill_customer_data(self) -> None:
        self.name_entry.insert(
            0,
            self.customer["name"] or "",
        )

        self.phone_entry.insert(
            0,
            self.customer["phone"] or "",
        )

        self.address_textbox.insert(
            "1.0",
            self.customer["address"] or "",
        )

        self.description_textbox.insert(
            "1.0",
            self.customer["description"] or "",
        )

    def handle_save(self) -> None:
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()

        address = self.address_textbox.get(
            "1.0",
            "end-1c",
        ).strip()

        description = self.description_textbox.get(
            "1.0",
            "end-1c",
        ).strip()

        if not name:
            messagebox.showwarning(
                "Eksik Bilgi",
                "Müşteri adı boş bırakılamaz.",
                parent=self,
            )
            return

        success, message = self.on_save(
            name,
            phone,
            address,
            description,
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
                "Hata",
                message,
                parent=self,
            )