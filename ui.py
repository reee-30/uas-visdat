import re
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

JUDUL_SITUS = "Visualisasi Data Pariwisata Indonesia"

# ===================== VIDEO BERANDA =====================
VIDEO_FILE = "static/beranda.mp4"
VIDEO_YT_ID = "ojQbArbuN4E"   
VIDEO_MULAI = 0             
VIDEO_SELESAI = 60            

# Sumber data (muncul di kotak "Sumber data" yang bisa dilipat di setiap halaman).
SUMBER_BPS = [
    dict(judul="Jumlah Akomodasi, Kamar, dan Tempat Tidur yang Tersedia pada Hotel Bintang Menurut Provinsi",
         jenis="Tabel Statistik", tahun="2025", akses="2 Oktober 2026",
         url="https://www.bps.go.id/id/statistics-table/3/TjBWSldsWklZVnBXU1RKcVlsVTNSRXhpU2tzclFUMDkjMw==/jumlah-akomodasi--kamar--dan-tempat-tidur-yang-tersedia-pada-hotel-bintang-menurut-provinsi--2021.html"),
    dict(judul="Jumlah Akomodasi, Kamar, dan Tempat Tidur yang Tersedia pada Hotel Nonbintang dan Akomodasi Lainnya Menurut Provinsi",
         jenis="Tabel Statistik", tahun="2025", akses="2 Oktober 2026",
         url="https://www.bps.go.id/id/statistics-table/3/ZEdWTmFXVlpWMDFCUms5MFJuTTNabEIyVVZOSlVUMDkjMyMwMDAw/jumlah-akomodasi-kamar-dan-tempat-tidur-yang-tersedia-pada-hotel-nonbintang-dan-akomodasi-lainnya-menurut-provinsi.html"),
    dict(judul="Jumlah Perjalanan Wisatawan Nusantara Menurut Provinsi Tujuan (Perjalanan)",
         jenis="Tabel Statistik", tahun="2025", akses="2 Oktober 2026",
         url="https://www.bps.go.id/id/statistics-table/2/MjIwMSMy/jumlah-perjalanan-wisatawan-nusantara-menurut-provinsi-tujuan--perjalanan-.html"),
    dict(judul="Jumlah Perjalanan Wisatawan Nusantara Menurut Provinsi Asal (Perjalanan)",
         jenis="Tabel Statistik", tahun="2025", akses="2 Oktober 2026",
         url="https://www.bps.go.id/id/statistics-table/2/MTE4OSMy/jumlah-perjalanan-wisatawan-nusantara.html"),
    dict(judul="Statistik Wisatawan Nusantara 2025",
         jenis="Publikasi", tahun="2025", akses="2 Oktober 2026",
         url="https://www.bps.go.id/id/publication/2026/04/30/06948320ebe75b7678b09c56/statistik-wisatawan-nusantara-2025.html"),
    dict(judul="Statistik Indonesia 2026",
         jenis="Publikasi", tahun="2025 (terbit 2026)", akses="2 Oktober 2026",
         url="https://www.bps.go.id/id/publication/2026/02/27/a43f03f45543dc4e9942f44c/statistik-indonesia-2026.html"),
]

HOOK = "Jejak Wisata <em>Nusantara</em>"
SUBJUDUL = "Analisis Dinamika Pergerakan Wisatawan, Kapasitas Akomodasi, dan Karakteristik Wilayah di 38 Provinsi"
# =========================================================

