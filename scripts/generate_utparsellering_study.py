"""
Genererer visuell mulighetsstudie (side-om-side SVG + PNG) for maksimal oppdeling
av Myrteveien 6 (Gnr 140 / Bnr 371, 3 752 m²) til flest mulig fornuftige ~600 m²-tomter
mens eksisterende 1947-bolig beholdes.

Panel A (Venstre): 6 tomter (586–638 m², snitt 604 m²) med veirett i Trollheggveien + Myrteveien
Panel B (Høyre):   5 tomter (625–696 m²) + 150 m² nærlekeplass — 100 % fra Myrteveien (uavhengig av Trollheggveien)
"""

import os
import subprocess
import numpy as np
from PIL import Image

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
assets_dir = os.path.join(repo_root, "assets", "images")

bg_im = Image.open(os.path.join(assets_dir, "situasjonsplan_render.png")).convert("RGBA")

# Beskjær hele 3 752 m²-eiendommen rent uten tittelfelt i bunnen
CROP_X0, CROP_Y0 = 420, 120
CROP_X1, CROP_Y1 = 1660, 1545
PW = CROP_X1 - CROP_X0  # 1240 per panel
PH = CROP_Y1 - CROP_Y0  # 1425 per panel
crop_panel = bg_im.crop((CROP_X0, CROP_Y0, CROP_X1, CROP_Y1))

# Side-om-side lerret: to paneler + toppbanner + bunnpanel
GAP = 36
MARGIN_X = 28
HEADER_H = 112
FOOTER_H = 148
W = MARGIN_X * 2 + PW * 2 + GAP     # 2572
H = HEADER_H + PH + FOOTER_H        # 1730

# Kalibrerte hjørner på situasjonsplan_render.png (14,7909 px/m)
PX = 14.7909
NW_ORIG = np.array([548.8, 395.7])
NE_ORIG = np.array([1292.8, 207.2])
SE_ORIG = np.array([1546.2, 1218.2])
SW_ORIG = np.array([915.2, 1534.3])

u_e = (NE_ORIG - NW_ORIG) / np.linalg.norm(NE_ORIG - NW_ORIG)
u_s = np.array([-u_e[1], u_e[0]])
if u_s[1] < 0:
    u_s = -u_s


def to_local(p):
    v = p - NW_ORIG
    return np.array([np.dot(v, u_e) / PX, np.dot(v, u_s) / PX])


L_NW = to_local(NW_ORIG)
L_NE = to_local(NE_ORIG)
L_SE = to_local(SE_ORIG)
L_SW = to_local(SW_ORIG)


def xw(y):
    return L_NW[0] + (y / L_SW[1]) * (L_SW[0] - L_NW[0])


def xe(y):
    return L_NE[0] + (y / L_SE[1]) * (L_SE[0] - L_NE[0])


def ys(x):
    return L_SW[1] + ((x - L_SW[0]) / (L_SE[0] - L_SW[0])) * (L_SE[1] - L_SW[1])


def area_m2(pts):
    return 0.5 * abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts))))


def to_canvas(xy, panel_idx):
    p_orig = NW_ORIG + xy[0] * PX * u_e + xy[1] * PX * u_s
    ox = MARGIN_X + panel_idx * (PW + GAP)
    oy = HEADER_H
    return np.array([p_orig[0] - CROP_X0 + ox, p_orig[1] - CROP_Y0 + oy])


def poly_canvas_str(pts, panel_idx):
    return " ".join(f"{to_canvas(p, panel_idx)[0]:.1f},{to_canvas(p, panel_idx)[1]:.1f}" for p in pts)


def centroid_local(pts):
    """Arealvektet tyngdepunkt for polygon i lokale meterkoordinater."""
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


# ---------------- ALTERNATIV A: 6 TOMTER (Myrteveien + Trollheggveien) ----------------
A_plots = [
    ("T1", "Nord-Vest",   "Myrteveien",     "#10b981", "#047857", [[0.0, 0.0], [26.0, 0.0], [26.0, 23.2], [xw(23.2), 23.2]], (0, 0)),
    ("T2", "Nord-Øst",    "Myrteveien",     "#06b6d4", "#0e7490", [[26.0, 0.0], [L_NE[0], 0.0], [xe(23.2), 23.2], [26.0, 23.2]], (0, 0)),
    ("T3", "Eksist. hus", "Trollheggvn.",   "#f59e0b", "#b45309", [[xw(23.2), 23.2], [30.8, 23.2], [30.8, 43.8], [xw(43.8), 43.8]], (-6.5, 0.0)),
    ("T4", "Midt-Øst",    "Stikkvei",       "#3b82f6", "#1d4ed8", [[30.8, 23.2], [xe(23.2), 23.2], [xe(51.4), 51.4], [30.8, 51.4]], (0, 0)),
    ("T5", "Sør-Vest",    "Trollheggvn.",   "#8b5cf6", "#6d28d9", [[xw(47.8), 47.8], [24.0, 47.8], [24.0, ys(24.0)], [L_SW[0], L_SW[1]]], (0, 2.0)),
    ("T6", "Sør-Øst",     "Stikkvei",       "#ec4899", "#be185d", [[24.0, 47.8], [30.8, 47.8], [30.8, 51.4], [xe(51.4), 51.4], [L_SE[0], L_SE[1]], [24.0, ys(24.0)]], (1.5, 1.5)),
]
A_road = [[xw(43.8), 43.8], [30.8, 43.8], [30.8, 47.8], [xw(47.8), 47.8]]

