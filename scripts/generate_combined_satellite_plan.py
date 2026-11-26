"""
Genererer høyoppløselig satellitt-oversiktsplan (Google Maps satellittkart z=20 +
offisielle Kartverket/Geonorge matrikkelgrenser) for felles utparsellering av:
  - Myrteveien 6 (Gnr 140 / Bnr 371 — 3 752 m²)
  - Onkels tomt i sydenden: Trollheggveien 8 (Gnr 140 / Bnr 1247 — 1 087 m² i matrikkelen)
  - Samlet utviklingsområde: ~4 839 m² (~4,84 mål)

Panel A (Venstre): 8 tomter (~555–615 m², snitt 576 m²) — Myrteveien + Trollheggveien
Panel B (Høyre):   7 tomter (~600–615 m²) + 225 m² nærlekeplass — 100 % fra Myrteveien (0 % avhengig av Trollheggveien!)
"""

import io
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

# 1. Hent eksakte offisielle matrikkelgrenser fra Geonorge (eller fra /tmp-cache)
cache_json = "/tmp/m6_parcels_wgs84.json"
if os.path.exists(cache_json):
    with open(cache_json) as f:
        parcels = json.load(f)
else:
    parcels = {}
    for gnr, bnr in [(140, 371), (140, 1247), (140, 1008), (140, 995), (140, 1014), (141, 94)]:
        u = f"https://ws.geonorge.no/eiendom/v1/geokoding?kommunenummer=3905&gardsnummer={gnr}&bruksnummer={bnr}&omrade=true"
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read().decode())
        parcels[f"{gnr}/{bnr}"] = d["features"][0]["geometry"]["coordinates"][0]
    with open(cache_json, "w") as f:
        json.dump(parcels, f)

# 2. Web Mercator hjelpefunksjoner for Google Maps Satellite (zoom 20)
ZOOM = 20
TILE_SIZE = 256


def latlon_to_world_px(lat, lon, z=ZOOM):
    n = 2.0 ** z
    x = (lon + 180.0) / 360.0 * n * TILE_SIZE
    lat_rad = math.radians(lat)
    y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n * TILE_SIZE
    return np.array([x, y])


# Beregn bounding box rundt 140/371 + 140/1247 med god luft
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

# Last ned Google Maps satellitt-fliser (cached i /tmp/gm_tiles)
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

# Beskjær til eksakt panel-utsnitt
cx0 = wx0 - tx0 * TILE_SIZE
cy0 = wy0 - ty0 * TILE_SIZE
PW = wx1 - wx0
PH = wy1 - wy0
sat_panel = stitched.crop((cx0, cy0, cx0 + PW, cy0 + PH))
print(f"Google Maps satellittpanel z={ZOOM}: {PW} x {PH} px ({(tx1-tx0+1)*(ty1-ty0+1)} fliser)")

# 3. Eksakt lokalt metersystem (x=øst langs Myrteveien, y=sør vinkelrett) -> WGS84 -> lerret!
lat0 = 59.2666356
lon0 = 10.4757783
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


# Side-om-side lerret
GAP = 32
MARGIN_X = 24
HEADER_H = 114
FOOTER_H = 152
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


