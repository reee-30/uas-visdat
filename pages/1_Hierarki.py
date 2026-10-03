import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Hierarki - Pariwisata", layout="wide")

TINGGI = 540
FONT = "Outfit, Source Sans Pro, Segoe UI, Arial, sans-serif"
TEAL_GELAP, TEKS, TEKS_REDUP = "#0B4F4A", "#12302D", "#4E6B67"


PAL_MENGINAP = ["#FFF1B8", "#FDC85C", "#F28C38", "#C8402F", "#6E1F3F"]     
PAL_LAKI = ["#FFE98A", "#8FD694", "#27B1A5", "#2F76C0", "#2B2F7E"]          
PAL_PEREMPUAN = ["#FFE98A", "#FFB066", "#F2686B", "#C23A92", "#59227F"]     
NBIN = 5  # 

NAMA_LEVEL = {"Negara": "Negara", "Pulau": "Kelompok pulau", "Provinsi": "Provinsi"}
URUT_LEVEL = ["Negara", "Pulau", "Provinsi"]

OPSI = ["Rata-rata lama menginap", "Wisatawan nusantara menurut jenis kelamin"]
UKURAN_BENTUK = {"Treemap": "Luas kotak", "Sunburst": "Lebar irisan", "Icicle": "Lebar balok"}


def deskripsi(nama, c):
    return (f"{UKURAN_BENTUK[nama]} menunjukkan {c['luas']}; warna menunjukkan {c['warna_txt']}. "
            "Klik untuk masuk ke tingkat di bawahnya, klik tingkat atas untuk kembali.")


BENTUK = {
    "Treemap": "Kotak bersarang: makin luas sebuah kotak, makin besar nilainya.",
    "Sunburst": "Lingkaran berlapis dari pusat ke tepi: makin lebar sebuah irisan, makin besar nilainya.",
    "Icicle": "Balok bertingkat dari atas ke bawah: makin lebar sebuah balok, makin besar nilainya.",
}
BENTUK = {"Treemap": go.Treemap, "Sunburst": go.Sunburst, "Icicle": go.Icicle}
# Tanpa toolbar dan zoom-scroll: kotak grafik tidak bisa digeser atau digulir, hanya bisa diklik.
CONFIG_PLOT = {"displayModeBar": False, "scrollZoom": False, "doubleClick": False, "responsive": True}


def cfg_menginap():
    return dict(
        jenis="menginap", file="data/processed/hierarki_menginap.csv",
        leaf="Akomodasi", leaf_label="Jenis akomodasi",
        size="Kamar", color="LamaMenginap", bobot="Kamar",
        rentang=(1, 4), palet=PAL_MENGINAP,
        judul_warna="Rata-rata lama menginap (malam)", satuan_tick="",
        ukuran_label="Jumlah kamar", warna_label="Rata-rata lama menginap",
        satuan_warna=" malam", fmt=".2f",
        terbesar="Kamar terbanyak", tinggi="Menginap terlama", rendah="Menginap tersingkat",
        judul_grafik="Kamar hotel dan rata-rata lama menginap",
        luas="jumlah kamar", warna_txt="rata-rata lama menginap", unit_rentang=" malam",
        views=["Treemap", "Sunburst"],
    )


def cfg_wisnus(jk):
    laki = jk == "Laki-laki"
    return dict(
        jenis="wisnus", file="data/processed/hierarki_wisnus.csv",
        leaf="JenisKelamin", leaf_label="Jenis kelamin",
        size="Jumlah", color="Persen_LakiLaki" if laki else "Persen_Perempuan", bobot="JumlahWisatawanAsal",
        rentang=(50, 80) if laki else (20, 50), palet=PAL_LAKI if laki else PAL_PEREMPUAN,
        judul_warna=f"Persentase {jk.lower()} (%)", satuan_tick="%",
        ukuran_label="Jumlah perjalanan", warna_label=f"Persentase {jk.lower()}",
        satuan_warna="%", fmt=".1f", jk=jk,
        terbesar="Wisnus terbanyak", tinggi=f"Persentase {jk.lower()} tertinggi",
        rendah=f"Persentase {jk.lower()} terendah",
        judul_grafik="Perjalanan wisatawan nusantara menurut jenis kelamin",
        luas="jumlah perjalanan (perkiraan)", warna_txt=f"persentase {jk.lower()}", unit_rentang="%",
        views=["Icicle", "Treemap"],
    )


