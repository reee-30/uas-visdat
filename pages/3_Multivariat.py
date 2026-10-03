import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from scipy.stats import chi2
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Multivariat - Profil Provinsi", page_icon="📊", layout="wide")

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "processed" / "multivariat_provinsi.csv"

# ------------------------------------------------------------------ konstanta
MAIN = [
    "TPK_Bintang", "TPK_NonBintang",
    "Akomodasi_Bintang", "Akomodasi_NonBintang",
    "Kamar_Bintang", "Kamar_NonBintang",
    "TempatTidur_Bintang", "TempatTidur_NonBintang",
    "LamaMenginap_Bintang", "LamaMenginap_NonBintang",
]
BINTANG = [v for v in MAIN if v.endswith("_Bintang")]
NONBINTANG = [v for v in MAIN if v.endswith("_NonBintang")]
COUNT_VARS = [v for v in MAIN if v.split("_")[0] in ("Akomodasi", "Kamar", "TempatTidur")]
TPK_VARS = ["TPK_Bintang", "TPK_NonBintang"]
STAY_VARS = ["LamaMenginap_Bintang", "LamaMenginap_NonBintang"]

LABEL = {
    "TPK_Bintang": "TPK Bintang (%)", "TPK_NonBintang": "TPK Nonbintang (%)",
    "Akomodasi_Bintang": "Akomodasi Bintang (unit)", "Akomodasi_NonBintang": "Akomodasi Nonbintang (unit)",
    "Kamar_Bintang": "Kamar Bintang (unit)", "Kamar_NonBintang": "Kamar Nonbintang (unit)",
    "TempatTidur_Bintang": "Tempat Tidur Bintang (unit)", "TempatTidur_NonBintang": "Tempat Tidur Nonbintang (unit)",
    "LamaMenginap_Bintang": "Lama Menginap Bintang (hari)", "LamaMenginap_NonBintang": "Lama Menginap Nonbintang (hari)",
}
NAME = {v: re.sub(r"\s*\(.*\)", "", LABEL[v]) for v in MAIN}   # label tanpa satuan
UNIT = {v: re.search(r"\((.*)\)", LABEL[v]).group(1) for v in MAIN}
SHORT = {  # label pendek untuk panah biplot
    "TPK_Bintang": "TPK-B", "TPK_NonBintang": "TPK-NB",
    "Akomodasi_Bintang": "Akom-B", "Akomodasi_NonBintang": "Akom-NB",
    "Kamar_Bintang": "Kamar-B", "Kamar_NonBintang": "Kamar-NB",
    "TempatTidur_Bintang": "TT-B", "TempatTidur_NonBintang": "TT-NB",
    "LamaMenginap_Bintang": "Lama-B", "LamaMenginap_NonBintang": "Lama-NB",
}
PAR_LABEL = {  # label dua baris yang ringkas untuk sumbu parallel coordinates
    "TPK_Bintang": "TPK<br>B", "TPK_NonBintang": "TPK<br>NB",
    "Akomodasi_Bintang": "Akom.<br>B", "Akomodasi_NonBintang": "Akom.<br>NB",
    "Kamar_Bintang": "Kamar<br>B", "Kamar_NonBintang": "Kamar<br>NB",
    "TempatTidur_Bintang": "T.Tidur<br>B", "TempatTidur_NonBintang": "T.Tidur<br>NB",
    "LamaMenginap_Bintang": "Lama<br>B", "LamaMenginap_NonBintang": "Lama<br>NB",
}
HEAT_LABEL = {v: NAME[v].replace(" ", "<br>", 1) for v in MAIN}

CUSTOM = "Pilih sendiri…"
PRESETS = {
    "Semua indikator (10)": MAIN,
    "Hanya hotel Bintang": BINTANG,
    "Hanya hotel Nonbintang": NONBINTANG,
    "Kapasitas (akomodasi, kamar, tempat tidur)": COUNT_VARS,
    "Kinerja (TPK dan lama menginap)": TPK_VARS + STAY_VARS,
    "TPK, lama menginap, dan kamar": TPK_VARS + STAY_VARS + ["Kamar_Bintang", "Kamar_NonBintang"],
}

