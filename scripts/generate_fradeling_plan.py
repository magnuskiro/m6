"""
Genererer foreløpig situasjonsplan (SVG + PNG) for søknad om tomtefradeling
(ca. 650 m² i nord-øst) på Myrteveien 6, Gnr 140 / Bnr 371, Tønsberg kommune.

Basert på KB Arkitekters situasjonsplan som inkluderer NY GARASJE (2026-04-21,
assets/images/drawings/situasjonsplan-1.jpg, 1:400 i A3, 14,6994 px/m)
og Kartverkets matrikkeldata (nordgrense 51,89 m, østgrense mot 140/1008 42,77 m).
Inkluderer også historisk avløpstrasé fra 1946-kart (septikk/synkekum) og antatt
avløpsretning fra husets NØ-hjørne ned mot naboen (140/1008) for påvisning/VA-kontroll.
"""

import math
import os
import subprocess
import numpy as np
from PIL import Image

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
assets_dir = os.path.join(repo_root, "assets", "images")

# Bruk situasjonsplanen som inkluderer NY GARASJE (9,9 x 5,9 m, ca. 20,74 m fra østgrense)
bg_path = os.path.join(assets_dir, "drawings", "situasjonsplan-1.jpg")
im = Image.open(bg_path).convert("RGBA")

# Beskjær rundt Myrteveien 6, ny garasje og NØ-hjørnet (med god luft til toppbanner og bunn)
CROP_X0, CROP_Y0 = 460, 45
CROP_X1, CROP_Y1 = 1720, 1185
W = CROP_X1 - CROP_X0  # 1260
H = CROP_Y1 - CROP_Y0  # 1140
crop_im = im.crop((CROP_X0, CROP_Y0, CROP_X1, CROP_Y1))

# Kalibrerte referansepunkter på situasjonsplan-1.jpg (verifisert mot 51,89 m nordgrense)
PX_PER_M = 14.6994
NE = np.array([1293.17, 208.93])
NW = np.array([554.70, 399.88])

u_west = (NW - NE) / np.linalg.norm(NW - NE)
u_south = np.array([0.24028, 1.0]) / math.hypot(0.24028, 1.0)

# Foreslått tomt med full 4,0 m lovlig avstand fra NY GARASJE (58,4 m² > 50 m², 20,74 m fra østgrense):
# 16,7 m (bredde langs Myrteveien) x 39,0 m (dybde langs 140/1008) = 651,2 m²
W_M = 16.7
D_M = 39.0
sin_theta = abs(u_west[0] * u_south[1] - u_west[1] * u_south[0])
ACTUAL_AREA = W_M * D_M * sin_theta


def pt(west_m, south_m):
    p = NE + (west_m * PX_PER_M) * u_west + (south_m * PX_PER_M) * u_south
    return np.array([p[0] - CROP_X0, p[1] - CROP_Y0])


def poly_str(pts):
    return " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)


# Geometrier
parcel_pts = [pt(0.0, 0.0), pt(W_M, 0.0), pt(W_M, D_M), pt(0.0, D_M)]
build_pts = [pt(4.0, 11.0), pt(W_M - 4.0, 11.0), pt(W_M - 4.0, D_M - 4.0), pt(4.0, D_M - 4.0)]
road_line_pts = [pt(-1.5, 11.0), pt(W_M + 1.5, 11.0)]
avkjorsel_pts = [pt(11.2, -1.2), pt(15.2, -1.2), pt(15.2, 8.0), pt(11.2, 8.0)]

# Nøkkelpunkter fra KB Arkitekters 2026-04-21 tegning (med ny garasje)
gar_ne = pt(20.74, 10.01)
gar_se = pt(20.74, 19.91)
gar_mid_e = pt(20.74, 15.0)
p_west_at_gar = pt(W_M, 15.0)

m6_ne = pt(24.84, 26.5)
p_west_at_m6 = pt(W_M, 26.5)
overvannskum = pt(23.6, 27.9)