CSS = """
.hn-h{font-family:'Outfit',sans-serif;font-weight:700;font-size:1.25rem;color:var(--dk,#0B4F4A);margin:0;line-height:1.3;}
.hn-sub{color:var(--mut,#4E6B67);font-size:.93rem;margin:.2rem 0 0;line-height:1.55;}
.hn-path{color:var(--mut,#4E6B67);font-size:.88rem;}
.hn-p p{margin:0 0 .85rem;line-height:1.75;font-size:1.02rem;color:var(--txt,#12302D);}
.hn-p b{color:var(--dk,#0B4F4A);}
.hn-bars{display:flex;flex-direction:column;gap:.55rem;margin-top:.7rem;}
.hn-bar{display:grid;grid-template-columns:minmax(110px,190px) 1fr 62px minmax(78px,auto);gap:.7rem;align-items:center;font-size:.9rem;}
.hn-bar .n{color:var(--txt,#12302D);font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.hn-bar .t{height:12px;border-radius:999px;background:#E6F2EF;overflow:hidden;}
.hn-bar .t i{display:block;height:100%;border-radius:999px;}
.hn-bar .p{text-align:right;color:var(--dk,#0B4F4A);font-weight:700;}
.hn-bar .b{text-align:center;border-radius:999px;padding:.12rem .6rem;font-size:.8rem;font-weight:700;}
.st-key-hn_root{gap:1.3rem!important;}
[class*="st-key-hn_box"]{background:#fff;border:1px solid var(--line,#D3E4E0);border-radius:18px;padding:1.3rem 1.5rem;gap:1rem!important;}
[class*="st-key-hn_box"] [data-testid="stMetric"]{background:#E9F4F1;}
[class*="st-key-hn_box"] [data-testid="stPlotlyChart"]{border:0;box-shadow:none;padding:0;border-radius:0;background:transparent;}
[data-testid="stPlotlyChart"],[data-testid="stPlotlyChart"]>div,[data-testid="stPlotlyChart"] .js-plotly-plot,[data-testid="stPlotlyChart"] .plot-container{overflow:hidden!important;max-width:100%;}
@media(max-width:760px){.hn-bar{grid-template-columns:90px 1fr 52px;}.hn-bar .b{display:none;}[class*="st-key-hn_box"]{padding:1rem 1rem;}}
"""


# ---------------- helper format ----------------
def ringkas(x):
   
    if x >= 1e9:
        t = f"{x / 1e9:,.2f} miliar"
    elif x >= 1e6:
        t = f"{x / 1e6:,.1f} juta"
    else:
        t = f"{x:,.0f}"
    return t.replace(",", "_").replace(".", ",").replace("_", ".")


def angka(x, fmt=",.0f"):
    return format(x, fmt).replace(",", "_").replace(".", ",").replace("_", ".")


def html(s):
    st.markdown("".join(x.strip() for x in s.splitlines()), unsafe_allow_html=True)


@st.cache_data
def load(path):
    return pd.read_csv(path)


# ---------------- warna ----------------
def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def kelas_warna(nilai, c):
    lo, hi = c["rentang"]
    return min(max(int((nilai - lo) / (hi - lo) * NBIN), 0), NBIN - 1)


def warna_dan_teks(nilai, c):
    
    hx = c["palet"][kelas_warna(nilai, c)]
    r, g, b = _rgb(hx)
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return hx, ("#2B1A12" if lum > 0.62 else "#FFFFFF")


def skala_bertingkat(palet):
    n = len(palet)
    return [p for i, h in enumerate(palet) for p in ([i / n, h], [(i + 1) / n, h])]


# ---------------- pengolahan ----------------
def top_n_dengan_lainnya(df, c, n):
    urut = df.groupby("Provinsi")[c["size"]].sum().sort_values(ascending=False)
    top = urut.head(n).index
    simpan, sisa = df[df["Provinsi"].isin(top)], df[~df["Provinsi"].isin(top)]
    if sisa.empty:
        return simpan
    sisa = sisa.assign(_w=sisa[c["color"]] * sisa[c["bobot"]])
    agg = (
        sisa.groupby(["Negara", "Pulau", c["leaf"]], as_index=False)
        .agg(**{c["size"]: (c["size"], "sum"), "_w": ("_w", "sum"),
                "_b": (c["bobot"], "sum"), "k": ("Provinsi", "nunique")})
    )
    agg[c["color"]] = agg["_w"] / agg["_b"]
    agg["Provinsi"] = "Provinsi lainnya (" + agg["k"].astype(str) + ")"
    return pd.concat([simpan, agg[simpan.columns.intersection(agg.columns)]], ignore_index=True)


