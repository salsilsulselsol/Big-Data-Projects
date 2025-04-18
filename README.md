# Big Data Platform Kelompok 1

# 1. Identifikasi Sumber Data

## 1) YFinance

### Isi
- **Field/Content**: YFinance menyajikan data pasar saham, keuangan perusahaan, harga saham, data historis, laporan keuangan, dan informasi terkait investasi.
- **Struktur**: Data disajikan dalam format tabular (misalnya harga saham, volume perdagangan, PE ratio, dividen, dll.) dan dapat diunduh dalam format CSV atau JSON.

### Accessibility
- **Open Access**: YFinance adalah sumber data yang bebas diakses, namun untuk penggunaan skala besar atau fitur lanjutan, beberapa pembatasan mungkin diterapkan.
- **Lisensi**: Data ini tersedia secara bebas, tetapi penggunaan dalam aplikasi komersial mungkin memerlukan izin lebih lanjut.

### Karakteristik Data
- **Usability**: Data dapat dengan mudah diekstrak menggunakan API YFinance dan sudah terstruktur dengan baik, jadi proses ekstraksi relatif mudah tanpa banyak praproses.
- **Coverage**: Data yang tersedia meliputi saham global, namun mungkin tidak mencakup pasar tertentu atau data yang sangat spesifik untuk perusahaan tertentu.
- **Reliability**: Sumber ini cukup terpercaya, dengan data yang diperbarui secara teratur. Namun, kadang ada keterlambatan kecil atau masalah teknis.
- **Quality**: Yahoo Finance adalah sumber data yang kredibel dan banyak digunakan oleh investor dan analis pasar.
- **Velocity**: Data diperbarui secara real-time untuk sebagian besar harga saham dan indeks, dengan pembaruan untuk laporan keuangan yang lebih jarang.

## 2) IDX (Bursa Efek Indonesia)

### Isi
- **Field/Content**: Laporan keuangan perusahaan yang terdaftar di Bursa Efek Indonesia (BEI) meliputi laporan laba rugi, neraca, laporan arus kas, dan catatan atas laporan keuangan.
- **Struktur**: Laporan disediakan dalam format XML, yang memudahkan ekstraksi data terstruktur.

### Accessibility
- **Open Access**: Data ini terbuka untuk umum, namun terdapat beberapa keterbatasan akses melalui API atau sistem lain yang membutuhkan otorisasi.
- **Lisensi**: Data ini biasanya tidak berlisensi khusus dan dapat digunakan untuk analisis atau publikasi.

### Karakteristik Data
- **Usability**: IDX menggunakan format XML membuat data ini agak rumit untuk diekstraksi dan mungkin memerlukan parsing lebih lanjut. Data tidak selalu "bersih" untuk analisis langsung tanpa praproses.
- **Coverage**: IDX menyediakan data untuk seluruh perusahaan publik yang terdaftar di BEI, tetapi tidak mencakup perusahaan swasta atau laporan non-finansial.
- **Reliability**: Data IDX ini dapat dipercaya karena bersumber dari laporan yang diaudit oleh otoritas yang berwenang, namun tetap tergantung pada ketepatan laporan dari masing-masing perusahaan.
- **Quality**: Kualitas data dari sumber ini sangat kredibel, karena data berasal dari laporan keuangan yang diserahkan oleh perusahaan yang terdaftar dan diaudit secara resmi.
- **Velocity**: Pada IDX data diperbarui tahunan atau kuartalan, tergantung pada siklus laporan perusahaan.

## 3) IQPLUS

### Isi
- **Field/Content**: IQPlus menyediakan berbagai artikel berita yang berfokus pada keuangan, analisis pasar, dan informasi ekonomi di Indonesia. Berita yang tersedia mencakup data pasar, laporan analisis ekonomi, serta perkembangan terbaru dalam sektor keuangan.
- **Struktur**: Biasanya disajikan dalam bentuk teks bebas, dengan tag atau kategori untuk mempermudah pencarian.

### Accessibility
- Sebagian besar berita di IQPlus bisa diakses secara gratis, tapi ada juga beberapa artikel premium yang hanya bisa dibaca oleh pengguna yang berlangganan atau memiliki akun. Selain itu, karena artikel ini memiliki hak cipta, pengguna yang ingin menggunakannya untuk keperluan bisnis atau publikasi ulang harus meminta izin terlebih dahulu.

