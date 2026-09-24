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

# Focus on the work area
ax.set_xlim(520, 1420)
ax.set_ylim(1120, 220)

# -------------------------------------------------------------
# 1. KJELLERTRAPP (NØYAKTIG TILPASSET CAD-TEGNET TRAPP)
# -------------------------------------------------------------
# Trinnløp fra terreng (øst) ned til repos under platting (vest)
stair_pts = np.array([
    [966, 695],
    [1015, 679],
    [1019, 693],
    [970, 709]
])
trapp_poly = Polygon(stair_pts, closed=True, facecolor="#38bdf8", edgecolor="#0284c7",
                     lw=2, alpha=0.85, zorder=6, label="2. Kjellertrapp (støpt betong m/PEX-smelterør)")
ax.add_patch(trapp_poly)

# Støttemur / vangemur på utsiden av trappen
vangemur_pts = np.array([
    [965, 686],
    [1014, 672],
    [1015, 679],
    [966, 695]
])
vange_poly = Polygon(vangemur_pts, closed=True, facecolor="#94a3b8", edgecolor="#475569",
                     lw=1.5, alpha=0.85, zorder=6)
ax.add_patch(vange_poly)

# Trinnlinjer i trappen
for t in np.linspace(0.12, 0.88, 8):
    p1 = [966 + (1015 - 966) * t, 695 + (679 - 695) * t]
    p2 = [970 + (1019 - 970) * t, 709 + (693 - 709) * t]
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#0369a1", lw=1.2, zorder=7)

# -------------------------------------------------------------
# 2. PLATTING FOR INNGANGSPARTI (PÅ NORDVEGGEN I INNTEGNET OMRISS)
# -------------------------------------------------------------
# Dekke 1. etasje som danner tak/overbygg over kjellerdør, utebod og el-skap
platting_outer = np.array([
    [891, 694],
    [955, 673],
    [965, 671],
    [967, 695],
    [970, 709],
    [905, 726]
])
platting_poly = Polygon(platting_outer, closed=True, facecolor="#fdba74", edgecolor="#ea580c",
                        lw=2.5, alpha=0.45, hatch="//", zorder=5,
                        label="1. Ny platting inngangsparti 1. etg (overbygg/tak over kjellerdør & bod)")
ax.add_patch(platting_poly)

# Repos foran ny kjellerdør (under taket, kote C+24.4)
repos_pts = np.array([
    [936, 705],
    [966, 695],
    [970, 709],
    [940, 719]
])
repos_poly = Polygon(repos_pts, closed=True, facecolor="#0284c7", edgecolor="#0369a1",
                     lw=1.8, alpha=0.75, zorder=7, label="   ↳ Repos v/ny kjellerdør m/trappesluk (under tak)")
ax.add_patch(repos_poly)

# Trappesluk i repos
ax.plot(952, 704, marker="s", markersize=7, color="#ffffff", markeredgecolor="#0284c7", markeredgewidth=2, zorder=9)

# Utebod og skap for strøm-inntak (under taket)
bod_pts = np.array([
    [896, 708],
    [936, 705],
    [940, 719],
    [905, 726]
])
bod_poly = Polygon(bod_pts, closed=True, facecolor="#f59e0b", edgecolor="#b45309",
                   lw=1.8, alpha=0.75, hatch="\\\\", zorder=7, label="   ↳ Utebod & skap for strøm-inntak (under tak)")
ax.add_patch(bod_poly)

# Annotering 1 & 2: Platting og under taket
ax.annotate(
    "1. NY PLATTING FOR INNGANGSPARTI (1. ETG)\n"
    "Danner overbygg/tak for kjellernedgang\n"
    "--------------------------------------------------\n"
    "UNDER TAKET (Kjellernivå C+24,4):\n"
    "• Ny kjellerdør inn til kjeller\n"
    "• Utebod & skap for strøm-inntak\n"
    "• Støpt repos foran dør m/trappesluk",
    xy=(930, 685), xytext=(630, 620),
    arrowprops=dict(arrowstyle="->", color="#c2410c", lw=2, connectionstyle="arc3,rad=-0.1"),
    fontsize=9.5, weight="bold", color="#7c2d12",
    bbox=dict(boxstyle="round,pad=0.5", fc="#ffedd5", ec="#ea580c", lw=1.8),
    zorder=12
)