def bangun_node(df, c, level):
    d = df.copy()
    d[[c["size"], c["color"]]] = d[[c["size"], c["color"]]].fillna(0)
    d["_w"] = d[c["color"]] * d[c["size"]]
    bagian = []
    for k in range(1, len(level) + 1):
        kol = level[:k]
        g = d.groupby(kol, as_index=False).agg(v=(c["size"], "sum"), w=("_w", "sum"))
        g["warna"] = (g["w"] / g["v"].where(g["v"] > 0)).fillna(0)
        g["id"] = g[kol].astype(str).agg("|".join, axis=1)
        g["parent"] = g[kol[:-1]].astype(str).agg("|".join, axis=1) if k > 1 else ""
        g["label"] = g[kol[-1]].astype(str)
        g["path"] = g[kol].astype(str).agg(" › ".join, axis=1)
        bagian.append(g[["id", "parent", "label", "path", "v", "warna"]])
    n = pd.concat(bagian, ignore_index=True)

    akar = n["parent"] == ""
    total_akar = n.loc[akar, "v"].sum()
    banyak_akar = int(akar.sum())
    nilai = n.set_index("id")["v"]
    nama = n.set_index("id")["label"]
    n["induk_label"] = n["parent"].map(nama).fillna("")
    n["porsi"] = (n["v"] / n["parent"].map(nilai).fillna(total_akar).where(lambda s: s > 0)).fillna(0) * 100

    def teks(r):
        if c["jenis"] == "menginap":
            return f"<b>{r.label}</b><br>{angka(r.v)} kamar<br>{angka(r.warna, '.2f')} malam"
        if r.parent == "":
            baris3 = "Total keseluruhan" if banyak_akar == 1 else f"{angka(r.porsi, '.1f')}% dari total"
        else:
            baris3 = f"{angka(r.porsi, '.1f')}% dari {r.induk_label}"
        return f"<b>{r.label}</b><br>{angka(r.v)}<br>{baris3}"

    def hover(r):
        h = (f"<b>{r.label}</b><br>{r.path}<br>{c['ukuran_label']}: {angka(r.v)}<br>"
             f"{c['warna_label']}: {angka(r.warna, c['fmt'])}{c['satuan_warna']}")
        if r.parent != "":
            h += f"<br>Bagian dari {r.induk_label}: {angka(r.porsi, '.1f')}%"
        elif banyak_akar > 1:
            h += f"<br>Bagian dari total: {angka(r.porsi, '.1f')}%"
        return h

    n["teks"] = [teks(r) for r in n.itertuples()]
    n["hover"] = [hover(r) for r in n.itertuples()]
    n["warna_teks"] = [warna_dan_teks(w, c)[1] for w in n["warna"]]
    return n


def _tick(c):
    lo, hi = c["rentang"]
    nilai = [lo + (hi - lo) * i / NBIN for i in range(NBIN + 1)]
    teks = [angka(v, ",.0f" if abs(v - round(v)) < 1e-9 else ",.1f") + c["satuan_tick"] for v in nilai]
    teks[-1] = "≥ " + teks[-1]  
    return nilai, teks


def buat_grafik(nama, n, c):
    tv, tt = _tick(c)
    skala = skala_bertingkat(c["palet"])
    fig = go.Figure(
        BENTUK[nama](
            ids=n["id"], parents=n["parent"], labels=n["label"], values=n["v"],
            branchvalues="total",
            text=n["teks"], textinfo="text",
            hovertext=n["hover"], hoverinfo="text",
            textfont=dict(color=list(n["warna_teks"]), size=13, family=FONT),
            marker=dict(
                colors=n["warna"], colorscale=skala,
                cmin=c["rentang"][0], cmax=c["rentang"][1],
                line=dict(color="#FFFFFF", width=1.5),
                showscale=True,
                colorbar=dict(
                    title=dict(text=c["judul_warna"], side="right",
                               font=dict(color=TEKS_REDUP, size=12, family=FONT)),
                    orientation="h", thickness=12, len=0.5,
                    x=0.5, xanchor="center", y=0, yanchor="top", ypad=16,
                    tickvals=tv, ticktext=tt, outlinewidth=0,
                    tickfont=dict(color=TEKS_REDUP, size=12, family=FONT),
                ),
            ),
        )
    )
    fig.update_layout(
        height=TINGGI, autosize=True, dragmode=False,
        font=dict(family=FONT, size=13, color=TEKS),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=8, l=4, r=4, b=78),
        hoverlabel=dict(bgcolor=TEAL_GELAP, font=dict(color="white", size=13, family=FONT), align="left"),
    )
    return fig


