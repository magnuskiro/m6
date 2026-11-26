"""
Genererer foreløpig situasjonsplan (SVG + PNG) for søknad om tomtefradeling
i nord-øst på Myrteveien 6, Gnr 140 / Bnr 371, Tønsberg kommune.

Basert på KB Arkitekters situasjonsplan som inkluderer NY GARASJE (2026-04-21,
assets/images/drawings/situasjonsplan-1.jpg, 1:400 i A3, 14,6994 px/m)
og Kartverkets matrikkeldata (nordgrense 51,89 m, østgrense mot 140/1008 42,77 m).

Alle informasjonskort og merkelapper er plassert i dedikerte venstre- og høyremarger
utenfor tiltakseiendommen (140/371) og den fradelte parsellen slik at hele
tomte- og bygningsområdet fremstår helt rent og udekket.
"""

import math
import os
import subprocess
import numpy as np
from PIL import Image

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
assets_dir = os.path.join(repo_root, "assets", "images")

bg_path = os.path.join(assets_dir, "drawings", "situasjonsplan-1.jpg")
im = Image.open(bg_path).convert("RGBA")

# Bredt utsnitt (1620 x 1160) slik at alle merkelapper får rene marger på venstre og høyre side
CROP_X0, CROP_Y0 = 280, 45
CROP_X1, CROP_Y1 = 1900, 1205
W = CROP_X1 - CROP_X0  # 1620
H = CROP_Y1 - CROP_Y0  # 1160
crop_im = im.crop((CROP_X0, CROP_Y0, CROP_X1, CROP_Y1))

# Kalibrerte referansepunkter i originalbildet (px)
PX_PER_M = 14.6994
NE_ORIG = np.array([1293.17, 208.93])
NW_ORIG = np.array([554.70, 399.88])
# Eksisterende tomtemarkør mellom 140/1008 (Myrteveien 2) og 140/995 (Øvre Bogenvei 31)
SE_MARKER_ORIG = np.array([1440.56, 822.33])

u_west = (NW_ORIG - NE_ORIG) / np.linalg.norm(NW_ORIG - NE_ORIG)
u_east_edge = (SE_MARKER_ORIG - NE_ORIG) / np.linalg.norm(SE_MARKER_ORIG - NE_ORIG)

# Eksakt bygningsakse (parallell med både eksisterende Enebolig og planlagt Ny garasje)
C_BLDG = 0.3227
u_par = np.array([C_BLDG, 1.0]) / math.hypot(C_BLDG, 1.0)
n_east = np.array([u_par[1], -u_par[0]])  # normal vinkelrett østover fra hus/garasje

# Referansepunkter på østvegg til Ny garasje og Enebolig (originalbilde)
p_gar_wall = np.array([0.32277 * 500.0 + 898.15, 500.0])
p_gar_ne = np.array([0.32277 * 432.0 + 898.15, 432.0])
p_house_wall = np.array([0.32254 * 800.0 + 808.28, 800.0])

# Plasser ny vestgrense eksakt 4,05 m (vinkelrett) øst for Ny garasje (58,4 m² > 50 m²)
SETBACK_GAR_M = 4.05
L_WEST_M = 34.0  # SV-hjørne flyttet nordover (~8,7 m nord for SØ-markøren)

p_w0 = p_gar_wall + (SETBACK_GAR_M * PX_PER_M) * n_east
A_mat = np.column_stack([u_par, -u_west])
t_nw, s_nw = np.linalg.solve(A_mat, NE_ORIG - p_w0)
NW_NEW_ORIG = p_w0 + t_nw * u_par
SW_NEW_ORIG = NW_NEW_ORIG + (L_WEST_M * PX_PER_M) * u_par


def to_crop(p):
    return np.array([p[0] - CROP_X0, p[1] - CROP_Y0])


def pt_ne(west_m, south_m):
    p = NE_ORIG + (west_m * PX_PER_M) * u_west + (south_m * PX_PER_M) * u_east_edge
    return to_crop(p)


def poly_str(pts):
    return " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)


def nf(val, dec=1):
    return f"{val:.{dec}f}".replace(".", ",")


