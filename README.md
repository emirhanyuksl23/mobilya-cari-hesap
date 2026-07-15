# 🪑 Mobilya Cari Hesap

Profesyonel mobilya işletmeleri için geliştirilen, Python tabanlı masaüstü cari hesap yönetim sistemi.

Bu uygulama sayesinde müşterilerin borç, tahsilat, indirim ve iade işlemleri kolayca takip edilebilir. Program tamamen yerel olarak çalışır ve internet bağlantısı gerektirmez.

---

# ✨ Özellikler

## 🔐 Güvenli Giriş

- Kullanıcı adı ve şifre ile giriş
- Şifrelerin bcrypt ile hashlenerek saklanması
- Kullanıcı bilgilerini değiştirebilme

---

## 👤 Müşteri Yönetimi

- Yeni müşteri ekleme
- Müşteri bilgilerini düzenleme
- Müşteri silme
- Telefon ile arama
- Müşteri detay ekranı

---

## 💰 Cari Hesap İşlemleri

Desteklenen işlemler:

- Borçlandırma
- Tahsilat
- İndirim
- İade

### Ek Özellikler

- Otomatik kalan borç hesaplama
- Türk Lirası para formatı
- Hareket düzenleme
- Hareket silme
- Tarihe göre kayıt

---

## 📊 Dashboard

Ana ekranda;

- Toplam müşteri sayısı
- Toplam alacak
- Toplam tahsilat
- Günlük tahsilat
- Son cari hareketler

anlık olarak görüntülenebilir.

---

## 📄 Raporlar

Program aşağıdaki raporları oluşturabilir.

- Borçlu müşteriler
- Borcu kapanan müşteriler
- Cari hareket listesi
- Tahsilat raporu
- Müşteri ekstresi

Desteklenen çıktı formatları

- PDF
- Excel (.xlsx)

---

## 💾 Veritabanı Yedekleme

- Tek tıkla yedek alma
- Yedek listeleme
- Yedek geri yükleme
- Güvenlik amacıyla geri yükleme öncesi otomatik yedek oluşturma

---

## ⚙️ Ayarlar

- İşletme bilgileri
- Kullanıcı adı değiştirme
- Şifre değiştirme
- Açık / Koyu tema

---

# 🛠 Kullanılan Teknolojiler

- Python 3.11
- CustomTkinter
- SQLite
- bcrypt
- openpyxl
- ReportLab
- PyInstaller

---

# 📂 Proje Yapısı

```text
mobilya_cari/
│
├── assets/
│
├── pages/
│   ├── dashboard.py
│   ├── customers.py
│   ├── customer_detail.py
│   ├── transactions.py
│   ├── reports.py
│   ├── backup.py
│   └── settings.py
│
├── services/
│   ├── customer_service.py
│   ├── transaction_service.py
│   ├── dashboard_service.py
│   ├── report_service.py
│   ├── backup_service.py
│   └── settings_service.py
│
├── auth.py
├── config.py
├── database.py
├── main.py
└── requirements.txt
```

---

# 🚀 Kurulum

Projeyi bilgisayarınıza indirin.

```bash
git clone https://github.com/emirhanyuksl23/mobilya-cari-hesap.git
```

Klasöre girin.

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

# 📦 Windows EXE Oluşturma

```bash
pip install pyinstaller
```

Ardından

```bash
pyinstaller --noconfirm --clean --onedir --windowed --name MobilyaCari main.py
```

oluşan uygulama

```text
dist/
    MobilyaCari/
        MobilyaCari.exe
```

klasöründedir.

---

# 💻 Sistem Gereksinimleri

- Windows 10 / 11
- Python 3.11+
- Yaklaşık 100 MB boş disk alanı

---

# 📁 Verilerin Saklandığı Konum

Program verileri proje klasöründe tutulmaz.

Windows üzerinde otomatik olarak

```text
Belgeler/
    MobilyaCari/
```

klasörü oluşturulur.

Bu klasör içerisinde

```text
cari.db
yedekler/
raporlar/
```

bulunur.

Bu sayede program silinse bile kullanıcı verileri korunur.

---

# 🎯 Gelecek Sürümler

Planlanan özellikler

- 📦 Stok Takibi
- 🛒 Sipariş Yönetimi
- 🚚 Teslimat Takibi
- 👥 Çok Kullanıcılı Sistem
- 🌐 Ağ Üzerinden Kullanım
- ☁️ Bulut Yedekleme
- 📱 Mobil Uygulama
- 📈 Grafik ve İstatistikler

---

# 👨‍💻 Geliştirici

**Emirhan Yüksel**

GitHub

https://github.com/emirhanyuksl23

---

# 📌 Proje Durumu

✅ Aktif olarak geliştirilmektedir.

Yeni özellikler düzenli olarak eklenecektir.

---

# 📄 Lisans

Bu proje **MIT License** altında lisanslanmıştır.

Ayrıntılar için proje dizinindeki **LICENSE** dosyasına bakabilirsiniz.