# Palet Okabe-Ito (ramah buta warna)
CL_COLORS = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]
PROV_COLORS = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00", "#56B4E9"]
ACCENT, HL_COLOR, DIM_COLOR = "#0F7C73", "#D55E00", "#C8C8C8"

CSS = """
[class*="st-key-kartu_"]{background:#fff;border:1px solid var(--line);border-radius:18px;padding:1.3rem 1.4rem 1.1rem;margin:0 0 .4rem;}
[class*="st-key-kartu_"] [data-testid="stPlotlyChart"]{border:none;box-shadow:none;padding:0;border-radius:0;}
.kartu-judul{font-family:'Outfit',sans-serif;font-weight:700;font-size:1.3rem;color:var(--dk);margin:0;line-height:1.25;}
.kartu-sub{color:var(--mut);margin:.15rem 0 .9rem;font-size:.95rem;line-height:1.55;}
.mv-p p{margin:0 0 .8rem;line-height:1.75;font-size:1.02rem;color:var(--txt);}
.mv-p b{color:var(--dk);}
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:0 0 1.2rem;}
.kpi{background:#fff;border:1px solid var(--line);border-radius:16px;padding:1rem 1.2rem 1.05rem;}
.kpi .n{font-family:'Outfit',sans-serif;font-weight:800;font-size:2rem;line-height:1.1;color:var(--dk);}
.kpi .l{font-weight:700;color:var(--txt);margin-top:.25rem;}
.kpi .s{color:var(--mut);font-size:.85rem;line-height:1.45;margin-top:.15rem;}
.badge{display:inline-flex;align-items:center;gap:.55rem;font-family:'Outfit',sans-serif;font-weight:700;font-size:1.2rem;color:var(--dk);margin:0 0 .5rem;}
.badge i{width:15px;height:15px;border-radius:50%;display:inline-block;}
.tbl-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:14px;}
.tbl{width:100%;border-collapse:collapse;font-size:.82rem;}
.tbl th{background:#E9F4F1;color:var(--mut);font-weight:600;text-align:right;padding:.55rem .45rem;line-height:1.25;border-bottom:1px solid var(--line);}
.tbl td{padding:.75rem .45rem;text-align:right;border-bottom:1px solid var(--line);color:var(--txt);}
.tbl tr:last-child td{border-bottom:none;}
.tbl th:first-child,.tbl td:first-child{text-align:left;padding-left:.8rem;}
.tbl .kl{font-weight:700;color:var(--dk);white-space:nowrap;}
.tbl .kl i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:.45rem;}
.tbl .u{font-weight:400;font-size:.72rem;}
@media(max-width:760px){.kpi-grid{grid-template-columns:1fr;}[class*="st-key-kartu_"]{padding:1rem 1rem .8rem;}}
"""


def html(s: str):
    """Gabungkan baris HTML jadi satu baris agar tidak dibaca sebagai blok kode oleh markdown."""
    st.markdown("".join(x.strip() for x in s.splitlines()), unsafe_allow_html=True)


def fid(x: float, nd: int = 1, sign: bool = False) -> str:
    """Format angka dengan koma desimal (gaya Indonesia)."""
    s = f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"
    return s.replace(".", ",")


# ------------------------------------------------------------------ data & analisis
@st.cache_data
def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def _standardize(use_log: bool):
    df = load_data()
    X = df[MAIN].astype(float).copy()
    if use_log:
        X[COUNT_VARS] = np.log1p(X[COUNT_VARS])
    Z = pd.DataFrame(StandardScaler().fit_transform(X), columns=MAIN, index=df["Provinsi"])
    return df, Z


@st.cache_data
def compute(use_log: bool, k: int) -> dict:
   
    df, Z = _standardize(use_log)
    pca = PCA().fit(Z.values)
    sc = pca.transform(Z.values)
    for j in range(sc.shape[1]):
        if pca.components_[j].sum() < 0:
            sc[:, j] *= -1

    Zl = linkage(Z.values, method="ward")
    raw = fcluster(Zl, k, criterion="maxclust")
    labs = np.array(sorted(set(raw)))
    labs = labs[np.argsort([sc[raw == c, 0].mean() for c in labs])]   
    remap = {c: i + 1 for i, c in enumerate(labs)}
    cluster = np.array([remap[c] for c in raw])
    sil = float(silhouette_score(Z.values, cluster))

    m = 3  
    mahal = np.sqrt(((sc[:, :m] / np.sqrt(pca.explained_variance_[:m])) ** 2).sum(axis=1))
    thr = float(np.sqrt(chi2.ppf(0.975, m)))

    out = df.copy()
    out["cluster"], out["mahal"], out["outlier"] = cluster, mahal, mahal > thr
    return dict(df=out, Z=Z, var=pca.explained_variance_ratio_, sil=sil, thr=thr,
                leaves=dendrogram(Zl, no_plot=True)["leaves"])


