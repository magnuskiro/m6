import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import numpy as np

# Set up figure with high DPI
fig, ax = plt.subplots(figsize=(16, 12), dpi=220)

# Colors
bg_color = "#f8fafc"
fig.patch.set_facecolor(bg_color)
ax.set_facecolor(bg_color)

# 1. Roads and boundaries
# Myrteveien (North / Top)
ax.fill_between([0, 100], [86, 90], [100, 100], color="#cbd5e1", alpha=0.7)
ax.plot([0, 100], [86, 90], color="#64748b", lw=2, ls="--")
ax.text(50, 93.5, "MYRTEVEIEN (Kommunal veg)", fontsize=13, weight="bold", color="#1e293b", ha="center")

# Trollheggveien (West / Left)
troll_poly = Polygon([(0, 0), (14, 0), (10, 100), (0, 100)], closed=True, color="#e2e8f0", alpha=0.8)
ax.add_patch(troll_poly)
ax.text(6, 50, "TROLLHEGGVEIEN", fontsize=11, weight="bold", color="#475569", rotation=87, ha="center")

# Property boundary (Gnr 140 / Bnr 371)
prop_poly = Polygon([(14, 3), (96, 6), (94, 88), (11, 86)], closed=True, fill=False, edgecolor="#ef4444", lw=2, ls="-.", label="Eiendomsgrense (140/371)")
ax.add_patch(prop_poly)

# 2. Existing Buildings
# Existing garage
garasje = patches.Rectangle((22, 58), 14, 18, angle=4, facecolor="#94a3b8", edgecolor="#334155", lw=2, zorder=3)
ax.add_patch(garasje)
ax.text(29, 67, "EKSISTERENDE\nGARASJE", fontsize=9, weight="bold", color="#0f172a", ha="center", va="center", zorder=4)

# Future garage position (dashed)
ny_garasje = patches.Rectangle((20, 32), 16, 18, angle=4, facecolor="#eff6ff", edgecolor="#3b82f6", lw=2, ls=":", zorder=3)
ax.add_patch(ny_garasje)
ax.text(28, 41, "FREMTIDIG\nDOBBELGARASJE", fontsize=8.5, weight="bold", color="#1d4ed8", ha="center", va="center", zorder=4)

# Existing House Main Body
bolig_poly = Polygon([(45, 18), (75, 20), (73, 48), (43, 46)], closed=True, facecolor="#e2e8f0", edgecolor="#1e293b", lw=2.5, zorder=3)
ax.add_patch(bolig_poly)
ax.text(59, 32, "EKSISTERENDE BOLIG\n(Kjeller / 1. etg / 2. etg)", fontsize=10, weight="bold", color="#1e293b", ha="center", va="center", zorder=4)

# 3. Groundwork Measures (Tiltak)
# TILTAK 1: Underbygget kjeller under nytt inngangsparti (Nordvest)
inngang_poly = Polygon([(38, 40), (43.5, 40.4), (43, 47.5), (37.5, 47.1)], closed=True, facecolor="#fdba74", edgecolor="#ea580c", lw=2.5, hatch="//", zorder=5, label="1. Underbygget kjeller (Inngangsparti ~9 m², dybde 2.7m)")
ax.add_patch(inngang_poly)
ax.text(40.5, 43.8, "NYTT INNGANGS-\nPARTI\n(Underbygget kjeller\n~9 m², dybde 2.7m)", fontsize=7.5, weight="bold", color="#9a3412", ha="center", va="center", zorder=6)

# TILTAK 2: Ny utvendig kjellernedgang (langs nordvegg til inngang)
trapp_poly = Polygon([(37.5, 47.1), (43, 47.5), (42.6, 53.5), (37.1, 53.1)], closed=True, facecolor="#7dd3fc", edgecolor="#0284c7", lw=2, zorder=5, label="2. Ny kjellernedgang (kote C+24,4 m/sluk & smelterør)")
ax.add_patch(trapp_poly)
for frac in [0.2, 0.4, 0.6, 0.8]:
    p1 = (37.5 + (37.1 - 37.5) * frac, 47.1 + (53.1 - 47.1) * frac)
    p2 = (43.0 + (42.6 - 43.0) * frac, 47.5 + (53.5 - 47.5) * frac)
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#0369a1", lw=1.2, zorder=6)
ax.text(40, 50.3, "Kjeller-\nnedgang\n(C+24,4)", fontsize=7.5, weight="bold", color="#0c4a6e", ha="center", va="center", zorder=7)

# Sluk / drensrist in bottom of stairs
ax.plot(40, 47.8, marker="s", markersize=6, color="#0284c7", zorder=8)

# TILTAK 3: Re-drenering nordvegg (dybde 2.75m)
dren_x = [42.6, 43, 43.5, 73.5, 74]
dren_y = [53.5, 47.5, 45.8, 48.2, 49.5]
ax.plot(dren_x, dren_y, color="#dc2626", lw=4.5, solid_capstyle='round', zorder=5, label="3. Ny drensledning (dybde 2.7m, 110mm pukk/duk)")
ax.plot([43, 73.5], [46.8, 49.2], color="#f97316", lw=2.5, ls="--", zorder=4, label="Platon knotteplast + 100-150mm XPS")

# Rørgjennomføring fra kjeller (#96)
ax.plot([50, 50], [42, 46.5], color="#16a34a", lw=3.5, zorder=7)
ax.plot(50, 46.5, marker="o", markersize=8, color="#16a34a", zorder=8)
ax.annotate("Rør fra kjeller (#96)\n(topp 246cm kobles på)", xy=(50, 46.5), xytext=(56, 54),
            arrowprops=dict(arrowstyle="->", color="#15803d", lw=1.5),
            fontsize=8.5, weight="bold", color="#15803d", bbox=dict(boxstyle="round,pad=0.3", fc="#dcfce7", ec="#16a34a"))