def inset_quad(pts, insets_m):
    """Beregner dispensasjonsfritt byggefelt ved å forskyve hver av de 4 grensene innover."""
    sa = sum(pts[i][0] * pts[(i + 1) % 4][1] - pts[(i + 1) % 4][0] * pts[i][1] for i in range(4))
    sign = 1.0 if sa > 0 else -1.0
    lines = []
    for i in range(4):
        p1, p2 = pts[i], pts[(i + 1) % 4]
        d = p2 - p1
        d = d / np.linalg.norm(d)
        n_in = sign * np.array([-d[1], d[0]])
        q = p1 + insets_m[i] * PX_PER_M * n_in
        lines.append((q, d))
    out = []
    for i in range(4):
        q1, d1 = lines[(i - 1) % 4]
        q2, d2 = lines[i]
        M = np.column_stack([d1, -d2])
        t, _ = np.linalg.solve(M, q2 - q1)
        out.append(q1 + t * d1)
    return out


# Hjørner i beskåret koordinatsystem: [NØ, NV_ny, SV_ny, SØ_markør]
NE = to_crop(NE_ORIG)
NW_NEW = to_crop(NW_NEW_ORIG)
SW_NEW = to_crop(SW_NEW_ORIG)
SE_MARKER = to_crop(SE_MARKER_ORIG)
parcel_pts = [NE, NW_NEW, SW_NEW, SE_MARKER]

# Beregn eksakte mål og arealer
ACTUAL_AREA = 0.5 * abs(sum(parcel_pts[i][0] * parcel_pts[(i + 1) % 4][1] - parcel_pts[(i + 1) % 4][0] * parcel_pts[i][1] for i in range(4))) / (PX_PER_M ** 2)
FRONTAGE_M = np.linalg.norm(NW_NEW - NE) / PX_PER_M
EAST_LEN_M = np.linalg.norm(SE_MARKER - NE) / PX_PER_M
SOUTH_LEN_M = np.linalg.norm(SE_MARKER - SW_NEW) / PX_PER_M
SETBACK_HOUSE_M = np.dot(p_w0 - p_house_wall, n_east) / PX_PER_M
M6_REM_STR = f"{3752 - round(ACTUAL_AREA):,}".replace(",", " ")

# Dispensasjonsfritt byggefelt (11,0 m fra Myrteveien = 15 m fra vegmidt; 4,0 m fra vest, sør, øst)
build_pts = inset_quad(parcel_pts, [11.0, 4.0, 4.0, 4.0])
BUILD_AREA = 0.5 * abs(sum(build_pts[i][0] * build_pts[(i + 1) % 4][1] - build_pts[(i + 1) % 4][0] * build_pts[i][1] for i in range(4))) / (PX_PER_M ** 2)
BUILD_W_N = np.linalg.norm(build_pts[1] - build_pts[0]) / PX_PER_M
BUILD_W_S = np.linalg.norm(build_pts[3] - build_pts[2]) / PX_PER_M

# 15 m byggegrense fra vegmidt Myrteveien (~11,0 m vinkelrett inn fra nordgrense)
n_south_road = np.array([-u_west[1], u_west[0]])
if n_south_road[1] < 0:
    n_south_road = -n_south_road
road_line_pts = [
    NE - 1.8 * PX_PER_M * u_west + 11.0 * PX_PER_M * n_south_road,
    NW_NEW + 1.8 * PX_PER_M * u_west + 11.0 * PX_PER_M * n_south_road,
]

# Foreslått ny avkjørsel (ca. 4 m bredde i vestre del av ny tomt langs Myrteveien)
avk_p1 = NW_NEW - 1.5 * PX_PER_M * u_west - 1.2 * PX_PER_M * n_south_road
avk_p2 = NW_NEW - 5.5 * PX_PER_M * u_west - 1.2 * PX_PER_M * n_south_road
avk_p3 = avk_p2 + 9.0 * PX_PER_M * u_par
avk_p4 = avk_p1 + 9.0 * PX_PER_M * u_par
avkjorsel_pts = [avk_p1, avk_p2, avk_p3, avk_p4]

# Vinkelrette avstandslinjer fra Ny garasje (ved NØ-hjørnet) og Enebolig til ny vestgrense
gar_ref = to_crop(p_gar_ne)
west_at_gar = gar_ref + (SETBACK_GAR_M * PX_PER_M) * n_east

house_ref = to_crop(np.array([0.32254 * 795.0 + 808.28, 795.0]))
west_at_house = house_ref + (SETBACK_HOUSE_M * PX_PER_M) * n_east

