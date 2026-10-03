from pathlib import Path
import pandas as pd

RAW = Path("data/raw/Raw_Data.xlsx")
OUT = Path("data/processed")


PULAU = {
    "Sumatera": ["Aceh", "Sumatera Utara", "Sumatera Barat", "Riau", "Jambi",
                 "Sumatera Selatan", "Bengkulu", "Lampung",
                 "Kepulauan Bangka Belitung", "Kepulauan Riau"],
    "Jawa": ["DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta",
             "Jawa Timur", "Banten"],
    "Bali & Nusa Tenggara": ["Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur"],
    "Kalimantan": ["Kalimantan Barat", "Kalimantan Tengah", "Kalimantan Selatan",
                   "Kalimantan Timur", "Kalimantan Utara"],
    "Sulawesi": ["Sulawesi Utara", "Sulawesi Tengah", "Sulawesi Selatan",
                 "Sulawesi Tenggara", "Gorontalo", "Sulawesi Barat"],
    "Maluku": ["Maluku", "Maluku Utara"],
    "Papua": ["Papua Barat", "Papua Barat Daya", "Papua", "Papua Selatan",
              "Papua Tengah", "Papua Pegunungan"],
}
PROV2PULAU = {p: k for k, v in PULAU.items() for p in v}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    geo = pd.read_excel(RAW, sheet_name="GeoNMulti")
    hier = pd.read_excel(RAW, sheet_name="Hierarki", header=None, skiprows=2).iloc[:, :5]
    hier.columns = ["Provinsi", "Bintang|Asing", "Bintang|Lokal",
                    "Nonbintang|Asing", "Nonbintang|Lokal"]
    hier["Provinsi"] = hier["Provinsi"].str.strip()
    geo["Provinsi"] = geo["Provinsi"].str.strip()

    # ---- Validasi ----
    assert set(geo["Provinsi"]) == set(hier["Provinsi"]), "Nama provinsi tidak cocok"
    assert set(geo["Provinsi"]) <= set(PROV2PULAU), "Ada provinsi belum dipetakan ke pulau"
    assert not geo.isna().any().any() and not hier.isna().any().any(), "Ada nilai kosong"

    # ---- Hierarki 1: lama menginap (long format) ----
    rows = []
    for _, r in geo.iterrows():
        h = hier.loc[hier["Provinsi"] == r["Provinsi"]].iloc[0]
        for jenis, kolom_geo in [("Bintang", "Bintang"), ("Nonbintang", "NonBintang")]:
            base = dict(
                Negara="Indonesia",
                Pulau=PROV2PULAU[r["Provinsi"]],
                Provinsi=r["Provinsi"],
                Akomodasi=jenis,
                Kamar=r[f"Kamar_{kolom_geo}"],
                UnitAkomodasi=r[f"Akomodasi_{kolom_geo}"],
                TempatTidur=r[f"TempatTidur_{kolom_geo}"],
            )
            rows.append({**base, "Asal": "Gabungan",
                         "LamaMenginap": r[f"LamaMenginap_{kolom_geo}"]})
            rows.append({**base, "Asal": "Asing", "LamaMenginap": h[f"{jenis}|Asing"]})
            rows.append({**base, "Asal": "Lokal", "LamaMenginap": h[f"{jenis}|Lokal"]})
    menginap = pd.DataFrame(rows)
    menginap.to_csv(OUT / "hierarki_menginap.csv", index=False)

    # ---- Hierarki 2: wisnus menurut jenis kelamin ----
    # Laki-laki/Perempuan berupa persentase; jumlah = persentase x JumlahWisatawanAsal
    geo["Pulau"] = geo["Provinsi"].map(PROV2PULAU)
    geo["Negara"] = "Indonesia"
    out = []
    for jk in ["Laki-laki", "Perempuan"]:
        t = geo[["Negara", "Pulau", "Provinsi", "JumlahWisatawanAsal"]].copy()
        t["JenisKelamin"] = jk
        t["Persen"] = geo[jk]
        t["Persen_LakiLaki"] = geo["Laki-laki"]
        t["Jumlah"] = (geo["JumlahWisatawanAsal"] * geo[jk] / 100).round(0)
        out.append(t)
    wisnus = pd.concat(out, ignore_index=True)
    wisnus.to_csv(OUT / "hierarki_wisnus.csv", index=False)

    print(f"hierarki_menginap.csv : {len(menginap)} baris")
    print(f"hierarki_wisnus.csv   : {len(wisnus)} baris")


if __name__ == "__main__":
    main()