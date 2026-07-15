import os

import customtkinter as ctk
from tkinter import messagebox, ttk

from config import REPORTS_DIR, create_application_directories
from services.report_service import (
    REPORT_TYPES,
    export_report_to_excel,
    export_report_to_pdf,
    generate_report,
    get_customers_for_report,
)


class ReportsPage(ctk.CTkFrame):
    """
    Raporların oluşturulduğu ve dışa aktarıldığı sayfa.
    """

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            fg_color="transparent",
        )

        self.current_headers: list[str] = []
        self.current_rows: list[list] = []
        self.current_summary: dict = {}
        self.current_report_title = ""

        self.customer_display_to_id: dict[str, int] = {}

        self.create_customer_mapping()
        self.create_widgets()
        self.handle_report_type_change(
            self.report_type_combobox.get()
        )

    def create_customer_mapping(self) -> None:
        """
        Müşteri seçim kutusu için müşteri adı-ID eşleştirmesi oluşturur.
        """

        customers = get_customers_for_report()

        for customer in customers:
            display_name = customer["name"]

            if customer["phone"]:
                display_name = (
                    f"{display_name} - {customer['phone']}"
                )

            self.customer_display_to_id[display_name] = (
                customer["id"]
            )

    def create_widgets(self) -> None:
        """
        Raporlar sayfasının arayüzünü oluşturur.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text="Raporlar",
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

        self.create_filter_area()
        self.create_info_area()
        self.create_report_table()
        self.create_bottom_area()

    def create_filter_area(self) -> None:
        """
        Rapor türü, müşteri ve tarih filtrelerini oluşturur.
        """

        filter_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        filter_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 15),
        )

        filter_frame.grid_columnconfigure(
            (0, 1, 2, 3),
            weight=1,
        )

        report_type_label = ctk.CTkLabel(
            filter_frame,
            text="Rapor Türü",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        report_type_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(20, 10),
            pady=(18, 5),
        )

        customer_label = ctk.CTkLabel(
            filter_frame,
            text="Müşteri",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        customer_label.grid(
            row=0,
            column=1,
            sticky="w",
            padx=10,
            pady=(18, 5),
        )

        start_date_label = ctk.CTkLabel(
            filter_frame,
            text="Başlangıç Tarihi",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        start_date_label.grid(
            row=0,
            column=2,
            sticky="w",
            padx=10,
            pady=(18, 5),
        )

        end_date_label = ctk.CTkLabel(
            filter_frame,
            text="Bitiş Tarihi",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        end_date_label.grid(
            row=0,
            column=3,
            sticky="w",
            padx=(10, 20),
            pady=(18, 5),
        )

        self.report_type_combobox = ctk.CTkComboBox(
            filter_frame,
            height=42,
            values=list(REPORT_TYPES),
            state="readonly",
            command=self.handle_report_type_change,
        )
        self.report_type_combobox.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(20, 10),
            pady=(0, 15),
        )
        self.report_type_combobox.set(
            "Borçlu Müşteriler"
        )

        customer_values = list(
            self.customer_display_to_id.keys()
        )

        if not customer_values:
            customer_values = ["Müşteri bulunmuyor"]

        self.customer_combobox = ctk.CTkComboBox(
            filter_frame,
            height=42,
            values=customer_values,
            state="readonly",
        )
        self.customer_combobox.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=10,
            pady=(0, 15),
        )
        self.customer_combobox.set(customer_values[0])

        self.start_date_entry = ctk.CTkEntry(
            filter_frame,
            height=42,
            placeholder_text="GG.AA.YYYY",
        )
        self.start_date_entry.grid(
            row=1,
            column=2,
            sticky="ew",
            padx=10,
            pady=(0, 15),
        )

        self.end_date_entry = ctk.CTkEntry(
            filter_frame,
            height=42,
            placeholder_text="GG.AA.YYYY",
        )
        self.end_date_entry.grid(
            row=1,
            column=3,
            sticky="ew",
            padx=(10, 20),
            pady=(0, 15),
        )

        button_frame = ctk.CTkFrame(
            filter_frame,
            fg_color="transparent",
        )
        button_frame.grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="e",
            padx=20,
            pady=(0, 18),
        )

        clear_button = ctk.CTkButton(
            button_frame,
            text="Filtreyi Temizle",
            width=145,
            height=40,
            fg_color="#7f8c8d",
            hover_color="#626f70",
            command=self.clear_filters,
        )
        clear_button.grid(
            row=0,
            column=0,
            padx=(0, 8),
        )

        show_report_button = ctk.CTkButton(
            button_frame,
            text="Raporu Göster",
            width=155,
            height=40,
            command=self.handle_generate_report,
        )
        show_report_button.grid(
            row=0,
            column=1,
        )

    def create_info_area(self) -> None:
        """
        Rapor hakkında özet bilgi gösterilecek alanı oluşturur.
        """

        self.report_info_label = ctk.CTkLabel(
            self,
            text="Henüz rapor oluşturulmadı.",
            text_color="gray",
            anchor="w",
        )
        self.report_info_label.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 10),
        )

    def create_report_table(self) -> None:
        """
        Rapor tablosunun kapsayıcı alanını oluşturur.
        """

        self.table_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        self.table_frame.grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 15),
        )

        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        self.report_table = None
        self.vertical_scrollbar = None
        self.horizontal_scrollbar = None

        self.build_table(
            ["Bilgi"],
        )

    def build_table(self, headers: list[str]) -> None:
        """
        Rapor türüne göre tablo sütunlarını yeniden oluşturur.
        """

        if self.report_table is not None:
            self.report_table.destroy()

        if self.vertical_scrollbar is not None:
            self.vertical_scrollbar.destroy()

        if self.horizontal_scrollbar is not None:
            self.horizontal_scrollbar.destroy()

        columns = [
            f"column_{index}"
            for index in range(len(headers))
        ]

        self.report_table = ttk.Treeview(
            self.table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        for index, header in enumerate(headers):
            column_name = columns[index]

            self.report_table.heading(
                column_name,
                text=header,
            )

            width = 150

            if header in (
                "Müşteri",
                "Açıklama",
                "İşlem Sonrası Bakiye",
            ):
                width = 220

            self.report_table.column(
                column_name,
                width=width,
                minwidth=100,
                anchor=(
                    "e"
                    if "Tutar" in header
                    or "Borç" in header
                    or "Ödeme" in header
                    or "Bakiye" in header
                    else "center"
                ),
            )

        self.report_table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(15, 0),
            pady=(15, 0),
        )

        self.vertical_scrollbar = ttk.Scrollbar(
            self.table_frame,
            orient="vertical",
            command=self.report_table.yview,
        )
        self.vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(0, 15),
            pady=(15, 0),
        )

        self.horizontal_scrollbar = ttk.Scrollbar(
            self.table_frame,
            orient="horizontal",
            command=self.report_table.xview,
        )
        self.horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(15, 0),
            pady=(0, 15),
        )

        self.report_table.configure(
            yscrollcommand=self.vertical_scrollbar.set,
            xscrollcommand=self.horizontal_scrollbar.set,
        )

    def create_bottom_area(self) -> None:
        """
        Dışa aktarma ve klasör açma butonlarını oluşturur.
        """

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

        self.record_count_label = ctk.CTkLabel(
            bottom_frame,
            text="Gösterilen kayıt: 0",
            text_color="gray",
        )
        self.record_count_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        open_folder_button = ctk.CTkButton(
            bottom_frame,
            text="Rapor Klasörünü Aç",
            width=165,
            height=40,
            fg_color="#5d6d7e",
            hover_color="#485460",
            command=self.open_reports_folder,
        )
        open_folder_button.grid(
            row=0,
            column=1,
            padx=5,
        )

        excel_button = ctk.CTkButton(
            bottom_frame,
            text="Excel'e Aktar",
            width=140,
            height=40,
            fg_color="#1e8449",
            hover_color="#196f3d",
            command=self.handle_export_excel,
        )
        excel_button.grid(
            row=0,
            column=2,
            padx=5,
        )

        pdf_button = ctk.CTkButton(
            bottom_frame,
            text="PDF Oluştur",
            width=140,
            height=40,
            fg_color="#b03a2e",
            hover_color="#922b21",
            command=self.handle_export_pdf,
        )
        pdf_button.grid(
            row=0,
            column=3,
            padx=(5, 0),
        )

    def handle_report_type_change(
        self,
        selected_report_type: str,
    ) -> None:
        """
        Müşteri ekstresi seçildiğinde müşteri kutusunu etkinleştirir.
        """

        if selected_report_type == "Müşteri Ekstresi":
            self.customer_combobox.configure(
                state="readonly",
            )
        else:
            self.customer_combobox.configure(
                state="disabled",
            )

    def clear_filters(self) -> None:
        """
        Rapor filtrelerini temizler.
        """

        self.report_type_combobox.set(
            "Borçlu Müşteriler"
        )

        self.start_date_entry.delete(0, "end")
        self.end_date_entry.delete(0, "end")

        self.handle_report_type_change(
            "Borçlu Müşteriler"
        )

    def handle_generate_report(self) -> None:
        """
        Seçilen filtrelere göre rapor oluşturur.
        """

        report_type = self.report_type_combobox.get()

        customer_id = None

        if report_type == "Müşteri Ekstresi":
            selected_customer = self.customer_combobox.get()

            customer_id = self.customer_display_to_id.get(
                selected_customer
            )

        success, message, headers, rows, summary = generate_report(
            report_type=report_type,
            start_date_text=self.start_date_entry.get(),
            end_date_text=self.end_date_entry.get(),
            customer_id=customer_id,
        )

        if not success:
            messagebox.showerror(
                "Rapor Oluşturulamadı",
                message,
            )
            return

        self.current_headers = headers
        self.current_rows = rows
        self.current_summary = summary
        self.current_report_title = report_type

        if report_type == "Müşteri Ekstresi":
            customer_name = summary.get(
                "customer_name",
                "",
            )

            self.current_report_title = (
                f"{customer_name} Cari Ekstresi"
            )

        self.load_report_table(
            headers,
            rows,
        )

        info_text = f"{self.current_report_title} oluşturuldu."

        if "total_payment" in summary:
            from services.transaction_service import format_currency

            info_text += (
                f" Toplam tahsilat: "
                f"{format_currency(summary['total_payment'])}"
            )

        if "remaining" in summary:
            from services.transaction_service import format_currency

            info_text += (
                f" Kalan borç: "
                f"{format_currency(summary['remaining'])}"
            )

        self.report_info_label.configure(
            text=info_text,
        )

    def load_report_table(
        self,
        headers: list[str],
        rows: list[list],
    ) -> None:
        """
        Rapor verilerini tabloya yükler.
        """

        self.build_table(headers)

        for row in rows:
            self.report_table.insert(
                "",
                "end",
                values=row,
            )

        self.record_count_label.configure(
            text=f"Gösterilen kayıt: {len(rows)}",
        )

    def handle_export_excel(self) -> None:
        """
        Oluşturulan raporu Excel'e aktarır.
        """

        if not self.current_rows:
            messagebox.showwarning(
                "Rapor Bulunamadı",
                "Önce ekranda bir rapor oluşturun.",
            )
            return

        success, message = export_report_to_excel(
            report_title=self.current_report_title,
            headers=self.current_headers,
            rows=self.current_rows,
            summary=self.current_summary,
        )

        if success:
            messagebox.showinfo(
                "Excel Raporu Hazır",
                message,
            )
        else:
            messagebox.showerror(
                "Excel Hatası",
                message,
            )

    def handle_export_pdf(self) -> None:
        """
        Oluşturulan raporu PDF'e aktarır.
        """

        if not self.current_rows:
            messagebox.showwarning(
                "Rapor Bulunamadı",
                "Önce ekranda bir rapor oluşturun.",
            )
            return

        success, message = export_report_to_pdf(
            report_title=self.current_report_title,
            headers=self.current_headers,
            rows=self.current_rows,
            summary=self.current_summary,
        )

        if success:
            messagebox.showinfo(
                "PDF Raporu Hazır",
                message,
            )
        else:
            messagebox.showerror(
                "PDF Hatası",
                message,
            )

    def open_reports_folder(self) -> None:
        """
        Windows Dosya Gezgini'nde rapor klasörünü açar.
        """

        try:
            create_application_directories()

            if os.name == "nt":
                os.startfile(REPORTS_DIR)
            else:
                messagebox.showerror(
                    "Hata",
                    "Bu işlem yalnızca Windows için hazırlandı.",
                )

        except OSError as error:
            messagebox.showerror(
                "Klasör Açılamadı",
                str(error),
            )