# Historisk avløpstrasé fra 1946-kart (Sem bygn.råd J.nr. 814/1946):
# Fra NØ-hjørnet av dagens hus diagonalt NØ til KLOAKK. SEPTIKK -> SYNKEKUM,
# samt antatt videre selvfallsretning ned skråningen (1:13 øst) mot naboen (140/1008).
sewer_house_ne = pt(24.84, 26.8)
sewer_septik = pt(12.0, 18.0)       # 1946-kart: KLOAKK. SEPTIKK (~12 m NØ for husets NØ-hjørne)
sewer_synkekum = pt(9.8, 10.2)      # 1946-kart: SYNKEKUM (nord for septikk)
sewer_to_neighbor = pt(-2.2, 23.5)  # Antatt selvfallsretning ned mot nabo (Myrteveien 2, 140/1008)


def dim_svg(p1, p2, label, dx=0, dy=0, color="#047857", w_box=74, h_box=22, font_size=11.0):
    mid = (p1 + p2) / 2.0 + np.array([dx, dy])
    return f'''
    <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}"
          stroke="{color}" stroke-width="2.4" marker-start="url(#arrow-{color[1:]})" marker-end="url(#arrow-{color[1:]})"/>
    <rect x="{mid[0] - w_box/2:.1f}" y="{mid[1] - h_box/2:.1f}" width="{w_box}" height="{h_box}"
          rx="5" fill="#ffffff" fill-opacity="0.96" stroke="{color}" stroke-width="1.4"/>
    <text x="{mid[0]:.1f}" y="{mid[1] + 4:.1f}" text-anchor="middle"
          font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="{font_size}" fill="{color}">{label}</text>
    '''


