"""
Genererer side-om-side Google Maps satellittplan (z=20 + Kartverket/Geonorge grenser)
som viser hvordan den låste 750 m² tomten fra #110 (Variant 1C) passer direkte inn i
mulighetsstudien #111 (Myrteveien 6 [140/371] + Onkels tomt [140/1247] = ca. 4 839 m²).

Panel A (Venstre): 2x3 = 6 store tomter (~710–760 m²) for 2-mannsboliger ved 25 % BYA
                   — #110 (750 m²) er Tomt 1 av 6! Sør-tun fra Trollheggveien lar Ny garasje på M6 stå urørt.
Panel B (Høyre):   7 tomter (#110 750 m² + 6 tomter à ~575–615 m²) + 200 m² nærlekeplass
                   — 100 % fra Myrteveien! Sentral stikkvei følger vestgrensen til #110 rett forbi huset
                     (viser samtidig at kun Ny garasje på M6 krysser denne veikorridoen).
"""

import json
import math
import os
import subprocess
import urllib.request
import numpy as np
from PIL import Image

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
assets_dir = os.path.join(repo_root, "assets", "images")

cache_json = "/tmp/m6_parcels_wgs84.json"
if not os.path.exists(cache_json):
    parcels = {}
    for gnr, bnr in [(140, 371), (140, 1247), (140, 1008), (140, 995), (140, 1014), (141, 94)]:
        u = f"https://ws.geonorge.no/eiendom/v1/geokoding?kommunenummer=3905&gardsnummer={gnr}&bruksnummer={bnr}&omrade=true"
        with urllib.request.urlopen(u, timeout=15) as r:
            d = json.loads(r.read().decode())
        parcels[f"{gnr}/{bnr}"] = d["features"][0]["geometry"]["coordinates"][0]
    with open(cache_json, "w") as f:
        json.dump(parcels, f)
else:
    with open(cache_json) as f:
        parcels = json.load(f)

ZOOM = 20
TILE_SIZE = 256


def latlon_to_world_px(lat, lon, z=ZOOM):
    n = 2.0 ** z
    x = (lon + 180.0) / 360.0 * n * TILE_SIZE
    lat_rad = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n * TILE_SIZE
    return np.array([x, y])


all_pts = parcels["140/371"] + parcels["140/1247"]
w_pts = np.array([latlon_to_world_px(lat, lon) for lon, lat in all_pts])
pad_x_l, pad_x_r = 210, 210
pad_y_t, pad_y_b = 200, 140
wx0 = int(math.floor(w_pts[:, 0].min() - pad_x_l))
wx1 = int(math.ceil(w_pts[:, 0].max() + pad_x_r))
wy0 = int(math.floor(w_pts[:, 1].min() - pad_y_t))
wy1 = int(math.ceil(w_pts[:, 1].max() + pad_y_b))

tx0, tx1 = wx0 // TILE_SIZE, wx1 // TILE_SIZE
ty0, ty1 = wy0 // TILE_SIZE, wy1 // TILE_SIZE

tile_dir = "/tmp/gm_tiles"
os.makedirs(tile_dir, exist_ok=True)
stitched = Image.new("RGBA", ((tx1 - tx0 + 1) * TILE_SIZE, (ty1 - ty0 + 1) * TILE_SIZE))
for tx in range(tx0, tx1 + 1):
    for ty in range(ty0, ty1 + 1):
        tpath = os.path.join(tile_dir, f"s_{ZOOM}_{tx}_{ty}.jpg")
        if not os.path.exists(tpath):
            url = f"https://mt1.google.com/vt/lyrs=s&x={tx}&y={ty}&z={ZOOM}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = r.read()
            with open(tpath, "wb") as f:
                f.write(data)
        tim = Image.open(tpath).convert("RGBA")
        stitched.paste(tim, ((tx - tx0) * TILE_SIZE, (ty - ty0) * TILE_SIZE))

cx0 = wx0 - tx0 * TILE_SIZE
cy0 = wy0 - ty0 * TILE_SIZE
PW = wx1 - wx0
PH = wy1 - wy0
sat_panel = stitched.crop((cx0, cy0, cx0 + PW, cy0 + PH))

lat0, lon0 = 59.2666356, 10.4757783
lon_s = 111320.0 * math.cos(math.radians(lat0))
lat_s = 111320.0


