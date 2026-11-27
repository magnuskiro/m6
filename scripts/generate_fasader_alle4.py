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


def draw_west(d: ElevDraw):
    """FASADE VEST (Left = Nord y=0, Right = Sør y=1166).
    Original chimney sits ON THE WEST ROOF SLOPE at y=720..775, x_roof=135..230 -> roof intersection at -697..-758, top at -865 (BELOW ridge -890!)."""
    d.rect(-260, -1020, 1520, 1020, fill="#f0f9ff", opacity=0.45)
    d.rect(-260, 0, 1520, 42, fill="#dcfce7", opacity=0.8)
    d.line(-260, 0, 1260, 0, stroke="#15803d", sw=3)

    # 1-story north extension + covered NW entry porch (left, y=-210..0) with PARALLEL 32.7° SALTAK (peak Z=494 cm!)
    d.rect(-210, -290, 210, 290, fill="#f8fafc", stroke="#334155", sw=2)
    d.siding(-210, -290, 210, 250)
    d.rect(-210, -40, 210, 40, fill="#64748b", stroke="#334155", sw=1.5)
    # Porch column + railing + visible 140/210 entrance door inside covered NW porch
    d.rect(-198, -285, 16, 245, fill="#ffffff", stroke="#334155", sw=1.6)
    d.solid_door(-138, -248, 105, 208, glass_top=True)
    # Parallel 32.7° saltak west roof slope (eaves -285, ridge -494 running N-S!)
    d.poly([(-228, -285), (0, -285), (0, -494), (-228, -494)], fill="#1e293b", stroke="#0f172a", sw=2)
    for ry in range(-470, -285, 30):
        d.line(-225, ry, -2, ry, stroke="#334155", sw=1)
    d.text(-85, -262, "Inngang 140/210", size=11, weight="700", fill="#475569")

    # Main wall (0..1166)
    d.rect(0, -610, 1166, 610, fill="#ffffff", stroke="#1e293b", sw=2.5)
    d.siding(0, -610, 1166, 570)
    d.rect(0, -40, 1166, 40, fill="#64748b", stroke="#334155", sw=1.5)

    # Main roof (32.7°, eaves -610, ridge -890)
    d.poly([(-35, -600), (1201, -600), (1201, -890), (-35, -890)], fill="#1e293b", stroke="#0f172a", sw=2.5)
    for ry in range(-860, -600, 34):
        d.line(-32, ry, 1198, ry, stroke="#334155", sw=1)
    # 2 skylights on west slope
    d.rect(145, -825, 110, 135, fill="#93c5fd", stroke="#0f172a", sw=2.2)
    d.rect(975, -825, 110, 135, fill="#93c5fd", stroke="#0f172a", sw=2.2)

    # ORIGINAL CHIMNEY — CORRECTLY ON WEST ROOF SLOPE (y=720..775, base at slope ~-730, top ~-880, right near ridge level, NOT sitting on ridge!)
    d.rect(720, -895, 55, 185, fill="#7c2d12", stroke="#431407", sw=2.2)
    d.rect(714, -905, 67, 12, fill="#475569", stroke="#0f172a", sw=1.4)
    d.text(748, -922, "Orig. pipe (på vestflate)", size=13, weight="700", fill="#9a3412")

    # Main wall kors-sprosse windows (aligned with floor plan!)
    # Trapp (y=30..250 -> center 140), Vask/Bod (y=262..410 -> center 335), Spisestue (y=930..1166 -> center 1048)
    d.kors_win(90, -248, 105, 140, single=False)   # Trapp 1. etg
    d.kors_win(90, -528, 105, 140, single=False)   # Trapp 2. etg
    d.kors_win(285, -248, 72, 130, single=True)    # Vask 1. etg
    d.kors_win(285, -528, 72, 130, single=True)    # Bod/Vask 2. etg
    d.kors_win(992, -248, 115, 145, single=False)  # Spis 1. etg
    d.kors_win(992, -528, 115, 145, single=False)  # Spis 2. etg

    # Enclosed 2-story WEST EXTENSION (y=410..930 = 5.20 m wide, 20° gable!)
    d.rect(930, -605, 22, 605, fill="#94a3b8", opacity=0.35)
    d.rect(410, -610, 520, 610, fill="#ffffff", stroke="#0f172a", sw=3)
    d.siding(410, -610, 520, 570)
    d.rect(410, -40, 520, 40, fill="#475569", stroke="#1e293b", sw=1.5)

    # Two paired classic kors-sprosse windows on 1st and 2nd floor (symmetrical in 5.20m wing)
    d.kors_win(475, -255, 165, 155, single=False)
    d.kors_win(700, -255, 165, 155, single=False)
    d.kors_win(475, -530, 165, 150, single=False)
    d.kors_win(700, -530, 165, 150, single=False)

    # 20° low-pitched gable roof (peak -708 -> 182 cm below main ridge -890!)
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


