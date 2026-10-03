from pathlib import Path

import holoviews as hv
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from bokeh.embed import file_html
from bokeh.models import BoxZoomTool, HoverTool, PanTool, ResetTool, WheelZoomTool
from bokeh.resources import CDN
from holoviews import opts

hv.extension("bokeh")

st.set_page_config(page_title="Flow - Pergerakan Wisatawan", layout="wide")

PROC = Path(__file__).resolve().parents[1] / "data" / "processed"

# ---------------- palet (Okabe-Ito seperti bab 3; skala heatmap seperti bab 1; ramah buta warna) ----------------
FONT = "Outfit, Source Sans Pro, Segoe UI, Arial, sans-serif"
TEAL_GELAP, TEKS, TEKS_REDUP = "#0B4F4A", "#12302D", "#4E6B67"
JENIS_COLOR = {
    "Bandara": "#0072B2",
    "Pelabuhan laut": "#E69F00",
    "Pos lintas batas darat": "#009E73",
    "Lainnya": "#999999",
}
NEGARA_COLOR = "#4E6B67"
HEAT_SCALE = [[0, "#FFF1B8"], [0.25, "#FDC85C"], [0.5, "#F28C38"], [0.75, "#C8402F"], [1, "#6E1F3F"]]
WILAYAH_COLOR = {
    "Sumatera": "#0072B2",
    "Jawa": "#D55E00",
    "Bali & Nusa Tenggara": "#E69F00",
    "Kalimantan": "#009E73",
    "Sulawesi": "#56B4E9",
    "Maluku": "#CC79A7",
    "Papua": "#6E1F3F",
}
WILAYAH_ORDER = list(WILAYAH_COLOR)
DIR_COLOR = {"a": "#0F7C73", "b": "#E69F00"}  # arah dominan / arah balik pada batang

CSS = """
.fl-head{margin:2rem 0 .6rem;}
.fl-h{font-family:'Outfit',sans-serif;font-weight:700;font-size:1.4rem;color:var(--dk,#0B4F4A);line-height:1.25;margin:0;}
.fl-sub{color:var(--mut,#4E6B67);font-size:.97rem;line-height:1.55;margin:.2rem 0 0;}
.fl-p p{margin:.2rem 0 .85rem;line-height:1.75;font-size:1.02rem;color:var(--txt,#12302D);}
.fl-p b{color:var(--dk,#0B4F4A);}
[class*="st-key-fl_card"]{background:#fff;border:1px solid var(--line,#D3E4E0);border-radius:18px;padding:1.3rem 1.5rem 1.2rem;margin:0 0 .4rem;}
[class*="st-key-fl_card"] [data-testid="stPlotlyChart"]{border:none;box-shadow:none;padding:0;border-radius:0;}
[data-testid="stPlotlyChart"]{padding:0!important;border:0!important;box-shadow:0 0 0 1px var(--line,#D3E4E0)!important;box-sizing:border-box;}
[data-testid="stPlotlyChart"],[data-testid="stPlotlyChart"]>div,[data-testid="stPlotlyChart"] .js-plotly-plot,[data-testid="stPlotlyChart"] .plot-container{overflow:hidden!important;max-width:100%;}
.fl-kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:0 0 1.2rem;}
.fl-kpi{background:#fff;border:1px solid var(--line,#D3E4E0);border-radius:16px;padding:1rem 1.2rem 1.05rem;}
.fl-kpi .n{font-family:'Outfit',sans-serif;font-weight:800;font-size:2rem;line-height:1.1;color:var(--dk,#0B4F4A);}
.fl-kpi .l{font-weight:700;color:var(--txt,#12302D);margin-top:.25rem;}
.fl-kpi .s{color:var(--mut,#4E6B67);font-size:.88rem;line-height:1.45;margin-top:.15rem;}
.fl-top3{border-top:1px solid var(--line,#D3E4E0);margin-top:1.1rem;padding:1.2rem 0 .6rem;}
.fl-top3 .t{font-family:'Outfit',sans-serif;font-weight:700;font-size:1.1rem;color:var(--dk,#0B4F4A);margin:0;line-height:1.3;}
.fl-top3 .s{color:var(--mut,#4E6B67);font-size:.9rem;margin:.15rem 0 1rem;}
.fl-t3-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:.9rem;}
.fl-t3-card{background:#F4F9F8;border:1px solid var(--line,#D3E4E0);border-radius:14px;padding:1rem 1.1rem 1.1rem;}
.fl-t3-card .ttl{font-family:'Outfit',sans-serif;font-weight:700;font-size:1.02rem;color:var(--dk,#0B4F4A);margin-bottom:.9rem;}
.fl-t3-row{display:grid;grid-template-columns:30px 1fr auto;gap:.7rem;align-items:center;padding:.55rem 0;border-top:1px solid var(--line,#D3E4E0);}
.fl-t3-row:first-of-type{border-top:none;padding-top:0;}
.fl-t3-row .no{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;font-family:'Outfit',sans-serif;font-weight:800;background:#E6F2EF;color:var(--dk,#0B4F4A);}
.fl-t3-row.p1 .no{background:#8CEBD8;color:#06332E;}
.fl-t3-row .nm{font-weight:700;color:var(--txt,#12302D);line-height:1.25;}
.fl-t3-row .sb{font-size:.78rem;color:var(--mut,#4E6B67);}
.fl-t3-row .bar{height:8px;border-radius:999px;background:#DCEBE8;margin-top:.4rem;overflow:hidden;}
.fl-t3-row .bar span{display:block;height:100%;border-radius:999px;background:#0F7C73;}
.fl-t3-row .val{text-align:right;font-family:'Outfit',sans-serif;font-weight:700;color:var(--dk,#0B4F4A);line-height:1.2;white-space:nowrap;}
.fl-t3-row .val small{display:block;font-family:'Source Sans Pro',sans-serif;font-weight:600;font-size:.78rem;color:var(--mut,#4E6B67);}
@media(max-width:900px){.fl-kpis,.fl-t3-grid{grid-template-columns:1fr;}}
@media(max-width:600px){[class*="st-key-dua_"] iframe{height:430px!important;}}
"""


