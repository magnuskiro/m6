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

    def stairs_u(self, x, y, w, h):
        self.rect(x, y, w, h, fill="#e2e8f0", stroke="#64748b", sw=2)
        mid_x = x + w / 2
        steps = 7
        step_h = (h - 75) / steps
        for i in range(steps):
            sy = y + 75 + i * step_h
            self.line(x, sy, mid_x - 8, sy, stroke="#64748b", sw=1.5)
            self.line(mid_x + 8, sy, x + w, sy, stroke="#64748b", sw=1.5)
        self.rect(mid_x - 8, y + 75, 16, h - 75, fill="#94a3b8")
        ax1, ay1 = self.p(x + w * 0.25, y + h - 20)
        ax2, ay2 = self.p(x + w * 0.25, y + 38)
        ax3, ay3 = self.p(x + w * 0.75, y + 38)
        ax4, ay4 = self.p(x + w * 0.75, y + h - 25)
        self.path(f"M {ax1:.1f} {ay1:.1f} L {ax2:.1f} {ay2:.1f} L {ax3:.1f} {ay3:.1f} L {ax4:.1f} {ay4:.1f}", stroke="#334155", sw=2.5)
        self.path(f"M {ax4 - 10:.1f} {ay4 - 12:.1f} L {ax4:.1f} {ay4:.1f} L {ax4 + 10:.1f} {ay4 - 12:.1f}", stroke="#334155", sw=2.5)

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

    def chimney_and_fireplace(self, x=135, y=720, w=95, h=55, label_side="right"):
        """Exact original chimney core (95 cm east-west x 55 cm north-south) + fireplace insert."""
        self.rect(x, y, w, h, fill="#b45309", stroke="#78350f", sw=3)
        self.rect(x + 12, y + 12, 28, 31, fill="#fef3c7", stroke="#78350f", sw=2)
        self.rect(x + 54, y + 12, 28, 31, fill="#fef3c7", stroke="#78350f", sw=2)
        self.rect(x - 18, y + 8, 18, h - 16, fill="#fb923c", stroke="#9a3412", sw=2)
        self.text(x + w / 2, y + h + 20, "Orig. pipe (95×55 cm Ø–V)", size=14, weight="700", fill="#9a3412", anchor="middle")
        self.text(x + w / 2, y + h + 37, "(peis vest/sør)", size=13, weight="600", fill="#b45309", anchor="middle")

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


