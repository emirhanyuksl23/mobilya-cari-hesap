import customtkinter as ctk
from tkinter import messagebox, ttk

from services.backup_service import (
    create_backup,
    delete_backup,
    format_file_size,
    get_backups,
    open_backup_folder,
    restore_backup,
)


class BackupPage(ctk.CTkFrame):
    """
    Veritabanı yedeklerinin yönetildiği sayfa.
    """

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            fg_color="transparent",
        )

        self.selected_backup_name: str | None = None

        self.create_widgets()
        self.load_backups()

    def create_widgets(self) -> None:
        """
        Yedekleme sayfasının arayüzünü oluşturur.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text="Yedekleme",
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

        info_frame.grid_columnconfigure(0, weight=1)

        info_title = ctk.CTkLabel(
            info_frame,
            text="Verilerinizi düzenli olarak yedekleyin",
            font=ctk.CTkFont(
                size=18,
                weight="bold",
            ),
        )
        info_title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=25,
            pady=(20, 8),
        )

        info_description = ctk.CTkLabel(
            info_frame,
            text=(
                "Yedekleme; müşterilerin, cari hareketlerin, kullanıcıların "
                "ve işletme ayarlarının kopyasını oluşturur. Yedekleri "
                "harici diske veya USB belleğe de kopyalayabilirsiniz."
            ),
            font=ctk.CTkFont(size=14),
            text_color="gray",
            justify="left",
            wraplength=800,
        )
        info_description.grid(
            row=1,
            column=0,
            sticky="w",
            padx=25,
            pady=(0, 20),
        )

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

        actions_frame.grid_columnconfigure(3, weight=1)

        create_backup_button = ctk.CTkButton(
            actions_frame,
            text="Yeni Yedek Al",
            width=150,
            height=42,
            command=self.handle_create_backup,
        )
        create_backup_button.grid(
            row=0,
            column=0,
            padx=(0, 8),
        )

        restore_backup_button = ctk.CTkButton(
            actions_frame,
            text="Yedeği Geri Yükle",
            width=170,
            height=42,
            fg_color="#d68910",
            hover_color="#b9770e",
            command=self.handle_restore_backup,
        )
        restore_backup_button.grid(
            row=0,
            column=1,
            padx=8,
        )

        open_folder_button = ctk.CTkButton(
            actions_frame,
            text="Yedek Klasörünü Aç",
            width=170,
            height=42,
            fg_color="#5d6d7e",
            hover_color="#485460",
            command=self.handle_open_backup_folder,
        )
        open_folder_button.grid(
            row=0,
            column=2,
            padx=8,
        )

        refresh_button = ctk.CTkButton(
            actions_frame,
            text="Listeyi Yenile",
            width=140,
            height=42,
            fg_color="#7f8c8d",
            hover_color="#626f70",
            command=self.load_backups,
        )
        refresh_button.grid(
            row=0,
            column=4,
        )

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
            "name",
            "date",
            "size",
        )

        self.backup_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        self.backup_table.heading(
            "name",
            text="Yedek Dosyası",
        )
        self.backup_table.heading(
            "date",
            text="Oluşturulma Tarihi",
        )
        self.backup_table.heading(
            "size",
            text="Dosya Boyutu",
        )

        self.backup_table.column(
            "name",
            width=430,
        )
        self.backup_table.column(
            "date",
            width=210,
            anchor="center",
        )
        self.backup_table.column(
            "size",
            width=150,
            anchor="center",
        )

        self.backup_table.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(15, 0),
            pady=15,
        )

        vertical_scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.backup_table.yview,
        )
        vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(0, 15),
            pady=15,
        )

        self.backup_table.configure(
            yscrollcommand=vertical_scrollbar.set,
        )

        self.backup_table.bind(
            "<<TreeviewSelect>>",
            self.handle_backup_select,
        )

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

        self.backup_count_label = ctk.CTkLabel(
            bottom_frame,
            text="Toplam yedek: 0",
            text_color="gray",
        )
        self.backup_count_label.grid(
            row=0,
            column=0,
            sticky="w",
        )

        delete_button = ctk.CTkButton(
            bottom_frame,
            text="Seçili Yedeği Sil",
            width=170,
            height=40,
            fg_color="#c0392b",
            hover_color="#922b21",
            command=self.handle_delete_backup,
        )
        delete_button.grid(
            row=0,
            column=1,
        )

    def load_backups(self) -> None:
        """
        Yedek dosyalarını tabloya yükler.
        """

        for item in self.backup_table.get_children():
            self.backup_table.delete(item)

        backups = get_backups()

        for backup in backups:
            created_at = backup["created_at"].strftime(
                "%d.%m.%Y %H:%M:%S"
            )

            file_size = format_file_size(
                backup["size_bytes"]
            )

            self.backup_table.insert(
                "",
                "end",
                values=(
                    backup["name"],
                    created_at,
                    file_size,
                ),
            )

        self.backup_count_label.configure(
            text=f"Toplam yedek: {len(backups)}",
        )

        self.selected_backup_name = None

    def handle_backup_select(self, event=None) -> None:
        """
        Tabloda seçilen yedeğin adını saklar.
        """

        selected_items = self.backup_table.selection()

        if not selected_items:
            self.selected_backup_name = None
            return

        selected_item = selected_items[0]

        values = self.backup_table.item(
            selected_item,
            "values",
        )

        if not values:
            self.selected_backup_name = None
            return

        self.selected_backup_name = str(values[0])

    def handle_create_backup(self) -> None:
        """
        Yeni veritabanı yedeği oluşturur.
        """

        success, message = create_backup()

        if success:
            messagebox.showinfo(
                "Başarılı",
                message,
            )
            self.load_backups()
        else:
            messagebox.showerror(
                "Yedekleme Hatası",
                message,
            )

    def handle_restore_backup(self) -> None:
        """
        Seçilen yedeği geri yükler.
        """

        if self.selected_backup_name is None:
            messagebox.showwarning(
                "Yedek Seçilmedi",
                "Önce geri yüklemek istediğiniz yedeği seçin.",
            )
            return

        answer = messagebox.askyesno(
            "Yedeği Geri Yükle",
            (
                f"{self.selected_backup_name} yedeğini geri yüklemek "
                "istediğinize emin misiniz?\n\n"
                "Mevcut veriler seçilen yedekteki verilerle "
                "değiştirilecektir.\n\n"
                "İşlem öncesinde mevcut verilerin güvenlik "
                "yedeği otomatik alınacaktır."
            ),
        )

        if not answer:
            return

        success, message = restore_backup(
            self.selected_backup_name,
        )

        if success:
            messagebox.showinfo(
                "Geri Yükleme Başarılı",
                message,
            )
            self.load_backups()
        else:
            messagebox.showerror(
                "Geri Yükleme Hatası",
                message,
            )

    def handle_delete_backup(self) -> None:
        """
        Seçilen yedek dosyasını siler.
        """

        if self.selected_backup_name is None:
            messagebox.showwarning(
                "Yedek Seçilmedi",
                "Önce silmek istediğiniz yedeği seçin.",
            )
            return

        answer = messagebox.askyesno(
            "Yedeği Sil",
            (
                f"{self.selected_backup_name} isimli yedeği "
                "kalıcı olarak silmek istediğinize emin misiniz?"
            ),
        )

        if not answer:
            return

        success, message = delete_backup(
            self.selected_backup_name,
        )

        if success:
            messagebox.showinfo(
                "Başarılı",
                message,
            )
            self.load_backups()
        else:
            messagebox.showerror(
                "Silme Hatası",
                message,
            )

    def handle_open_backup_folder(self) -> None:
        """
        Yedek klasörünü Dosya Gezgini'nde açar.
        """

        success, message = open_backup_folder()

        if not success:
            messagebox.showerror(
                "Klasör Açılamadı",
                message,
            )