def draw_east(d: ElevDraw):
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

    # Main roof (32.7°) with 3 symmetrical skylights (as in architect's fasader-1.jpg!)
    d.poly([(-35, -600), (1201, -600), (1201, -890), (-35, -890)], fill="#1e293b", stroke="#0f172a", sw=2.5)
    for ry in range(-860, -600, 34):
        d.line(-32, ry, 1198, ry, stroke="#334155", sw=1)
    for sx in [165, 528, 890]:
        d.rect(sx, -825, 110, 135, fill="#93c5fd", stroke="#0f172a", sw=2.2)

    # FOUR CLEAN VERTICAL KORS-SPROSSE WINDOW AXES matching exact room layout:
    # Axis 1 (Sørøst, y=990 -> x=176): 1.etg Kjøkken / 2.etg Sov 3
    # Axis 2 (Midt-sør, y=710 -> x=456): 1.etg Sov/Kontor (sør) / 2.etg Sov 2
    # Axis 3 (Midt-nord, y=495 -> x=671): 1.etg Sov/Kontor (pult) / 2.etg Bad
    # Axis 4 (Nordøst, y=220 -> x=946): 1.etg Bad / 2.etg Hovedsoverom
    axes = [
        (176, "Kjøkken", "Sov 3"),
        (456, "Sov (1.etg)", "Sov 2"),
        (671, "Sov/Pult", "Bad 2.etg"),
        (946, "Bad 1.etg", "Hovedsov"),
    ]
    for cx, lbl1, lbl2 in axes:
        d.kors_win(cx - 62, -248, 124, 145, single=False)
        d.kors_win(cx - 62, -528, 124, 145, single=False)
        d.text(cx, -75, lbl1, size=11, weight="700", fill="#64748b")
        d.text(cx, -355, lbl2, size=11, weight="700", fill="#64748b")

    # 1-story NORTH EXTENSION on the right (x=1166..1376 = 2.10 m north!) with SALTAK (ridge running N-S!)
    d.rect(1166, -290, 210, 290, fill="#ffffff", stroke="#0f172a", sw=2.5)
    d.siding(1166, -290, 210, 250)
    d.rect(1166, -40, 210, 40, fill="#475569", stroke="#1e293b", sw=1.5)
    # 110/210 external basement stair door + Utebod door on east face of north extension!
    d.solid_door(1182, -245, 82, 205, glass_top=True)   # Kjellernedgang 110/210
    d.solid_door(1280, -245, 76, 205, glass_top=False)  # Utebod
    d.text(1223, -260, "Kjeller", size=11, weight="700", fill="#475569")
    d.text(1318, -260, "Bod", size=11, weight="700", fill="#475569")
    # Parallel 32.7° saltak east roof slope (eaves -285, ridge -494!)
    d.poly([(1166, -285), (1395, -285), (1395, -494), (1166, -494)], fill="#1e293b", stroke="#0f172a", sw=2)
    for ry in range(-470, -285, 30):
        d.line(1168, ry, 1392, ry, stroke="#334155", sw=1)

    d.dim_h(0, 1166, 70, "11,66 m (eksisterende lengde)", bold=True)
    d.dim_h(1166, 1376, 70, "2,10 m nord", color="#ea580c", bold=True)
    d.text(650, -1065, "FASADE ØST (Nordøst)", size=23, weight="800", fill="#0f172a")
    d.text(650, -1032, "4 stramme kors-sprosse-akser (romjustert!) • 3 takvinduer • Kjellernedgang + Utebod i nord-tilbygg", size=14, weight="600", fill="#059669")


