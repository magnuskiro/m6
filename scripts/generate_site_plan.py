import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from PIL import Image
import numpy as np

# Find repo root / assets dir
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
assets_dir = os.path.join(repo_root, "assets", "images")

# Load original situasjonsplan
im = Image.open(os.path.join(assets_dir, "situasjonsplan_render.png"))

fig, ax = plt.subplots(figsize=(20, 20), dpi=200)
ax.imshow(im)
ax.set_xlim(480, 1420)
ax.set_ylim(1120, 80)

# -------------------------------------------------------------
# 1. KJELLERTRAPP (NØYAKTIG TILPASSET CAD-TEGNET TRAPP)
# -------------------------------------------------------------
stair_pts = np.array([[966, 695], [1015, 679], [1019, 693], [970, 709]])
ax.add_patch(Polygon(stair_pts, closed=True, facecolor="#38bdf8", edgecolor="#0284c7", lw=2, alpha=0.85, zorder=6, label="2. Kjellertrapp (støpt betong m/PEX-smelterør)"))
vange_pts = np.array([[965, 686], [1014, 672], [1015, 679], [966, 695]])
ax.add_patch(Polygon(vange_pts, closed=True, facecolor="#94a3b8", edgecolor="#475569", lw=1.5, alpha=0.85, zorder=6))
for t in np.linspace(0.12, 0.88, 8):
    p1 = [966 + (1015 - 966) * t, 695 + (679 - 695) * t]
    p2 = [970 + (1019 - 970) * t, 709 + (693 - 709) * t]
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#0369a1", lw=1.2, zorder=7)

# -------------------------------------------------------------
# 2. INNGANGSPLATTING & UNDERBYGD KJELLERNEDGANG (1. ETG, C+26,8)
# -------------------------------------------------------------
platting_outer = np.array([[891, 694], [955, 673], [965, 671], [967, 695], [970, 709], [905, 726]])
ax.add_patch(Polygon(platting_outer, closed=True, facecolor="#fdba74", edgecolor="#ea580c", lw=2.5, alpha=0.55, hatch="//", zorder=5, label="1. Ny platting inngangsparti 1. etg (overbygg tak over kjellerdør & bod)"))
repos_pts = np.array([[936, 705], [966, 695], [970, 709], [940, 719]])
ax.add_patch(Polygon(repos_pts, closed=True, facecolor="#0284c7", edgecolor="#0369a1", lw=1.8, alpha=0.75, zorder=7, label="   ↳ Repos v/ny kjellerdør m/trappesluk (under tak)"))
ax.plot(952, 704, marker="s", markersize=7, color="#ffffff", markeredgecolor="#0284c7", markeredgewidth=2, zorder=9)
bod_pts = np.array([[896, 708], [936, 705], [940, 719], [905, 726]])
ax.add_patch(Polygon(bod_pts, closed=True, facecolor="#f59e0b", edgecolor="#b45309", lw=1.8, alpha=0.75, hatch="\\\\", zorder=7, label="   ↳ Utebod & skap for strøm-inntak (under tak)"))

# Avtrapping fra platting ned til innkjøring (C+26.8 -> C+25.0)
for off in range(3):
    ax.plot([888 - off*4, 930 - off*4], [700 - off*5, 687 - off*5], color="#c2410c", lw=2.2, ls="-", zorder=6)

# -------------------------------------------------------------
# 3. LILLA SOLPLATTING M/BUE FRA HUSHJØRNE TVERRFLØY TIL HUSHJØRNE NORD-VEST
# -------------------------------------------------------------
p_tverr = np.array([849, 811])   # Hushjørnet på tverrfløyen mot vest
p_nw = np.array([894, 729])      # Hushjørnet nord-vest på hovedhuset
p_inner = np.array([918, 796])   # Indre hjørne hvor fasadene møtes

# Bue som buer ut mot nord-vest over hagen:
chord_vec = p_nw - p_tverr
chord_len = np.linalg.norm(chord_vec)
normal = np.array([-chord_vec[1], chord_vec[0]]) / chord_len
if normal[0] > 0:
    normal = -normal

bulge = 16.0
ctrl = (p_tverr + p_nw) / 2.0 + normal * bulge * 1.8
arc_pts = []
for t in np.linspace(0, 1, 20):
    pt = (1-t)**2 * p_tverr + 2*(1-t)*t * ctrl + t**2 * p_nw
    arc_pts.append(pt)