@st.cache_data
def pca_subset(use_log: bool, vars_: tuple) -> dict:
   
    _, Z = _standardize(use_log)
    cols = list(vars_)
    pca = PCA(n_components=2).fit(Z[cols].values)
    sc = pca.transform(Z[cols].values)
    load = pca.components_.T * np.sqrt(pca.explained_variance_)
    for j in range(2):
        if load[:, j].sum() < 0:
            load[:, j] *= -1
            sc[:, j] *= -1
    return dict(scores=sc, load=pd.DataFrame(load, index=cols, columns=["PC1", "PC2"]),
                var=pca.explained_variance_ratio_, vars=cols)


def level(z: float) -> str:
    return ("sangat tinggi" if z > 1 else "tinggi" if z > 0.3 else "sedang" if z > -0.3
            else "rendah" if z > -1 else "sangat rendah")


# ------------------------------------------------------------------ util figur
def add_source(fig, y):
    fig.add_annotation(text="Sumber: BPS", xref="paper", yref="paper", x=1, y=y, xanchor="right",
                       yanchor="top", showarrow=False, font=dict(size=10, color="#555"))


def discrete_scale(colors):
    n = len(colors)
    return [pair for i, c in enumerate(colors) for pair in ([i / n, c], [(i + 1) / n, c])]


def group_arrow_tips(load: pd.DataFrame, scale: float, tol: float):
 
    groups = []
    for v in load.index:
        p = np.array([load.loc[v, "PC1"], load.loc[v, "PC2"]]) * scale
        for g in groups:
            if np.linalg.norm(g["pos"] - p) < tol:
                g["vars"].append(v)
                g["pos"] = np.mean([g["pos"], p], axis=0)
                break
        else:
            groups.append(dict(pos=p, vars=[v]))
    return groups


# ------------------------------------------------------------------ figur
def fig_biplot(res, sub, sel, all_labels):
    d = res["df"]
    sc, load, var = sub["scores"], sub["load"], sub["var"]
    has = len(sel) > 0
    is_sel = d["Provinsi"].isin(sel).values
    is_out = d["outlier"].values
    labels = [p if (all_labels or s or o) else "" for p, s, o in zip(d["Provinsi"], is_sel, is_out)]
    custom = np.column_stack([d["cluster"]])

    fig = go.Figure()
    fig.add_trace(go.Scatter(  
        x=sc[:, 0], y=sc[:, 1], mode="markers+text", text=labels, textposition="top center",
        textfont=dict(size=11), hovertext=d["Provinsi"], customdata=custom,
        marker=dict(
            color=[CL_COLORS[c - 1] for c in d["cluster"]], size=13,
            symbol=np.where(is_out, "diamond", "circle").tolist(),
            opacity=np.where(is_sel | (not has), 0.95, 0.3).tolist(),
            line=dict(width=np.where(is_sel, 3, 0.8).tolist(),
                      color=np.where(is_sel, "#000000", "#FFFFFF").tolist()),
        ),
        hovertemplate=("<b>%{hovertext}</b><br>Klaster %{customdata[0]:.0f}"
                       "<br>PC1: %{x:.2f} · PC2: %{y:.2f}<extra></extra>"),
        showlegend=False,
    ))
    for c in range(1, res["k"] + 1):  
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers", name=f"Klaster {c}",
                                 marker=dict(color=CL_COLORS[c - 1], size=10), hoverinfo="skip"))

    lim = np.abs(sc).max()
    scale = 0.85 * lim / np.abs(load.values).max()
    for g in group_arrow_tips(load, scale, tol=0.09 * lim):
        for v in g["vars"]:
            fig.add_annotation(x=load.loc[v, "PC1"] * scale, y=load.loc[v, "PC2"] * scale, ax=0, ay=0,
                               xref="x", yref="y", axref="x", ayref="y", showarrow=True, text="",
                               arrowhead=2, arrowwidth=1.3, arrowcolor="#555")
        fig.add_annotation(x=g["pos"][0], y=g["pos"][1], text="<br>".join(SHORT[v] for v in g["vars"]),
                           showarrow=False, xanchor="left" if g["pos"][0] >= 0 else "right",
                           yanchor="bottom" if g["pos"][1] >= 0 else "top",
                           font=dict(size=10, color="#222"), bgcolor="rgba(255,255,255,0.75)")

    fig.update_layout(
        template="plotly_white", height=540, margin=dict(l=10, r=10, t=40, b=55),
        xaxis=dict(title=f"PC1 ({var[0] * 100:.1f}% informasi)"),
        yaxis=dict(title=f"PC2 ({var[1] * 100:.1f}% informasi)"),
        legend=dict(orientation="h", y=1.1, x=0),
        dragmode="select", clickmode="event+select",  
    )
    add_source(fig, -0.14)
    return fig