def draw_south(d: ElevDraw):
    """FASADE SØR (Left = Vest x=-320..0, Right = Main x=0..866).
    Original chimney at x=135..230 (95 cm wide EAST-WEST!) rising on the WEST roof slope!"""
    d.rect(-400, -1020, 1380, 1020, fill="#f0f9ff", opacity=0.45)
    d.rect(-400, 0, 1380, 42, fill="#dcfce7", opacity=0.8)
    d.line(-400, 0, 980, 0, stroke="#15803d", sw=3)

    # West extension side wall (x=-320..0)
    d.rect(-320, -610, 320, 610, fill="#f8fafc", stroke="#1e293b", sw=2.5)
    d.siding(-320, -610, 320, 570)
    d.rect(-320, -40, 320, 40, fill="#64748b", stroke="#334155", sw=1.5)
    d.kors_win(-225, -248, 130, 145, single=False)  # Stue 1. etg
    d.kors_win(-225, -528, 130, 145, single=False)  # Loftstue 2. etg

    # 20° gable roof of west wing in side profile (eaves -600, ridge -708, meets main slope at x=147)
    d.poly([(-345, -600), (-345, -708), (147, -708), (0, -600)], fill="#1e293b", stroke="#0f172a", sw=2.2)

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

    # South gable windows & terrace door (kors-sprosser!)
    d.kors_win(135, -248, 145, 145, single=False)   # Spisestue 1. etg
    d.french_door_kors(465, -250, 160, 210)         # Terrassedør fra kjøkken/allrom
    d.kors_win(135, -528, 145, 145, single=False)   # Opphold 2. etg
    d.kors_win(575, -528, 145, 145, single=False)   # Sov 3 (2. etg)
    d.kors_win(375, -768, 116, 115, single=False)   # Loft gavl (220 cm takhøyde)

    # Timber terrace deck
    d.rect(360, -24, 540, 24, fill="#d97706", opacity=0.4, stroke="#92400e", sw=1.8)
    d.text(630, -7, "Markterrasse syd", size=12, weight="700", fill="#78350f")

    d.dim_h(-320, 0, 70, "3,20 m vest", color="#0284c7", bold=True)
    d.dim_h(0, 866, 70, "8,66 m (eksist. bredde)", bold=True)
    d.text(275, -1065, "FASADE SØR (Sørgavl — uten syd-tilbygg)", size=23, weight="800", fill="#0f172a")
    d.text(275, -1032, "Orig. pipe plassert riktig på vestre takflate (x=1,35–2,30 m, IKKE på mønet!) • Kors-sprosser", size=14, weight="600", fill="#9a3412")