# ---------------- ALTERNATIV B: 5 TOMTER + LEKEPLASS (100 % fra Myrteveien) ----------------
B_road = [[28.5, 0.0], [32.5, 0.0], [32.5, 51.0], [36.5, 51.0], [36.5, 57.0], [24.5, 57.0], [24.5, 51.0], [28.5, 51.0]]
B_lek = [[28.0, 57.0], [36.5, 57.0], [36.5, ys(36.5)], [28.0, ys(28.0)]]
B_plots = [
    ("T1", "Nord-Vest",   "Myrteveien",     "#10b981", "#047857", [[0.0, 0.0], [28.5, 0.0], [28.5, 22.5], [xw(22.5), 22.5]], (0, 0)),
    ("T2", "Nord-Øst",    "Myrteveien",     "#06b6d4", "#0e7490", [[32.5, 0.0], [L_NE[0], 0.0], [xe(32.5), 32.5], [32.5, 32.5]], (0, 0)),
    ("T3", "Eksist. hus", "Stikkvei",       "#f59e0b", "#b45309", [[xw(22.5), 22.5], [28.5, 22.5], [28.5, 48.5], [xw(48.5), 48.5]], (-6.0, 5.5)),
    ("T4", "Sør-Øst",     "Stikkvei/tun",   "#3b82f6", "#1d4ed8", [[32.5, 32.5], [xe(32.5), 32.5], [L_SE[0], L_SE[1]], [36.5, ys(36.5)], [36.5, 51.0], [32.5, 51.0]], (1.5, 0)),
    ("T5", "Sør-Vest",    "Stikkvei/tun",   "#8b5cf6", "#6d28d9", [[xw(48.5), 48.5], [28.5, 48.5], [28.5, 51.0], [24.5, 51.0], [24.5, 57.0], [28.0, 57.0], [28.0, ys(28.0)], [L_SW[0], L_SW[1]]], (-1.5, 3.0)),
]

# Eksisterende 1947-hus (uthevet ramme så man tydelig ser at det beholdes)
house_box = [[15.45, 27.34], [26.71, 27.34], [26.71, 39.30], [15.45, 39.30]]


