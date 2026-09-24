import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from PIL import Image
import numpy as np

# Load original situasjonsplan
im = Image.open('m6/assets/images/situasjonsplan_render.png')

# Create figure
fig, ax = plt.subplots(figsize=(18, 18), dpi=200)
ax.imshow(im)

# Define crop limits to focus on the work area (from Myrteveien to south of house)
ax.set_xlim(520, 1420)
ax.set_ylim(1120, 220)  # Inverted Y for image coordinates

# -------------------------------------------------------------
# OVERLAY MEASURES DIRECTLY ON TOP OF SITUASJONSPLAN
# -------------------------------------------------------------

# 1. UNDERBYGGET KJELLER UNDER NYTT INNGANGSPARTI
# The new addition fills between the tverrfløy and the north wall (approx x=870-938, y=705-793)
inngang_pts = np.array([
    [885, 742],
    [938, 725],
    [923, 793],  # Indre hjørne mot tverrfløy
    [888, 804]   # Nordvest-hjørne på tverrfløy
])
inngang_poly = Polygon(inngang_pts, closed=True, facecolor="#ea580c", edgecolor="#9a3412",
                       lw=3, alpha=0.65, hatch="//", zorder=5, label="1. Underbygget kjeller (Inngangsparti ~9 m², dybde 2.7m)")
ax.add_patch(inngang_poly)

ax.annotate(
    "1. NYTT INNGANGSPARTI\n(Underbygget full kjeller\n~9 m², dybde 2.75 m)",
    xy=(895, 760), xytext=(680, 770),
    arrowprops=dict(arrowstyle="->", color="#c2410c", lw=2, connectionstyle="arc3,rad=-0.15"),
    fontsize=9.5, weight="bold", color="#7c2d12",
    bbox=dict(boxstyle="round,pad=0.4", fc="#ffedd5", ec="#ea580c", lw=1.5),
    zorder=10
)

# 2. NY UTVENDIG KJELLERNEDGANG
kjeller_trapp_pts = np.array([
    [925, 688],
    [985, 668],
    [995, 698],
    [935, 718]
])
trapp_poly = Polygon(kjeller_trapp_pts, closed=True, facecolor="#38bdf8", edgecolor="#0284c7",
                     lw=2.5, alpha=0.7, zorder=5, label="2. Ny kjellernedgang (C+24,4 m/trappesluk & smelterør)")
ax.add_patch(trapp_poly)

# Trappetrinn
for t in [0.2, 0.4, 0.6, 0.8]:
    p1 = [925 + (985 - 925) * t, 688 + (668 - 688) * t]
    p2 = [935 + (995 - 935) * t, 718 + (698 - 718) * t]
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#0369a1", lw=1.5, zorder=6)

# Sluk i repos foran dør
ax.plot(932, 710, marker="s", markersize=7, color="#0369a1", zorder=7)

ax.annotate(
    "2. KJELLERNEDGANG\n(Støpt trapp til C+24,4\nm/sluk & PEX-smelterør)",
    xy=(960, 685), xytext=(780, 620),
    arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2, connectionstyle="arc3,rad=-0.1"),
    fontsize=9.5, weight="bold", color="#075985",
    bbox=dict(boxstyle="round,pad=0.4", fc="#e0f2fe", ec="#0284c7", lw=1.5),
    zorder=10
)

# 3. RE-DRENERING NORDVEGG (DYBDE 2.75M)
dren_x = [885, 938, 1005, 1045]
dren_y = [742, 725, 703, 690]
ax.plot(dren_x, dren_y, color="#dc2626", lw=5, solid_capstyle='round', zorder=6,
        label="3. Ny drensledning (dybde 2.7m, 110mm drensrør i pukk/duk)")

# Knotted membrane / XPS outline
ax.plot([938, 1045], [722, 687], color="#f97316", lw=3, ls="--", zorder=5, label="Platon knotteplast + 100-150mm XPS")

