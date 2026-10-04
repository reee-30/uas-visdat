# Jejak Wisata Nusantara

Dashboard visualisasi data pariwisata Indonesia di 38 provinsi, dibangun dengan Streamlit. Dashboard ini menjawab tiga pertanyaan: di mana kamar hotel dan wisatawan menumpuk, ke mana wisatawan bergerak, dan provinsi mana yang punya profil serupa.

**Demo:** `https://uas-visdat-pariwisata.streamlit.app`

> Proyek ini dibuat untuk tugas mata kuliah Visualisasi Data (UAS).

---

## Isi Dashboard

| Halaman | Isi | Visualisasi |
|---|---|---|
| **Beranda** | Pembuka dengan video latar dan tiga angka kunci | Hero, kartu ringkasan |
| **Explore** (Hierarki) | Sebaran kamar hotel dan lama menginap, serta asal perjalanan wisatawan nusantara menurut jenis kelamin | Treemap, Sunburst, Icicle |
| **Journey** (Flow) | Asal negara dan pintu masuk wisatawan mancanegara, serta perjalanan antarprovinsi wisatawan nusantara | Sankey, Heatmap, Chord, Batang dua arah |
| **Patterns** (Multivariat) | Pengelompokan provinsi dari 10 indikator akomodasi | Biplot PCA, Parallel Coordinates, Heatmap klaster, Klaster hierarkis (Ward) |

Fitur lain: mode gelap dan terang, filter interaktif di tiap halaman, tampilan responsif untuk desktop dan HP, serta kartu temuan yang ikut berubah mengikuti filter.

## Sumber Data

Seluruh data berasal dari **Badan Pusat Statistik (BPS)**, diakses 2 Oktober 2026:

1. Jumlah Akomodasi, Kamar, dan Tempat Tidur pada Hotel Bintang Menurut Provinsi
2. Jumlah Akomodasi, Kamar, dan Tempat Tidur pada Hotel Nonbintang dan Akomodasi Lainnya Menurut Provinsi
3. Jumlah Perjalanan Wisatawan Nusantara Menurut Provinsi Tujuan
4. Jumlah Perjalanan Wisatawan Nusantara Menurut Provinsi Asal
5. Statistik Wisatawan Nusantara 2025 (publikasi)
6. Statistik Indonesia 2026 (publikasi)

Daftar tautan lengkap tersedia di kotak **Lihat data & sumber** di bagian bawah setiap halaman.

## Struktur Proyek

```
uas-visdat/
├── app.py                  # titik masuk aplikasi
├── ui.py                   # tata letak, gaya, navigasi, beranda, mode gelap
├── requirements.txt        # daftar library
├── .streamlit/
│   └── config.toml         # pengaturan server dan tema
├── pages/
│   ├── 1_Hierarki.py       # halaman Explore
│   ├── 2_Flow.py           # halaman Journey
│   └── 3_Multivariat.py    # halaman Patterns
├── scripts/
│   ├── prepare_hierarki.py     # menyiapkan data halaman Explore
│   ├── prepare_flow.py         # menyiapkan data halaman Journey
│   └── prepare_multivariat.py  # menyiapkan data halaman Patterns
├── data/
│   ├── raw/                # data mentah (Raw_Data.xlsx, chord.csv)
│   └── processed/          # data bersih yang dibaca dashboard
└── static/                 # aset statis (video beranda)
```

Halaman di `pages/` tidak dijalankan langsung. `ui.py` memuatnya, menambahkan banner, navigasi, dan gaya yang seragam.

## Menjalankan di Komputer Sendiri

Butuh Python 3.10 atau lebih baru.

```bash
# 1. Salin repositori
git clone https://github.com/reee-30/uas-visdat.git
cd uas-visdat

# 2. (Opsional) buat virtual environment
python -m venv venv
venv\Scripts\activate          

# 3. Pasang library
pip install -r requirements.txt

# 4. Jalankan
streamlit run app.py
```

Buka `http://localhost:8501` di browser.

### Menyiapkan ulang data (opsional)

Data bersih sudah ada di `data/processed/`. Jika data mentah di `data/raw/` diperbarui, jalankan ulang skrip persiapan:

```bash
python scripts/prepare_hierarki.py
python scripts/prepare_flow.py
python scripts/prepare_multivariat.py
```

## Teknologi

- **Streamlit** sebagai kerangka aplikasi
- **Plotly** untuk treemap, sunburst, icicle, sankey, heatmap, biplot, dan parallel coordinates
- **HoloViews + Bokeh** untuk chord diagram
- **pandas, NumPy, SciPy, scikit-learn** untuk pengolahan data, PCA, dan klasterisasi

## Deploy

Aplikasi ini dideploy di [Streamlit Community Cloud](https://streamlit.io/cloud) dan tersambung ke repositori GitHub. Setiap `git push` ke branch utama akan memperbarui web secara otomatis.

## Kredit

- Data: Badan Pusat Statistik (BPS)
- Video latar: [Wonderful Indonesia : A Visual Journey](https://www.youtube.com/watch?v=ojQbArbuN4E), Pesona Indonesia (Kementerian Pariwisata), melalui YouTube. Hak cipta video dimiliki oleh pemiliknya dan digunakan di sini hanya untuk keperluan akademik.
- Font: [Outfit](https://fonts.google.com/specimen/Outfit) (Google Fonts)


| Nama | NIM |
|---|---|
|Lady Theresia Simbolon | 222313168 |