def lonlat_to_m(lon, lat):
    return np.array([(lon - lon0) * lon_s, (lat - lat0) * lat_s])


def m_to_lonlat(v):
    return (lon0 + v[0] / lon_s, lat0 + v[1] / lat_s)


m371 = [lonlat_to_m(lon, lat) for lon, lat in parcels["140/371"][:-1]]
NW_M = min(m371, key=lambda v: v[0] - v[1])
NE_M = max(m371, key=lambda v: v[0] + v[1])
u_e = (NE_M - NW_M) / np.linalg.norm(NE_M - NW_M)
u_s = np.array([u_e[1], -u_e[0]])
if u_s[1] > 0:
    u_s = -u_s


def local_to_lonlat(xy):
    v = NW_M + xy[0] * u_e + xy[1] * u_s
    return m_to_lonlat(v)


def xw(y):
    if y <= 80.82:
        return 0.0 + (y / 80.82) * 5.06
    return 5.06 + ((y - 80.82) / (105.82 - 80.82)) * (6.62 - 5.06)


def xe(y):
    if y <= 70.59:
        return 51.89 + (y / 70.59) * (51.66 - 51.89)
    if y <= 81.58:
        return 51.66 + ((y - 70.59) / (81.58 - 70.59)) * (51.62 - 51.66)
    return 51.62 + ((y - 81.58) / (90.23 - 81.58)) * (56.19 - 51.62)


def ys(x):
    return 105.82 + ((x - 6.62) / (56.19 - 6.62)) * (90.23 - 105.82)


def area_m2(pts):
    return 0.5 * abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))))


def centroid_local(pts):
    cx = cy = a2 = 0.0
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        cr = x0 * y1 - x1 * y0
        a2 += cr
        cx += (x0 + x1) * cr
        cy += (y0 + y1) * cr
    return np.array([cx / (3.0 * a2), cy / (3.0 * a2)])


GAP = 32
MARGIN_X = 24
HEADER_H = 114
FOOTER_H = 170
W = MARGIN_X * 2 + PW * 2 + GAP
H = HEADER_H + PH + FOOTER_H


def lonlat_to_canvas(lon, lat, panel_idx):
    wp = latlon_to_world_px(lat, lon)
    ox = MARGIN_X + panel_idx * (PW + GAP)
    return np.array([wp[0] - wx0 + ox, wp[1] - wy0 + HEADER_H])


def local_to_canvas(xy, panel_idx):
    lon, lat = local_to_lonlat(xy)
    return lonlat_to_canvas(lon, lat, panel_idx)


def poly_local_str(pts, panel_idx):
    return " ".join(f"{local_to_canvas(p, panel_idx)[0]:.1f},{local_to_canvas(p, panel_idx)[1]:.1f}" for p in pts)


def poly_wgs_str(ring, panel_idx):
    return " ".join(f"{lonlat_to_canvas(lon, lat, panel_idx)[0]:.1f},{lonlat_to_canvas(lon, lat, panel_idx)[1]:.1f}" for lon, lat in ring)


# === EKSAKT VARIANT 1C (#110, ca. 750 m²) i #111-koordinater ===
# Vestgrense: (32.00, 0) -> (34.15, 37.43); Østgrense: (51.89, 0) -> (xe(42.91), 42.91) -> eksakt ~750 m²!
def x_var1c(y):
    """x-koordinat langs Variant 1C sin parallelle vestgrense ved dybde y."""
    return 32.00 + (y / 37.43) * (34.15 - 32.00)


VAR1C_POLY = [[32.00, 0.0], [51.89, 0.0], [xe(42.91), 42.91], [34.15, 37.43]]
# Ny garasje på M6 (<=50 m², 8,4 x 5,9 m i portrommet — krysser kun 100 % Myrteveien stikkvei!)
NY_GAR_POLY = [[25.37, 10.69], [31.26, 10.34], [31.76, 18.73], [25.87, 19.08]]


