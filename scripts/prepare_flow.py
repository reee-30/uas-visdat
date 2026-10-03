from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# 1. WISMAN: negara asal -> pintu kedatangan
# --------------------------------------------------------------------------
# Pemetaan nama pintu mentah -> (nama bersih, provinsi, jenis pintu).
# Jenis pintu adalah klasifikasi berdasarkan nama pintu (bandara / pelabuhan
# laut / pos lintas batas darat); "Lainnya" dibiarkan terpisah.
PINTU = {
    "Ngurah Rai, Bali": ("Ngurah Rai", "Bali", "Bandara"),
    "Soekarno Hatta, Banten": ("Soekarno-Hatta", "Banten", "Bandara"),
    "Juanda, Jawa Timur": ("Juanda", "Jawa Timur", "Bandara"),
    "Kualanamu, Sumatera Utara": ("Kualanamu", "Sumatera Utara", "Bandara"),
    "Bandara Internasional Yogyakarta, DIY": ("Yogyakarta Intl.", "DI Yogyakarta", "Bandara"),
    "Bandara Internasional Lombok, NTB": ("Lombok Intl.", "Nusa Tenggara Barat", "Bandara"),
    "Halim Perdanakusuma, DK Jakarta": ("Halim Perdanakusuma", "DKI Jakarta", "Bandara"),
    "Hang Nadim, Kep. Riau": ("Hang Nadim", "Kepulauan Riau", "Bandara"),
    "Hassanudin, Sulawesi Selatan": ("Hasanuddin", "Sulawesi Selatan", "Bandara"),
    "Kertajati, Jawa Barat": ("Kertajati", "Jawa Barat", "Bandara"),
    "Minangkabau,Sumatera Barat": ("Minangkabau", "Sumatera Barat", "Bandara"),
    "Sam Ratalungi, Sulawesi Utara": ("Sam Ratulangi", "Sulawesi Utara", "Bandara"),
    "Sepinggan, Kalimantan Timur": ("Sepinggan", "Kalimantan Timur", "Bandara"),
    "Sultan Iskandar Muda, Aceh": ("Sultan Iskandar Muda", "Aceh", "Bandara"),
    "Sultan Syarif Kasim II, Riau": ("Sultan Syarif Kasim II", "Riau", "Bandara"),
    "Batam, Kepulauan Riau": ("Pelabuhan Batam", "Kepulauan Riau", "Pelabuhan laut"),
    "Dumai, Riau": ("Dumai", "Riau", "Pelabuhan laut"),
    "Tanjung Balai Karimun, Kepulauan Riau": ("Tj. Balai Karimun", "Kepulauan Riau", "Pelabuhan laut"),
    "Tanjung Benoa, Bali": ("Tanjung Benoa", "Bali", "Pelabuhan laut"),
    "Tanjung Pinang, Kepulauan Riau": ("Tanjung Pinang", "Kepulauan Riau", "Pelabuhan laut"),
    "Tanjung Uban, Kepulauan Riau": ("Tanjung Uban", "Kepulauan Riau", "Pelabuhan laut"),
    "Perbatasan Laut Sea Border": ("Perbatasan laut (lain)", "Lintas provinsi", "Pelabuhan laut"),
    "Aruk, Kalimantan Barat": ("Aruk", "Kalimantan Barat", "Pos lintas batas darat"),
    "Atambua, NTT": ("Atambua", "Nusa Tenggara Timur", "Pos lintas batas darat"),
    "Entikong, Kalimantan Barat": ("Entikong", "Kalimantan Barat", "Pos lintas batas darat"),
    "Nangga Badau, Kalimantan Barat": ("Nanga Badau", "Kalimantan Barat", "Pos lintas batas darat"),
    "Skow, Papua": ("Skouw", "Papua", "Pos lintas batas darat"),
    "Perbatasan Darat Land Border": ("Perbatasan darat (lain)", "Lintas provinsi", "Pos lintas batas darat"),
    "Lainnya Others": ("Pintu lainnya", "Lintas provinsi", "Lainnya"),
}


def bersihkan_negara(nama: str) -> str:
    nama = nama.split("/")[0].strip()
    return nama.replace("Asean", "ASEAN")


flow = pd.read_excel(RAW / "Raw_Data.xlsx", sheet_name="Flow")
total_sheet = flow.loc[flow["Asal"].isna(), "Value"].sum()  # baris total (=SUM) di dasar sheet
flow = flow.dropna(subset=["Asal", "Pintu Kedatangan"]).copy()  # buang baris total