# Annotering 3: Kjellertrapp
ax.annotate(
    "2. NY KJELLERTRAPP\n(Støpt trappeløp i inntegnet trasé\nm/PEX-smelterør i trinn ned til C+24,4)",
    xy=(995, 686), xytext=(1040, 620),
    arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2, connectionstyle="arc3,rad=0.1"),
    fontsize=9.5, weight="bold", color="#075985",
    bbox=dict(boxstyle="round,pad=0.4", fc="#e0f2fe", ec="#0284c7", lw=1.5),
    zorder=12
)

# -------------------------------------------------------------
# 3. RE-DRENERING FRA SYD-VEST HJØRNE AV TVERRFLØY TIL OVERVANNSKUM
# -------------------------------------------------------------
# Forlenget drenstrasé: starter i syd-vest hjørnet av tverrfløyen mot vest,
# følger vestvegg og nordvegg på tverrfløy, vestvegg hovedhus, og rundt platting & trapp.
dren_pts = [
    [880, 882],   # 1. Syd-vest hjørne av tverrfløy mot vest
    [858, 808],   # 2. Nord-vest hjørne av tverrfløy
    [912, 793],   # 3. Indre hjørne tverrfløy / vestvegg
    [898, 730],   # 4. Vestvegg mot inngangsplatting
    [885, 694],   # 5. Ytterkant inngangsplatting NV
    [955, 668],   # 6. Ytterkant inngangsplatting N
    [1015, 668],  # 7. Utkant kjellertrapp
    [1035, 678],  # 8. Nord-øst hjørne
    [1055, 692]   # 9. Overvannskum
]
dren_x = [p[0] for p in dren_pts]
dren_y = [p[1] for p in dren_pts]
ax.plot(dren_x, dren_y, color="#dc2626", lw=5, solid_capstyle='round', zorder=8,
        label="3. Ny drensledning (dybde 2.7m, fra SV-hjørne tverrfløy til kum)")

# Startpunkt i syd-vest hjørnet av tverrfløyen
ax.plot(880, 882, marker="s", markersize=9, color="#b91c1c", zorder=10)
ax.annotate(
    "START DRENSLEDNING\n(Syd-vest hjørne tverrfløy)",
    xy=(880, 882), xytext=(940, 915),
    arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.8),
    fontsize=8.5, weight="bold", color="#7f1d1d",
    bbox=dict(boxstyle="round,pad=0.3", fc="#fef2f2", ec="#dc2626", lw=1.2),
    zorder=12
)

# Knotted membrane / XPS langs murer fra SV-hjørne rundt hele nordveggen
membrane_pts = [
    [888, 875], [864, 808], [918, 795], [905, 726], [1030, 686]
]
mem_x = [p[0] for p in membrane_pts]
mem_y = [p[1] for p in membrane_pts]
ax.plot(mem_x, mem_y, color="#f97316", lw=3, ls="--", zorder=5, label="Platon knotteplast + 100-150mm XPS")

# Rørgjennomføring fra kjeller (#96)
# Grøft i kjeller ca. 1,5m fra nordveggen, føres under grunnmur og under ny kjellertrapp
ax.plot([960, 1015], [728, 710], color="#16a34a", lw=3.5, ls="-", zorder=7,
        label="Rør i grøft i kjeller (#96, ca. 1,5m fra nordvegg)")
ax.plot([992, 995], [717, 701], color="#16a34a", lw=4, zorder=7)
ax.plot([995, 999], [701, 675], color="#16a34a", lw=4, ls="--", zorder=8)  # Under kjellertrapp
ax.plot([999, 1000], [675, 668], color="#16a34a", lw=4, zorder=7)  # Tilkobling drensledning
ax.plot(995, 701, marker="o", markersize=6, color="#15803d", zorder=9)
ax.plot(1000, 668, marker="o", markersize=9, color="#16a34a", zorder=9)
ax.annotate(
    "RØR FRA KJELLER (#96)\n"
    "Grøft i kjeller ca. 1,5m fra nordvegg\n"
    "Føres under ny kjellertrapp (topp 246 cm)\n"
    "Kobles på drensnettet på utsiden",
    xy=(998, 680), xytext=(1060, 745),
    arrowprops=dict(arrowstyle="->", color="#15803d", lw=2, connectionstyle="arc3,rad=0.15"),
    fontsize=9, weight="bold", color="#14532d",
    bbox=dict(boxstyle="round,pad=0.4", fc="#dcfce7", ec="#16a34a", lw=1.5),
    zorder=12
)

