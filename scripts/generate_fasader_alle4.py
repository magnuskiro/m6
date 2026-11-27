#!/usr/bin/env python3
"""
Generate all 4 architectural facade elevations (Vest, Sør, Øst, Nord) in exact 1:100/1:50 scale
for Myrteveien 6 — Alternativ 1 (5.20m x 3.20m west extension with 20° low-pitched gable +
2.10m 1-story north extension for vindfang/kjellernedgang/utebod, NO south extension),
featuring:
  - Traditional Norwegian KORS-SPROSSER (4-pane cross-post / krysspost) windows throughout
  - EXACT chimney position ON THE WEST ROOF SLOPE (x=135..230 cm, NOT on the ridge!)
  - Exact room-to-window alignment across all 4 facades (including 4 vertical axes on East facade)
"""

import os

OUT_DIR = "/home/kiro/repos/m6/assets/images/drawings"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


class ElevDraw:
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

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1.5, dash=None, opacity=1.0):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        self.add(
            f'<rect x="{self.px(x):.1f}" y="{self.py(y):.1f}" width="{w*self.s:.1f}" height="{h*self.s:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}{op}/>'
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

    def siding(self, x, y, w, h, step=24):
        yy = y + step
        while yy < y + h - 4:
            self.line(x, yy, x + w, yy, stroke="#e2e8f0", sw=0.9)
            yy += step

    def kors_win(self, x, y, w=125, h=145, single=False):
        """Authentic Norwegian KORS-SPROSSE (krysspost) window:
        - Double window: 1 vertical center bar + 1 horizontal bar at 34% from top (4 clean panes '+')
        - Single window: 1 horizontal bar at 34% from top (2 clean panes matching adjacent height)
        """
        # White outer casing (omramming) + top drip cap (vannbrett)
        self.rect(x - 7, y - 7, w + 14, h + 14, fill="#ffffff", stroke="#475569", sw=1.4)
        self.rect(x - 11, y - 12, w + 22, 6, fill="#f1f5f9", stroke="#334155", sw=1.2)
        # Glass pane
        self.rect(x, y, w, h, fill="#cbd5e1", stroke="#1e293b", sw=1.8)
        self.rect(x + 2, y + 2, w - 4, h - 4, fill="#dbeafe", opacity=0.75)
        # Horizontal krysspost bar at 34% down from top
        hy = y + h * 0.34
        self.line(x, hy, x + w, hy, stroke="#ffffff", sw=4.2)
        self.line(x, hy, x + w, hy, stroke="#475569", sw=1.1)
        if not single:
            vx = x + w / 2
            self.line(vx, y, vx, y + h, stroke="#ffffff", sw=4.2)
            self.line(vx, y, vx, y + h, stroke="#475569", sw=1.1)

    def top_third_win(self, x, y, w=124, h=50):
        """Upper third (øvre 1/3) of a classic 4-pane Norwegian kors-sprosse window: 2 crisp panes matching adjacent top rows."""
        self.rect(x - 7, y - 7, w + 14, h + 14, fill="#ffffff", stroke="#475569", sw=1.4)
        self.rect(x - 11, y - 12, w + 22, 6, fill="#f1f5f9", stroke="#334155", sw=1.2)
        self.rect(x, y, w, h, fill="#cbd5e1", stroke="#1e293b", sw=1.8)
        self.rect(x + 2, y + 2, w - 4, h - 4, fill="#dbeafe", opacity=0.75)
        vx = x + w / 2
        self.line(vx, y, vx, y + h, stroke="#ffffff", sw=4.2)
        self.line(vx, y, vx, y + h, stroke="#475569", sw=1.1)

    def french_door_kors(self, x, y, w=160, h=210):
        """Double French terrace door with matching upper kors-sprosser."""
        self.rect(x - 7, y - 7, w + 14, h + 7, fill="#ffffff", stroke="#475569", sw=1.4)
        self.rect(x - 11, y - 12, w + 22, 6, fill="#f1f5f9", stroke="#334155", sw=1.2)
        self.rect(x, y, w, h, fill="#dbeafe", stroke="#1e293b", sw=2)
        # Solid bottom door panel
        self.rect(x + 2, y + h - 55, w - 4, 53, fill="#f8fafc", stroke="#475569", sw=1.4)
        # Center vertical stile + horizontal bar matching window transom line (34% of 145 = 50cm from top)
        self.line(x + w / 2, y, x + w / 2, y + h, stroke="#ffffff", sw=4.5)
        self.line(x + w / 2, y, x + w / 2, y + h, stroke="#334155", sw=1.3)
        hy = y + 50
        self.line(x, hy, x + w, hy, stroke="#ffffff", sw=4.0)
        self.line(x, hy, x + w, hy, stroke="#475569", sw=1.1)

    def solid_door(self, x, y, w=95, h=205, glass_top=True):
        self.rect(x - 6, y - 6, w + 12, h + 6, fill="#ffffff", stroke="#475569", sw=1.4)
        self.rect(x, y, w, h, fill="#f8fafc", stroke="#1e293b", sw=1.8)
        if glass_top:
            self.rect(x + 14, y + 18, w - 28, 65, fill="#dbeafe", stroke="#475569", sw=1.3)
        self.rect(x + 14, y + 100, w - 28, 82, fill="none", stroke="#94a3b8", sw=1.2)

    def dim_h(self, x1, x2, y, label, color="#334155", bold=False, dy=-10):
        self.line(x1, y, x2, y, stroke=color, sw=1.8)
        self.line(x1, y - 10, x1, y + 10, stroke=color, sw=1.8)
        self.line(x2, y - 10, x2, y + 10, stroke=color, sw=1.8)
        self.text((x1 + x2) / 2, y + dy, label, size=14, weight="700" if bold else "600", fill=color)

    def dim_v(self, x, y1, y2, label, color="#334155", bold=False, dx=-16):
        self.line(x, y1, x, y2, stroke=color, sw=1.8)
        self.line(x - 10, y1, x + 10, y1, stroke=color, sw=1.8)
        self.line(x - 10, y2, x + 10, y2, stroke=color, sw=1.8)
        self.text(x + dx, (y1 + y2) / 2, label, size=14, weight="700" if bold else "600", fill=color, rotate=-90)


def draw_west(d: ElevDraw, alt: int = 1):
    """FASADE VEST (Left = Nord y=0, Right = Sør y=1166).
    Original chimney sits ON THE WEST ROOF SLOPE at y=720..775, x_roof=135..230."""
    d.rect(-260, -1020, 1520, 1020, fill="#f0f9ff", opacity=0.45)
    d.rect(-260, 0, 1520, 42, fill="#dcfce7", opacity=0.8)
    d.line(-260, 0, 1260, 0, stroke="#15803d", sw=3)

    # 1-story north extension + covered NW entry porch (left, y=-nd..0) with PARALLEL 32.7° SALTAK (peak Z=494 cm!)
    nd = 210 if alt == 1 else 250
    d.rect(-nd, -290, nd, 290, fill="#f8fafc", stroke="#334155", sw=2)
    d.siding(-nd, -290, nd, 250)
    d.rect(-nd, -40, nd, 40, fill="#64748b", stroke="#334155", sw=1.5)
    d.rect(-nd + 12, -285, 16, 245, fill="#ffffff", stroke="#334155", sw=1.6)
    d.solid_door(-nd + 68, -248, 105, 208, glass_top=True)
    d.poly([(-nd - 18, -285), (0, -285), (0, -494), (-nd - 18, -494)], fill="#1e293b", stroke="#0f172a", sw=2)
    for ry in range(-470, -285, 30):
        d.line(-nd - 15, ry, -2, ry, stroke="#334155", sw=1)
    d.text(-nd / 2 + 12, -262, "Inngang 140/210", size=11, weight="700", fill="#475569")

    # Main wall (0..1166)
    d.rect(0, -610, 1166, 610, fill="#ffffff", stroke="#1e293b", sw=2.5)
    d.siding(0, -610, 1166, 570)
    d.rect(0, -40, 1166, 40, fill="#64748b", stroke="#334155", sw=1.5)

    # Main roof (32.7°, eaves -610, ridge -890)
    d.poly([(-35, -600), (1201, -600), (1201, -890), (-35, -890)], fill="#1e293b", stroke="#0f172a", sw=2.5)
    for ry in range(-860, -600, 34):
        d.line(-32, ry, 1198, ry, stroke="#334155", sw=1)
    # 2 skylights on west slope
    if alt == 1:
        d.rect(145, -825, 110, 135, fill="#93c5fd", stroke="#0f172a", sw=2.2)
        d.rect(975, -825, 110, 135, fill="#93c5fd", stroke="#0f172a", sw=2.2)
    else:
        d.rect(105, -825, 110, 135, fill="#93c5fd", stroke="#0f172a", sw=2.2)
        d.rect(939, -825, 110, 135, fill="#93c5fd", stroke="#0f172a", sw=2.2)

    # ORIGINAL CHIMNEY — CORRECTLY ON WEST ROOF SLOPE (y=720..775)
    d.rect(720, -895, 55, 185, fill="#7c2d12", stroke="#431407", sw=2.2)
    d.rect(714, -905, 67, 12, fill="#475569", stroke="#0f172a", sw=1.4)
    d.text(748, -922, "Orig. pipe (på vestflate)", size=13, weight="700", fill="#9a3412")

    if alt == 1:
        # Alt 1: Main wall flanking windows (Trapp, Vask, Spisestue) + 5.20m wing (410..930, 20° gable)
        d.kors_win(90, -248, 105, 140, single=False)
        d.kors_win(90, -528, 105, 140, single=False)
        d.kors_win(285, -248, 72, 130, single=True)
        d.kors_win(285, -528, 72, 130, single=True)
        d.kors_win(992, -248, 115, 145, single=False)
        d.kors_win(992, -528, 115, 145, single=False)

        d.rect(930, -605, 22, 605, fill="#94a3b8", opacity=0.35)
        d.rect(410, -610, 520, 610, fill="#ffffff", stroke="#0f172a", sw=3)
        d.siding(410, -610, 520, 570)
        d.rect(410, -40, 520, 40, fill="#475569", stroke="#1e293b", sw=1.5)

        d.kors_win(475, -255, 165, 155, single=False)
        d.kors_win(700, -255, 165, 155, single=False)
        d.kors_win(475, -530, 165, 150, single=False)
        d.kors_win(700, -530, 165, 150, single=False)

        d.poly([(385, -600), (670, -708), (955, -600)], fill="#ffffff", stroke="#0f172a", sw=3)
        for sy in [-625, -650, -675]:
            frac = (-sy - 600) / 108.0
            hw = 285 * (1.0 - frac) - 10
            if hw > 20:
                d.line(670 - hw, sy, 670 + hw, sy, stroke="#e2e8f0", sw=0.9)
        d.poly([(375, -595), (670, -722), (965, -595), (950, -588), (670, -704), (390, -588)], fill="#1e293b", stroke="#0f172a", sw=2)

        d.dim_h(0, 410, 70, "4,10 m", color="#475569")
        d.dim_h(410, 930, 70, "5,20 m (vest-tilbygg)", color="#0284c7", bold=True)
        d.dim_h(930, 1166, 70, "2,36 m", color="#475569")
        d.dim_v(-285, -890, 0, "8,9 m møne", bold=True, dx=-20)
        d.text(490, -1065, "FASADE VEST (Sørvest)", size=23, weight="800", fill="#0f172a")
        d.text(490, -1032, "Kors-sprosser • 20° slak saltak-gavl • Orig. pipe på vest-takflate (28 cm klar av gradrenne)", size=14, weight="600", fill="#0284c7")
    else:
        # Alt 2 (Catrines oppsett): 3.20 m from north + existing south wall (y=320..822 = 5.02 m wide, 3.44 m south) + PARALLEL 32.7° SALTAK (peak -771, 33 cm clear of chimney!)
        d.kors_win(95, -248, 130, 145, single=False)   # Trapp 1. etg (centered in 3.20 m north flank!)
        d.kors_win(95, -528, 130, 145, single=False)   # Trapp 2. etg
        d.kors_win(929, -248, 130, 145, single=False)  # Spis 1. etg (centered in 3.44 m south flank!)
        d.kors_win(929, -528, 130, 145, single=False)  # Spis 2. etg

        d.rect(822, -605, 18, 605, fill="#94a3b8", opacity=0.35)
        d.rect(320, -610, 502, 610, fill="#ffffff", stroke="#0f172a", sw=3)
        d.siding(320, -610, 502, 570)
        d.rect(320, -40, 502, 40, fill="#475569", stroke="#1e293b", sw=1.5)

        # Two symmetrical paired kors-sprosse windows in 5.02m wing (center 571)
        d.kors_win(382, -255, 155, 155, single=False)
        d.kors_win(605, -255, 155, 155, single=False)
        d.kors_win(382, -530, 155, 150, single=False)
        d.kors_win(605, -530, 155, 150, single=False)

        # PARALLEL 32.7° SALTAK GABLE (half_w=251 -> peak = -610 - 251*0.642 = -771!)
        d.poly([(295, -600), (571, -771), (847, -600)], fill="#ffffff", stroke="#0f172a", sw=3)
        for sy in [-625, -650, -675, -700, -725, -750]:
            frac = (-sy - 600) / 171.0
            hw = 276 * (1.0 - frac) - 10
            if hw > 20:
                d.line(571 - hw, sy, 571 + hw, sy, stroke="#e2e8f0", sw=0.9)
        d.poly([(285, -594), (571, -785), (857, -594), (842, -585), (571, -765), (300, -585)], fill="#1e293b", stroke="#0f172a", sw=2)

        d.dim_h(0, 320, 70, "3,20 m (nord)", color="#059669", bold=True)
        d.dim_h(320, 822, 70, "5,02 m (vest-tilbygg)", color="#059669", bold=True)
        d.dim_h(822, 1166, 70, "3,44 m (eksist. sørvegg)", color="#059669", bold=True)
        d.dim_v(-285, -890, 0, "8,9 m møne", bold=True, dx=-20)
        d.text(490, -1065, "FASADE VEST — ALT 2 (3,20 | 5,02 | 3,44 m)", size=23, weight="800", fill="#0f172a")
        d.text(490, -1032, "3,20 m fra nord + eksist. sørvegg vest • Parallelt 32,7° saltak (samme vinkel som hovedtak — 33 cm klar av pipe!)", size=13, weight="600", fill="#059669")


def draw_east(d: ElevDraw, alt: int = 1):
    """FASADE ØST (Left = Sør y=1166, Right = Nord y=0, plus 1-etg Nord-tilbygg to the right y=0..-210).
    Coordinate x_plot = 1166 - y, so Sør is at x=0, Nord is at x=1166, North ext is x=1166..1376!"""
    d.rect(-80, -1020, 1540, 1020, fill="#f0f9ff", opacity=0.45)
    d.rect(-80, 0, 1540, 42, fill="#dcfce7", opacity=0.8)
    d.line(-80, 0, 1460, 0, stroke="#15803d", sw=3)

    # Chimney top peeking slightly behind main ridge (x_plot = 1166 - 775..720 = 391..446)
    d.rect(391, -905, 55, 30, fill="#7c2d12", stroke="#431407", sw=2)
    d.rect(386, -914, 65, 10, fill="#475569", stroke="#0f172a", sw=1.3)
    d.text(418, -930, "Pipetopp (bak mønet)", size=12, weight="700", fill="#9a3412")

    # Main wall (x=0..1166)
    d.rect(0, -610, 1166, 610, fill="#ffffff", stroke="#1e293b", sw=2.5)
    d.siding(0, -610, 1166, 570)
    d.rect(0, -40, 1166, 40, fill="#64748b", stroke="#334155", sw=1.5)

    # Main roof (32.7°) with 4 skylights aligned directly over the 4 vertical east window axes!
    d.poly([(-35, -600), (1201, -600), (1201, -890), (-35, -890)], fill="#1e293b", stroke="#0f172a", sw=2.5)
    for ry in range(-860, -600, 34):
        d.line(-32, ry, 1198, ry, stroke="#334155", sw=1)
    for cx in [176, 456, 671, 946]:
        d.rect(cx - 55, -825, 110, 135, fill="#93c5fd", stroke="#0f172a", sw=2.2)

    # FOUR CLEAN VERTICAL KORS-SPROSSE WINDOW AXES matching exact room layout:
    # Axis 1 (Sørøst, y=990 -> x=176): 1.etg Kjøkken / 2.etg Sov 3
    # Axis 2 (Midt-sør, y=710 -> x=456): 1.etg Sov/Kontor (sør) / 2.etg Sov 2
    # Axis 3 (Midt-nord, y=495 -> x=671): 1.etg Sov/Pult (609..733) / 2.etg Bad (smalt 62 cm: 609..671 -> flukter m/ sydkant & midtpost!)
    # Axis 4 (Nordøst, y=220 -> x=946): 1.etg Bad / 2.etg Hovedsoverom
    axes = [
        (176, "Kjøkken", "Sov 3"),
        (456, "Sov (1.etg)", "Sov 2"),
        (671, "Sov/Pult", "Bad 2.etg"),
        (946, "Bad 1.etg", "Hovedsov"),
    ]
    for cx, lbl1, lbl2 in axes:
        if alt == 2 and cx == 946:
            # Upper third (øvre 1/3) of standard kors-sprosse window (124 x 50 cm, Z = 198..248, flush top!) ABOVE stair roof!
            d.top_third_win(cx - 62, -248, 124, 50)
            d.text(cx, -264, "Bad (øvre 1/3 vindu)", size=10, weight="700", fill="#059669")
        else:
            d.kors_win(cx - 62, -248, 124, 145, single=False)
            d.text(cx, -75, lbl1, size=11, weight="700", fill="#64748b")
        if cx == 671:
            # Bad 2.etg: half-width single kors-sprosse (62 x 145 cm, x=609..671 -> flush w/ SOUTH edge & center mullion of 1.etg window!)
            d.kors_win(cx - 62, -528, 62, 145, single=True)
            d.text(cx - 31, -355, lbl2, size=11, weight="700", fill="#64748b")
        else:
            d.kors_win(cx - 62, -528, 124, 145, single=False)
            d.text(cx, -355, lbl2, size=11, weight="700", fill="#64748b")

    # 1-story NORTH EXTENSION on the right (2.10 m in Alt 1, 2.50 m in Alt 2!) with PARALLEL 32.7° SALTAK
    nd = 210 if alt == 1 else 250
    d.rect(1166, -290, nd, 290, fill="#ffffff", stroke="#0f172a", sw=2.5)
    d.siding(1166, -290, nd, 250)
    d.rect(1166, -40, nd, 40, fill="#475569", stroke="#1e293b", sw=1.5)
    if alt == 1:
        # SINGLE centered 110/210 external door on east face of north extension (utebod accessed internally from basement landing!)
        d.solid_door(1224, -245, 96, 205, glass_top=True)
        d.text(1272, -260, "Kjeller / Bod (110/210)", size=11, weight="700", fill="#475569")
    # Parallel 32.7° saltak east roof slope (eaves -285, ridge -494!)
    d.poly([(1166, -285), (1166 + nd + 19, -285), (1166 + nd + 19, -494), (1166, -494)], fill="#1e293b", stroke="#0f172a", sw=2)
    for ry in range(-470, -285, 30):
        d.line(1168, ry, 1166 + nd + 16, ry, stroke="#334155", sw=1)

    if alt == 2:
        # Alt 2 (2,50 m north ext): Full 3,65 m external basement stair landing at SOUTH END OF U.04 (y=+60..+425 -> x_plot=1106..741)!
        # Top 3 steps open (1106..1031), then LOW HORIZONTAL roof (12° east, Z=186->163) runs 1031..741:
        # - Cleanly BELOW upper-third Bad 1.etg window (x_plot=884..1008)
        # - Stops 8 cm NORTH of Sov/Pult 1.etg window (x_plot=609..733) -> ZERO overlap!
        # - Enters straight into south end of U.04 -> direct access to central basement hallway!
        d.poly([(741, 0), (1106, 0), (1106, -65), (741, -65)], fill="#cbd5e1", stroke="#334155", sw=1.6)
        d.poly([(741, 0), (1106, 0), (1106, 15), (846, 195), (741, 195)], fill="#94a3b8", opacity=0.22, stroke="#64748b", sw=1.3, dash="5,4")
        d.text(795, 115, "Bunn-repos syd i U.04 (-1,95 m)", size=10, weight="700", fill="#475569")
        d.rect(1020, -163, 12, 163, fill="#ffffff", stroke="#334155", sw=1.5)
        d.rect(882, -163, 12, 163, fill="#ffffff", stroke="#334155", sw=1.5)
        d.rect(745, -163, 12, 163, fill="#ffffff", stroke="#334155", sw=1.5)
        d.poly([(738, -163), (1035, -163), (1035, -186), (738, -186)], fill="#1e293b", stroke="#0f172a", sw=2.0)
        d.line(740, -174, 1033, -174, stroke="#334155", sw=1.0)
        d.text(890, -110, "Lavt horisontalt tak (12° øst)", size=10, weight="700", fill="#059669")
        d.text(1070, -82, "3 åpne trinn", size=9, weight="600", fill="#475569")
        d.dim_h(741, 1106, 225, "3,65 m kjellertrapp -> bunn-repos syd i U.04 (rett inn i kjellergang!)", color="#0284c7", bold=True, dy=18)

    d.dim_h(0, 1166, 70, "11,66 m (eksisterende lengde)", bold=True)
    d.dim_h(1166, 1166 + nd, 70, "2,10 m nord" if alt == 1 else "2,50 m nord", color="#ea580c", bold=True)
    d.text(650, -1065, "FASADE ØST (Nordøst)", size=23, weight="800", fill="#0f172a")
    sub_e = (
        "4 stramme kors-sprosse-akser • 4 takvinduer linjert over vinduene • 1 sentrert kjeller-/boddør i nord-tilbygg"
        if alt == 1
        else "4 stramme kors-sprosse-akser • 4 takvinduer • Overbygd kjellertrapp trukket 1,50 m tilbake fra nordfasade (klar av badvindu!)"
    )
    d.text(650, -1032, sub_e, size=13, weight="600", fill="#059669")


def draw_south(d: ElevDraw, alt: int = 1):
    """FASADE SØR (Left = Vest x=-west_d..0, Right = Main x=0..866).
    Original chimney at x=135..230 (95 cm wide EAST-WEST!) rising on the WEST roof slope!"""
    west_d = 320 if alt == 1 else 280
    d.rect(-400, -1020, 1380, 1020, fill="#f0f9ff", opacity=0.45)
    d.rect(-400, 0, 1380, 42, fill="#dcfce7", opacity=0.8)
    d.line(-400, 0, 980, 0, stroke="#15803d", sw=3)

    # West extension side wall (x=-west_d..0) — symmetric double kors-sprosse windows 1st & 2nd floor
    d.rect(-west_d, -610, west_d, 610, fill="#f8fafc", stroke="#1e293b", sw=2.5)
    d.siding(-west_d, -610, west_d, 570)
    d.rect(-west_d, -40, west_d, 40, fill="#64748b", stroke="#334155", sw=1.5)
    win_w = 130
    wx = -west_d / 2 - win_w / 2
    d.kors_win(wx, -248, win_w, 145, single=False)  # Stue 1. etg
    d.kors_win(wx, -528, win_w, 145, single=False)  # Loftstue 2. etg

    # West wing roof profile: Alt 1 = 20° saltak (-708, x_stop=147); Alt 2 = 32.7° parallel saltak (-771, x_stop=251)
    z_wr = -708 if alt == 1 else -771
    x_st = 147 if alt == 1 else 251
    d.poly([(-west_d - 25, -600), (-west_d - 25, z_wr), (x_st, z_wr), (0, -600)], fill="#1e293b", stroke="#0f172a", sw=2.2)

    # ORIGINAL CHIMNEY (x=135..230 = 95 cm wide EAST-WEST, rising cleanly from WEST roof slope!)
    # Roof height at x=135 is -697, at x=230 is -758; top rises to ~-895 (just ~0.5-1m above slope / near ridge level!)
    d.rect(135, -895, 95, 200, fill="#7c2d12", stroke="#431407", sw=2.5)
    d.rect(128, -905, 109, 12, fill="#475569", stroke="#0f172a", sw=1.4)
    d.text(182, -922, "Orig. pipe 95 cm Ø–V", size=13, weight="700", fill="#9a3412")
    d.text(182, -906, "", size=10)

    # Main south gable (x=0..866)
    d.poly([(0, 0), (866, 0), (866, -610), (433, -890), (0, -610)], fill="#ffffff", stroke="#0f172a", sw=3)
    d.siding(0, -610, 866, 570)
    d.rect(0, -40, 866, 40, fill="#64748b", stroke="#334155", sw=1.5)
    d.poly([(-35, -588), (433, -906), (901, -588), (885, -578), (433, -885), (-19, -578)], fill="#1e293b", stroke="#0f172a", sw=2)

    # South gable — 100% SYMMETRIC around EXISTING centered veranda door openings (x=353..513, center=433)!
    # 1. etg: flanking kors-sprosse (Spisestue) + EXISTING centered veranda door + flanking kors-sprosse (Kjøkken)
    d.kors_win(105, -248, 130, 145, single=False)   # Spisestue 1. etg (symmetrisk venstre)
    d.french_door_kors(353, -250, 160, 210)         # Eksist. sentrert terrassedør 1. etg (x=353..513)
    d.kors_win(631, -248, 130, 145, single=False)   # Kjøkken 1. etg (symmetrisk høyre)
    # 2. etg: flanking kors-sprosse + EXISTING centered veranda door (Opphold 2.etg, vest for Sov 3 ved x=526!) + flanking kors-sprosse (Sov 3)
    d.kors_win(105, -528, 130, 145, single=False)   # Opphold 2. etg (symmetrisk venstre)
    d.french_door_kors(353, -530, 160, 208)         # Eksist. sentrert verandadør 2. etg (rett over 1. etg!)
    # Modern 2nd-floor south balcony (3,80 x 2,15 m = 8,2 m²) on 2 slim white columns (aligned w/ flanking windows x=243..623!)
    d.rect(249, -302, 14, 278, fill="#ffffff", stroke="#334155", sw=1.6)  # Left slim column down to terrace
    d.rect(603, -302, 14, 278, fill="#ffffff", stroke="#334155", sw=1.6)  # Right slim column down to terrace
    d.rect(243, -322, 380, 20, fill="#ffffff", stroke="#1e293b", sw=2.0)  # Balcony deck fascia
    d.rect(243, -424, 380, 6, fill="#1e293b")                              # Top matte-black railing bar
    d.rect(243, -330, 380, 5, fill="#1e293b")                              # Bottom railing bar
    for rx in range(254, 618, 18):
        d.line(rx, -418, rx, -330, stroke="#1e293b", sw=1.6)
    d.text(433, -545, "Moderne sydbalkong 8,2 m² (3,80 × 2,15 m på 2 søyler)", size=10, weight="700", fill="#047857")
    d.kors_win(631, -528, 130, 145, single=False)   # Sov 3 (2. etg, bredde 3,1 m)
    d.kors_win(375, -768, 116, 115, single=False)   # Loft gavl (sentrert rett over dørene!)

    # Timber terrace deck along main south gable
    d.rect(-15, -24, 905, 24, fill="#d97706", opacity=0.4, stroke="#92400e", sw=1.8)
    d.text(433, -7, "Markterrasse sør (fra sentrert verandadør 1. etg)", size=12, weight="700", fill="#78350f")

    d.dim_h(-west_d, 0, 70, "3,20 m vest" if alt == 1 else "2,80 m vest (+0,5 m mur)", color="#0284c7" if alt == 1 else "#059669", bold=True)
    d.dim_h(0, 866, 70, "8,66 m (eksist. bredde)", bold=True)
    d.text(275, -1065, "FASADE SØR (Sørgavl — uten syd-tilbygg)", size=23, weight="800", fill="#0f172a")
    d.text(275, -1032, "Orig. pipe plassert riktig på vestre takflate (x=1,35–2,30 m, IKKE på mønet!) • Sentrerte eksist. verandadører", size=14, weight="600", fill="#9a3412")


def draw_north(d: ElevDraw, alt: int = 1):
    """FASADE NORD — Exact match to Magnus's hand sketch!
    Left = Øst (x_plot=0), Right = Vest (x_plot=866), Far Right = West extension (3.30 m in Alt 1, 2.80 m in Alt 2)."""
    west_d = 330 if alt == 1 else 280
    d.rect(-100, -1020, 1410, 1020, fill="#f0f9ff", opacity=0.45)
    d.rect(-100, 0, 1410, 42, fill="#dcfce7", opacity=0.8)
    d.line(-100, 0, 1310, 0, stroke="#15803d", sw=3)

    # West extension on the RIGHT (x_plot=866..866+west_d)
    d.rect(866, -610, west_d, 610, fill="#f8fafc", stroke="#1e293b", sw=2.5)
    d.siding(866, -610, west_d, 570)
    d.rect(866, -40, west_d, 40, fill="#64748b", stroke="#334155", sw=1.5)
    if alt == 1:
        # 1st floor DOUBLE VERANDA DOOR + 2nd floor double kors-sprosse window on NORTH face of west extension!
        d.french_door_kors(958, -250, 150, 210)
        d.kors_win(965, -528, 135, 145, single=False)
        d.rect(925, -22, 245, 22, fill="#d97706", opacity=0.38, stroke="#92400e", sw=1.5)
        d.text(1048, -6, "Uteplass NV (verandadør)", size=11, weight="700", fill="#78350f")
        d.poly([(719, -708), (866 + west_d + 25, -708), (866 + west_d + 25, -600), (866, -600)], fill="#1e293b", stroke="#0f172a", sw=2.2)
    else:
        # Alt 2 (3.00 m deep, 5.02 m wide): centered 130 cm double kors-sprosse windows in 1st & 2nd floor + parallel 32.7° saltak (-771)!
        wx = 866 + west_d / 2 - 65
        d.kors_win(wx, -248, 130, 145, single=False)
        d.kors_win(wx, -528, 130, 145, single=False)
        d.poly([(615, -771), (866 + west_d + 25, -771), (866 + west_d + 25, -600), (866, -600)], fill="#1e293b", stroke="#0f172a", sw=2.2)

    # Original chimney on west slope (x_plot = 866 - 230..135 = 636..731, right/west side of main ridge!)
    d.rect(636, -895, 95, 200, fill="#7c2d12", stroke="#431407", sw=2.2)
    d.rect(630, -905, 107, 12, fill="#475569", stroke="#0f172a", sw=1.4)
    d.text(683, -922, "Orig. pipe (bak)", size=12, weight="700", fill="#9a3412")

    # Main north gable (x_plot=0..866, 32.7° pitch -> peak -890 at x=433)
    d.poly([(0, 0), (866, 0), (866, -610), (433, -890), (0, -610)], fill="#ffffff", stroke="#0f172a", sw=3)
    d.siding(0, -610, 866, 570)
    d.rect(0, -40, 866, 40, fill="#64748b", stroke="#334155", sw=1.5)
    d.poly([(-35, -588), (433, -906), (901, -588), (885, -578), (433, -885), (-19, -578)], fill="#1e293b", stroke="#0f172a", sw=2)

    # Main north gable windows (aligned flush on west edge X=128 -> x_plot=738, clear of stair mid-landing X=36..126!):
    # NO window on left/east 2. etg (Hovedsoverom)!
    d.kors_win(676, -248, 62, 145, single=True)     # 1. etg half 62 cm window in Trapp (X=128..190 -> flush w/ west edge & center mullion of 2.etg!)
    d.kors_win(614, -528, 124, 145, single=False)   # 2. etg full 124 cm window in Trapp (X=128..252 -> 80 cm clear above 32,7° north-ext roof!)
    d.kors_win(375, -768, 116, 115, single=False)   # Centered loft gable window

    # 1-STORY NORTH EXTENSION (x_plot = 0..635 = 6.35 m wide, PARALLEL 32.7° SALTAK!)
    if alt == 2:
        # Subtle recessed side view of low horizontal east-sloping stair roof (12° east, Z=186->163, set back 2,25 m behind north facade!)
        d.rect(-115, -65, 115, 65, fill="#cbd5e1", stroke="#475569", sw=1.4, opacity=0.85)
        d.rect(-112, -163, 12, 98, fill="#f8fafc", stroke="#475569", sw=1.3)
        d.poly([(-124, -161), (0, -186), (0, -176), (-124, -151)], fill="#1e293b", stroke="#0f172a", sw=1.6)
        d.text(-68, -206, "Kjellertak", size=10, weight="700", fill="#059669")
        d.text(-68, -193, "(12° øst, bak)", size=9, weight="600", fill="#475569")

    # Enclosed Utebod/Vaskerom + Vindfang (x_plot = 0..485)
    d.rect(0, -290, 485, 290, fill="#ffffff", stroke="#0f172a", sw=2.8)
    d.siding(0, -290, 485, 250)
    d.rect(0, -40, 485, 40, fill="#475569", stroke="#1e293b", sw=1.5)
    if alt == 1:
        d.kors_win(85, -238, 72, 132, single=True)      # Narrow single window (Utebod / kjellerlys)
        d.kors_win(240, -242, 135, 140, single=False)   # Double kors-sprosse window (Vindfang)
        d.text(121, -72, "Bod", size=12, weight="700", fill="#64748b")
        d.text(308, -72, "Vindfang", size=12, weight="700", fill="#475569")
    else:
        d.kors_win(85, -238, 72, 132, single=True)      # Halvt vindu på vaskerommet mot øst (som nordfasade-skissen!)
        d.kors_win(240, -242, 135, 140, single=False)   # Helt dobbeltvindu i vindfanget!
        d.text(121, -72, "Vaskerom", size=12, weight="700", fill="#059669")
        d.text(308, -72, "Vindfang", size=12, weight="700", fill="#475569")

    # Covered entry porch / portico on RIGHT side of north extension (x_plot = 485..635) with classic vertical railing!
    d.rect(485, -40, 150, 40, fill="#94a3b8", stroke="#334155", sw=1.5)
    d.rect(618, -285, 16, 245, fill="#ffffff", stroke="#334155", sw=1.8)  # Right porch column
    # Classic wooden balustrade / railing (as sketched!)
    d.rect(485, -135, 136, 10, fill="#ffffff", stroke="#334155", sw=1.4)
    d.rect(485, -52, 136, 10, fill="#ffffff", stroke="#334155", sw=1.4)
    for rx in range(500, 616, 18):
        d.line(rx, -125, rx, -52, stroke="#475569", sw=2.2)

    # PARALLEL 32.7° SALTAK GABLE TRIANGLE (x=0..635, center x=317.5, peak Z=290 + 317.5*0.642 = 494!)
    d.poly([(0, -290), (317.5, -494), (635, -290)], fill="#ffffff", stroke="#0f172a", sw=2.6)
    for sy in [-318, -346, -374, -402, -430, -458]:
        frac = (-sy - 290) / 204.0
        hw = 317.5 * (1.0 - frac) - 10
        if hw > 20:
            d.line(317.5 - hw, sy, 317.5 + hw, sy, stroke="#e2e8f0", sw=0.9)
    # Matte black gable roof verge parallel to main roof!
    d.poly([(-28, -272), (317.5, -508), (663, -272), (648, -262), (317.5, -488), (-13, -262)], fill="#1e293b", stroke="#0f172a", sw=2)
    d.text(317.5, -524, "32,7° parallelt saltak", size=13, weight="700", fill="#ea580c")

    d.dim_h(0, 485, 70, "4,85 m (Bod + Vindfang)" if alt == 1 else "4,85 m (Vaskerom + Vindfang)", color="#ea580c", bold=True)
    d.dim_h(485, 635, 70, "1,50 m", color="#475569")
    d.dim_h(635, 866, 70, "2,31 m", color="#475569")
    d.dim_h(866, 866 + west_d, 70, "3,30 m vest" if alt == 1 else "2,80 m vest", color="#0284c7" if alt == 1 else "#059669", bold=True)
    d.text(560, -1065, "FASADE NORD (Synkronisert med nordfasade-skissen!)", size=23, weight="800", fill="#0f172a")
    sub_n = (
        "Parallelt 32,7° saltak på nord-tilbygg • Rekkverk i inngangsparti • Ingen nordvindu på Hovedsov • Verandadør nord på vest-tilbygg"
        if alt == 1
        else "Parallelt 32,7° saltak på BÅDE nord-tilbygg og vest-tilbygg • Rekkverk i inngangsparti • Ingen nordvindu på Hovedsov"
    )
    d.text(560, -1032, sub_n, size=13, weight="600", fill="#ea580c")


def build_sheet(alt: int):
    W, H = 2660, 2000
    accent = "#0284c7" if alt == 1 else "#059669"
    title = (
        "M6 (#50) — Alle 4 fasader (Alternativ 1: 5,20×3,20 m vest + Nord-tilbygg)"
        if alt == 1
        else "M6 (#50) — Alle 4 fasader (Alternativ 2: 5,02×2,80 m vest — 3,20 m nord + eksist. sørvegg)"
    )
    subtitle = (
        "Korrigert pipeplassering (på vest-takflate, IKKE på mønet) • Norske kors-sprossevinduer • Romjustert mot 1:50-plantegning"
        if alt == 1
        else "Catrines oppsett (2,80 m vest • 3,20 | 5,02 | 3,44 m) • Parallelt 32,7° saltak over hele huset (33 cm klar av pipe) • 2,50 m nord-tilbygg"
    )
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{W}" height="{H}" fill="#faf9f6"/>',
        f'<rect x="0" y="0" width="{W}" height="135" fill="#0f172a"/>',
        f'<rect x="0" y="129" width="{W}" height="6" fill="{accent}"/>',
        f'<text x="60" y="60" font-size="38" font-weight="800" fill="#ffffff">{esc(title)}</text>',
        f'<text x="60" y="102" font-size="22" font-weight="500" fill="#cbd5e1">{esc(subtitle)}</text>',
    ]

    # Top-left: Fasade Vest
    d1 = ElevDraw(ox=285, oy=955, scale=0.68)
    draw_west(d1, alt=alt)
    svg.extend(d1.els)

    # Top-right: Fasade Øst
    d2 = ElevDraw(ox=1520, oy=955, scale=0.68)
    draw_east(d2, alt=alt)
    svg.extend(d2.els)

    # Bottom-left: Fasade Sør
    d3 = ElevDraw(ox=375, oy=1885, scale=0.68)
    draw_south(d3, alt=alt)
    svg.extend(d3.els)

    # Bottom-right: Fasade Nord
    d4 = ElevDraw(ox=1540, oy=1885, scale=0.68)
    draw_north(d4, alt=alt)
    svg.extend(d4.els)

    svg.append("</svg>")
    out = os.path.join(OUT_DIR, f"fasader_alt{alt}_alle4.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out}")


def main():
    build_sheet(alt=1)
    build_sheet(alt=2)


if __name__ == "__main__":
    main()