# ---------------- helper format ----------------
def idn(x: float, d: int = 0) -> str:
    """Angka gaya Indonesia: 1.234.567,89"""
    return f"{x:,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def ringkas(x: float) -> str:
    """Angka pendek: 615.402 | 2,28 juta | 13,9 juta"""
    if x >= 1e9:
        return f"{idn(x / 1e9, 2)} miliar"
    if x >= 1e7:
        return f"{idn(x / 1e6, 1)} juta"
    if x >= 1e6:
        return f"{idn(x / 1e6, 2)} juta"
    return idn(x)


def pct(x: float, d: int = 1) -> str:
    return f"{idn(x * 100, d)}%"


def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def html(s: str):
    st.markdown("".join(x.strip() for x in s.splitlines()), unsafe_allow_html=True)


def kepala(label: str, judul: str, sub: str = ""):
    html(f'<div class="fl-head"><div class="fl-h">{judul}</div>'
         + (f'<div class="fl-sub">{sub}</div>' if sub else "") + "</div>")


def judul_kartu(label: str, judul: str, sub: str = ""):
    html(f'<div><div class="fl-h">{judul}</div>' + (f'<div class="fl-sub">{sub}</div>' if sub else "") + "</div>")


def chips(mapping: dict) -> str:
    """Legenda warna: titik berwarna + nama."""
    return '<div class="legenda">' + "".join(
        f'<span><i style="background:{c}"></i>{k}</span>' for k, c in mapping.items()) + "</div>"


def gaya_plotly(fig: go.Figure, tinggi: int, atas: int = 40, bawah: int = 8):
    fig.update_layout(
        height=tinggi, autosize=True, separators=",.",
        font=dict(family=FONT, size=12, color=TEKS),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=atas, l=14, r=14, b=bawah),
        hoverlabel=dict(bgcolor=TEAL_GELAP, font=dict(color="white", size=13, family=FONT), align="left"),
    )
    fig.update_xaxes(automargin=True)  
    fig.update_yaxes(automargin=True)


@st.cache_data
def load_data():
    return (pd.read_csv(PROC / "flow_wisman.csv"), pd.read_csv(PROC / "flow_wisnus_od.csv"),
            pd.read_csv(PROC / "flow_wisnus_provinsi.csv"))


