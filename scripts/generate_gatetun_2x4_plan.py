"""
Genererer satellitt-oversiktsplan (Google Maps z=20 + Kartverket/Geonorge grenser)
for 2x4-tomters klyngekonsept med TO GATETUN (der 4 og 4 tomter møtes) på samlet
areal for Myrteveien 6 (140/371) + Onkels tomt i sydenden (140/1247) = ca. 4 839 m².

Viser også illustrative fotavtrykk for kompakte 2-mannsboliger (~112 m² ved regulert
30 % BYA) for å teste byggbarhet, solgang, parkering og avstander direkte på flyfoto.

Panel A (Venstre): Alt. C1 — 2x4 Gatetun (Nord-tun fra Myrteveien + Sør-tun fra Trollheggveien)
Panel B (Høyre):   Alt. C2 — 2x4 Gatetun koblet 100 % fra Myrteveien (0 % avhengig av Trollheggveien)
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
FOOTER_H = 166
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


def rect_local(cx, cy, w, h):
    return [[cx - w / 2, cy - h / 2], [cx + w / 2, cy - h / 2], [cx + w / 2, cy + h / 2], [cx - w / 2, cy + h / 2]]


# ---------------- ALT C1: 2x4 GATETUN (Nord-tun fra Myrteveien + Sør-tun fra Trollheggveien) ----------------
ex0, ex1 = 24.0, 28.0
nx0, nx1, ny0, ny1 = 23.0, 33.0, 17.0, 24.5
C1_tun_n = [[ex0, 0], [ex1, 0], [ex1, ny0], [nx1, ny0], [nx1, ny1], [nx0, ny1], [nx0, ny0], [ex0, ny0]]
C1_tun_s = [[xw(69.5), 69.5], [24.5, 69.5], [24.5, 67.5], [33.5, 67.5], [33.5, 75.5], [24.5, 75.5], [24.5, 73.5], [xw(73.5), 73.5]]

C1_plots = [
    ("T1", "Nord-Vest",   "Tun Nord", "#10b981", "#34d399", [[0, 0], [ex0, 0], [ex0, ny0], [nx0, ny0], [nx0, 23.2], [xw(23.2), 23.2]], (0, -3.5)),
    ("T2", "Nord-Øst",    "Tun Nord", "#06b6d4", "#22d3ee", [[ex1, 0], [51.89, 0], [xe(24.2), 24.2], [nx1, 24.2], [nx1, ny0], [ex1, ny0]], (0, -3.5)),
    ("T3", "Eksist. hus", "Tun Nord", "#f59e0b", "#fbbf24", [[xw(23.2), 23.2], [nx0, 23.2], [nx0, ny1], [30.7, ny1], [30.7, 44.2], [xw(44.2), 44.2]], (-6.2, 0.5)),
    ("T4", "Midt-NØ",     "Tun Nord", "#3b82f6", "#60a5fa", [[30.7, ny1], [nx1, ny1], [nx1, 24.2], [xe(24.2), 24.2], [xe(50.2), 50.2], [30.7, 50.2]], (0.5, -5.0)),
    ("T5", "Midt-SV",     "Tun Sør",  "#8b5cf6", "#a78bfa", [[xw(44.2), 44.2], [30.7, 44.2], [30.7, 50.2], [28.0, 50.2], [28.0, 67.5], [24.5, 67.5], [24.5, 69.5], [xw(69.5), 69.5]], (0, -5.0)),
    ("T6", "Midt-SØ",     "Tun Sør",  "#0ea5e9", "#38bdf8", [[28.0, 50.2], [xe(50.2), 50.2], [51.66, 70.59], [xe(73.5), 73.5], [33.5, 73.5], [33.5, 67.5], [28.0, 67.5]], (1.5, -4.0)),
    ("T7", "SV (Onkel)",  "Tun Sør",  "#ec4899", "#f472b6", [[xw(73.5), 73.5], [24.5, 73.5], [24.5, 75.5], [25.5, 75.5], [25.5, ys(25.5)], [6.62, 105.82], [5.06, 80.82]], (-0.5, 4.5)),
    ("T8", "SØ (Onkel)",  "Tun Sør",  "#f43f5e", "#fb7185", [[25.5, 75.5], [33.5, 75.5], [33.5, 73.5], [xe(73.5), 73.5], [51.62, 81.58], [56.19, 90.23], [25.5, ys(25.5)]], (2.5, 4.5)),
]

# Illustrative fotavtrykk for kompakte 2-mannsboliger (ca. 13,5 x 8,3 m = 112 m² ved 30 % BYA!)
C1_footprints = [
    rect_local(12.2, 14.5, 13.5, 8.2),   # T1 (4m fra vest, 8m strøkslinje nord, 4m sør)
    rect_local(40.5, 15.0, 13.5, 8.2),   # T2
    rect_local(41.2, 37.5, 12.5, 9.0),   # T4
    rect_local(15.2, 57.5, 13.5, 8.2),   # T5
    rect_local(40.5, 60.5, 12.5, 9.0),   # T6
    rect_local(15.8, 86.5, 12.5, 9.0),   # T7 (Onkel)
    rect_local(39.0, 84.5, 13.5, 8.2),   # T8 (Onkel)
]

# ---------------- ALT C2: 2x4 GATETUN — 100 % FRA MYRTEVEIEN (0 % avhengig av Trollheggveien!) ----------------
C2_road = [
    [ex0, 0], [ex1, 0], [ex1, ny0], [nx1, ny0], [nx1, ny1], [32.0, ny1],
    [32.0, 69.0], [34.0, 69.0], [34.0, 76.5], [24.5, 76.5], [24.5, 69.0], [28.0, 69.0],
    [28.0, ny1], [nx0, ny1], [nx0, ny0], [ex0, ny0]
]
C2_plots = [
    ("T1", "Nord-Vest",   "Tun Nord", "#10b981", "#34d399", [[0, 0], [ex0, 0], [ex0, ny0], [nx0, ny0], [nx0, 23.2], [xw(23.2), 23.2]], (0, -3.5)),
    ("T2", "Nord-Øst",    "Tun Nord", "#06b6d4", "#22d3ee", [[ex1, 0], [51.89, 0], [xe(24.0), 24.0], [nx1, 24.0], [nx1, ny0], [ex1, ny0]], (0, -3.5)),
    ("T3", "Eksist. hus", "Tun Nord", "#f59e0b", "#fbbf24", [[xw(23.2), 23.2], [nx0, 23.2], [nx0, ny1], [28.0, ny1], [28.0, 45.2], [xw(45.2), 45.2]], (-6.2, 0.5)),
    ("T4", "Midt-NØ",     "Tun Nord", "#3b82f6", "#60a5fa", [[32.0, ny1], [nx1, ny1], [nx1, 24.0], [xe(24.0), 24.0], [xe(49.5), 49.5], [32.0, 49.5]], (0.5, -5.0)),
    ("T5", "Midt-SV",     "Tun Sør",  "#8b5cf6", "#a78bfa", [[xw(45.2), 45.2], [28.0, 45.2], [28.0, 69.0], [24.5, 69.0], [24.5, 70.5], [xw(70.5), 70.5]], (0, -5.0)),
    ("T6", "Midt-SØ",     "Tun Sør",  "#0ea5e9", "#38bdf8", [[32.0, 49.5], [xe(49.5), 49.5], [51.66, 70.59], [xe(77.5), 77.5], [34.0, 77.5], [34.0, 69.0], [32.0, 69.0]], (1.5, -4.0)),
    ("T7", "SV (Onkel)",  "Tun Sør",  "#ec4899", "#f472b6", [[xw(70.5), 70.5], [24.5, 70.5], [24.5, 76.5], [24.5, ys(24.5)], [6.62, 105.82], [5.06, 80.82]], (-0.5, 4.5)),
    ("T8", "SØ (Onkel)",  "Tun Sør",  "#f43f5e", "#fb7185", [[24.5, 76.5], [34.0, 76.5], [34.0, 77.5], [xe(77.5), 77.5], [51.62, 81.58], [56.19, 90.23], [24.5, ys(24.5)]], (2.5, 4.5)),
]
C2_footprints = [
    rect_local(12.2, 14.5, 13.5, 8.2),   # T1
    rect_local(40.5, 15.0, 13.5, 8.2),   # T2
    rect_local(41.8, 37.5, 11.8, 9.5),   # T4
    rect_local(15.2, 57.5, 13.5, 8.2),   # T5
    rect_local(41.8, 63.0, 11.8, 9.5),   # T6
    rect_local(15.2, 87.5, 12.0, 9.2),   # T7 (Onkel)
    rect_local(39.0, 86.0, 13.5, 8.2),   # T8 (Onkel)
]

orig_split_p1 = [5.06, 80.82]
orig_split_p2 = [51.66, 70.59]

print("ALT C1 (2x4 Gatetun, Myrteveien + Trollheggveien):")
for c, n, _, _, _, pts, _ in C1_plots:
    print(f"  {c} {n:12s}: {area_m2(pts):.1f} m2")
print(f"  Tun Nord: {area_m2(C1_tun_n):.1f} m2, Tun Sør: {area_m2(C1_tun_s):.1f} m2 (totalt {area_m2(C1_tun_n)+area_m2(C1_tun_s):.1f} m2)")
print("ALT C2 (2x4 Gatetun, 100% fra Myrteveien):")
for c, n, _, _, _, pts, _ in C2_plots:
    print(f"  {c} {n:12s}: {area_m2(pts):.1f} m2")
print(f"  Vei + 2 gatetun: {area_m2(C2_road):.1f} m2")


def render_panel(plots, roads, footprints, panel_idx):
    els = []
    # Nabotomter
    for key in ["140/1008", "140/995", "140/1014", "141/94"]:
        if key in parcels:
            els.append(f'<polygon points="{poly_wgs_str(parcels[key], panel_idx)}" fill="none" stroke="#ffffff" stroke-opacity="0.38" stroke-width="1.3" stroke-dasharray="4,4"/>')

    # 1. Tomtene
    for code, name, acc, fill, stroke, pts, nudge in plots:
        els.append(f'<polygon points="{poly_local_str(pts, panel_idx)}" fill="{fill}" fill-opacity="0.26" stroke="{stroke}" stroke-width="2.6"/>')

    # 2. Illustrative 2-mannsbolig-fotavtrykk (~112 m², delt i 2 boenheter med midtlinje)
    for fp in footprints:
        els.append(f'<polygon points="{poly_local_str(fp, panel_idx)}" fill="#ffffff" fill-opacity="0.34" stroke="#ffffff" stroke-width="2.0" stroke-dasharray="5,3"/>')
        # Midtlinje mellom de 2 boenhetene i tomannsboligen
        m1 = local_to_canvas([(fp[0][0] + fp[1][0]) / 2, (fp[0][1] + fp[1][1]) / 2], panel_idx)
        m2 = local_to_canvas([(fp[2][0] + fp[3][0]) / 2, (fp[2][1] + fp[3][1]) / 2], panel_idx)
        els.append(f'<line x1="{m1[0]:.1f}" y1="{m1[1]:.1f}" x2="{m2[0]:.1f}" y2="{m2[1]:.1f}" stroke="#ffffff" stroke-width="1.5" stroke-dasharray="3,2"/>')

    # 3. Gatetun / vei (varm brostein/tun-farge!)
    for rpts, label, lpos in roads:
        els.append(f'<polygon points="{poly_local_str(rpts, panel_idx)}" fill="#fef3c7" fill-opacity="0.68" stroke="#b45309" stroke-width="2.4" stroke-dasharray="6,3"/>')
        lp = local_to_canvas(lpos, panel_idx)
        els.append(f'''
        <g transform="translate({lp[0] - 72:.1f}, {lp[1] - 11:.1f})">
          <rect width="144" height="22" rx="5" fill="#78350f" fill-opacity="0.95" stroke="#fde68a" stroke-width="1.3"/>
          <text x="72" y="14.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="9.0" fill="#ffffff">{label}</text>
        </g>
        ''')

    # 4. Tomte-kort (etter fotavtrykk så tekst er skarp)
    for code, name, acc, fill, stroke, pts, nudge in plots:
        ar = area_m2(pts)
        c = centroid_local(pts) + np.array(nudge)
        cp = local_to_canvas(c, panel_idx)
        bya30 = ar * 0.30
        els.append(f'''
        <g transform="translate({cp[0] - 68:.1f}, {cp[1] - 25:.1f})">
          <rect width="136" height="50" rx="6" fill="#0f172a" fill-opacity="0.88" stroke="{stroke}" stroke-width="1.7"/>
          <text x="68" y="15" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.2" fill="{stroke}">{code} • {name}</text>
          <text x="68" y="30.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="12.2" fill="#ffffff">ca. {ar:.0f} m²</text>
          <text x="68" y="43.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="8.2" fill="#cbd5e1">30% BYA ≤ {bya30:.0f} m² • {acc}</text>
        </g>
        ''')

    # 5. Opprinnelig grense M6 / Onkel (gul stiplet + etikett utenfor i østmarg)
    sp1 = local_to_canvas(orig_split_p1, panel_idx)
    sp2 = local_to_canvas(orig_split_p2, panel_idx)
    els.append(f'<line x1="{sp1[0]:.1f}" y1="{sp1[1]:.1f}" x2="{sp2[0]:.1f}" y2="{sp2[1]:.1f}" stroke="#facc15" stroke-width="3.0" stroke-dasharray="9,5"/>')
    smid = sp2 + np.array([104.0, -22.0])
    els.append(f'<line x1="{sp2[0] + 4:.1f}" y1="{sp2[1] - 1:.1f}" x2="{smid[0] - 86:.1f}" y2="{smid[1]:.1f}" stroke="#facc15" stroke-width="2.0"/>')
    els.append(f'''
    <g transform="translate({smid[0] - 86:.1f}, {smid[1] - 15:.1f})">
      <rect width="172" height="30" rx="5" fill="#422006" fill-opacity="0.94" stroke="#facc15" stroke-width="1.4"/>
      <text x="86" y="12.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="8.4" fill="#fef08a">Dagens grense M6 / Onkel</text>
      <text x="86" y="24" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="8.0" fill="#fde047">140/371 vs. 140/1247</text>
    </g>
    ''')

    # Ytre ramme
    els.append(f'<polygon points="{poly_wgs_str(parcels["140/371"], panel_idx)}" fill="none" stroke="#ffffff" stroke-width="1.8" stroke-opacity="0.7"/>')
    els.append(f'<polygon points="{poly_wgs_str(parcels["140/1247"], panel_idx)}" fill="none" stroke="#facc15" stroke-width="2.2" stroke-opacity="0.85"/>')

    # Eksist. hus badge
    hc = local_to_canvas(np.array([21.1, 33.3]), panel_idx)
    els.append(f'''
    <g transform="translate({hc[0] - 44:.1f}, {hc[1] - 10:.1f})">
      <rect width="88" height="20" rx="4" fill="#78350f" fill-opacity="0.94" stroke="#fde68a" stroke-width="1.4"/>
      <text x="44" y="13.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="9.0" fill="#ffffff">EKSIST. HUS</text>
    </g>
    ''')

    # Veinavn
    mv = local_to_canvas(np.array([22.0, -7.0]), panel_idx)
    els.append(f'''
    <g transform="translate({mv[0]:.1f}, {mv[1]:.1f}) rotate(-14)">
      <rect x="-48" y="-9" width="96" height="18" rx="4" fill="#0f172a" fill-opacity="0.88"/>
      <text x="0" y="3.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="9.5" fill="#38bdf8" letter-spacing="1">MYRTEVEIEN</text>
    </g>
    ''')
    th = local_to_canvas(np.array([-5.5, 58.0]), panel_idx)
    els.append(f'''
    <g transform="translate({th[0]:.1f}, {th[1]:.1f}) rotate(73)">
      <rect x="-58" y="-9" width="116" height="18" rx="4" fill="#0f172a" fill-opacity="0.88"/>
      <text x="0" y="3.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="9.5" fill="#38bdf8" letter-spacing="1">TROLLHEGGVEIEN</text>
    </g>
    ''')
    return "\n".join(els)


ox0 = MARGIN_X
ox1 = MARGIN_X + PW + GAP

C1_roads_render = [
    (C1_tun_n, f"GATETUN NORD ({area_m2(C1_tun_n):.0f} m²)", [28.0, 20.8]),
    (C1_tun_s, f"GATETUN SØR ({area_m2(C1_tun_s):.0f} m²)", [29.0, 71.5]),
]
C2_roads_render = [
    (C2_road, f"GATETUN NORD ({area_m2(C2_road):.0f} m² tot.)", [28.0, 20.8]),
    ([[[0,0],[0,0],[0,0]]][0], "GATETUN SØR (koblet)", [29.2, 72.8]),
]
# Clean render for C2: draw C2_road once, and add two crisp labels (Nord-tun & Sør-tun)
def render_panel_c2():
    s = render_panel(C2_plots, [(C2_road, "GATETUN NORD", [28.0, 20.8])], C2_footprints, 1)
    lp = local_to_canvas([29.2, 72.8], 1)
    s += f'''
    <g transform="translate({lp[0] - 62:.1f}, {lp[1] - 11:.1f})">
      <rect width="124" height="22" rx="5" fill="#78350f" fill-opacity="0.95" stroke="#fde68a" stroke-width="1.3"/>
      <text x="62" y="14.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="9.2" fill="#ffffff">GATETUN SØR</text>
    </g>
    '''
    return s


svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <rect x="0" y="0" width="{W}" height="{HEADER_H}" fill="#0f172a"/>
  <rect x="0" y="{HEADER_H + PH}" width="{W}" height="{FOOTER_H}" fill="#0f172a"/>
  <rect x="0" y="{HEADER_H}" width="{MARGIN_X}" height="{PH}" fill="#0f172a"/>
  <rect x="{ox0 + PW}" y="{HEADER_H}" width="{GAP}" height="{PH}" fill="#0f172a"/>
  <rect x="{ox1 + PW}" y="{HEADER_H}" width="{MARGIN_X}" height="{PH}" fill="#0f172a"/>

  <!-- Hovedbanner -->
  <text x="{W/2:.1f}" y="38" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="23" fill="#ffffff">ALTERNATIV C: 2×4 TOMTER MED TO GATETUN + 2-MANNSBOLIG-TEST</text>
  <text x="{W/2:.1f}" y="68" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="14.5" fill="#fbbf24">Myrteveien 6 (140/371) + Onkels tomt (140/1247) = ca. 4 839 m² • 4 + 4 tomter møtes i felles Nord- og Sør-tun</text>
  <text x="{W/2:.1f}" y="94" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="12.2" fill="#cbd5e1">Hvite stiplede bokser viser illustrative fotavtrykk for kompakte 2-mannsboliger (~112 m² grunnflate = 2 × ~110 m² BRA ved 30 % BYA)</text>

  {render_panel(C1_plots, C1_roads_render, C1_footprints, 0)}
  {render_panel_c2()}

  <rect x="{ox0}" y="{HEADER_H}" width="{PW}" height="{PH}" fill="none" stroke="#f59e0b" stroke-width="2.8"/>
  <rect x="{ox1}" y="{HEADER_H}" width="{PW}" height="{PH}" fill="none" stroke="#10b981" stroke-width="2.8"/>

  <!-- Panel A toppkort -->
  <g transform="translate({ox0 + 14}, {HEADER_H + 14})">
    <rect width="645" height="68" rx="8" fill="#0f172a" fill-opacity="0.93" stroke="#f59e0b" stroke-width="2.0"/>
    <text x="14" y="25" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="15.0" fill="#fbbf24">ALT. C1: 2×4 GATETUN — Nord fra Myrteveien + Sør fra Trollheggveien</text>
    <text x="14" y="44" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.5" fill="#ffffff">8 tomter 519–628 m² (snitt 566 m²) • Kun 295 m² totalt til 2 gatetun (6,1 %!)</text>
    <text x="14" y="60" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.5" fill="#fde68a">Svært arealeffektivt! Ingen gjennomkjøring mellom tunene • Krever veirett for Sør-tun i Trollheggveien</text>
  </g>

  <!-- Panel B toppkort -->
  <g transform="translate({ox1 + 14}, {HEADER_H + 14})">
    <rect width="712" height="68" rx="8" fill="#0f172a" fill-opacity="0.93" stroke="#10b981" stroke-width="2.0"/>
    <text x="14" y="25" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="15.0" fill="#34d399">ALT. C2: 2×4 GATETUN KOBLET — 100 % fra Myrteveien (0 % Trollheggveien)</text>
    <text x="14" y="44" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.5" fill="#ffffff">8 tomter 504–620 m² (snitt 554 m²) • 392 m² totalt til vei + 2 gatetun (8,1 %)</text>
    <text x="14" y="60" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.5" fill="#a7f3d0">Begge gatetun betjenes fra kommunal vei Myrteveien — 0 % avhengig av privat veieier i Trollheggveien!</text>
  </g>

  <!-- Bunnpanel: 2-mannsbolig-vurdering -->
  <g transform="translate({MARGIN_X}, {HEADER_H + PH + 14})">
    <rect width="{W - MARGIN_X * 2}" height="136" rx="8" fill="#1e293b" stroke="#475569" stroke-width="1.6"/>
    <text x="20" y="26" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="14" fill="#ffffff">KONKLUSJON: KAN MAN BYGGE 2-MANNSBOLIGER PÅ 2×4 GATETUN-TOMTENE (~550–590 m²)?</text>
    <text x="20" y="50" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.8" fill="#fca5a5">1. Under standard 25 % BYA (frittliggende småhus): NEI / FOR TRANGT — 25 % av 565 m² = 141 m²; minus 3–4 p-plasser (54–72 m²) gir bare 69–87 m² fotavtrykk for hele bygget.</text>
    <text x="20" y="72" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.8" fill="#fde68a">2. Under regulert 30 % BYA (konsentrert småhus i detaljregulering): TEKNISK MULIG for kompakte 2-mannsboliger (~112 m² fotavtrykk + 3 p-plasser = 166 m² BYA → 2 × ~110 m² BRA), men stramt på MUA og gir 15 boenheter totalt.</text>
    <text x="20" y="94" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.8" fill="#86efac">3. To smarteste veier til maksimal verdi: (a) 2×4 tomter med enebolig + utleiedel/sekundærleilighet (mye lettere politisk enn 15 hovedenheter!), ELLER (b) 2×3 = 6 tomter à ~730–750 m² rundt samme to gatetun (oppfyller Tønsbergs 750 m²-norm for 2-mannsbolig → 11–12 romslige boenheter!).</text>
    <text x="20" y="118" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.2" fill="#94a3b8">Kartgrunnlag: Google Maps Satellite (z=20) &amp; Kartverket / Geonorge Matrikkel API (Tønsberg 3905). Hvite bokser er illustrative 2-mannsboliger (ca. 13,5 × 8,2 m = 111 m²).</text>
  </g>
</svg>
'''

svg_path = os.path.join(assets_dir, "utparsellering_2x4_gatetun_satellitt.svg")
overlay_png = "/tmp/gatetun_2x4_overlay.png"
png_path = os.path.join(assets_dir, "utparsellering_2x4_gatetun_satellitt.png")

with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg)

res = subprocess.run(
    ["inkscape", svg_path, "-o", overlay_png, "--export-area-page", f"--export-width={W}"],
    capture_output=True, text=True
)
if res.returncode != 0:
    raise RuntimeError(f"Inkscape failed: {res.stderr}")

base = Image.new("RGBA", (W, H), (15, 23, 42, 255))
base.paste(sat_panel, (ox0, HEADER_H))
base.paste(sat_panel, (ox1, HEADER_H))

ov = Image.open(overlay_png).convert("RGBA")
if ov.size != base.size:
    ov = ov.resize(base.size, Image.Resampling.LANCZOS)
composed = Image.alpha_composite(base, ov).convert("RGB")
composed.save(png_path, format="PNG", optimize=True)
os.remove(overlay_png)
print(f"Saved 2x4 gatetun satellite plan: {png_path} ({composed.size[0]}x{composed.size[1]})")
