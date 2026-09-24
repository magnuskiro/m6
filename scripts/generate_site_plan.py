import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from PIL import Image
import numpy as np

# Find repo root / assets dir
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir) # m6 folder
assets_dir = os.path.join(repo_root, "assets", "images")

# Load original situasjonsplan
img_path = os.path.join(assets_dir, "situasjonsplan_render.png")
im = Image.open(img_path)

# Create figure
fig, ax = plt.subplots(figsize=(18, 18), dpi=200)
ax.imshow(im)

# Focus on the work area (expand top to show Myrteveien, lyktestolpe and title banner fully)
ax.set_xlim(520, 1420)
ax.set_ylim(1120, 90)

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

# Annotering 1: Platting og under taket
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

# Annotering 2: Kjellertrapp
ax.annotate(
    "2. NY KJELLERTRAPP\n(Støpt trappeløp i inntegnet trasé\nm/PEX-smelterør i trinn ned til C+24,4)",
    xy=(995, 686), xytext=(1040, 620),
    arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2, connectionstyle="arc3,rad=0.1"),
    fontsize=9.5, weight="bold", color="#075985",
    bbox=dict(boxstyle="round,pad=0.4", fc="#e0f2fe", ec="#0284c7", lw=1.5),
    zorder=12
)

# -------------------------------------------------------------
# 3. UTEPLASS KVELDSSOL MED UNDERBYGD KJELLER (NV-KROK)
# -------------------------------------------------------------
# Nook mellom tverrfløy og inngangsplatting: 2,0m mot vest x 2,5m mot nord
# Erstatning/vedlikehold av eksisterende inngangsparti
uteplass_pts = np.array([
    [918, 796],   # Indre hjørne tverrfløy / vestvegg
    [887, 805],   # 2,0m vest langs tverrfløy nordvegg
    [875, 766],   # Ytre NV-hjørne uteplass / kjeller
    [906, 757]    # 2,5m nord langs vestvegg
])
uteplass_poly = Polygon(uteplass_pts, closed=True, facecolor="#c084fc", edgecolor="#7e22ce",
                        lw=2.5, alpha=0.6, hatch="//", zorder=5,
                        label="3. Uteplass kveldssol m/underbygd kjeller (2,0x2,5m, vedlikehold inngang)")
ax.add_patch(uteplass_poly)

# Annotering 3: Uteplass & underbygd kjeller
ax.annotate(
    "3. UTEPLASS KVELDSSOL M/UNDERBYGD KJELLER\n"
    "Vedlikehold av nåværende inngangsparti (~5 m²)\n"
    "--------------------------------------------------\n"
    "• OVER: Uteplass kveldssol (2,0m x 2,5m, dekke C+26,8)\n"
    "• UNDER: Utgravd underbygd kjeller (bunn C+24,4)\n"
    "• Støpt plate, armerte betongvegger & vanntett dekke\n"
    "• Gjennomføring Doyma-hylse for nytt vanninntak",
    xy=(880, 775), xytext=(560, 715),
    arrowprops=dict(arrowstyle="->", color="#7e22ce", lw=2, connectionstyle="arc3,rad=-0.08"),
    fontsize=9.5, weight="bold", color="#581c87",
    bbox=dict(boxstyle="round,pad=0.45", fc="#faf5ff", ec="#a855f7", lw=1.8),
    zorder=12
)

