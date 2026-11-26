"""
Genererer eget forslag til skisse for FELLES UTKJØRING (Myrteveien 6 + fradelt tomt Var. 1C):
- Plantegning (1:250 utsnitt) med to nivåer:
  * Øvre nivå (+25,5–25,8 NN2000): M6 hovedinngang nord, portrom, Ny garasje vestporter,
    og trinnfri gangvei (UU ~4 %) vest for Ny garasje ut til felles utkjøring.
  * Nedre nivå (+23,25–24,4 NN2000): Kjellerport NØ på Ny garasje, felles nedre tun/utkjørsel
    forskjøvet østover mot lavere Myrteveien (kote +24,1–24,6), og ny garasje/carport på
    fradelt tomt parallelt med Myrteveien (2,5 m fra veigrense).
- To eksakte høydeprofiler (lengdesnitt) basert på Kartverket DTM1 (NN2000):
  * Profil A: Kjellerport NØ -> felles tun -> Myrteveien (sammenligning e=+8 m vs rett nord)
  * Profil B: M6 norddør -> portrom vest -> felles utkjøring (trinnfri ~4 %)

Alle merkelapper ligger utenfor tomtene / i dedikerte marger.
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

# Tight, høyoppløst utsnitt rundt Myrteveien + Ny garasje + M6 nord + nordre halvdel av ny parsell
# Plass til venstre og høyre marg utenfor tomteområdet
CROP_X0, CROP_Y0 = 560, 120
CROP_X1, CROP_Y1 = 1580, 820
CROP_W = CROP_X1 - CROP_X0  # 1020
CROP_H = CROP_Y1 - CROP_Y0  # 700
crop_im = im.crop((CROP_X0, CROP_Y0, CROP_X1, CROP_Y1))

# Total lerretsstørrelse (SVG-enheter; rendres i 2x = 3200 x 2400 px)
W, H = 1600, 1200
MAP_X0, MAP_Y0 = 290, 92
MAP_W, MAP_H = 1020, 700  # 1:1 med crop_im!

# Kalibrerte referansepunkter i originalbildet (px)
PX = 14.6994
NE_ORIG = np.array([1293.17, 208.93])
NW_ORIG = np.array([554.70, 399.88])
SE_MARKER_ORIG = np.array([1440.56, 822.33])

u_west = (NW_ORIG - NE_ORIG) / np.linalg.norm(NW_ORIG - NE_ORIG)
u_east_road = -u_west
n_south_road = np.array([-u_west[1], u_west[0]])
if n_south_road[1] < 0:
    n_south_road = -n_south_road

C_BLDG = 0.3227
u_par = np.array([C_BLDG, 1.0]) / math.hypot(C_BLDG, 1.0)
n_east = np.array([u_par[1], -u_par[0]])  # vinkelrett østover fra hus/garasje

# Ny garasje (M6) hjørner i originalbilde
p_gar_ne_orig = np.array([0.32277 * 432.0 + 898.15, 432.0])
p_gar_se_orig = p_gar_ne_orig + 9.9 * PX * u_par
p_gar_nw_orig = p_gar_ne_orig - 5.9 * PX * n_east
p_gar_sw_orig = p_gar_se_orig - 5.9 * PX * n_east

# Variant 1C ny vestgrense (1,05 m øst for Ny garasje)
p_w0 = np.array([0.32277 * 500.0 + 898.15, 500.0]) + (1.05 * PX) * n_east
t_nw, _ = np.linalg.solve(np.column_stack([u_par, -u_west]), NE_ORIG - p_w0)
NW_NEW_ORIG = p_w0 + t_nw * u_par
SW_NEW_ORIG = NW_NEW_ORIG + (37.5 * PX) * u_par

# M6 hovedhus nordvegg & inngangsdør (trapp på nordveggen)
p_house_ne_orig = np.array([0.32254 * 695.0 + 808.28, 695.0])
p_house_inngang_orig = p_house_ne_orig - 4.7 * PX * n_east
p_house_nw_orig = p_house_ne_orig - 8.6 * PX * n_east


def to_svg(p_orig):
    return np.array([p_orig[0] - CROP_X0 + MAP_X0, p_orig[1] - CROP_Y0 + MAP_Y0])


def poly_str(pts):
    return " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)


def road_pt(e_m, s_m=0.0):
    """Punkt målt e_m meter øst for NV_ny langs Myrteveien og s_m meter sørover vinkelrett på veien."""
    return to_svg(NW_NEW_ORIG + (e_m * PX) * u_east_road + (s_m * PX) * n_south_road)


NE = to_svg(NE_ORIG)
NW_NEW = to_svg(NW_NEW_ORIG)
SW_NEW = to_svg(SW_NEW_ORIG)
SE_MARKER = to_svg(SE_MARKER_ORIG)
GAR_NE = to_svg(p_gar_ne_orig)
GAR_SE = to_svg(p_gar_se_orig)
GAR_NW = to_svg(p_gar_nw_orig)
GAR_SW = to_svg(p_gar_sw_orig)
H_NE = to_svg(p_house_ne_orig)
H_INNG = to_svg(p_house_inngang_orig)
H_NW = to_svg(p_house_nw_orig)

# Beregn 15 m byggegrense fra vegmidt (~11 m fra nordgrense) + 4 m byggefelt på ny parsell
def inset_quad(pts, insets_m):
    sa = sum(pts[i][0] * pts[(i + 1) % 4][1] - pts[(i + 1) % 4][0] * pts[i][1] for i in range(4))
    sign = 1.0 if sa > 0 else -1.0
    lines = []
    for i in range(4):
        p1, p2 = pts[i], pts[(i + 1) % 4]
        d = (p2 - p1) / np.linalg.norm(p2 - p1)
        n_in = sign * np.array([-d[1], d[0]])
        lines.append((p1 + insets_m[i] * PX * n_in, d))
    out = []
    for i in range(4):
        q1, d1 = lines[(i - 1) % 4]
        q2, d2 = lines[i]
        t, _ = np.linalg.solve(np.column_stack([d1, -d2]), q2 - q1)
        out.append(q1 + t * d1)
    return out


parcel_pts = [NE, NW_NEW, SW_NEW, SE_MARKER]
build_pts = inset_quad(parcel_pts, [11.0, 4.0, 4.0, 4.0])
road_15m_p1 = road_pt(-1.5, 11.0)
road_15m_p2 = road_pt(21.5, 11.0)

# === 1. FELLES NEDRE UTKJØRING & SNUTUN (kote +23,25 -> +24,4) ===
# Felles munning mot Myrteveien ved e = +5,5 til +10,8 m (5,3 m bred, kote +24,15–24,65)
# Går skrått inn til felles snutun foran både kjellerport NØ (på M6s Ny garasje) og ny garasje/carport på ny tomt!
kjeller_port_n = GAR_NE + 0.5 * PX * u_par
kjeller_port_s = GAR_NE + 4.8 * PX * u_par

felles_drive_pts = [
    road_pt(5.5, -1.6),                                # Myrteveien kant vest (kote +24,65)
    road_pt(10.8, -1.6),                               # Myrteveien kant øst (kote +24,15)
    road_pt(11.3, 4.8),                                # Sving inn mot ny garasje/carport port (vest)
    road_pt(11.5, 10.6),                               # Sørkant av felles snutun (nord for 15 m-linje)
    kjeller_port_s + 2.8 * PX * n_east + 0.8 * PX * u_par,  # Utkjøringslomme sør for kjellerport NØ
    kjeller_port_s + 0.1 * PX * n_east,                # Kjellerport NØ sørkant (kote +23,25)
    kjeller_port_n + 0.1 * PX * n_east,                # Kjellerport NØ nordkant (kote +23,25)
    GAR_NE - 2.2 * PX * u_par + 1.0 * PX * n_east,     # Støttemur-hjørne nord for kjellerport
    road_pt(5.2, 4.5),                                 # Indre vestkant mot støttemur
]

# === 2. NY GARASJE / CARPORT PÅ FRADELT TOMT (i forsonen nord for 15 m-linje!) ===
# Parallelt med Myrteveien, 2,5 m fra nordgrense, e = +11,5 til +18,3 m (6,8 m x 5,8 m = ~39,4 m² <= 50 m²)
# Port/innkjøring mot VEST rett inn på felles nedre tun (kote +23,8–24,0)
ny_gar_pts = [
    road_pt(11.6, 2.5),
    road_pt(18.4, 2.5),
    road_pt(18.4, 8.3),
    road_pt(11.6, 8.3),
]
# 2 ekstra åpne p-plasser rett sør/øst ved siden av for tomannsbolig (totalt 4 p-plasser!)
ny_park_pts = [
    road_pt(11.6, 8.6),
    road_pt(16.6, 8.6),
    road_pt(16.6, 11.1),
    road_pt(11.6, 11.1),
]

# === 3. ØVRE NIVÅ M6: GÅRDSPLASS + TRINNFRI GANGVEI FRA INNGANGSDØR NORDVEGG ===
# Fra M6 hovedinngang (nordvegg, kote +25,7 / platting +26,1) gjennom portrommet VEST for Ny garasje (+25,5),
# rundt nordvest-hjørnet av Ny garasje (+25,7) og slakt østover (+25,2 -> +24,6) til felles utkjøring!
gang_pts = [
    H_INNG - 0.5 * PX * u_par,
    GAR_SW - 2.3 * PX * n_east + 1.2 * PX * u_par,
    GAR_NW - 2.4 * PX * n_east - 0.8 * PX * u_par,
    GAR_NW - 0.5 * PX * n_east - 4.0 * PX * u_par,
    road_pt(-1.5, 2.6),
    road_pt(3.5, 2.0),
    road_pt(6.2, 0.2),
]

# Kort utvendig hagetrappe-snarvei fra M6 portrom/østkant ned til felles nedre tun (~10 trinn)
trapp_p1 = GAR_SE + 0.6 * PX * u_par - 0.5 * PX * n_east
trapp_p2 = GAR_SE + 0.6 * PX * u_par + 3.2 * PX * n_east

# Støttemur mellom øvre nivå (+25,5–25,7) og nedre utkjøringsnivå (+23,3–24,5)
# Taper ned mot 0 m ved s=1,8 m slik at gangveien møter felles munning trinnfritt uten å krysse muren!
mur_pts = [
    GAR_NE + 0.05 * PX * n_east,
    GAR_NE - 2.4 * PX * u_par + 0.8 * PX * n_east,
    road_pt(4.6, 4.3),
    road_pt(4.9, 1.8),
]
mur_south_pts = [
    kjeller_port_s + 0.05 * PX * n_east,
    kjeller_port_s + 2.8 * PX * n_east + 0.9 * PX * u_par,
    GAR_SE + 2.5 * PX * n_east + 1.2 * PX * u_par,
]

# Kjørepiler for tydelig trafikkflyt
kjeller_arrow_pts = [
    kjeller_port_n * 0.5 + kjeller_port_s * 0.5 - 0.8 * PX * n_east,
    kjeller_port_n * 0.5 + kjeller_port_s * 0.5 + 3.2 * PX * n_east,
    road_pt(7.8, 5.5),
    road_pt(8.0, -2.5),
]
ny_gar_arrow_pts = [
    road_pt(13.2, 5.4),
    road_pt(9.0, 5.4),
    road_pt(8.3, -2.2),
]
vest_port_arrow1 = [GAR_NW + 2.2 * PX * u_par + 0.8 * PX * n_east, GAR_NW + 2.2 * PX * u_par - 3.4 * PX * n_east]
vest_port_arrow2 = [GAR_NW + 5.2 * PX * u_par + 0.8 * PX * n_east, GAR_NW + 5.2 * PX * u_par - 3.4 * PX * n_east]


def path_d(pts):
    return "M " + " L ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)


def kote_badge(pt, txt, bg="#ffffff", stroke="#0f172a", fg="#0f172a", dx=0, dy=0):
    x, y = pt[0] + dx, pt[1] + dy
    w = max(44, len(txt) * 6.4 + 10)
    return f'''
    <circle cx="{pt[0]:.1f}" cy="{pt[1]:.1f}" r="3.2" fill="{stroke}" stroke="#ffffff" stroke-width="1.2"/>
    <rect x="{x - w/2:.1f}" y="{y - 8.5:.1f}" width="{w:.1f}" height="17" rx="3.5" fill="{bg}" fill-opacity="0.95" stroke="{stroke}" stroke-width="1.1"/>
    <text x="{x:.1f}" y="{y + 3.3:.1f}" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.0" fill="{fg}">{txt}</text>
    '''


# ===================== HØYDEPROFILER (NEDRE DEL: Y = 810..1180) =====================
def build_profile_svg(ox, oy, pw, ph, title, subtitle, x_max, z_min, z_max, series, notes):
    """Bygger et rent, målsatt høydeprofil-diagram i NN2000."""
    pad_l, pad_r, pad_t, pad_b = 56, 22, 48, 40
    gx0, gy0 = ox + pad_l, oy + pad_t
    gw, gh = pw - pad_l - pad_r, ph - pad_t - pad_b

    def sx(x):
        return gx0 + (x / x_max) * gw

    def sy(z):
        return gy0 + gh - ((z - z_min) / (z_max - z_min)) * gh

    els = [
        f'<rect x="{ox}" y="{oy}" width="{pw}" height="{ph}" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.6"/>',
        f'<text x="{ox + 16}" y="{oy + 21}" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="11.5" fill="#0f172a">{title}</text>',
        f'<text x="{ox + 16}" y="{oy + 36}" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.3" fill="#475569">{subtitle}</text>',
    ]
    # Grid Y (hver 0,5 m)
    z_val = z_min
    while z_val <= z_max + 0.001:
        yy = sy(z_val)
        is_int = abs(z_val - round(z_val)) < 0.01
        els.append(f'<line x1="{gx0:.1f}" y1="{yy:.1f}" x2="{gx0+gw:.1f}" y2="{yy:.1f}" stroke="{"#cbd5e1" if is_int else "#f1f5f9"}" stroke-width="{"1.1" if is_int else "0.8"}"/>')
        if is_int or abs(z_val - z_min) < 0.01 or abs(z_val - z_max) < 0.01:
            lbl = f"+{z_val:.1f}".replace(".", ",")
            els.append(f'<text x="{gx0 - 7:.1f}" y="{yy + 3.2:.1f}" text-anchor="end" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="8.8" fill="#64748b">{lbl}</text>')
        z_val += 0.5
    # Grid X (hver 5 m)
    for xv in range(0, int(x_max) + 1, 5):
        xx = sx(xv)
        els.append(f'<line x1="{xx:.1f}" y1="{gy0:.1f}" x2="{xx:.1f}" y2="{gy0+gh:.1f}" stroke="#f1f5f9" stroke-width="0.9"/>')
        els.append(f'<text x="{xx:.1f}" y="{gy0 + gh + 14:.1f}" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="8.8" fill="#64748b">{xv} m</text>')

    # Akseramme
    els.append(f'<rect x="{gx0:.1f}" y="{gy0:.1f}" width="{gw:.1f}" height="{gh:.1f}" fill="none" stroke="#94a3b8" stroke-width="1.2"/>')
    els.append(f'<text x="{ox + 14}" y="{gy0 + gh/2:.1f}" transform="rotate(-90 {ox + 14} {gy0 + gh/2:.1f})" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="8.8" fill="#475569">Kote NN2000 (m)</text>')

    # Serier
    for s in series:
        pts_s = [(sx(x), sy(z)) for x, z in s["pts"]]
        d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts_s)
        if s.get("fill"):
            fill_d = d + f" L {pts_s[-1][0]:.1f},{gy0+gh:.1f} L {pts_s[0][0]:.1f},{gy0+gh:.1f} Z"
            els.append(f'<path d="{fill_d}" fill="{s["fill"]}" fill-opacity="{s.get("fill_op", 0.14)}" stroke="none"/>')
        dash = f' stroke-dasharray="{s["dash"]}"' if s.get("dash") else ""
        els.append(f'<path d="{d}" fill="none" stroke="{s["color"]}" stroke-width="{s.get("lw", 2.6)}"{dash}/>')
        for (x_m, z_m), (px, py) in zip(s["pts"], pts_s):
            if s.get("dots", True):
                els.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.6" fill="{s["color"]}" stroke="#ffffff" stroke-width="1.3"/>')
        for lbl_x, lbl_z, txt, dx, dy, col in s.get("ann", []):
            ax, ay = sx(lbl_x) + dx, sy(lbl_z) + dy
            els.append(f'<text x="{ax:.1f}" y="{ay:.1f}" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="8.8" fill="{col}">{txt}</text>')

    # Notatlinje nederst
    els.append(f'<text x="{gx0}" y="{oy + ph - 9}" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.0" fill="#334155">{notes}</text>')
    return "\n".join(els)


# Profil A: Kjellerport NØ (+23,25) -> Felles tun (+23,70) -> Myrteveien ved e=+8 m (+24,35)
# vs. Rett nord til NV_ny (+25,25 -> 18 % for bratt!)
profile_a_svg = build_profile_svg(
    ox=20, oy=812, pw=770, ph=368,
    title="PROFIL A — KJELLERPORT NØ → FELLES UTKJØRING (MYRTEVEIEN)",
    subtitle="Eksakte DTM1-koter (NN2000): Å legge felles avkjørsel 6–10 m øst for NV_ny halverer stigningen og sparer sprengning!",
    x_max=16.0, z_min=22.5, z_max=26.5,
    series=[
        {
            "pts": [(0, 24.85), (3, 24.75), (7, 24.26), (11, 24.30), (15, 24.38)],
            "color": "#64748b", "lw": 2.0, "dash": "6,4", "dots": False, "fill": "#94a3b8", "fill_op": 0.12,
            "ann": [(4.5, 24.95, "Dagens terreng (~+24,8 → +24,3)", 0, -4, "#475569")],
        },
        {
            "pts": [(0, 25.85), (0.8, 25.85)],
            "color": "#334155", "lw": 4.0, "dots": False,
            "ann": [(2.2, 26.05, "Ny garasje 1. etg (+25,85)", 0, 0, "#0f172a")],
        },
        {
            # Rød advarselslinje: Rett nord til NV_ny (+25,25 på 11 m) = 18 %!
            "pts": [(0, 23.25), (3.5, 23.55), (10.8, 25.25)],
            "color": "#dc2626", "lw": 2.2, "dash": "5,3", "dots": True,
            "ann": [(8.8, 25.48, "Rett nord til NV_ny (+25,25): ~18 % (FOR BRATT!)", 0, 0, "#b91c1c")],
        },
        {
            # Grønn/oransje anbefalt profil: Diagonalt til felles avkjørsel e=+8 m (+24,35 på 14,5 m)
            "pts": [(0, 23.25), (3.5, 23.40), (10.5, 24.12), (14.5, 24.32)],
            "color": "#d97706", "lw": 3.4, "dots": True, "fill": "#f59e0b", "fill_op": 0.14,
            "ann": [
                (1.5, 23.02, "Kjellerport +23,25", 0, 12, "#92400e"),
                (7.0, 23.58, "Anbefalt: ~7,5 % (1:13) [OK]", 0, 12, "#047857"),
                (12.8, 24.08, "Siste 4 m: 5 % (1:20)", 0, 14, "#047857"),
                (14.5, 24.55, "Myrteveien +24,32", -12, -4, "#92400e"),
            ],
        },
    ],
    notes="Obs fjell (0,2–1,5 m): Kjeller på +23,25 gir ~1,5 m uttak ved NØ-vegg (ca. 0,9 m mindre enn rett nord). Krever sluk/dren v/port!"
)

# Profil B: Trinnfri gangvei fra M6 norddør (+26,1 platting / +25,7 terreng) -> portrom vest (+25,5) -> felles utkjøring (+24,6)
profile_b_svg = build_profile_svg(
    ox=810, oy=812, pw=770, ph=368,
    title="PROFIL B — GANGVEI FRA INNGANGSDØR NORDVEGG (M6) → FELLES UTKJØRING",
    subtitle="Går på ØVRE nivå vest for Ny garasje (skjermet fra kjellerutkjøring) med slakt, trinnfritt fall ut til Myrteveien",
    x_max=28.0, z_min=22.5, z_max=26.5,
    series=[
        {
            "pts": [(0, 25.69), (6, 25.46), (14, 25.70), (20, 25.50), (24, 25.05), (27, 24.62)],
            "color": "#64748b", "lw": 1.9, "dash": "6,4", "dots": False,
            "ann": [(13.5, 25.92, "Eksisterende terreng langs vestside (+25,5–25,7)", 0, 0, "#475569")],
        },
        {
            "pts": [(0, 25.75), (6, 25.55), (14, 25.50), (21, 25.15), (27, 24.62)],
            "color": "#0d9488", "lw": 3.4, "dots": True, "fill": "#14b8a6", "fill_op": 0.15,
            "ann": [
                (2.2, 26.15, "M6 norddør (terreng +25,7 / dør +26,1)", 48, 0, "#0f766e"),
                (9.5, 25.20, "Portrom v/vestporter (+25,5)", 0, 10, "#0f766e"),
                (20.0, 24.78, "Slak gangvei: ~4 % (1:25) — UU trinnfri [OK]", -14, 14, "#047857"),
                (26.5, 24.92, "Felles munning +24,6", -34, -4, "#0f766e"),
            ],
        },
        {
            # Referanse: Nedre kjellernivå (på østsiden av støttemuren)
            "pts": [(14, 23.25), (27, 24.32)],
            "color": "#d97706", "lw": 1.8, "dash": "4,4", "dots": False,
            "ann": [(19.5, 23.45, "← Nivåsprang til nedre kjellerplan (~1,8–2,2 m støttemur)", 0, 8, "#b45309")],
        },
    ],
    notes="Alternativ snarvei: Utvendig hagetrappe (~10–12 trinn) ved SØ-hjørne av Ny garasje gir 12 m rett ned til felles nedre tun."
)

# Piler fra sidekort inn til kartet
avk_mid = road_pt(8.2, 2.0)
ny_gar_mid = road_pt(15.0, 5.4)
kjeller_mid = (kjeller_port_n + kjeller_port_s) / 2.0 + 0.5 * PX * n_east
gang_mid = gang_pts[2]

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <defs>
    <clipPath id="map-clip">
      <rect x="{MAP_X0}" y="{MAP_Y0}" width="{MAP_W}" height="{MAP_H}" rx="6"/>
    </clipPath>
    <pattern id="dots-build" width="8" height="8" patternUnits="userSpaceOnUse">
      <circle cx="4" cy="4" r="1.2" fill="#1d4ed8" opacity="0.40"/>
    </pattern>
    <pattern id="hatch-mur" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="6" stroke="#78350f" stroke-width="2.2"/>
    </pattern>
    <marker id="arr-amber" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#b45309"/>
    </marker>
    <marker id="arr-teal" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#0f766e"/>
    </marker>
    <marker id="arr-sky" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#0369a1"/>
    </marker>
    <marker id="arr-red" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#dc2626"/>
    </marker>
    <marker id="arr-slate" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#334155"/>
    </marker>
  </defs>

  <!-- Bakgrunn kun for marger og nedre profilfelt (kartfeltet forblir transparent) -->
  <rect x="0" y="0" width="{W}" height="{MAP_Y0}" fill="#f8fafc"/>
  <rect x="0" y="{MAP_Y0 + MAP_H}" width="{W}" height="{H - MAP_Y0 - MAP_H}" fill="#f8fafc"/>
  <rect x="0" y="{MAP_Y0}" width="{MAP_X0}" height="{MAP_H}" fill="#f8fafc"/>
  <rect x="{MAP_X0 + MAP_W}" y="{MAP_Y0}" width="{W - MAP_X0 - MAP_W}" height="{MAP_H}" fill="#f8fafc"/>

  <!-- Toppbanner -->
  <g transform="translate(20, 12)">
    <rect width="1560" height="68" rx="8" fill="#0f172a" stroke="#334155" stroke-width="1.8"/>
    <text x="780" y="24" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="15.5" fill="#ffffff">FORSLAG TIL SKISSE — FELLES UTKJØRING, KJELLERPORT NØ &amp; GANGVEI FRA NORDDØR (M6 + VAR. 1C)</text>
    <text x="780" y="43" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="11.2" fill="#38bdf8">Myrteveien 6 (140/371) + Ny 750 m² parsell • Eksakte DTM1-koter (NN2000) • To-nivå løsning utnytter 2,2 m fall langs Myrteveien</text>
    <text x="780" y="59" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="10.0" fill="#cbd5e1">Øvre nivå (+25,5–25,8): M6 vestporter + trinnfri gangvei fra norddør • Nedre nivå (+23,25–24,4): Kjellerport NØ + felles utkjørsel + ny garasje/carport</text>
  </g>

  <!-- Kartramme (bakgrunnsbildet composes her i Python) -->
  <rect x="{MAP_X0}" y="{MAP_Y0}" width="{MAP_W}" height="{MAP_H}" rx="6" fill="none" stroke="#334155" stroke-width="2.0"/>

  <!-- KARTLAG (klippet rent til kartrammen) -->
  <g clip-path="url(#map-clip)">
    <!-- 1. Ny parsell Variant 1C (grønn) -->
    <polygon points="{poly_str(parcel_pts)}" fill="#10b981" fill-opacity="0.16" stroke="#047857" stroke-width="2.2"/>

    <!-- 2. Dispensasjonsfritt byggefelt på ny parsell (blå — helt urørt bak garasjen!) -->
    <polygon points="{poly_str(build_pts)}" fill="#3b82f6" fill-opacity="0.13" stroke="#1d4ed8" stroke-width="1.8" stroke-dasharray="5,4"/>
    <polygon points="{poly_str(build_pts)}" fill="url(#dots-build)" stroke="none"/>

    <!-- 3. 15 m byggegrense fra vegmidt Myrteveien -->
    <line x1="{road_15m_p1[0]:.1f}" y1="{road_15m_p1[1]:.1f}" x2="{road_15m_p2[0]:.1f}" y2="{road_15m_p2[1]:.1f}"
          stroke="#d97706" stroke-width="2.2" stroke-dasharray="9,4,2,4"/>

    <!-- 4. Felles nedre utkjørsel & snutun (kote +23,25 -> +24,4) -->
    <polygon points="{poly_str(felles_drive_pts)}" fill="#f59e0b" fill-opacity="0.34" stroke="#b45309" stroke-width="2.4"/>

    <!-- 5. Ny garasje/carport på fradelt tomt (parallelt m/Myrteveien, 2,5 m fra veigrense, <=50 m²) -->
    <polygon points="{poly_str(ny_gar_pts)}" fill="#0ea5e9" fill-opacity="0.38" stroke="#0369a1" stroke-width="2.6"/>
    <!-- Portåpning på vestsiden av ny garasje -->
    <line x1="{ny_gar_pts[0][0]:.1f}" y1="{ny_gar_pts[0][1]:.1f}" x2="{ny_gar_pts[3][0]:.1f}" y2="{ny_gar_pts[3][1]:.1f}"
          stroke="#0284c7" stroke-width="5.0" stroke-dasharray="6,4"/>
    <!-- 2 ekstra p-plasser rett sør for ny garasje (totalt 4 p-plasser for tomannsbolig) -->
    <polygon points="{poly_str(ny_park_pts)}" fill="#38bdf8" fill-opacity="0.22" stroke="#0369a1" stroke-width="1.6" stroke-dasharray="4,3"/>

    <!-- 6. Støttemur mellom øvre nivå (+25,5) og nedre utkjøringsnivå (+23,3–24,5) -->
    <path d="{path_d(mur_pts)}" fill="none" stroke="#78350f" stroke-width="5.5" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="{path_d(mur_pts)}" fill="none" stroke="#fef3c7" stroke-width="1.5" stroke-dasharray="4,4"/>
    <path d="{path_d(mur_south_pts)}" fill="none" stroke="#78350f" stroke-width="5.0" stroke-linecap="round"/>
    <path d="{path_d(mur_south_pts)}" fill="none" stroke="#fef3c7" stroke-width="1.4" stroke-dasharray="4,4"/>

    <!-- 7. Variant 1C ny vestgrense (rød stiplet — 1,05 m fra Ny garasje) -->
    <line x1="{NW_NEW[0]:.1f}" y1="{NW_NEW[1]:.1f}" x2="{SW_NEW[0]:.1f}" y2="{SW_NEW[1]:.1f}"
          stroke="#dc2626" stroke-width="3.6" stroke-dasharray="10,5"/>
    <circle cx="{NW_NEW[0]:.1f}" cy="{NW_NEW[1]:.1f}" r="5.5" fill="#dc2626" stroke="#ffffff" stroke-width="2"/>
    <circle cx="{NE[0]:.1f}" cy="{NE[1]:.1f}" r="6.0" fill="#059669" stroke="#ffffff" stroke-width="2"/>

    <!-- 8. Kjellerport NØ markering på østveggen til Ny garasje -->
    <line x1="{kjeller_port_n[0]:.1f}" y1="{kjeller_port_n[1]:.1f}" x2="{kjeller_port_s[0]:.1f}" y2="{kjeller_port_s[1]:.1f}"
          stroke="#dc2626" stroke-width="6.0"/>

    <!-- 9. Kjørepiler: Kjellerport NØ ut + Ny garasje ut + M6 vestporter (øvre nivå) -->
    <path d="{path_d(kjeller_arrow_pts)}" fill="none" stroke="#b45309" stroke-width="3.2" stroke-linejoin="round" marker-end="url(#arr-amber)"/>
    <path d="{path_d(ny_gar_arrow_pts)}" fill="none" stroke="#0369a1" stroke-width="2.8" stroke-linejoin="round" marker-end="url(#arr-sky)"/>
    <path d="{path_d(vest_port_arrow1)}" fill="none" stroke="#334155" stroke-width="2.4" stroke-dasharray="4,3" marker-end="url(#arr-slate)"/>
    <path d="{path_d(vest_port_arrow2)}" fill="none" stroke="#334155" stroke-width="2.4" stroke-dasharray="4,3" marker-end="url(#arr-slate)"/>

    <!-- 10. Trinnfri gangvei fra M6 norddør (vest for Ny garasje -> felles munning) -->
    <path d="{path_d(gang_pts)}" fill="none" stroke="#0f766e" stroke-width="4.4" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="9,5" marker-end="url(#arr-teal)"/>
    <!-- Inngangsdør M6 nordvegg markør -->
    <circle cx="{H_INNG[0]:.1f}" cy="{H_INNG[1]:.1f}" r="6.5" fill="#0f766e" stroke="#ffffff" stroke-width="2.2"/>
    <!-- Valgfri utvendig trappesnarvei SØ for Ny garasje -->
    <line x1="{trapp_p1[0]:.1f}" y1="{trapp_p1[1]:.1f}" x2="{trapp_p2[0]:.1f}" y2="{trapp_p2[1]:.1f}"
          stroke="#0f766e" stroke-width="6.5" stroke-dasharray="2.5,2.5"/>

    <!-- 11. Eksakte kotepunkter (Kartverket DTM1, NN2000) langs Myrteveien og i anlegget -->
    {kote_badge(road_pt(-5.0, -2.5), "+25,8", bg="#f1f5f9", stroke="#334155", fg="#0f172a", dy=-15)}
    {kote_badge(road_pt(0.0, -2.5), "+25,2", bg="#fef2f2", stroke="#dc2626", fg="#991b1b", dy=-15)}
    {kote_badge(road_pt(8.0, -2.5), "+24,4", bg="#fef3c7", stroke="#b45309", fg="#78350f", dy=-15)}
    {kote_badge(road_pt(15.0, -2.5), "+23,7", bg="#e0f2fe", stroke="#0369a1", fg="#0c4a6e", dy=-15)}
    {kote_badge(road_pt(20.0, -2.5), "+23,1", bg="#ecfdf5", stroke="#047857", fg="#064e3b", dy=-15)}

    <!-- Koter ved M6 norddør, vestporter, kjellerport og ny garasje -->
    {kote_badge(H_INNG, "Dør +26,1 / T +25,7", bg="#ccfbf1", stroke="#0f766e", fg="#134e4a", dx=-72, dy=-12)}
    {kote_badge(GAR_SW - 1.5*PX*n_east, "+25,5", bg="#f1f5f9", stroke="#334155", fg="#0f172a", dx=-28, dy=0)}
    {kote_badge(kjeller_mid, "Kjeller +23,25", bg="#fee2e2", stroke="#dc2626", fg="#991b1b", dx=54, dy=14)}
    {kote_badge(ny_gar_mid, "Ny garasje +23,8", bg="#e0f2fe", stroke="#0369a1", fg="#0c4a6e", dx=0, dy=0)}
  </g>

  <!-- ===================== VENSTRE MARG (X = 16..278) ===================== -->
  <!-- V1: Øvre nivå Ny garasje + Kjellerport NØ -->
  <polyline points="276,285 315,285 {GAR_NW[0] - 8:.1f},{GAR_NW[1]:.1f}" fill="none" stroke="#334155" stroke-width="2.0" marker-end="url(#arr-slate)"/>
  <g transform="translate(18, 108)">
    <rect width="258" height="202" rx="7" fill="#ffffff" stroke="#334155" stroke-width="1.8"/>
    <text x="12" y="21" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.6" fill="#0f172a">1. NY GARASJE M6 (2 NIVÅER)</text>
    <text x="12" y="39" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.5" fill="#1e293b">Øvre plan (porter mot VEST):</text>
    <text x="12" y="54" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#334155">• Gulv kote +25,60 til +25,85</text>
    <text x="12" y="68" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#334155">• Innkjøring fra M6 gårdsplass</text>
    <text x="12" y="82" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#334155">• Portrom mot hus fullt bevart</text>
    <line x1="12" y1="92" x2="246" y2="92" stroke="#e2e8f0" stroke-width="1.2"/>
    <text x="12" y="109" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.5" fill="#b91c1c">Kjellerplan (port mot NØ):</text>
    <text x="12" y="124" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#334155">• Gulv ca. +23,25 (2,35 m takhøyde)</text>
    <text x="12" y="138" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#334155">• NB! Grense kun 1,05 m øst:</text>
    <text x="12" y="152" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.0" fill="#991b1b">  → Kjøring ut over grensen krever</text>
    <text x="12" y="165" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.0" fill="#991b1b">    tinglyst felles snutun/kjørerett!</text>
    <text x="12" y="182" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="8.9" fill="#475569">• Ca. 1,5 m fjelluttak (dren/sluk!)</text>
    <text x="12" y="194" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="8.9" fill="#475569">• Brannskille EI 30/60 på østvegg</text>
  </g>

  <!-- V2: Gangvei fra inngangsdør nordvegg M6 -->
  <polyline points="276,470 340,470 {gang_mid[0] - 8:.1f},{gang_mid[1]:.1f}" fill="none" stroke="#0f766e" stroke-width="2.2" marker-end="url(#arr-teal)"/>
  <g transform="translate(18, 332)">
    <rect width="258" height="196" rx="7" fill="#f0fdfa" stroke="#0f766e" stroke-width="1.8"/>
    <text x="12" y="21" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.4" fill="#134e4a">2. GANGVEI FRA NORDDØR (M6)</text>
    <text x="12" y="39" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.2" fill="#0f766e">Trinnfri hovedrute (vestsiden):</text>
    <text x="12" y="54" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Fra norddør (+25,7 / platting +26,1)</text>
    <text x="12" y="68" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Gjennom portrommet vest for</text>
    <text x="12" y="81" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">  Ny garasje (+25,5) rundt NV-hjørne</text>
    <text x="12" y="95" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Slakt ned til felles munning (+24,6)</text>
    <text x="12" y="111" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.3" fill="#047857">• ~27 m lengde • ~4 % fall (1:25) [OK]</text>
    <text x="12" y="126" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#334155">• Helt adskilt fra biler i kjeller!</text>
    <line x1="12" y1="136" x2="246" y2="136" stroke="#99f6e4" stroke-width="1.2"/>
    <text x="12" y="152" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.2" fill="#0f766e">Snarvei (utvendig trapp SØ):</text>
    <text x="12" y="167" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#334155">• 10–12 trinn ved støttemur SØ</text>
    <text x="12" y="180" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#334155">  gir rask tilgang rett til nedre tun</text>
  </g>

  <!-- V3: Kompakt tegnforklaring i venstre marg -->
  <g transform="translate(18, 548)">
    <rect width="258" height="244" rx="7" fill="#ffffff" stroke="#0f172a" stroke-width="1.6"/>
    <text x="12" y="21" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.6" fill="#0f172a">TEGNFORKLARING</text>

    <rect x="12" y="33" width="22" height="13" fill="#f59e0b" fill-opacity="0.38" stroke="#b45309" stroke-width="1.8"/>
    <text x="42" y="43" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.1" fill="#1e293b">Felles nedre utkjørsel &amp; snutun</text>

    <rect x="12" y="56" width="22" height="13" fill="#0ea5e9" fill-opacity="0.40" stroke="#0369a1" stroke-width="1.8"/>
    <text x="42" y="66" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.1" fill="#1e293b">Ny garasje/carport (≤ 50 m²)</text>

    <rect x="12" y="79" width="22" height="13" fill="#38bdf8" fill-opacity="0.25" stroke="#0369a1" stroke-width="1.4" stroke-dasharray="3,2"/>
    <text x="42" y="89" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.1" fill="#1e293b">2 ekstra p-plasser (4 tot. 2-mb.)</text>

    <line x1="12" y1="109" x2="34" y2="109" stroke="#0f766e" stroke-width="3.6" stroke-dasharray="6,3"/>
    <text x="42" y="113" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.1" fill="#1e293b">Trinnfri gangvei fra M6 norddør</text>

    <line x1="12" y1="132" x2="34" y2="132" stroke="#78350f" stroke-width="4.5"/>
    <text x="42" y="136" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.1" fill="#1e293b">Støttemur (øvre / nedre nivå)</text>

    <line x1="12" y1="155" x2="34" y2="155" stroke="#dc2626" stroke-width="3.2" stroke-dasharray="6,3"/>
    <text x="42" y="159" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.1" fill="#1e293b">Ny tomtegrense Var. 1C (1,05 m)</text>

    <line x1="12" y1="178" x2="34" y2="178" stroke="#dc2626" stroke-width="5.5"/>
    <text x="42" y="182" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.1" fill="#1e293b">Kjellerport NØ (Ny garasje M6)</text>

    <rect x="12" y="196" width="22" height="13" fill="#3b82f6" fill-opacity="0.16" stroke="#1d4ed8" stroke-width="1.5" stroke-dasharray="3,2"/>
    <text x="42" y="206" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.1" fill="#1e293b">Byggefelt ny tomt (259 m² urørt)</text>

    <text x="12" y="232" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="8.6" fill="#64748b">Koter: Kartverket DTM1 (NN2000)</text>
  </g>

  <!-- ===================== HØYRE MARG (X = 1322..1582) ===================== -->
  <!-- H1: Felles avkjørsel forskjøvet østover -->
  <polyline points="1322,190 1280,190 {avk_mid[0] + 10:.1f},{avk_mid[1]:.1f}" fill="none" stroke="#b45309" stroke-width="2.2" marker-end="url(#arr-amber)"/>
  <g transform="translate(1322, 108)">
    <rect width="260" height="186" rx="7" fill="#fffbeb" stroke="#d97706" stroke-width="1.8"/>
    <text x="12" y="21" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.4" fill="#92400e">3. FELLES AVKJØRSEL (ØST-FORSKYV.)</text>
    <text x="12" y="39" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.3" fill="#78350f">Hvorfor flytte den 6–10 m østover?</text>
    <text x="12" y="54" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Myrteveien faller 2,2 m østover!</text>
    <text x="12" y="68" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Ved NV_ny (+25,2) blir kjellerrampe</text>
    <text x="12" y="81" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="9.1" fill="#b91c1c">  ~18 % (for bratt + overvannsgrop!)</text>
    <text x="12" y="96" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Ved e = +5,5–10,8 m (+24,15–24,65):</text>
    <text x="12" y="110" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.2" fill="#047857">  → Slak ~7,5 % (1:13) ut fra kjeller [OK]</text>
    <text x="12" y="125" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Siste 4 m mot vei: maks 5 % (1:20)</text>
    <text x="12" y="140" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Kun 1 avkjørsel (kommunen liker!)</text>
    <text x="12" y="155" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Sparer asfalt &amp; dobbel snuplass</text>
    <text x="12" y="172" font-family="DejaVu Sans, Arial, sans-serif" font-weight="600" font-size="8.9" fill="#92400e">• Tinglyses: kjørerett, brøyting, p-forbud</text>
  </g>

  <!-- H2: Ny garasje/carport på fradelt tomt -->
  <polyline points="1322,380 1285,380 {ny_gar_pts[1][0] + 4:.1f},{ny_gar_pts[1][1] + 24:.1f}" fill="none" stroke="#0369a1" stroke-width="2.2" marker-end="url(#arr-sky)"/>
  <g transform="translate(1322, 314)">
    <rect width="260" height="206" rx="7" fill="#f0f9ff" stroke="#0284c7" stroke-width="1.8"/>
    <text x="12" y="21" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.4" fill="#0c4a6e">4. GARASJE / CARPORT NY TOMT</text>
    <text x="12" y="39" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.3" fill="#0369a1">Plassert i forsonen (kote +23,8):</text>
    <text x="12" y="54" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Parallelt m/Myrteveien, 2,5 m fra vei</text>
    <text x="12" y="68" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">  (KPA tillater ≥ 2,0 m ved parallell port!)</text>
    <text x="12" y="83" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Ca. 6,8 × 5,8 m = ~39 m² (≤ 50 m²)</text>
    <text x="12" y="98" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Innkjøring fra VEST rett fra felles tun</text>
    <text x="12" y="113" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• + 2 åpne p-plasser rett sør = 4 p-pl.</text>
    <text x="12" y="128" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.2" fill="#047857">• Spiser 0 m² av 259 m² byggefelt! [OK]</text>
    <text x="12" y="143" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Nesten BYA-nøytralt (erstatter p-BYA)</text>
    <text x="12" y="158" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.1" fill="#1e293b">• Skjermer ny bolig mot støy/innsyn</text>
    <text x="12" y="173" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#475569">• 1,8 m fra østgrense (Myrteveien 2)</text>
    <text x="12" y="188" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#475569">• Ca. 10 m til M6-garasje (null brannkonfl.)</text>
  </g>

  <!-- H3: Viktig vurdering / trade-offs -->
  <g transform="translate(1322, 540)">
    <rect width="260" height="252" rx="7" fill="#fef2f2" stroke="#dc2626" stroke-width="1.6"/>
    <text x="12" y="21" font-family="DejaVu Sans, Arial, sans-serif" font-weight="800" font-size="10.4" fill="#991b1b">5. VIKTIG Å VURDERE FØR VALG</text>
    <text x="12" y="40" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.2" fill="#7f1d1d">A) Kjellerport over ny tomtegrense:</text>
    <text x="12" y="54" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#1e293b">• Med Var. 1C-grense 1,05 m fra garasje</text>
    <text x="12" y="67" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#1e293b">  må felles snutun (~6×8 m) tinglyses</text>
    <text x="12" y="80" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#1e293b">  som felles kjøreareal i NV av ny tomt.</text>
    <text x="12" y="98" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.2" fill="#7f1d1d">B) Alternativ port i NORDGAVLEN:</text>
    <text x="12" y="112" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#1e293b">• Legges kjellerporten i nordøst-hjørnet</text>
    <text x="12" y="125" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#1e293b">  av nordgavlen (i stedet for østveggen),</text>
    <text x="12" y="138" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#1e293b">  kjører du ut på egen grunn først!</text>
    <text x="12" y="156" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.2" fill="#7f1d1d">C) Fjell &amp; overvann (geoteknikk):</text>
    <text x="12" y="170" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#1e293b">• Fjell på 0,2–1,5 m → kjeller (+23,25)</text>
    <text x="12" y="183" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#1e293b">  krever sprengning + god overvannsrenne</text>
    <text x="12" y="196" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#1e293b">  foran port (sluk mot 2014 OV-kum!).</text>
    <text x="12" y="214" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="9.2" fill="#047857">D) Tomteverdi ved eksternt salg:</text>
    <text x="12" y="228" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#1e293b">• Felles innkjørsel sparer ~150–250 k</text>
    <text x="12" y="241" font-family="DejaVu Sans, Arial, sans-serif" font-weight="500" font-size="9.0" fill="#1e293b">  i vei/asfalt — men krever ryddig servitutt.</text>
  </g>

  <!-- ===================== NEDRE DEL: TO HØYDEPROFILER ===================== -->
  {profile_a_svg}
  {profile_b_svg}
</svg>
'''

svg_path = os.path.join(assets_dir, "skisse_felles_utkjoring_m6.svg")
overlay_png = "/tmp/felles_utkjoring_overlay.png"
png_path = os.path.join(assets_dir, "skisse_felles_utkjoring_m6.png")

with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg)

res = subprocess.run(
    ["inkscape", svg_path, "-o", overlay_png, "--export-area-page", f"--export-width={W * 2}"],
    capture_output=True, text=True
)
if res.returncode != 0:
    raise RuntimeError(f"Inkscape failed: {res.stderr}")

# Kompositt: rent lysgrått bakgrunnslerret + arkitektplan kun i kartfeltet + SVG-lag over
canvas = Image.new("RGBA", (W * 2, H * 2), (248, 250, 252, 255))
bg_up = crop_im.resize((MAP_W * 2, MAP_H * 2), Image.Resampling.LANCZOS)
canvas.paste(bg_up, (MAP_X0 * 2, MAP_Y0 * 2))

ov_im = Image.open(overlay_png).convert("RGBA")
if ov_im.size != canvas.size:
    ov_im = ov_im.resize(canvas.size, Image.Resampling.LANCZOS)
composed = Image.alpha_composite(canvas, ov_im).convert("RGB")
composed.save(png_path, format="PNG", optimize=True)
os.remove(overlay_png)
print(f"Saved: {png_path} ({composed.size[0]}x{composed.size[1]})")