# Ny garasje vestside-referanse for pil fra venstremargen
gar_west_mid = to_crop(p_gar_wall - (5.9 * PX_PER_M) * n_east)
m6_lawn_target = to_crop(np.array([750.0, 620.0]))

overvannskum = pt_ne(23.6, 27.9)

# Avløps- og overvannstrasé fra husets NØ-hjørne (ny kommunal soil + overvann gravd i 2014 etter pålegg;
# 1946 septiktank er fjernet, ev. gammel synkekum ukjent — nøyaktig 2014-trasé hentes fra kommunalt VA-kart)
sewer_house_ne = pt_ne(24.84, 26.8)
sewer_synkekum_ukjent = pt_ne(9.6, 10.2)
sewer_to_neighbor = pt_ne(-2.2, 23.5)


def dim_svg(p1, p2, label, dx=0, dy=0, color="#047857", w_box=68, h_box=20, font_size=10.5):
    mid = (p1 + p2) / 2.0 + np.array([dx, dy])
    return f'''
    <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}"
          stroke="{color}" stroke-width="2.1" marker-start="url(#arrow-{color[1:]})" marker-end="url(#arrow-{color[1:]})"/>
    <rect x="{mid[0] - w_box/2:.1f}" y="{mid[1] - h_box/2:.1f}" width="{w_box}" height="{h_box}"
          rx="4" fill="#ffffff" fill-opacity="0.96" stroke="{color}" stroke-width="1.3"/>
    <text x="{mid[0]:.1f}" y="{mid[1] + 3.8:.1f}" text-anchor="middle"
          font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="{font_size}" fill="{color}">{label}</text>
    '''


def rotated_dim_svg(p1, p2, label, offset_px=12, color="#dc2626", font_size=10.5):
    """Kompakt mållinje med rotert tekst langs utsiden av linjen — dekker ingen flater."""
    mid = (p1 + p2) / 2.0
    d = p2 - p1
    angle = math.degrees(math.atan2(d[1], d[0]))
    if angle > 90 or angle < -90:
        angle += 180
    n = np.array([-d[1], d[0]]) / np.linalg.norm(d)
    tp = mid + n * offset_px
    return f'''
    <line x1="{p1[0]:.1f}" y1="{p1[1]:.1f}" x2="{p2[0]:.1f}" y2="{p2[1]:.1f}"
          stroke="{color}" stroke-width="1.8" marker-start="url(#arrow-{color[1:]})" marker-end="url(#arrow-{color[1:]})"/>
    <g transform="translate({tp[0]:.1f}, {tp[1]:.1f}) rotate({angle:.1f})">
      <rect x="-50" y="-9.5" width="100" height="19" rx="4" fill="#ffffff" fill-opacity="0.94" stroke="{color}" stroke-width="1.1"/>
      <text x="0" y="3.5" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="{font_size}" fill="{color}">{label}</text>
    </g>
    '''


# Pilmål (peker rent inn fra margene uten å krysse hverandre)
avk_target = (avk_p1 + avk_p2 + avk_p3 + avk_p4) / 4.0
road_target = road_line_pts[0] + 0.18 * (road_line_pts[1] - road_line_pts[0])
parcel_edge_target = NE + 0.44 * (SE_MARKER - NE) - 18.0 * (-u_west)
sewer_east_target = sewer_to_neighbor + np.array([12.0, -3.0])