def pair_stats(f: pd.DataFrame) -> pd.DataFrame:
   
    t = f.copy()
    t["A"] = t[["Asal", "Tujuan"]].min(axis=1)
    t["B"] = t[["Asal", "Tujuan"]].max(axis=1)
    t["ab"] = t["Asal"] == t["A"]
    pv = t.pivot_table(index=["A", "B"], columns="ab", values="Value", aggfunc="sum").fillna(0)
    pv = pv.rename(columns={True: "AB", False: "BA"}).reset_index()
    for c in ("AB", "BA"):
        if c not in pv:
            pv[c] = 0.0
    pv["max"] = pv[["AB", "BA"]].max(axis=1)
    pv["min"] = pv[["AB", "BA"]].min(axis=1)
    pv["tot"] = pv["AB"] + pv["BA"]
    pv["dom"] = np.where(pv["AB"] >= pv["BA"], pv["A"] + " → " + pv["B"], pv["B"] + " → " + pv["A"])
    pv["rev"] = np.where(pv["AB"] >= pv["BA"], pv["B"] + " → " + pv["A"], pv["A"] + " → " + pv["B"])
    pv["rasio"] = pv["min"] / pv["max"].replace(0, np.nan)
    return pv


wisman, od, prov = load_data()
html(f"<style>{''.join(x.strip() for x in CSS.splitlines())}</style>")

TOTAL_WISMAN = int(wisman["Value"].sum())  # total seluruh negara & pintu; tidak ikut filter
tot_negara = wisman.groupby("Negara")["Value"].sum().sort_values(ascending=False)
tot_pintu = wisman.groupby("Pintu")["Value"].sum().sort_values(ascending=False)
pintu_prov = wisman.drop_duplicates("Pintu").set_index("Pintu")["Provinsi_Pintu"]
antar = od[~od["Internal"]]  # perjalanan di dalam provinsi sendiri (±71%) tidak digambar sebagai arus
TOTAL_ANTAR = int(antar["Value"].sum())

_porsi_dalam = od.loc[od["Internal"], "Value"].sum() / od["Value"].sum()
html(" ".join(f'''<div class="cerita"><p>Wisatawan mancanegara mencatat <b>{idn(TOTAL_WISMAN)} kunjungan</b> dari
{wisman["Negara"].nunique()} negara lewat {wisman["Pintu"].nunique()} pintu masuk. Satu pintu saja,
<b>{tot_pintu.index[0]}</b>, menerima {pct(tot_pintu.iloc[0] / TOTAL_WISMAN)} dari semuanya.</p>
<p>Wisatawan nusantara bergerak dengan pola lain: {pct(_porsi_dalam, 0)} perjalanan berakhir di provinsi asal sendiri.
Bagian kedua halaman ini hanya melihat sisanya, yaitu perjalanan yang melintasi batas provinsi.</p></div>'''.split()))

# =====================================================================================
# BAGIAN 1 - WISATAWAN MANCANEGARA
# =====================================================================================
with st.container(key="fl_card_atur"):
    judul_kartu("Wisatawan mancanegara", "Atur tampilan aliran",
                "Pilih jumlah negara dan batas minimal aliran. Semua grafik di bagian ini ikut berubah.")
    a, b = st.columns(2, gap="large")
    top_n = a.slider("Jumlah negara asal", 15, 30, 15, key="flow_topn",
                     help="Negara diurutkan dari jumlah kunjungan terbanyak.")
    min_flow = b.select_slider(
        "Tampilkan aliran minimal", options=[0, 1_000, 2_500, 5_000, 10_000, 25_000, 50_000, 100_000, 250_000],
        value=10_000, key="flow_minflow",
        format_func=lambda v: "Semua aliran" if v == 0 else f"{idn(v)} kunjungan",
        help="Aliran di bawah batas ini disembunyikan agar diagram tidak penuh garis.",
    )

top_c = tot_negara.head(top_n)
d_top = wisman[wisman["Negara"].isin(top_c.index)]
d_s = d_top[d_top["Value"] >= min_flow]
tot_s = d_s["Value"].sum()