# ---------------- ALTERNATIV A: 8 TOMTER (~555–615 m², snitt 576 m²) ----------------
# Myrteveien + Trollheggveien + kort 4 m L-stikkvei (216 m²)
A_road = [[xw(43.8), 43.8], [30.7, 43.8], [30.7, 73.5], [26.7, 73.5], [26.7, 47.8], [xw(47.8), 47.8]]
A_plots = [
    ("T1", "Nord-Vest",    "Myrteveien",   "#10b981", "#34d399", [[0.0, 0.0], [25.5, 0.0], [25.5, 23.2], [xw(23.2), 23.2]], (0, 0)),
    ("T2", "Nord-Øst",     "Myrteveien",   "#06b6d4", "#22d3ee", [[25.5, 0.0], [51.89, 0.0], [xe(23.2), 23.2], [25.5, 23.2]], (0, 0)),
    ("T3", "Eksist. hus",  "Trollheggvn.", "#f59e0b", "#fbbf24", [[xw(23.2), 23.2], [30.7, 23.2], [30.7, 43.8], [xw(43.8), 43.8]], (-6.5, 0)),
    ("T4", "Midt-NØ",      "Stikkvei",     "#3b82f6", "#60a5fa", [[30.7, 23.2], [xe(23.2), 23.2], [xe(48.5), 48.5], [30.7, 48.5]], (0, 0)),
    ("T5", "Midt-SV",      "Trollheggvn.", "#8b5cf6", "#a78bfa", [[xw(47.8), 47.8], [26.7, 47.8], [26.7, 74.5], [xw(74.5), 74.5]], (0, 0)),
    ("T6", "Midt-SØ",      "Stikkvei",     "#0ea5e9", "#38bdf8", [[30.7, 48.5], [xe(48.5), 48.5], [xe(73.5), 73.5], [30.7, 73.5]], (0, 0)),
    ("T7", "SV (Onkel)",   "Trollheggvn.", "#ec4899", "#f472b6", [[xw(74.5), 74.5], [26.7, 74.5], [26.7, ys(26.7)], [6.62, 105.82], [5.06, 80.82]], (0, 1.5)),
    ("T8", "SØ (Onkel)",   "Stikkvei",     "#f43f5e", "#fb7185", [[26.7, 73.5], [30.7, 73.5], [xe(73.5), 73.5], [51.62, 81.58], [56.19, 90.23], [26.7, ys(26.7)]], (1.5, 1.0)),
]

# ---------------- ALTERNATIV B: 7 TOMTER (~600–615 m²) + 225 m² NÆRLEKEPLASS ----------------
# 100 % fra kommunal vei Myrteveien — 0 % avhengig av privat veirett i Trollheggveien!
B_road = [[28.0, 0.0], [32.0, 0.0], [32.0, 72.0], [35.5, 72.0], [35.5, 78.0], [24.5, 78.0], [24.5, 72.0], [28.0, 72.0]]
B_lek = [[24.5, 78.0], [35.5, 78.0], [35.5, ys(35.5)], [24.5, ys(24.5)]]
B_plots = [
    ("T1", "Nord-Vest",    "Myrteveien",     "#10b981", "#34d399", [[0.0, 0.0], [28.0, 0.0], [28.0, 22.5], [xw(22.5), 22.5]], (0, 0)),
    ("T2", "Nord-Øst",     "Myrteveien",     "#06b6d4", "#22d3ee", [[32.0, 0.0], [51.89, 0.0], [xe(30.5), 30.5], [32.0, 30.5]], (0, 0)),
    ("T3", "Eksist. hus",  "Stikkvei",       "#f59e0b", "#fbbf24", [[xw(22.5), 22.5], [28.0, 22.5], [28.0, 46.0], [xw(46.0), 46.0]], (-6.5, 1.5)),
    ("T4", "Midt-Øst",     "Stikkvei",       "#3b82f6", "#60a5fa", [[32.0, 30.5], [xe(30.5), 30.5], [xe(60.5), 60.5], [32.0, 60.5]], (0, 0)),
    ("T5", "Midt-SV",      "Stikkvei/tun",   "#8b5cf6", "#a78bfa", [[xw(46.0), 46.0], [28.0, 46.0], [28.0, 71.0], [xw(71.0), 71.0]], (0, 0)),
    ("T6", "SØ (Onkel)",   "Stikkvei/tun",   "#ec4899", "#f472b6", [[32.0, 60.5], [xe(60.5), 60.5], [51.66, 70.59], [51.62, 81.58], [56.19, 90.23], [35.5, ys(35.5)], [35.5, 72.0], [32.0, 72.0]], (3.5, 5.0)),
    ("T7", "SV (Onkel)",   "Stikkvei/tun",   "#f43f5e", "#fb7185", [[xw(71.0), 71.0], [28.0, 71.0], [28.0, 72.0], [24.5, 72.0], [24.5, ys(24.5)], [6.62, 105.82], [5.06, 80.82]], (-1.0, 2.5)),
]

# Eksisterende delelinje mellom Myrteveien 6 (140/371) og onkels tomt (140/1247)
orig_split_p1 = [5.06, 80.82]
orig_split_p2 = [51.66, 70.59]

# Skriv ut nøyaktige arealer til konsoll
print("ALT A (8 tomter):")
for c, n, _, _, _, pts, _ in A_plots:
    print(f"  {c} {n:14s}: {area_m2(pts):.1f} m2")