sol_poly_pts = [p_inner, p_tverr] + arc_pts + [p_nw]
sol_poly = Polygon(sol_poly_pts, closed=True, facecolor="#c084fc", edgecolor="#7e22ce",
                   lw=2.5, alpha=0.6, zorder=5, label="3. Solplatting kveldssol m/bue & underbygd kjeller (C+24,4 / C+26,8)")
ax.add_patch(sol_poly)

# Kryss (X) inne i plattingen
apex_pt = arc_pts[len(arc_pts)//2]
ax.plot([p_inner[0], apex_pt[0]], [p_inner[1], apex_pt[1]], color="#6b21a8", lw=2.2, zorder=6)
ax.plot([p_tverr[0], p_nw[0]], [p_tverr[1], p_nw[1]], color="#6b21a8", lw=2.2, zorder=6)

# -------------------------------------------------------------
# 4. GANGVEI / STI FRA TROLLHEGGVEIEN
# -------------------------------------------------------------
gangvei_pts = np.array([
    [540, 860],
    [640, 845],
    [740, 805],
    [815, 760],
    [855, 725],
    [890, 700]
])
ax.plot(gangvei_pts[:,0], gangvei_pts[:,1], color="#b45309", lw=5, solid_capstyle="round", zorder=7, label="4. Gangvei/sti fra Trollheggveien til ny inngangsdør (kote C+26,4)")
ax.plot(gangvei_pts[:,0], gangvei_pts[:,1], color="#fef3c7", lw=2.5, ls="--", zorder=8)
ax.plot(540, 860, marker="s", markersize=9, color="#b45309", zorder=9)

# -------------------------------------------------------------
# 5. DRENERING (FRA SV-HJØRNE TVERRFLØY, RUNDT SOLPLATTINGENS BUE, TIL OVERVANNSKUM)
# -------------------------------------------------------------
dren_arc = [pt + normal * 4.0 for pt in arc_pts]
dren_pts = [[878, 882], p_tverr] + dren_arc + [p_nw, [885, 694], [955, 668], [1015, 668], [1035, 678], [1055, 692]]
dx = [p[0] for p in dren_pts]
dy = [p[1] for p in dren_pts]
ax.plot(dx, dy, color="#dc2626", lw=4.5, solid_capstyle="round", zorder=8, label="5. Ny drensledning (dybde 2.7m, fra SV-hjørne rundt bue til kum)")
ax.plot(878, 882, marker="s", markersize=9, color="#b91c1c", zorder=10)

# Knotteplast langs murene
membrane_pts = [[885, 875], p_tverr] + dren_arc + [p_nw, [905, 726], [1030, 686]]
ax.plot([p[0] for p in membrane_pts], [p[1] for p in membrane_pts], color="#f97316", lw=3, ls="--", zorder=5, label="Platon knotteplast + 100-150mm XPS")

# Rør fra kjeller (#96)
ax.plot([960, 1015], [728, 710], color="#16a34a", lw=3.5, zorder=7, label="Rør i grøft i kjeller (#96, ca. 1,5m fra nordvegg)")
ax.plot([992, 995], [717, 701], color="#16a34a", lw=4, zorder=7)
ax.plot([995, 999], [701, 675], color="#16a34a", lw=4, ls="--", zorder=8)
ax.plot([999, 1000], [675, 668], color="#16a34a", lw=4, zorder=7)
ax.plot(995, 701, marker="o", markersize=6, color="#15803d", zorder=9)
ax.plot(1000, 668, marker="o", markersize=9, color="#16a34a", zorder=9)
ax.plot(1055, 692, marker="o", markersize=13, color="#2563eb", zorder=8)

# -------------------------------------------------------------
# 6. VANNFORSYNING FRA TROLLHEGGVEIEN HELT TIL TEKNISK ROM
# -------------------------------------------------------------
ax.plot([680, 786], [945, 894], color="#0284c7", lw=3, ls=":", zorder=5)
ax.plot(786, 894, marker="o", markersize=12, color="#0284c7", zorder=9)
ax.plot(786, 894, marker="X", markersize=8, color="#ffffff", zorder=10)

va_ext = np.array([[786, 894], [818, 860], [852, 830], [885, 810], [918, 796]])
ax.plot(va_ext[:,0], va_ext[:,1], color="#0284c7", lw=4.5, ls="-", zorder=7, label="6. Ny 32mm vannledning (utvendig fra stoppekran)")
ax.plot(918, 796, marker="D", markersize=11, color="#0369a1", zorder=9)

va_int = np.array([[918, 796], [950, 788], [985, 795]])
ax.plot(va_int[:,0], va_int[:,1], color="#0284c7", lw=4.5, ls="--", zorder=8, label="   ↳ Ført innvendig til teknisk rom U.11 i senter av huset")
ax.plot(985, 795, marker="o", markersize=11, color="#1d4ed8", zorder=10)
ax.plot(985, 795, marker="*", markersize=7, color="#ffffff", zorder=11)

# -------------------------------------------------------------
# 7. INNKJØRING (VESTGRENSE LANGS 27,7M, UTKJØRING VEST FOR LYKTESTOLPE, HUSBREDDE)
# -------------------------------------------------------------
driveway_pts = np.array([
    [885, 700],   # Vestkant ved inngangsplatting / fasade (møter 27,7m-linjen)
    [795, 333],   # Vestgrense ved Myrteveien (langs 27,7m målelinjen)
    [892, 310],   # Østgrense ved Myrteveien: Lyktestolpe ca. midt på tomtegrensen
    [1035, 675]   # Østkant ved kjellertrapp / husets nordøsthjørne (husets fulle bredde)
])
drive_poly = Polygon(driveway_pts, closed=True, facecolor="#94a3b8", edgecolor="#334155",
                     lw=2.2, alpha=0.45, hatch="//", zorder=3,
                     label="7. Innkjøring (vestgrense langs 27,7m, utkjøring vest for lyktestolpe, husbredde)")
ax.add_patch(drive_poly)

# Marker vestgrensen spesifikt langs 27,7m målelinjen
ax.plot([885, 795], [700, 333], color="#0284c7", lw=3.5, ls="-", zorder=6)

# Lyktestolpe ca. midt på tomtegrensen mot nord (892, 310)
ax.plot(892, 310, marker="o", markersize=12, color="#2563eb", zorder=12)
ax.plot(892, 310, marker="*", markersize=8, color="#ffffff", zorder=13)
ax.annotate(
    "LYKTESTOLPE (Veglys)\nCa. midt på tomtegrensen mot nord\n(Innkjøringens østkant ved Myrteveien)",
    xy=(892, 310), xytext=(960, 240),
    arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=2, connectionstyle="arc3,rad=-0.1"),
    fontsize=9, weight="bold", color="#1e40af",
    bbox=dict(boxstyle="round,pad=0.4", fc="#eff6ff", ec="#2563eb", lw=1.5),
    zorder=14
)