def gambar(df, c, n_prov, level, nama_level, kunci):
    df_plot = top_n_dengan_lainnya(df, c, n_prov) if "Provinsi" in level else df
    n = bangun_node(df_plot, c, level)
    jalur = " › ".join(nama_level[k] for k in level)
    for nama in c["views"]:  # tersusun ke bawah; tiap visualisasi punya kartu sendiri
        with st.container(key=f"hn_box_{kunci}_{nama}"):
            html(f'<div><div class="hn-h">{nama}: {c["judul_grafik"]}</div>'
                 f'<div class="hn-sub">{deskripsi(nama, c)}</div></div>'
                 f'<div class="hn-path">Susunan: {jalur}</div>')
            st.plotly_chart(buat_grafik(nama, n, c), use_container_width=True,
                            key=f"{kunci}_{nama}", theme=None, config=CONFIG_PLOT)


# ---------------- ringkasan ----------------
def per_provinsi(df, c):
    prov = (
        df.assign(_w=df[c["color"]] * df[c["bobot"]])
        .groupby("Provinsi")
        .agg(_w=("_w", "sum"), _b=(c["bobot"], "sum"), ukuran=(c["size"], "sum"))
    )
    prov["warna"] = prov["_w"] / prov["_b"].where(prov["_b"] > 0)
    return prov


def ringkasan(df, c, judul, wilayah):
    with st.container(key="hn_box_ringkasan"):
        html(f'<div><div class="hn-h">{judul}</div><div class="hn-sub">Wilayah: {wilayah}</div></div>')
        t1, t2, t3, t4 = st.columns(4)
        if c["jenis"] == "menginap":
            per = df.groupby("Akomodasi")
            unit, kamar, bed = per["UnitAkomodasi"].sum(), per["Kamar"].sum(), per["TempatTidur"].sum()
            rata = (df["LamaMenginap"] * df["Kamar"]).sum() / df["Kamar"].sum()

            def split(v):
                return f"Bintang {angka(v.get('Bintang', 0))} · Nonbintang {angka(v.get('Nonbintang', 0))}"

            t1.metric("Akomodasi", angka(unit.sum()), split(unit), delta_color="off")
            t2.metric("Kamar", angka(kamar.sum()), split(kamar), delta_color="off")
            t3.metric("Tempat tidur", angka(bed.sum()), split(bed), delta_color="off")
            t4.metric("Rata-rata lama menginap", f"{angka(rata, '.2f')} malam",
                      "tertimbang jumlah kamar", delta_color="off")
        else:
            per = df.groupby("JenisKelamin")["Jumlah"].sum()
            total = per.sum()
            t1.metric("Total perjalanan wisnus", ringkas(total), angka(total), delta_color="off")
            t2.metric("Laki-laki", ringkas(per["Laki-laki"]),
                      f"{angka(per['Laki-laki'] / total * 100, '.1f')}% dari total", delta_color="off")
            t3.metric("Perempuan", ringkas(per["Perempuan"]),
                      f"{angka(per['Perempuan'] / total * 100, '.1f')}% dari total", delta_color="off")
            t4.metric("Provinsi asal", df["Provinsi"].nunique(),
                      f"{df['Pulau'].nunique()} kelompok pulau", delta_color="off")



# ---------------- interpretasi (mengikuti filter yang dipilih) ----------------
def _top(prov, total, n=5):
    urut = prov.sort_values("ukuran", ascending=False)
    return urut, urut["ukuran"].head(3).sum() / total * 100


def _bars(prov, total, c, fmt_badge):
    urut = prov.sort_values("ukuran", ascending=False).head(5)
    maks = (urut["ukuran"] / total * 100).max()
    baris = []
    for nama, r in urut.iterrows():
        porsi = r["ukuran"] / total * 100
        if pd.isna(r["warna"]):
            continue
        bg, fg = warna_dan_teks(r["warna"], c)
        baris.append(
            f'<div class="hn-bar"><span class="n">{nama}</span>'
            f'<span class="t"><i style="width:{porsi / maks * 100:.1f}%;background:{bg}"></i></span>'
            f'<span class="p">{angka(porsi, ".1f")}%</span>'
            f'<span class="b" style="background:{bg};color:{fg}">{fmt_badge(r["warna"])}</span></div>')
    return '<div class="hn-bars">' + "".join(baris) + "</div>"