# Rørgjennomføring fra kjeller (#96)
ax.plot([955, 955], [755, 718], color="#16a34a", lw=4, zorder=7)
ax.plot(955, 718, marker="o", markersize=9, color="#16a34a", zorder=8)
ax.annotate(
    "RØR FRA KJELLER (#96)\n(Topp 246 cm kobles på drensnett)",
    xy=(955, 718), xytext=(1050, 750),
    arrowprops=dict(arrowstyle="->", color="#15803d", lw=2, connectionstyle="arc3,rad=0.15"),
    fontsize=9, weight="bold", color="#14532d",
    bbox=dict(boxstyle="round,pad=0.4", fc="#dcfce7", ec="#16a34a", lw=1.5),
    zorder=10
)

# Overvannskum & stenkiste
ax.plot(1055, 692, marker="o", markersize=13, color="#2563eb", zorder=8)
ax.annotate(
    "OVERVANNSKUM\n(Vannstand 253cm / tilkobling LOD)",
    xy=(1055, 692), xytext=(1160, 670),
    arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=2),
    fontsize=9, weight="bold", color="#1e40af",
    bbox=dict(boxstyle="round,pad=0.4", fc="#eff6ff", ec="#2563eb", lw=1.5),
    zorder=10
)

# -------------------------------------------------------------
# 4. VANNFORSYNING: FRA TROLLHEGGVEIEN VIA STOPPEKRAN VED 13.3M
# -------------------------------------------------------------
# Eksisterende stikkledning fra Trollheggveien (langs 13,3m-målelinjen)
ax.plot([680, 786], [945, 894], color="#0284c7", lw=3, ls=":", zorder=5)
ax.text(710, 935, "Eksist. vann fra Trollheggveien", fontsize=8, color="#0369a1", rotation=-24, weight="bold")

# Stoppekran ved 13,3 m-målet
ax.plot(786, 894, marker="o", markersize=12, color="#0284c7", zorder=9)
ax.plot(786, 894, marker="X", markersize=8, color="#ffffff", zorder=10)

ax.annotate(
    "EKSISTERENDE STOPPEKRAN\n(Ved 13,3m-målelinjen)",
    xy=(786, 894), xytext=(570, 890),
    arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2),
    fontsize=9.5, weight="bold", color="#0c4a6e",
    bbox=dict(boxstyle="round,pad=0.4", fc="#e0f2fe", ec="#0284c7", lw=1.5),
    zorder=11
)

# Ny 32mm vannledning fra stoppekran nordover til indre hjørne nord-vest
va_new_pts = [
    [786, 894],   # Stoppekran ved 13,3m
    [810, 860],
    [840, 830],
    [875, 812],
    [923, 793]    # Indre hjørne NV der vestvegg møter nordvegg på tverrfløy
]
va_new_x = [p[0] for p in va_new_pts]
va_new_y = [p[1] for p in va_new_pts]
ax.plot(va_new_x, va_new_y, color="#0284c7", lw=4.5, ls="-", zorder=7,
        label="4. Ny 32mm vannledning (fra stoppekran til indre hjørne NV)")

# Inntakspunkt i indre hjørne
ax.plot(923, 793, marker="D", markersize=11, color="#0369a1", zorder=9)
ax.annotate(
    "4. INNVENDIG VANNINNTAK\nIndre hjørne nord-vest\n(Vestvegg møter nordvegg på tverrfløy)\nInnstøpt vanntett Doyma-hylse",
    xy=(923, 793), xytext=(620, 835),
    arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2, connectionstyle="arc3,rad=-0.1"),
    fontsize=9.5, weight="bold", color="#0c4a6e",
    bbox=dict(boxstyle="round,pad=0.4", fc="#f0f9ff", ec="#0284c7", lw=1.5),
    zorder=11
)

# 5. NY VINKLET INNKJØRING & BÆRELAG (PUKK 0-63)
driveway_pts = np.array([
    [885, 290],
    [960, 280],
    [970, 480],
    [1010, 640],
    [930, 660],
    [870, 480]
])
drive_poly = Polygon(driveway_pts, closed=True, facecolor="#94a3b8", edgecolor="#475569",
                     lw=2, alpha=0.45, hatch="..", zorder=3, label="5. Ny innkjøring (Pukk 0-63 bærelag for betong/kranbil)")
