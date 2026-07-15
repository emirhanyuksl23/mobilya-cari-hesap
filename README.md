# 🪑 Mobilya Cari Hesap

Python, **CustomTkinter** ve **SQLite** kullanılarak geliştirilen, mobilya işletmeleri için tasarlanmış masaüstü cari hesap yönetim sistemi.

Uygulama; müşteri kayıtlarını, borçlandırma, tahsilat, indirim ve iade işlemlerini kolayca yönetebilmek amacıyla geliştirilmiştir. Tamamen yerel olarak çalışır ve internet bağlantısı gerektirmez.

---

## ✨ Özellikler

- 🔐 Güvenli kullanıcı girişi (bcrypt)
- 👤 Müşteri ekleme, düzenleme ve silme
- 🔍 Müşteri arama
- 📄 Müşteri detay ekranı
- 💰 Borçlandırma işlemleri
- 💵 Tahsilat işlemleri
- 🧾 İndirim ve iade kayıtları
- 📊 Dashboard özet ekranı
- 📑 PDF raporları
- 📗 Excel raporları
- 💾 Veritabanı yedekleme
- ♻️ Veritabanı geri yükleme
- 🌙 Açık / Koyu tema desteği
- ⚙️ Kullanıcı ve işletme ayarları

---

## 🛠 Kullanılan Teknolojiler

| Teknoloji | Açıklama |
|-----------|----------|
| Python 3.11 | Uygulama geliştirme |
| CustomTkinter | Modern masaüstü arayüz |
| SQLite | Yerel veritabanı |
| bcrypt | Şifre güvenliği |
| openpyxl | Excel raporları |
| ReportLab | PDF raporları |
| PyInstaller | EXE oluşturma |

---

## 📂 Proje Yapısı

```text
mobilya_cari
│
├── assets/
├── pages/
├── services/
│
├── auth.py
├── config.py
├── database.py
├── main.py
└── requirements.txt
```

---

## 🚀 Kurulum

Depoyu klonlayın.

```bash
git clone https://github.com/emirhanyuksl23/mobilya-cari-hesap.git
```

Proje klasörüne girin.

```bash
cd mobilya-cari-hesap
```

Gerekli paketleri yükleyin.

```bash
pip install -r requirements.txt
```

Programı çalıştırın.

```bash
python main.py
```

---

## 📦 Windows Uygulaması

Windows sürümü PyInstaller kullanılarak oluşturulmuştur.

Programın çalışabilmesi için **dist/MobilyaCari** klasörünün tamamı kullanılmalıdır.

---

## 📁 Veri Konumu

Program kullanıcı verilerini proje klasöründe saklamaz.

Veriler otomatik olarak aşağıdaki klasöre kaydedilir.

```text
Belgeler/
└── MobilyaCari/
    ├── cari.db
    ├── yedekler/
    └── raporlar/
```

Bu sayede uygulama silinse bile kullanıcı verileri korunur.

---

## 🎯 Yol Haritası

Planlanan geliştirmeler:

- 📦 Stok Takibi
- 🧾 Sipariş Yönetimi
- 🚚 Teslimat Takibi
- 👥 Çok Kullanıcılı Sistem
- ☁️ Bulut Yedekleme
- 📱 Mobil Uygulama
- 📈 Grafik ve İstatistikler

---

## 👨‍💻 Geliştirici

**Emirhan Yüksel**

GitHub

https://github.com/emirhanyuksl23

---

## 📄 Lisans

Bu proje **MIT License** altında lisanslanmıştır.

Daha fazla bilgi için **LICENSE** dosyasına bakabilirsiniz.