def fig_parallel(res, sel, vars_):
    d, Z, k = res["df"], res["Z"], res["k"]
    is_sel = d["Provinsi"].isin(sel).values
    order = np.argsort(is_sel, kind="stable") 
    if sel:
        cv, colors = is_sel[order].astype(float), [DIM_COLOR, HL_COLOR]
    else:
        cv, colors = (d["cluster"].values[order] - 1).astype(float), CL_COLORS[:k]
    zmin, zmax = float(Z[vars_].values.min()), float(Z[vars_].values.max())
    lo, hi = zmin - 1.0, zmax + 1.0  
    ticks = list(range(int(np.ceil(zmin)), int(np.floor(zmax)) + 1))
    dims = [dict(label=PAR_LABEL[v], values=Z[v].values[order], range=[lo, hi],
                 tickvals=ticks, ticktext=[f"{t:+d}" if t else "0" for t in ticks]) for v in vars_]
    fig = go.Figure(go.Parcoords(
        line=dict(color=cv, colorscale=discrete_scale(colors), cmin=-0.5, cmax=len(colors) - 0.5),
        dimensions=dims, labelfont=dict(size=11), tickfont=dict(size=10), labelside="top",
    ))
    fig.update_layout(template="plotly_white", height=540, margin=dict(l=40, r=40, t=110, b=70))
    add_source(fig, -0.06)
    return fig


def fig_bars(res, sel):
    d, Z, k = res["df"], res["Z"], res["k"]
    series = []   
    if not sel:
        for c in range(1, k + 1):
            m = d["cluster"].values == c
            series.append((f"Klaster {c}", Z[m].mean(), d.loc[m, MAIN].mean(), CL_COLORS[c - 1]))
    elif len(sel) <= 6:
        for i, p in enumerate(sel):
            series.append((p, Z.loc[p], d.set_index("Provinsi").loc[p, MAIN], PROV_COLORS[i]))
    else:
        m = d["Provinsi"].isin(sel).values
        series.append((f"Rata-rata {len(sel)} provinsi disorot", Z[m].mean(), d.loc[m, MAIN].mean(), ACCENT))

    ylab = [NAME[v] for v in MAIN]
    units = [UNIT[v] for v in MAIN]
    fig = go.Figure()
    for nm, z, raw, col in series:
        fig.add_trace(go.Bar(
            y=ylab, x=z.values, orientation="h", name=nm, marker_color=col,
            customdata=np.column_stack([raw.values.astype(float), units]),
            text=[fid(x, 1, True) for x in z.values] if len(series) == 1 else None,
            textposition="outside", cliponaxis=False,
            hovertemplate="<b>" + nm + "</b><br>%{y}<br>z-score: %{x:.2f}"
                          "<br>Nilai asli: %{customdata[0]} %{customdata[1]}<extra></extra>",
        ))
    lim = max(2.0, max(np.abs(z.values).max() for _, z, _, _ in series)) + 0.7
    fig.add_vline(x=0, line=dict(color="#333", width=1.5))
    fig.update_layout(
        template="plotly_white", barmode="group", height=max(440, 110 + 10 * (len(series) * 13 + 12)),
        margin=dict(l=10, r=20, t=40, b=70), legend=dict(orientation="h", y=1.07, x=0),
        xaxis=dict(range=[-lim, lim], dtick=1, zeroline=False, title="z-score (0 = rata-rata seluruh provinsi)"),
        yaxis=dict(autorange="reversed", automargin=True),
    )
    add_source(fig, -0.16)
    return fig


