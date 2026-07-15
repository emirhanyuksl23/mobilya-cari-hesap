import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from config import (
    BACKUP_DIR,
    DATABASE_PATH,
    create_application_directories,
)


def create_backup() -> tuple[bool, str]:
    """
    Mevcut veritabanının güvenli bir yedeğini oluşturur.
    """

    try:
        create_application_directories()

        if not DATABASE_PATH.exists():
            return False, "Veritabanı dosyası bulunamadı."

        backup_name = datetime.now().strftime(
            "cari_yedek_%Y-%m-%d_%H-%M-%S.db"
        )

        backup_path = BACKUP_DIR / backup_name

        source_connection = sqlite3.connect(DATABASE_PATH)
        backup_connection = sqlite3.connect(backup_path)

        try:
            source_connection.backup(backup_connection)
        finally:
            backup_connection.close()
            source_connection.close()

        return (
            True,
            f"Yedek başarıyla oluşturuldu:\n{backup_name}",
        )

    except (OSError, sqlite3.Error) as error:
        return (
            False,
            f"Yedek oluşturulurken hata oluştu: {error}",
        )


def get_backups() -> list[dict]:
    """
    Yedek klasöründeki bütün .db dosyalarını getirir.
    """

    create_application_directories()

    backups = []

    for backup_path in BACKUP_DIR.glob("*.db"):
        try:
            file_info = backup_path.stat()

            backups.append(
                {
                    "name": backup_path.name,
                    "path": backup_path,
                    "created_at": datetime.fromtimestamp(
                        file_info.st_mtime
                    ),
                    "size_bytes": file_info.st_size,
                }
            )

        except OSError:
            continue

    backups.sort(
        key=lambda backup: backup["created_at"],
        reverse=True,
    )

    return backups


def restore_backup(
    backup_name: str,
) -> tuple[bool, str]:
    """
    Seçilen yedeği aktif veritabanı olarak geri yükler.

    Geri yüklemeden önce mevcut veritabanının ayrıca
    güvenlik yedeğini oluşturur.
    """

    try:
        create_application_directories()

        safe_backup_name = Path(backup_name).name
        backup_path = BACKUP_DIR / safe_backup_name

        if not backup_path.exists():
            return False, "Seçilen yedek dosyası bulunamadı."

        if backup_path.suffix.lower() != ".db":
            return False, "Geçersiz yedek dosyası."

        if not is_valid_sqlite_database(backup_path):
            return (
                False,
                "Seçilen dosya geçerli veya sağlam bir SQLite veritabanı değil.",
            )

        # Mevcut veritabanını geri yükleme öncesi korur.
        if DATABASE_PATH.exists():
            safety_backup_name = datetime.now().strftime(
                "geri_yukleme_oncesi_%Y-%m-%d_%H-%M-%S.db"
            )

            safety_backup_path = (
                BACKUP_DIR / safety_backup_name
            )

            source_connection = sqlite3.connect(
                DATABASE_PATH
            )
            safety_connection = sqlite3.connect(
                safety_backup_path
            )

            try:
                source_connection.backup(
                    safety_connection
                )
            finally:
                safety_connection.close()
                source_connection.close()

        temporary_database_path = (
            DATABASE_PATH.parent / "cari_restore_tmp.db"
        )

        shutil.copy2(
            backup_path,
            temporary_database_path,
        )

        if not is_valid_sqlite_database(
            temporary_database_path
        ):
            temporary_database_path.unlink(
                missing_ok=True
            )

            return (
                False,
                "Yedek dosyası geri yüklenemedi.",
            )

        temporary_database_path.replace(
            DATABASE_PATH
        )

        return (
            True,
            (
                "Yedek başarıyla geri yüklendi.\n\n"
                "Verilerin tamamen yenilenmesi için uygulamayı "
                "kapatıp tekrar açın."
            ),
        )

    except (OSError, sqlite3.Error) as error:
        return (
            False,
            f"Yedek geri yüklenirken hata oluştu: {error}",
        )


def delete_backup(
    backup_name: str,
) -> tuple[bool, str]:
    """
    Seçilen yedek dosyasını kalıcı olarak siler.
    """

    try:
        safe_backup_name = Path(backup_name).name
        backup_path = BACKUP_DIR / safe_backup_name

        if not backup_path.exists():
            return False, "Silinecek yedek bulunamadı."

        if backup_path.suffix.lower() != ".db":
            return False, "Geçersiz yedek dosyası."

        backup_path.unlink()

        return True, "Yedek başarıyla silindi."

    except OSError as error:
        return (
            False,
            f"Yedek silinirken hata oluştu: {error}",
        )


def open_backup_folder() -> tuple[bool, str]:
    """
    Windows Dosya Gezgini'nde yedek klasörünü açar.
    """

    try:
        create_application_directories()

        if os.name != "nt":
            return (
                False,
                "Bu işlem yalnızca Windows için hazırlandı.",
            )

        os.startfile(BACKUP_DIR)

        return True, "Yedek klasörü açıldı."

    except OSError as error:
        return (
            False,
            f"Yedek klasörü açılamadı: {error}",
        )


def is_valid_sqlite_database(
    database_path: Path,
) -> bool:
    """
    Veritabanı dosyasının sağlamlığını kontrol eder.
    """

    try:
        connection = sqlite3.connect(database_path)

        try:
            result = connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()

            if result is None:
                return False

            return result[0] == "ok"

        finally:
            connection.close()

    except sqlite3.Error:
        return False


def format_file_size(
    size_bytes: int,
) -> str:
    """
    Dosya boyutunu okunabilir biçime dönüştürür.
    """

    size = float(size_bytes)

    if size < 1024:
        return f"{size:.0f} B"

    size /= 1024

    if size < 1024:
        return f"{size:.1f} KB"

    size /= 1024

    if size < 1024:
        return f"{size:.1f} MB"

    size /= 1024

    return f"{size:.1f} GB"