# -------------------------------------------------------------
# 4. RE-DRENERING FRA SYD-VEST HJØRNE AV TVERRFLØY TIL OVERVANNSKUM
# -------------------------------------------------------------
# Forlenget drenstrasé: starter i syd-vest hjørnet av tverrfløyen mot vest,
# følger vestvegg og nordvegg på tverrfløy, rundt ny underbygd kjeller,
# langs vestvegg hovedhus, og rundt inngangsplatting & kjellertrapp til kum.
dren_pts = [
    [880, 882],   # 1. Syd-vest hjørne av tverrfløy mot vest
    [858, 808],   # 2. Nord-vest hjørne av tverrfløy
    [882, 803],   # 3. Ytterkant tverrfløy mot ny underbygd kjeller
    [870, 762],   # 4. Ytre NV-hjørne ny underbygd kjeller (2x2,5m)
    [903, 753],   # 5. Møter vestvegg hovedhus
    [898, 730],   # 6. Vestvegg mot inngangsplatting
    [885, 694],   # 7. Ytterkant inngangsplatting NV
    [955, 668],   # 8. Ytterkant inngangsplatting N
    [1015, 668],  # 9. Utkant kjellertrapp
    [1035, 678],  # 10. Nord-øst hjørne
    [1055, 692]   # 11. Overvannskum
]
dren_x = [p[0] for p in dren_pts]
dren_y = [p[1] for p in dren_pts]
ax.plot(dren_x, dren_y, color="#dc2626", lw=5, solid_capstyle='round', zorder=8,
        label="4. Ny drensledning (dybde 2.7m, fra SV-hjørne tverrfløy til kum)")

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

# Knotted membrane / XPS langs murer fra SV-hjørne rundt ny underbygd kjeller og hele nordveggen
membrane_pts = [
    [888, 875], [864, 808], [882, 803], [870, 762], [903, 753], [898, 730], [905, 726], [1030, 686]
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
# 5. VANNFORSYNING: FRA TROLLHEGGVEIEN VIA STOPPEKRAN VED 13.3M
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
        label="5. Ny 32mm vannledning (fra stoppekran til indre NV-inntak)")

# Inntakspunkt i underbygd kjeller / indre hjørne
ax.plot(918, 795, marker="D", markersize=11, color="#0369a1", zorder=9)
ax.annotate(
    "5. INNVENDIG VANNINNTAK\nUnderbygd kjeller / indre NV-hjørne\n(Vestvegg møter tverrfløy)\nInnstøpt vanntett Doyma-hylse",
    xy=(918, 795), xytext=(610, 815),
    arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2, connectionstyle="arc3,rad=-0.1"),
    fontsize=9.5, weight="bold", color="#0c4a6e",
    bbox=dict(boxstyle="round,pad=0.4", fc="#f0f9ff", ec="#0284c7", lw=1.5),
    zorder=12
)

# -------------------------------------------------------------
# 6. INNKJØRING (VESTGRENSE LANGS 27,7M, VIDER SEG UT TIL LYKTESTOLPEN MIDT PÅ NORDGRENSEN)
# -------------------------------------------------------------
driveway_pts = np.array([
    [885, 700],   # Vestkant ved inngangsplatting / fasade (møter 27,7m-linjen)
    [795, 333],   # Vestgrense ved Myrteveien (langs 27,7m målelinjen)
    [892, 310],   # Østgrense ved Myrteveien: Lyktestolpe ca. midt på tomtegrensen
    [1035, 675]   # Østkant ved kjellertrapp / husets nordøsthjørne (husets fulle bredde)
])
drive_poly = Polygon(driveway_pts, closed=True, facecolor="#94a3b8", edgecolor="#334155",
                     lw=2, alpha=0.45, hatch="..", zorder=3,
                     label="6. Innkjøring (vestgrense langs 27,7m, utvidet til lyktestolpe midt på grensen)")
ax.add_patch(drive_poly)

# Marker vestgrensen spesifikt langs 27,7m målelinjen
ax.plot([885, 795], [700, 333], color="#0284c7", lw=3.5, ls="-", zorder=6)

# Markering og annotering for lyktestolpe ca. midt på tomtegrensen mot nord (892, 310)
ax.plot(892, 310, marker="o", markersize=12, color="#2563eb", zorder=12)
ax.plot(892, 310, marker="*", markersize=8, color="#ffffff", zorder=13)
ax.annotate(
    "LYKTESTOLPE (Veglys)\n"
    "Ca. midt på tomtegrensen mot nord\n"
    "(Innkjøringen vider seg ut hit mot øst)",
    xy=(892, 310), xytext=(960, 240),
    arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=2, connectionstyle="arc3,rad=-0.1"),
    fontsize=9, weight="bold", color="#1e40af",
    bbox=dict(boxstyle="round,pad=0.4", fc="#eff6ff", ec="#2563eb", lw=1.5),
    zorder=14
)

