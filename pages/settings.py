import customtkinter as ctk
from tkinter import messagebox
from typing import Callable

from auth import change_password, change_username
from services.settings_service import (
    get_business_settings,
    update_business_settings,
)


class SettingsPage(ctk.CTkScrollableFrame):
    """
    İşletme, kullanıcı hesabı ve görünüm ayarlarının yönetildiği sayfa.
    """

    def __init__(
        self,
        parent,
        current_username: str,
        on_username_changed: Callable[[str], None],
    ) -> None:
        super().__init__(
            parent,
            fg_color="transparent",
        )

        self.current_username = current_username
        self.on_username_changed = on_username_changed

        self.create_widgets()
        self.load_business_settings()

    def create_widgets(self) -> None:
        """
        Ayarlar ekranındaki bütün arayüz bileşenlerini oluşturur.
        """

        self.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text="Ayarlar",
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

        self.create_business_settings_section()
        self.create_username_section()
        self.create_password_section()
        self.create_theme_section()

    def create_business_settings_section(self) -> None:
        """
        İşletme bilgileri bölümünü oluşturur.
        """

        business_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        business_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 18),
        )

        business_frame.grid_columnconfigure(0, weight=1)

        section_title = ctk.CTkLabel(
            business_frame,
            text="İşletme Bilgileri",
            font=ctk.CTkFont(
                size=20,
                weight="bold",
            ),
        )
        section_title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=25,
            pady=(22, 18),
        )

        business_name_label = ctk.CTkLabel(
            business_frame,
            text="İşletme Adı *",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        business_name_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=25,
            pady=(0, 5),
        )

        self.business_name_entry = ctk.CTkEntry(
            business_frame,
            height=42,
            placeholder_text="Mobilya işletmesinin adı",
        )
        self.business_name_entry.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=25,
            pady=(0, 14),
        )

        business_phone_label = ctk.CTkLabel(
            business_frame,
            text="İşletme Telefonu",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        business_phone_label.grid(
            row=3,
            column=0,
            sticky="w",
            padx=25,
            pady=(0, 5),
        )

        self.business_phone_entry = ctk.CTkEntry(
            business_frame,
            height=42,
            placeholder_text="Örnek: 0532 111 22 33",
        )
        self.business_phone_entry.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=25,
            pady=(0, 14),
        )

        business_address_label = ctk.CTkLabel(
            business_frame,
            text="İşletme Adresi",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        business_address_label.grid(
            row=5,
            column=0,
            sticky="w",
            padx=25,
            pady=(0, 5),
        )

        self.business_address_textbox = ctk.CTkTextbox(
            business_frame,
            height=100,
            wrap="word",
        )
        self.business_address_textbox.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=25,
            pady=(0, 16),
        )

        save_business_button = ctk.CTkButton(
            business_frame,
            text="İşletme Bilgilerini Kaydet",
            width=220,
            height=42,
            command=self.handle_save_business_settings,
        )
        save_business_button.grid(
            row=7,
            column=0,
            sticky="e",
            padx=25,
            pady=(0, 22),
        )

    def create_username_section(self) -> None:
        """
        Kullanıcı adı değiştirme bölümünü oluşturur.
        """

        username_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        username_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 18),
        )

        username_frame.grid_columnconfigure(0, weight=1)
        username_frame.grid_columnconfigure(1, weight=1)

        section_title = ctk.CTkLabel(
            username_frame,
            text="Kullanıcı Adını Değiştir",
            font=ctk.CTkFont(
                size=20,
                weight="bold",
            ),
        )
        section_title.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=25,
            pady=(22, 18),
        )

        current_username_label = ctk.CTkLabel(
            username_frame,
            text=f"Mevcut kullanıcı adı: {self.current_username}",
            text_color="gray",
        )
        current_username_label.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            padx=25,
            pady=(0, 12),
        )

        self.current_username_info_label = current_username_label

        new_username_label = ctk.CTkLabel(
            username_frame,
            text="Yeni Kullanıcı Adı",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        new_username_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=(25, 10),
            pady=(0, 5),
        )

        username_password_label = ctk.CTkLabel(
            username_frame,
            text="Mevcut Şifre",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        username_password_label.grid(
            row=2,
            column=1,
            sticky="w",
            padx=(10, 25),
            pady=(0, 5),
        )

        self.new_username_entry = ctk.CTkEntry(
            username_frame,
            height=42,
            placeholder_text="Yeni kullanıcı adı",
        )
        self.new_username_entry.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=(25, 10),
            pady=(0, 16),
        )

        self.username_password_entry = ctk.CTkEntry(
            username_frame,
            height=42,
            placeholder_text="Şifrenizi girin",
            show="*",
        )
        self.username_password_entry.grid(
            row=3,
            column=1,
            sticky="ew",
            padx=(10, 25),
            pady=(0, 16),
        )

        change_username_button = ctk.CTkButton(
            username_frame,
            text="Kullanıcı Adını Değiştir",
            width=210,
            height=42,
            command=self.handle_change_username,
        )
        change_username_button.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="e",
            padx=25,
            pady=(0, 22),
        )

    def create_password_section(self) -> None:
        """
        Şifre değiştirme bölümünü oluşturur.
        """

        password_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        password_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 18),
        )

        password_frame.grid_columnconfigure((0, 1, 2), weight=1)

        section_title = ctk.CTkLabel(
            password_frame,
            text="Şifreyi Değiştir",
            font=ctk.CTkFont(
                size=20,
                weight="bold",
            ),
        )
        section_title.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=25,
            pady=(22, 18),
        )

        old_password_label = ctk.CTkLabel(
            password_frame,
            text="Mevcut Şifre",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        old_password_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=(25, 8),
            pady=(0, 5),
        )

        new_password_label = ctk.CTkLabel(
            password_frame,
            text="Yeni Şifre",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        new_password_label.grid(
            row=1,
            column=1,
            sticky="w",
            padx=8,
            pady=(0, 5),
        )

        repeat_password_label = ctk.CTkLabel(
            password_frame,
            text="Yeni Şifre Tekrar",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        repeat_password_label.grid(
            row=1,
            column=2,
            sticky="w",
            padx=(8, 25),
            pady=(0, 5),
        )

        self.old_password_entry = ctk.CTkEntry(
            password_frame,
            height=42,
            placeholder_text="Mevcut şifre",
            show="*",
        )
        self.old_password_entry.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=(25, 8),
            pady=(0, 16),
        )

        self.new_password_entry = ctk.CTkEntry(
            password_frame,
            height=42,
            placeholder_text="En az 6 karakter",
            show="*",
        )
        self.new_password_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=8,
            pady=(0, 16),
        )

        self.repeat_password_entry = ctk.CTkEntry(
            password_frame,
            height=42,
            placeholder_text="Yeni şifreyi tekrar girin",
            show="*",
        )
        self.repeat_password_entry.grid(
            row=2,
            column=2,
            sticky="ew",
            padx=(8, 25),
            pady=(0, 16),
        )

        change_password_button = ctk.CTkButton(
            password_frame,
            text="Şifreyi Değiştir",
            width=180,
            height=42,
            command=self.handle_change_password,
        )
        change_password_button.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="e",
            padx=25,
            pady=(0, 22),
        )

    def create_theme_section(self) -> None:
        """
        Tema seçimi bölümünü oluşturur.
        """

        theme_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
        )
        theme_frame.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 30),
        )

        theme_frame.grid_columnconfigure(1, weight=1)

        section_title = ctk.CTkLabel(
            theme_frame,
            text="Görünüm",
            font=ctk.CTkFont(
                size=20,
                weight="bold",
            ),
        )
        section_title.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=25,
            pady=(22, 18),
        )

        theme_label = ctk.CTkLabel(
            theme_frame,
            text="Uygulama Teması",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
        )
        theme_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=25,
            pady=(0, 22),
        )

        self.theme_combobox = ctk.CTkComboBox(
            theme_frame,
            width=220,
            height=42,
            values=[
                "Açık",
                "Koyu",
                "Sistem",
            ],
            state="readonly",
            command=self.handle_theme_change,
        )
        self.theme_combobox.grid(
            row=1,
            column=1,
            sticky="e",
            padx=25,
            pady=(0, 22),
        )

        current_mode = ctk.get_appearance_mode()

        if current_mode == "Dark":
            self.theme_combobox.set("Koyu")
        else:
            self.theme_combobox.set("Açık")

    def load_business_settings(self) -> None:
        """
        Kayıtlı işletme bilgilerini forma yükler.
        """

        settings = get_business_settings()

        self.business_name_entry.delete(0, "end")
        self.business_name_entry.insert(
            0,
            settings["business_name"],
        )

        self.business_phone_entry.delete(0, "end")
        self.business_phone_entry.insert(
            0,
            settings["phone"],
        )

        self.business_address_textbox.delete(
            "1.0",
            "end",
        )
        self.business_address_textbox.insert(
            "1.0",
            settings["address"],
        )

    def handle_save_business_settings(self) -> None:
        """
        İşletme bilgilerini veritabanına kaydeder.
        """

        business_name = self.business_name_entry.get()
        phone = self.business_phone_entry.get()

        address = self.business_address_textbox.get(
            "1.0",
            "end-1c",
        )

        success, message = update_business_settings(
            business_name=business_name,
            phone=phone,
            address=address,
        )

        if success:
            messagebox.showinfo(
                "Başarılı",
                message,
            )
        else:
            messagebox.showerror(
                "Ayar Hatası",
                message,
            )

    def handle_change_username(self) -> None:
        """
        Kullanıcının kullanıcı adını değiştirir.
        """

        new_username = self.new_username_entry.get()
        password = self.username_password_entry.get()

        success, message = change_username(
            current_username=self.current_username,
            new_username=new_username,
            password=password,
        )

        if not success:
            messagebox.showerror(
                "Kullanıcı Adı Değiştirilemedi",
                message,
            )
            return

        self.current_username = new_username.strip()

        self.current_username_info_label.configure(
            text=f"Mevcut kullanıcı adı: {self.current_username}",
        )

        self.new_username_entry.delete(0, "end")
        self.username_password_entry.delete(0, "end")

        self.on_username_changed(
            self.current_username,
        )

        messagebox.showinfo(
            "Başarılı",
            message,
        )

    def handle_change_password(self) -> None:
        """
        Kullanıcının şifresini değiştirir.
        """

        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()
        repeat_password = self.repeat_password_entry.get()

        success, message = change_password(
            username=self.current_username,
            old_password=old_password,
            new_password=new_password,
            new_password_repeat=repeat_password,
        )

        if not success:
            messagebox.showerror(
                "Şifre Değiştirilemedi",
                message,
            )
            return

        self.old_password_entry.delete(0, "end")
        self.new_password_entry.delete(0, "end")
        self.repeat_password_entry.delete(0, "end")

        messagebox.showinfo(
            "Başarılı",
            message,
        )

    def handle_theme_change(self, selected_theme: str) -> None:
        """
        Seçilen temayı hemen uygular.
        """

        theme_map = {
            "Açık": "light",
            "Koyu": "dark",
            "Sistem": "system",
        }

        appearance_mode = theme_map.get(
            selected_theme,
            "light",
        )

        ctk.set_appearance_mode(
            appearance_mode,
        )