def tafsir_menginap(df_pulau, pilih_asal, asal, wilayah, c):
    d = df_pulau[df_pulau["Asal"] == asal]
    prov = per_provinsi(d, c)
    total = prov["ukuran"].sum()
    rata = (d["LamaMenginap"] * d["Kamar"]).sum() / total
    ada = prov.dropna(subset=["warna"])
    ada = ada[ada["ukuran"] > 0]

    p1 = f"{pilih_asal} di {wilayah} menginap rata-rata <b>{angka(rata, '.2f')} malam</b>."
    p2 = []
    if len(ada) > 1:
        a, b = ada["warna"].idxmax(), ada["warna"].idxmin()
        sel = ada["warna"].max() - ada["warna"].min()
        p1 += (f" Tamu paling lama menginap di <b>{a}</b> ({angka(ada['warna'].max(), '.2f')} malam) "
               f"dan paling singkat di <b>{b}</b> ({angka(ada['warna'].min(), '.2f')} malam).")
        p2.append(f"Selisih antarprovinsi mencapai {angka(sel, '.2f')} malam, jadi lama menginap sangat "
                  f"bergantung pada daerah tujuan.")
        if len(prov) > 1:
            p_besar = prov["ukuran"].idxmax()
            w1 = prov.loc[p_besar, "warna"]
            if p_besar == a:
                p2.append(f"{p_besar} memiliki kamar terbanyak sekaligus tamu yang paling lama menginap.")
            elif pd.notna(w1):
                arah = "di atas" if w1 > rata else "di bawah"
                p2.append(f"{p_besar} memiliki kamar terbanyak, tetapi rata-rata menginap di sana "
                          f"({angka(w1, '.2f')} malam) berada {arah} rata-rata keseluruhan.")
    p3 = []
    if len(prov) > 1:
        urut, s3 = _top(prov, total)
        n3 = min(3, len(urut))
        p3.append(f"Kamar terpusat di {n3} provinsi teratas ({', '.join(urut.index[:n3])}) yang bersama-sama "
                  f"memegang {angka(s3, '.1f')}% kamar.")
    g = {}
    for k in ("Bintang", "Nonbintang"):
        x = d[d["Akomodasi"] == k]
        if not x.empty and x["Kamar"].sum() > 0:
            g[k] = (x["LamaMenginap"] * x["Kamar"]).sum() / x["Kamar"].sum()
    if len(g) == 2:
        lebih = "bintang" if g["Bintang"] >= g["Nonbintang"] else "nonbintang"
        p3.append(f"Tamu hotel bintang menginap {angka(g['Bintang'], '.2f')} malam dan hotel nonbintang "
                  f"{angka(g['Nonbintang'], '.2f')} malam, sehingga tamu lebih lama menginap di hotel {lebih}.")
    pb = {}
    for k in ("Asing", "Lokal"):
        x = df_pulau[df_pulau["Asal"] == k]
        if not x.empty and x["Kamar"].sum() > 0:
            pb[k] = (x["LamaMenginap"] * x["Kamar"]).sum() / x["Kamar"].sum()
    if len(pb) == 2:
        lebih = "asing" if pb["Asing"] >= pb["Lokal"] else "lokal"
        p3.append(f"Tamu asing menginap {angka(pb['Asing'], '.2f')} malam dan tamu lokal {angka(pb['Lokal'], '.2f')} "
                  f"malam; tamu {lebih} menginap lebih lama.")

    bars = _bars(prov, total, c, lambda w: f"{angka(w, '.2f')} malam") if len(prov) > 0 else ""
    return dict(
        para=[p for p in (p1, " ".join(p2), " ".join(p3)) if p],
        bar_judul="Lima provinsi dengan kamar terbanyak",
        bar_sub="Panjang batang menunjukkan porsi kamar terhadap total; label berwarna menunjukkan rata-rata lama menginap.",
        bars=bars,
    )


