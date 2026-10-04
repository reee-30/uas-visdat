import base64
import re
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

JUDUL_SITUS = "Jejak Wisata Nusantara"

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
    dict(judul="Statistik Kunjungan Wisatawan Mancanegara 2024",
         jenis="Publikasi", tahun="2024 (terbit 2025)", akses="4 Oktober 2026", katalog="8401011, ISSN 2085-9309",
         url="https://www.bps.go.id/id/publication/2025/03/20/a85d584df19ea65a5e2b3d0b/statistik-kunjungan-wisatawan-mancanegara-2024.html"),
    dict(judul="Statistik Indonesia 2026",
         jenis="Publikasi", tahun="2025 (terbit 2026)", akses="2 Oktober 2026",
         url="https://www.bps.go.id/id/publication/2026/02/27/a43f03f45543dc4e9942f44c/statistik-indonesia-2026.html"),
]

HOOK = "Lihat Indonesia <em>Bergerak</em>"
SUBJUDUL = "Cerita di balik perjalanan wisata, pintu masuk, hotel, dan pola 38 provinsi"
# =========================================================

# Satu entri = satu halaman. 'file' dicari di folder halaman/ lalu pages/.
HALAMAN = [
    dict(id="hierarki", nama="Explore", file="1_Hierarki.py", warna="#0F7C73",
         judul="Di Mana Wisatawan <em>Berkumpul</em>?",
         sub="Dari kamar hotel sampai asal perjalanan, lihat siapa yang paling menonjol."),
    dict(id="flow", nama="Journey", file="2_Flow.py", warna="#0F7C73", story_sankey=True,
         judul="Ke Mana Wisatawan <em>Pergi</em>?",
         sub="Ikuti jejak wisman dari gerbang masuk dan perjalanan wisnus antarprovinsi."),
    dict(id="multivariat", nama="Patterns", file="3_Multivariat.py", warna="#0F7C73",
         judul="Provinsi yang <em>Mirip</em> atau Berbeda?",
         sub="Sepuluh indikator diringkas menjadi pola dan kelompok provinsi."),
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


_F = ['[class*="st-key-hn_box_filter"]', '[class*="st-key-fl_card_atur"]', '[class*="st-key-kartu_pengaturan"]']


def _kena(sub):
    """Terapkan selector `sub` hanya di dalam kotak filter."""
    return ",".join(f"{s} {sub}" for s in _F)


CSS_EXTRA = """
:root{--shadow:0 1px 0 rgba(11,79,74,.04),0 10px 28px rgba(11,79,74,.08);--ring:#B7DDD6;}
::selection{background:#8CEBD8;color:#06332E;}
.stApp{font-family:'Outfit','Source Sans Pro',sans-serif;}
.st-key-banner{padding:2.6rem 2.8rem 2.2rem!important;border-radius:28px;background:linear-gradient(135deg,#0A4B46 0%,#0F7C73 100%);box-shadow:0 18px 44px rgba(11,79,74,.28);overflow:hidden;}
.st-key-banner::after{content:"";position:absolute;right:-90px;top:-90px;width:320px;height:320px;border-radius:50%;background:radial-gradient(circle,rgba(140,235,216,.28),transparent 70%);pointer-events:none;}
.banner-in .t{font-size:clamp(2.1rem,4.4vw,3.5rem);letter-spacing:-.02em;margin:0 0 .5rem;text-shadow:0 0 28px rgba(140,235,216,.25);}
.banner-in .t em{font-style:normal;color:#8CEBD8;text-shadow:0 0 22px rgba(140,235,216,.6);}
.banner-in .s{font-size:clamp(.88rem,1.1vw,1rem);opacity:.85;max-width:38rem;margin:0 0 1.2rem;}
.st-key-tema{position:absolute;top:1.2rem;right:1.5rem;width:auto!important;z-index:5;}
.st-key-tema button{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.35);border-radius:999px;color:#fff;padding:.2rem .9rem;min-height:2.2rem;backdrop-filter:blur(6px);}
.st-key-tema button:hover{background:rgba(255,255,255,.26);border-color:#8CEBD8;color:#fff;}
.st-key-tema button p{color:#fff;font-size:.85rem;font-weight:600;margin:0;}
.sum-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.9rem;margin-top:1.2rem;}
.sum{background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.22);border-radius:16px;padding:.9rem 1.1rem 1rem;backdrop-filter:blur(8px);transition:transform .2s,background .2s;}
.sum:hover{transform:translateY(-3px);background:rgba(255,255,255,.14);}
.sum.on{background:rgba(140,235,216,.18);border-color:#8CEBD8;box-shadow:0 0 0 1px #8CEBD8 inset;}
.sum .k{font-size:.7rem;letter-spacing:.16em;font-weight:800;color:#8CEBD8;}
.sum .v{font-family:'Outfit',sans-serif;font-weight:800;font-size:1.75rem;color:#fff;line-height:1.15;margin:.15rem 0 .1rem;}
.sum .d{font-size:.84rem;color:rgba(255,255,255,.82);line-height:1.4;}
.cerita{max-width:none;background:var(--card);border:1px solid var(--line);border-left:6px solid var(--acc);border-radius:20px;padding:1.3rem 1.6rem 1.1rem;box-shadow:var(--shadow);margin:0 0 .4rem;}
.cerita::before{content:"SEKILAS";display:block;font-size:.7rem;letter-spacing:.16em;font-weight:800;color:var(--acc);margin-bottom:.45rem;}
.cerita p{font-size:1.02rem;line-height:1.75;}
[class*="st-key-hn_box"],[class*="st-key-fl_card"],[class*="st-key-kartu_"]{background:var(--card)!important;border:1px solid var(--line)!important;border-radius:20px!important;padding:1.4rem 1.6rem!important;box-shadow:var(--shadow);gap:.9rem!important;margin:0 0 .5rem!important;}
[class*="st-key-hn_box_filter"],[class*="st-key-fl_card_atur"],[class*="st-key-kartu_pengaturan"]{background:linear-gradient(135deg,#DDF3EE 0%,#F2FAF8 55%,#FFFFFF 100%)!important;border:1.5px solid #9ED6CB!important;border-left:7px solid var(--acc)!important;padding:1.1rem 1.5rem 1.25rem!important;gap:.65rem!important;}
[class*="st-key-hn_box_filter"]::before,[class*="st-key-fl_card_atur"]::before,[class*="st-key-kartu_pengaturan"]::before{content:"FILTER DATA";align-self:flex-start;font-size:.68rem;letter-spacing:.16em;font-weight:800;color:#fff;background:var(--acc);padding:.22rem .7rem;border-radius:999px;}
__FILTER_WIDGET__
[data-testid="stCaptionContainer"]{background:#F2F8F6;border:1px dashed #CFE7E2;border-radius:10px;padding:.5rem .8rem;}
[data-baseweb="tab"][aria-selected="true"]{color:var(--acc)!important;font-weight:700;}
[data-baseweb="tab-highlight"]{background:var(--acc)!important;}
[data-testid="stMetric"]{border:1px solid #CFE7E2;border-left:5px solid var(--acc);background:linear-gradient(135deg,#EAF6F3,#fff)!important;}
.fl-kpi,.kpi{border-top:4px solid var(--acc)!important;box-shadow:var(--shadow);}
.ins-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;margin:.2rem 0;}
.ins{background:linear-gradient(180deg,#F2FAF8 0%,#FFFFFF 100%);border:1px solid var(--line);border-top:5px solid var(--acc);border-radius:16px;padding:1.1rem 1.25rem 1.2rem;transition:transform .2s,box-shadow .2s;}
.ins:hover{transform:translateY(-3px);box-shadow:0 12px 26px rgba(11,79,74,.12);}
.ins:nth-child(2){border-top-color:#E69F00;}.ins:nth-child(3){border-top-color:#0072B2;}.ins:nth-child(4){border-top-color:#CC79A7;}
.ins .n{font-weight:800;font-size:.72rem;letter-spacing:.14em;color:var(--acc);}
.ins:nth-child(2) .n{color:#B87800;}.ins:nth-child(3) .n{color:#0072B2;}.ins:nth-child(4) .n{color:#A04F82;}
.ins h4{font-family:'Outfit',sans-serif;font-weight:700;font-size:1.12rem;color:var(--dk);margin:.3rem 0 .5rem;line-height:1.25;}
.ins p{margin:0;color:#3B5551;line-height:1.65;font-size:.97rem;}
.ins b{color:var(--dk);}
.callout{background:#EAF6F3;border:1px solid #CFE7E2;border-left:5px solid var(--acc);border-radius:14px;padding:.9rem 1.1rem;color:var(--txt);line-height:1.7;font-size:1rem;margin:.3rem 0;}
.callout b{color:var(--dk);}
.callout p{margin:0 0 .5rem;}.callout p:last-child{margin:0;}
.callout .tag{display:block;font-size:.7rem;letter-spacing:.14em;font-weight:800;color:var(--acc);margin-bottom:.2rem;}
.mini-h{font-family:'Outfit',sans-serif;font-weight:700;color:var(--dk);margin:.1rem 0 .4rem;}
.secban{display:flex;flex-direction:column;gap:.15rem;background:linear-gradient(135deg,#0B4F4A,#0F7C73);border-radius:18px;padding:1rem 1.4rem 1.05rem;margin:1.8rem 0 .7rem;box-shadow:var(--shadow);}
.secban .k{font-size:.7rem;letter-spacing:.16em;font-weight:800;color:#8CEBD8;}
.secban .t{font-family:'Outfit',sans-serif;font-weight:800;font-size:1.5rem;color:#fff;line-height:1.2;}
.secban .s{color:rgba(255,255,255,.82);font-size:.92rem;}
.srcbps{text-align:right;font-size:.82rem;font-style:italic;color:var(--mut);margin:1.4rem .3rem -.6rem;}
::-webkit-scrollbar{width:10px;height:10px;}::-webkit-scrollbar-thumb{background:#9ED6CB;border-radius:999px;}::-webkit-scrollbar-track{background:transparent;}
.swipe{display:none;font-size:.82rem;color:var(--mut);margin:0 0 .3rem;}
@media(max-width:1000px){.swipe{display:block;}}
@media(max-width:760px){.sum-grid{grid-template-columns:1fr;}.st-key-banner{padding:1.6rem 1.2rem 1.4rem!important;}.st-key-tema{position:static;margin-bottom:.4rem;}[class*="st-key-hn_box"],[class*="st-key-fl_card"],[class*="st-key-kartu_"]{padding:1rem 1rem!important;}[class*="st-key-hn_box_filter"],[class*="st-key-fl_card_atur"],[class*="st-key-kartu_pengaturan"]{padding:.9rem 1rem 1rem!important;border-left-width:5px!important;}.cerita{padding:1.1rem 1.2rem .9rem;}.secban{padding:.9rem 1.1rem;}.secban .t{font-size:1.25rem;}.ins-grid{grid-template-columns:1fr;}.sum .v{font-size:1.5rem;}}
"""
CSS_EXTRA = CSS_EXTRA.replace("__FILTER_WIDGET__", (
    _kena('[data-baseweb="select"]>div') + "{background:#fff!important;border:1.5px solid #B7DDD6!important;border-radius:12px!important;}"
    + _kena('[data-testid="stWidgetLabel"] p') + "{font-weight:700;font-size:.82rem;color:var(--dk);}"
    + _kena('[data-testid="stBaseButton-segmented_control"]') + "{background:#fff;border:1.5px solid #B7DDD6;border-radius:999px;}"
    + _kena('[data-testid="stBaseButton-segmented_controlActive"]') + "{background:#0F7C73!important;color:#fff!important;border-color:#0F7C73!important;}"
    + _kena('[data-testid="stBaseButton-segmented_controlActive"] p') + "{color:#fff!important;}"
))

CSS_GELAP = """
.stApp{background:linear-gradient(180deg,#06161A 0%,#0A2528 100%)!important;}
:root{--shadow:0 14px 36px rgba(0,0,0,.5);}
.st-key-banner{background:linear-gradient(135deg,#05302D 0%,#0A5750 100%)!important;box-shadow:0 18px 44px rgba(0,0,0,.5);}
.srcbps{color:#9FC4BE;}
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
    semua = CSS + CSS_EXTRA + (CSS_GELAP if st.session_state.get("gelap") else "")
    css = "".join(x.strip() for x in semua.splitlines())
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _ganti_tema():
    st.session_state["gelap"] = not st.session_state.get("gelap", False)


@st.cache_data
def _ringkas_halaman():
    """Satu angka kunci per halaman untuk kotak ringkasan di header."""
    try:
        g = pd.read_csv("data/processed/hierarki_menginap.csv")
        g = g[g["Asal"] == "Gabungan"]
        w = pd.read_csv("data/processed/flow_wisman.csv")
        m = pd.read_csv("data/processed/multivariat_provinsi.csv")
        return {
            "hierarki": (_angka(g["Kamar"].sum()), f"kamar hotel tersebar di {g['Provinsi'].nunique()} provinsi"),
            "flow": (_ringkas(w["Value"].sum()), f"kunjungan wisman lewat {w['Pintu'].nunique()} pintu masuk"),
            "multivariat": (f"{len(m)} provinsi", "dikelompokkan dari 10 indikator akomodasi"),
        }
    except Exception:
        return {h["id"]: ("—", "") for h in HALAMAN}


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
        + (f'Katalog: {x["katalog"]}<br>' if x.get("katalog") else "")
        + f'URL: <a href="{x["url"]}" target="_blank" rel="noopener">{x["url"]}</a><br>'
        f'Tanggal akses: {x["akses"]}</li>' for x in SUMBER_BPS)
    _html('<div class="srcbps">Sumber: BPS</div>')
    with st.container(key="sumber"):
        with st.expander("Lihat data & sumber", expanded=False):
            _html(f'<div class="srcbox"><b>Data &amp; sumber</b><ol>{daftar}</ol></div>')


def _label_sumber():
    """Tulisan 'Sumber: BPS' di pojok kanan bawah kotak visualisasi (dipakai untuk Sankey yang dibungkus di sini)."""
    _html('<div class="vz-src" style="text-align:right;font-size:.8rem;font-style:italic;'
          'color:var(--mut,#4E6B67);margin:-.35rem .1rem 0;">Sumber: BPS</div>')


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
.st-key-hero{position:fixed!important;top:0;left:0;width:100vw;height:100vh;height:100dvh;z-index:1;}
.st-key-hero [data-testid="stElementContainer"]{height:100vh;height:100dvh;width:100%;}
.st-key-navpill_hero{position:fixed!important;bottom:2rem;left:50%;transform:translateX(-50%);width:min(92vw,calc(3*var(--cell) + 1.3rem + 2px));z-index:60;}
.st-key-hero iframe{width:100%!important;height:100vh!important;height:100dvh!important;border:0!important;border-radius:0!important;background:#0B4F4A;}
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
.content{position:relative;height:100%;display:flex;flex-direction:column;padding:0 clamp(1.4rem,6vw,5.5rem) 6.5rem;overflow-y:auto;scrollbar-width:none}.content::-webkit-scrollbar{display:none}
.main{flex:1;display:flex;flex-direction:column;justify-content:center;gap:2.6rem;padding-top:1rem}
h1{font-weight:800;font-size:clamp(2.4rem,6vw,5.2rem);line-height:1.04;max-width:15em;letter-spacing:-.015em;color:#fff;text-shadow:0 0 18px rgba(255,255,255,.35),0 0 42px rgba(140,235,216,.35),0 2px 24px rgba(0,0,0,.35)}
h1 em{font-style:normal;color:#8CEBD8;text-shadow:0 0 16px rgba(140,235,216,.9),0 0 38px rgba(140,235,216,.6),0 0 80px rgba(47,168,154,.55)}
.w{display:inline-block;white-space:nowrap}
.ch{display:inline-block;animation:huruf .55s cubic-bezier(.2,.8,.2,1) both,glow 3.2s ease-in-out 2.2s infinite}
@keyframes huruf{from{opacity:0;transform:translateY(.45em) scale(.85);filter:blur(8px)}to{opacity:1;transform:none;filter:blur(0)}}
@keyframes glow{0%,100%{filter:brightness(1) drop-shadow(0 0 0 rgba(140,235,216,0))}50%{filter:brightness(1.18) drop-shadow(0 0 14px rgba(140,235,216,.75))}}
.sub-fade{opacity:0;animation:up .9s cubic-bezier(.2,.7,.2,1) 1.9s both}
.hl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1.2rem;max-width:960px}
.sub{margin-top:1rem;max-width:34em;font-size:clamp(.9rem,1.3vw,1.1rem);line-height:1.5;color:#D8F3EE;font-weight:400;letter-spacing:.01em}
.card{background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.22);border-left:4px solid #8CEBD8;border-radius:18px;padding:1.2rem 1.4rem;backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);box-shadow:0 10px 30px rgba(0,0,0,.22);transition:transform .25s,background .25s}
.card:hover{transform:translateY(-4px);background:rgba(255,255,255,.14)}
.card b{display:block;font-weight:800;font-size:clamp(1.6rem,2.8vw,2.4rem);line-height:1.1;color:#fff}
.card span{display:block;margin-top:.3rem;font-size:.95rem;line-height:1.4;color:#D8F3EE}
.credit{position:absolute;right:1.2rem;bottom:.8rem;z-index:5;max-width:calc(100% - 2.4rem);font-size:.72rem;line-height:1.35;color:rgba(255,255,255,.7);text-align:right;text-shadow:0 1px 6px rgba(0,0,0,.6)}
.credit a{color:rgba(255,255,255,.9);text-decoration:underline;text-underline-offset:2px}.credit a:hover{color:#8CEBD8}
@media(max-width:760px){.credit{right:0;left:0;bottom:.5rem;text-align:center;font-size:.66rem;padding:0 1rem}}
@keyframes up{from{opacity:0;transform:translateY(26px)}to{opacity:1;transform:none}}
.up{animation:up .9s cubic-bezier(.2,.7,.2,1) both}
@media(max-width:760px){.hl{grid-template-columns:1fr;gap:.7rem}.card{padding:.8rem 1rem}.card b{display:inline;font-size:1.4rem}.card span{display:inline;margin-left:.5rem;font-size:.85rem}.main{gap:1.2rem;justify-content:flex-start;padding-top:9vh}h1{font-size:clamp(2rem,9.5vw,2.7rem)}.content{padding-bottom:7.5rem}}
@media(max-height:560px){.main{justify-content:flex-start;padding-top:1.4rem}}
@media(prefers-reduced-motion:reduce){.ch,.sub-fade{animation:none!important;opacity:1!important}}
</style></head><body>
<div class="stage">
  __LATAR__
  <div class="shade"></div>
  <div class="content">
    <div class="main">
      <div><h1>__HOOK__</h1><p class="sub sub-fade">__SUB__</p></div>
      <div class="hl">__KARTU__</div>
    </div>
  </div>
  <div class="credit">Video latar: <a href="https://www.youtube.com/watch?v=ojQbArbuN4E" target="_blank" rel="noopener noreferrer">Wonderful Indonesia : A Visual Journey</a> · Pesona Indonesia, Kemenparekraf</div>
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
        ukuran = Path(VIDEO_FILE).stat().st_size
        if ukuran <= 12 * 1024 * 1024:  # <= 12 MB: sematkan langsung, tidak butuh static serving
            src = "data:video/mp4;base64," + base64.b64encode(Path(VIDEO_FILE).read_bytes()).decode()
        else:
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


def _judul_animasi(teks):
    """Pecah judul jadi huruf-huruf yang muncul satu per satu (<em> dipertahankan)."""
    n = [0]

    def huruf(s):
        out = []
        for kata in s.split(" "):
            if not kata:
                continue
            spans = ""
            for c in kata:
                spans += f'<span class="ch" style="animation-delay:{0.25 + n[0] * 0.07:.2f}s,{2.2 + n[0] * 0.08:.2f}s">{c}</span>'
                n[0] += 1
            out.append(f'<span class="w">{spans}</span>')
            n[0] += 1  # jeda kecil antar kata
        return " ".join(out)

    hasil = ""
    for bagian in re.split(r"(<em>.*?</em>)", teks):
        if bagian.startswith("<em>"):
            hasil += " <em>" + huruf(bagian[4:-5]) + "</em> "
        elif bagian.strip():
            hasil += huruf(bagian)
    return hasil


def _hero_html():
    latar, js = _latar_video()
    kartu = "".join(
        f'<div class="card up" style="animation-delay:{2.3 + i * 0.15:.2f}s"><b>{n}</b><span>{k}</span></div>'
        for i, (n, k) in enumerate(_highlight())
    )
    return (HERO_TPL.replace("__LATAR__", latar)
            .replace("__HOOK__", _judul_animasi(HOOK)).replace("__SUB__", SUBJUDUL).replace("__KARTU__", kartu)
            .replace("__JS__", js))


def _beranda():
    css = "".join(x.strip() for x in CSS_BERANDA.splitlines())
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    with st.container(key="hero"):
        components.html(_hero_html(), height=720, scrolling=False)
    _pil_halaman("navpill_hero", aktif="beranda", beranda=False)


# ---------------- halaman: BAB (Hierarki / Flow / Multivariat) ----------------
def _banner(h):
    ring = _ringkas_halaman()
    kartu = "".join(
        f'<div class="sum{" on" if x["id"] == h["id"] else ""}"><div class="k">{x["nama"].upper()}</div>'
        f'<div class="v">{ring[x["id"]][0]}</div><div class="d">{ring[x["id"]][1]}</div></div>'
        for x in HALAMAN)
    gelap = st.session_state.get("gelap", False)
    with st.container(key="banner"):
        with st.container(key="tema"):
            st.button("Mode terang" if gelap else "Mode gelap", key="btn_tema", on_click=_ganti_tema,
                      icon=":material/light_mode:" if gelap else ":material/dark_mode:")
        _html(f'<div class="banner-in"><div class="t">{h["judul"]}</div><div class="s">{h["sub"]}</div></div>')
        _pil_halaman("navpill_bab", aktif=h["id"])
        _html(f'<div class="sum-grid">{kartu}</div>')


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
                    _label_sumber()
                _narasi(h)
            return hasil
        return asli(fig, *a, **k)

    def pembungkus_html(*a, **k):  
        return asli_html(*a, **k)

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