ax.add_patch(drive_poly)

ax.annotate(
    "5. NY INNKJØRING / ANLEGGSVEI\n(Forsterket bærelag pukk 0-63 mm\ndim. for betongbiler & kran)",
    xy=(940, 450), xytext=(1040, 420),
    arrowprops=dict(arrowstyle="->", color="#475569", lw=1.8),
    fontsize=9.5, weight="bold", color="#1e293b",
    bbox=dict(boxstyle="round,pad=0.4", fc="#f1f5f9", ec="#64748b", lw=1.5),
    zorder=10
)

# 6. TREKKERØR & INFRASTRUKTUR I GRØFT
ax.plot([920, 840, 780], [670, 640, 600], color="#10b981", lw=3.5, ls="--", zorder=6,
        label="6. Trekkerør (Ø110mm ny garasje / Ø50mm snøsmelte)")

# 7. RIGG & LOGISTIKK
# Arbeidssone gravemaskin
ax.plot(910, 630, marker="^", markersize=14, color="#eab308", zorder=8)
ax.text(910, 615, "GRAVEMASKIN (8-15t)\nArbeidssone", fontsize=8.5, weight="bold", color="#854d0e", ha="center", zorder=10)

# Massedeponi (mellomlagring rene steinmasser)
deponi_pts = np.array([
    [1010, 500],
    [1130, 470],
    [1150, 560],
    [1030, 590]
])
deponi_poly = Polygon(deponi_pts, closed=True, facecolor="#fef08a", edgecolor="#ca8a04",
                      lw=1.8, ls="--", alpha=0.6, zorder=3)
ax.add_patch(deponi_poly)
ax.text(1080, 530, "Mellomlagring\nrene steinmasser\n(Gjenbruk)", fontsize=9, weight="bold", color="#713f12", ha="center", zorder=4)

# Planering nord-vest
planering_pts = np.array([
    [640, 480],
    [760, 450],
    [740, 360],
    [620, 390]
])
planering_poly = Polygon(planering_pts, closed=True, facecolor="#bbf7d0", edgecolor="#22c55e",
                         lw=1.5, ls=":", alpha=0.5, zorder=2)
ax.add_patch(planering_poly)
ax.text(690, 420, "Terrengplanering\nNord-Vest", fontsize=8.5, weight="bold", color="#166534", ha="center", zorder=4)

# -------------------------------------------------------------
# TITLE BANNER & LEGEND
# -------------------------------------------------------------
title_box = dict(boxstyle="square,pad=0.6", fc="#ffffff", ec="#0f172a", lw=2)
title_str = (
    "MYRTEVEIEN 6 — ANLEGGSOMRÅDE & PLANSKISSE FOR GRUNNARBEIDER NORD\n"
    "Prosjekt: M6 Totalrehabilitering | Tiltakshaver: Magnus Kirø | Gnr 140 / Bnr 371 | Tønsberg kommune\n"
    "Bakgrunn: Offisiell Situasjonsplan A-001 (KB Arkitekter AS) | Referanse: GitHub Issue #92"
)
ax.text(970, 255, title_str, fontsize=10.5, weight="bold", color="#0f172a", ha="center", bbox=title_box, zorder=12)

# Custom Legend
ax.legend(loc="lower left", bbox_to_anchor=(0.02, 0.02), fontsize=9, framealpha=0.96,
          facecolor="#ffffff", edgecolor="#0f172a", fancybox=False)

ax.axis("off")
plt.tight_layout()

# Save image
out_path_repo = "m6/assets/images/planskisse_anleggsomraade_nord.png"
out_path_brain = "C:/Users/magkir/.gemini/antigravity/brain/773222c6-8706-4aad-83b9-5ad2ac2dc3ae/planskisse_anleggsomraade_nord.png"

plt.savefig(out_path_repo, dpi=200, bbox_inches='tight')
plt.savefig(out_path_brain, dpi=200, bbox_inches='tight')
print("Successfully generated refined overlay with updated water line!")
