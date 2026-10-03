from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "Raw_Data.xlsx"
OUT = ROOT / "data" / "processed" / "multivariat_provinsi.csv"

# 10 variabel utama (PCA, klaster, heatmap, parallel coordinates)
MAIN_VARS = [
    "TPK_Bintang", "TPK_NonBintang",
    "Akomodasi_Bintang", "Akomodasi_NonBintang",
    "Kamar_Bintang", "Kamar_NonBintang",
    "TempatTidur_Bintang", "TempatTidur_NonBintang",
    "LamaMenginap_Bintang", "LamaMenginap_NonBintang",
]

def main():
    df = pd.read_excel(RAW, sheet_name=0)        
    df = df.dropna(subset=["Provinsi"])            
    df = df[["Provinsi", *MAIN_VARS]]  
    df["Provinsi"] = df["Provinsi"].str.strip()

    # ---- validasi ----
    assert df["Provinsi"].is_unique, "Ada provinsi duplikat"
    assert df.drop(columns="Provinsi").notna().all().all(), "Ada nilai kosong"
    assert (df[MAIN_VARS] >= 0).all().all(), "Ada nilai negatif"
    assert df["TPK_Bintang"].between(0, 100).all() and df["TPK_NonBintang"].between(0, 100).all()
    assert len(df) >= 34, "Unit observasi kurang dari 34"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"OK: {len(df)} provinsi, {len(MAIN_VARS)} variabel utama -> {OUT}")


if __name__ == "__main__":
    main()