def tafsir_wisnus(df, wilayah, c):
    jk = c["jk"]
    per = df.groupby("JenisKelamin")["Jumlah"].sum()
    total = per.sum()
    pl, pp = per["Laki-laki"] / total * 100, per["Perempuan"] / total * 100
    dominan = "laki-laki" if pl >= pp else "perempuan"
    prov = per_provinsi(df, c)
    ada = prov.dropna(subset=["warna"])
    ada = ada[ada["ukuran"] > 0]

    p1 = (f"Dari sekitar <b>{ringkas(total)} perjalanan</b> wisatawan nusantara asal {wilayah}, wisatawan "
          f"<b>{dominan}</b> lebih banyak: <b>{angka(max(pl, pp), '.1f')}%</b> berbanding "
          f"<b>{angka(min(pl, pp), '.1f')}%</b>, selisih {angka(abs(pl - pp), '.1f')} poin persentase.")
    p2 = []
    if len(prov) > 1:
        urut, s3 = _top(prov, total)
        n3 = min(3, len(urut))
        p2.append(f"Perjalanan terpusat pada provinsi asal tertentu: {n3} provinsi teratas "
                  f"({', '.join(urut.index[:n3])}) menyumbang {angka(s3, '.1f')}% perjalanan.")
    pulau = df.groupby("Pulau")["Jumlah"].sum().sort_values(ascending=False)
    if len(pulau) > 1:
        p2.append(f"Menurut kelompok pulau, {pulau.index[0]} menjadi asal terbanyak dengan "
                  f"{angka(pulau.iloc[0] / total * 100, '.1f')}% dari seluruh perjalanan.")
    p3 = []
    if len(ada) > 1:
        hi, lo = ada["warna"].idxmax(), ada["warna"].idxmin()
        p3.append(f"Persentase {jk.lower()} berkisar dari {angka(ada['warna'].min(), '.1f')}% di {lo} hingga "
                  f"{angka(ada['warna'].max(), '.1f')}% di {hi}.")
        lk = per_provinsi(df, dict(c, color="Persen_LakiLaki"))["warna"].dropna()
        k = int((lk > 50).sum())
        p3.append(f"Wisatawan laki-laki lebih banyak di {k} dari {len(lk)} provinsi, perempuan di {len(lk) - k} provinsi lainnya.")
    p3.append("Jumlah per jenis kelamin dihitung dari persentase dikalikan total perjalanan, jadi sifatnya perkiraan.")
    bars = _bars(prov, total, c, lambda w: f"{angka(w, '.1f')}% {jk.lower()}") if len(prov) > 0 else ""
    return dict(
        para=[p for p in (p1, " ".join(p2), " ".join(p3)) if p],
        bar_judul="Lima provinsi asal terbanyak",
        bar_sub=f"Panjang batang menunjukkan porsi perjalanan terhadap total; label berwarna menunjukkan persentase {jk.lower()}.",
        bars=bars,
    )


def tampil_tafsir(judul, t):
    with st.container(key="hn_box_tafsir"):
        html(f'<div class="hn-h">{judul}</div>')
        html('<div class="hn-p">' + "".join(f"<p>{p}</p>" for p in t["para"]) + "</div>")
        if t["bars"]:
            html(f'<div><div class="hn-h" style="font-size:1.05rem">{t["bar_judul"]}</div>'
                 f'<div class="hn-sub">{t["bar_sub"]}</div>{t["bars"]}</div>')


# ================= HALAMAN =================
html(f"<style>{''.join(x.strip() for x in CSS.splitlines())}</style>")

