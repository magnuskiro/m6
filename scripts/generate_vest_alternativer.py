#!/usr/bin/env python3
"""
Generate architectural 2D SVG floor plans (1 px = 1 cm scale) matching Magnus's 1:50 hand sketches:
- Main house: exact original 1946/47 footprint (11.66m x 8.66m, NO south extension)
- 1-story north extension (y=-210..0, x=250..866): Vindfang (140/210 entrance from west),
  utvendig kjellernedgang (110/210 from east), and Utebod in NE
- 1. etg NE: Bad (~8.7 m²) + separate WC, mid-east Sov (~13.5 m²) w/ pult, south-facing bed & skyvedørskap
- 2. etg east: Hovedsoverom (13.3 m²), Bad (~6.8 m²), Sov (9.0 m²), Sov (9.2 m² / kitchen option)
- Exact original chimney: 95 cm (E-W) x 55 cm (N-S) at x=135..230, y=720..775
- Comparing Alternativ 1 (3.20m x 5.20m west extension) vs Alternativ 2 (2.30m x 4.60m symmetric west extension).
"""

import os

OUT_DIR = "/home/kiro/repos/m6/assets/images/drawings"


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


class PlanBuilder:
    """Coordinate system: x=0 is main west outer wall, x=866 is main east outer wall,
    y=0 is existing main north outer wall, y=1166 is main south outer wall.
    Negative x extends west; negative y extends north (1-story north extension)."""

    def __init__(self, ox: float, oy: float):
        self.ox = ox
        self.oy = oy
        self.els = []

    def p(self, x: float, y: float):
        return (self.ox + x, self.oy + y)

    def add(self, s: str):
        self.els.append(s)

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1, dash=None, rx=0, opacity=1.0):
        px, py = self.p(x, y)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        rxa = f' rx="{rx}"' if rx else ""
        self.add(
            f'<rect x="{px:.1f}" y="{py:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}{op}{rxa}/>'
        )

    def line(self, x1, y1, x2, y2, stroke="#2d3748", sw=2, dash=None, opacity=1.0):
        px1, py1 = self.p(x1, y1)
        px2, py2 = self.p(x2, y2)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        self.add(
            f'<line x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" y2="{py2:.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}"{da}{op}/>'
        )

    def path(self, d_cmds, fill="none", stroke="#2d3748", sw=2, dash=None, opacity=1.0):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        self.add(
            f'<path d="{d_cmds}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linejoin="miter"{da}{op}/>'
        )

    def poly(self, pts, fill="none", stroke="#2d3748", sw=2, dash=None, opacity=1.0):
        pts_str = " ".join(f"{self.ox + x:.1f},{self.oy + y:.1f}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        self.add(
            f'<polygon points="{pts_str}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linejoin="miter"{da}{op}/>'
        )

    def text(self, x, y, txt, size=24, weight="normal", fill="#1e293b", anchor="middle", rotate=0):
        px, py = self.p(x, y)
        rot = f' transform="rotate({rotate} {px:.1f} {py:.1f})"' if rotate else ""
        self.add(
            f'<text x="{px:.1f}" y="{py:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{rot}>{esc(txt)}</text>'
        )

    def room_label(self, cx, cy, name, area_str, sub=None):
        self.text(cx, cy - (10 if sub else 4), name, size=22, weight="700", fill="#1e293b")
        self.text(cx, cy + (15 if sub else 20), area_str, size=18, weight="600", fill="#475569")
        if sub:
            self.text(cx, cy + 37, sub, size=14, weight="500", fill="#64748b")

    def wall_h(self, x1, x2, y_center, thick=12, fill="#475569"):
        self.rect(x1, y_center - thick / 2, x2 - x1, thick, fill=fill)

    def wall_v(self, x_center, y1, y2, thick=12, fill="#475569"):
        self.rect(x_center - thick / 2, y1, thick, y2 - y1, fill=fill)

    def window_h(self, x1, x2, y_center, wall_t=30):
        self.rect(x1, y_center - wall_t / 2, x2 - x1, wall_t, fill="#ffffff", stroke="#334155", sw=2)
        self.line(x1, y_center - 5, x2, y_center - 5, stroke="#0284c7", sw=3.5)
        self.line(x1, y_center + 5, x2, y_center + 5, stroke="#0284c7", sw=3.5)

    def window_v(self, x_center, y1, y2, wall_t=30):
        self.rect(x_center - wall_t / 2, y1, wall_t, y2 - y1, fill="#ffffff", stroke="#334155", sw=2)
        self.line(x_center - 5, y1, x_center - 5, y2, stroke="#0284c7", sw=3.5)
        self.line(x_center + 5, y1, x_center + 5, y2, stroke="#0284c7", sw=3.5)

    def door(self, hx, hy, w, orientation="h_right_down", wall_t=14):
        px, py = self.p(hx, hy)
        if orientation == "h_right_down":
            self.rect(hx, hy - wall_t / 2 - 1, w, wall_t + 2, fill="#ffffff")
            self.line(hx, hy, hx, hy + w, stroke="#334155", sw=3.5)
            self.path(f"M {px:.1f} {py + w:.1f} A {w} {w} 0 0 0 {px + w:.1f} {py:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "h_right_up":
            self.rect(hx, hy - wall_t / 2 - 1, w, wall_t + 2, fill="#ffffff")
            self.line(hx, hy, hx, hy - w, stroke="#334155", sw=3.5)
            self.path(f"M {px:.1f} {py - w:.1f} A {w} {w} 0 0 1 {px + w:.1f} {py:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "h_left_down":
            self.rect(hx - w, hy - wall_t / 2 - 1, w, wall_t + 2, fill="#ffffff")
            self.line(hx, hy, hx, hy + w, stroke="#334155", sw=3.5)
            self.path(f"M {px:.1f} {py + w:.1f} A {w} {w} 0 0 1 {px - w:.1f} {py:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "h_left_up":
            self.rect(hx - w, hy - wall_t / 2 - 1, w, wall_t + 2, fill="#ffffff")
            self.line(hx, hy, hx, hy - w, stroke="#334155", sw=3.5)
            self.path(f"M {px:.1f} {py - w:.1f} A {w} {w} 0 0 0 {px - w:.1f} {py:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "v_down_right":
            self.rect(hx - wall_t / 2 - 1, hy, wall_t + 2, w, fill="#ffffff")
            self.line(hx, hy, hx + w, hy, stroke="#334155", sw=3.5)
            self.path(f"M {px + w:.1f} {py:.1f} A {w} {w} 0 0 1 {px:.1f} {py + w:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "v_down_left":
            self.rect(hx - wall_t / 2 - 1, hy, wall_t + 2, w, fill="#ffffff")
            self.line(hx, hy, hx - w, hy, stroke="#334155", sw=3.5)
            self.path(f"M {px - w:.1f} {py:.1f} A {w} {w} 0 0 0 {px:.1f} {py + w:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "v_up_right":
            self.rect(hx - wall_t / 2 - 1, hy - w, wall_t + 2, w, fill="#ffffff")
            self.line(hx, hy, hx + w, hy, stroke="#334155", sw=3.5)
            self.path(f"M {px + w:.1f} {py:.1f} A {w} {w} 0 0 0 {px:.1f} {py - w:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "v_up_left":
            self.rect(hx - wall_t / 2 - 1, hy - w, wall_t + 2, w, fill="#ffffff")
            self.line(hx, hy, hx - w, hy, stroke="#334155", sw=3.5)
            self.path(f"M {px - w:.1f} {py:.1f} A {w} {w} 0 0 1 {px:.1f} {py - w:.1f}", stroke="#64748b", sw=2, dash="6,5")

    def double_terrace_door_h(self, cx, y_center, total_w=160, wall_t=30, swing_down=True):
        half = total_w / 2
        self.rect(cx - half, y_center - wall_t / 2, total_w, wall_t, fill="#ffffff", stroke="#334155", sw=2)
        self.line(cx - half, y_center, cx + half, y_center, stroke="#0284c7", sw=3)
        sign = 1 if swing_down else -1
        px1, py = self.p(cx - half, y_center)
        px2, _ = self.p(cx + half, y_center)
        self.line(cx - half, y_center, cx - half, y_center + sign * half, stroke="#334155", sw=3)
        self.line(cx + half, y_center, cx + half, y_center + sign * half, stroke="#334155", sw=3)
        if swing_down:
            self.path(f"M {px1:.1f} {py + half:.1f} A {half} {half} 0 0 0 {px1 + half:.1f} {py:.1f}", stroke="#64748b", sw=1.8, dash="5,4")
            self.path(f"M {px2:.1f} {py + half:.1f} A {half} {half} 0 0 1 {px2 - half:.1f} {py:.1f}", stroke="#64748b", sw=1.8, dash="5,4")
        else:
            self.path(f"M {px1:.1f} {py - half:.1f} A {half} {half} 0 0 1 {px1 + half:.1f} {py:.1f}", stroke="#64748b", sw=1.8, dash="5,4")
            self.path(f"M {px2:.1f} {py - half:.1f} A {half} {half} 0 0 0 {px2 - half:.1f} {py:.1f}", stroke="#64748b", sw=1.8, dash="5,4")

    def dim_h(self, x1, x2, y, label, color="#334155", bold=False):
        self.line(x1, y, x2, y, stroke=color, sw=2)
        self.line(x1, y - 14, x1, y + 14, stroke=color, sw=2)
        self.line(x2, y - 14, x2, y + 14, stroke=color, sw=2)
        self.text((x1 + x2) / 2, y - 12, label, size=20, weight="700" if bold else "600", fill=color)

    def dim_v(self, x, y1, y2, label, color="#334155", bold=False, text_offset=-16):
        self.line(x, y1, x, y2, stroke=color, sw=2)
        self.line(x - 14, y1, x + 14, y1, stroke=color, sw=2)
        self.line(x - 14, y2, x + 14, y2, stroke=color, sw=2)
        self.text(x + text_offset, (y1 + y2) / 2, label, size=20, weight="700" if bold else "600", fill=color, rotate=-90)

    def stairs_u(self, x, y, w, h, floor=1):
        """Stacked 3-story U-stair matching 1:50 sketch:
        - Enter NE (1.etg) -> go west along north flight -> turn on west landing -> go east along south flight UP to SE (2.etg).
        - In 1.etg: basement door (lengst syd, SE) sits cleanly under the high end of the rising south flight!"""
        self.rect(x, y, w, h, fill="#e2e8f0", stroke="#64748b", sw=2)
        land_w = 82
        mid_y = y + h / 2
        steps = 7
        step_w = (w - land_w) / steps
        for i in range(steps):
            sx = x + land_w + i * step_w
            self.line(sx, y, sx, mid_y - 7, stroke="#64748b", sw=1.4)
            self.line(sx, mid_y + 7, sx, y + h, stroke="#64748b", sw=1.4)
        # Center handrail/stringer
        self.rect(x + land_w, mid_y - 7, w - land_w, 14, fill="#94a3b8")
        # Direction arrow (UP): NE -> west -> west landing -> east to SE (exact match to 1:50 sketch!)
        ax1, ay1 = self.p(x + w - 16, y + h * 0.24)
        ax2, ay2 = self.p(x + land_w * 0.5, y + h * 0.24)
        ax3, ay3 = self.p(x + land_w * 0.5, y + h * 0.76)
        ax4, ay4 = self.p(x + w - 18, y + h * 0.76)
        self.path(f"M {ax1:.1f} {ay1:.1f} L {ax2:.1f} {ay2:.1f} L {ax3:.1f} {ay3:.1f} L {ax4:.1f} {ay4:.1f}", stroke="#334155", sw=2.4)
        self.path(f"M {ax4 - 11:.1f} {ay4 - 9:.1f} L {ax4:.1f} {ay4:.1f} L {ax4 - 11:.1f} {ay4 + 9:.1f}", stroke="#334155", sw=2.4)
        if floor == 1:
            # Diagonal break line on rising south flight indicating basement stair door underneath (lengst syd)
            self.line(x + land_w + 26, y + h, x + w - 30, mid_y + 7, stroke="#0f172a", sw=2.2, dash="5,4")
            self.text(x + w - 42, y + 20, "OPP 2.etg", size=11, weight="700", fill="#0369a1")
            self.text(x + w - 46, y + h - 8, "NED KJELLER", size=10, weight="800", fill="#b45309")
        # Clean pill behind label
        self.rect(x + 10, mid_y - 25, 114, 50, fill="#ffffff", stroke="#cbd5e1", sw=1.2, rx=6, opacity=0.93)

    def basement_stairs_v(self, x, y, w, h, steps=11):
        """External basement stair along east wall descending south (top -> bottom)."""
        self.rect(x, y, w, h, fill="#e2e8f0", stroke="#64748b", sw=1.8)
        sh = h / steps
        for i in range(1, steps):
            self.line(x, y + i * sh, x + w, y + i * sh, stroke="#64748b", sw=1.3)
        ax, ay1 = self.p(x + w / 2, y + 18)
        _, ay2 = self.p(x + w / 2, y + h - 18)
        self.path(f"M {ax:.1f} {ay1:.1f} L {ax:.1f} {ay2:.1f}", stroke="#334155", sw=2.4)
        self.path(f"M {ax - 9:.1f} {ay2 - 11:.1f} L {ax:.1f} {ay2:.1f} L {ax + 9:.1f} {ay2 - 11:.1f}", stroke="#334155", sw=2.4)

    def basement_stairs_h(self, x, y, w, h):
        """External basement stair descending from east (right) to west (left)."""
        self.rect(x, y, w, h, fill="#e2e8f0", stroke="#64748b", sw=1.8)
        steps = 10
        sw = w / steps
        for i in range(1, steps):
            self.line(x + i * sw, y, x + i * sw, y + h, stroke="#64748b", sw=1.4)
        # Arrow pointing west (down)
        ax1, ay = self.p(x + w - 18, y + h / 2)
        ax2, _ = self.p(x + 22, y + h / 2)
        self.path(f"M {ax1:.1f} {ay:.1f} L {ax2:.1f} {ay:.1f}", stroke="#334155", sw=2.5)
        self.path(f"M {ax2 + 12:.1f} {ay - 10:.1f} L {ax2:.1f} {ay:.1f} L {ax2 + 12:.1f} {ay + 10:.1f}", stroke="#334155", sw=2.5)

    def chimney_and_fireplace(self, x=135, y=720, w=95, h=55, mode="west_insert"):
        """Exact original chimney core (95 cm east-west x 55 cm north-south) + compact H2O fireplace/stove."""
        if mode == "west_insert":
            # Compact/slank vannkappepeis (e.g. Brunner HKD 2.2 SK Flat / Spartherm Varia 2R-55h H2O):
            # 56 cm deep (x-56..x = 79..135) x 78 cm wide (y-11..y+67 = 709..787)
            fp_d, fp_w = 56, 78
            # 100 cm fire safety zone west of glass front (x-56-100..x-56 = -21..79 -> clears sofa at x=-30!)
            self.rect(x - fp_d - 100, y - 32, 100, 120, fill="#ef4444", opacity=0.09, stroke="#dc2626", sw=1.6, dash="7,5")
            self.text(x - fp_d - 50, y + 24, "100 cm", size=12, weight="700", fill="#dc2626")
            self.text(x - fp_d - 50, y + 39, "brannsone", size=11, weight="600", fill="#dc2626")
            # 30 cm non-combustible hearth plate (glass/skifer) west + corner south
            self.rect(x - fp_d - 30, y - 19, 30, 96, fill="#cbd5e1", opacity=0.65, stroke="#64748b", sw=1.3)
            self.rect(x - fp_d - 30, y + 67, fp_d + 30, 26, fill="#cbd5e1", opacity=0.55, stroke="#64748b", sw=1.2)
            # Nett 56 x 78 cm H2O fireplace surround + firebox
            self.rect(x - fp_d, y - 11, fp_d, fp_w, fill="#334155", stroke="#0f172a", sw=2.2, rx=2)
            self.rect(x - fp_d + 8, y - 1, fp_d - 16, 58, fill="#f97316", stroke="#9a3412", sw=1.5, rx=2)
            # 2-sided corner glass: west (toward sofa) + south (toward dining table)
            self.rect(x - fp_d, y + 3, 8, 50, fill="#fef08a", stroke="#b45309", sw=1.3)
            self.rect(x - fp_d + 6, y + 59, 40, 8, fill="#fef08a", stroke="#b45309", sw=1.2)
            self.text(x - fp_d / 2, y + 26, "H2O", size=12, weight="800", fill="#ffffff")
            self.text(x - fp_d / 2, y + 41, "PEIS", size=11, weight="800", fill="#ffffff")
            self.text(x - fp_d / 2, y + 112, "Vannkappe 56×78", size=12, weight="700", fill="#c2410c")
            self.text(x + w / 2, y - 12, "Orig. pipe 95×55", size=12, weight="700", fill="#9a3412")
        elif mode == "west_stove":
            # 2. etg: Compact optional Ø48 cm Scandinavian wood stove on flue 2 (1. etg H2O heats 2. etg!)
            self.rect(x - 76, y - 10, 76, 75, fill="#cbd5e1", opacity=0.45, stroke="#94a3b8", sw=1.3, dash="5,4")
            self.rect(x - 48, y + 4, 44, 44, fill="#475569", stroke="#0f172a", sw=2, rx=22)
            self.rect(x - 41, y + 11, 28, 30, fill="#f97316", stroke="#9a3412", sw=1.3, rx=14)
            self.rect(x - 48, y + 15, 7, 22, fill="#fef08a", stroke="#b45309", sw=1.2)
            self.text(x - 28, y + 83, "Valgfri nett ovn (løp 2)", size=11, weight="700", fill="#c2410c")
            self.text(x + w / 2, y - 12, "Orig. pipe 95×55", size=12, weight="700", fill="#9a3412")
        elif mode == "north_insert":
            # Alt 2 - 1. etg: Nett 78 x 56 cm H2O vannkappepeis on NORTH face of chimney (facing directly into sofakrok!)
            # x = 143..221 (narrower than 95 cm chimney!), y = 664..720 (56 cm north of chimney)
            fp_w, fp_d = 78, 56
            fx = x + (w - fp_w) / 2  # 143.5
            fy = y - fp_d            # 664
            # 100 cm fire safety zone west + north of 2-sided glass (west: x=43..143, north: y=564..664)
            self.rect(fx - 100, fy - 15, 100, fp_d + 45, fill="#ef4444", opacity=0.08, stroke="#dc2626", sw=1.5, dash="7,5")
            self.rect(fx - 10, fy - 95, fp_w + 20, 95, fill="#ef4444", opacity=0.08, stroke="#dc2626", sw=1.5, dash="7,5")
            self.text(fx - 50, fy + 26, "100 cm", size=11, weight="700", fill="#dc2626")
            self.text(fx + fp_w / 2, fy - 42, "100 cm brannsone", size=11, weight="700", fill="#dc2626")
            # 30 cm non-combustible hearth plate (glass/skifer) north + west of corner glass
            self.rect(fx - 30, fy - 30, fp_w + 38, 30, fill="#cbd5e1", opacity=0.65, stroke="#64748b", sw=1.2)
            self.rect(fx - 30, fy, 30, fp_d + 20, fill="#cbd5e1", opacity=0.65, stroke="#64748b", sw=1.2)
            # Nett 78 x 56 cm H2O fireplace surround + firebox
            self.rect(fx, fy, fp_w, fp_d, fill="#334155", stroke="#0f172a", sw=2.2, rx=2)
            self.rect(fx + 9, fy + 8, fp_w - 18, fp_d - 16, fill="#f97316", stroke="#9a3412", sw=1.5, rx=2)
            # 2-sided corner glass: NORTH + WEST (facing directly into sofa lounge!)
            self.rect(fx + 6, fy, fp_w - 14, 8, fill="#fef08a", stroke="#b45309", sw=1.3)
            self.rect(fx, fy + 6, 8, fp_d - 14, fill="#fef08a", stroke="#b45309", sw=1.3)
            self.text(fx + fp_w / 2, fy + 27, "H2O", size=12, weight="800", fill="#ffffff")
            self.text(fx + fp_w / 2, fy + 41, "PEIS", size=11, weight="800", fill="#ffffff")
            self.text(x + w / 2, y + h + 20, "Orig. pipe 95×55 + Vannkappe 78×56 (nord/vest)", size=12, weight="700", fill="#c2410c")
        elif mode == "north_stove":
            # Alt 2 - 2. etg: Compact optional Ø44 cm stove on NORTH face of chimney (facing loftstue sofa!)
            self.rect(x + 8, y - 72, 79, 72, fill="#cbd5e1", opacity=0.45, stroke="#94a3b8", sw=1.3, dash="5,4")
            self.rect(x + 25, y - 48, 44, 44, fill="#475569", stroke="#0f172a", sw=2, rx=22)
            self.rect(x + 32, y - 41, 30, 28, fill="#f97316", stroke="#9a3412", sw=1.3, rx=14)
            self.rect(x + 36, y - 48, 22, 7, fill="#fef08a", stroke="#b45309", sw=1.2)
            self.text(x + w / 2, y + h + 20, "Orig. pipe 95×55 + Valgfri nett ovn (løp 2)", size=12, weight="700", fill="#c2410c")
        else:
            # South-mounted stove fallback
            self.rect(x + 10, y + h, 75, 72, fill="#cbd5e1", opacity=0.6, stroke="#64748b", sw=1.3)
            self.rect(x + 22, y + h + 2, 50, 48, fill="#334155", stroke="#0f172a", sw=2, rx=6)
            self.rect(x + 30, y + h + 10, 34, 30, fill="#f97316", stroke="#9a3412", sw=1.4, rx=3)
            self.rect(x + 32, y + h + 42, 30, 8, fill="#fef08a", stroke="#b45309", sw=1.2)
            self.text(x + w + 10, y + h + 30, "Nett peis (sør)", size=12, weight="700", fill="#c2410c", anchor="start")
            self.text(x + w + 10, y + 32, "Orig. pipe 95×55", size=12, weight="700", fill="#9a3412", anchor="start")

        # Original 2-flue brick chimney core (always on top)
        self.rect(x, y, w, h, fill="#b45309", stroke="#78350f", sw=3)
        self.rect(x + 12, y + 12, 28, 31, fill="#fef3c7", stroke="#78350f", sw=2)
        self.rect(x + 54, y + 12, 28, 31, fill="#fef3c7", stroke="#78350f", sw=2)

    def double_bed(self, x, y, w=180, h=200, head="right"):
        self.rect(x, y, w, h, fill="#ffffff", stroke="#64748b", sw=2, rx=4)
        if head == "right":
            self.rect(x + w - 42, y + 14, 32, h / 2 - 22, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=4)
            self.rect(x + w - 42, y + h / 2 + 8, 32, h / 2 - 22, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=4)
            self.line(x + w - 58, y, x + w - 58, y + h, stroke="#cbd5e1", sw=1.5)
        elif head == "top":
            self.rect(x + 14, y + 10, w / 2 - 22, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=4)
            self.rect(x + w / 2 + 8, y + 10, w / 2 - 22, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=4)
            self.line(x, y + 58, x + w, y + 58, stroke="#cbd5e1", sw=1.5)
        elif head == "bottom":
            self.rect(x + 14, y + h - 42, w / 2 - 22, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=4)
            self.rect(x + w / 2 + 8, y + h - 42, w / 2 - 22, 32, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=4)
            self.line(x, y + h - 58, x + w, y + h - 58, stroke="#cbd5e1", sw=1.5)

    def single_bed(self, x, y, w=200, h=100, head="right"):
        self.rect(x, y, w, h, fill="#ffffff", stroke="#64748b", sw=2, rx=4)
        if head == "right":
            self.rect(x + w - 40, y + 14, 30, h - 28, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=4)
            self.line(x + w - 56, y, x + w - 56, y + h, stroke="#cbd5e1", sw=1.5)
        else:
            self.rect(x + 14, y + 10, w - 28, 30, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=4)

    def desk(self, x, y, w=125, h=58):
        self.rect(x, y, w, h, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=2)
        self.text(x + w / 2, y + h / 2 + 6, "Pult", size=14, fill="#64748b")

    def wardrobe(self, x, y, w, h, label=None):
        self.rect(x, y, w, h, fill="#f1f5f9", stroke="#64748b", sw=1.8)
        self.line(x, y, x + w, y + h, stroke="#cbd5e1", sw=1.2)
        self.line(x + w, y, x, y + h, stroke="#cbd5e1", sw=1.2)
        if label:
            rot = -90 if h > w * 1.8 else 0
            self.text(x + w / 2, y + h / 2 + 5, label, size=13, weight="600", fill="#475569", rotate=rot)

    def sofa_l(self, x, y, w_horiz=280, h_vert=210, depth=92, corner="bl"):
        if corner == "bl":
            self.rect(x, y, depth, h_vert, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)
            self.rect(x, y + h_vert - depth, w_horiz, depth, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)
            self.rect(x + 4, y + 4, 22, h_vert - 8, fill="#bae6fd", stroke="#0369a1", sw=1.2, rx=3)
            self.rect(x + 4, y + h_vert - 26, w_horiz - 8, 22, fill="#bae6fd", stroke="#0369a1", sw=1.2, rx=3)

    def coffee_table(self, x, y, w=130, h=75):
        self.rect(x, y, w, h, fill="#ffffff", stroke="#0369a1", sw=1.8, rx=8)

    def tv_bench(self, x, y, w=190, h=42):
        self.rect(x, y, w, h, fill="#334155", stroke="#0f172a", sw=2, rx=3)
        self.line(x + 25, y + 10, x + w - 25, y + 10, stroke="#38bdf8", sw=4)
        self.text(x + w / 2, y + 32, "TV-VEGG", size=14, weight="700", fill="#f8fafc")

    def armchair(self, x, y, w=78, h=78):
        self.rect(x, y, w, h, fill="#e0f2fe", stroke="#0369a1", sw=2, rx=8)

    def dining_table(self, cx, cy, w=240, h=100, seats=8):
        x, y = cx - w / 2, cy - h / 2
        n_side = (seats - 2) // 2
        for i in range(n_side):
            chx = x + 28 + i * ((w - 56) / max(1, n_side - 1)) - 20
            self.rect(chx, y - 34, 40, 30, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=4)
            self.rect(chx, y + h + 4, 40, 30, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=4)
        self.rect(x - 34, cy - 20, 30, 40, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=4)
        self.rect(x + w + 4, cy - 20, 30, 40, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=4)
        self.rect(x, y, w, h, fill="#fefce8", stroke="#a16207", sw=2.2, rx=4)
        self.text(cx, cy + 7, f"Spisebord ({seats} pers)", size=17, weight="600", fill="#854d0e")

    def kitchen_block(self, x_east_inner=836, y_north=760, y_south=1136, x_left=470):
        self.rect(x_left + 15, y_north, x_east_inner - x_left - 75, 60, fill="#f1f5f9", stroke="#475569", sw=2)
        self.text((x_left + 15 + x_east_inner - 60) / 2, y_north + 36, "Høyskap (kjøl/ovn)", size=14, fill="#475569")
        self.rect(x_east_inner - 60, y_north, 60, y_south - y_north - 10, fill="#f8fafc", stroke="#475569", sw=2)
        self.rect(x_east_inner - 50, y_north + 115, 40, 65, fill="#e0f2fe", stroke="#0284c7", sw=1.6, rx=3)
        self.rect(x_east_inner - 52, y_north + 235, 44, 65, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=2)
        ix = x_east_inner - 60 - 115 - 95
        iy = y_north + 60 + 110
        self.rect(ix, iy, 95, 195, fill="#fefce8", stroke="#a16207", sw=2, rx=3)
        self.text(ix + 47, iy + 102, "Øy", size=18, weight="700", fill="#854d0e")

    def wc(self, x, y, rot=0):
        if rot == 0:
            self.rect(x, y, 40, 62, fill="#ffffff", stroke="#475569", sw=1.8, rx=12)
            self.rect(x + 2, y, 36, 18, fill="#f1f5f9", stroke="#475569", sw=1.5)
        elif rot == 90:
            self.rect(x, y, 62, 40, fill="#ffffff", stroke="#475569", sw=1.8, rx=12)
            self.rect(x + 44, y + 2, 18, 36, fill="#f1f5f9", stroke="#475569", sw=1.5)
        elif rot == 270:
            self.rect(x, y, 62, 40, fill="#ffffff", stroke="#475569", sw=1.8, rx=12)
            self.rect(x, y + 2, 18, 36, fill="#f1f5f9", stroke="#475569", sw=1.5)

    def sink(self, x, y, w=80, h=45):
        self.rect(x, y, w, h, fill="#ffffff", stroke="#475569", sw=1.8, rx=3)
        self.rect(x + 12, y + 8, w - 24, h - 16, fill="#e0f2fe", stroke="#0284c7", sw=1.4, rx=6)

    def shower(self, x, y, w=90, h=90):
        self.rect(x, y, w, h, fill="#e0f2fe", stroke="#0284c7", sw=1.8)
        self.line(x, y, x + w, y + h, stroke="#7dd3fc", sw=1.3)
        self.line(x + w, y, x, y + h, stroke="#7dd3fc", sw=1.3)

    def tub(self, x, y, w=75, h=165):
        self.rect(x, y, w, h, fill="#ffffff", stroke="#0284c7", sw=2, rx=8)
        self.rect(x + 9, y + 12, w - 18, h - 24, fill="#e0f2fe", stroke="#38bdf8", sw=1.4, rx=14)

    def washer_dryer(self, x, y, count=2, vertical=False):
        for i in range(count):
            wx = x if vertical else x + i * 64
            wy = y + i * 64 if vertical else y
            self.rect(wx, wy, 60, 60, fill="#ffffff", stroke="#475569", sw=1.8, rx=3)
            self.text(wx + 30, wy + 36, "V" if i == 0 else "T", size=16, weight="700", fill="#475569")


def draw_outer_shell(pb: PlanBuilder, west_depth: float, wy1: float, wy2: float, north_ext: bool = False, north_depth: float = 210):
    """Draw 30cm insulated outer shell for main rectangle + west extension + optional 1-story north extension."""
    nd = north_depth
    if north_ext:
        # 1. etasje includes 1-story north extension (y = -nd..0, x = 250..866)
        outer_pts = [
            (0, 0),
            (250, 0),
            (250, -nd),
            (866, -nd),
            (866, 1166),
            (0, 1166),
            (0, wy2),
            (-west_depth, wy2),
            (-west_depth, wy1),
            (0, wy1),
        ]
        inner_pts = [
            (30, 30),
            (280, 30),
            (280, -nd + 30),
            (836, -nd + 30),
            (836, 1136),
            (30, 1136),
            (30, wy2 - 30),
            (-west_depth + 30, wy2 - 30),
            (-west_depth + 30, wy1 + 30),
            (30, wy1 + 30),
        ]
    else:
        # 2. etasje: straight existing north wall at y=0
        outer_pts = [
            (0, 0),
            (866, 0),
            (866, 1166),
            (0, 1166),
            (0, wy2),
            (-west_depth, wy2),
            (-west_depth, wy1),
            (0, wy1),
        ]
        inner_pts = [
            (30, 30),
            (836, 30),
            (836, 1136),
            (30, 1136),
            (30, wy2 - 30),
            (-west_depth + 30, wy2 - 30),
            (-west_depth + 30, wy1 + 30),
            (30, wy1 + 30),
        ]

    pb.poly(outer_pts, fill="#334155", stroke="#0f172a", sw=3)
    pb.poly(inner_pts, fill="#ffffff", stroke="#334155", sw=2)

    if north_ext:
        # Covered entry portico (1.50m wide next to Vindfang: x=100..250, y=-nd..0, matching Fasade Nord!)
        pb.rect(100, -nd, 150, nd, fill="#f1f5f9", stroke="#94a3b8", sw=2, dash="10,6", opacity=0.8)
        # Entry steps on west side of portico
        pb.rect(58, -nd + 55, 42, 130, fill="#e2e8f0", stroke="#64748b", sw=1.5)
        pb.line(79, -nd + 55, 79, -nd + 185, stroke="#64748b", sw=1.3)
        # Portico corner post & north railing line
        pb.rect(100, -nd, 14, 14, fill="#334155")
        pb.line(114, -nd + 7, 250, -nd + 7, stroke="#475569", sw=3)
        pb.text(175, -nd + 38, "Overbygd", size=15, weight="600", fill="#475569")
        pb.text(175, -nd + 58, "inngang", size=15, weight="600", fill="#475569")
        # Show existing north wall outer line at y=0 (dashed orange)
        pb.line(250, 0, 866, 0, stroke="#ea580c", sw=3, dash="14,10")
    else:
        # Show 1-story north extension roof outline (dashed gray) in 2. etg
        pb.rect(100, -nd, 766, nd, fill="#f1f5f9", stroke="#94a3b8", sw=2, dash="10,6", opacity=0.55)
        pb.text(483, -nd / 2, "Tak over 1-etg nord-tilbygg (portico / vindfang / vaskerom el. bod)", size=16, weight="600", fill="#64748b")

    # Existing west bump-out reference dashed line (2.28m deep, y=415..822)
    ex_pts = [(0, 415), (-228, 415), (-228, 822), (0, 822)]
    d = "M " + " L ".join(f"{pb.ox + x:.1f} {pb.oy + y:.1f}" for x, y in ex_pts)
    pb.path(d, stroke="#ea580c", sw=3.5, dash="14,10")


def draw_shared_east_floor1(pb: PlanBuilder, north_vaskerom: bool = False, north_depth: float = 210):
    """Exact match to Magnus's 1:50 sketch for 1. etg:
    - If north_vaskerom=False (Alt 1): 1-story north extension (2,10 m) holds Vindfang + Kjellernedgang + Utebod NE
    - If north_vaskerom=True  (Alt 2): 1-story north extension (2,50 m!) holds roomy 6,0 m² Vindfang + 6,0 m² Vaskerom (NE),
      and external covered basement stair moves outside along the east wall, set back 1,50 m from north facade!
    """
    nd = north_depth
    ni = nd - 30  # interior depth (180 cm for Alt 1, 220 cm for Alt 2!)
    # North extension interior (y=-ni..0, x=280..836) — aligned cleanly with existing 30 cm north wall at y=0..30!
    pb.rect(280, -ni, 274, ni, fill="#f8fafc", opacity=0.95)  # Vindfang
    if north_vaskerom:
        pb.rect(566, -ni, 270, ni, fill="#eff6ff", opacity=0.95)  # Full 6,0 m² Vaskerom!
    else:
        pb.rect(566, -ni, 270, 82, fill="#f1f5f9", opacity=0.95)   # Utebod (~2.3 m²)
        pb.rect(566, -92, 270, 92, fill="#e2e8f0", opacity=0.95)    # Kjellernedgang + øst-repos

    # Main 1. etg NE & East zones — aligned cleanly on ONE continuous vertical wall axis x=464!
    pb.rect(558, 30, 278, 328, fill="#eff6ff", opacity=0.85)    # Bad 8.7 m²
    pb.rect(468, 30, 86, 174, fill="#eff6ff", opacity=0.85)     # WC (compact, clean)
    pb.rect(470, 366, 366, 386, fill="#f0fdf4", opacity=0.72)   # Sov 13.5 m²
    pb.rect(470, 760, 366, 376, fill="#fef3c7", opacity=0.55)   # Kitchen 14.5 m²

    # Walls in north extension + clean 30 cm existing load-bearing north wall at y=0..30!
    pb.wall_v(560, -ni, 0, 12)                   # Vindfang / Vaskerom (or Utebod-Kjeller) wall
    if not north_vaskerom:
        pb.wall_h(560, 836, -94, 12)             # Utebod / Kjellernedgang wall
    pb.wall_h(280, 836, 15, 30, fill="#334155")  # Existing 30 cm north wall (flush across full width!)

    # Bad (8.7 m²), WC & Sov walls — ALL aligned cleanly on x=464 (matches 2. etg directly above!)
    pb.wall_v(556, 30, 360, 12)  # Bad west wall (against WC & bad-nisje)
    pb.wall_v(464, 30, 208, 12)  # WC west wall (aligned on x=464!)
    pb.wall_h(464, 556, 206, 12) # WC south wall
    pb.wall_h(464, 836, 360, 12) # Bad south wall -> closed cleanly all the way to x=464!

    # Sov (13.5 m²) walls
    pb.wall_v(464, 360, 756, 12)  # Sov west wall (continuous x=464 axis!)
    pb.wall_h(464, 836, 756, 12)  # Sov / Kitchen wall

    # Doors — ZERO collisions with walls, stairs, or cabinets!
    # 140/210 main entrance from WEST into Vindfang (centered in north extension!)
    ey = -165 if north_vaskerom else -155
    pb.rect(250 - 1, ey, 32, 130, fill="#ffffff")
    pb.door(265, ey + 7, 92, "v_down_right", wall_t=30)
    pb.rect(258, ey + 101, 14, 28, fill="#bae6fd", stroke="#334155", sw=1.4)  # Glass sidefelt
    pb.text(182, ey + 77, "140/210", size=14, weight="700", fill="#475569")
    # Inner door Vindfang -> Gang (through 30 cm existing north wall, swings cleanly into Gang!)
    pb.door(325, 15, 90, "h_right_down", wall_t=30)
    if north_vaskerom:
        # Door Vindfang -> Vaskerom (6,0 m²), cleanly at south end of partition (y=-92..-12), swings EAST into Vaskerom!
        pb.door(560, -92, 80, "v_down_right", wall_t=12)
    else:
        # 100/210 SINGLE external door on EAST wall of north extension into flat landing (y=-90..-4 -> clear of y=0..30 wall!)
        pb.door(851, -88, 84, "v_down_right", wall_t=30)
        pb.text(918, -42, "100/210", size=14, weight="700", fill="#475569")
        # Internal door from flat east landing (x=746..836) NORTH into Utebod (zero stair collision!)
        pb.door(752, -94, 74, "h_right_up", wall_t=12)
    # WC door (from gang alcove, swings cleanly south)
    pb.door(474, 206, 72, "h_right_down", wall_t=12)
    # Bad 85/210 door (swings into Bad between WC y=200 and sink cabinet y=304 -> ZERO cabinet collision!)
    pb.door(556, 214, 82, "v_down_right", wall_t=12)
    # Sov 85/210 door on NORTH wall (y=360) -> entered directly from GANG (not from Stue!), matching 1:50 sketch!
    pb.door(470, 360, 82, "h_right_down", wall_t=12)
    # South terrace double door — EXISTING centered opening (x=353..513, center=433)!
    pb.double_terrace_door_h(433, 1151, 160, wall_t=30, swing_down=True)

    # Windows on north & east walls (100% synced with Fasade Nord & Fasade Øst!)
    pb.window_h(128, 190, 15, 30)         # Trapp narrow 62 cm north window (flush w/ west edge & center mullion of 2.etg 128..252, clear of mid-landing 36..126!)
    pb.window_h(340, 470, -nd + 15, 30)   # Vindfang helt dobbeltvindu nord
    if north_vaskerom:
        pb.window_h(708, 780, -nd + 15, 30)  # Vaskerom halvt vindu nord (mot øst, som nordfasade-skissen!)
    else:
        pb.window_h(620, 692, -nd + 15, 30)  # Utebod narrow north window (matches Fasade Nord Alt 1!)
    pb.window_v(851, 158, 282, 30)    # Axis 4: Bad 1. etg
    pb.window_v(851, 433, 557, 30)    # Axis 3: Sov/Pult 1. etg (sydkant y=557 flukter med smalt Bad 2.etg-vindu!)
    pb.window_v(851, 635, 745, 30)    # Axis 2: Sov sør 1. etg
    pb.window_v(851, 928, 1052, 30)   # Axis 1: Kitchen east
    pb.window_h(631, 761, 1151, 30)   # Kitchen south window

    # Fixtures — North extension
    if north_vaskerom:
        # Roomy 6,0 m² Vindfang (2,74 x 2,20 m): full 60x120 cm coat wardrobe NE + 190 cm shoe bench under north window!
        # ZERO door collisions anywhere!
        pb.wardrobe(492, -ni + 6, 60, 118, "Garderobe")
        pb.rect(288, -ni + 6, 196, 38, fill="#f1f5f9", stroke="#64748b", sw=1.5, rx=2)
        pb.text(386, -ni + 30, "Sittebenk / sko", size=12, weight="600", fill="#475569")
        pb.room_label(408, -74, "Vindfang", "6,0 m²")
        # Roomy 6,0 m² Vaskerom (2,70 x 2,20 m): full 60 cm deep laundry counter north (V+T+vask+benk) + 175 cm tall cabinets south!
        pb.washer_dryer(574, -ni + 6, count=2, vertical=False)
        pb.sink(706, -ni + 6, 72, 56)
        pb.rect(782, -ni + 6, 48, 56, fill="#f1f5f9", stroke="#64748b", sw=1.5)  # Benkeskap
        pb.wardrobe(654, -56, 176, 52, "Høyskap / Tørk")
        pb.room_label(724, -108, "Vaskerom", "6,0 m²")
        # NEW external basement stair along EAST wall landing at SOUTH END OF U.04 (y=+320..+425 -> straight into basement hallway!):
        # Starts at y=+60 (off the north extension!), top 3 steps open (+60..+135), then LOW HORIZONTAL roof (12° east, Z=186->163)
        # runs y=+135..+425 (cleanly BELOW upper-third Bad 1.etg window y=158..282 AND stops 8 cm NORTH of Sov/Pult window y=433..557!).
        st_y1 = 60          # +60 cm (clear of north ext, 3,10 m back from north facade y=-250)
        st_y2 = st_y1 + 365 # +425 cm (helt mot syd i U.04, 8 cm klar nord for Sov/Pult-vindu!)
        roof_y1 = st_y1 + 75 # +135 cm (3 open steps -> -54 cm -> 2,17-2,40 m headroom under roof!)
        pb.rect(866, roof_y1, 116, st_y2 - roof_y1, fill="#f1f5f9", stroke="#475569", sw=2.0, dash="8,5", opacity=0.85)
        pb.basement_stairs_v(872, st_y1 + 6, 98, 254, steps=11)
        # Bottom landing (bunn-repos, -1,95 m under terreng, helt mot syd i U.04 -> rett inn i kjellergang!)
        pb.rect(872, st_y1 + 260, 98, 102, fill="#f8fafc", stroke="#64748b", sw=1.6)
        pb.text(921, st_y1 + 300, "Bunn-repos", size=10, weight="700", fill="#475569")
        pb.text(921, st_y1 + 314, "syd i U.04", size=10, weight="700", fill="#059669")
        pb.text(921, st_y1 + 330, "(-1,95 m)", size=10, weight="600", fill="#0284c7")
        pb.rect(970, roof_y1, 12, 12, fill="#334155")
        pb.rect(970, (roof_y1 + st_y2) / 2 - 6, 12, 12, fill="#334155")
        pb.rect(970, st_y2 - 12, 12, 12, fill="#334155")
        pb.text(924, st_y1 - 14, "Kjellertrapp", size=12, weight="700", fill="#059669")
        pb.text(924, st_y2 + 18, "Lavt tak (12° øst)", size=11, weight="700", fill="#059669")
        pb.dim_v(1005, st_y1, st_y2, "3,65 m (til syd i U.04)", color="#0284c7", bold=False, text_offset=20)
    else:
        pb.wardrobe(498, -172, 54, 164, "Gard.")
        pb.rect(746, -88, 88, 86, fill="#f8fafc", stroke="#94a3b8", sw=1.4)  # Flat landing (Repos)
        pb.text(790, -40, "Repos", size=12, weight="700", fill="#475569")
        pb.basement_stairs_h(568, -86, 176, 82)
        pb.text(650, -132, "Utebod (~2,3 m²)", size=16, weight="700", fill="#334155")
        pb.text(656, -40, "Kjellertrapp", size=13, weight="700", fill="#1e293b")
        pb.room_label(422, -92, "Vindfang", "5,0 m²")

    # Fixtures — Bad 1. etg (8.7 m², exact match to Magnus's sketch!)
    pb.shower(568, 38, 92, 92)  # Dusj i NV
    pb.tub(750, 42, 78, 175)  # Badekar langs østvegg
    pb.wc(568, 152, rot=270)  # WC mot vestvegg (clear of Bad door at y=214!)
    pb.sink(642, 304, 120, 48)  # Bred servant langs sørvegg
    pb.rect(570, 304, 68, 48, fill="#f1f5f9", stroke="#64748b", sw=1.6)  # Skap venstre for servant
    pb.rect(766, 304, 62, 48, fill="#f1f5f9", stroke="#64748b", sw=1.6)  # Skap høyre for servant
    pb.room_label(695, 250, "Bad", "8,7 m²")

    # Fixtures — Separate WC (west of bad)
    pb.wc(474, 42, rot=270)
    pb.sink(474, 122, 46, 62)
    pb.text(516, 108, "WC", size=16, weight="700", fill="#1e293b")

    # Fixtures — Sov 1. etg (~13.5 m², exact match to Magnus's sketch!)
    pb.desk(645, 372, 145, 58)  # Pult mot badvegg!
    pb.double_bed(610, 540, 180, 200, head="bottom")
    pb.rect(572, 695, 34, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.4)  # Nattbord vest
    pb.rect(794, 695, 34, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.4)  # Nattbord øst
    pb.wardrobe(474, 490, 60, 256, "Skyvedørskap")
    pb.rect(414, 368, 44, 92, fill="#f8fafc", stroke="#64748b", sw=1.5)  # Kommode mot tett Sov-vestvegg (som på 1:50-skisse!)
    pb.text(436, 417, "Kom.", size=11, fill="#64748b", rotate=-90)
    pb.room_label(610, 488, "Sov / Kontor", "13,5 m²")

    # Kitchen
    pb.kitchen_block(836, 764, 1132, 470)
    pb.room_label(650, 875, "Kjøkken", "14,5 m²")


def draw_shared_east_floor2(pb: PlanBuilder):
    """Exact match to Magnus's 1:50 sketch for 2. etg east side:
    - Hovedsoverom (13.3 m²) NE w/ north headboard
    - Bad (~6.8 m², 2.0m length) w/ WC, servant & dusj on north wall, skap/vask on south wall
    - Sov 2 (9.0 m², ~2.7m length) w/ bed + pult
    - Sov 3 (9.2 m², ~2.8m length) w/ bed + pult + dashed kitchen option over 1. etg kitchen
    """
    pb.rect(470, 30, 366, 360, fill="#f0fdf4", opacity=0.75)  # Master 13.3 m²
    pb.rect(470, 396, 366, 198, fill="#eff6ff", opacity=0.85)  # Bad 6.8 m²
    pb.rect(470, 604, 366, 258, fill="#f0fdf4", opacity=0.75)  # Sov 2 (9.0 m²)
    pb.rect(526, 842, 310, 294, fill="#f0fdf4", opacity=0.75)  # Sov 3 (9.2 m² = 3.10m x 2.94m, clears centered veranda door!)

    # East rooms walls
    pb.wall_v(464, 30, 842, 12)
    pb.wall_v(524, 842, 1136, 12)  # Sov 3 west wall at x=524 (3.10 m wide as sketched -> frees centered x=353..513 door!)
    pb.wall_h(464, 836, 392, 12)  # Master / Bad (3.62 m -> 13.3 m²)
    pb.wall_h(464, 836, 598, 12)  # Bad / Sov 2 (2.00 m -> ~7.1 m²)
    pb.wall_h(464, 836, 842, 12)  # Sov 2 / Sov 3 (~2.94 m -> 9.2 m²)

    # Doors — ZERO collisions with toilets or cabinets!
    pb.door(464, 285, 85, "v_down_right", wall_t=12)  # Master
    pb.door(464, 492, 80, "v_down_right", wall_t=12)  # Bad (clear of WC y=466 & Skap x=585!)
    pb.door(464, 635, 85, "v_down_right", wall_t=12)  # Sov 2
    pb.door(524, 875, 85, "v_down_right", wall_t=12)  # Sov 3

    # East & north windows (4 clean vertical axes matching 1. etg & Fasade Øst/Nord!)
    pb.window_v(851, 158, 282, 30)   # Axis 4: Master east
    pb.window_v(851, 495, 557, 30)   # Axis 3: Bad 2.etg east — smalt 62 cm vindu, sydkant y=557 flukter med 1.etg & klar sør for dusjnisje!
    pb.window_v(851, 648, 772, 30)   # Axis 2: Sov 2 east
    pb.window_v(851, 928, 1052, 30)  # Axis 1: Sov 3 east
    pb.window_h(128, 252, 15, 30)    # Trapp north full 124 cm window (flush w/ west edge of 1.etg 128..190, clear of mid-landing 36..126 & 80 cm above north-ext roof!) — NO north window in Master!

    # Fixtures — Master (north headboard, matching Magnus's 2. etg sketch!)
    pb.double_bed(605, 42, 180, 200, head="top")
    pb.wardrobe(474, 36, 58, 225, "Skap")
    pb.room_label(680, 315, "Hovedsoverom", "13,3 m²")

    # Fixtures — Bad 2. etg (WC, servant, 90×90 dusjnisje along north wall; skap/vask shifted west to keep narrow east window bay 100% clear!)
    pb.wc(485, 404, rot=0)
    pb.sink(578, 404, 115, 46)
    pb.shower(742, 400, 90, 90)
    pb.wardrobe(565, 542, 130, 46, "Skap")
    pb.washer_dryer(700, 528, count=1, vertical=False)
    pb.room_label(620, 495, "Bad", "7,0 m²", "(rør nær bad 1. etg)")

    # Sov 2
    pb.single_bed(626, 616, 200, 105, head="right")
    pb.desk(680, 790, 140, 58)
    pb.wardrobe(474, 740, 55, 114)
    pb.room_label(595, 745, "Soverom 2", "9,2 m²")

    # Sov 3 (with dashed future kitchen option over 1. etg kitchen!)
    pb.single_bed(626, 886, 200, 105, head="right")
    pb.desk(680, 1060, 140, 58)
    pb.rect(774, 878, 56, 250, fill="none", stroke="#d97706", sw=2, dash="7,5")
    pb.room_label(610, 1015, "Soverom 3", "9,2 m²", "(el. kjøkken utleie)")


def build_alt1_floor1(pb: PlanBuilder):
    """Alternativ 1 - 1. etg: Nord-tilbygg + 3.20m x 5.20m vest-tilbygg (y=410..930) + Vask (3.9 m²) sør for trapp."""
    west_d, wy1, wy2 = 320, 410, 930
    draw_outer_shell(pb, west_d, wy1, wy2, north_ext=True)

    # Social & hall tints — strictly EXCLUDE 110 cm Gangpassasje (x=348..458) from Stue area!
    pb.rect(-290, 440, 290 + 348, 352, fill="#fffbeb", opacity=0.85)   # Stue (vest for 110 cm gangpassasje, 25,4 m² netto)
    pb.rect(-290, 792, 320, 108, fill="#fffbeb", opacity=0.85)         # Vestfløy sør-del (y=792..900)
    pb.rect(348, 440, 110, 352, fill="#f1f5f9", opacity=0.9)           # Gangpassasje 110 cm (ekskludert fra stue!)
    pb.line(348, 440, 348, 792, stroke="#94a3b8", sw=2.0, dash="6,6")
    pb.text(403, 625, "Gangpassasje 110 cm", size=13, weight="700", fill="#64748b", rotate=-90)
    pb.rect(30, 792, 428, 344, fill="#fefce8", opacity=0.75)           # Spisestue
    pb.rect(-286, 444, 418, 452, fill="none", stroke="#0284c7", sw=3, dash="12,8")
    pb.rect(132, 444, 212, 272, fill="none", stroke="#0284c7", sw=2.2, dash="8,6")
    pb.rect(30, 256, 220, 178, fill="#eff6ff", opacity=0.85)  # Vask
    pb.rect(256, 30, 202, 410, fill="#f8fafc", opacity=0.85)  # Gang

    # Shared east side + north extension (100% match to Magnus's sketch!)
    draw_shared_east_floor1(pb)

    # NW stairwell + Vask: open entry NE (up to 2. etg) + basement door lengst syd (SE, under rising south flight!)
    pb.wall_v(256, 30, 440, 12)
    pb.wall_h(30, 256, 256, 12)
    pb.wall_h(30, 256, 434, 14)  # TV wall north of living!
    pb.rect(249, 40, 14, 92, fill="#ffffff")          # Åpen oppgang nordøst (opp til 2. etg)
    pb.door(256, 162, 82, "v_down_right", wall_t=12)  # Dør ned til kjeller (lengst syd i trappen, slår ut i Gang!)
    pb.door(256, 332, 80, "v_down_left", wall_t=12)   # Vask (20 cm clear of sink y=270..315!)

    # Bearing beam dashed lines
    pb.line(170, 434, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 468, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    # West, north & south windows + veranda door on NORTH wall of west wing (matching Fasade Vest/Nord/Sør!)
    pb.window_v(-305, 475, 640, 30)  # Vestfløy vindu nord (kors-sprosse)
    pb.window_v(-305, 700, 865, 30)  # Vestfløy vindu sør (kors-sprosse)
    pb.window_h(-225, -95, 915, 30)  # Vestfløy dobbeltvindu sør (1. etg — frigjør hele SV-hjørnet til sofa!)
    pb.double_terrace_door_h(-160, 425, 150, wall_t=30, swing_down=False)  # Verandadør NORD på vest-tverrfløy (utadslående!)
    pb.window_h(105, 235, 1151, 30)  # Spisestue sør (symmetrisk vest for sentrert verandadør)
    pb.window_v(15, 90, 195, 30)     # Trapp vest
    pb.window_v(15, 285, 357, 30)    # Vask vest
    pb.window_v(15, 992, 1107, 30)   # Spisestue vest

    # Fixtures & furniture — cozy SW corner sofa aligned directly with H2O fireplace + wide open corridor to north veranda door!
    pb.stairs_u(36, 36, 212, 212)
    pb.washer_dryer(42, 270, count=2, vertical=False)
    pb.sink(174, 270, 72, 45)
    pb.dining_table(205, 985, 200, 95, seats=8)
    pb.tv_bench(-55, 444, 190, 42)   # På 100% tett vegg (30 cm klar av nord-verandadør x=-235..-85!)
    pb.sofa_l(-270, 635, w_horiz=240, h_vert=240, depth=92, corner="bl")  # Lun SV-hjørnesofa rett mot H2O-peis (109 cm klar!)
    pb.coffee_table(-142, 668, 120, 70)
    pb.armchair(18, 555, 76, 76)
    pb.chimney_and_fireplace(135, 720, 95, 55, mode="west_insert")

    # Labels
    pb.room_label(106, 142, "Trapp", "4,8 m²")
    pb.room_label(110, 382, "Vask", "3,9 m²")
    pb.text(362, 295, "Gang", size=20, weight="700", fill="#475569")
    pb.text(-140, 535, "STUE ~25,4 m²", size=22, weight="800", fill="#0369a1")
    pb.text(-140, 561, "(netto ekskl. 110 cm gang)", size=14, weight="700", fill="#0284c7")
    pb.text(205, 882, "SPISESTUE ~11 m²", size=19, weight="700", fill="#854d0e")

    # Dimensions
    pb.dim_h(0, 866, -265, "8,66 m (eksisterende bredde)", bold=True)
    pb.dim_h(-320, 0, -265, "3,20 m ny vest", color="#0284c7", bold=True)
    pb.dim_v(960, -210, 0, "2,10 m nord", color="#ea580c", bold=True, text_offset=26)
    pb.dim_v(960, 0, 1166, "11,66 m (eksisterende lengde — INGEN syd-tilbygg)", bold=True, text_offset=26)
    pb.dim_v(-385, 0, 410, "4,10 m", color="#475569")
    pb.dim_v(-385, 410, 930, "5,20 m (nytt vest-tilbygg)", color="#0284c7", bold=True)
    pb.dim_v(-385, 930, 1166, "2,36 m", color="#475569")


def build_alt1_floor2(pb: PlanBuilder):
    """Alternativ 1 - 2. etg."""
    west_d, wy1, wy2 = 320, 410, 930
    draw_outer_shell(pb, west_d, wy1, wy2, north_ext=False)

    pb.rect(-290, 440, 290 + 348, 352, fill="#fffbeb", opacity=0.85)
    pb.rect(-290, 792, 320, 108, fill="#fffbeb", opacity=0.85)
    pb.rect(348, 440, 110, 402, fill="#f1f5f9", opacity=0.9)           # Gangpassasje 110 cm (ekskludert fra stue!)
    pb.line(348, 440, 348, 842, stroke="#94a3b8", sw=2.0, dash="6,6")
    pb.text(403, 640, "Gangpassasje 110 cm", size=13, weight="700", fill="#64748b", rotate=-90)
    pb.rect(30, 792, 428, 344, fill="#fefce8", opacity=0.75)
    pb.rect(-286, 444, 418, 452, fill="none", stroke="#0284c7", sw=3, dash="12,8")
    pb.rect(132, 444, 212, 272, fill="none", stroke="#0284c7", sw=2.2, dash="8,6")
    pb.rect(30, 256, 220, 178, fill="#eff6ff", opacity=0.8)
    pb.rect(256, 30, 202, 226, fill="#f8fafc", opacity=0.9)
    pb.rect(256, 256, 202, 184, fill="#f8fafc", opacity=0.7)

    draw_shared_east_floor2(pb)

    pb.wall_v(256, 30, 440, 12)
    pb.wall_h(30, 256, 256, 12)
    pb.wall_h(30, 256, 434, 14)
    pb.wall_h(256, 464, 256, 12)
    pb.line(170, 434, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 464, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    pb.door(256, 158, 82, "v_down_right", wall_t=12)  # Trapp arrival SE (swings cleanly into Hall!)
    pb.door(310, 256, 90, "h_right_down", wall_t=12)  # 2-mannsbolig / leilighetsdør
    pb.door(256, 332, 80, "v_down_left", wall_t=12)   # Bod / Vask (clear of Skap ending at x=165!)

    # South windows + EXISTING centered veranda door (x=353..513) in 2. etg (matching all 4 facades!)
    pb.window_v(-305, 475, 640, 30)   # Vestfløy vindu nord
    pb.window_v(-305, 700, 865, 30)   # Vestfløy vindu sør
    pb.window_h(-225, -95, 915, 30)   # Vestfløy sørvindu 2. etg
    pb.window_h(-234, -99, 425, 30)   # Dobbeltvindu nord på vest-tilbygg (2. etg)
    pb.window_h(105, 235, 1151, 30)   # Flanking south window west (Opphold 2. etg)
    pb.double_terrace_door_h(433, 1151, 160, wall_t=30, swing_down=False)  # Eksist. sentrert verandadør 2. etg sør!
    pb.window_h(631, 761, 1151, 30)   # Flanking south window east (Sov 3)
    pb.window_v(15, 90, 195, 30)      # Trapp vest
    pb.window_v(15, 285, 357, 30)     # Bod/Vask vest
    pb.window_v(15, 992, 1107, 30)    # Spis/opphold vest

    pb.stairs_u(36, 36, 212, 212, floor=2)
    pb.washer_dryer(42, 270, count=2, vertical=False)
    pb.wardrobe(42, 376, 122, 46, "Skap")
    pb.tv_bench(-55, 444, 190, 42)    # På 100% tett nordvegg (klar av nordvindu!)
    pb.sofa_l(-270, 635, w_horiz=240, h_vert=240, depth=92, corner="bl")
    pb.coffee_table(-142, 668, 120, 70)
    pb.armchair(18, 555, 76, 76)
    pb.dining_table(200, 985, 180, 90, seats=6)  # Helt klar av innadslående sør-verandadør!
    pb.chimney_and_fireplace(135, 720, 95, 55, mode="west_stove")

    pb.room_label(103, 142, "Trapp", "4,8 m²")
    pb.room_label(112, 352, "Bod / Vask", "3,6 m²")
    pb.room_label(362, 102, "Hall", "4,5 m²", "(2-mannsbolig)")
    pb.text(-140, 535, "LOFTSTUE ~25,4 m²", size=20, weight="800", fill="#0369a1")
    pb.text(-140, 561, "(netto ekskl. 110 cm gang)", size=14, weight="700", fill="#0284c7")

    pb.dim_h(0, 866, -265, "8,66 m", bold=True)
    pb.dim_h(-320, 0, -265, "3,20 m (innbygd 2. etg)", color="#0284c7", bold=True)
    pb.dim_v(925, 30, 392, "3,6 m", text_offset=24)
    pb.dim_v(925, 392, 598, "2,0 m", text_offset=24)
    pb.dim_v(925, 598, 842, "2,4 m", text_offset=24)
    pb.dim_v(925, 842, 1136, "2,9 m", text_offset=24)


def build_alt2_floor1(pb: PlanBuilder, west_d: int = 230):
    """Alternativ 2 (2,30 m) / Alternativ 2.5 (3,00 m) - 1. etg: 2,50 m nord-tilbygg (6,0 m² Vindfang + 6,0 m² Vaskerom!)
    + west_d × 5,02 m vest-tilbygg (y=320..822)!"""
    wy1, wy2 = 320, 822
    is_25 = west_d >= 290
    dx_w = west_d - 230  # 0 for Alt 2, 70 for Alt 2.5
    draw_outer_shell(pb, west_d, wy1, wy2, north_ext=True, north_depth=250)

    # Social & hall tints — strictly EXCLUDE 110 cm Gangpassasje (x=348..458) from Stue area!
    pb.rect(-west_d + 30, 350, (west_d - 30) + 348, 442, fill="#fffbeb", opacity=0.85)  # Netto Stue vest for 110 cm gangpassasje!
    pb.rect(348, 350, 110, 442, fill="#f1f5f9", opacity=0.92)                           # Gangpassasje 110 cm (ekskludert!)
    pb.line(348, 350, 348, 792, stroke="#94a3b8", sw=2.0, dash="6,6")
    pb.text(403, 600, "Gangpassasje 110 cm", size=13, weight="700", fill="#64748b", rotate=-90)
    pb.rect(30, 792, 428, 344, fill="#fefce8", opacity=0.75)
    # Dashed net living zone stops cleanly at x=344 (STRICTLY excluding 110 cm Gangpassasje x=348..458!)
    pb.rect(-west_d + 34, 354, (west_d - 34) + 344, 362, fill="none", stroke="#059669", sw=3.2, dash="12,8")
    pb.rect(-west_d + 34, 716, (west_d - 34) + 122, 72, fill="none", stroke="#059669", sw=2.5, dash="8,6")
    pb.rect(30, 244, 220, 100, fill="#eff6ff", opacity=0.85)  # Garderobe / Bod (2,2 m²)
    pb.rect(256, 30, 202, 320, fill="#f8fafc", opacity=0.85)  # Gang

    # Shared east side + 2,50 m north extension WITH roomy 6,0 m² Vindfang, 6,0 m² Vaskerom & east-wall basement stair!
    draw_shared_east_floor1(pb, north_vaskerom=True, north_depth=250)

    # NW stairwell (y=30..242) + Garderobe / Bod (y=244..346): open entry NE (up) + basement door lengst syd (SE)!
    pb.wall_v(256, 30, 350, 12)
    pb.wall_h(30, 256, 242, 12)
    pb.wall_h(30, 256, 348, 14)  # TV wall north of living (flush with wy1=320 inner wall y=350!)
    pb.rect(249, 40, 14, 88, fill="#ffffff")          # Åpen oppgang nordøst (opp til 2. etg)
    pb.door(256, 152, 80, "v_down_right", wall_t=12)  # Dør ned til kjeller (lengst syd i trappen!)
    pb.door(256, 258, 76, "v_down_right", wall_t=12)  # Garderobe / Bod (slår ut i Gang!)

    # Structural beam dashed lines
    pb.line(170, 350, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 464, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    # West, north & south windows (100% synced with Fasade Vest Alt 2 / Alt 2.5!)
    pb.window_v(-west_d + 15, 382, 537, 30)  # Vestfløy nordre kors-sprosse
    pb.window_v(-west_d + 15, 605, 760, 30)  # Vestfløy søndre kors-sprosse
    wx_c = -west_d / 2.0
    wx_hw = 65 if is_25 else 60
    pb.window_h(wx_c - wx_hw, wx_c + wx_hw, 807, 30)  # Vestfløy sørvindu
    pb.window_h(wx_c - wx_hw, wx_c + wx_hw, 335, 30)  # Vestfløy nordvindu
    pb.window_h(105, 235, 1151, 30)  # Spisestue sør
    pb.window_v(15, 929, 1059, 30)   # Spisestue vest
    pb.window_v(15, 95, 225, 30)     # Trapp vest

    # Fixtures & furniture — H2O fireplace on NORTH/WEST of chimney facing directly into sofa lounge!
    pb.stairs_u(36, 36, 212, 200)
    pb.wardrobe(38, 294, 155, 46, "Gard. / Skap")
    pb.dining_table(205, 985, 200, 95, seats=8)
    pb.tv_bench(38, 356, 200, 42)
    if is_25:
        pb.sofa_l(-255, 520, w_horiz=255, h_vert=250, depth=95, corner="bl")  # Romslig 2,55×2,50 m L-sofa!
        pb.coffee_table(-125, 540, 130, 75)
        pb.armchair(255, 495, 76, 76)
    else:
        pb.sofa_l(-185, 540, w_horiz=225, h_vert=230, depth=92, corner="bl")  # 103 cm klar til vestglass på H2O-peis!
        pb.coffee_table(-65, 545, 120, 70)
        pb.armchair(255, 495, 76, 76)
    pb.chimney_and_fireplace(135, 720, 95, 55, mode="north_insert")

    # Labels
    pb.room_label(103, 136, "Trapp", "4,6 m²")
    pb.text(122, 278, "Gard. / Bod 2,2 m²", size=14, weight="700", fill="#1e293b")
    pb.text(365, 285, "Gang", size=20, weight="700", fill="#475569")
    if is_25:
        pb.text(40, 434, "STUE ~26,8 m² (4,42 × 6,18 m)", size=21, weight="800", fill="#047857")
        pb.text(40, 460, "Netto ekskl. 110 cm gangpassasje • 3,00 m vest-fløy", size=14, weight="700", fill="#059669")
    else:
        pb.text(65, 434, "STUE ~23,7 m² (4,42 × 5,48 m)", size=21, weight="800", fill="#047857")
        pb.text(65, 460, "Netto ekskl. 110 cm gangpassasje • Eksist. sørvegg vest", size=14, weight="700", fill="#059669")
    pb.text(205, 882, "SPISESTUE ~12,5 m²", size=19, weight="700", fill="#854d0e")

    # Dimensions
    pb.dim_h(0, 866, -280, "8,66 m (eksisterende bredde)", bold=True)
    pb.dim_h(-west_d, 0, -280, "3,00 m (+0,7 m mur)" if is_25 else "2,30 m (eksist. mur!)", color="#059669", bold=True)
    pb.dim_v(1085, -250, 0, "2,50 m nord", color="#ea580c", bold=True, text_offset=26)
    pb.dim_v(1085, 0, 1166, "11,66 m (eksisterende lengde — INGEN syd-tilbygg)", bold=True, text_offset=26)
    pb.dim_v(-west_d - 65, 0, 320, "3,20 m (nord)", color="#059669", bold=True)
    pb.dim_v(-west_d - 65, 320, 822, "5,02 m (vest-tilbygg)", color="#059669", bold=True)
    pb.dim_v(-west_d - 65, 822, 1166, "3,44 m (eksist. sørvegg)", color="#059669", bold=True)


def build_alt2_floor2(pb: PlanBuilder, west_d: int = 230):
    """Alternativ 2 (2,30 m) / Alternativ 2.5 (3,00 m) - 2. etg."""
    wy1, wy2 = 320, 822
    is_25 = west_d >= 290
    dx_w = west_d - 230
    draw_outer_shell(pb, west_d, wy1, wy2, north_ext=False, north_depth=250)

    pb.rect(-west_d + 30, 350, (west_d - 30) + 348, 442, fill="#fffbeb", opacity=0.85)
    pb.rect(348, 350, 110, 492, fill="#f1f5f9", opacity=0.92)
    pb.line(348, 350, 348, 842, stroke="#94a3b8", sw=2.0, dash="6,6")
    pb.text(403, 600, "Gangpassasje 110 cm", size=13, weight="700", fill="#64748b", rotate=-90)
    pb.rect(30, 792, 428, 344, fill="#fefce8", opacity=0.75)
    pb.rect(-west_d + 34, 354, (west_d - 34) + 344, 362, fill="none", stroke="#059669", sw=3.2, dash="12,8")
    pb.rect(-west_d + 34, 716, (west_d - 34) + 122, 72, fill="none", stroke="#059669", sw=2.5, dash="8,6")
    pb.rect(30, 244, 220, 100, fill="#eff6ff", opacity=0.85)
    pb.rect(256, 30, 202, 212, fill="#f8fafc", opacity=0.9)
    pb.rect(256, 242, 202, 108, fill="#f8fafc", opacity=0.7)

    draw_shared_east_floor2(pb)

    pb.wall_v(256, 30, 350, 12)
    pb.wall_h(30, 256, 242, 12)
    pb.wall_h(30, 256, 348, 14)
    pb.wall_h(256, 464, 242, 12)
    pb.line(170, 350, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 464, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    pb.door(256, 152, 80, "v_down_right", wall_t=12)  # Stairwell arrival SE (swings cleanly into Hall!)
    pb.door(310, 242, 90, "h_right_down", wall_t=12)  # 2-mannsbolig / leilighetsdør
    pb.door(256, 258, 76, "v_down_right", wall_t=12)  # Bod / Vask (swings into corridor!)

    pb.window_v(-west_d + 15, 382, 537, 30)
    pb.window_v(-west_d + 15, 605, 760, 30)
    wx_c = -west_d / 2.0
    wx_hw = 65 if is_25 else 60
    pb.window_h(wx_c - wx_hw, wx_c + wx_hw, 807, 30)
    pb.window_h(wx_c - wx_hw, wx_c + wx_hw, 335, 30)
    pb.window_h(105, 235, 1151, 30)
    pb.double_terrace_door_h(433, 1151, 160, wall_t=30, swing_down=False)  # Eksist. sentrert verandadør 2. etg sør!
    pb.window_h(631, 761, 1151, 30)
    pb.window_v(15, 929, 1059, 30)
    pb.window_v(15, 95, 225, 30)

    pb.stairs_u(36, 36, 212, 200, floor=2)
    pb.washer_dryer(40, 262, count=1, vertical=False)
    pb.wardrobe(106, 266, 62, 56)
    pb.tv_bench(38, 356, 200, 42)
    if is_25:
        pb.sofa_l(-255, 520, w_horiz=255, h_vert=250, depth=95, corner="bl")
        pb.coffee_table(-125, 540, 130, 75)
        pb.armchair(255, 495, 76, 76)
    else:
        pb.sofa_l(-185, 540, w_horiz=225, h_vert=230, depth=92, corner="bl")
        pb.coffee_table(-65, 545, 120, 70)
        pb.armchair(255, 495, 76, 76)
    pb.dining_table(200, 985, 180, 90, seats=6)
    pb.chimney_and_fireplace(135, 720, 95, 55, mode="north_stove")

    pb.room_label(103, 136, "Trapp", "4,6 m²")
    pb.text(210, 294, "Bod/Vask", size=14, weight="700", fill="#1e293b")
    pb.text(210, 314, "2,2 m²", size=13, weight="600", fill="#475569")
    pb.room_label(362, 98, "Hall", "4,3 m²", "(2-mannsbolig)")
    if is_25:
        pb.text(40, 434, "LOFTSTUE ~26,8 m² (4,42 × 6,18 m)", size=19, weight="800", fill="#047857")
        pb.text(40, 460, "(netto ekskl. 110 cm gang + 12,5 m² spis)", size=14, weight="700", fill="#059669")
    else:
        pb.text(65, 434, "LOFTSTUE ~23,7 m² (4,42 × 5,48 m)", size=19, weight="800", fill="#047857")
        pb.text(65, 460, "(netto ekskl. 110 cm gang + 12,5 m² spis)", size=14, weight="700", fill="#059669")

    pb.dim_h(0, 866, -280, "8,66 m", bold=True)
    pb.dim_h(-west_d, 0, -280, "3,00 m (innbygd 2. etg)" if is_25 else "2,30 m (innbygd 2. etg)", color="#059669", bold=True)
    pb.dim_v(925, 30, 392, "3,6 m", text_offset=24)
    pb.dim_v(925, 392, 598, "2,0 m", text_offset=24)
    pb.dim_v(925, 598, 842, "2,4 m", text_offset=24)
    pb.dim_v(925, 842, 1136, "2,9 m", text_offset=24)


def make_sheet(filename: str, title: str, subtitle: str, accent: str, fn1, fn2, highlights: list[str]):
    W, H = 3160, 1940
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        "<defs>",
        '  <pattern id="grid100" width="100" height="100" patternUnits="userSpaceOnUse">',
        '    <path d="M 100 0 L 0 0 0 100" fill="none" stroke="#e7e5e0" stroke-width="1.2"/>',
        "  </pattern>",
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="#faf9f6"/>',
        f'<rect width="{W}" height="{H}" fill="url(#grid100)"/>',
        f'<rect x="0" y="0" width="{W}" height="150" fill="#0f172a"/>',
        f'<rect x="0" y="144" width="{W}" height="6" fill="{accent}"/>',
        f'<text x="70" y="68" font-size="40" font-weight="800" fill="#ffffff">{esc(title)}</text>',
        f'<text x="70" y="114" font-size="24" font-weight="500" fill="#cbd5e1">{esc(subtitle)}</text>',
        f'<g transform="translate({W - 140}, 75)">',
        '  <circle cx="0" cy="0" r="44" fill="none" stroke="#94a3b8" stroke-width="2.5"/>',
        '  <polygon points="0,-34 -14,14 0,4 14,14" fill="#f8fafc"/>',
        '  <text x="0" y="34" font-size="20" font-weight="800" fill="#38bdf8" text-anchor="middle">N</text>',
        "</g>",
        f'<text x="780" y="196" font-size="28" font-weight="800" fill="#0f172a" text-anchor="middle">1. ETASJE (inkl. 1-etg nord-tilbygg)</text>',
        f'<text x="2340" y="196" font-size="28" font-weight="800" fill="#0f172a" text-anchor="middle">2. ETASJE (Soverom + Stue / Utleie-opsjon)</text>',
        f'<line x1="1575" y1="185" x2="1575" y2="1745" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="10,8"/>',
    ]

    pb1 = PlanBuilder(ox=480, oy=540)
    fn1(pb1)
    svg.extend(pb1.els)

    pb2 = PlanBuilder(ox=2020, oy=540)
    fn2(pb2)
    svg.extend(pb2.els)

    fy = 1785
    svg.append(f'<rect x="50" y="{fy}" width="{W - 100}" height="125" fill="#ffffff" stroke="#cbd5e1" stroke-width="2" rx="12"/>')
    svg.append(f'<line x1="90" y1="{fy + 38}" x2="155" y2="{fy + 38}" stroke="#ea580c" stroke-width="4" stroke-dasharray="12,8"/>')
    svg.append(f'<text x="170" y="{fy + 45}" font-size="19" font-weight="600" fill="#334155">Eksisterende yttervegg / vest-utbygg (2,28 × 4,07 m)</text>')
    svg.append(f'<rect x="690" y="{fy + 24}" width="38" height="22" fill="#b45309" stroke="#78350f" stroke-width="2"/>')
    svg.append(f'<text x="742" y="{fy + 45}" font-size="19" font-weight="600" fill="#334155">Original teglpipe (95×55 cm øst–vest, ~1,3 m fra hovedvegg vest)</text>')
    svg.append(f'<rect x="1420" y="{fy + 24}" width="36" height="24" fill="none" stroke="{accent}" stroke-width="3" stroke-dasharray="8,5"/>')
    svg.append(f'<text x="1470" y="{fy + 45}" font-size="19" font-weight="600" fill="#334155">Fri rektangulær stuesone</text>')
    svg.append(f'<line x1="2610" y1="{fy + 42}" x2="2810" y2="{fy + 42}" stroke="#0f172a" stroke-width="4"/>')
    svg.append(f'<line x1="2610" y1="{fy + 30}" x2="2610" y2="{fy + 54}" stroke="#0f172a" stroke-width="3"/>')
    svg.append(f'<line x1="2710" y1="{fy + 34}" x2="2710" y2="{fy + 50}" stroke="#0f172a" stroke-width="2"/>')
    svg.append(f'<line x1="2810" y1="{fy + 30}" x2="2810" y2="{fy + 54}" stroke="#0f172a" stroke-width="3"/>')
    svg.append(f'<text x="2710" y="{fy + 78}" font-size="19" font-weight="700" fill="#0f172a" text-anchor="middle">Målestokk: 2 meter (1 px = 1 cm)</text>')

    hx = 90
    for i, hl in enumerate(highlights):
        svg.append(f'<text x="{hx + i * 830}" y="{fy + 96}" font-size="20" font-weight="700" fill="#0f172a">• {esc(hl)}</text>')

    svg.append("</svg>")
    out_path = os.path.join(OUT_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    make_sheet(
        "plan_alt1_dypere_vest.svg",
        "M6 — ALTERNATIV 1: Dypere vest-tilbygg (3,20 × 5,20 m) + Nord-tilbygg",
        "Tro mot 1:50-skisse (Vindfang/Kjellernedgang/Utebod i nord, 8,7 m² Bad, 13,5 m² Sov, 3,9 m² Vask) • 4,25 × 4,60 m stue VEST for pipe",
        "#0284c7",
        build_alt1_floor1,
        build_alt1_floor2,
        [
            "Netto Stue ~25,4 m² (ekskl. 110 cm gangpassasje; 19,2 m² vest for pipe)",
            "Nord-tilbygg (Vindfang 5,4 m², Kjellernedg., Utebod) + 8,7 m² Bad",
            "Krever ~0,9 m nytt fundament vest + 20° saltak (28 cm klar av 2-løps pipe)",
        ],
    )
    make_sheet(
        "plan_alt2_symmetrisk_vest.svg",
        "M6 — ALTERNATIV 2: 3,00 × 5,02 m vest + 2,50 m nord-tilbygg (6 m² Vindfang + 6 m² Vaskerom)",
        "Catrines 3,20 | 5,02 | 3,44 m oppsett (3,00 m vest) • Netto Stue ~26,8 m² (ekskl. 110 cm gang) • Parallelt 32,7° saltak (33 cm pipeklaring)",
        "#059669",
        lambda pb: build_alt2_floor1(pb, west_d=300),
        lambda pb: build_alt2_floor2(pb, west_d=300),
        [
            "Netto Stue ~26,8 m² (4,42 × 6,18 m ekskl. 110 cm gangpassasje!)",
            "6 m² Vindfang + 6 m² Vaskerom (2,5 m nord) + overbygd øst-kjellertrapp (U.04)",
            "Parallelt 32,7° saltak over hele huset — 33 cm klar av original 2-løps pipe!",
        ],
    )