tak_terpetakan = set(flow["Pintu Kedatangan"]) - set(PINTU)
assert not tak_terpetakan, f"Pintu belum dipetakan: {tak_terpetakan}"

flow["Negara"] = flow["Asal"].map(bersihkan_negara)
flow["Pintu"] = flow["Pintu Kedatangan"].map(lambda p: PINTU[p][0])
flow["Provinsi_Pintu"] = flow["Pintu Kedatangan"].map(lambda p: PINTU[p][1])
flow["Jenis_Pintu"] = flow["Pintu Kedatangan"].map(lambda p: PINTU[p][2])


wisman = (
    flow.groupby(["Negara", "Pintu", "Provinsi_Pintu", "Jenis_Pintu"], as_index=False)["Value"]
    .sum()
    .query("Value > 0")  # sel bernilai 0 = tidak ada kunjungan, tidak digambar sebagai aliran
    .sort_values("Value", ascending=False)
    .reset_index(drop=True)
)

assert wisman["Value"].sum() == total_sheet, "Total hasil olahan tidak sama dengan total sheet"
wisman.to_csv(OUT / "flow_wisman.csv", index=False)
print(f"[wisman] {len(wisman)} aliran | {wisman['Negara'].nunique()} negara | "
      f"{wisman['Pintu'].nunique()} pintu | total = {wisman['Value'].sum():,.0f}")

# --------------------------------------------------------------------------
# 2. WISNUS: matriks OD provinsi (untuk chord diagram)
# --------------------------------------------------------------------------
WILAYAH = {
    "Sumatera": ["Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi", "Sumatera Selatan",
                 "Bengkulu", "Lampung", "Kepulauan Bangka Belitung", "Kepulauan Riau"],
    "Jawa": ["DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur", "Banten"],
    "Bali & Nusa Tenggara": ["Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur"],
    "Kalimantan": ["Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan",
                   "Kalimantan Timur", "Kalimantan Utara"],
    "Sulawesi": ["Sulawesi Utara", "Gorontalo", "Sulawesi Tengah", "Sulawesi Selatan",
                 "Sulawesi Barat", "Sulawesi Tenggara"],
    "Maluku": ["Maluku", "Maluku Utara"],
    "Papua": ["Papua", "Papua Barat", "Papua Barat Daya", "Papua Selatan", "Papua Tengah",
              "Papua Pegunungan"],
}
PROV2WIL = {p: w for w, ps in WILAYAH.items() for p in ps}

chord = pd.read_csv(RAW / "chord.csv")
chord["Asal"] = chord["Asal"].str.strip()
chord["Tujuan"] = chord["Tujuan"].str.strip()

assert chord[["Asal", "Tujuan"]].duplicated().sum() == 0, "Ada pasangan asal-tujuan ganda"
assert chord["Value"].notna().all() and (chord["Value"] >= 0).all()
tak_terpetakan = (set(chord["Asal"]) | set(chord["Tujuan"])) - set(PROV2WIL)
assert not tak_terpetakan, f"Provinsi belum dipetakan ke wilayah: {tak_terpetakan}"

chord["Wilayah_Asal"] = chord["Asal"].map(PROV2WIL)
chord["Wilayah_Tujuan"] = chord["Tujuan"].map(PROV2WIL)
chord["Internal"] = chord["Asal"] == chord["Tujuan"]  # perjalanan di dalam provinsi sendiri
chord = chord.query("Value > 0").sort_values("Value", ascending=False)
chord.to_csv(OUT / "flow_wisnus_od.csv", index=False)

antar = chord[~chord["Internal"]]
ringkas = pd.DataFrame({
    "Internal": chord[chord["Internal"]].set_index("Asal")["Value"],
    "Keluar": antar.groupby("Asal")["Value"].sum(),
    "Masuk": antar.groupby("Tujuan")["Value"].sum(),
}).fillna(0)
ringkas["Neto"] = ringkas["Masuk"] - ringkas["Keluar"]
ringkas["Wilayah"] = ringkas.index.map(PROV2WIL)
ringkas = ringkas.rename_axis("Provinsi").reset_index().sort_values("Masuk", ascending=False)
ringkas.to_csv(OUT / "flow_wisnus_provinsi.csv", index=False)

print(f"[wisnus] {len(chord)} pasangan OD | {chord['Asal'].nunique()} provinsi | "
      f"internal = {chord.loc[chord['Internal'], 'Value'].sum() / chord['Value'].sum():.1%} dari total")
print("Selesai. Berkas tersimpan di", OUT)