with st.container(key="hn_root"):
    menginap_all = load("data/processed/hierarki_menginap.csv")
    wisnus_all = load("data/processed/hierarki_wisnus.csv")
    wisnus_all = wisnus_all.assign(Persen_Perempuan=100 - wisnus_all["Persen_LakiLaki"])

    g0 = menginap_all[menginap_all["Asal"] == "Gabungan"]
    kp = g0.groupby("Pulau")["Kamar"].sum().sort_values(ascending=False)
    html(f'<div class="cerita"><p>Hotel bintang dan nonbintang di Indonesia memiliki <b>{angka(kp.sum())} kamar</b> '
         f'yang tersebar di {g0["Provinsi"].nunique()} provinsi, tetapi sebarannya jauh dari merata: '
         f'<b>{kp.index[0]}</b> memegang {angka(kp.iloc[0] / kp.sum() * 100, ".0f")}% di antaranya.</p>'
         '<p>Halaman ini menelusurinya selapis demi selapis, dari kelompok pulau sampai provinsi dan jenis hotel. '
         'Setelah itu pertanyaannya bergeser ke wisatawan nusantara: dari provinsi mana mereka berasal, '
         'dan lebih banyak laki-laki atau perempuan.</p></div>')

    with st.container(key="hn_box_filter"):
        html('<div><div class="hn-h">Pilih topik yang ingin ditelusuri</div>'
             '<div class="hn-sub">Atur wilayah dan susunan hierarki; semua grafik di bawah menyesuaikan.</div></div>')
        topik = st.segmented_control(
            "Topik", OPSI, selection_mode="single", default=OPSI[0],
            key="hn_topik", label_visibility="collapsed",
        ) or OPSI[0]
        jenis = "menginap" if topik == OPSI[0] else "wisnus"
        semua = menginap_all if jenis == "menginap" else wisnus_all
        leaf_label = "Jenis akomodasi" if jenis == "menginap" else "Jenis kelamin"
        leaf = "Akomodasi" if jenis == "menginap" else "JenisKelamin"
        nama_level = dict(NAMA_LEVEL, **{leaf: leaf_label})
        pilihan_level = {**{NAMA_LEVEL[k]: k for k in URUT_LEVEL}, leaf_label: leaf}

        r1a, r1b, r1c = st.columns([1.3, 1.5, 1])
        pulau_dipilih = r1a.multiselect(
            "Kelompok pulau", sorted(semua["Pulau"].unique()),
            placeholder="Semua pulau", key="hn_pulau",
        )
        level_dipilih = r1b.multiselect(
            "Tingkat hierarki", list(pilihan_level), default=list(pilihan_level),
            placeholder="Pilih tingkat", key=f"hn_level_{jenis}",
        ) or list(pilihan_level)
        leaf_dulu = r1c.toggle(f"Mulai dari {leaf_label.lower()}", key=f"hn_balik_{jenis}",
                               help="Jenis di tingkat teratas, wilayah di bawahnya.")

        if pulau_dipilih:
            menginap_all = menginap_all[menginap_all["Pulau"].isin(pulau_dipilih)]
            wisnus_all = wisnus_all[wisnus_all["Pulau"].isin(pulau_dipilih)]
            semua = menginap_all if jenis == "menginap" else wisnus_all
        wilayah = ", ".join(pulau_dipilih) if pulau_dipilih else "seluruh Indonesia"

        level = [pilihan_level[x] for x in pilihan_level if x in level_dipilih]
        if leaf_dulu and leaf in level:
            level = [leaf] + [k for k in level if k != leaf]

        r2a, r2b, _ = st.columns([1.3, 1.5, 1])
        n_maks = semua["Provinsi"].nunique()
        if "Provinsi" in level and n_maks > 5:
            n_prov = r2a.slider("Jumlah provinsi pada grafik (terbesar)", 5, n_maks, min(10, n_maks),
                                help="Provinsi di luar daftar digabung per pulau sebagai 'Provinsi lainnya'. "
                                     "Angka ringkasan tetap dihitung dari semua provinsi.")
        else:
            n_prov = n_maks
        if jenis == "menginap":
            pilih_asal = r2b.selectbox("Asal tamu", ["Semua tamu", "Tamu asing", "Tamu lokal"], key="hn_asal")
        else:
            jk = r2b.radio("Warna menunjukkan", ["Laki-laki", "Perempuan"], horizontal=True, key="hn_jk")

    # ---------- isi ----------
    if jenis == "menginap":
        c = cfg_menginap()
        asal = {"Semua tamu": "Gabungan", "Tamu asing": "Asing", "Tamu lokal": "Lokal"}[pilih_asal]
        df = menginap_all[menginap_all["Asal"] == asal]
        judul_ringkas = f"Lama menginap di hotel · {pilih_asal.lower()}"
        tafsir = tafsir_menginap(menginap_all, pilih_asal, asal, wilayah, c)
        judul_tafsir = "Apa arti pola lama menginap ini?"
    else:
        c = cfg_wisnus(jk)
        df = wisnus_all
        judul_ringkas = "Wisatawan nusantara menurut jenis kelamin"
        tafsir = tafsir_wisnus(df, wilayah, c)
        judul_tafsir = "Apa arti komposisi wisatawan ini?"

    ringkasan(df, c, judul_ringkas, wilayah)

    gambar(df, c, n_prov, level, nama_level, jenis)
    tampil_tafsir(judul_tafsir, tafsir)