### Karakteristik Data
- **Usability**: Secara teknis, berita yang diambil memang sudah berbentuk teks, tetapi sering kali masih perlu diolah lebih lanjut agar lebih terstruktur dan siap untuk dianalisis.
- **Coverage**: IQplus fokusnya lebih pada berita dan analisis ekonomi keuangan Indonesia, jadi tidak begitu komprehensif untuk pasar global atau sektor tertentu.
- **Reliability**: Kualitas berita di IQPlus umumnya dapat dipercaya karena berasal dari sumber yang cukup kredibel dan diperbarui secara rutin. Namun, seperti halnya dengan semua sumber berita, tetap perlu melakukan verifikasi tambahan untuk memastikan keakuratan informasi, terutama jika digunakan untuk pengambilan keputusan penting.
- **Quality**: Meskipun kredibel, kualitas berita bisa bervariasi tergantung pada jurnalis atau penulis yang menulis artikel.
- **Velocity**: IQPlus selalu memperbarui berita secara real-time, jadi informasi yang muncul biasanya sangat up-to-date. Dalam sehari, bisa ada banyak artikel baru, terutama jika ada peristiwa penting di dunia ekonomi dan bisnis.

# 2. Ingest

### **1) YFinance**
- **Tujuan**: Mengambil data historis saham dari Yahoo Finance.
- **Metode**: Baca daftar kode saham dari CSV → Ambil data historis (2014–2025) menggunakan yfinance.
- **Data yang Diambil**: Open, Close, High, Low, Volume, Adjusted Close.
- **Format Output**: JSON.
- **Manfaat**: Kompatibel untuk penyimpanan di MongoDB dan analisis lanjutan.

### **2) IDX (Indonesia Stock Exchange)**
- **Tujuan**: Mengambil laporan keuangan perusahaan dari situs IDX secara otomatis.
- **Metode**: 
  - Gunakan Selenium untuk navigasi dan download file ZIP.
  - Ekstrak file XML dari ZIP → Konversi ke JSON.
- **Data yang Diambil**: Laporan keuangan berdasarkan kode perusahaan, tahun, dan periode.
- **Format Output**: JSON, disimpan ke MongoDB.
- **Fitur Tambahan**: 
  - Penanganan error saat unduh.
  - Hapus file ZIP setelah diproses untuk hemat ruang.

### **3) IQPLUS**
- **Tujuan**: Scraping berita pasar dari situs IQPlus.
- **Metode**: 
  - Selenium untuk navigasi halaman.
  - BeautifulSoup untuk parsing HTML.
  - Ambil detail setiap berita: judul, waktu, link, tanggal, isi.
- **Data yang Diambil**: Berita pasar lengkap.
- **Format Output**: JSON, disimpan ke MongoDB.
- **Fitur Tambahan**: 
  - Hindari duplikasi data.
  - Hapus elemen tidak relevan dari artikel.

# 3. Simpan Ke MongoDB

### **1) YFINANCE**
- **Penyimpanan**: Data disimpan di database **`yfinance`** pada MongoDB, dengan satu **koleksi per perusahaan**.
- **Format**: JSON, disimpan menggunakan PyMongo (`insert_many()`).
- **Langkah-langkah**:
  1. Baca daftar saham dari CSV.
  2. Ambil data historis (2014–2025) dengan `Ticker.history()`.
  3. Konversi ke JSON dan simpan jika data tidak kosong.
- **Kendala**:
  - Durasi proses tergantung jumlah saham dan koneksi ke server Yahoo.
  - Risiko pemblokiran akibat terlalu banyak permintaan.
- **Solusi**: Gunakan `sleep` atau paralelisasi untuk efisiensi.

### **2) IDX (Indonesia Stock Exchange)**
- **Penyimpanan**: Data disimpan di MongoDB dalam direktori utama **`IDX_Financial_Data`**, dipisahkan berdasarkan **tahun**.
- **Format**: XML (instance.xbrl, Taxonomy.xsd) → dikonversi ke JSON.
- **Langkah-langkah**:
  1. Download file ZIP berisi XML.
  2. Ekstraksi → konversi ke JSON.
  3. Simpan menggunakan PyMongo.
- **Kendala**:
  - Proses lambat karena **rendering halaman dengan Selenium**.
  - Kinerja dipengaruhi oleh stabilitas jaringan dan server IDX.

### **3) IQPLUS**
- **Penyimpanan**: Berita disimpan di database **`scraping_db`**, dalam dua koleksi:  
  - `iqplus_stock_news` → Berita saham  
  - `iqplus_market_news` → Berita pasar umum
- **Format**: JSON, dengan data lengkap (judul, waktu, link, tanggal, isi).
- **Langkah-langkah**:
  1. Scrape daftar berita (judul & link).
  2. Ambil isi setiap berita.
  3. Cek duplikasi sebelum menyimpan.
  4. Simpan ke MongoDB jika belum ada.
- **Kendala**:
  - **Selenium** memperlambat proses karena harus merender halaman.
  - Durasi proses tergantung banyaknya berita, respons server, dan kestabilan jaringan.