def render_panel_elements(plots, road, panel_idx, lek=None):
    els = []
    # 1. Tomter
    for code, name, acc, fill, stroke, pts, nudge in plots:
        ar = area_m2(pts)
        els.append(f'<polygon points="{poly_canvas_str(pts, panel_idx)}" fill="{fill}" fill-opacity="0.24" stroke="{stroke}" stroke-width="3.2"/>')
        c = centroid_local(pts) + np.array(nudge)
        cp = to_canvas(c, panel_idx)
        bya = ar * 0.25
        # Kompakt og tydelig etikett for hver tomt
        els.append(f'''
        <g transform="translate({cp[0] - 88:.1f}, {cp[1] - 34:.1f})">
          <rect width="176" height="68" rx="8" fill="#ffffff" fill-opacity="0.93" stroke="{stroke}" stroke-width="2.2"/>
          <text x="88" y="21" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="14" fill="{stroke}">{code} — {name}</text>
          <text x="88" y="40" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="15.5" fill="#0f172a">ca. {ar:.0f} m²</text>
          <text x="88" y="57" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.5" fill="#475569">BYA ≤ {bya:.0f} m² • {acc}</text>
        </g>
        ''')

    # 2. Felles vei / snutun
    r_ar = area_m2(road)
    els.append(f'<polygon points="{poly_canvas_str(road, panel_idx)}" fill="#64748b" fill-opacity="0.45" stroke="#1e293b" stroke-width="2.6" stroke-dasharray="6,4"/>')
    rc = to_canvas(centroid_local(road), panel_idx)
    if panel_idx == 0:
        els.append(f'''
        <g transform="translate({rc[0] - 88:.1f}, {rc[1] - 13:.1f})">
          <rect width="176" height="26" rx="5" fill="#0f172a" fill-opacity="0.92"/>
          <text x="88" y="17" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="11.5" fill="#f8fafc">Stikkvei 4 m ({r_ar:.0f} m²)</text>
        </g>
        ''')
    else:
        # Plasser veietikett midt i snutunet
        tun_c = to_canvas(np.array([30.5, 54.0]), panel_idx)
        els.append(f'''
        <g transform="translate({tun_c[0] - 84:.1f}, {tun_c[1] - 14:.1f})">
          <rect width="168" height="28" rx="5" fill="#0f172a" fill-opacity="0.93"/>
          <text x="84" y="18" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="11.5" fill="#f8fafc">Vei + snutun ({r_ar:.0f} m²)</text>
        </g>
        ''')

    # 3. Felles lekeplass (Panel B)
    if lek is not None:
        l_ar = area_m2(lek)
        els.append(f'<polygon points="{poly_canvas_str(lek, panel_idx)}" fill="#84cc16" fill-opacity="0.38" stroke="#3f6212" stroke-width="2.8" stroke-dasharray="5,3"/>')
        lc = to_canvas(centroid_local(lek), panel_idx)
        els.append(f'''
        <g transform="translate({lc[0] - 66:.1f}, {lc[1] - 24:.1f})">
          <rect width="132" height="48" rx="7" fill="#f7fee7" fill-opacity="0.95" stroke="#4d7c0f" stroke-width="2.0"/>
          <text x="66" y="19" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="11.5" fill="#365314">NÆRLEKEPLASS</text>
          <text x="66" y="37" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="13" fill="#3f6212">ca. {l_ar:.0f} m²</text>
        </g>
        ''')

    # 4. Uthev eksisterende 1947-hus som beholdes
    els.append(f'<polygon points="{poly_canvas_str(house_box, panel_idx)}" fill="#f59e0b" fill-opacity="0.32" stroke="#92400e" stroke-width="3.2"/>')
    hc = to_canvas(np.array([21.1, 33.3]), panel_idx)
    els.append(f'''
    <g transform="translate({hc[0] - 58:.1f}, {hc[1] - 13:.1f})">
      <rect width="116" height="26" rx="5" fill="#78350f" fill-opacity="0.94" stroke="#fef3c7" stroke-width="1.4"/>
      <text x="58" y="17" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="11" fill="#ffffff">EKSIST. HUS</text>
    </g>
    ''')
    return "\n".join(els)


