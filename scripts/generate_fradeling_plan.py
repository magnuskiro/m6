"""
Genererer foreløpig situasjonsplan (SVG + PNG) for søknad om tomtefradeling
(ca. 650 m² i nord-øst) på Myrteveien 6, Gnr 140 / Bnr 371, Tønsberg kommune.

Kalibrert mot KB Arkitekters offisielle situasjonsplan (1:400 i A3, 14,792 px/m)
og Kartverkets matrikkeldata (nordgrense 51,89 m, østgrense mot 140/1008 42,77 m).
"""

import os
import subprocess
import numpy as np
from PIL import Image

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
assets_dir = os.path.join(repo_root, "assets", "images")

# Beskjær bakgrunnsbilde rundt Myrteveien 6 og NØ-hjørnet (med god luft over Myrteveien til toppbanner)
CROP_X0, CROP_Y0 = 460, 50
CROP_X1, CROP_Y1 = 1680, 1160
W = CROP_X1 - CROP_X0  # 1220
H = CROP_Y1 - CROP_Y0  # 1110

im = Image.open(os.path.join(assets_dir, "situasjonsplan_render.png")).convert("RGBA")
crop_im = im.crop((CROP_X0, CROP_Y0, CROP_X1, CROP_Y1))

# Kalibrerte referansepunkter i originalbildets koordinater (px)
PX_PER_M = 14.792
NE = np.array([1292.64, 207.18])
NW = np.array([548.50, 395.50])

u_west = (NW - NE) / np.linalg.norm(NW - NE)
east_dir = np.array([0.2508, 1.0])
u_south = east_dir / np.linalg.norm(east_dir)

W_M = 20.0
D_M = 32.5
sin_theta = abs(u_west[0] * u_south[1] - u_west[1] * u_south[0])
ACTUAL_AREA = W_M * D_M * sin_theta


def pt(west_m, south_m):
    p = NE + (west_m * PX_PER_M) * u_west + (south_m * PX_PER_M) * u_south
    return np.array([p[0] - CROP_X0, p[1] - CROP_Y0])


def orig(x, y):
    return np.array([x - CROP_X0, y - CROP_Y0])


def poly_str(pts):
    return " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)


# Geometrier i beskåret koordinatsystem
parcel_pts = [pt(0.0, 0.0), pt(W_M, 0.0), pt(W_M, D_M), pt(0.0, D_M)]
build_pts = [pt(4.0, 11.0), pt(W_M - 4.0, 11.0), pt(W_M - 4.0, D_M - 4.0), pt(4.0, D_M - 4.0)]
road_line_pts = [pt(-1.5, 11.0), pt(W_M + 1.5, 11.0)]
avkjorsel_pts = [pt(14.0, -1.2), pt(18.0, -1.2), pt(18.0, 8.0), pt(14.0, 8.0)]
m6_driveway_pts = [orig(885, 700), orig(795, 333), orig(892, 310), orig(1035, 675)]

lyktestolpe = orig(892, 310)
overvannskum = orig(1055, 692)
m6_ne = orig(1035, 675)
p_west_at_m6 = pt(W_M, 26.45)


def dim_svg(p1, p2, label, dx=0, dy=0, color="#047857", w_box=68, h_box=22, font_size=11.5):
    mid = (p1 + p2) / 2.0 + np.array([dx, dy])
    return f'''
    <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}"
          stroke="{color}" stroke-width="2.4" marker-start="url(#arrow-{color[1:]})" marker-end="url(#arrow-{color[1:]})"/>
    <rect x="{mid[0] - w_box/2:.1f}" y="{mid[1] - h_box/2:.1f}" width="{w_box}" height="{h_box}"
          rx="5" fill="#ffffff" fill-opacity="0.96" stroke="{color}" stroke-width="1.4"/>
    <text x="{mid[0]:.1f}" y="{mid[1] + 4:.1f}" text-anchor="middle"
          font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="{font_size}" fill="{color}">{label}</text>
    '''