html(f"""
<div class="fl-kpis">
  <div class="fl-kpi"><div class="n">{idn(TOTAL_WISMAN)}</div><div class="l">Total kunjungan wisatawan mancanegara</div>
    <div class="s">{wisman['Negara'].nunique()} negara asal · {wisman['Pintu'].nunique()} pintu masuk</div></div>
  <div class="fl-kpi"><div class="n">{pct(top_c.sum() / TOTAL_WISMAN)}</div><div class="l">Porsi {top_n} negara teratas</div>
    <div class="s">{idn(top_c.sum())} kunjungan dari {top_n} negara tersebut.</div></div>
  <div class="fl-kpi"><div class="n">{idn(len(d_s))}</div><div class="l">Aliran pada diagram</div>
    <div class="s">{"Semua aliran ditampilkan" if min_flow == 0 else f"Aliran ≥ {idn(min_flow)} kunjungan"} · {pct(tot_s / TOTAL_WISMAN)} dari total.</div></div>
</div>""")

# ---------------- SANKEY ----------------
kepala("Sankey", "Dari negara asal ke pintu masuk",
       "Makin tebal pita, makin banyak kunjungan. Arahkan kursor ke pita untuk melihat angka pastinya.")
html(chips({"Bandara": JENIS_COLOR["Bandara"], "Pelabuhan laut": JENIS_COLOR["Pelabuhan laut"],
            "Pos lintas batas darat": JENIS_COLOR["Pos lintas batas darat"], "Lainnya": JENIS_COLOR["Lainnya"]}))

if d_s.empty:
    st.session_state["narasi_flow"] = []
    html('<div class="fl-sub">Belum ada aliran yang lolos batas ini. Turunkan batas minimal di atas.</div>')