print(f"  Stikkvei         : {area_m2(A_road):.1f} m2")
print("ALT B (7 tomter + lekeplass):")
for c, n, _, _, _, pts, _ in B_plots:
    print(f"  {c} {n:14s}: {area_m2(pts):.1f} m2")
print(f"  Nærlekeplass     : {area_m2(B_lek):.1f} m2")
print(f"  Vei + snutun     : {area_m2(B_road):.1f} m2")


def render_panel(plots, road, panel_idx, lek=None):
    els = []
    # Svak hvit/gul omriss av nabotomter for kontekst
    for key in ["140/1008", "140/995", "140/1014", "141/94"]:
        if key in parcels:
            els.append(f'<polygon points="{poly_wgs_str(parcels[key], panel_idx)}" fill="none" stroke="#ffffff" stroke-opacity="0.38" stroke-width="1.3" stroke-dasharray="4,4"/>')

    # 1. Tomtene (semi-transparent over satellittfoto så hus, trær og veier synes tydelig!)
    for code, name, acc, fill, stroke, pts, nudge in plots:
        ar = area_m2(pts)
        els.append(f'<polygon points="{poly_local_str(pts, panel_idx)}" fill="{fill}" fill-opacity="0.28" stroke="{stroke}" stroke-width="2.8"/>')
        c = centroid_local(pts) + np.array(nudge)
        cp = local_to_canvas(c, panel_idx)
        bya = ar * 0.25
        els.append(f'''
        <g transform="translate({cp[0] - 64:.1f}, {cp[1] - 26:.1f})">
          <rect width="128" height="52" rx="6" fill="#0f172a" fill-opacity="0.86" stroke="{stroke}" stroke-width="1.8"/>
          <text x="64" y="16" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.5" fill="{stroke}">{code} • {name}</text>
          <text x="64" y="32" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="12.5" fill="#ffffff">ca. {ar:.0f} m²</text>
          <text x="64" y="45" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="8.6" fill="#cbd5e1">BYA ≤ {bya:.0f} m² • {acc}</text>
        </g>
        ''')

    # 2. Felles vei / snutun
    r_ar = area_m2(road)
    els.append(f'<polygon points="{poly_local_str(road, panel_idx)}" fill="#e2e8f0" fill-opacity="0.58" stroke="#0f172a" stroke-width="2.2" stroke-dasharray="5,3"/>')
    if panel_idx == 0:
        rc = local_to_canvas(np.array([15.0, 45.8]), panel_idx)
        els.append(f'''
        <g transform="translate({rc[0] - 58:.1f}, {rc[1] - 10:.1f})">
          <rect width="116" height="20" rx="4" fill="#0f172a" fill-opacity="0.92"/>
          <text x="58" y="13.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.2" fill="#f8fafc">Stikkvei 4 m ({r_ar:.0f} m²)</text>
        </g>
        ''')
    else:
        rc = local_to_canvas(np.array([30.0, 75.0]), panel_idx)
        els.append(f'''
        <g transform="translate({rc[0] - 64:.1f}, {rc[1] - 10:.1f})">
          <rect width="128" height="20" rx="4" fill="#0f172a" fill-opacity="0.94"/>
          <text x="64" y="13.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.2" fill="#f8fafc">Vei + snutun ({r_ar:.0f} m²)</text>
        </g>
        ''')

    # 3. Felles nærlekeplass (Panel B)
    if lek is not None:
        l_ar = area_m2(lek)
        els.append(f'<polygon points="{poly_local_str(lek, panel_idx)}" fill="#84cc16" fill-opacity="0.45" stroke="#bef264" stroke-width="2.4" stroke-dasharray="5,3"/>')
        lc = local_to_canvas(centroid_local(lek), panel_idx)
        els.append(f'''
        <g transform="translate({lc[0] - 50:.1f}, {lc[1] - 18:.1f})">
          <rect width="100" height="36" rx="5" fill="#1a2e05" fill-opacity="0.92" stroke="#a3e635" stroke-width="1.5"/>
          <text x="50" y="14" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="9.2" fill="#bef264">NÆRLEKEPLASS</text>
          <text x="50" y="29" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="11.2" fill="#ffffff">ca. {l_ar:.0f} m²</text>
        </g>
        ''')

    # 4. Opprinnelig grense mellom 140/371 (M6) og 140/1247 (Onkel) — gul stiplet linje + merkelapp UTENFOR i østmarg!
    sp1 = local_to_canvas(orig_split_p1, panel_idx)
    sp2 = local_to_canvas(orig_split_p2, panel_idx)
    els.append(f'<line x1="{sp1[0]:.1f}" y1="{sp1[1]:.1f}" x2="{sp2[0]:.1f}" y2="{sp2[1]:.1f}" stroke="#facc15" stroke-width="3.2" stroke-dasharray="9,5"/>')
    smid = sp2 + np.array([106.0, -24.0])
    els.append(f'<line x1="{sp2[0] + 4:.1f}" y1="{sp2[1] - 1:.1f}" x2="{smid[0] - 88:.1f}" y2="{smid[1]:.1f}" stroke="#facc15" stroke-width="2.0"/>')
    els.append(f'''
    <g transform="translate({smid[0] - 88:.1f}, {smid[1] - 16:.1f})">
      <rect width="176" height="32" rx="5" fill="#422006" fill-opacity="0.94" stroke="#facc15" stroke-width="1.4"/>
      <text x="88" y="13" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="8.6" fill="#fef08a">Dagens grense M6 / Onkel</text>
      <text x="88" y="25" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="8.2" fill="#fde047">140/371 vs. 140/1247</text>
    </g>
    ''')

    # 5. Ytre felles eiendomsgrense (kraftig hvit/gul ramme rundt hele 4 839 m² feltet)
    els.append(f'<polygon points="{poly_wgs_str(parcels["140/371"], panel_idx)}" fill="none" stroke="#ffffff" stroke-width="2.0" stroke-opacity="0.7"/>')
    els.append(f'<polygon points="{poly_wgs_str(parcels["140/1247"], panel_idx)}" fill="none" stroke="#facc15" stroke-width="2.2" stroke-opacity="0.85"/>')

    # 6. Eksisterende 1947-hus-badge rett over hustaket
    hc = local_to_canvas(np.array([21.1, 33.3]), panel_idx)
    els.append(f'''
    <g transform="translate({hc[0] - 44:.1f}, {hc[1] - 10:.1f})">
      <rect width="88" height="20" rx="4" fill="#78350f" fill-opacity="0.94" stroke="#fde68a" stroke-width="1.4"/>
      <text x="44" y="13.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="9.0" fill="#ffffff">EKSIST. HUS</text>
    </g>
    ''')

    # 7. Veinavn på satellittkartet
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

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <!-- Marger rundt de to satellittpanelene -->
  <rect x="0" y="0" width="{W}" height="{HEADER_H}" fill="#0f172a"/>
  <rect x="0" y="{HEADER_H + PH}" width="{W}" height="{FOOTER_H}" fill="#0f172a"/>
  <rect x="0" y="{HEADER_H}" width="{MARGIN_X}" height="{PH}" fill="#0f172a"/>
  <rect x="{ox0 + PW}" y="{HEADER_H}" width="{GAP}" height="{PH}" fill="#0f172a"/>
  <rect x="{ox1 + PW}" y="{HEADER_H}" width="{MARGIN_X}" height="{PH}" fill="#0f172a"/>

  <!-- Hovedbanner -->
  <text x="{W/2:.1f}" y="38" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="23" fill="#ffffff">FELLES UTPARSELLERING — MYRTEVEIEN 6 (140/371) + ONKELS TOMT (140/1247)</text>
  <text x="{W/2:.1f}" y="68" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="14.5" fill="#38bdf8">Samlet areal: ca. 4 839 m² (3 752 m² + 1 087 m² i matrikkelen) • Google Maps satellittkart + Kartverket eiendomsgrenser</text>
  <text x="{W/2:.1f}" y="94" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="12.2" fill="#cbd5e1">Beholder eksisterende 1947-hus • Felles regulering fjerner skrå skillelinje mellom M6 og onkel (140/1247) og gir 7–8 fullverdige ~600 m²-tomter</text>

  <!-- Panel A & B innhold -->
  {render_panel(A_plots, A_road, 0, lek=None)}
  {render_panel(B_plots, B_road, 1, lek=B_lek)}

  <!-- Rammer rundt panelene -->
  <rect x="{ox0}" y="{HEADER_H}" width="{PW}" height="{PH}" fill="none" stroke="#38bdf8" stroke-width="2.8"/>
  <rect x="{ox1}" y="{HEADER_H}" width="{PW}" height="{PH}" fill="none" stroke="#10b981" stroke-width="2.8"/>

  <!-- Panel A toppkort -->
  <g transform="translate({ox0 + 14}, {HEADER_H + 14})">
    <rect width="585" height="68" rx="8" fill="#0f172a" fill-opacity="0.92" stroke="#38bdf8" stroke-width="2.0"/>
    <text x="14" y="25" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="15.5" fill="#38bdf8">ALT. A: 8 TOMTER (525–611 m²) — Myrteveien + Trollheggveien</text>
    <text x="14" y="44" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.5" fill="#ffffff">1 eksist. hus + 7 nye tomter (6 på M6 + 2 på onkel) • Stikkvei 214 m²</text>
    <text x="14" y="60" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.5" fill="#fbbf24">Forutsetning: Utvidet veirett i privat vei Trollheggveien (141/1) + detaljregulering</text>
  </g>

  <!-- Panel B toppkort -->
  <g transform="translate({ox1 + 14}, {HEADER_H + 14})">
    <rect width="625" height="68" rx="8" fill="#0f172a" fill-opacity="0.92" stroke="#10b981" stroke-width="2.0"/>
    <text x="14" y="25" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="15.5" fill="#34d399">ALT. B: 7 TOMTER (~605 m²) + LEKEPLASS — 100 % fra Myrteveien</text>
    <text x="14" y="44" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.5" fill="#ffffff">Alle 7 tomter 592–614 m² + 225 m² nærlekeplass + snutun (354 m²)</text>
    <text x="14" y="60" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.5" fill="#a7f3d0">Største fordel: 0 % avhengig av privat veieier i Trollheggveien • Mest reguleringssikker!</text>
  </g>

  <!-- Bunnpanel -->
  <g transform="translate({MARGIN_X}, {HEADER_H + PH + 14})">
    <rect width="{W - MARGIN_X * 2}" height="122" rx="8" fill="#1e293b" stroke="#475569" stroke-width="1.6"/>
    <text x="20" y="26" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="14" fill="#ffffff">AREALFORDELING &amp; SYNERGI MELLOM MYRTEVEIEN 6 (140/371) OG ONKELS TOMT (140/1247)</text>
    <text x="20" y="50" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.8" fill="#e2e8f0">1. Matrikkelobservasjon: Kartverket/Geonorge viser 1 087 m² på Trollheggveien 8 (140/1247) + 3 752 m² på Myrteveien 6 (140/371) = ca. 4 839 m² (77,5 % M6 / 22,5 % onkel).</text>
    <text x="20" y="72" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.8" fill="#e2e8f0">2. Synergi for onkel: Alene er 140/1247 (1 087 m²) trang/skrå for to 600 m²-tomter. Felles detaljregulering retter ut skrågrensen og gir onkel 2 fullverdige tomter (~600 m² hver) med ordnet vei/VA!</text>
    <text x="20" y="94" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.8" fill="#93c5fd">3. Anbefaling: Alt. B (7 tomter à ~605 m² + 225 m² lekeplass, 100 % fra kommunal vei Myrteveien) gir 5 tomter til M6 + 2 til onkel (eller fordeling etter eksakt arealnøkkel) uten veirettrisiko i Trollheggveien.</text>
    <text x="20" y="113" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.2" fill="#94a3b8">Kartgrunnlag: Google Maps Satellite (z=20) &amp; Kartverket / Geonorge Matrikkel API (Tønsberg kommune 3905). Foreløpig mulighetsskisse.</text>
  </g>
</svg>
'''

svg_path = os.path.join(assets_dir, "utparsellering_m6_og_onkel_satellitt.svg")
overlay_png = "/tmp/combined_sat_overlay.png"
png_path = os.path.join(assets_dir, "utparsellering_m6_og_onkel_satellitt.png")

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
print(f"Saved satellite masterplan: {png_path} ({composed.size[0]}x{composed.size[1]})")