center_parcel = pt(W_M / 2.0, D_M / 2.0 + 3.2)
avk_target = pt(16.0, 2.5)
road_target = pt(2.5, 11.0)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <pattern id="hatch-drive" width="10" height="10" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="0" y2="10" stroke="#475569" stroke-width="1.8" opacity="0.5"/>
    </pattern>
    <pattern id="dots-build" width="8" height="8" patternUnits="userSpaceOnUse">
      <circle cx="4" cy="4" r="1.2" fill="#1d4ed8" opacity="0.45"/>
    </pattern>
    <marker id="arrow-047857" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#047857"/>
    </marker>
    <marker id="arrow-dc2626" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#dc2626"/>
    </marker>
    <marker id="arrow-1d4ed8" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#1d4ed8"/>
    </marker>
    <marker id="arrow-b45309" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#b45309"/>
    </marker>
    <marker id="arrow-0284c7" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#0284c7"/>
    </marker>
  </defs>

  <!-- 1. Planlagt innkjøring M6 (#92) -->
  <polygon points="{poly_str(m6_driveway_pts)}" fill="#94a3b8" fill-opacity="0.28" stroke="#475569" stroke-width="1.8" stroke-dasharray="6,4"/>
  <polygon points="{poly_str(m6_driveway_pts)}" fill="url(#hatch-drive)" stroke="none"/>

  <!-- 2. Foreslått ny parsell (~650 m²) -->
  <polygon points="{poly_str(parcel_pts)}" fill="#10b981" fill-opacity="0.24" stroke="#047857" stroke-width="2.5"/>

  <!-- 3. Dispensasjonsfritt byggefelt (12,0 x 17,5 m = 210 m²) -->
  <polygon points="{poly_str(build_pts)}" fill="#3b82f6" fill-opacity="0.18" stroke="#1d4ed8" stroke-width="2.0" stroke-dasharray="5,4"/>
  <polygon points="{poly_str(build_pts)}" fill="url(#dots-build)" stroke="none"/>

  <!-- 4. Foreslått ny avkjørsel -->
  <polygon points="{poly_str(avkjorsel_pts)}" fill="#f59e0b" fill-opacity="0.50" stroke="#b45309" stroke-width="2.2"/>

  <!-- 5. 15 m byggegrense fra vegmidt Myrteveien -->
  <line x1="{road_line_pts[0][0]:.1f}" y1="{road_line_pts[0][1]:.1f}"
        x2="{road_line_pts[1][0]:.1f}" y2="{road_line_pts[1][1]:.1f}"
        stroke="#d97706" stroke-width="2.8" stroke-dasharray="10,4,2,4"/>

  <!-- 6. Prosjekterte nye eiendomsgrenser (vest- og sørgrense) -->
  <polyline points="{parcel_pts[1][0]:.1f},{parcel_pts[1][1]:.1f} {parcel_pts[2][0]:.1f},{parcel_pts[2][1]:.1f} {parcel_pts[3][0]:.1f},{parcel_pts[3][1]:.1f}"
            fill="none" stroke="#dc2626" stroke-width="4.0" stroke-dasharray="10,5"/>

  <!-- Grensepunkter ny parsell -->
  {"".join(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="5.5" fill="#dc2626" stroke="#ffffff" stroke-width="2"/>' for p in parcel_pts)}

  <!-- Lyktestolpe og overvannskum M6 -->
  <circle cx="{lyktestolpe[0]:.1f}" cy="{lyktestolpe[1]:.1f}" r="7" fill="#2563eb" stroke="#ffffff" stroke-width="2"/>
  <circle cx="{overvannskum[0]:.1f}" cy="{overvannskum[1]:.1f}" r="6.5" fill="#0284c7" stroke="#ffffff" stroke-width="2"/>

  <!-- Mållinjer -->
  {dim_svg(pt(0.0, -2.0), pt(W_M, -2.0), "20,0 m", dx=-6, dy=-17, color="#047857", w_box=64, h_box=22, font_size=12)}
  {dim_svg(pt(-2.0, 0.0), pt(-2.0, D_M), "32,5 m", dx=38, dy=0, color="#047857", w_box=64, h_box=22, font_size=12)}
  {dim_svg(m6_ne, p_west_at_m6, "4,6 m (> 4,0 m)", dx=-4, dy=-22, color="#dc2626", w_box=102, h_box=22, font_size=10.5)}
  {dim_svg(lyktestolpe, pt(W_M, 0.0), "~8,0 m til lyktestolpe", dx=-12, dy=-26, color="#1d4ed8", w_box=132, h_box=21, font_size=10)}

  <!-- Kort: Ny parsell -->
  <g transform="translate({center_parcel[0] - 114:.1f}, {center_parcel[1] - 54:.1f})">
    <rect width="228" height="108" rx="8" fill="#ecfdf5" fill-opacity="0.96" stroke="#059669" stroke-width="2.2"/>
    <text x="114" y="21" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="12" fill="#064e3b">NY PARSELL (NORD-ØST)</text>
    <text x="114" y="40" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="13.5" fill="#047857">ca. {ACTUAL_AREA:.0f} m² (20,0 × 32,5 m)</text>
    <line x1="16" y1="49" x2="212" y2="49" stroke="#a7f3d0" stroke-width="1.2"/>
    <text x="114" y="66" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.5" fill="#065f46">Byggefelt: 12,0 × 17,5 m (210 m²)</text>
    <text x="114" y="82" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.5" fill="#065f46">Maks 25 % BYA = 162,5 m²</text>
    <text x="114" y="98" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.5" fill="#065f46">MUA ≥ 150 m² (god margin)</text>
  </g>

  <!-- Kort: Gjenværende M6 -->
  <g transform="translate(345, 818)">
    <rect width="286" height="72" rx="8" fill="#f8fafc" fill-opacity="0.96" stroke="#334155" stroke-width="1.8"/>
    <text x="143" y="20" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="11.5" fill="#0f172a">GJENVÆRENDE HOVEDTOMT (M6)</text>
    <text x="143" y="38" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="11.5" fill="#334155">Gnr 140 / Bnr 371 • ca. 3 102 m²</text>
    <text x="143" y="56" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10" fill="#475569">BYA &lt; 10 % • MUA &gt; 2 500 m² • Beholder innkjøring</text>
  </g>

  <!-- Callout: Ny avkjørsel (god klaring fra ~8,0 m label) -->
  <line x1="382" y1="145" x2="{avk_target[0]:.1f}" y2="{avk_target[1]:.1f}" stroke="#b45309" stroke-width="2.2" marker-end="url(#arrow-b45309)"/>
  <g transform="translate(155, 114)">
    <rect width="230" height="58" rx="6" fill="#fef3c7" fill-opacity="0.97" stroke="#d97706" stroke-width="1.6"/>
    <text x="10" y="18" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.5" fill="#78350f">NY AVKJØRSEL (MYRTEVEIEN)</text>
    <text x="10" y="34" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#92400e">Direkte til kommunal vei (141/288)</text>
    <text x="10" y="48" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#92400e">God klaring øst for lyktestolpe / M6</text>
  </g>

  <!-- Callout: 15 m byggegrense -->
  <line x1="955" y1="274" x2="{road_target[0]:.1f}" y2="{road_target[1]:.1f}" stroke="#b45309" stroke-width="2.2" marker-end="url(#arrow-b45309)"/>
  <g transform="translate(955, 244)">
    <rect width="244" height="58" rx="6" fill="#fffbeb" fill-opacity="0.97" stroke="#d97706" stroke-width="1.6"/>
    <text x="10" y="18" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.5" fill="#92400e">15 m BYGGEGRENSE FRA VEGMIDT</text>
    <text x="10" y="34" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#78350f">Tilsv. ~11 m fra nordre tomtegrense</text>
    <text x="10" y="48" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#78350f">(NB: Myrteveien 2 ligger nærmere vei)</text>
  </g>

  <!-- Callout: Overvannskum M6 -->
  <line x1="472" y1="712" x2="{overvannskum[0] - 8:.1f}" y2="{overvannskum[1] + 4:.1f}" stroke="#0284c7" stroke-width="2.2" marker-end="url(#arrow-0284c7)"/>
  <g transform="translate(248, 690)">
    <rect width="226" height="44" rx="6" fill="#e0f2fe" fill-opacity="0.97" stroke="#0284c7" stroke-width="1.5"/>
    <text x="10" y="18" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10" fill="#0c4a6e">OVERVANNSKUM M6 (#92)</text>
    <text x="10" y="34" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#075985">Blir liggende på M6 (~3,6 m fra grense)</text>
  </g>

  <!-- Toppbanner -->
  <g transform="translate(20, 14)">
    <rect width="1180" height="72" rx="8" fill="#0f172a" fill-opacity="0.95" stroke="#334155" stroke-width="1.8"/>
    <text x="590" y="24" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="15.5" fill="#ffffff">FORELØPIG SITUASJONSPLAN — TOMTEFRADELING NORD-ØST (ca. 650 m²)</text>
    <text x="590" y="44" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.5" fill="#38bdf8">Myrteveien 6 (Gnr 140 / Bnr 371, 3 752 m²) • Tønsberg kommune • Tiltakshaver: Magnus Kirø</text>
    <text x="590" y="61" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.2" fill="#cbd5e1">Strategi: Delingstillatelse nå (PBL § 20-1 m) — Oppmålingsforretning rekvireres ved byggesøknad / byggetillatelse (innen 3 år, PBL § 21-9)</text>
  </g>

  <!-- Tegnforklaring (Nederst til venstre) -->
  <g transform="translate(20, 918)">
    <rect width="474" height="172" rx="8" fill="#ffffff" fill-opacity="0.97" stroke="#0f172a" stroke-width="1.8"/>
    <text x="14" y="22" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="11.5" fill="#0f172a">TEGNFORKLARING</text>

    <rect x="14" y="34" width="24" height="14" fill="#10b981" fill-opacity="0.28" stroke="#047857" stroke-width="2"/>
    <text x="48" y="45" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#1e293b">Foreslått fradelt boligtomt (ca. 650 m² — 20,0 × 32,5 m)</text>

    <line x1="14" y1="64" x2="38" y2="64" stroke="#dc2626" stroke-width="3.5" stroke-dasharray="6,3"/>
    <text x="48" y="68" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#1e293b">Ny prosjektert eiendomsgrense (2 rette grenselinjer)</text>

    <rect x="14" y="80" width="24" height="14" fill="#3b82f6" fill-opacity="0.22" stroke="#1d4ed8" stroke-width="1.8" stroke-dasharray="4,3"/>
    <text x="48" y="91" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#1e293b">Dispensasjonsfritt byggefelt (12,0 × 17,5 m = 210 m²)</text>

    <line x1="14" y1="110" x2="38" y2="110" stroke="#d97706" stroke-width="2.5" stroke-dasharray="8,3,2,3"/>
    <text x="48" y="114" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#1e293b">15 m byggegrense fra vegmidt Myrteveien (~11 m fra grense)</text>

    <rect x="14" y="126" width="24" height="14" fill="#f59e0b" fill-opacity="0.50" stroke="#b45309" stroke-width="1.8"/>
    <text x="48" y="137" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#1e293b">Foreslått ny avkjørsel fra Myrteveien (kommunal vei)</text>

    <rect x="14" y="148" width="24" height="14" fill="#94a3b8" fill-opacity="0.35" stroke="#475569" stroke-width="1.6" stroke-dasharray="4,3"/>
    <text x="48" y="159" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#1e293b">Planlagt innkjøring M6 (#92 — vest for lyktestolpe)</text>
  </g>

  <!-- Stempel (Nederst til høyre) -->
  <g transform="translate(812, 1044)">
    <rect width="388" height="46" rx="6" fill="#fef2f2" fill-opacity="0.97" stroke="#dc2626" stroke-width="1.6"/>
    <text x="194" y="19" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.2" fill="#991b1b">FORELØPIG ARBEIDSSKISSE — FOR AVKLARING FØR INNSENDING</text>
    <text x="194" y="35" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#7f1d1d">Kartgrunnlag: KB Arkitekter 1:400 (27.04.2026) &amp; Kartverket Matrikkel</text>
  </g>
</svg>
'''

svg_path = os.path.join(assets_dir, "situasjonsplan_fradeling_no.svg")
overlay_png = "/tmp/fradeling_overlay.png"
png_path = os.path.join(assets_dir, "situasjonsplan_fradeling_no.png")

with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg)

# Render transparent vector overlay at 2x resolution via Inkscape
res = subprocess.run(
    ["inkscape", svg_path, "-o", overlay_png, "--export-area-page", f"--export-width={W * 2}"],
    capture_output=True, text=True
)
if res.returncode != 0:
    raise RuntimeError(f"Inkscape failed: {res.stderr}")

# Composite vector overlay cleanly onto upscaled situasjonsplan background
bg_up = crop_im.resize((W * 2, H * 2), Image.Resampling.LANCZOS)
ov_im = Image.open(overlay_png).convert("RGBA")
if ov_im.size != bg_up.size:
    ov_im = ov_im.resize(bg_up.size, Image.Resampling.LANCZOS)
composed = Image.alpha_composite(bg_up, ov_im).convert("RGB")
composed.save(png_path, format="PNG", optimize=True)
os.remove(overlay_png)
print(f"Saved composed PNG: {png_path} ({composed.size[0]}x{composed.size[1]}, parcel area = {ACTUAL_AREA:.1f} m2)")
