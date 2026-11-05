# Real Estate Management System (Odoo 17)

[![Odoo Version](https://img.shields.io/badge/Odoo-17.0-blue.svg)](https://www.odoo.com)
[![Python Version](https://img.shields.io/badge/Python-3.10-green.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-LGPL--3-purple.svg)](https://www.gnu.org/licenses/lgpl-3.0.html)

Modul custom enterprise untuk Odoo 17 yang dirancang untuk mengelola siklus hidup properti real estate secara end-to-end: mulai dari listing properti, penerimaan penawaran harga interaktif (*bidding*), alur status (*status bar workflow*), hingga pencetakan laporan PDF ringkasan spesifikasi properti.

---

## 📸 Demo & Screenshots

> *Ganti URL di bawah dengan screenshot/GIF rekaman layar dari browser Anda.*

| Kanban View & Filter | Detail Form & Statusbar |
|:---:|:---:|
| ![Kanban View](docs/screenshots/kanban.png) | ![Form View](docs/screenshots/form.png) |

| Wizard Popup Penawaran | Cetak Dokumen PDF (QWeb) |
|:---:|:---:|
| ![Wizard Popup](docs/screenshots/wizard.png) | ![Report PDF](docs/screenshots/report.png) |

---

## ✨ Fitur Utama (Key Highlights)

### 1. Arsitektur Data Relasional Kompleks
- **Relasi Multi-Tabel**: Integrasi `Many2one` (Tipe Properti, Pembeli, Salesperson), `Many2many` (Tag Properti berlabel warna), dan `One2many` (Daftar Penawaran Masuk).
- **Perhitungan Otomatis (`@api.depends`)**:
  - Otomatis menghitung Luas Total (`living_area + garden_area`).
  - Menentukan nominal penawaran tertinggi (*Best Offer*) secara real-time.
- **Logika UI Reaktif (`@api.onchange`)**: Centang opsi *Garden* otomatis mengisi default luas taman dan orientasi arah.
- **Validasi Data (`@api.constrains`)**: Validasi harga ekspektasi wajib bernilai positif (> 0).

### 2. Antarmuka Modern & Pengalaman Pengguna (UI/UX)
- **Kanban Board**: Pengelompokan visual kartu properti berdasarkan kategori/tipe properti.
- **Form View Lengkap**: Dilengkapi *Header Actions* (`Sold`, `Cancel`, `Reset`), tab *Notebook*, serta badge status dinamis.
- **Filter & Grouping Cepat**: Kemampuan menyaring properti yang masih tersedia dan mengelompokkan berdasarkan kodepos atau tipe.

### 3. Wizard Interaktif (`models.TransientModel`)
- Modal dialog pop-up untuk mengajukan penawaran harga secara cepat.
- Dilengkapi kalkulasi otomatis tanggal kedaluwarsa penawaran (*validity days & deadline*).
- Otomatis memperbarui status properti dan mencatat log aktivitas ke dalam Chatter.

### 4. Keamanan & Hak Akses Bertingkat (Role & Record Rules)
- **Role Agent**: Dibatasi oleh **Record Rule (`ir.rule`)** sehingga hanya dapat melihat & mengelola properti miliknya sendiri. Dilarang menghapus (*unlink*) data.
- **Role Manager**: Hak akses penuh (CRUD) ke seluruh data properti dan pengelolaan master data tipe/tag.

### 5. Audit Trail & Komunikasi (`mail.thread`)
- Integrasi Chatter untuk diskusi internal tim, log catatan (*log notes*), dan penjadwalan aktivitas/meeting.
- **Field Tracking (`tracking=True`)** untuk merekam riwayat perubahan harga, nama pembeli, dan pergantian status secara otomatis.

### 6. Pelaporan Cetak Dokumen (QWeb Report)
- Template laporan PDF resmi untuk lembar spesifikasi properti dan riwayat daftar penawaran masuk.

### 7. Integrasi Modul Invoicing & Stat Button (Enterprise Workflow)
- **Otomatisasi Tagihan (`account.move`)**: Saat properti berstatus *Sold*, sistem menyediakan tombol untuk otomatis membuat faktur tagihan pelanggan ke pembeli (komisi penjualan + biaya administrasi).
- **Smart Button (Stat Button)**: Menampilkan tautan cepat menuju faktur tagihan terkait langsung di pojok kanan atas formulir properti.

### 8. Konfigurasi Sistem Dinamis (`res.config.settings`)
- **Tab Pengaturan Real Estate**: Terintegrasi ke dalam menu *General Settings* Odoo untuk mengatur parameter global aplikasi.
- **Nilai Konfigurasi Dinamis**: Pengaturan persentase komisi agen dan biaya administrasi standar tersimpan otomatis ke `ir.config_parameter`, sehingga nilai kalkulasi invoice dapat disesuaikan tanpa mengubah kode program.

---

## 📂 Struktur Modul

```text
real_estate/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── models.py                   # Model: Property, PropertyType, PropertyTag, Offer
├── wizards/
│   ├── __init__.py
│   ├── property_offer_wizard.py    # TransientModel logika popup penawaran
│   └── property_offer_wizard_views.xml
├── views/
│   ├── views.xml                   # Kanban, Tree, Form, Search Views & Menus
│   └── templates.xml
├── security/
│   ├── security.xml                # User Groups & Row-level Record Rules (ir.rule)
│   └── ir.model.access.csv         # Table-level CRUD Access Rights
├── reports/
│   └── property_report.xml         # QWeb PDF Report Template & Action
└── README.md
```

---

## 🚀 Cara Pemasangan (Installation)

1. Pastikan server Odoo 17 dan PostgreSQL telah terpasang dan berjalan.
2. Clone repositori ini ke dalam direktori custom addons Anda:
   ```bash
   git clone https://github.com/username-anda/odoo17-real-estate-management.git custom_addons/real_estate
   ```
3. Tambahkan path folder custom addons ke dalam file `odoo.conf`:
   ```ini
   addons_path = /path/to/odoo/addons, /path/to/custom_addons
   ```
4. Update modul list dan pasang modul via CLI:
   ```bash
   python odoo-bin -c odoo.conf -i real_estate -d <nama_database>
   ```
   *Atau aktifkan Developer Mode di web Odoo &rarr; Update Apps List &rarr; Cari "Real Estate" &rarr; Klik Install.*

---

## 👨‍💻 Author
- **Mochamad Afif Solahudin**: [LinkedIn Profile](https://linkedin.com/in/mmafifss) | [GitHub](https://github.com/mmafifss)