# Annotering for innkjøring og vestgrense
ax.annotate(
    "6. INNKJØRING / FORSTERKET BÆRELAG (~200 m²)\n"
    "• Vestgrense følger målelinjen på 27,7 m\n"
    "• Åpning mot Myrteveien vider seg ut til lyktestolpen (892, 310)\n"
    "• Dekker husets fulle bredde ved fasaden (~9,5 m)\n"
    "• Forsterket bærelag pukk 0-63 mm (betongbiler/mobilkran)",
    xy=(840, 480), xytext=(550, 430),
    arrowprops=dict(arrowstyle="->", color="#334155", lw=2, connectionstyle="arc3,rad=0.1"),
    fontsize=9.5, weight="bold", color="#0f172a",
    bbox=dict(boxstyle="round,pad=0.45", fc="#f8fafc", ec="#475569", lw=1.8),
    zorder=12
)

# -------------------------------------------------------------
# 7. TREKKERØR & INFRASTRUKTUR I GRØFT
# -------------------------------------------------------------
ax.plot([900, 840, 780], [665, 640, 600], color="#10b981", lw=3.5, ls="--", zorder=6,
        label="7. Trekkerør (Ø110mm ny garasje / Ø50mm snøsmelte)")

# -------------------------------------------------------------
# 8. RIGG & LOGISTIKK
# -------------------------------------------------------------
# Arbeidssone gravemaskin
ax.plot(900, 600, marker="^", markersize=14, color="#eab308", zorder=8)
ax.text(900, 585, "GRAVEMASKIN (8-15t)\nArbeidssone", fontsize=8.5, weight="bold", color="#854d0e", ha="center", zorder=10)

# Massedeponi (mellomlagring rene steinmasser) - plassert i hagen øst for innkjøring
deponi_pts = np.array([
    [1160, 480],
    [1270, 450],
    [1290, 550],
    [1180, 580]
])
deponi_poly = Polygon(deponi_pts, closed=True, facecolor="#fef08a", edgecolor="#ca8a04",
                      lw=1.8, ls="--", alpha=0.6, zorder=3)
ax.add_patch(deponi_poly)
ax.text(1225, 515, "Mellomlagring\nrene steinmasser\n(Gjenbruk)", fontsize=9, weight="bold", color="#713f12", ha="center", zorder=4)

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
title_box = dict(boxstyle="square,pad=0.5", fc="#ffffff", ec="#0f172a", lw=1.8)
title_str = (
    "MYRTEVEIEN 6 — ANLEGGSOMRÅDE & PLANSKISSE FOR GRUNNARBEIDER NORD\n"
    "Prosjekt: M6 Totalrehabilitering | Tiltakshaver: Magnus Kirø | Gnr 140 / Bnr 371 | Tønsberg kommune\n"
    "Bakgrunn: Offisiell Situasjonsplan A-001 (KB Arkitekter AS) | Referanse: GitHub Issue #92"
)
ax.text(780, 125, title_str, fontsize=9.5, weight="bold", color="#0f172a", ha="center", bbox=title_box, zorder=15)

# Custom Legend
ax.legend(loc="lower left", bbox_to_anchor=(0.02, 0.02), fontsize=8.8, framealpha=0.96,
          facecolor="#ffffff", edgecolor="#0f172a", fancybox=False)

ax.axis("off")
plt.tight_layout()

# Save image
out_path_repo = os.path.join(assets_dir, "planskisse_anleggsomraade_nord.png")
out_path_brain = "C:/Users/magkir/.gemini/antigravity/brain/773222c6-8706-4aad-83b9-5ad2ac2dc3ae/planskisse_anleggsomraade_nord.png"

plt.savefig(out_path_repo, dpi=200, bbox_inches='tight')
plt.savefig(out_path_brain, dpi=200, bbox_inches='tight')
print("Successfully generated refined overlay matching CAD stair & platting!")