center_parcel = pt(W_M / 2.0, 28.5)
avk_target = pt(13.2, 2.5)
road_target = pt(2.2, 11.0)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
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
    <marker id="arrow-9333ea" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#9333ea"/>
    </marker>
  </defs>

  <!-- 1. Foreslått ny parsell (16,7 x 39,0 m = ca. 651 m²) -->
  <polygon points="{poly_str(parcel_pts)}" fill="#10b981" fill-opacity="0.22" stroke="#047857" stroke-width="2.4"/>

  <!-- 2. Dispensasjonsfritt byggefelt (8,7 x 24,0 m = 209 m²) -->
  <polygon points="{poly_str(build_pts)}" fill="#3b82f6" fill-opacity="0.16" stroke="#1d4ed8" stroke-width="2.0" stroke-dasharray="5,4"/>
  <polygon points="{poly_str(build_pts)}" fill="url(#dots-build)" stroke="none"/>

  <!-- 3. Foreslått ny avkjørsel -->
  <polygon points="{poly_str(avkjorsel_pts)}" fill="#f59e0b" fill-opacity="0.50" stroke="#b45309" stroke-width="2.2"/>

  <!-- 4. 15 m byggegrense fra vegmidt Myrteveien -->
  <line x1="{road_line_pts[0][0]:.1f}" y1="{road_line_pts[0][1]:.1f}"
        x2="{road_line_pts[1][0]:.1f}" y2="{road_line_pts[1][1]:.1f}"
        stroke="#d97706" stroke-width="2.8" stroke-dasharray="10,4,2,4"/>

  <!-- 5. Prosjekterte nye eiendomsgrenser (vest- og sørgrense) -->
  <polyline points="{parcel_pts[1][0]:.1f},{parcel_pts[1][1]:.1f} {parcel_pts[2][0]:.1f},{parcel_pts[2][1]:.1f} {parcel_pts[3][0]:.1f},{parcel_pts[3][1]:.1f}"
            fill="none" stroke="#dc2626" stroke-width="4.0" stroke-dasharray="10,5"/>

  <!-- Grensepunkter ny parsell -->
  {"".join(f'<circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="5.5" fill="#dc2626" stroke="#ffffff" stroke-width="2"/>' for p in parcel_pts)}

  <!-- 6. Historisk avløpstrasé (1946-kart: septikk & synkekum) + antatt trasé ned mot nabo (140/1008) -->
  <polyline points="{sewer_house_ne[0]:.1f},{sewer_house_ne[1]:.1f} {sewer_septik[0]:.1f},{sewer_septik[1]:.1f} {sewer_synkekum[0]:.1f},{sewer_synkekum[1]:.1f}"
            fill="none" stroke="#9333ea" stroke-width="3.6" stroke-dasharray="7,4"/>
  <line x1="{sewer_house_ne[0]:.1f}" y1="{sewer_house_ne[1]:.1f}"
        x2="{sewer_to_neighbor[0]:.1f}" y2="{sewer_to_neighbor[1]:.1f}"
        stroke="#9333ea" stroke-width="3.2" stroke-dasharray="3,5" marker-end="url(#arrow-9333ea)"/>

  <!-- Symboler for 1946 septikk & synkekum + utløp ved husets NØ-hjørne -->
  <circle cx="{sewer_house_ne[0]:.1f}" cy="{sewer_house_ne[1]:.1f}" r="6.5" fill="#7e22ce" stroke="#ffffff" stroke-width="2"/>
  <rect x="{sewer_septik[0] - 8:.1f}" y="{sewer_septik[1] - 6:.1f}" width="16" height="12" rx="2"
        fill="#a855f7" stroke="#581c87" stroke-width="2"/>
  <circle cx="{sewer_synkekum[0]:.1f}" cy="{sewer_synkekum[1]:.1f}" r="6" fill="#c084fc" stroke="#581c87" stroke-width="2"/>

  <!-- Overvannskum M6 -->
  <circle cx="{overvannskum[0]:.1f}" cy="{overvannskum[1]:.1f}" r="5.5" fill="#0284c7" stroke="#ffffff" stroke-width="1.8"/>

  <!-- Mållinjer -->
  {dim_svg(pt(0.0, -2.0), pt(W_M, -2.0), "16,7 m", dx=-4, dy=-17, color="#047857", w_box=64, h_box=22, font_size=12)}
  {dim_svg(pt(-2.0, 0.0), pt(-2.0, D_M), "39,0 m", dx=38, dy=0, color="#047857", w_box=64, h_box=22, font_size=12)}
  {dim_svg(gar_mid_e, p_west_at_gar, "4,04 m (≥ 4,0 m)", dx=0, dy=-22, color="#dc2626", w_box=112, h_box=21, font_size=10.2)}
  {dim_svg(m6_ne, p_west_at_m6, "8,1 m til bolig", dx=-4, dy=-22, color="#1d4ed8", w_box=96, h_box=21, font_size=10.2)}

  <!-- Kort: Ny parsell -->
  <g transform="translate({center_parcel[0] - 108:.1f}, {center_parcel[1] - 54:.1f})">
    <rect width="216" height="108" rx="8" fill="#ecfdf5" fill-opacity="0.96" stroke="#059669" stroke-width="2.2"/>
    <text x="108" y="21" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="11.5" fill="#064e3b">NY PARSELL (NORD-ØST)</text>
    <text x="108" y="40" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="13" fill="#047857">ca. {ACTUAL_AREA:.0f} m² (16,7 × 39,0 m)</text>
    <line x1="14" y1="49" x2="202" y2="49" stroke="#a7f3d0" stroke-width="1.2"/>
    <text x="108" y="66" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#065f46">Byggefelt: 8,7 × 24,0 m (209 m²)</text>
    <text x="108" y="82" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#065f46">Maks 25 % BYA = 162,8 m²</text>
    <text x="108" y="98" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#065f46">Full 4,0 m avstand til Ny garasje</text>
  </g>

  <!-- Kort: Gjenværende M6 -->
  <g transform="translate(345, 868)">
    <rect width="316" height="72" rx="8" fill="#f8fafc" fill-opacity="0.96" stroke="#334155" stroke-width="1.8"/>
    <text x="158" y="20" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="11.5" fill="#0f172a">GJENVÆRENDE HOVEDTOMT (M6)</text>
    <text x="158" y="38" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="11.5" fill="#334155">Gnr 140 / Bnr 371 • ca. 3 101 m²</text>
    <text x="158" y="56" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.8" fill="#475569">Inkl. Ny garasje (58,4 m²) • BYA &lt; 10 % • MUA &gt; 2 500 m²</text>
  </g>

  <!-- Callout: Ny avkjørsel -->
  <line x1="472" y1="152" x2="{avk_target[0]:.1f}" y2="{avk_target[1]:.1f}" stroke="#b45309" stroke-width="2.2" marker-end="url(#arrow-b45309)"/>
  <g transform="translate(242, 118)">
    <rect width="232" height="58" rx="6" fill="#fef3c7" fill-opacity="0.97" stroke="#d97706" stroke-width="1.6"/>
    <text x="10" y="18" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.5" fill="#78350f">NY AVKJØRSEL (MYRTEVEIEN)</text>
    <text x="10" y="34" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#92400e">Direkte til kommunal vei (141/288)</text>
    <text x="10" y="48" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#92400e">God klaring øst for Ny garasje / M6</text>
  </g>

  <!-- Callout: 15 m byggegrense -->
  <line x1="980" y1="274" x2="{road_target[0]:.1f}" y2="{road_target[1]:.1f}" stroke="#b45309" stroke-width="2.2" marker-end="url(#arrow-b45309)"/>
  <g transform="translate(980, 240)">
    <rect width="258" height="58" rx="6" fill="#fffbeb" fill-opacity="0.97" stroke="#d97706" stroke-width="1.6"/>
    <text x="10" y="18" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.5" fill="#92400e">15 m BYGGEGRENSE FRA VEGMIDT</text>
    <text x="10" y="34" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#78350f">Tilsv. ~11 m fra nordre tomtegrense</text>
    <text x="10" y="48" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#78350f">(NB: Myrteveien 2 ligger nærmere vei)</text>
  </g>

  <!-- Callout: 1946 Avløpsrør / Septikk / Selvfall mot naboen -->
  <line x1="980" y1="535" x2="{sewer_to_neighbor[0] + 6:.1f}" y2="{sewer_to_neighbor[1] + 2:.1f}" stroke="#9333ea" stroke-width="2.2" marker-end="url(#arrow-9333ea)"/>
  <g transform="translate(980, 488)">
    <rect width="260" height="86" rx="6" fill="#faf5ff" fill-opacity="0.97" stroke="#9333ea" stroke-width="1.8"/>
    <text x="10" y="18" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.2" fill="#581c87">AVLØPSRØR FRA NØ-HJØRNE (OBS!)</text>
    <text x="10" y="34" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.3" fill="#6b21a8">• 1946-kart: Kloakk → Septikk → Synkekum i NØ</text>
    <text x="10" y="49" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.3" fill="#6b21a8">• Terrengfall 1:13 øst ned mot nabo (140/1008)</text>
    <text x="10" y="64" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.2" fill="#7e22ce">• MÅ bekreftes med VA-kart / påvisning</text>
    <text x="10" y="78" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.2" fill="#7e22ce">• Krever ledningsrett eller omlegging v/deling</text>
  </g>

  <!-- Callout: Ny garasje-merknad -->
  <line x1="398" y1="435" x2="{gar_ne[0] - 88:.1f}" y2="{gar_ne[1] + 55:.1f}" stroke="#334155" stroke-width="1.8"/>
  <g transform="translate(150, 408)">
    <rect width="250" height="58" rx="6" fill="#f1f5f9" fill-opacity="0.97" stroke="#475569" stroke-width="1.5"/>
    <text x="10" y="18" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.2" fill="#0f172a">NY GARASJE M6 (9,9 × 5,9 m = 58,4 m²)</text>
    <text x="10" y="34" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.3" fill="#334155">&gt; 50 m² ⇒ krever min. 4,0 m til ny grense</text>
    <text x="10" y="48" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.3" fill="#334155">(Alt.: flytt vestover / ≤ 50 m² ⇒ bredere tomt)</text>
  </g>

  <!-- Toppbanner -->
  <g transform="translate(20, 14)">
    <rect width="1220" height="72" rx="8" fill="#0f172a" fill-opacity="0.95" stroke="#334155" stroke-width="1.8"/>
    <text x="610" y="24" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="15.5" fill="#ffffff">FORELØPIG SITUASJONSPLAN — TOMTEFRADELING NORD-ØST (ca. 650 m², INKL. NY GARASJE)</text>
    <text x="610" y="44" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.5" fill="#38bdf8">Myrteveien 6 (Gnr 140 / Bnr 371, 3 752 m²) • Tønsberg kommune • Tiltakshaver: Magnus Kirø</text>
    <text x="610" y="61" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.2" fill="#cbd5e1">Delingstillatelse nå (PBL § 20-1 m) — Oppmålingsforretning ved byggesøknad / byggetillatelse (innen 3 år, PBL § 21-9)</text>
  </g>

  <!-- Tegnforklaring (Nederst til venstre) -->
  <g transform="translate(20, 946)">
    <rect width="490" height="176" rx="8" fill="#ffffff" fill-opacity="0.97" stroke="#0f172a" stroke-width="1.8"/>
    <text x="14" y="22" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="11.5" fill="#0f172a">TEGNFORKLARING</text>

    <rect x="14" y="34" width="24" height="14" fill="#10b981" fill-opacity="0.26" stroke="#047857" stroke-width="2"/>
    <text x="48" y="45" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#1e293b">Foreslått fradelt boligtomt (ca. 651 m² — 16,7 × 39,0 m)</text>

    <line x1="14" y1="64" x2="38" y2="64" stroke="#dc2626" stroke-width="3.5" stroke-dasharray="6,3"/>
    <text x="48" y="68" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#1e293b">Ny prosjektert eiendomsgrense (4,04 m fra Ny garasje)</text>

    <rect x="14" y="80" width="24" height="14" fill="#3b82f6" fill-opacity="0.20" stroke="#1d4ed8" stroke-width="1.8" stroke-dasharray="4,3"/>
    <text x="48" y="91" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#1e293b">Dispensasjonsfritt byggefelt (8,7 × 24,0 m = 209 m²)</text>

    <line x1="14" y1="110" x2="38" y2="110" stroke="#d97706" stroke-width="2.5" stroke-dasharray="8,3,2,3"/>
    <text x="48" y="114" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#1e293b">15 m byggegrense fra vegmidt Myrteveien (~11 m fra grense)</text>

    <rect x="14" y="126" width="24" height="14" fill="#f59e0b" fill-opacity="0.50" stroke="#b45309" stroke-width="1.8"/>
    <text x="48" y="137" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#1e293b">Foreslått ny avkjørsel fra Myrteveien (kommunal vei)</text>

    <line x1="14" y1="156" x2="38" y2="156" stroke="#9333ea" stroke-width="3.4" stroke-dasharray="5,3"/>
    <text x="48" y="160" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.2" fill="#581c87">Avløpstrasé: 1946 septikk/synkekum + antatt føring mot nabo (OBS)</text>
  </g>

  <!-- Stempel (Nederst til høyre) -->
  <g transform="translate(836, 1076)">
    <rect width="404" height="46" rx="6" fill="#fef2f2" fill-opacity="0.97" stroke="#dc2626" stroke-width="1.6"/>
    <text x="202" y="19" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.2" fill="#991b1b">FORELØPIG ARBEIDSSKISSE — FOR AVKLARING FØR INNSENDING</text>
    <text x="202" y="35" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.4" fill="#7f1d1d">Grunnlag: KB Arkitekter 1:400 m/Ny garasje (2026-04-21) &amp; 1946-kart</text>
  </g>
</svg>
'''

svg_path = os.path.join(assets_dir, "situasjonsplan_fradeling_no.svg")
overlay_png = "/tmp/fradeling_overlay.png"
png_path = os.path.join(assets_dir, "situasjonsplan_fradeling_no.png")

with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg)

res = subprocess.run(
    ["inkscape", svg_path, "-o", overlay_png, "--export-area-page", f"--export-width={W * 2}"],
    capture_output=True, text=True
)
if res.returncode != 0:
    raise RuntimeError(f"Inkscape failed: {res.stderr}")

bg_up = crop_im.resize((W * 2, H * 2), Image.Resampling.LANCZOS)
ov_im = Image.open(overlay_png).convert("RGBA")
if ov_im.size != bg_up.size:
    ov_im = ov_im.resize(bg_up.size, Image.Resampling.LANCZOS)
composed = Image.alpha_composite(bg_up, ov_im).convert("RGB")
composed.save(png_path, format="PNG", optimize=True)
os.remove(overlay_png)
print(f"Saved composed PNG: {png_path} ({composed.size[0]}x{composed.size[1]}, parcel area = {ACTUAL_AREA:.1f} m2)")