else:
    neg_v = d_s.groupby("Negara")["Value"].sum().sort_values(ascending=False)
    pin_v = d_s.groupby("Pintu")["Value"].sum().sort_values(ascending=False)
    countries, gates = neg_v.index.tolist(), pin_v.index.tolist()
    gate_info = d_s.drop_duplicates("Pintu").set_index("Pintu")[["Jenis_Pintu", "Provinsi_Pintu"]]

    labels = countries + gates
    idx = {n: i for i, n in enumerate(labels)}
    node_color = [NEGARA_COLOR] * len(countries) + [JENIS_COLOR[gate_info.loc[g, "Jenis_Pintu"]] for g in gates]
    node_hover = [f"Negara asal<br>{idn(neg_v[c])} kunjungan pada diagram<br>{idn(tot_negara[c])} kunjungan seluruhnya"
                  for c in countries] + [
        f"{gate_info.loc[g, 'Jenis_Pintu']} · {gate_info.loc[g, 'Provinsi_Pintu']}<br>{idn(pin_v[g])} kunjungan pada diagram"
        for g in gates]

    fig_sankey = go.Figure(go.Sankey(
        node=dict(pad=8, thickness=16, label=labels, color=node_color, customdata=node_hover,
                  line=dict(color="rgba(0,0,0,0.2)", width=0.5),
                  hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>"),
        link=dict(source=[idx[s] for s in d_s["Negara"]], target=[idx[t] for t in d_s["Pintu"]], value=d_s["Value"],
                  color=[rgba(JENIS_COLOR[j], 0.4) for j in d_s["Jenis_Pintu"]],
                  hovertemplate="%{source.label} → %{target.label}<br><b>%{value:,.0f}</b> kunjungan<extra></extra>"),
    ))
    gaya_plotly(fig_sankey, int(min(660, max(480, 15 * max(len(countries), len(gates)) + 150))), atas=10, bawah=10)

    
    n1, p1 = countries[0], gates[0]
    teratas = d_s.loc[d_s["Value"].idxmax()]
    sisa_pin = [g for g in gates[1:3]]
    kartu = [
        ("NEGARA ASAL", f"{n1} paling banyak mengirim wisatawan",
         f"Dari {top_n} negara terpilih, {n1} mengirim {ringkas(neg_v.iloc[0])} kunjungan, "
         f"atau {pct(neg_v.iloc[0] / tot_s)} dari aliran yang tampil."),
        ("PINTU MASUK", f"{p1} jadi gerbang utama",
         f"Pintu ini menerima {pct(pin_v.iloc[0] / tot_s)} kunjungan pada tampilan ini"
         + (f", disusul {' dan '.join(sisa_pin)}." if sisa_pin else ".")),
        ("JALUR TERSIBUK", f"{teratas['Negara']} → {teratas['Pintu']}",
         f"{idn(teratas['Value'])} kunjungan, setara {pct(teratas['Value'] / tot_negara[teratas['Negara']])} "
         f"dari seluruh kunjungan wisatawan asal {teratas['Negara']}."),
        ("CAKUPAN", "Seberapa lengkap gambarnya?",
         f"Dengan {top_n} negara dan " + ("tanpa batas minimal" if min_flow == 0 else f"batas {idn(min_flow)} kunjungan")
         + f", diagram memuat {idn(len(d_s))} jalur yang mencakup {pct(tot_s / TOTAL_WISMAN)} dari seluruh kunjungan."
         + (" Turunkan batas untuk melihat jalur yang lebih kecil." if min_flow > 0 else "")),
    ]
    st.session_state["narasi_flow"] = kartu
    st.plotly_chart(fig_sankey, use_container_width=True, key="sankey_flow", theme=None, config={"displaylogo": False})

# ---------------- HEATMAP ----------------
kepala("Heatmap", "Pasangan negara dan pintu yang paling ramai",
       "Makin pekat warnanya, makin banyak kunjungan. Kotak paling pucat berarti tidak ada kunjungan.")
skala = st.radio("Skala warna", ["Logaritmik", "Linear"], horizontal=True, key="heat_scale",
                 help="Ngurah Rai jauh di atas pintu lain. Skala logaritmik menjaga pasangan kecil tetap terlihat.")

mat = d_top.pivot_table(index="Negara", columns="Pintu", values="Value", aggfunc="sum", fill_value=0)
mat = mat.reindex(index=top_c.index)
mat = mat[mat.sum().sort_values(ascending=False).index]
z = mat.values.astype(float)  # tidak ada kunjungan = 0 (tetap diberi warna)
if skala == "Logaritmik":
    zplot = np.log10(1 + z)  # log(1+x): nilai 0 tetap terdefinisi
    batas = [v for v in (0, 10, 100, 1_000, 10_000, 100_000, 1_000_000) if np.log10(1 + v) <= zplot.max() + 0.2]
    colorbar = dict(title="Kunjungan", thickness=14, tickvals=[np.log10(1 + v) for v in batas],
                    ticktext=[idn(v) for v in batas])
else:
    zplot = z
    colorbar = dict(title="Kunjungan", thickness=14)

fig_heat = go.Figure(go.Heatmap(
    z=zplot, x=mat.columns.tolist(), y=mat.index.tolist(), customdata=z, colorscale=HEAT_SCALE, xgap=2, ygap=2,
    colorbar=colorbar, hovertemplate="Negara: %{y}<br>Pintu: %{x}<br>Kunjungan: <b>%{customdata:,.0f}</b><extra></extra>",
))
gaya_plotly(fig_heat, int(max(500, 24 * len(mat) + 250)), atas=16, bawah=28)
fig_heat.update_layout(
    dragmode=False,
    xaxis=dict(title="Pintu masuk (urut dari terbanyak)", tickangle=-45, type="category"),
    yaxis=dict(title="Negara asal (urut dari terbanyak)", autorange="reversed", type="category"),
)
i, j = np.unravel_index(np.argmax(z), z.shape)
st.plotly_chart(fig_heat, use_container_width=True, key="heatmap_flow", theme=None,
                config={"displaylogo": False, "displayModeBar": False})
html(f'<div class="fl-p"><p>Di antara {top_n} negara terpilih, pasangan paling ramai adalah <b>{mat.index[i]} → {mat.columns[j]}</b> '
     f'dengan {idn(z[i, j])} kunjungan.</p></div>')

# =====================================================================================
# BAGIAN 2 - WISATAWAN NUSANTARA
# =====================================================================================
kepala("Wisatawan nusantara", "Perjalanan antarprovinsi",
       "Provinsi mana yang paling sering mengirim dan menerima wisatawan dari provinsi lain?")

totals = antar.groupby("Asal")["Value"].sum().add(antar.groupby("Tujuan")["Value"].sum(), fill_value=0)
with st.container(key="fl_card_atur2"):
    judul_kartu("Pengaturan", "Atur tampilan chord dan batang")
    c1, c2, c3 = st.columns(3, gap="large")
    n_prov = c1.slider("Jumlah provinsi", 15, 38, 15, key="chord_filter", help="Diurutkan dari volume terbesar.")
    top_prov = totals.nlargest(n_prov).index.tolist()
    fokus = c2.selectbox("Fokus provinsi", ["Semua provinsi"] + sorted(top_prov), key="chord_focus",
                         help="Pilih satu provinsi untuk melihat mitra perjalanannya.")
    min_chord = c3.select_slider(
        "Arus minimal pada chord", options=[0, 10_000, 50_000, 100_000, 250_000, 500_000, 1_000_000], value=100_000,
        key="chord_min", format_func=lambda v: "Semua arus" if v == 0 else f"{idn(v)} perjalanan",
        help="Hanya memengaruhi chord. Batang selalu memuat semua arus.")

flows = antar[antar["Asal"].isin(top_prov) & antar["Tujuan"].isin(top_prov)]
edges = flows[flows["Value"] >= min_chord]
if fokus != "Semua provinsi":
    edges = edges[(edges["Asal"] == fokus) | (edges["Tujuan"] == fokus)]

# ---- data untuk batang & interpretasi ----
if fokus == "Semua provinsi":
    pv = pair_stats(flows).nlargest(10, "tot")
    pf = None
else:
    out_ = flows[flows["Asal"] == fokus].set_index("Tujuan")["Value"].rename("keluar")
    in_ = flows[flows["Tujuan"] == fokus].set_index("Asal")["Value"].rename("masuk")
    pf = pd.concat([out_, in_], axis=1).fillna(0)
    pf["tot"] = pf["keluar"] + pf["masuk"]
    pf["rasio"] = pf[["keluar", "masuk"]].min(axis=1) / pf[["keluar", "masuk"]].max(axis=1).replace(0, np.nan)
    pf = pf.nlargest(10, "tot")
    pv = None

with st.container(key="dua_flow"):
    col_chord, col_bar = st.columns([1.1, 1], gap="large")

# ---------------- CHORD ----------------
with col_chord:
    judul_kartu("Chord", "Arus antarprovinsi", "Lebar pita menunjukkan jumlah perjalanan, warna menunjukkan pulau provinsi asal. Arahkan kursor ke busur untuk melihat angkanya.")
    html(chips(WILAYAH_COLOR))
    if edges.empty:
        html('<div class="fl-sub">Belum ada arus yang lolos batas ini. Turunkan batas minimal di atas.</div>')
    else:
        names = pd.unique(edges[["Asal", "Tujuan"]].values.ravel())
        pinfo = prov.set_index("Provinsi")
        node_df = pd.DataFrame({"name": names})
        node_df["Wilayah"] = node_df["name"].map(pinfo["Wilayah"])
        node_df["Keluar"] = node_df["name"].map(lambda n: idn(pinfo.loc[n, "Keluar"]))
        node_df["Masuk"] = node_df["name"].map(lambda n: idn(pinfo.loc[n, "Masuk"]))
        node_df["_w"] = node_df["Wilayah"].map({w: k for k, w in enumerate(WILAYAH_ORDER)})
        node_df["_t"] = node_df["name"].map(totals)
        node_df = node_df.sort_values(["_w", "_t"], ascending=[True, False]).drop(columns=["_w", "_t"])

        edge_df = edges.rename(columns={"Asal": "source", "Tujuan": "target", "Value": "value"})[
            ["source", "target", "value", "Wilayah_Asal"]]
        nodes = hv.Dataset(node_df, "name", vdims=["Wilayah", "Keluar", "Masuk"])
        chord = hv.Chord((edge_df, nodes), vdims=["value", "Wilayah_Asal"])
        chord.opts(opts.Chord(
            cmap=WILAYAH_COLOR, edge_cmap=WILAYAH_COLOR, node_color="Wilayah", edge_color="Wilayah_Asal",
            labels="name", edge_alpha=0.6, node_size=12, label_text_font_size="8pt",
            inspection_policy="nodes", selection_policy="nodes",
            default_tools=[], tools=["hover", "tap"],
            width=520, height=520, padding=0.22, title="",
        ))
        bokeh_fig = hv.render(chord, backend="bokeh")
     
        node_layers = [r for r in bokeh_fig.renderers
                       if hasattr(r, "node_renderer") or "text" not in r.data_source.data]
        hover = HoverTool(renderers=node_layers, tooltips=[
            ("Provinsi", "@index_hover"), ("Wilayah", "@Wilayah"),
            ("Keluar (antarprovinsi)", "@Keluar"), ("Masuk (antarprovinsi)", "@Masuk")])
        lock = (PanTool, WheelZoomTool, BoxZoomTool, ResetTool, HoverTool)  # tanpa pan/zoom: posisi tetap
        bokeh_fig.toolbar.tools = [t for t in bokeh_fig.toolbar.tools if not isinstance(t, lock)] + [hover]
        bokeh_fig.toolbar.active_drag = None
        bokeh_fig.toolbar.active_scroll = None
        bokeh_fig.toolbar.active_inspect = hover
        bokeh_fig.sizing_mode = "scale_width"  
        bokeh_fig.max_width = 520
        bokeh_fig.align = "center"
        bokeh_fig.toolbar_location = None
        chord_html = file_html(bokeh_fig, CDN, "Chord Diagram")
        if hasattr(st, "iframe"):
            st.iframe(chord_html, height=545)
        else:
            st.components.v1.html(chord_html, height=545, scrolling=False)

# ---------------- BATANG TIMBAL BALIK ----------------
with col_bar:
    if pf is None:
        judul_kartu("Batang", "Arus dua arah pada pasangan provinsi terpadat",
                    "Tiap pasangan punya dua batang: hijau tua untuk perjalanan searah panah pada labelnya, "
                    "oranye untuk perjalanan sebaliknya. Makin pendek batang oranye, makin timpang arusnya.")
    else:
        judul_kartu("Batang", f"Arus keluar dan masuk {fokus}",
                    f"Tiap mitra punya dua batang: hijau tua untuk perjalanan dari {fokus} ke mitra, "
                    f"oranye untuk perjalanan dari mitra ke {fokus}.")
    if (pv is not None and pv.empty) or (pf is not None and pf.empty):
        html('<div class="fl-sub">Belum ada arus untuk ditampilkan pada pengaturan ini.</div>')
    else:
        fig_bar = go.Figure()
        if pv is not None:
            fig_bar.add_bar(
                y=pv["dom"], x=pv["max"] / 1e6, orientation="h", name="Searah panah pada label", marker_color=DIR_COLOR["a"],
                text=[idn(v / 1e6, 2) for v in pv["max"]], textposition="outside", cliponaxis=False,
                customdata=np.column_stack([pv["dom"], pv["max"], pv["rasio"].fillna(0)]),
                hovertemplate="%{customdata[0]}<br><b>%{customdata[1]:,.0f}</b> perjalanan<br>Arah balik: %{customdata[2]:.0%} dari arah dominan<extra></extra>")
            fig_bar.add_bar(
                y=pv["dom"], x=pv["min"] / 1e6, orientation="h", name="Arah sebaliknya", marker_color=DIR_COLOR["b"],
                text=[idn(v / 1e6, 2) for v in pv["min"]], textposition="outside", cliponaxis=False,
                customdata=np.column_stack([pv["rev"], pv["min"], pv["rasio"].fillna(0)]),
                hovertemplate="%{customdata[0]}<br><b>%{customdata[1]:,.0f}</b> perjalanan<br>Arah balik: %{customdata[2]:.0%} dari arah dominan<extra></extra>")
        else:
            fig_bar.add_bar(
                y=pf.index, x=pf["keluar"] / 1e6, orientation="h", name=f"{fokus} → mitra", marker_color=DIR_COLOR["a"],
                text=[idn(v / 1e6, 2) for v in pf["keluar"]], textposition="outside", cliponaxis=False,
                hovertemplate=f"{fokus} → %{{y}}<br><b>%{{customdata:,.0f}}</b> perjalanan<extra></extra>", customdata=pf["keluar"])
            fig_bar.add_bar(
                y=pf.index, x=pf["masuk"] / 1e6, orientation="h", name=f"mitra → {fokus}", marker_color=DIR_COLOR["b"],
                text=[idn(v / 1e6, 2) for v in pf["masuk"]], textposition="outside", cliponaxis=False,
                hovertemplate=f"%{{y}} → {fokus}<br><b>%{{customdata:,.0f}}</b> perjalanan<extra></extra>", customdata=pf["masuk"])
        gaya_plotly(fig_bar, 560, atas=60, bawah=40)
        fig_bar.update_layout(
            barmode="group", dragmode=False,
            xaxis=dict(title="Perjalanan wisatawan nusantara (juta)", gridcolor="#E6F2EF", zeroline=False),
            yaxis=dict(title="", autorange="reversed", tickfont=dict(size=11), ticksuffix="\u00a0\u00a0"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(size=12)),
        )
        fig_bar.update_layout(margin=dict(t=60, l=14, r=44, b=28))
        st.plotly_chart(fig_bar, use_container_width=True, key="chord_bar_flow", theme=None,
                        config={"displaylogo": False, "displayModeBar": False})


def kartu_top3(judul, items, total):
    maks = items[0][2]
    isi = ""
    for k, (nama, sub, nilai) in enumerate(items, 1):
        isi += (f'<div class="fl-t3-row {"p1" if k == 1 else ""}"><div class="no">{k}</div>'
                f'<div><div class="nm">{nama}</div>' + (f'<div class="sb">{sub}</div>' if sub else "")
                + f'<div class="bar"><span style="width:{max(6, nilai / maks * 100):.0f}%"></span></div></div>'
                f'<div class="val">{ringkas(nilai)}<small>{pct(nilai / total)}</small></div></div>')
    return f'<div class="fl-t3-card"><div class="ttl">{judul}</div>{isi}</div>'


pairs_all = pair_stats(antar).nlargest(3, "tot")
top_neg = [(n, "", v) for n, v in tot_negara.head(3).items()]
top_pin = [(p, pintu_prov[p], v) for p, v in tot_pintu.head(3).items()]
top_pair = [(f"{r['A']} ⇄ {r['B']}", "dua arah", r["tot"]) for _, r in pairs_all.iterrows()]
# ---------------- INTERPRETASI (di bawah chord & batang) ----------------
with st.container(key="fl_card_interp"):
    if pf is None and pv is not None and not pv.empty:
        r0 = pv.iloc[0]
        seimbang, timpang = pv.loc[pv["rasio"].idxmax()], pv.loc[pv["rasio"].idxmin()]
        paras = [f"Arus dua arah terbesar ada di antara <b>{r0['A']}</b> dan <b>{r0['B']}</b>: "
                 f"<b>{ringkas(r0['tot'])} perjalanan</b>. Arah dominannya {r0['dom']}; arus baliknya "
                 f"{pct(r0['rasio'], 0)} dari itu.",
                 f"Pasangan yang paling seimbang adalah {seimbang['A']} dan {seimbang['B']} (arah balik "
                 f"{pct(seimbang['rasio'], 0)} dari arah dominan). Yang paling timpang adalah {timpang['A']} dan "
                 f"{timpang['B']}, dengan arah balik hanya {pct(timpang['rasio'], 0)}."]
    elif pf is not None and not pf.empty:
        r = prov.set_index("Provinsi").loc[fokus]
        net = r["Masuk"] - r["Keluar"]
        paras = [f"<b>{fokus}</b> lebih banyak <b>{'menerima' if net > 0 else 'mengirim'}</b> wisatawan: "
                 f"masuk {ringkas(r['Masuk'])}, keluar {ringkas(r['Keluar'])}, selisih {ringkas(abs(net))} perjalanan. "
                 f"Mitra terbesarnya adalah <b>{pf.index[0]}</b>.",
                 f"Dari seluruh perjalanan wisatawan asal {fokus}, {pct(r['Internal'] / (r['Internal'] + r['Keluar']), 0)} "
                 f"berakhir di provinsinya sendiri."]
    else:
        paras = ["Belum ada arus untuk ditafsirkan pada pengaturan ini."]
    judul_kartu("Interpretasi", "Apa arti pola arus ini?")
    html('<div class="fl-p">' + "".join(f"<p>{p}</p>" for p in paras) + "</div>")
    html(f"""
<div class="fl-top3">
  <div class="t">Tiga besar dari seluruh data</div>
  <div class="s">Bagian ini tidak berubah saat pengaturan di atas diubah.</div>
  <div class="fl-t3-grid">
    {kartu_top3("Negara asal terbanyak", top_neg, TOTAL_WISMAN)}
    {kartu_top3("Pintu masuk tersibuk", top_pin, TOTAL_WISMAN)}
    {kartu_top3("Pasangan provinsi terpadat", top_pair, TOTAL_ANTAR)}
  </div>
</div>""")