def draw_north(d: ElevDraw):
    """FASADE NORD — Exact match to Magnus's hand sketch!
    Left = Øst (x_plot=0), Right = Vest (x_plot=866), Far Right = West extension (x_plot=866..1196, 3.30 m!).
    - 1-story north extension (x_plot=0..635) with PARALLEL 32.7° SALTAK (peak at x=317, Z=494 cm!),
      narrow window (Utebod) + double kors-sprosse window (Vindfang) + covered portico with railing (x=485..635).
    - Right of north extension on main north wall (x=635..866): narrow single 1st-floor window + double 2nd-floor kors-sprosse window.
    - NO window on left/east 2nd floor (Hovedsoverom); centered loft gable window.
    - West extension north face (x=866..1196): double kors-sprosse window in BOTH 1st and 2nd floor!
    """
    d.rect(-100, -1020, 1410, 1020, fill="#f0f9ff", opacity=0.45)
    d.rect(-100, 0, 1410, 42, fill="#dcfce7", opacity=0.8)
    d.line(-100, 0, 1310, 0, stroke="#15803d", sw=3)

    # West extension on the RIGHT (x_plot=866..1196 = 3.30 m deep!)
    d.rect(866, -610, 330, 610, fill="#f8fafc", stroke="#1e293b", sw=2.5)
    d.siding(866, -610, 330, 570)
    d.rect(866, -40, 330, 40, fill="#64748b", stroke="#334155", sw=1.5)
    # 1st & 2nd floor double kors-sprosse windows on NORTH face of west extension (as sketched by Magnus!)
    d.kors_win(965, -248, 135, 145, single=False)
    d.kors_win(965, -528, 135, 145, single=False)
    # West wing roof profile: solid 20° saltak (-708, clears chimney!) + dashed line showing 32.7° height (-778)
    d.poly([(719, -708), (1221, -708), (1221, -600), (866, -600)], fill="#1e293b", stroke="#0f172a", sw=2.2)

    # Original chimney on west slope (x_plot = 866 - 230..135 = 636..731, right/west side of main ridge!)
    d.rect(636, -895, 95, 200, fill="#7c2d12", stroke="#431407", sw=2.2)
    d.rect(630, -905, 107, 12, fill="#475569", stroke="#0f172a", sw=1.4)
    d.text(683, -922, "Orig. pipe (bak)", size=12, weight="700", fill="#9a3412")

    # Main north gable (x_plot=0..866, 32.7° pitch -> peak -890 at x=433)
    d.poly([(0, 0), (866, 0), (866, -610), (433, -890), (0, -610)], fill="#ffffff", stroke="#0f172a", sw=3)
    d.siding(0, -610, 866, 570)
    d.rect(0, -40, 866, 40, fill="#64748b", stroke="#334155", sw=1.5)
    d.poly([(-35, -588), (433, -906), (901, -588), (885, -578), (433, -885), (-19, -578)], fill="#1e293b", stroke="#0f172a", sw=2)

    # Main north gable windows (EXACTLY as sketched by Magnus!):
    # NO window on left/east 2. etg (Hovedsoverom)!
    d.kors_win(700, -245, 74, 138, single=True)     # 1. etg narrow single window right of entry porch (Trapp)
    d.kors_win(585, -528, 135, 145, single=False)   # 2. etg double kors-sprosse window right of north gable peak
    d.kors_win(375, -768, 116, 115, single=False)   # Centered loft gable window

    # 1-STORY NORTH EXTENSION (x_plot = 0..635 = 6.35 m wide, PARALLEL 32.7° SALTAK!)
    # Enclosed Utebod + Vindfang (x_plot = 0..485)
    d.rect(0, -290, 485, 290, fill="#ffffff", stroke="#0f172a", sw=2.8)
    d.siding(0, -290, 485, 250)
    d.rect(0, -40, 485, 40, fill="#475569", stroke="#1e293b", sw=1.5)
    d.kors_win(85, -238, 72, 132, single=True)      # Narrow single window (Utebod / kjellerlys)
    d.kors_win(240, -242, 135, 140, single=False)   # Double kors-sprosse window (Vindfang)
    d.text(121, -72, "Bod", size=12, weight="700", fill="#64748b")
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

    d.dim_h(0, 485, 70, "4,85 m (Bod + Vindfang)", color="#ea580c", bold=True)
    d.dim_h(485, 635, 70, "1,50 m", color="#475569")
    d.dim_h(635, 866, 70, "2,31 m", color="#475569")
    d.dim_h(866, 1196, 70, "3,30 m vest", color="#0284c7", bold=True)
    d.text(560, -1065, "FASADE NORD (Synkronisert med nordfasade-skissen!)", size=23, weight="800", fill="#0f172a")
    d.text(560, -1032, "Parallelt 32,7° saltak på nord-tilbygg • Rekkverk i inngangsparti • Ingen nordvindu på Hovedsov • Dobbeltvindu på vest-tilbygg", size=13, weight="600", fill="#ea580c")


def main():
    W, H = 2660, 2000
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        f'<rect width="{W}" height="{H}" fill="#faf9f6"/>',
        f'<rect x="0" y="0" width="{W}" height="135" fill="#0f172a"/>',
        f'<rect x="0" y="129" width="{W}" height="6" fill="#0284c7"/>',
        f'<text x="60" y="60" font-size="38" font-weight="800" fill="#ffffff">M6 (#50) — Alle 4 fasader (Alternativ 1: 5,20×3,20 m vest + Nord-tilbygg)</text>',
        f'<text x="60" y="102" font-size="22" font-weight="500" fill="#cbd5e1">Korrigert pipeplassering (på vest-takflate, IKKE på mønet) • Norske kors-sprossevinduer • Romjustert mot 1:50-plantegning</text>',
    ]

    # Top-left: Fasade Vest
    d1 = ElevDraw(ox=285, oy=955, scale=0.68)
    draw_west(d1)
    svg.extend(d1.els)

    # Top-right: Fasade Øst
    d2 = ElevDraw(ox=1520, oy=955, scale=0.68)
    draw_east(d2)
    svg.extend(d2.els)

    # Bottom-left: Fasade Sør
    d3 = ElevDraw(ox=375, oy=1885, scale=0.68)
    draw_south(d3)
    svg.extend(d3.els)

    # Bottom-right: Fasade Nord
    d4 = ElevDraw(ox=1540, oy=1885, scale=0.68)
    draw_north(d4)
    svg.extend(d4.els)

    svg.append("</svg>")
    out = os.path.join(OUT_DIR, "fasader_alt1_alle4.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