# Satu entri = satu halaman. 'file' dicari di folder halaman/ lalu pages/.
HALAMAN = [
    dict(id="hierarki", nama="Hierarki", file="1_Hierarki.py", warna="#0F7C73",
         judul="Di Mana Kamar Hotel &amp; Wisatawan Menumpuk?",
         sub="Ketimpangan Fasilitas dan Karakter Wisatawan di Setiap Wilayah"),
    dict(id="flow", nama="Flow", file="2_Flow.py", warna="#0F7C73", story_sankey=True,
         judul="Ke Mana Wisatawan Mengalir?",
         sub="Pintu Masuk Wisman vs Perjalanan Melintas Batas Wisnus"),
    dict(id="multivariat", nama="Multivariat", file="3_Multivariat.py", warna="#0F7C73",
         judul="Provinsi Mana yang Serupa, Mana yang Menonjol?",
         sub="Meringkas 10 Indikator Pariwisata Menjadi Klaster Wilayah"),
]

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap');
:root{--bg:#F4F9F8;--card:#FFFFFF;--line:#D3E4E0;--acc:#0F7C73;--dk:#0B4F4A;--mint:#8CEBD8;--txt:#12302D;--mut:#4E6B67;--cell:8.5rem;}
html,[data-testid="stMain"],section.main{scroll-behavior:smooth;}
.stApp{background:linear-gradient(180deg,#F4F9F8 0%,#EAF4F1 100%);color:var(--txt);}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important;}
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="collapsedControl"],[data-testid="stSidebarNav"]{display:none!important;}
.block-container{max-width:1320px;padding:2rem 1.5rem 4rem!important;overflow-x:clip;}
.st-key-banner{position:relative;border-radius:26px;padding:2.4rem 2.6rem 2rem;margin:0 0 1.4rem;gap:.5rem!important;background:linear-gradient(135deg,color-mix(in srgb,var(--acc) 82%,black) 0%,var(--acc) 100%);box-shadow:0 12px 30px rgba(11,79,74,.18);}
.banner-in .t{font-family:'Outfit',sans-serif;font-size:clamp(1.8rem,3.6vw,3rem);font-weight:800;color:#fff;margin:0 0 .5rem;line-height:1.1;}
.banner-in .s{font-family:'Outfit',sans-serif;font-size:clamp(1rem,1.7vw,1.3rem);font-weight:400;color:rgba(255,255,255,.92);margin:0 0 1rem;line-height:1.4;max-width:46rem;}
.cerita{max-width:62rem;margin:0 0 .6rem;font-size:1.06rem;line-height:1.75;color:var(--txt);}
.cerita p{margin:0 0 .8rem;}
.cerita b{color:var(--dk);}
.bagian{margin:1.6rem 0 .2rem;}
.bagian h3{font-family:'Outfit',sans-serif;font-weight:700;font-size:1.4rem;color:var(--dk);line-height:1.25;margin:0;}
.bagian p{color:var(--mut);font-size:.98rem;line-height:1.6;margin:.25rem 0 0;max-width:62rem;}
.legenda{display:flex;flex-wrap:wrap;gap:.3rem 1.1rem;margin:.4rem 0 .5rem;font-size:.88rem;color:var(--mut);}
.legenda span{display:inline-flex;align-items:center;gap:.4rem;}
.legenda i{width:10px;height:10px;border-radius:50%;display:inline-block;}
[class*="st-key-navpill"]{box-sizing:border-box;padding:.35rem;border-radius:999px;background:rgba(5,36,34,.34);border:1px solid rgba(255,255,255,.28);}
[class*="st-key-navpill"] [data-testid="stHorizontalBlock"]{display:grid!important;grid-auto-flow:column;grid-auto-columns:minmax(0,var(--cell));gap:.3rem!important;}
[class*="st-key-navpill"] [data-testid="stColumn"]{width:100%!important;min-width:0!important;flex:none!important;}
[class*="st-key-navpill"] [data-testid="stElementContainer"],[class*="st-key-navpill"] [data-testid="stPageLink"]{width:100%;}
[class*="st-key-navpill"] a[data-testid="stPageLink-NavLink"]{box-sizing:border-box;width:100%;height:2.75rem;display:flex;align-items:center;justify-content:center;padding:0 .5rem;border-radius:999px;background:transparent;text-decoration:none;transition:background .15s;}
[class*="st-key-navpill"] a[data-testid="stPageLink-NavLink"] p{color:#fff!important;font-weight:600;font-size:.95rem;margin:0;white-space:nowrap;text-align:center;}
[class*="st-key-navpill"] a[data-testid="stPageLink-NavLink"]:hover{background:rgba(255,255,255,.18);}
[class*="st-key-navpill"] a[data-testid="stPageLink-NavLink"]:focus-visible{outline:2px solid #8CEBD8;outline-offset:2px;}
.pill-on{box-sizing:border-box;width:100%;height:2.75rem;display:flex;align-items:center;justify-content:center;border-radius:999px;background:#8CEBD8;color:#06332E;font-weight:600;font-size:.95rem;white-space:nowrap;}
.st-key-navpill_bab{width:min(100%,calc(4*var(--cell) + 1.6rem + 2px));margin-top:.3rem;}
.st-key-pager{margin-top:2rem;}
.st-key-pager [data-testid="stHorizontalBlock"]{display:flex!important;justify-content:space-between;align-items:center;gap:1rem!important;flex-wrap:nowrap!important;}
.st-key-pager [data-testid="stColumn"]{flex:0 0 auto!important;width:auto!important;min-width:0!important;}
.st-key-pager [data-testid="stElementContainer"],.st-key-pager [data-testid="stPageLink"]{width:auto;}
.st-key-pager a[data-testid="stPageLink-NavLink"]{width:fit-content;background:var(--card);border:1px solid var(--line);border-radius:999px;padding:.35rem 1rem;min-height:2.4rem;transition:all .15s;}
.st-key-pager a[data-testid="stPageLink-NavLink"]:hover{border-color:var(--acc);}
.st-key-pager a[data-testid="stPageLink-NavLink"]:focus-visible{outline:2px solid var(--acc);outline-offset:2px;}
.st-key-pager a[data-testid="stPageLink-NavLink"] p{font-family:'Outfit',sans-serif;font-weight:600;font-size:.88rem;color:var(--dk);margin:0;}
.st-key-sumber{margin-top:1.6rem;}
.st-key-sumber [data-testid="stExpander"]{border:1px solid var(--line)!important;border-radius:16px!important;background:#fff;}
.st-key-sumber [data-testid="stExpander"] summary p{font-family:'Outfit',sans-serif;font-weight:700;color:var(--dk);font-size:1.05rem;}
.srcbox{line-height:1.7;font-size:.92rem;color:var(--txt);}
.srcbox ol{margin:.5rem 0 0 1.1rem;padding:0;}
.srcbox li{margin-bottom:.8rem;}
.srcbox a{color:var(--acc);word-break:break-all;}
.srcbps{text-align:right;font-size:.8rem;font-style:italic;color:var(--mut);margin:-.5rem .4rem .2rem;}
h2,h3,[data-testid="stHeading"] h2,[data-testid="stHeading"] h3{font-family:'Outfit',sans-serif!important;color:var(--dk)!important;letter-spacing:-.01em;}
[data-testid="stMetric"]{background:#E9F4F1;border-radius:14px;padding:.85rem 1rem;}
[data-testid="stMetricValue"]{font-family:'Outfit',sans-serif;color:var(--dk);}
[data-testid="stPlotlyChart"]{background:#FFFFFF;border:1px solid var(--line);border-radius:16px;padding:.5rem;}
iframe{border-radius:16px;background:#fff;border:1px solid var(--line);}
[data-baseweb="select"]>div,[data-baseweb="input"]>div{border-radius:12px;}
[data-testid="stButtonGroup"]{flex-wrap:wrap;}
[class*="st-key-story_"]{display:grid!important;grid-template-columns:minmax(0,1fr);gap:0!important;margin:1rem 0 0;}
[class*="st-key-story_"]>*{grid-area:1/1;min-width:0;}
[class*="st-key-story_"]>*:first-child{position:sticky;top:84px;align-self:start;z-index:1;}
[class*="st-key-story_"]>*:nth-child(2){z-index:2;pointer-events:none;}
.story{padding:6vh 0 12vh;}
.step{pointer-events:auto;width:min(360px,92%);background:rgba(255,255,255,.93);backdrop-filter:blur(8px);border:1px solid var(--line);border-top:5px solid var(--acc);border-radius:18px;padding:1.3rem 1.5rem;margin:0 0 72vh;box-shadow:0 14px 34px rgba(11,79,74,.2);}
.step:nth-child(even){margin-left:auto;}
.step:last-child{margin-bottom:10vh;}
.step .n{font-family:'Outfit',sans-serif;font-weight:800;font-size:.78rem;letter-spacing:.14em;color:var(--acc);}
.step h4{font-family:'Outfit',sans-serif;font-size:1.3rem;color:var(--dk);margin:.3rem 0 .45rem;line-height:1.2;}
.step p{color:var(--mut);line-height:1.6;margin:0;font-size:1rem;}
@keyframes rise{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
@supports (animation-timeline:view()){.step{animation:rise linear both;animation-timeline:view();animation-range:entry 0% entry 55%;}}
[class*="st-key-dua_"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;}
[class*="st-key-dua_"] [data-testid="stColumn"]{flex:1 1 380px!important;min-width:min(100%,380px)!important;}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important;}}
@media(max-width:520px){.st-key-navpill_bab{width:100%;border-radius:26px;}.st-key-navpill_bab [data-testid="stHorizontalBlock"]{grid-auto-flow:row;grid-template-columns:repeat(2,minmax(0,1fr));}}
@media(max-width:900px){[class*="st-key-story_"]{display:block!important;}[class*="st-key-story_"]>*:first-child{position:static;}[class*="st-key-story_"]>*:nth-child(2){pointer-events:auto;}.step{width:100%;margin:0 0 1rem!important;}.story{padding:1rem 0;}}
@media(max-width:760px){.st-key-banner{padding:1.5rem 1.2rem 1.3rem;}[class*="st-key-navpill"] a[data-testid="stPageLink-NavLink"] p,.pill-on{font-size:.8rem;}.block-container{padding:1.2rem .8rem 3rem!important;}.cerita{font-size:1rem;}.bagian h3{font-size:1.2rem;}}
"""

_PAGES = {}  # diisi di jalankan(): id halaman -> objek st.Page


# ---------------- helper ----------------
def _html(s: str):
    """Satukan baris-baris HTML jadi satu baris agar tidak dibaca sebagai kode oleh markdown."""
    st.markdown("".join(x.strip() for x in s.splitlines()), unsafe_allow_html=True)


def _angka(x, fmt=",.0f"):
    return format(x, fmt).replace(",", "_").replace(".", ",").replace("_", ".")


def _ringkas(x):
    if x >= 1e9:
        return _angka(x / 1e9, ",.2f") + " miliar"
    if x >= 1e6:
        return _angka(x / 1e6, ",.1f") + " juta"
    return _angka(x)


# ---------------- komponen bersama (semua halaman) ----------------
def _css():
    css = "".join(x.strip() for x in CSS.splitlines())
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _pil_halaman(key, aktif, beranda=True):
    """Kapsul navigasi antarhalaman. Halaman aktif ditampilkan sebagai label (bukan tombol)."""
    item = ([("beranda", "Beranda")] if beranda else []) + [(h["id"], h["nama"]) for h in HALAMAN]
    with st.container(key=key):
        kol = st.columns(len(item))
        for k, (i, nama) in zip(kol, item):
            with k:
                if i == aktif:
                    _html(f'<div class="pill-on">{nama}</div>')
                else:
                    st.page_link(_PAGES[i], label=nama)


def _sumber():
    daftar = "".join(
        f'<li><b>{x["judul"]}</b> ({x["jenis"]}, {x["tahun"]})<br>'
        f'URL: <a href="{x["url"]}" target="_blank" rel="noopener">{x["url"]}</a><br>'
        f'Tanggal akses: {x["akses"]}</li>' for x in SUMBER_BPS)
    with st.container(key="sumber"):
        with st.expander("Sumber data", expanded=False):
            _html(f'<div class="srcbox"><b>Sumber: BPS</b><ol>{daftar}</ol></div>')


def _cap_bps(fig=None):
    try:
        ann = (fig.get("layout", {}).get("annotations") if isinstance(fig, dict) else fig.layout.annotations) or []
        for a in ann:
            t = a.get("text") if isinstance(a, dict) else getattr(a, "text", "")
            if "Sumber: BPS" in (t or ""):
                return
    except Exception:
        pass
    _html('<div class="srcbps">Sumber: BPS</div>')


# ---------------- halaman: BERANDA ----------------
CSS_BERANDA = """
.stApp .block-container{padding:0!important;max-width:100%!important;}
html,body,.stApp,[data-testid="stMain"]{overflow:hidden!important;}
.st-key-hero{position:fixed!important;top:0;left:0;width:100vw;height:100vh;z-index:1;}
.st-key-hero [data-testid="stElementContainer"]{height:100vh;width:100%;}
.st-key-navpill_hero{position:fixed!important;bottom:2rem;left:50%;transform:translateX(-50%);width:min(92vw,calc(3*var(--cell) + 1.3rem + 2px));z-index:60;}
.st-key-hero iframe{width:100%!important;height:100vh!important;border:0!important;border-radius:0!important;background:#0B4F4A;}
"""

HERO_TPL = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;font-family:'Outfit',sans-serif;background:#0B4F4A;color:#fff}
.stage{position:relative;height:100vh;min-height:540px;overflow:hidden;background:linear-gradient(150deg,#0B4F4A 0%,#0F7C73 58%,#2FA89A 100%)}
video{position:absolute;top:50%;left:50%;min-width:100%;min-height:100%;width:auto;height:auto;transform:translate(-50%,-50%);object-fit:cover}
.yt{position:absolute;top:50%;left:50%;width:max(100%,177.78vh);height:max(100%,56.25vw);transform:translate(-50%,-50%);border:0;pointer-events:none}
.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(4,34,32,.40) 0%,rgba(4,34,32,.50) 40%,rgba(4,34,32,.90) 100%)}
.content{position:relative;height:100%;display:flex;flex-direction:column;padding:0 clamp(1.4rem,6vw,5.5rem) 6.5rem}
.main{flex:1;display:flex;flex-direction:column;justify-content:center;gap:2.6rem;padding-top:1rem}
h1{font-weight:800;font-size:clamp(2.4rem,6vw,5.2rem);line-height:1.04;max-width:15em;letter-spacing:-.015em;text-shadow:0 2px 24px rgba(0,0,0,.35)}
h1 em{font-style:normal;color:#8CEBD8}
.hl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:2rem;max-width:960px}
.sub{margin-top:1.1rem;max-width:36em;font-size:clamp(1rem,1.9vw,1.45rem);line-height:1.5;color:#D8F3EE;font-weight:400}
.card{border-left:3px solid #8CEBD8;padding:.1rem 0 .1rem 1rem}
.card b{display:block;font-weight:800;font-size:clamp(1.7rem,3vw,2.6rem);line-height:1.1;color:#fff}
.card span{display:block;margin-top:.3rem;font-size:.95rem;line-height:1.4;color:#D8F3EE}
@keyframes up{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}
.up{animation:up .9s cubic-bezier(.2,.7,.2,1) both}
@media(max-width:760px){.hl{grid-template-columns:1fr;gap:.8rem}.card b{display:inline;font-size:1.5rem}.card span{display:inline;margin-left:.5rem;font-size:.88rem}.main{gap:1.4rem}}
</style></head><body>
<div class="stage">
  __LATAR__
  <div class="shade"></div>
  <div class="content">
    <div class="main">
      <div class="up"><h1>__HOOK__</h1><p class="sub">__SUB__</p></div>
      <div class="hl">__KARTU__</div>
    </div>
  </div>
</div>
__JS__
</body></html>"""


@st.cache_data
def _highlight():
    """Tiga angka beranda, dihitung dari data."""
    try:
        w = pd.read_csv("data/processed/hierarki_wisnus.csv")
        m = pd.read_csv("data/processed/hierarki_menginap.csv")
        m = m[m["Asal"] == "Gabungan"]
        a = (_ringkas(w["Jumlah"].sum()), "perjalanan wisatawan nusantara")
        b = (_angka(m["Kamar"].sum()), "kamar hotel bintang dan nonbintang")
        c = (str(w["Provinsi"].nunique()), "provinsi diobservasi")
    except Exception:
        a, b, c = ("—", "perjalanan wisatawan nusantara"), ("—", "kamar hotel"), ("38", "provinsi diobservasi")
    return [a, b, c]


def _latar_video():
    if Path(VIDEO_FILE).exists():
        src = "/app/" + VIDEO_FILE.replace("\\", "/")
        loop = "" if VIDEO_SELESAI else " loop"
        html = f'<video id="v" autoplay muted playsinline{loop} preload="auto"><source src="{src}"></video>'
        js = (f"<script>var v=document.getElementById('v');if(v){{var S={VIDEO_MULAI},E={VIDEO_SELESAI};"
              "v.addEventListener('loadedmetadata',function(){if(S){v.currentTime=S;}});"
              "v.addEventListener('timeupdate',function(){if(E&&v.currentTime>=E){v.currentTime=S;}});"
              "v.addEventListener('ended',function(){v.currentTime=S;v.play();});"
              "var p=v.play();if(p&&p.catch){p.catch(function(){});}}</script>")
        return html, js
    if VIDEO_YT_ID:
        q = (f"autoplay=1&mute=1&controls=0&loop=1&playlist={VIDEO_YT_ID}&start={VIDEO_MULAI}"
             + (f"&end={VIDEO_SELESAI}" if VIDEO_SELESAI else "")
             + "&modestbranding=1&playsinline=1&rel=0&disablekb=1&iv_load_policy=3")
        return (f'<iframe class="yt" src="https://www.youtube-nocookie.com/embed/{VIDEO_YT_ID}?{q}" '
                'allow="autoplay; encrypted-media" referrerpolicy="strict-origin-when-cross-origin"></iframe>'), ""
    return "", ""


def _hero_html():
    latar, js = _latar_video()
    kartu = "".join(
        f'<div class="card up" style="animation-delay:{0.45 + i * 0.12:.2f}s"><b>{n}</b><span>{k}</span></div>'
        for i, (n, k) in enumerate(_highlight())
    )
    return (HERO_TPL.replace("__LATAR__", latar)
            .replace("__HOOK__", HOOK).replace("__SUB__", SUBJUDUL).replace("__KARTU__", kartu)
            .replace("__JS__", js))


def _beranda():
    css = "".join(x.strip() for x in CSS_BERANDA.splitlines())
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    with st.container(key="hero"):
        components.html(_hero_html(), height=720, scrolling=False)
    _pil_halaman("navpill_hero", aktif="beranda", beranda=False)


# ---------------- halaman: BAB (Hierarki / Flow / Multivariat) ----------------
def _banner(h):
    with st.container(key="banner"):
        _html(f'<div class="banner-in"><div class="t">{h["judul"]}</div><div class="s">{h["sub"]}</div></div>')
        _pil_halaman("navpill_bab", aktif=h["id"])


def _pager(idx):
    sebelum = _PAGES["beranda"] if idx == 0 else _PAGES[HALAMAN[idx - 1]["id"]]
    nama_sebelum = "Beranda" if idx == 0 else HALAMAN[idx - 1]["nama"]
    with st.container(key="pager"):
        kiri, kanan = st.columns(2)
        with kiri:
            st.page_link(sebelum, label=f"← {nama_sebelum}")
        with kanan:
            if idx < len(HALAMAN) - 1:
                st.page_link(_PAGES[HALAMAN[idx + 1]["id"]], label=f"{HALAMAN[idx + 1]['nama']} →")
            else:
                st.page_link(_PAGES["beranda"], label="Beranda →")


def _cari(nama_file):
    for folder in ("halaman", "pages"):
        p = Path(folder) / nama_file
        if p.exists():
            return p
    return None


def _narasi(h):
    butir = st.session_state.get(f"narasi_{h['id']}") or []
    if not butir:
        return
    isi = ""
    for i, b in enumerate(butir, 1):
        label, judul, teks = b if len(b) == 3 else (f"LANGKAH {i}", *b)
        isi += f'<div class="step"><div class="n">{label}</div><h4>{judul}</h4><p>{teks}</p></div>'
    _html(f'<div class="story" style="--acc:{h["warna"]}">{isi}</div>')


def _adalah_sankey(fig):
    try:
        data = fig["data"] if isinstance(fig, dict) else fig.data
        return any((t.get("type") if isinstance(t, dict) else getattr(t, "type", None)) == "sankey"
                   for t in data)
    except Exception:
        return False


def _jalankan(h):
    p = _cari(h["file"])
    if p is None:
        st.warning(f"File halaman {h['file']} tidak ditemukan di folder halaman/ atau pages/.")
        return
    kode = re.sub(r"\bst\.(set_page_config|title)\(", "_abaikan(", p.read_text(encoding="utf-8"))
    ruang = {"__name__": "__main__", "__file__": str(p), "_abaikan": lambda *a, **k: None}

    asli = st.plotly_chart
    asli_html = components.html
    status = {"sudah": False}

    def pembungkus(fig=None, *a, **k):
        if h.get("story_sankey") and not status["sudah"] and _adalah_sankey(fig):
            status["sudah"] = True
            with st.container(key=f"story_{h['id']}"):
                with st.container(key=f"kanan_{h['id']}"):
                    hasil = asli(fig, *a, **k)
                    _cap_bps(fig)
                _narasi(h)
            return hasil
        hasil = asli(fig, *a, **k)
        _cap_bps(fig)
        return hasil

    def pembungkus_html(*a, **k):  
        hasil = asli_html(*a, **k)
        _cap_bps()
        return hasil

    st.plotly_chart = pembungkus
    components.html = pembungkus_html
    try:
        exec(compile(kode, str(p), "exec"), ruang)
    except Exception as e: 
        st.error(f"Halaman {h['nama']} gagal dimuat.")
        st.exception(e)
    finally:
        st.plotly_chart = asli
        components.html = asli_html


def _buat_halaman(idx):
    h = HALAMAN[idx]

    def tampil():
        _banner(h)
        _jalankan(h)
        _sumber()
        _pager(idx)

    return tampil


# ---------------- titik masuk ----------------
def jalankan():
    st.set_page_config(
        page_title=JUDUL_SITUS, layout="wide",
        initial_sidebar_state="collapsed",
    )
    _PAGES.clear()
    _PAGES["beranda"] = st.Page(_beranda, title="Beranda", url_path="beranda", default=True)
    for i, h in enumerate(HALAMAN):
        _PAGES[h["id"]] = st.Page(_buat_halaman(i), title=h["nama"], url_path=h["id"])
    try:
        pg = st.navigation(list(_PAGES.values()), position="hidden")
    except TypeError:  # Streamlit lama tanpa parameter position
        pg = st.navigation(list(_PAGES.values()))
    _css()
    pg.run()


jalankan_beranda = jalankan 