# -------------------------------------------------------------
# 8. TREKKERØR & INFRASTRUKTUR
# -------------------------------------------------------------
ax.plot([900, 840, 780], [665, 640, 600], color="#10b981", lw=3.5, ls="--", zorder=6, label="8. Trekkerør (Ø110mm garasje / Ø50mm snøsmelte)")

# -------------------------------------------------------------
# 9. RIGG & DEPONI
# -------------------------------------------------------------
ax.plot(900, 600, marker="^", markersize=14, color="#eab308", zorder=8)
ax.text(900, 585, "GRAVEMASKIN (8-15t)\nArbeidssone", fontsize=8.5, weight="bold", color="#854d0e", ha="center", zorder=10)
deponi_pts = np.array([[1160, 480], [1270, 450], [1290, 550], [1180, 580]])
ax.add_patch(Polygon(deponi_pts, closed=True, facecolor="#fef08a", edgecolor="#ca8a04", lw=1.8, ls="--", alpha=0.6, zorder=3))
ax.text(1225, 515, "Mellomlagring\nrene steinmasser\n(Gjenbruk)", fontsize=9, weight="bold", color="#713f12", ha="center", zorder=4)

# ---------------- ANNOTASJONER ----------------
# 1. Platting & avtrapping
ax.annotate(
    "1. NY INNGANGSPLATTING (1. ETG, C+26,8)\n"
    "Danner overbygg/tak over kjellernedgang\n"
    "--------------------------------------------------\n"
    "• AVTRAPPING: Trinn ned til innkjøring (C+26,8 ➔ C+25,0)\n"
    "• UNDER TAKET (Kjellernivå C+24,4):\n"
    "  - Ny kjellerdør inn til kjeller\n"
    "  - Utebod & utvendig skap for strøm-inntak\n"
    "  - Støpt repos foran dør m/trappesluk",
    xy=(915, 690), xytext=(500, 630),
    arrowprops=dict(arrowstyle="->", color="#c2410c", lw=2, connectionstyle="arc3,rad=-0.1"),
    fontsize=9.2, weight="bold", color="#7c2d12",
    bbox=dict(boxstyle="round,pad=0.45", fc="#ffedd5", ec="#ea580c", lw=1.8),
    zorder=12
)