# Overvannskum & utløp LOD
ax.plot(76, 50, marker="o", markersize=11, color="#2563eb", zorder=7)
ax.text(76, 52.5, "Overvannskum\n(Vannstand 253cm)", fontsize=8, weight="bold", color="#1e40af", ha="center")
ax.plot([76, 85], [50, 51], color="#2563eb", lw=2.5, ls=":", zorder=5)
ax.plot(86, 51.5, marker="h", markersize=14, color="#3b82f6", zorder=6)
ax.text(86, 54.5, "LOD Infiltrasjon\n(Stenkiste)", fontsize=8, color="#1d4ed8", ha="center")

# TILTAK 4: Ny kommunal vannledning (fra Myrteveien til NV-hjørne)
va_x = [37, 34, 32, 34, 37.5]
va_y = [87, 78, 65, 52, 47.1]
ax.plot(va_x, va_y, color="#0284c7", lw=3.5, ls="-", zorder=6, label="4. Ny 32mm vannledning (i varerør >1.6m dybde)")
ax.plot(37.5, 47.1, marker="D", markersize=9, color="#0369a1", zorder=8)
ax.annotate("INNVENDIG INNTAK\nNordvest-hjørne\n(Vanntett Doyma-hylse)", xy=(37.5, 47.1), xytext=(17, 51),
            arrowprops=dict(arrowstyle="->", color="#0284c7", lw=1.5),
            fontsize=8.5, weight="bold", color="#0369a1", bbox=dict(boxstyle="round,pad=0.3", fc="#e0f2fe", ec="#0284c7"))

# TILTAK 5: Ny vinklet innkjøring & Bærelag (Pukk 0-63)
driveway_poly = Polygon([(48, 87), (64, 88), (58, 66), (48, 56), (42, 56), (42, 73)], closed=True,
                        facecolor="#cbd5e1", edgecolor="#64748b", lw=1.5, alpha=0.55, hatch="..", zorder=2, label="5. Ny innkjøring (Pukk 0-63 bærelag for tungbil)")
ax.add_patch(driveway_poly)
ax.text(52, 72, "NY INNKJØRING\n(Bærelag 0-63 for\nbetong-/kranbil)", fontsize=9, weight="bold", color="#334155", ha="center", va="center")

# Old driveway entry (faded)
ax.plot([36, 44], [87, 87], color="#94a3b8", lw=3, ls="--")
ax.text(40, 84, "Gml. avkjørsel", fontsize=7.5, color="#64748b", ha="center")

# TILTAK 6: Trekkerør (røde kabelrør til garasje og el/fiber)
ax.plot([48, 36, 28], [58, 52, 42], color="#10b981", lw=2.5, ls="--", zorder=6, label="6. Trekkerør (Ø110mm garasje / Ø50mm snøsmelte)")

# 4. Rigging, Machine & Soil Logistics
# Gravemaskin posisjon
ax.plot(47, 60, marker="^", markersize=12, color="#eab308", zorder=7)
ax.text(47, 62.5, "Gravemaskin (8-15t)\nArbeidssone", fontsize=8, weight="bold", color="#a16207", ha="center")

# Midlertidig massedeponi
deponi = patches.Ellipse((70, 70), 15, 11, angle=-10, facecolor="#fef08a", edgecolor="#ca8a04", lw=1.5, ls="--", alpha=0.6, zorder=2)
ax.add_patch(deponi)
ax.text(70, 70, "Mellomlagring\nrene steinmasser\n(Gjenbruk)", fontsize=8, color="#854d0e", ha="center", va="center")

# Planering nord-vest
planering = patches.Polygon([(18, 76), (32, 78), (30, 64), (16, 64)], closed=True, facecolor="#dcfce7", edgecolor="#86efac", lw=1, ls=":", alpha=0.6, zorder=1)
ax.add_patch(planering)
ax.text(23, 71, "Terrengplanering\nNord-Vest", fontsize=8, color="#166534", ha="center")

# North Arrow
ax.annotate('N', xy=(90, 80), xytext=(90, 72),
            arrowprops=dict(facecolor='#1e293b', edgecolor='#1e293b', width=3, headwidth=10),
            fontsize=14, weight='bold', color='#1e293b', ha='center', va='center')

# Title block & Info box
title_box = dict(boxstyle="square,pad=0.5", fc="#ffffff", ec="#0f172a", lw=1.5)
info_text = (
    "MYRTEVEIEN 6 - ANLEGGSOMRÅDE & PLANSKISSE FOR GRUNNARBEIDER NORD\n"
    "Prosjekt: M6 Totalrehabilitering | Tiltakshaver: Magnus Kirø | Gnr 140 / Bnr 371 | Tønsberg kommune\n"
    "Dato: 2026-09-24 | Referanse: GitHub #92 | Tegningsref: KB Arkitekter A-001 / A-100PS / A-101PS / A-201PS"
)
ax.text(50, 4.5, info_text, fontsize=9.5, weight="bold", color="#0f172a", ha="center", bbox=title_box, zorder=10)

# Set axis limits & styling
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Add Legend
ax.legend(loc="lower left", bbox_to_anchor=(0.02, 0.08), fontsize=8.2, framealpha=0.98, facecolor="#ffffff", edgecolor="#cbd5e1")

plt.tight_layout()
plt.savefig("m6/assets/images/planskisse_anleggsomraade_nord.png", dpi=220, bbox_inches='tight')
print("Successfully generated refined m6/assets/images/planskisse_anleggsomraade_nord.png")