def fig_heatmap(res, sel):
    d, Z = res["df"], res["Z"]
    idx = [i for i in res["leaves"] if (not sel or d["Provinsi"].iat[i] in sel)]
    names = d["Provinsi"].values[idx].tolist()
    clus = d["cluster"].values[idx]
    raw = d[MAIN].values[idx]
    n = len(names)
    text = [[f"<b>{names[i]}</b> (Klaster {clus[i]})<br>{LABEL[v]}: {raw[i, j]:,.2f}"
             for j, v in enumerate(MAIN)] for i in range(n)]
    height = max(320, 28 * n + 200)
    fig = go.Figure(go.Heatmap(
        z=Z.values[idx], x=[HEAT_LABEL[v] for v in MAIN], y=names, text=text,
        colorscale="RdBu_r", zmin=-3, zmax=3, zmid=0, xgap=2, ygap=2,
        texttemplate="%{z:.1f}", textfont=dict(size=11 if n <= 20 else 9),
        hovertemplate="%{text}<br>z-score: %{z:.2f}<extra></extra>",
        colorbar=dict(title=dict(text="z-score", side="top"), orientation="h", x=0.5, xanchor="center",
                      y=-0.04, yanchor="top", len=0.6, thickness=12,
                      tickvals=[-3, -2, -1, 0, 1, 2, 3], ticktext=["≤-3", "-2", "-1", "0", "1", "2", "≥3"]),
    ))
    ticktext = [f'<span style="color:{CL_COLORS[c - 1]}">●</span> {nm}' for nm, c in zip(names, clus)]
    fig.update_xaxes(side="top", tickfont=dict(size=11), showgrid=False)
    fig.update_yaxes(autorange="reversed", tickmode="array", tickvals=names, ticktext=ticktext,
                     tickfont=dict(size=11), automargin=True, showgrid=False)
    fig.update_layout(template="plotly_white", height=height, margin=dict(l=10, r=10, t=80, b=120))
    add_source(fig, -0.04 - 70 / height)
    return fig


# ------------------------------------------------------------------ callback brushing & linking
def _on_biplot_select():
    ev = st.session_state.get("biplot")
    pts = ev.get("selection", {}).get("points", []) if ev else []
    names = load_data()["Provinsi"].tolist()
    idx = sorted({p.get("point_index") for p in pts if p.get("curve_number", 0) == 0} - {None})
    st.session_state["sel"] = [names[i] for i in idx]


def var_picker(title: str, key: str, min_vars: int):
    """Dropdown preset indikator (+ opsi pilih sendiri)."""
    choice = st.selectbox(title, list(PRESETS) + [CUSTOM], key=f"{key}_preset")
    if choice == CUSTOM:
        vars_ = st.multiselect("Indikator:", MAIN, default=TPK_VARS + STAY_VARS + ["Kamar_Bintang"],
                               format_func=lambda v: LABEL[v], key=f"{key}_custom")
    else:
        vars_ = PRESETS[choice]
    if len(vars_) < min_vars:
        st.warning(f"Pilih minimal {min_vars} indikator. Sementara semua indikator ditampilkan.")
        vars_ = MAIN
    return [v for v in MAIN if v in vars_]


def card_title(judul: str, sub: str = ""):
    if sub:
        html(f'<div class="kartu-judul">{judul}</div><div class="kartu-sub">{sub}</div>')
    else:
        html(f'<div class="kartu-judul" style="margin-bottom:.8rem">{judul}</div>')


# ------------------------------------------------------------------ teks interpretasi
_BASE = {"TPK": "TPK", "Akomodasi": "Akom.", "Kamar": "Kamar", "TempatTidur": "T. Tidur", "LamaMenginap": "Lama"}