# Overvannskum & stenkiste
ax.plot(1055, 692, marker="o", markersize=13, color="#2563eb", zorder=8)
ax.annotate(
    "OVERVANNSKUM\n(Vannstand 253cm / tilkobling LOD)",
    xy=(1055, 692), xytext=(1160, 680),
    arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=2),
    fontsize=9, weight="bold", color="#1e40af",
    bbox=dict(boxstyle="round,pad=0.4", fc="#eff6ff", ec="#2563eb", lw=1.5),
    zorder=12
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
    zorder=12
)

# Ny 32mm vannledning fra stoppekran nordover til indre hjørne nord-vest
va_new_pts = [
    [786, 894],   # Stoppekran ved 13,3m
    [810, 860],
    [840, 830],
    [875, 812],
    [918, 795]    # Indre hjørne NV der vestvegg møter nordvegg på tverrfløy
]
va_new_x = [p[0] for p in va_new_pts]
va_new_y = [p[1] for p in va_new_pts]
ax.plot(va_new_x, va_new_y, color="#0284c7", lw=4.5, ls="-", zorder=7,
        label="4. Ny 32mm vannledning (fra stoppekran til indre hjørne NV)")

# Inntakspunkt i indre hjørne
ax.plot(918, 795, marker="D", markersize=11, color="#0369a1", zorder=9)
ax.annotate(
    "4. INNVENDIG VANNINNTAK\nIndre hjørne nord-vest\n(Vestvegg møter tverrfløy)\nInnstøpt vanntett Doyma-hylse",
    xy=(918, 795), xytext=(610, 805),
    arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2, connectionstyle="arc3,rad=-0.1"),
    fontsize=9.5, weight="bold", color="#0c4a6e",
    bbox=dict(boxstyle="round,pad=0.4", fc="#f0f9ff", ec="#0284c7", lw=1.5),
    zorder=12
)

# -------------------------------------------------------------
# 5. NY VINKLET INNKJØRING & BÆRELAG (PUKK 0-63)
# -------------------------------------------------------------
driveway_pts = np.array([
    [885, 290],
    [960, 280],
    [970, 480],
    [1010, 630],
    [930, 650],
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
    zorder=11
)

# -------------------------------------------------------------
# 6. TREKKERØR & INFRASTRUKTUR I GRØFT
# -------------------------------------------------------------
ax.plot([900, 840, 780], [665, 640, 600], color="#10b981", lw=3.5, ls="--", zorder=6,
        label="6. Trekkerør (Ø110mm ny garasje / Ø50mm snøsmelte)")

# -------------------------------------------------------------
# 7. RIGG & LOGISTIKK
# -------------------------------------------------------------
# Arbeidssone gravemaskin
ax.plot(900, 600, marker="^", markersize=14, color="#eab308", zorder=8)
ax.text(900, 585, "GRAVEMASKIN (8-15t)\nArbeidssone", fontsize=8.5, weight="bold", color="#854d0e", ha="center", zorder=10)

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
ax.legend(loc="lower left", bbox_to_anchor=(0.02, 0.02), fontsize=8.8, framealpha=0.96,
          facecolor="#ffffff", edgecolor="#0f172a", fancybox=False)

ax.axis("off")
plt.tight_layout()

# Save image
out_path_repo = "m6/assets/images/planskisse_anleggsomraade_nord.png"
out_path_brain = "C:/Users/magkir/.gemini/antigravity/brain/773222c6-8706-4aad-83b9-5ad2ac2dc3ae/planskisse_anleggsomraade_nord.png"

plt.savefig(out_path_repo, dpi=200, bbox_inches='tight')
plt.savefig(out_path_brain, dpi=200, bbox_inches='tight')
print("Successfully generated refined overlay matching CAD stair & platting!")