# 2. Kjellertrapp
ax.annotate(
    "2. NY KJELLERTRAPP\n(Støpt trappeløp i inntegnet trasé\nm/PEX-smelterør i trinn ned til C+24,4)",
    xy=(995, 686), xytext=(1040, 615),
    arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2, connectionstyle="arc3,rad=0.1"),
    fontsize=9.2, weight="bold", color="#075985",
    bbox=dict(boxstyle="round,pad=0.4", fc="#e0f2fe", ec="#0284c7", lw=1.5),
    zorder=12
)

# 3. Solplatting m/bue
ax.annotate(
    "3. LILLA SOLPLATTING M/BUE (KVELDSSOL)\n"
    "Bue fra hushjørne tverrfløy til hushjørne NV\n"
    "--------------------------------------------------\n"
    "• OVER: Solplatting for kveldssola (dekke C+26,8)\n"
    "• UNDER: Fullt underbygd kjeller (bunn C+24,4)\n"
    "• Støpt plate, armerte betongvegger & vanntett dekke\n"
    "• Innstøpt Doyma-hylse for nytt vanninntak",
    xy=(860, 770), xytext=(490, 735),
    arrowprops=dict(arrowstyle="->", color="#7e22ce", lw=2, connectionstyle="arc3,rad=-0.08"),
    fontsize=9.2, weight="bold", color="#581c87",
    bbox=dict(boxstyle="round,pad=0.45", fc="#faf5ff", ec="#a855f7", lw=1.8),
    zorder=12
)

# 4. Gangvei
ax.annotate(
    "4. GANGVEI / STI FRA TROLLHEGGVEIEN\n"
    "• Adkomststi fra Trollheggveien til ny inngangsdør\n"
    "• Etableres i flatt terrengnivå (kote ~C+26,4)\n"
    "• Skifer/heller/grus over hagen frem til platting",
    xy=(700, 825), xytext=(490, 845),
    arrowprops=dict(arrowstyle="->", color="#b45309", lw=2, connectionstyle="arc3,rad=0.1"),
    fontsize=9.2, weight="bold", color="#78350f",
    bbox=dict(boxstyle="round,pad=0.45", fc="#fef3c7", ec="#d97706", lw=1.8),
    zorder=12
)

# 5. Dren start
ax.annotate(
    "START DRENSLEDNING\n(Syd-vest hjørne tverrfløy)",
    xy=(878, 882), xytext=(940, 915),
    arrowprops=dict(arrowstyle="->", color="#b91c1c", lw=1.8),
    fontsize=8.5, weight="bold", color="#7f1d1d",
    bbox=dict(boxstyle="round,pad=0.3", fc="#fef2f2", ec="#dc2626", lw=1.2),
    zorder=12
)

# 6. Vannledning & Teknisk rom
ax.annotate(
    "6. VANNLEDNING TIL TEKNISK ROM (U.11)\n"
    "• 32mm PE fra stoppekran (13,3m) til NV-inntak\n"
    "• Doyma-hylse i ny underbygd kjeller\n"
    "• FØRES INNVENDIG I KJELLEREN TIL TEKNISK ROM\n"
    "  i senter av huset (U.11, kote C+24,4)",
    xy=(985, 795), xytext=(1060, 825),
    arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2, connectionstyle="arc3,rad=-0.1"),
    fontsize=9.2, weight="bold", color="#0c4a6e",
    bbox=dict(boxstyle="round,pad=0.45", fc="#f0f9ff", ec="#0284c7", lw=1.8),
    zorder=12
)