# ==============================================================================
# PANEL A: 7 BALANSERTE TOMTER (#110 750 m² + 6 TOMTER) M/SØR-TUN FRA TROLLHEGGVEIEN
# Portrom & Ny garasje på M6 bevares 100 % urørt!
# ==============================================================================
P1_tun_s = [[xw(65.5), 65.5], [24.0, 65.5], [24.0, 63.5], [33.0, 63.5], [33.0, 71.5], [24.0, 71.5], [24.0, 69.5], [xw(69.5), 69.5]]
P1_lek = [[24.0, 71.5], [31.5, 71.5], [31.5, 84.0], [24.0, 84.0]]  # ~94 m² felles lek rett ved tunet

P1_plots = [
    ("T1",   "Nord-Vest",    "Myrteveien",   "#10b981", "#34d399", [[0.0, 0.0], [24.5, 0.0], [24.5, 23.0], [xw(23.0), 23.0]], (-1.0, -2.0)),
    ("#110", "Var. 1C (NØ)", "Myrteveien",   "#f97316", "#fb923c", VAR1C_POLY, (0.0, -2.0)),
    ("T3",   "Eksist. hus",  "M6 (bevart)",  "#f59e0b", "#fbbf24", [[24.5, 0.0], [32.00, 0.0], [34.15, 37.43], [33.0, 45.0], [xw(45.0), 45.0], [xw(23.0), 23.0], [24.5, 23.0]], (-8.5, 8.0)),
    ("T4",   "Midt-SV",      "Tun Sør",      "#8b5cf6", "#a78bfa", [[xw(45.0), 45.0], [33.0, 45.0], [33.0, 63.5], [24.0, 63.5], [24.0, 65.5], [xw(65.5), 65.5]], (-2.0, -1.0)),
    ("T5",   "Sør-Øst",      "Tun Sør",      "#0ea5e9", "#38bdf8", [[34.15, 37.43], [xe(42.91), 42.91], [xe(68.5), 68.5], [33.0, 68.5], [33.0, 45.0]], (1.0, 1.0)),
    ("T6",   "Onkel (SV)",   "Tun Sør",      "#ec4899", "#f472b6", [[xw(69.5), 69.5], [24.0, 69.5], [24.0, ys(24.0)], [6.62, 105.82], [5.06, 80.82]], (-1.0, 4.5)),
    ("T7",   "Onkel (SØ)",   "Tun Sør",      "#f43f5e", "#fb7185", [[24.0, 84.0], [31.5, 84.0], [31.5, 71.5], [33.0, 71.5], [33.0, 68.5], [xe(68.5), 68.5], [51.66, 70.59], [51.62, 81.58], [56.19, 90.23], [24.0, ys(24.0)]], (4.5, 4.0)),
]


# ==============================================================================
# PANEL B: 7 BALANSERTE TOMTER (#110 750 m² + 6 TOMTER à ~560–640 m²) + LEKEPLASS
# 100 % FRA MYRTEVEIEN! Sentral 4 m stikkvei følger #110s vestgrense rett forbi huset!
# ==============================================================================
P2_road = [
    [28.00, 0.0], [32.00, 0.0],
    [34.15, 37.43], [32.00, 45.5], [32.00, 70.0],
    [33.5, 70.0], [33.5, 76.5],
    [23.5, 76.5], [23.5, 70.0],
    [28.00, 70.0], [28.00, 45.5], [30.15, 37.43],
]
P2_lek = [[23.5, 76.5], [31.5, 76.5], [31.5, ys(31.5)], [23.5, ys(23.5)]]

P2_plots = [
    ("T1",   "Nord-Vest",    "Myrteveien",   "#10b981", "#34d399", [[0.0, 0.0], [28.00, 0.0], [x_var1c(21.5) - 4.0, 21.5], [xw(21.5), 21.5]], (-1.5, -1.5)),
    ("#110", "Var. 1C (NØ)", "Myrteveien",   "#f97316", "#fb923c", VAR1C_POLY, (0.0, -2.0)),
    ("T3",   "Eksist. hus",  "Stikkvei",     "#f59e0b", "#fbbf24", [[xw(21.5), 21.5], [x_var1c(21.5) - 4.0, 21.5], [30.15, 37.43], [28.00, 45.5], [xw(45.5), 45.5]], (-6.5, 2.0)),
    ("T4",   "Midt-SV",      "Stikkvei/tun", "#8b5cf6", "#a78bfa", [[xw(45.5), 45.5], [28.00, 45.5], [28.00, 70.0], [xw(70.0), 70.0]], (-1.0, 0.0)),
    ("T5",   "Midt-SØ",      "Stikkvei",     "#0ea5e9", "#38bdf8", [[34.15, 37.43], [xe(42.91), 42.91], [xe(66.0), 66.0], [32.00, 66.0], [32.00, 45.5]], (0.5, 0.0)),
    ("T6",   "Onkel (SV)",   "Snutun",       "#ec4899", "#f472b6", [[xw(70.0), 70.0], [23.5, 70.0], [23.5, ys(23.5)], [6.62, 105.82], [5.06, 80.82]], (-1.0, 3.5)),
    ("T7",   "Onkel (SØ)",   "Snutun",       "#f43f5e", "#fb7185", [[32.00, 66.0], [xe(66.0), 66.0], [51.66, 70.59], [51.62, 81.58], [56.19, 90.23], [31.5, ys(31.5)], [31.5, 76.5], [33.5, 76.5], [33.5, 70.0], [32.00, 70.0]], (2.0, 3.5)),
]