# Kompakte utvendige mållinjer
west_dim_p1 = NW_NEW - 1.0 * PX_PER_M * n_east
west_dim_p2 = SW_NEW - 1.0 * PX_PER_M * n_east

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
    <marker id="arrow-059669" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#059669"/>
    </marker>
    <marker id="arrow-334155" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#334155"/>
    </marker>
  </defs>

  <!-- 1. Foreslått ny parsell (helt ren, ingen tekstbokser oppå flata) -->
  <polygon points="{poly_str(parcel_pts)}" fill="#10b981" fill-opacity="0.22" stroke="#047857" stroke-width="2.4"/>

  <!-- 2. Dispensasjonsfritt byggefelt (helt åpent og synlig) -->
  <polygon points="{poly_str(build_pts)}" fill="#3b82f6" fill-opacity="0.16" stroke="#1d4ed8" stroke-width="2.0" stroke-dasharray="5,4"/>
  <polygon points="{poly_str(build_pts)}" fill="url(#dots-build)" stroke="none"/>

  <!-- 3. Foreslått ny avkjørsel -->
  <polygon points="{poly_str(avkjorsel_pts)}" fill="#f59e0b" fill-opacity="0.50" stroke="#b45309" stroke-width="2.2"/>

  <!-- 4. 15 m byggegrense fra vegmidt Myrteveien -->
  <line x1="{road_line_pts[0][0]:.1f}" y1="{road_line_pts[0][1]:.1f}"
        x2="{road_line_pts[1][0]:.1f}" y2="{road_line_pts[1][1]:.1f}"
        stroke="#d97706" stroke-width="2.8" stroke-dasharray="10,4,2,4"/>

  <!-- 5. Prosjekterte nye eiendomsgrenser -->
  <polyline points="{NW_NEW[0]:.1f},{NW_NEW[1]:.1f} {SW_NEW[0]:.1f},{SW_NEW[1]:.1f} {SE_MARKER[0]:.1f},{SE_MARKER[1]:.1f}"
            fill="none" stroke="#dc2626" stroke-width="4.0" stroke-dasharray="10,5"/>

  <!-- Grensepunkter: røde (nye NV/SV) og grønne (eksisterende NØ/SØ-markør) -->
  <circle cx="{NW_NEW[0]:.1f}" cy="{NW_NEW[1]:.1f}" r="5.5" fill="#dc2626" stroke="#ffffff" stroke-width="2"/>
  <circle cx="{SW_NEW[0]:.1f}" cy="{SW_NEW[1]:.1f}" r="5.5" fill="#dc2626" stroke="#ffffff" stroke-width="2"/>
  <circle cx="{NE[0]:.1f}" cy="{NE[1]:.1f}" r="6.5" fill="#059669" stroke="#ffffff" stroke-width="2.2"/>
  <circle cx="{SE_MARKER[0]:.1f}" cy="{SE_MARKER[1]:.1f}" r="11" fill="none" stroke="#059669" stroke-width="2.6" stroke-dasharray="4,2"/>
  <circle cx="{SE_MARKER[0]:.1f}" cy="{SE_MARKER[1]:.1f}" r="6.5" fill="#059669" stroke="#ffffff" stroke-width="2.2"/>

  <!-- 6. 2014 kommunal soil + overvann fra husets NØ-hjørne ned mot naboen (140/1008) + ev. gammel synkekum (?) -->
  <line x1="{sewer_house_ne[0]:.1f}" y1="{sewer_house_ne[1]:.1f}"
        x2="{sewer_to_neighbor[0]:.1f}" y2="{sewer_to_neighbor[1]:.1f}"
        stroke="#9333ea" stroke-width="3.6" stroke-dasharray="8,4" marker-end="url(#arrow-9333ea)"/>
  <line x1="{sewer_house_ne[0]:.1f}" y1="{sewer_house_ne[1]:.1f}"
        x2="{sewer_synkekum_ukjent[0]:.1f}" y2="{sewer_synkekum_ukjent[1]:.1f}"
        stroke="#c084fc" stroke-width="2.0" stroke-dasharray="3,5"/>

  <circle cx="{sewer_house_ne[0]:.1f}" cy="{sewer_house_ne[1]:.1f}" r="6.5" fill="#7e22ce" stroke="#ffffff" stroke-width="2"/>
  <circle cx="{sewer_synkekum_ukjent[0]:.1f}" cy="{sewer_synkekum_ukjent[1]:.1f}" r="6.5" fill="#f3e8ff" stroke="#7e22ce" stroke-width="1.8" stroke-dasharray="3,2"/>
  <text x="{sewer_synkekum_ukjent[0]:.1f}" y="{sewer_synkekum_ukjent[1] + 3.5:.1f}" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="9.5" fill="#581c87">?</text>

  <!-- Overvannskum M6 -->
  <circle cx="{overvannskum[0]:.1f}" cy="{overvannskum[1]:.1f}" r="5.5" fill="#0284c7" stroke="#ffffff" stroke-width="1.8"/>

  <!-- Mållinjer (kompakte og trukket utenfor ny parsell og bygninger) -->
  {dim_svg(NE - 1.9 * PX_PER_M * n_south_road, NW_NEW - 1.9 * PX_PER_M * n_south_road, f"{nf(FRONTAGE_M)} m", dx=-4, dy=-16, color="#047857", w_box=60, h_box=21, font_size=11.5)}
  {dim_svg(NE + 1.8 * PX_PER_M * (-u_west), SE_MARKER + 1.8 * PX_PER_M * (-u_west), f"{nf(EAST_LEN_M)} m (eksist.)", dx=52, dy=-12, color="#047857", w_box=98, h_box=21, font_size=10.5)}
  {rotated_dim_svg(west_dim_p1, west_dim_p2, f"{nf(L_WEST_M)} m (parallell)", offset_px=-14, color="#dc2626", font_size=9.8)}
  {dim_svg(SW_NEW + 1.6 * PX_PER_M * u_par, SE_MARKER + 1.6 * PX_PER_M * u_par, f"{nf(SOUTH_LEN_M)} m", dx=-4, dy=18, color="#dc2626", w_box=58, h_box=20, font_size=10.5)}
  {dim_svg(gar_ref, west_at_gar, f"{nf(SETBACK_GAR_M, 2)} m", dx=2, dy=-18, color="#dc2626", w_box=54, h_box=19, font_size=9.8)}
  {dim_svg(house_ref, west_at_house, f"{nf(SETBACK_HOUSE_M)} m", dx=2, dy=17, color="#1d4ed8", w_box=48, h_box=19, font_size=9.8)}

  <!-- ===================== VENSTRE MARG (UTENFOR 140/371) ===================== -->

  <!-- Callout V1: Ny avkjørsel (over Myrteveien, utenfor tomtene) -->
  <line x1="600" y1="138" x2="{avk_target[0]:.1f}" y2="{avk_target[1]:.1f}" stroke="#b45309" stroke-width="2.2" marker-end="url(#arrow-b45309)"/>
  <g transform="translate(362, 104)">
    <rect width="240" height="58" rx="6" fill="#fef3c7" fill-opacity="0.97" stroke="#d97706" stroke-width="1.6"/>
    <text x="12" y="18" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.5" fill="#78350f">NY AVKJØRSEL (MYRTEVEIEN)</text>
    <text x="12" y="34" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#92400e">Direkte til kommunal vei (141/288)</text>
    <text x="12" y="48" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#92400e">God klaring øst for Ny garasje / M6</text>
  </g>

  <!-- Callout V2: Ny garasje M6 (helt i venstre marg, vest for Trollheggveien) -->
  <polyline points="292,438 415,438 {gar_west_mid[0] - 8:.1f},{gar_west_mid[1]:.1f}" fill="none" stroke="#334155" stroke-width="2.0" marker-end="url(#arrow-334155)"/>
  <g transform="translate(20, 396)">
    <rect width="274" height="84" rx="7" fill="#f1f5f9" fill-opacity="0.97" stroke="#475569" stroke-width="1.6"/>
    <text x="12" y="20" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.5" fill="#0f172a">NY GARASJE M6 (9,9 × 5,9 m)</text>
    <text x="12" y="36" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.5" fill="#334155">• 58,4 m² BYA (&gt; 50 m² ⇒ min. 4,0 m)</text>
    <text x="12" y="51" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#334155">• Vestgrense parallell m/hus &amp; garasje</text>
    <text x="12" y="66" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#334155">• Full 4,05 m avstand (ingen dispensasjon)</text>
    <text x="12" y="79" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#64748b">(Alt.: 2,0 m / ≤ 50 m² garasje gir 650 m²)</text>
  </g>

  <!-- Callout V3: Gjenværende hovedtomt M6 (helt i venstre marg, vest for Trollheggveien) -->
  <polyline points="292,630 430,630 {m6_lawn_target[0]:.1f},{m6_lawn_target[1]:.1f}" fill="none" stroke="#334155" stroke-width="2.0" marker-end="url(#arrow-334155)"/>
  <g transform="translate(20, 588)">
    <rect width="274" height="86" rx="7" fill="#f8fafc" fill-opacity="0.97" stroke="#334155" stroke-width="1.8"/>
    <text x="12" y="20" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.8" fill="#0f172a">GJENVÆRENDE HOVEDTOMT (M6)</text>
    <text x="12" y="38" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="11.0" fill="#334155">Gnr 140 / Bnr 371 • ca. {M6_REM_STR} m²</text>
    <text x="12" y="55" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#475569">• Inkl. bolig + Ny garasje (BYA &lt; 10 %)</text>
    <text x="12" y="70" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#475569">• 9,9 m fra bolig til ny vestgrense</text>
    <text x="12" y="81" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.2" fill="#475569">• SV-hjørne trukket nord ⇒ åpen østhage</text>
  </g>

  <!-- ===================== HØYRE MARG (UTENFOR 140/371 & NY PARSELL) ===================== -->

  <!-- Callout H1: 15 m byggegrense -->
  <polyline points="1272,216 1160,216 {road_target[0]:.1f},{road_target[1]:.1f}" fill="none" stroke="#b45309" stroke-width="2.1" marker-end="url(#arrow-b45309)"/>
  <g transform="translate(1272, 184)">
    <rect width="328" height="62" rx="7" fill="#fffbeb" fill-opacity="0.97" stroke="#d97706" stroke-width="1.6"/>
    <text x="12" y="20" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.5" fill="#92400e">15 m BYGGEGRENSE FRA VEGMIDT</text>
    <text x="12" y="36" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.6" fill="#78350f">Tilsv. ~11 m inn fra nordre tomtegrense</text>
    <text x="12" y="51" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.4" fill="#78350f">(NB: Myrteveien 2 ligger nærmere vei — ev. strøkslinje)</text>
  </g>

  <!-- Callout H2: NY PARSELL hovedkort (i høyre marg, helt utenfor parsellen!) -->
  <polyline points="1272,368 1185,368 {parcel_edge_target[0]:.1f},{parcel_edge_target[1]:.1f}" fill="none" stroke="#059669" stroke-width="2.4" marker-end="url(#arrow-059669)"/>
  <g transform="translate(1272, 294)">
    <rect width="328" height="146" rx="8" fill="#ecfdf5" fill-opacity="0.98" stroke="#059669" stroke-width="2.2"/>
    <text x="164" y="22" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="12.0" fill="#064e3b">NY PARSELL (NORD-ØST)</text>
    <text x="164" y="42" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="14.5" fill="#047857">ca. {ACTUAL_AREA:.0f} m²</text>
    <line x1="16" y1="52" x2="312" y2="52" stroke="#a7f3d0" stroke-width="1.4"/>
    <text x="16" y="70" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.8" fill="#065f46">• Nord: {nf(FRONTAGE_M)} m • Øst: {nf(EAST_LEN_M)} m (eksist.)</text>
    <text x="16" y="86" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.8" fill="#065f46">• Vest: {nf(L_WEST_M)} m (parallell) • Sør: {nf(SOUTH_LEN_M)} m (skrå)</text>
    <text x="16" y="103" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.8" fill="#065f46">• Byggefelt: {nf(BUILD_W_N)}–{nf(BUILD_W_S)} × 21–25 m ({BUILD_AREA:.0f} m²)</text>
    <text x="16" y="119" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.8" fill="#065f46">• Maks 25 % BYA = {ACTUAL_AREA * 0.25:.0f} m² • MUA ≥ 150 m²</text>
    <text x="16" y="135" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.8" fill="#047857">• Kun 2 nye grensemerker (NV &amp; SV)</text>
  </g>

  <!-- Callout H3: 2014 kommunal soil + overvann & tinglyste retter -->
  <polyline points="1272,542 1190,542 {sewer_east_target[0]:.1f},{sewer_east_target[1]:.1f}" fill="none" stroke="#9333ea" stroke-width="2.2" marker-end="url(#arrow-9333ea)"/>
  <g transform="translate(1272, 488)">
    <rect width="328" height="110" rx="7" fill="#faf5ff" fill-opacity="0.98" stroke="#9333ea" stroke-width="1.8"/>
    <text x="12" y="20" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.4" fill="#581c87">KOMMUNAL SOIL &amp; OVERVANN (2014)</text>
    <text x="12" y="37" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.4" fill="#6b21a8">• Ny soil + overvann gravd til hus i 2014 (pålegg)</text>
    <text x="12" y="53" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.4" fill="#6b21a8">• 1946 septiktank fjernet; ev. synkekum (?) ukjent</text>
    <text x="12" y="69" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.4" fill="#7e22ce">• Innhente 2014-innmåling / VA-kart fra kommunen</text>
    <text x="12" y="85" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.4" fill="#581c87">• Tinglyses: strøm, vann, avløp, vei (+ omlegging)</text>
    <text x="12" y="100" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#7e22ce">(Samlet erklæring tinglyses ved matrikulering)</text>
  </g>

  <!-- Callout H4: Eksisterende tomtemarkør mellom naboene mot øst -->
  <polyline points="1272,778 {SE_MARKER[0] + 15:.1f},{SE_MARKER[1] + 2:.1f}" fill="none" stroke="#059669" stroke-width="2.2" marker-end="url(#arrow-059669)"/>
  <g transform="translate(1272, 742)">
    <rect width="328" height="68" rx="7" fill="#ecfdf5" fill-opacity="0.98" stroke="#059669" stroke-width="1.8"/>
    <text x="12" y="20" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.5" fill="#064e3b">EKSISTERENDE TOMTEMARKØR (SØ)</text>
    <text x="12" y="37" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#065f46">Felles grensepunkt Myrteveien 2 (140/1008) og</text>
    <text x="12" y="53" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.5" fill="#065f46">Øvre Bogenvei 31 (140/995) — gjenbrukes direkte</text>
  </g>

  <!-- Toppbanner -->
  <g transform="translate(20, 14)">
    <rect width="1580" height="72" rx="8" fill="#0f172a" fill-opacity="0.95" stroke="#334155" stroke-width="1.8"/>
    <text x="790" y="24" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="16.0" fill="#ffffff">FORELØPIG SITUASJONSPLAN — TOMTEFRADELING NORD-ØST (PARALLELL VESTGRENSE &amp; ØST-MARKØR)</text>
    <text x="790" y="44" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.8" fill="#38bdf8">Myrteveien 6 (Gnr 140 / Bnr 371, 3 752 m²) • Tønsberg kommune • Ny parsell: ca. {ACTUAL_AREA:.0f} m²</text>
    <text x="790" y="61" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.4" fill="#cbd5e1">Delingstillatelse nå (PBL § 20-1 m) — Oppmålingsforretning ved byggesøknad / byggetillatelse (innen 3 år, PBL § 21-9)</text>
  </g>

  <!-- Tegnforklaring (Nederst til venstre — helt utenfor 140/371) -->
  <g transform="translate(20, 956)">
    <rect width="468" height="184" rx="8" fill="#ffffff" fill-opacity="0.97" stroke="#0f172a" stroke-width="1.8"/>
    <text x="14" y="22" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="11.5" fill="#0f172a">TEGNFORKLARING</text>

    <rect x="14" y="34" width="24" height="14" fill="#10b981" fill-opacity="0.26" stroke="#047857" stroke-width="2"/>
    <text x="48" y="45" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.0" fill="#1e293b">Foreslått fradelt boligtomt (ca. {ACTUAL_AREA:.0f} m² — følger øst-markør)</text>

    <line x1="14" y1="64" x2="38" y2="64" stroke="#dc2626" stroke-width="3.5" stroke-dasharray="6,3"/>
    <text x="48" y="68" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.0" fill="#1e293b">Ny grense: vest parallell m/hus &amp; garasje (4,05 m), skrå mot SØ</text>

    <rect x="14" y="80" width="24" height="14" fill="#3b82f6" fill-opacity="0.20" stroke="#1d4ed8" stroke-width="1.8" stroke-dasharray="4,3"/>
    <text x="48" y="91" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.0" fill="#1e293b">Dispensasjonsfritt byggefelt ({nf(BUILD_W_N)}–{nf(BUILD_W_S)} × 21–25 m = {BUILD_AREA:.0f} m²)</text>

    <line x1="14" y1="110" x2="38" y2="110" stroke="#d97706" stroke-width="2.5" stroke-dasharray="8,3,2,3"/>
    <text x="48" y="114" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.0" fill="#1e293b">15 m byggegrense fra vegmidt Myrteveien (~11 m fra grense)</text>

    <rect x="14" y="126" width="24" height="14" fill="#f59e0b" fill-opacity="0.50" stroke="#b45309" stroke-width="1.8"/>
    <text x="48" y="137" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.0" fill="#1e293b">Foreslått ny avkjørsel fra Myrteveien (kommunal vei)</text>

    <line x1="14" y1="156" x2="38" y2="156" stroke="#9333ea" stroke-width="3.4" stroke-dasharray="5,3"/>
    <text x="48" y="160" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="10.0" fill="#581c87">2014 kommunal soil + overvann (antatt retning) • (?) ev. synkekum</text>
  </g>

  <!-- Stempel (Nederst til høyre) -->
  <g transform="translate(1196, 1094)">
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