def draw_outer_shell(pb: PlanBuilder, west_depth: float, wy1: float, wy2: float, north_ext: bool = False):
    """Draw 30cm insulated outer shell for main rectangle + west extension + optional 1-story north extension."""
    if north_ext:
        # 1. etasje includes 1-story north extension (y = -210..0, x = 250..866)
        outer_pts = [
            (0, 0),
            (250, 0),
            (250, -210),
            (866, -210),
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
            (280, -180),
            (836, -180),
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
        # Covered entry porch (uteplass) in NW recess (x=0..250, y=-210..0)
        pb.rect(0, -210, 250, 210, fill="#f1f5f9", stroke="#94a3b8", sw=2, dash="10,6", opacity=0.7)
        pb.text(125, -110, "Overbygd", size=17, weight="600", fill="#64748b")
        pb.text(125, -86, "inngangsparti", size=17, weight="600", fill="#64748b")
        # Show existing north wall line at y=0 (dashed orange)
        pb.line(250, 0, 866, 0, stroke="#ea580c", sw=3.5, dash="14,10")
    else:
        # Show 1-story north extension roof outline (dashed gray) in 2. etg
        pb.rect(250, -210, 616, 210, fill="#f1f5f9", stroke="#94a3b8", sw=2, dash="10,6", opacity=0.55)
        pb.text(558, -100, "Tak over 1-etg nord-tilbygg (vindfang / kjellernedgang / utebod)", size=16, weight="600", fill="#64748b")

    # Existing west bump-out reference dashed line (2.28m deep, y=415..822)
    ex_pts = [(0, 415), (-228, 415), (-228, 822), (0, 822)]
    d = "M " + " L ".join(f"{pb.ox + x:.1f} {pb.oy + y:.1f}" for x, y in ex_pts)
    pb.path(d, stroke="#ea580c", sw=3.5, dash="14,10")


def draw_shared_east_floor1(pb: PlanBuilder):
    """Exact match to Magnus's 1:50 sketch for 1. etg:
    - 1-story north extension: Vindfang (140/210 from west), Kjellernedgang (110/210 from east), Utebod NE
    - NE Bad (~8.7 m², y=30..355) + separate WC west of bad (y=30..225)
    - Mid-east Sov (~13.5 m², y=365..750) w/ Pult north, south-headboard bed, Skyvedørskap west, Kommode niche
    - SE Kitchen (14.5 m²) w/ tall cabinets, east counter, island & south terrace doors
    """
    # North extension interior (y=-180..30, x=280..836)
    pb.rect(280, -180, 274, 210, fill="#f8fafc", opacity=0.95)  # Vindfang
    pb.rect(566, -180, 270, 92, fill="#f1f5f9", opacity=0.95)  # Utebod
    pb.rect(566, -82, 270, 100, fill="#e2e8f0", opacity=0.95)  # Kjellernedgang

    # Main 1. etg NE & East zones
    pb.rect(558, 30, 278, 328, fill="#eff6ff", opacity=0.85)  # Bad 8.7 m²
    pb.rect(456, 30, 102, 198, fill="#eff6ff", opacity=0.85)  # WC
    pb.rect(472, 366, 364, 386, fill="#f0fdf4", opacity=0.72)  # Sov 13.5 m²
    pb.rect(470, 760, 366, 376, fill="#fef3c7", opacity=0.55)  # Kitchen 14.5 m²

    # Walls in north extension
    pb.wall_v(560, -180, 30, 12)  # Vindfang / Utebod-Kjeller wall
    pb.wall_h(560, 836, -85, 12)  # Utebod / Kjellernedgang wall
    pb.wall_h(456, 836, 24, 18, fill="#334155")  # Existing north wall (load-bearing) between kjellernedgang & bad/wc!
    # Wall between Vindfang & Hall/gang (with door)
    pb.wall_h(280, 456, 24, 12)

    # Bad (8.7 m²) & WC walls
    pb.wall_v(556, 30, 360, 12)  # Bad west wall (against WC & gang)
    pb.wall_v(456, 30, 230, 12)  # WC west wall
    pb.wall_h(456, 556, 228, 12)  # WC south wall
    pb.wall_h(556, 836, 360, 12)  # Bad south wall (against Sov)

    # Sov (13.5 m²) walls
    pb.wall_v(468, 360, 756, 12)  # Sov west wall (skyvedørskap inside)
    pb.wall_h(468, 836, 756, 12)  # Sov / Kitchen wall

    # Doors (matching Magnus's sketch!)
    # 140/210 main entrance from WEST into Vindfang
    pb.rect(250 - 1, -130, 32, 125, fill="#ffffff")
    pb.door(265, -120, 95, "v_down_right", wall_t=30)
    pb.text(200, -45, "140/210", size=14, weight="700", fill="#475569")
    # Inner door Vindfang -> Hall/gang
    pb.door(325, 24, 90, "h_right_down", wall_t=12)
    # 110/210 external door into Kjellernedgang (east)
    pb.door(851, -80, 90, "v_down_right", wall_t=30)
    pb.text(900, -30, "110/210", size=14, weight="700", fill="#475569")
    # Utebod door (east, north of kjellernedgang)
    pb.door(851, -168, 75, "v_down_right", wall_t=30)
    # WC door (from gang, south side as sketched)
    pb.door(468, 228, 75, "h_right_down", wall_t=12)
    # Bad 90/210 door (from gang)
    pb.door(556, 258, 85, "v_down_right", wall_t=12)
    # Sov 90/210 door (from gang, north-west of Sov)
    pb.door(468, 378, 85, "v_down_right", wall_t=12)
    # South terrace double door
    pb.double_terrace_door_h(530, 1151, 160, wall_t=30, swing_down=True)

    # Windows on east wall & north wall (4 vertical axes matching Fasade Øst!)
    pb.window_h(340, 470, -195, 30)  # Vindfang north window
    pb.window_v(851, 158, 282, 30)   # Axis 4: Bad 1. etg (aligned under Hovedsoverom!)
    pb.window_v(851, 433, 557, 30)   # Axis 3: Sov/Pult 1. etg (aligned under Bad 2. etg!)
    pb.window_v(851, 635, 745, 30)   # Axis 2: Sov sør 1. etg (aligned under Sov 2!)
    pb.window_v(851, 928, 1052, 30)  # Axis 1: Kitchen east (aligned under Sov 3!)

    # Fixtures — North extension
    pb.wardrobe(498, -172, 54, 185, "Gard.")
    pb.basement_stairs_h(572, -76, 258, 90)
    pb.text(700, -125, "Utebod (~2,6 m²)", size=17, weight="700", fill="#334155")
    pb.text(700, -25, "Kjellernedgang (utv.)", size=15, weight="700", fill="#1e293b")
    pb.room_label(422, -92, "Vindfang", "5,4 m²")

    # Fixtures — Bad 1. etg (8.7 m², exact match to Magnus's sketch!)
    pb.shower(568, 38, 92, 92)  # Dusj i NV
    pb.tub(750, 42, 78, 175)  # Badekar langs østvegg
    pb.wc(568, 160, rot=270)  # WC mot vestvegg
    pb.sink(642, 304, 120, 48)  # Bred servant langs sørvegg
    pb.rect(570, 304, 68, 48, fill="#f1f5f9", stroke="#64748b", sw=1.6)  # Skap venstre for servant
    pb.rect(766, 304, 62, 48, fill="#f1f5f9", stroke="#64748b", sw=1.6)  # Skap høyre for servant
    pb.room_label(690, 250, "Bad", "8,7 m²")

    # Fixtures — Separate WC (west of bad)
    pb.wc(466, 48, rot=270)
    pb.sink(466, 138, 48, 65)
    pb.text(508, 118, "WC", size=17, weight="700", fill="#1e293b")

    # Fixtures — Sov 1. etg (~13.5 m², exact match to Magnus's sketch!)
    pb.desk(645, 372, 145, 58)  # Pult mot badvegg!
    # Dobbeltseng med hodegavl mot SØR (rygg mot kjøkkenet!)
    pb.double_bed(610, 540, 180, 200, head="bottom")
    pb.rect(572, 695, 34, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.4)  # Nattbord vest
    pb.rect(794, 695, 34, 42, fill="#f8fafc", stroke="#94a3b8", sw=1.4)  # Nattbord øst
    pb.wardrobe(478, 490, 60, 256, "Skyvedørskap")
    pb.rect(410, 405, 50, 88, fill="#f8fafc", stroke="#64748b", sw=1.5)  # Kommode i gangnisje!
    pb.text(435, 452, "Kom.", size=11, fill="#64748b", rotate=-90)
    pb.room_label(610, 478, "Sov / Kontor", "13,5 m²")

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
    pb.rect(470, 872, 366, 264, fill="#f0fdf4", opacity=0.75)  # Sov 3 (9.2 m²)

    # East rooms walls
    pb.wall_v(464, 30, 1136, 12)
    pb.wall_h(464, 836, 392, 12)  # Master / Bad (3.62 m -> 13.3 m²)
    pb.wall_h(464, 836, 598, 12)  # Bad / Sov 2 (2.00 m -> ~7.1 m²)
    pb.wall_h(464, 836, 866, 12)  # Sov 2 / Sov 3 (~2.62 m -> ~9.2 m²)

    # Doors
    pb.door(464, 285, 85, "v_down_right", wall_t=12)  # Master
    pb.door(464, 465, 80, "v_down_right", wall_t=12)  # Bad
    pb.door(464, 635, 85, "v_down_right", wall_t=12)  # Sov 2
    pb.door(464, 900, 85, "v_down_right", wall_t=12)  # Sov 3

    # East & north windows (4 clean vertical axes matching 1. etg & Fasade Øst!)
    pb.window_v(851, 158, 282, 30)   # Axis 4: Master east
    pb.window_v(851, 433, 557, 30)   # Axis 3: Bad east
    pb.window_v(851, 648, 772, 30)   # Axis 2: Sov 2 east
    pb.window_v(851, 928, 1052, 30)  # Axis 1: Sov 3 east
    pb.window_h(360, 440, 15, 30)    # Hall north (symmetric center)
    pb.window_h(80, 205, 15, 30)     # Trapp north (symmetric west)
    pb.window_h(615, 745, 15, 30)    # Master north (symmetric east)

    # Fixtures — Master (north headboard, matching Magnus's 2. etg sketch!)
    pb.double_bed(605, 42, 180, 200, head="top")
    pb.wardrobe(474, 36, 58, 225, "Skap")
    pb.room_label(680, 315, "Hovedsoverom", "13,3 m²")

    # Fixtures — Bad 2. etg (WC, servant, dusj along north wall; skap/vask along south wall)
    pb.wc(485, 404, rot=0)
    pb.sink(580, 404, 115, 46)
    pb.shower(734, 404, 92, 92)
    pb.wardrobe(585, 542, 160, 46, "Skap")
    pb.washer_dryer(766, 530, count=1, vertical=False)
    pb.room_label(625, 495, "Bad", "7,0 m²", "(rør nær bad 1. etg)")

    # Sov 2
    pb.single_bed(626, 616, 200, 105, head="right")
    pb.desk(680, 790, 140, 58)
    pb.wardrobe(474, 740, 55, 114)
    pb.room_label(595, 745, "Soverom 2", "9,2 m²")

    # Sov 3 (with dashed future kitchen option over 1. etg kitchen!)
    pb.single_bed(626, 886, 200, 105, head="right")
    pb.desk(680, 1060, 140, 58)
    pb.rect(774, 878, 56, 250, fill="none", stroke="#d97706", sw=2, dash="7,5")
    pb.room_label(595, 1015, "Soverom 3", "9,4 m²", "(el. kjøkken utleie)")


def build_alt1_floor1(pb: PlanBuilder):
    """Alternativ 1 - 1. etg: Nord-tilbygg + 3.20m x 5.20m vest-tilbygg (y=410..930) + Vask (3.9 m²) sør for trapp."""
    west_d, wy1, wy2 = 320, 410, 930
    draw_outer_shell(pb, west_d, wy1, wy2, north_ext=True)

    # Social & hall tints
    pb.rect(-290, 440, 290 + 440, 460, fill="#fffbeb", opacity=0.8)
    pb.rect(30, 820, 440, 316, fill="#fefce8", opacity=0.75)
    pb.rect(-286, 444, 418, 452, fill="none", stroke="#0284c7", sw=3, dash="12,8")
    pb.rect(30, 256, 220, 178, fill="#eff6ff", opacity=0.85)  # Vask
    pb.rect(256, 30, 200, 410, fill="#f8fafc", opacity=0.85)  # Gang

    # Shared east side + north extension (100% match to Magnus's sketch!)
    draw_shared_east_floor1(pb)

    # NW stairwell + Vask
    pb.wall_v(256, 30, 440, 12)
    pb.wall_h(30, 256, 256, 12)
    pb.wall_h(30, 256, 434, 14)  # TV wall north of living!
    pb.door(256, 145, 85, "v_down_left", wall_t=12)  # Into stairwell
    pb.door(256, 315, 80, "v_down_left", wall_t=12)  # Into Vask

    # Bearing beam dashed lines
    pb.line(170, 434, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 468, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    # West & south windows
    pb.window_v(-305, 510, 840, 30)
    pb.window_h(-220, -60, 915, 30)
    pb.window_h(110, 290, 1151, 30)
    pb.window_v(15, 95, 195, 30)

    # Fixtures & furniture
    pb.stairs_u(36, 36, 212, 212)
    pb.washer_dryer(42, 270, count=2, vertical=False)
    pb.sink(174, 270, 72, 45)
    pb.dining_table(240, 1005, 240, 100, seats=8)
    pb.tv_bench(-185, 444, 195, 42)
    pb.sofa_l(-270, 650, w_horiz=280, h_vert=225, depth=92, corner="bl")
    pb.coffee_table(-145, 625, 130, 75)
    pb.armchair(32, 600, 76, 76)
    pb.chimney_and_fireplace(135, 720, 95, 55, label_side="right")

    # Labels
    pb.room_label(142, 138, "Trapp", "4,8 m²")
    pb.room_label(125, 375, "Vask", "3,9 m²")
    pb.text(355, 265, "Gang", size=20, weight="700", fill="#475569")
    pb.text(-80, 550, "STUE ~24 m²", size=24, weight="800", fill="#0369a1")
    pb.text(-80, 578, "(4,25 × 4,60 m fritt vest for pipe)", size=17, weight="700", fill="#0284c7")
    pb.text(240, 912, "SPISESTUE ~11 m²", size=19, weight="700", fill="#854d0e")

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

    pb.rect(-290, 440, 290 + 440, 460, fill="#fffbeb", opacity=0.8)
    pb.rect(30, 820, 440, 316, fill="#fefce8", opacity=0.75)
    pb.rect(-286, 444, 418, 452, fill="none", stroke="#0284c7", sw=3, dash="12,8")
    pb.rect(30, 256, 220, 178, fill="#eff6ff", opacity=0.8)
    pb.rect(256, 30, 210, 226, fill="#f8fafc", opacity=0.9)
    pb.rect(256, 256, 210, 184, fill="#f8fafc", opacity=0.7)

    draw_shared_east_floor2(pb)

    pb.wall_v(256, 30, 440, 12)
    pb.wall_h(30, 256, 256, 12)
    pb.wall_h(30, 256, 434, 14)
    pb.wall_h(256, 464, 256, 12)
    pb.line(170, 434, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 464, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    pb.door(256, 130, 85, "v_down_right", wall_t=12)
    pb.door(310, 256, 90, "h_right_down", wall_t=12)
    pb.door(256, 315, 80, "v_down_left", wall_t=12)

    pb.window_v(-305, 510, 840, 30)
    pb.window_h(-220, -60, 915, 30)
    pb.window_h(120, 320, 1151, 30)
    pb.window_v(15, 95, 195, 30)

    pb.stairs_u(36, 36, 212, 212)
    pb.washer_dryer(42, 270, count=2, vertical=False)
    pb.wardrobe(42, 375, 195, 48)
    pb.tv_bench(-185, 444, 195, 42)
    pb.sofa_l(-270, 650, w_horiz=280, h_vert=225, depth=92, corner="bl")
    pb.coffee_table(-145, 625, 130, 75)
    pb.dining_table(240, 1005, 200, 95, seats=6)
    pb.chimney_and_fireplace(135, 720, 95, 55, label_side="right")

    pb.room_label(142, 138, "Trapp", "4,8 m²")
    pb.room_label(118, 352, "Bod / Vask", "3,6 m²")
    pb.room_label(362, 100, "Hall", "4,5 m²", "(2-mannsbolig)")
    pb.text(-80, 550, "LOFTSTUE / HAGESTUE", size=22, weight="800", fill="#0369a1")
    pb.text(-80, 578, "~24 m² + 11 m² spis (innbygd)", size=17, weight="700", fill="#0284c7")

    pb.dim_h(0, 866, -265, "8,66 m", bold=True)
    pb.dim_h(-320, 0, -265, "3,20 m (innbygd 2. etg)", color="#0284c7", bold=True)
    pb.dim_v(925, 30, 392, "3,6 m", text_offset=24)
    pb.dim_v(925, 392, 598, "2,0 m", text_offset=24)
    pb.dim_v(925, 598, 866, "2,7 m", text_offset=24)
    pb.dim_v(925, 866, 1136, "2,8 m", text_offset=24)


def build_alt2_floor1(pb: PlanBuilder):
    """Alternativ 2 - 1. etg: Nord-tilbygg + 100% symmetrisk 2.30m x 4.60m vest-tilbygg (y=353..813) på eksist. mur!
    Kompakt Vask/Bod (2.7 m²) sør for trapp + identisk 8.7 m² Bad, WC og 13.5 m² Sov i øst!"""
    west_d, wy1, wy2 = 230, 353, 813
    draw_outer_shell(pb, west_d, wy1, wy2, north_ext=True)

    pb.rect(-200, 383, 668, 400, fill="#fffbeb", opacity=0.85)
    pb.rect(30, 783, 440, 353, fill="#fefce8", opacity=0.75)
    pb.rect(-196, 387, 586, 330, fill="none", stroke="#059669", sw=3.2, dash="12,8")
    pb.rect(-196, 717, 318, 62, fill="none", stroke="#059669", sw=2.5, dash="8,6")
    pb.rect(30, 250, 220, 127, fill="#eff6ff", opacity=0.85)  # Kompakt Vask / Bod
    pb.rect(256, 30, 200, 353, fill="#f8fafc", opacity=0.85)  # Gang

    # Shared east side + north extension (100% match to Magnus's sketch!)
    draw_shared_east_floor1(pb)

    # NW stairwell + compact Vask/Bod
    pb.wall_v(256, 30, 383, 12)
    pb.wall_h(30, 256, 248, 12)
    pb.wall_h(30, 256, 380, 14)  # TV wall north of living!
    pb.door(256, 140, 85, "v_down_left", wall_t=12)  # Stairwell
    pb.door(256, 275, 80, "v_down_left", wall_t=12)  # Kompakt Vask/Bod

    # Structural beam dashed lines
    pb.line(170, 383, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 468, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    # West & south windows
    pb.window_v(-215, 435, 735, 30)
    pb.window_h(-165, -45, 798, 30)
    pb.window_h(-165, -45, 368, 30)
    pb.window_h(100, 300, 1151, 30)
    pb.window_v(15, 900, 1050, 30)
    pb.window_v(15, 85, 190, 30)

    # Fixtures & furniture
    pb.stairs_u(36, 36, 212, 206)
    pb.washer_dryer(40, 262, count=1, vertical=False)  # Vaskesøyle (V+T)
    pb.rect(40, 326, 62, 44, fill="#f1f5f9", stroke="#64748b", sw=1.5)  # Benk/utslagsvask
    pb.dining_table(235, 975, 240, 100, seats=8)
    pb.tv_bench(38, 388, 200, 42)
    pb.sofa_l(-180, 540, w_horiz=285, h_vert=220, depth=92, corner="bl")
    pb.coffee_table(-55, 530, 135, 75)
    pb.armchair(225, 515, 78, 78)
    pb.armchair(225, 615, 78, 78)
    pb.chimney_and_fireplace(135, 720, 95, 55, label_side="right")

    # Labels
    pb.room_label(142, 135, "Trapp", "4,7 m²")
    pb.room_label(162, 315, "Vask / Bod", "2,7 m²")
    pb.text(355, 250, "Gang", size=20, weight="700", fill="#475569")
    pb.text(90, 468, "STUE 23,6 m² (4,00 × 5,90 m)", size=22, weight="800", fill="#047857")
    pb.text(90, 494, "Helt fritt rektangel NORD for original pipe!", size=16, weight="700", fill="#059669")
    pb.text(235, 882, "SPISESTUE ~12,8 m²", size=19, weight="700", fill="#854d0e")

    # Symmetry & dimensions
    pb.dim_h(0, 866, -265, "8,66 m (eksisterende bredde)", bold=True)
    pb.dim_h(-230, 0, -265, "2,30 m (eksist. mur!)", color="#059669", bold=True)
    pb.dim_v(960, -210, 0, "2,10 m nord", color="#ea580c", bold=True, text_offset=26)
    pb.dim_v(960, 0, 1166, "11,66 m (eksisterende lengde — INGEN syd-tilbygg)", bold=True, text_offset=26)
    pb.dim_v(-295, 0, 353, "3,53 m (symmetri!)", color="#059669", bold=True)
    pb.dim_v(-295, 353, 813, "4,60 m (vest-tilbygg)", color="#059669", bold=True)
    pb.dim_v(-295, 813, 1166, "3,53 m (symmetri!)", color="#059669", bold=True)


def build_alt2_floor2(pb: PlanBuilder):
    """Alternativ 2 - 2. etg."""
    west_d, wy1, wy2 = 230, 353, 813
    draw_outer_shell(pb, west_d, wy1, wy2, north_ext=False)

    pb.rect(-200, 383, 668, 400, fill="#fffbeb", opacity=0.85)
    pb.rect(30, 783, 440, 353, fill="#fefce8", opacity=0.75)
    pb.rect(-196, 387, 586, 330, fill="none", stroke="#059669", sw=3.2, dash="12,8")
    pb.rect(-196, 717, 318, 62, fill="none", stroke="#059669", sw=2.5, dash="8,6")
    pb.rect(30, 250, 220, 127, fill="#eff6ff", opacity=0.85)
    pb.rect(256, 30, 210, 220, fill="#f8fafc", opacity=0.9)
    pb.rect(256, 250, 210, 133, fill="#f8fafc", opacity=0.7)

    draw_shared_east_floor2(pb)

    pb.wall_v(256, 30, 383, 12)
    pb.wall_h(30, 256, 248, 12)
    pb.wall_h(30, 256, 380, 14)
    pb.wall_h(256, 464, 248, 12)
    pb.line(170, 383, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 464, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    pb.door(256, 130, 85, "v_down_right", wall_t=12)
    pb.door(310, 248, 90, "h_right_down", wall_t=12)
    pb.door(256, 275, 80, "v_down_left", wall_t=12)

    pb.window_v(-215, 435, 735, 30)
    pb.window_h(-165, -45, 798, 30)
    pb.window_h(-165, -45, 368, 30)
    pb.window_h(100, 300, 1151, 30)
    pb.window_v(15, 900, 1050, 30)
    pb.window_v(15, 85, 190, 30)

    pb.stairs_u(36, 36, 212, 206)
    pb.washer_dryer(40, 262, count=1, vertical=False)
    pb.rect(40, 326, 62, 42, fill="#f1f5f9", stroke="#64748b", sw=1.5)
    pb.tv_bench(38, 388, 200, 42)
    pb.sofa_l(-180, 540, w_horiz=285, h_vert=220, depth=92, corner="bl")
    pb.coffee_table(-55, 530, 135, 75)
    pb.dining_table(235, 975, 200, 95, seats=6)
    pb.chimney_and_fireplace(135, 720, 95, 55, label_side="right")

    pb.room_label(142, 135, "Trapp", "4,7 m²")
    pb.room_label(162, 315, "Bod / Vask", "2,7 m²")
    pb.room_label(362, 100, "Hall", "4,4 m²", "(2-mannsbolig)")
    pb.text(90, 468, "LOFTSTUE / HAGESTUE 23,6 m²", size=20, weight="800", fill="#047857")
    pb.text(90, 494, "(4,00 × 5,90 m + 12,8 m² sørvest)", size=16, weight="700", fill="#059669")

    pb.dim_h(0, 866, -265, "8,66 m", bold=True)
    pb.dim_h(-230, 0, -265, "2,30 m (innbygd 2. etg)", color="#059669", bold=True)
    pb.dim_v(925, 30, 392, "3,6 m", text_offset=24)
    pb.dim_v(925, 392, 598, "2,0 m", text_offset=24)
    pb.dim_v(925, 598, 866, "2,7 m", text_offset=24)
    pb.dim_v(925, 866, 1136, "2,8 m", text_offset=24)


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
        f'<text x="780" y="212" font-size="30" font-weight="800" fill="#0f172a" text-anchor="middle">1. ETASJE (inkl. 1-etg nord-tilbygg: Vindfang, Kjellernedgang &amp; Utebod)</text>',
        f'<text x="2340" y="212" font-size="30" font-weight="800" fill="#0f172a" text-anchor="middle">2. ETASJE (Soverom + Stue / Utleie-opsjon)</text>',
        f'<line x1="1575" y1="190" x2="1575" y2="1730" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="10,8"/>',
    ]

    pb1 = PlanBuilder(ox=480, oy=520)
    fn1(pb1)
    svg.extend(pb1.els)

    pb2 = PlanBuilder(ox=2020, oy=520)
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
            "Stue ~24 m² (4,25 × 4,60 m vest for pipe)",
            "Nord-tilbygg (Vindfang 5,4 m², Kjellernedg., Utebod) + 8,7 m² Bad",
            "Krever ~0,9 m nytt fundament vest + 25° tak / 1-løps pipe (#38)",
        ],
    )
    make_sheet(
        "plan_alt2_symmetrisk_vest.svg",
        "M6 — ALTERNATIV 2: Symmetrisk vest-tilbygg (2,30 × 4,60 m) + Nord-tilbygg",
        "Tro mot 1:50-skisse i nord/øst (8,7 m² Bad, 13,5 m² Sov, Nord-tilbygg) • 100 % symmetrisk vestfasade (3,53 | 4,60 | 3,53 m) • 4,00 × 5,90 m stue NORD for pipe",
        "#059669",
        build_alt2_floor1,
        build_alt2_floor2,
        [
            "Stue 23,6 m² (4,00 × 5,90 m fritt NORD for pipe)",
            "Samme 8,7 m² Bad + 13,5 m² Sov + Nord-tilbygg + 2,7 m² Vask/Bod",
            "Rett på eksist. 2,3 m mur + 0 pipekonflikt på tak (grønn linje #38)",
        ],
    )