ax.annotate(
    "EKSISTERENDE STOPPEKRAN\n(Ved 13,3m-målelinjen)",
    xy=(786, 894), xytext=(560, 930),
    arrowprops=dict(arrowstyle="->", color="#0284c7", lw=2),
    fontsize=9, weight="bold", color="#0c4a6e",
    bbox=dict(boxstyle="round,pad=0.4", fc="#e0f2fe", ec="#0284c7", lw=1.5),
    zorder=12
)

# 7. Innkjøring
ax.annotate(
    "7. INNKJØRING / FORSTERKET BÆRELAG (~200 m²)\n"
    "• Vestgrense følger målelinjen på 27,7 m helt til vei\n"
    "• Utkjøring ved Myrteveien er VEST for lyktestolpen (892, 310)\n"
    "• Dekker husets fulle bredde ved fasaden (~9,5 m)\n"
    "• Nivå innkjøring: Kote ~C+25,0 (fall mot Myrteveien)\n"
    "• Forsterket bærelag pukk 0-63 mm (betongbiler/mobilkran)",
    xy=(840, 480), xytext=(490, 480),
    arrowprops=dict(arrowstyle="->", color="#334155", lw=2, connectionstyle="arc3,rad=0.1"),
    fontsize=9.2, weight="bold", color="#0f172a",
    bbox=dict(boxstyle="round,pad=0.45", fc="#f8fafc", ec="#475569", lw=1.8),
    zorder=12
)

# Overvannskum
ax.annotate(
    "OVERVANNSKUM\n(Vannstand 253cm / LOD)",
    xy=(1055, 692), xytext=(1160, 680),
    arrowprops=dict(arrowstyle="->", color="#1d4ed8", lw=2),
    fontsize=9, weight="bold", color="#1e40af",
    bbox=dict(boxstyle="round,pad=0.4", fc="#eff6ff", ec="#2563eb", lw=1.5),
    zorder=12
)

# Rør fra kjeller
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

# Høydenivå-merkelapper (Koter)
kote_props = dict(boxstyle="square,pad=0.25", fc="#ffffff", ec="#334155", lw=1.2)
ax.text(880, 725, "Kote C+26,8 (Platting)", fontsize=8, weight="bold", color="#c2410c", bbox=kote_props, zorder=14)
ax.text(890, 660, "Kote C+25,0 (Innkjøring)", fontsize=8, weight="bold", color="#1e293b", bbox=kote_props, zorder=14)
ax.text(945, 815, "Kote C+24,4 (Kjeller)", fontsize=8, weight="bold", color="#0369a1", bbox=kote_props, zorder=14)
ax.text(620, 830, "Kote C+26,4 (Gangvei)", fontsize=8, weight="bold", color="#92400e", bbox=kote_props, zorder=14)

# Title banner
title_box = dict(boxstyle="square,pad=0.5", fc="#ffffff", ec="#0f172a", lw=1.8)
title_str = (
    "MYRTEVEIEN 6 — ANLEGGSOMRÅDE & PLANSKISSE FOR GRUNNARBEIDER NORD & VEST\n"
    "Prosjekt: M6 Totalrehabilitering | Tiltakshaver: Magnus Kirø | Gnr 140 / Bnr 371 | Tønsberg kommune\n"
    "Oppdatert: Solplatting m/bue fra hushjørne tverrfløy til NV, utkjøring vest for lyktestolpe"
)
ax.text(780, 125, title_str, fontsize=9.2, weight="bold", color="#0f172a", ha="center", bbox=title_box, zorder=15)

ax.legend(loc="lower left", bbox_to_anchor=(0.01, 0.01), fontsize=8.6, framealpha=0.96,
          facecolor="#ffffff", edgecolor="#0f172a", fancybox=False)

ax.axis("off")
plt.tight_layout()

out_path_repo = os.path.join(assets_dir, "planskisse_anleggsomraade_nord.png")
out_path_brain = "C:/Users/magkir/.gemini/antigravity/brain/773222c6-8706-4aad-83b9-5ad2ac2dc3ae/planskisse_anleggsomraade_nord.png"

plt.savefig(out_path_repo, dpi=200, bbox_inches="tight")
plt.savefig(out_path_brain, dpi=200, bbox_inches="tight")
print("Successfully generated updated site plan with curved solplatting and clean driveway!")