def tabel_klaster(res) -> str:
    """Tabel HTML: baris = klaster, kolom = indikator, nilai = rata-rata klaster (satuan asli)."""
    d, k = res["df"], res["k"]
    head = "".join(
        f"<th>{_BASE[v.split('_')[0]]} {'B' if v.endswith('_Bintang') else 'NB'}<br><span class='u'>{UNIT[v]}</span></th>"
        for v in MAIN)
    rows = ""
    for c in range(1, k + 1):
        m = d.loc[d["cluster"] == c, MAIN].mean()
        cells = ""
        for v in MAIN:
            if v in TPK_VARS:
                txt = fid(m[v], 1)
            elif v in STAY_VARS:
                txt = fid(m[v], 2)
            else:
                txt = f"{m[v]:,.0f}".replace(",", ".")
            cells += f"<td>{txt}</td>"
        rows += f'<tr><td class="kl"><i style="background:{CL_COLORS[c - 1]}"></i>Klaster {c}</td>{cells}</tr>'
    return f'<div class="tbl-wrap"><table class="tbl"><tr><th>Klaster</th>{head}</tr>{rows}</table></div>'


def tab_klaster(res, c):
    d, Z = res["df"], res["Z"]
    mem = d["cluster"].values == c
    zc = Z[mem].mean()
    s, t, l = zc[COUNT_VARS].mean(), zc[TPK_VARS].mean(), zc[STAY_VARS].mean()
    col = CL_COLORS[c - 1]
    html(f'<div class="badge"><i style="background:{col}"></i>Klaster {c} · {int(mem.sum())} provinsi</div>')
    html(f'<div class="mv-p"><p>Skala akomodasinya {level(s)}, TPK {level(t)}, dan lama menginap {level(l)}.</p>'
         f'<p>Anggota: {", ".join(d.loc[mem, "Provinsi"])}.</p></div>')


