#!/usr/bin/env python3
"""
Generate scaled architectural elevations (Fasade Vest for Roof B & Roof C, Fasade Sør, Fasade Nord)
plus an exact 3D-projected Roof Plan (Takplan) showing valley-to-chimney clearances for
Alternativ 1 (5.20m wide x 3.20m deep west extension + 2.10m 1-story north extension, NO south extension).

Exact elevations from snitt_a_bolig_200.jpg:
  Ground (terreng): C+26.4  (y_elev = 0)
  1. etg floor:     C+26.8  (+40 cm)
  2. etg floor:     C+29.6  (+320 cm)
  Main eaves:       C+32.5  (+610 cm)
  Main ridge:       C+35.3  (+890 cm, 32.7° pitch over 4.33 m half-width -> 278 cm rise)
  Chimney top:      C+36.1  (+970 cm, 80 cm above ridge/roof)
"""

import math
import os

OUT_DIR = "/home/kiro/repos/m6/assets/images/drawings"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


class Draw:
    def __init__(self, ox: float, oy: float, scale: float = 0.72):
        self.ox = ox
        self.oy = oy
        self.s = scale
        self.els = []

    def px(self, x):
        return self.ox + x * self.s

    def py(self, y):
        return self.oy + y * self.s

    def add(self, el):
        self.els.append(el)

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1.5, dash=None, opacity=1.0, rx=0):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        rxa = f' rx="{rx}"' if rx else ""
        self.add(
            f'<rect x="{self.px(x):.1f}" y="{self.py(y):.1f}" width="{w*self.s:.1f}" height="{h*self.s:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}{op}{rxa}/>'
        )

    def poly(self, pts, fill="none", stroke="#1e293b", sw=2, dash=None, opacity=1.0):
        pstr = " ".join(f"{self.px(x):.1f},{self.py(y):.1f}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        self.add(f'<polygon points="{pstr}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="miter"{da}{op}/>')

    def line(self, x1, y1, x2, y2, stroke="#1e293b", sw=2, dash=None, opacity=1.0):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        self.add(f'<line x1="{self.px(x1):.1f}" y1="{self.py(y1):.1f}" x2="{self.px(x2):.1f}" y2="{self.py(y2):.1f}" stroke="{stroke}" stroke-width="{sw}"{da}{op}/>')

    def text(self, x, y, txt, size=18, weight="600", fill="#1e293b", anchor="middle", rotate=0):
        tx, ty = self.px(x), self.py(y)
        rot = f' transform="rotate({rotate} {tx:.1f} {ty:.1f})"' if rotate else ""
        self.add(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{rot}>{esc(txt)}</text>')

    def siding(self, x, y, w, h, step=26):
        """Horizontal white timber cladding lines."""
        yy = y + step
        while yy < y + h - 4:
            self.line(x, yy, x + w, yy, stroke="#e2e8f0", sw=1)
            yy += step

    def win(self, x, y, w, h, panes_x=2, panes_y=2):
        """Classic Norwegian mullioned window (white frame + soft sky reflection)."""
        self.rect(x - 6, y - 6, w + 12, h + 12, fill="#ffffff", stroke="#475569", sw=1.4)
        self.rect(x, y, w, h, fill="#dbeafe", stroke="#334155", sw=1.8)
        for i in range(1, panes_x):
            vx = x + i * w / panes_x
            self.line(vx, y, vx, y + h, stroke="#ffffff", sw=2.6)
            self.line(vx, y, vx, y + h, stroke="#64748b", sw=0.8)
        for j in range(1, panes_y):
            hy = y + j * h / panes_y
            self.line(x, hy, x + w, hy, stroke="#ffffff", sw=2.4)
            self.line(x, hy, x + w, hy, stroke="#64748b", sw=0.8)

    def french_door(self, x, y, w, h):
        self.rect(x - 6, y - 6, w + 12, h + 6, fill="#ffffff", stroke="#475569", sw=1.4)
        self.rect(x, y, w, h, fill="#dbeafe", stroke="#334155", sw=2)
        self.line(x + w / 2, y, x + w / 2, y + h, stroke="#ffffff", sw=3.5)
        self.line(x + w / 2, y, x + w / 2, y + h, stroke="#334155", sw=1.2)
        # Bottom solid panel
        self.rect(x + 2, y + h - 45, w - 4, 43, fill="#f8fafc", stroke="#64748b", sw=1.2)
        # Mullions
        for hy in [y + 45, y + 95, y + 145]:
            self.line(x, hy, x + w, hy, stroke="#ffffff", sw=2)

    def dim_h(self, x1, x2, y, label, color="#334155", bold=False, dy=-12):
        self.line(x1, y, x2, y, stroke=color, sw=1.8)
        self.line(x1, y - 12, x1, y + 12, stroke=color, sw=1.8)
        self.line(x2, y - 12, x2, y + 12, stroke=color, sw=1.8)
        self.text((x1 + x2) / 2, y + dy, label, size=15, weight="700" if bold else "600", fill=color)

    def dim_v(self, x, y1, y2, label, color="#334155", bold=False, dx=-18):
        self.line(x, y1, x, y2, stroke=color, sw=1.8)
        self.line(x - 12, y1, x + 12, y1, stroke=color, sw=1.8)
        self.line(x - 12, y2, x + 12, y2, stroke=color, sw=1.8)
        self.text(x + dx, (y1 + y2) / 2, label, size=15, weight="700" if bold else "600", fill=color, rotate=-90)


def draw_west_elevation(d: Draw, roof_type: str, title: str, subtitle: str, accent: str):
    """West facade (looking east): left = North (y=0), right = South (y=1166).
    y_up = 0 is ground C+26.4; screen y = -height_cm (so ground is at y=0, ridge at y=-890)."""
    # Sky backdrop
    d.rect(-260, -1040, 1520, 1040, fill="#f0f9ff", opacity=0.45)
    # Ground line
    d.rect(-260, 0, 1520, 45, fill="#dcfce7", opacity=0.8)
    d.line(-260, 0, 1260, 0, stroke="#15803d", sw=3)

    # 1-story north extension peeking out on the left (x = -210..0, eaves -300, ridge -420)
    d.rect(-210, -300, 210, 300, fill="#f8fafc", stroke="#334155", sw=2)
    d.siding(-210, -300, 210, 260)
    d.rect(-210, -40, 210, 40, fill="#64748b", stroke="#334155", sw=1.5)
    # Porch roof over NW entry
    d.poly([(-225, -295), (-105, -405), (0, -300)], fill="#334155", stroke="#0f172a", sw=2)
    d.text(-105, -180, "Nord-tilb.", size=13, fill="#64748b")
    d.text(-105, -158, "(1 etg)", size=13, fill="#64748b")

    # Main house wall (x = 0..1166, height 610 cm to eaves)
    d.rect(0, -610, 1166, 610, fill="#ffffff", stroke="#1e293b", sw=2.5)
    d.siding(0, -610, 1166, 570)
    d.rect(0, -40, 1166, 40, fill="#64748b", stroke="#334155", sw=1.5)  # Plinth

    # Main pitched roof (eaves -610, ridge -890, overhangs -35 and +35)
    d.poly([(-35, -600), (1201, -600), (1201, -890), (-35, -890)], fill="#1e293b", stroke="#0f172a", sw=2.5)
    # Roof tile horizontal lines
    for ry in range(-860, -600, 36):
        d.line(-32, ry, 1198, ry, stroke="#334155", sw=1)
    # Two skylights on main roof
    d.rect(140, -825, 115, 140, fill="#93c5fd", stroke="#0f172a", sw=2.5)
    d.rect(970, -825, 115, 140, fill="#93c5fd", stroke="#0f172a", sw=2.5)

    # Original chimney (y = 720..775 -> width 55 cm in west elevation, rising behind west wing!)
    d.rect(720, -965, 55, 160, fill="#9a3412", stroke="#431407", sw=2.5)
    d.rect(714, -975, 67, 14, fill="#475569", stroke="#0f172a", sw=1.5)
    d.text(748, -992, "Orig. pipe", size=14, weight="700", fill="#9a3412")

    # Main wall windows (north side 0..410, south side 930..1166)
    d.win(95, -245, 110, 130, 2, 2)  # Stair 1st
    d.win(95, -525, 110, 130, 2, 2)  # Stair 2nd
    d.win(260, -245, 95, 120, 1, 2)  # Vask 1st
    d.win(260, -525, 95, 120, 1, 2)  # Bod 2nd
    d.win(995, -245, 115, 140, 2, 2)  # South dining 1st
    d.win(995, -525, 115, 140, 2, 2)  # South 2nd

    # WEST EXTENSION (x = 410..930 = 5.20 m wide, projects 3.20m toward viewer!)
    # Slight drop shadow on main wall
    d.rect(930, -605, 22, 605, fill="#94a3b8", opacity=0.35)
    d.rect(410, -610, 520, 610, fill="#ffffff", stroke="#0f172a", sw=3)
    d.siding(410, -610, 520, 570)
    d.rect(410, -40, 520, 40, fill="#475569", stroke="#1e293b", sw=1.5)

    # Generous west living windows (1st and 2nd floor — FULLY ENCLOSED!)
    d.win(465, -255, 185, 165, 3, 2)
    d.win(690, -255, 185, 165, 3, 2)
    d.win(465, -530, 185, 155, 3, 2)
    d.win(690, -530, 185, 155, 3, 2)

    if roof_type == "B_saltak20":
        # 20° low-pitched gable roof (rise = 95 cm over 260 cm half-width -> peak at -705)
        d.poly([(385, -600), (670, -708), (955, -600)], fill="#ffffff", stroke="#0f172a", sw=3)
        # Clipped horizontal siding lines strictly inside the gable triangle
        for sy in [-625, -650, -675]:
            frac = (-sy - 600) / 108.0
            half_w = 285 * (1.0 - frac) - 10
            if half_w > 20:
                d.line(670 - half_w, sy, 670 + half_w, sy, stroke="#e2e8f0", sw=1)
        # Roof fascia/verge (thick dark roof edge)
        d.poly([(375, -595), (670, -722), (965, -595), (950, -588), (670, -704), (390, -588)], fill="#1e293b", stroke="#0f172a", sw=2)
        d.text(670, -752, "20° slak saltak-gavl (møne C+33,45)", size=15, weight="700", fill=accent)
    elif roof_type == "C_pulttak10":
        # 10° shed/lean-to roof (eaves -600 on west face, rises 56 cm over 3.20m + 18cm to main roof -> top edge at -675)
        d.poly([(385, -600), (955, -600), (955, -682), (385, -682)], fill="#334155", stroke="#0f172a", sw=2.5)
        # Vertical standing-seam metal ribs
        for rx in range(420, 945, 45):
            d.line(rx, -680, rx, -602, stroke="#475569", sw=1.4)
        d.text(670, -715, "10° båndtekket pulttak / oppløft (null gradrenner!)", size=15, weight="700", fill=accent)

    # Dimension lines
    d.dim_h(0, 410, 75, "4,10 m", color="#475569")
    d.dim_h(410, 930, 75, "5,20 m (vest-tilbygg)", color=accent, bold=True)
    d.dim_h(930, 1166, 75, "2,36 m", color="#475569")
    d.dim_v(-290, -890, 0, "8,9 m møne", color="#334155", bold=True, dx=-22)

    # Titles
    d.text(490, -1100, title, size=24, weight="800", fill="#0f172a")
    d.text(490, -1064, subtitle, size=16, weight="600", fill=accent)


def draw_south_elevation(d: Draw):
    """South gable elevation (looking north): left = West (x=-320..0), right = Main (x=0..866)."""
    d.rect(-420, -1040, 1400, 1040, fill="#f0f9ff", opacity=0.45)
    d.rect(-420, 0, 1400, 45, fill="#dcfce7", opacity=0.8)
    d.line(-420, 0, 980, 0, stroke="#15803d", sw=3)

    # West extension side wall (x = -320..0, 2 full stories!)
    d.rect(-320, -610, 320, 610, fill="#f8fafc", stroke="#1e293b", sw=2.5)
    d.siding(-320, -610, 320, 570)
    d.rect(-320, -40, 320, 40, fill="#64748b", stroke="#334155", sw=1.5)
    d.win(-220, -245, 130, 145, 2, 2)  # 1st south window in west wing
    d.win(-220, -525, 130, 145, 2, 2)  # 2nd south window in west wing

    # Roof of west wing in side profile: show BOTH Option B (solid 20° ridge at -708) & Option C (dashed 10° pulttak!)
    d.poly([(-345, -600), (147, -708), (0, -600)], fill="#1e293b", stroke="#0f172a", sw=2.2)  # Wait: side view of gable is a trapezoid!
    d.poly([(-345, -600), (-345, -708), (147, -708), (0, -600)], fill="#1e293b", stroke="#0f172a", sw=2.2)
    # Dashed green line showing Option C (10° pulttak)
    d.line(-345, -600, 100, -674, stroke="#10b981", sw=3.5, dash="10,6")
    d.text(-190, -736, "Alt B: 20° saltak", size=14, weight="700", fill="#0284c7")
    d.text(-210, -578, "Alt C: 10° pulttak (stiplet)", size=13, weight="700", fill="#059669")

    # Original chimney (x = 135..230 -> 95 cm wide EAST-WEST in south elevation!!)
    d.rect(135, -965, 95, 260, fill="#9a3412", stroke="#431407", sw=2.5)
    d.rect(128, -975, 109, 14, fill="#475569", stroke="#0f172a", sw=1.5)
    d.text(182, -992, "Orig. pipe (95 cm Ø–V)", size=14, weight="700", fill="#9a3412")

    # Main south gable wall (x = 0..866, eaves -610, ridge at x=433, y=-890)
    d.poly([(0, 0), (866, 0), (866, -610), (433, -890), (0, -610)], fill="#ffffff", stroke="#0f172a", sw=3)
    d.siding(0, -610, 866, 570)
    d.rect(0, -40, 866, 40, fill="#64748b", stroke="#334155", sw=1.5)
    # Main gable roof fascia
    d.poly([(-35, -588), (433, -906), (901, -588), (885, -578), (433, -885), (-19, -578)], fill="#1e293b", stroke="#0f172a", sw=2)

    # South gable windows & French terrace door
    d.win(115, -245, 160, 145, 3, 2)  # Dining window
    d.french_door(450, -250, 160, 210)  # Terrace double door!
    d.win(130, -525, 165, 145, 3, 2)  # 2nd floor living
    d.win(560, -525, 155, 145, 2, 2)  # 2nd floor sov 3
    d.win(375, -765, 116, 110, 2, 2)  # Loft gable window (220 cm ceiling!)

    # Timber deck at ground level
    d.rect(350, -24, 560, 24, fill="#d97706", opacity=0.4, stroke="#92400e", sw=1.8)
    d.text(630, -7, "Markterrasse syd", size=13, weight="700", fill="#78350f")

    d.dim_h(-320, 0, 68, "3,20 m vest", color="#0284c7", bold=True)
    d.dim_h(0, 866, 68, "8,66 m (eksisterende bredde)", bold=True)
    d.text(280, -1100, "FASADE SØR (Sørgavl — uten syd-tilbygg)", size=24, weight="800", fill="#0f172a")
    d.text(280, -1064, "Viser profil på 3,20 m vest-tilbygg (Alt B saltak + Alt C pulttak) og 95 cm original pipe", size=15, weight="600", fill="#475569")


def draw_roof_plan(d: Draw):
    """Top-down Roof Plan (Takplan) proving exact 3D valley-to-chimney clearances for Alt A, B & C!
    Coords: x = 0..866 (west..east), y = 0..1166 (north..south), west wing x = -320..0, y = 410..930."""
    # 1-story north extension roof
    d.rect(250, -210, 616, 210, fill="#e2e8f0", stroke="#475569", sw=2, dash="8,5")
    d.text(558, -95, "1-etg nord-tilbygg (tak)", size=15, weight="600", fill="#475569")

    # Main roof rectangle (with 35 cm overhang)
    d.rect(-35, -35, 936, 1236, fill="#f1f5f9", stroke="#0f172a", sw=3)
    # Main ridge line (x = 433)
    d.line(433, -35, 433, 1201, stroke="#0f172a", sw=3.5)
    d.text(455, 110, "Hovedmøne C+35,3 (32,7°)", size=15, weight="700", fill="#0f172a", anchor="start")

    # West wing footprint (x = -320..0, y = 410..930)
    d.rect(-340, 395, 340, 550, fill="#e0f2fe", stroke="#0284c7", sw=2.5)
    d.text(-170, 575, "Vest-tilbygg", size=17, weight="800", fill="#0369a1")
    d.text(-170, 603, "5,20 × 3,20 m", size=15, weight="700", fill="#0369a1")

    # EXACT ORIGINAL CHIMNEY (95 x 55 cm east-west: x=135..230, y=720..775)
    d.rect(135, 720, 95, 55, fill="#b45309", stroke="#431407", sw=3)
    d.text(460, 756, "Orig. pipe (95×55 cm Ø–V)", size=15, weight="800", fill="#9a3412", anchor="start")
    d.line(235, 750, 452, 750, stroke="#b45309", sw=1.4)

    # --- ROOF OPTION A (RED — COLLISION!): 32.7° gable (x_stop=260, y_ridge=670) ---
    d.line(-340, 670, 260, 670, stroke="#dc2626", sw=2.2, dash="6,5")
    d.line(0, 410, 260, 670, stroke="#dc2626", sw=2.5, dash="8,5")
    d.line(0, 930, 260, 670, stroke="#dc2626", sw=3, dash="8,5")
    d.text(460, 668, "✗ Alt A (32,7°): krasjer i pipe!", size=14, weight="800", fill="#dc2626", anchor="start")
    d.line(265, 664, 452, 664, stroke="#dc2626", sw=1.3, dash="4,3")

    # --- ROOF OPTION B (BLUE — CLEAR!): 20° low-pitched gable (x_stop=147, y_ridge=670) ---
    d.line(-340, 670, 147, 670, stroke="#0284c7", sw=3.5)
    d.line(0, 410, 147, 670, stroke="#0284c7", sw=3.5)
    d.line(0, 930, 147, 670, stroke="#0284c7", sw=3.5)
    d.text(460, 560, "✓ Alt B (20° saltak): 28 cm klar nord for pipe!", size=15, weight="800", fill="#0284c7", anchor="start")
    d.line(130, 650, 452, 555, stroke="#0284c7", sw=1.5)

    # --- ROOF OPTION C (GREEN — CLEAR!): 10° shed roof (straight horizontal knee at x=100, y=410..930) ---
    d.line(100, 410, 100, 930, stroke="#059669", sw=4, dash="14,6")
    d.text(460, 880, "✓ Alt C (10° pulttak): rett knekk x=100", size=15, weight="800", fill="#059669", anchor="start")
    d.text(460, 905, "   (35 cm vest for pipe, 0 gradrenner!)", size=14, weight="700", fill="#059669", anchor="start")
    d.line(100, 875, 452, 875, stroke="#059669", sw=1.5)

    d.text(320, -290, "TAKPLAN (Ovenfra) — Eksakt 3D-sjekk av gradrenner mot original pipe", size=22, weight="800", fill="#0f172a")
    d.text(320, -255, "Viser hvorfor 32,7° saltak treffer pipa, mens 20° saltak (Alt B) og 10° pulttak (Alt C) går helt klar!", size=15, weight="600", fill="#475569")


def main():
    W, H = 2600, 1980
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{W}" height="{H}" fill="#faf9f6"/>',
        # Header
        f'<rect x="0" y="0" width="{W}" height="135" fill="#0f172a"/>',
        f'<rect x="0" y="129" width="{W}" height="6" fill="#0284c7"/>',
        f'<text x="60" y="60" font-size="38" font-weight="800" fill="#ffffff">M6 (#50) — Alternativ 1 (5,20 × 3,20 m vest): Fasader &amp; Takalternativer</text>',
        f'<text x="60" y="102" font-size="22" font-weight="500" fill="#cbd5e1">Tekniske fasadetegninger (Vest + Sør) og 3D-beregnet takplan for 20° slakt saltak (Alt B) vs. 10° pulttak/oppløft (Alt C) mot eksisterende 95×55 cm pipe</text>',
    ]

    # Top-left: Fasade Vest — Takalternativ B (20° saltak)
    d1 = Draw(ox=320, oy=960, scale=0.68)
    draw_west_elevation(
        d1,
        "B_saltak20",
        "FASADE VEST — Takalternativ B: 20° slakt saltak",
        "Klassisk gavluttrykk • Møne 1,8 m under hovedmøne • 28 cm klar av pipa",
        "#0284c7",
    )
    svg.extend(d1.els)

    # Top-right: Fasade Vest — Takalternativ C (10° pulttak)
    d2 = Draw(ox=1580, oy=960, scale=0.68)
    draw_west_elevation(
        d2,
        "C_pulttak10",
        "FASADE VEST — Takalternativ C: 10° pulttak / oppløft",
        "Enklest & billigst • Null gradrenner • 35 cm vest for hele pipa",
        "#059669",
    )
    svg.extend(d2.els)

    # Bottom-left: Fasade Sør
    d3 = Draw(ox=400, oy=1860, scale=0.68)
    draw_south_elevation(d3)
    svg.extend(d3.els)

    # Bottom-right: Takplan (exact 3D valley check!)
    d4 = Draw(ox=1620, oy=1295, scale=0.52)
    draw_roof_plan(d4)
    svg.extend(d4.els)

    svg.append("</svg>")
    out = os.path.join(OUT_DIR, "fasader_alt1_takalternativer.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
