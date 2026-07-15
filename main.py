import customtkinter as ctk
from tkinter import messagebox

from auth import login
from config import (
    APP_NAME,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from database import initialize_database
from pages.backup import BackupPage
from pages.customer_detail import CustomerDetailPage
from pages.customers import CustomersPage
from pages.dashboard import DashboardPage
from pages.reports import ReportsPage
from pages.settings import SettingsPage
from pages.transactions import TransactionsPage


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class MobilyaCariApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title(APP_NAME)
        self.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )
        self.minsize(
            MIN_WINDOW_WIDTH,
            MIN_WINDOW_HEIGHT,
        )

        self.current_user: str | None = None

        self.show_login_page()

    def clear_window(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def show_login_page(self) -> None:
        self.clear_window()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        login_frame = ctk.CTkFrame(
            self,
            width=400,
            height=430,
            corner_radius=20,
        )
        login_frame.grid(
            row=0,
            column=0,
            padx=20,
            pady=20,
        )

        login_frame.grid_propagate(False)
        login_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            login_frame,
            text="Mobilya Cari",
            font=ctk.CTkFont(
                size=30,
                weight="bold",
            ),
        )
        title_label.grid(
            row=0,
            column=0,
            pady=(50, 10),
        )

        subtitle_label = ctk.CTkLabel(
            login_frame,
            text="Kullanıcı Girişi",
            font=ctk.CTkFont(size=18),
        )
        subtitle_label.grid(
            row=1,
            column=0,
            pady=(0, 30),
        )

        self.username_entry = ctk.CTkEntry(
            login_frame,
            width=300,
            height=45,
            placeholder_text="Kullanıcı adı",
        )
        self.username_entry.grid(
            row=2,
            column=0,
            pady=10,
        )

        self.password_entry = ctk.CTkEntry(
            login_frame,
            width=300,
            height=45,
            placeholder_text="Şifre",
            show="*",
        )
        self.password_entry.grid(
            row=3,
            column=0,
            pady=10,
        )

        login_button = ctk.CTkButton(
            login_frame,
            text="Giriş Yap",
            width=300,
            height=45,
            command=self.handle_login,
        )
        login_button.grid(
            row=4,
            column=0,
            pady=(20, 10),
        )


        self.username_entry.bind(
            "<Return>",
            lambda event: self.password_entry.focus_set(),
        )

        self.password_entry.bind(
            "<Return>",
            lambda event: self.handle_login(),
        )

        self.username_entry.focus_set()

    def handle_login(self) -> None:
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning(
                "Eksik Bilgi",
                "Kullanıcı adı ve şifre boş bırakılamaz.",
            )
            return

        if login(username, password):
            self.current_user = username
            self.show_main_layout()
        else:
            messagebox.showerror(
                "Giriş Başarısız",
                "Kullanıcı adı veya şifre yanlış.",
            )

            self.password_entry.delete(0, "end")
            self.password_entry.focus_set()

    def show_main_layout(self) -> None:
        self.clear_window()

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(8, weight=1)

        app_title = ctk.CTkLabel(
            self.sidebar,
            text="Mobilya Cari",
            font=ctk.CTkFont(
                size=24,
                weight="bold",
            ),
        )
        app_title.grid(
            row=0,
            column=0,
            padx=20,
            pady=(30, 25),
        )

        self.create_menu_button(
            "Ana Sayfa",
            1,
            self.show_dashboard,
        )
        self.create_menu_button(
            "Müşteriler",
            2,
            self.show_customers,
        )
        self.create_menu_button(
            "Cari Hareketler",
            3,
            self.show_transactions,
        )
        self.create_menu_button(
            "Raporlar",
            4,
            self.show_reports,
        )
        self.create_menu_button(
            "Yedekleme",
            5,
            self.show_backup,
        )
        self.create_menu_button(
            "Ayarlar",
            6,
            self.show_settings,
        )

        self.user_label = ctk.CTkLabel(
            self.sidebar,
            text=f"Kullanıcı: {self.current_user}",
            text_color="gray",
        )
        self.user_label.grid(
            row=9,
            column=0,
            padx=20,
            pady=(10, 5),
        )

        logout_button = ctk.CTkButton(
            self.sidebar,
            text="Çıkış Yap",
            fg_color="#c0392b",
            hover_color="#922b21",
            command=self.logout,
        )
        logout_button.grid(
            row=10,
            column=0,
            padx=20,
            pady=(5, 25),
            sticky="ew",
        )

        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="transparent",
        )
        self.content_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.content_frame.grid_columnconfigure(
            0,
            weight=1,
        )
        self.content_frame.grid_rowconfigure(
            0,
            weight=1,
        )

        self.show_dashboard()

    def create_menu_button(
        self,
        text: str,
        row: int,
        command,
    ) -> None:

        button = ctk.CTkButton(
            self.sidebar,
            text=text,
            height=42,
            corner_radius=8,
            anchor="w",
            command=command,
        )
        button.grid(
            row=row,
            column=0,
            padx=15,
            pady=6,
            sticky="ew",
        )

    def clear_content(self) -> None:
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self) -> None:
        self.clear_content()

        page = DashboardPage(
            self.content_frame
        )
        page.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

    def show_customers(self) -> None:
        self.clear_content()

        page = CustomersPage(
            parent=self.content_frame,
            on_customer_open=self.show_customer_detail,
        )
        page.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

    def show_customer_detail(
        self,
        customer_id: int,
    ) -> None:

        self.clear_content()

        page = CustomerDetailPage(
            parent=self.content_frame,
            customer_id=customer_id,
            on_back=self.show_customers,
        )
        page.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

    def show_transactions(self) -> None:
        self.clear_content()

        page = TransactionsPage(
            self.content_frame
        )
        page.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

    def show_reports(self) -> None:
        self.clear_content()

        page = ReportsPage(
            self.content_frame
        )
        page.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

    def show_backup(self) -> None:
        self.clear_content()

        page = BackupPage(
            self.content_frame
        )
        page.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

    def show_settings(self) -> None:
        self.clear_content()

        page = SettingsPage(
            parent=self.content_frame,
            current_username=self.current_user,
            on_username_changed=self.handle_username_changed,
        )
        page.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

    def handle_username_changed(
        self,
        new_username: str,
    ) -> None:

        self.current_user = new_username

        self.user_label.configure(
            text=f"Kullanıcı: {self.current_user}",
        )

    def logout(self) -> None:
        answer = messagebox.askyesno(
            "Çıkış Yap",
            "Hesaptan çıkmak istediğinize emin misiniz?",
        )

        if answer:
            self.current_user = None
            self.show_login_page()


def main() -> None:
    try:
        initialize_database()

        application = MobilyaCariApp()
        application.mainloop()

    except Exception as error:
        messagebox.showerror(
            "Program Hatası",
            f"Program başlatılamadı:\n{error}",
        )


if __name__ == "__main__":
    main()