# ================================================================== UI
st.session_state.setdefault("sel", [])   # kosong = semua provinsi
st.markdown(f"<style>{''.join(x.strip() for x in CSS.splitlines())}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------- atur tampilan
html(" ".join("""<div class="cerita"><p>Satu provinsi bisa digambarkan oleh sepuluh angka sekaligus: TPK, jumlah akomodasi, kamar,
tempat tidur, dan lama menginap, masing-masing untuk hotel bintang dan nonbintang. Sepuluh angka itu sulit dibandingkan
satu per satu, jadi halaman ini meringkasnya menjadi satu peta kemiripan dan beberapa kelompok provinsi.</p>
<p>Pilih satu atau beberapa provinsi, dan semua grafik akan menyorotnya sekaligus.</p></div>""".split()))

with st.container(key="kartu_pengaturan"):
    card_title("Atur tampilan", "Pilih jumlah klaster dan provinsi yang ingin dilihat.")
    c1, c2, c3 = st.columns([1.4, 0.8, 1.2], vertical_alignment="center")
    k = c1.slider("Jumlah klaster", 3, 6, 3, key="k")
    use_log = c2.checkbox("Skala log", value=True, key="use_log",
                          help="Jumlah akomodasi, kamar, dan tempat tidur sangat timpang antarprovinsi "
                               "(Jawa Barat dan Bali jauh di atas yang lain). Skala log mencegah provinsi besar "
                               "mendominasi hasil PCA.")
    all_labels = c3.checkbox("Nama semua provinsi", value=False)
    st.multiselect("Pilih provinsi", options=sorted(load_data()["Provinsi"]), key="sel",
                   placeholder="Semua provinsi")
    sel = list(st.session_state["sel"])

res = compute(use_log, k)
res["k"] = k
d = res["df"]
out_names = d.loc[d["outlier"], "Provinsi"].tolist()
var2 = (res["var"][0] + res["var"][1]) * 100
sil_kata = "terpisah jelas" if res["sil"] > 0.5 else "cukup terpisah" if res["sil"] > 0.25 else "batas samar"
if not out_names:
    kpi_out = "0"
elif len(out_names) <= 2:
    kpi_out = ", ".join(out_names)
else:
    kpi_out = str(len(out_names))

# ---------------------------------------------------------------- ringkasan
html(f"""
<div class="kpi-grid">
  <div class="kpi"><div class="n">{fid(var2)}%</div><div class="l">Informasi tertangkap PCA</div><div class="s">10 indikator diringkas menjadi 2 sumbu</div></div>
  <div class="kpi"><div class="n">{k}</div><div class="l">Klaster</div><div class="s">Silhouette {fid(res['sil'], 2)}: {sil_kata}</div></div>
  <div class="kpi"><div class="n">{kpi_out}</div><div class="l">Pencilan</div><div class="s">{'Profil menyimpang jauh dari provinsi lain' if out_names else 'Tidak ada provinsi yang menyimpang jauh'}</div></div>
</div>
""")

cfg = {"displaylogo": False, "responsive": True}

# ---------------------------------------------------------------- biplot | parallel coordinates
with st.container(key="dua_mv"):
    left, right = st.columns(2, gap="medium")

with left:
    with st.container(key="kartu_biplot"):
        card_title("Peta kemiripan provinsi (Biplot PCA)", "Makin dekat dua titik, makin mirip profilnya. Tarik kotak untuk memilih beberapa provinsi; klik dua kali di area kosong untuk membatalkan.")
        bvars = var_picker("Indikator yang ditampilkan", "bip", min_vars=3)
        sub = pca_subset(use_log, tuple(bvars))
        st.plotly_chart(fig_biplot(res, sub, sel, all_labels), key="biplot", config=cfg, use_container_width=True,
                        on_select=_on_biplot_select, selection_mode=("points", "box", "lasso"))
        st.caption("Panah searah berarti berkaitan positif, berlawanan arah berarti berkaitan negatif. ◆ menandai pencilan.")

with right:
    with st.container(key="kartu_parallel"):
        card_title("Profil lintas indikator (Parallel Coordinates)", "Satu garis mewakili satu provinsi. B = Bintang, NB = Nonbintang; nilai berupa z-score, 0 = rata-rata seluruh provinsi.")
        pvars = var_picker("Indikator yang dibandingkan", "par", min_vars=2)
        st.plotly_chart(fig_parallel(res, sel, pvars), key="parallel", config=cfg, use_container_width=True)

# ---------------------------------------------------------------- interpretasi
with st.container(key="kartu_interpretasi"):
    card_title("Interpretasi")
    ukuran = d.groupby("cluster").size()
    kal = ", ".join(f"{n} provinsi di klaster {c}" for c, n in ukuran.items())
    kal = f"Dengan {k} klaster, provinsi terbagi menjadi {kal}."
    if out_names:
        kal += (f" {', '.join(out_names)} menyimpang jauh dari provinsi lain pada tiga sumbu utama PCA, "
                f"sehingga ditandai sebagai pencilan.")
    html(f'<div class="mv-p"><p>{kal}</p></div>')
    kiri, kanan = st.columns([1, 2.2], gap="large")
    with kiri:
        if out_names:
            st.markdown("**Pencilan**")
            out_tab = pd.DataFrame({"Provinsi": d.loc[d["outlier"], "Provinsi"].values,
                                    "Klaster": d.loc[d["outlier"], "cluster"].astype(int).values})
            st.dataframe(out_tab, hide_index=True, use_container_width=True, height=min(250, 38 + 35 * len(out_tab)))
        else:
            st.markdown("**Pencilan:** tidak ada.")
    with kanan:
        tabs = st.tabs([f"Klaster {c}" for c in range(1, k + 1)])
        for c, tb in zip(range(1, k + 1), tabs):
            with tb:
                tab_klaster(res, c)

# ---------------------------------------------------------------- heatmap
with st.container(key="kartu_heatmap"):
    card_title("Heatmap terklaster")
    st.plotly_chart(fig_heatmap(res, sel), key="heatmap", config=cfg, use_container_width=True)

# ---------------------------------------------------------------- tabel klaster | grafik batang
with st.container(key="kartu_profil"):
    card_title("Profil rata-rata klaster")
    kt, kg = st.columns([1.5, 1], gap="large", vertical_alignment="center")
    with kt:
        st.markdown("**Rata-rata indikator tiap klaster**")
        html(tabel_klaster(res))
    with kg:
        st.markdown("**Z-score provinsi terpilih**" if sel else "**Z-score rata-rata tiap klaster**")
        st.plotly_chart(fig_bars(res, sel), key="bars", config=cfg, use_container_width=True)