orig_split_p1 = [5.06, 80.82]
orig_split_p2 = [51.66, 70.59]

print("=== PANEL A (7 tomter m/Sør-tun fra Trollheggveien — Ny garasje urørt!) ===")
tot_a = 0
for c, n, _, _, _, pts, _ in P1_plots:
    ar = area_m2(pts); tot_a += ar
    print(f"  {c:4s} {n:14s}: {ar:6.1f} m2")
print(f"  Tun Sør: {area_m2(P1_tun_s):.1f} m2 | Lek: {area_m2(P1_lek):.1f} m2 | Sum: {tot_a + area_m2(P1_tun_s) + area_m2(P1_lek):.1f} m2")

print("\n=== PANEL B (7 tomter 100 % fra Myrteveien — Stikkvei følger #110s vestgrense!) ===")
tot_b = 0
for c, n, _, _, _, pts, _ in P2_plots:
    ar = area_m2(pts); tot_b += ar
    print(f"  {c:4s} {n:14s}: {ar:6.1f} m2")
print(f"  Vei+tun: {area_m2(P2_road):.1f} m2 | Lek: {area_m2(P2_lek):.1f} m2 | Sum: {tot_b + area_m2(P2_road) + area_m2(P2_lek):.1f} m2")


def render_panel(plots, road, lek, panel_idx, show_gar_warn=False):
    els = []
    # Nabotomter
    for key in ["140/1008", "140/995", "140/1014", "141/94"]:
        if key in parcels:
            els.append(f'<polygon points="{poly_wgs_str(parcels[key], panel_idx)}" fill="none" stroke="#ffffff" stroke-opacity="0.38" stroke-width="1.3" stroke-dasharray="4,4"/>')

    # 1. Tomter
    for code, name, acc, fill, stroke, pts, nudge in plots:
        is_110 = (code == "#110")
        op = "0.38" if is_110 else "0.24"
        sw = "4.2" if is_110 else "2.4"
        els.append(f'<polygon points="{poly_local_str(pts, panel_idx)}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"/>')

    # 2. Vei / gatetun
    els.append(f'<polygon points="{poly_local_str(road, panel_idx)}" fill="#e2e8f0" fill-opacity="0.62" stroke="#f8fafc" stroke-width="2.4"/>')
    # 3. Nærlekeplass
    els.append(f'<polygon points="{poly_local_str(lek, panel_idx)}" fill="#84cc16" fill-opacity="0.36" stroke="#bef264" stroke-width="2.2" stroke-dasharray="6,3"/>')

    # 4. Planlagt Ny garasje på M6 (viser tydelig relasjonen til stikkvei!)
    g_col = "#ef4444" if show_gar_warn else "#fde047"
    g_fill = "#ef4444" if show_gar_warn else "#facc15"
    els.append(f'<polygon points="{poly_local_str(NY_GAR_POLY, panel_idx)}" fill="{g_fill}" fill-opacity="0.38" stroke="{g_col}" stroke-width="2.4" stroke-dasharray="5,3"/>')

    # 5. Opprinnelig grense 140/371 vs 140/1247 + ytre 140/371
    s1 = local_to_canvas(orig_split_p1, panel_idx)
    s2 = local_to_canvas(orig_split_p2, panel_idx)
    els.append(f'<line x1="{s1[0]:.1f}" y1="{s1[1]:.1f}" x2="{s2[0]:.1f}" y2="{s2[1]:.1f}" stroke="#fde047" stroke-width="2.2" stroke-dasharray="7,4"/>')
    ox = MARGIN_X + panel_idx * (PW + GAP)
    els.append(f'''
    <line x1="{s2[0] + 6:.1f}" y1="{s2[1]:.1f}" x2="{ox + PW - 180:.1f}" y2="{s2[1]:.1f}" stroke="#fde047" stroke-width="1.6" stroke-dasharray="4,3"/>
    <g transform="translate({ox + PW - 180:.1f}, {s2[1] - 16:.1f})">
      <rect width="168" height="32" rx="5" fill="#0f172a" fill-opacity="0.90" stroke="#fde047" stroke-width="1.4"/>
      <text x="84" y="13" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="8.6" fill="#fef08a">OPPR. GRENSE</text>
      <text x="84" y="25" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="8.0" fill="#fde047">140/371 vs. 140/1247</text>
    </g>''')

    # 6. Callout i vestmargen for Ny garasje på M6
    gc = local_to_canvas([25.4, 15.0], panel_idx)
    gar_lbl = ("NY GARASJE M6", "Stenger 100 % Myrtevn.-vei!", "#fef2f2", "#ef4444", "#fca5a5") if show_gar_warn else ("NY GARASJE M6", "Står helt urørt i portrom!", "#fefce8", "#eab308", "#fde047")
    els.append(f'''
    <line x1="{ox + 178:.1f}" y1="{gc[1]:.1f}" x2="{gc[0] - 4:.1f}" y2="{gc[1]:.1f}" stroke="{gar_lbl[3]}" stroke-width="2.0" stroke-dasharray="4,3"/>
    <g transform="translate({ox + 12:.1f}, {gc[1] - 20:.1f})">
      <rect width="166" height="40" rx="5" fill="#0f172a" fill-opacity="0.92" stroke="{gar_lbl[3]}" stroke-width="1.6"/>
      <text x="83" y="16" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="9.0" fill="{gar_lbl[4]}">{gar_lbl[0]}</text>
      <text x="83" y="31" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="8.4" fill="#e2e8f0">{gar_lbl[1]}</text>
    </g>''')

    # 7. Rene tomtekort
    for code, name, acc, fill, stroke, pts, nudge in plots:
        ar = area_m2(pts)
        is_110 = (code == "#110")
        cp = local_to_canvas(centroid_local(pts) + np.array(nudge), panel_idx)
        w_box = 148 if is_110 else 132
        h_box = 60 if is_110 else 52
        sub = "2-mannsbolig (låst)" if is_110 else f"BYA {ar*0.25:.0f} m² • {acc}"
        els.append(f'''
        <g transform="translate({cp[0] - w_box/2:.1f}, {cp[1] - h_box/2:.1f})">
          <rect width="{w_box}" height="{h_box}" rx="6" fill="{"#431407" if is_110 else "#0f172a"}" fill-opacity="0.92" stroke="{stroke}" stroke-width="{"2.6" if is_110 else "1.8"}"/>
          <text x="{w_box/2:.1f}" y="16" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="{"11.2" if is_110 else "10.0"}" fill="{stroke}">{code} • {name}</text>
          <text x="{w_box/2:.1f}" y="33" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="{"12.8" if is_110 else "11.5"}" fill="#ffffff">ca. {ar:.0f} m²</text>
          <text x="{w_box/2:.1f}" y="47" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="8.4" fill="{"#fed7aa" if is_110 else "#cbd5e1"}">{sub}</text>
        </g>''')

    # Lekeplass-badge
    lc = local_to_canvas(centroid_local(lek), panel_idx)
    els.append(f'''
    <g transform="translate({lc[0] - 48:.1f}, {lc[1] - 14:.1f})">
      <rect width="96" height="28" rx="5" fill="#1a2e05" fill-opacity="0.90" stroke="#a3e635" stroke-width="1.5"/>
      <text x="48" y="12" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="8.5" fill="#bef264">LEKEPLASS</text>
      <text x="48" y="23" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="8.5" fill="#ffffff">~{area_m2(lek):.0f} m²</text>
    </g>''')

    # Veietiketter
    m_lbl = local_to_canvas([25.0, -7.5], panel_idx)
    t_lbl = local_to_canvas([-8.0, 48.0], panel_idx)
    els.append(f'''
    <g transform="translate({m_lbl[0] - 105:.1f}, {m_lbl[1] - 13:.1f})">
      <rect width="210" height="24" rx="4" fill="#0f172a" fill-opacity="0.88" stroke="#38bdf8" stroke-width="1.2"/>
      <text x="105" y="16" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.2" fill="#e0f2fe">MYRTEVEIEN (kommunal vei)</text>
    </g>
    <g transform="translate({t_lbl[0]:.1f}, {t_lbl[1]:.1f}) rotate(-78)">
      <rect x="-86" y="-11" width="172" height="22" rx="4" fill="#0f172a" fill-opacity="0.85" stroke="#fbbf24" stroke-width="1.1"/>
      <text x="0" y="4" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.2" fill="#fef08a">TROLLHEGGVEIEN (privat 141/1)</text>
    </g>''')

    return "\n".join(els)


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <rect x="0" y="0" width="{W}" height="{HEADER_H}" fill="#0f172a"/>
  <rect x="0" y="{HEADER_H + PH}" width="{W}" height="{FOOTER_H}" fill="#0f172a"/>
  <rect x="0" y="{HEADER_H}" width="{MARGIN_X}" height="{PH}" fill="#0f172a"/>
  <rect x="{MARGIN_X + PW}" y="{HEADER_H}" width="{GAP}" height="{PH}" fill="#0f172a"/>
  <rect x="{MARGIN_X + PW * 2 + GAP}" y="{HEADER_H}" width="{MARGIN_X}" height="{PH}" fill="#0f172a"/>

  <!-- Toppbanner -->
  <text x="{W/2:.1f}" y="38" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="22" fill="#ffffff">SAMMENHENG #110 + #111 — 750 m² TOMT (VAR. 1C) INTEGRERT I UTPARSELLERINGEN</text>
  <text x="{W/2:.1f}" y="66" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="14.2" fill="#fb923c">Myrteveien 6 (3 752 m²) + Onkels tomt 140/1247 (1 087 m²) = 4 839 m² • #110 (750 m²) passer sømløst inn uten å låse #111!</text>
  <text x="{W/2:.1f}" y="92" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="12.2" fill="#cbd5e1">Oransje = Låst #110 (Variant 1C, 750 m² tomannsbolig) • Gul/rød stiplet = Ny garasje M6 (≤ 50 m²) • Kartgrunnlag: Google Maps z=20 + Geonorge</text>

  <!-- Panel A og B -->
  {render_panel(P1_plots, P1_tun_s, P1_lek, 0, show_gar_warn=False)}
  {render_panel(P2_plots, P2_road, P2_lek, 1, show_gar_warn=True)}

  <!-- Paneltitler i topp av hvert kart -->
  <g transform="translate({MARGIN_X + 12}, {HEADER_H + 12})">
    <rect width="{PW - 24}" height="68" rx="7" fill="#0f172a" fill-opacity="0.91" stroke="#fb923c" stroke-width="2.0"/>
    <text x="14" y="23" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="13.5" fill="#fb923c">SPOR 1: #110 (750 m²) + 6 TOMTER M/SØR-TUN FRA TROLLHEGGVEIEN (NY GARASJE URØRT!)</text>
    <text x="14" y="42" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.0" fill="#ffffff">Totalt 7 balanserte tomter (#110 750 m² + 6 tomter på ~545–870 m²) • Portrom &amp; Ny garasje på M6 bevares 100 %</text>
    <text x="14" y="59" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.2" fill="#fde68a">Forutsetning: Utvidet veirett i privat vei Trollheggveien (141/1) for Sør-tunet + detaljregulering</text>
  </g>

  <g transform="translate({MARGIN_X + PW + GAP + 12}, {HEADER_H + 12})">
    <rect width="{PW - 24}" height="68" rx="7" fill="#0f172a" fill-opacity="0.91" stroke="#34d399" stroke-width="2.0"/>
    <text x="14" y="23" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="13.5" fill="#34d399">SPOR 2: #110 (750 m²) + 6 TOMTER — 100 % FRA MYRTEVEIEN (0 % AVHENGIG AV TROLLHEGGVN.!)</text>
    <text x="14" y="42" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.0" fill="#ffffff">Sentral 4 m stikkvei følger vestgrensen av #110 rett gjennom 6,9 m-åpningen forbi huset (+ ~170 m² lekeplass)</text>
    <text x="14" y="59" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.2" fill="#fca5a5">Viktig funn: #110 blokkerer IKKE veien — men Ny garasje på M6 står midt i veikorridoen (må utsettes/flyttes i Spor 2)</text>
  </g>

  <!-- Rammer rundt paneler -->
  <rect x="{MARGIN_X}" y="{HEADER_H}" width="{PW}" height="{PH}" fill="none" stroke="#334155" stroke-width="2.0"/>
  <rect x="{MARGIN_X + PW + GAP}" y="{HEADER_H}" width="{PW}" height="{PH}" fill="none" stroke="#334155" stroke-width="2.0"/>

  <!-- Bunnfelt med oppsummering -->
  <g transform="translate({MARGIN_X}, {HEADER_H + PH + 14})">
    <rect width="{W - 2*MARGIN_X}" height="{FOOTER_H - 26}" rx="8" fill="#1e293b" stroke="#475569" stroke-width="1.6"/>
    <text x="20" y="26" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="13.5" fill="#ffffff">HOVEDKONKLUSJON — HVORDAN #110 (750 m²) OG #111 SPILLER SAMMEN</text>
    <text x="20" y="49" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.6" fill="#fed7aa">1. Trygt å kjøre #110 nå: Å fradele Variant 1C (750 m² tomannsboligtomt) nå ødelegger IKKE fremtidig utparsellering — du beholder 7 tomter totalt (M6 + onkel) eller 5 på M6 alene!</text>
    <text x="20" y="70" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.6" fill="#a7f3d0">2. Veikorridoren fra Myrteveien forblir åpen: Vestgrensen på #110 (x=31,7 m) + 6,9 m klaring til huset gir eksakt plass til 4 m stikkvei sørover i Spor 2 (0 % avhengig av Trollheggveien).</text>
    <text x="20" y="91" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.6" fill="#fca5a5">3. Eneste reelle veivalg for M6 er timing på Ny garasje: Bygges Ny garasje i portrommet nå, må fremtidig Sør-utvikling gå fra Trollheggveien (Spor 1) — eller garasjen må flyttes ved utbygging.</text>
    <text x="20" y="112" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.6" fill="#e2e8f0">4. Kun 2x4 (8 tomter) mister 1 tomt: Dybden på #110 (37,5–42,9 m) slår sammen T2 og halve T4 (8 → 7 tomter), men til gjengjeld får du ut en fullverdig 750 m² 2-mannsboligtomt allerede i steg 1.</text>
    <text x="20" y="132" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.0" fill="#94a3b8">Kartgrunnlag: Google Maps Satellite (z=20) &amp; Kartverket / Geonorge Matrikkel API (Tønsberg kommune 3905). Foreløpig strategisk mulighetsskisse.</text>
  </g>
</svg>
'''

svg_path = os.path.join(assets_dir, "utparsellering_110_i_111_satellitt.svg")
overlay_png = "/tmp/110_i_111_overlay.png"
png_path = os.path.join(assets_dir, "utparsellering_110_i_111_satellitt.png")

with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg)

res = subprocess.run(
    ["inkscape", svg_path, "-o", overlay_png, "--export-area-page", f"--export-width={W}"],
    capture_output=True, text=True
)
if res.returncode != 0:
    raise RuntimeError(f"Inkscape failed: {res.stderr}")

canvas = Image.new("RGBA", (W, H), (15, 23, 42, 255))
canvas.paste(sat_panel, (MARGIN_X, HEADER_H))
canvas.paste(sat_panel, (MARGIN_X + PW + GAP, HEADER_H))

ov = Image.open(overlay_png).convert("RGBA")
if ov.size != canvas.size:
    ov = ov.resize(canvas.size, Image.Resampling.LANCZOS)
composed = Image.alpha_composite(canvas, ov).convert("RGB")
composed.save(png_path, format="PNG", optimize=True)
os.remove(overlay_png)
print(f"Saved: {png_path} ({composed.size[0]}x{composed.size[1]})")