ox0 = MARGIN_X
ox1 = MARGIN_X + PW + GAP

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <!-- Bakgrunn for marger -->
  <rect width="{W}" height="{H}" fill="#0f172a"/>

  <!-- Hovedbanner -->
  <text x="{W/2:.1f}" y="42" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="28" fill="#ffffff">MULIGHETSSTUDIE — MAKSIMAL UTPARSELLERING AV MYRTEVEIEN 6 (3 752 m²)</text>
  <text x="{W/2:.1f}" y="74" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="17" fill="#38bdf8">Gnr 140 / Bnr 371 • Tønsberg kommune • Flest mulig fornuftige ~600 m²-tomter mens eksisterende 1947-hus beholdes</text>
  <text x="{W/2:.1f}" y="99" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="13.5" fill="#cbd5e1">Merk: Oppdeling i 3+ nye boligtomter eller felles adkomstvei utløser krav om detaljregulering (KPA Tønsberg 2023–2035, ref. sak #86)</text>

  <!-- Panel A & B rammer (bakgrunnsbilder komposittes under av PIL) -->
  <rect x="{ox0}" y="{HEADER_H}" width="{PW}" height="{PH}" fill="none" stroke="#38bdf8" stroke-width="3"/>
  <rect x="{ox1}" y="{HEADER_H}" width="{PW}" height="{PH}" fill="none" stroke="#10b981" stroke-width="3"/>

  <!-- Panel A innhold -->
  {render_panel_elements(A_plots, A_road, 0, lek=None)}

  <!-- Panel B innhold -->
  {render_panel_elements(B_plots, B_road, 1, lek=B_lek)}

  <!-- Panel A toppkort -->
  <g transform="translate({ox0 + 18}, {HEADER_H + 16})">
    <rect width="650" height="78" rx="10" fill="#0f172a" fill-opacity="0.93" stroke="#38bdf8" stroke-width="2.2"/>
    <text x="18" y="30" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="19" fill="#38bdf8">ALTERNATIV A: 6 TOMTER à ~600 m² (1 eksist. + 5 nye)</text>
    <text x="18" y="53" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="13.5" fill="#ffffff">Snitt 604 m² (586–638 m²) • Kun 112 m² stikkvei • ≥ 4,0 m rundt eksisterende hus</text>
    <text x="18" y="70" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="12" fill="#fbbf24">Forutsetning: Utvidet veirett i privat vei Trollheggveien (141/1) + detaljregulering</text>
  </g>

  <!-- Panel B toppkort -->
  <g transform="translate({ox1 + 18}, {HEADER_H + 16})">
    <rect width="748" height="78" rx="10" fill="#0f172a" fill-opacity="0.93" stroke="#10b981" stroke-width="2.2"/>
    <text x="18" y="30" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="19" fill="#34d399">ALTERNATIV B: 5 TOMTER + LEKEPLASS (100 % fra Myrteveien)</text>
    <text x="18" y="53" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="13.5" fill="#ffffff">Romslige tomter 625–696 m² + 150 m² nærlekeplass + snutun (276 m²)</text>
    <text x="18" y="70" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="12" fill="#a7f3d0">Største fordel: 0 % avhengig av privat veieier i Trollheggveien • Mest reguleringssikker!</text>
  </g>

  <!-- Bunnpanel: Nøkkeltall og planvurdering -->
  <g transform="translate({MARGIN_X}, {HEADER_H + PH + 16})">
    <rect width="{W - MARGIN_X*2}" height="116" rx="10" fill="#1e293b" stroke="#475569" stroke-width="1.8"/>
    <text x="24" y="30" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="16" fill="#ffffff">VIKTIGSTE KONKLUSJONER FOR UTPARSELLERING (DETALJREGULERING, KPA TØNSBERG 2023–2035)</text>
    <text x="24" y="56" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="13.5" fill="#e2e8f0">1. Maks fornuftig antall: 6 eneboligtomter (~585–640 m² med Trollheggveien, eller ~550–610 m² kun fra Myrteveien uten lekeplass). 5 tomter + nærlekeplass (Alt. B) er lettest å få regulert.</text>
    <text x="24" y="80" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="13.5" fill="#e2e8f0">2. Eksisterende 1947-hus beholdes på ~590–680 m² (BYA ca. 21–24 % inkl. 2 p-plasser — under 25 %-grensen). Gammel tre-garasje i NV rives for å frigjøre T1.</text>
    <text x="24" y="104" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="13.5" fill="#93c5fd">3. Reguleringsfordel: Ved detaljregulering kan byggegrense mot Myrteveien settes etter strøkslinje (~8–10 m som Myrteveien 2) i stedet for 15 m fra vegmidt — gir romslige byggefelt på T1 &amp; T2.</text>
  </g>
</svg>
'''

svg_path = os.path.join(assets_dir, "mulighetsstudie_utparsellering_m6.svg")
overlay_png = "/tmp/utparsellering_overlay.png"
png_path = os.path.join(assets_dir, "mulighetsstudie_utparsellering_m6.png")

with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg)

# Render transparent overlay (men uten mørk bakgrunn over panelene — vi lager panel-maske)
res = subprocess.run(
    ["inkscape", svg_path, "-o", overlay_png, "--export-area-page", f"--export-width={W}"],
    capture_output=True, text=True
)
if res.returncode != 0:
    raise RuntimeError(f"Inkscape failed: {res.stderr}")

# Wait: SVG hadde solid <rect fill="#0f172a"/> over hele lerretet -> la oss legge panelbildene FØRST
# og bruke et rent transparent overlay uten solid bakgrunn over panelene!
# Enklest: erstatt topp-rect med 4 marg-rektangler slik at panelvinduene er 100 % transparente!
svg_trans = svg.replace(
    f'<rect width="{W}" height="{H}" fill="#0f172a"/>',
    f'''<rect x="0" y="0" width="{W}" height="{HEADER_H}" fill="#0f172a"/>
  <rect x="0" y="{HEADER_H + PH}" width="{W}" height="{FOOTER_H}" fill="#0f172a"/>
  <rect x="0" y="{HEADER_H}" width="{MARGIN_X}" height="{PH}" fill="#0f172a"/>
  <rect x="{ox0 + PW}" y="{HEADER_H}" width="{GAP}" height="{PH}" fill="#0f172a"/>
  <rect x="{ox1 + PW}" y="{HEADER_H}" width="{MARGIN_X}" height="{PH}" fill="#0f172a"/>'''
)
with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg_trans)

res = subprocess.run(
    ["inkscape", svg_path, "-o", overlay_png, "--export-area-page", f"--export-width={W}"],
    capture_output=True, text=True
)
if res.returncode != 0:
    raise RuntimeError(f"Inkscape failed: {res.stderr}")

base = Image.new("RGBA", (W, H), (15, 23, 42, 255))
base.paste(crop_panel, (ox0, HEADER_H))
base.paste(crop_panel, (ox1, HEADER_H))

ov = Image.open(overlay_png).convert("RGBA")
if ov.size != base.size:
    ov = ov.resize(base.size, Image.Resampling.LANCZOS)
composed = Image.alpha_composite(base, ov).convert("RGB")
composed.save(png_path, format="PNG", optimize=True)
os.remove(overlay_png)
print(f"Saved: {png_path} ({composed.size[0]}x{composed.size[1]})")
