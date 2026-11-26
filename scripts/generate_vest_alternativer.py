#!/usr/bin/env python3
"""
Generate architectural 2D SVG floor plans (1 px = 1 cm scale) comparing
Alternativ 1 (3.2m x 5.2m west extension) and Alternativ 2 (2.3m x 4.6m symmetric west extension)
for Myrteveien 6 (Issue #50), preserving the exact original 1946/1947 main footprint (11.66m x 8.66m)
and exact original chimney location.
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
    y=0 is main north outer wall, y=1166 is main south outer wall. Negative x extends west."""

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
        self.text(cx, cy - (10 if sub else 4), name, size=23, weight="700", fill="#1e293b")
        self.text(cx, cy + (16 if sub else 22), area_str, size=19, weight="600", fill="#475569")
        if sub:
            self.text(cx, cy + 40, sub, size=15, weight="500", fill="#64748b")

    def wall_h(self, x1, x2, y_center, thick=12, fill="#475569"):
        self.rect(x1, y_center - thick / 2, x2 - x1, thick, fill=fill)

    def wall_v(self, x_center, y1, y2, thick=12, fill="#475569"):
        self.rect(x_center - thick / 2, y1, thick, y2 - y1, fill=fill)

    def window_h(self, x1, x2, y_center, wall_t=30):
        # Clear opening in outer wall + glazing lines
        self.rect(x1, y_center - wall_t / 2, x2 - x1, wall_t, fill="#ffffff", stroke="#334155", sw=2)
        self.line(x1, y_center - 5, x2, y_center - 5, stroke="#0284c7", sw=3.5)
        self.line(x1, y_center + 5, x2, y_center + 5, stroke="#0284c7", sw=3.5)

    def window_v(self, x_center, y1, y2, wall_t=30):
        self.rect(x_center - wall_t / 2, y1, wall_t, y2 - y1, fill="#ffffff", stroke="#334155", sw=2)
        self.line(x_center - 5, y1, x_center - 5, y2, stroke="#0284c7", sw=3.5)
        self.line(x_center + 5, y1, x_center + 5, y2, stroke="#0284c7", sw=3.5)

    def door(self, hx, hy, w, orientation="right_down", wall_t=14):
        """Draw wall cutout + 90-degree door leaf + dashed swing arc.
        hinge at (hx, hy), width w."""
        # Cutout + leaf + arc based on orientation
        px, py = self.p(hx, hy)
        if orientation == "h_right_down":  # horizontal wall, hinge left, swings down
            self.rect(hx, hy - wall_t / 2 - 1, w, wall_t + 2, fill="#ffffff")
            self.line(hx, hy, hx, hy + w, stroke="#334155", sw=3.5)
            self.path(f"M {px:.1f} {py + w:.1f} A {w} {w} 0 0 0 {px + w:.1f} {py:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "h_right_up":  # horizontal wall, hinge left, swings up
            self.rect(hx, hy - wall_t / 2 - 1, w, wall_t + 2, fill="#ffffff")
            self.line(hx, hy, hx, hy - w, stroke="#334155", sw=3.5)
            self.path(f"M {px:.1f} {py - w:.1f} A {w} {w} 0 0 1 {px + w:.1f} {py:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "h_left_down":  # horizontal wall, hinge right, swings down
            self.rect(hx - w, hy - wall_t / 2 - 1, w, wall_t + 2, fill="#ffffff")
            self.line(hx, hy, hx, hy + w, stroke="#334155", sw=3.5)
            self.path(f"M {px:.1f} {py + w:.1f} A {w} {w} 0 0 1 {px - w:.1f} {py:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "h_left_up":  # horizontal wall, hinge right, swings up
            self.rect(hx - w, hy - wall_t / 2 - 1, w, wall_t + 2, fill="#ffffff")
            self.line(hx, hy, hx, hy - w, stroke="#334155", sw=3.5)
            self.path(f"M {px:.1f} {py - w:.1f} A {w} {w} 0 0 0 {px - w:.1f} {py:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "v_down_right":  # vertical wall, hinge top, swings right
            self.rect(hx - wall_t / 2 - 1, hy, wall_t + 2, w, fill="#ffffff")
            self.line(hx, hy, hx + w, hy, stroke="#334155", sw=3.5)
            self.path(f"M {px + w:.1f} {py:.1f} A {w} {w} 0 0 1 {px:.1f} {py + w:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "v_down_left":  # vertical wall, hinge top, swings left
            self.rect(hx - wall_t / 2 - 1, hy, wall_t + 2, w, fill="#ffffff")
            self.line(hx, hy, hx - w, hy, stroke="#334155", sw=3.5)
            self.path(f"M {px - w:.1f} {py:.1f} A {w} {w} 0 0 0 {px:.1f} {py + w:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "v_up_right":  # vertical wall, hinge bottom, swings right
            self.rect(hx - wall_t / 2 - 1, hy - w, wall_t + 2, w, fill="#ffffff")
            self.line(hx, hy, hx + w, hy, stroke="#334155", sw=3.5)
            self.path(f"M {px + w:.1f} {py:.1f} A {w} {w} 0 0 0 {px:.1f} {py - w:.1f}", stroke="#64748b", sw=2, dash="6,5")
        elif orientation == "v_up_left":  # vertical wall, hinge bottom, swings left
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

    # --- Furniture & fixture stencils (exact cm scale) ---
    def stairs_u(self, x, y, w, h):
        self.rect(x, y, w, h, fill="#e2e8f0", stroke="#64748b", sw=2)
        # U-shaped staircase with central wall/well
        mid_x = x + w / 2
        steps = 7
        step_h = (h - 75) / steps
        for i in range(steps):
            sy = y + 75 + i * step_h
            self.line(x, sy, mid_x - 8, sy, stroke="#64748b", sw=1.5)
            self.line(mid_x + 8, sy, x + w, sy, stroke="#64748b", sw=1.5)
        self.rect(mid_x - 8, y + 75, 16, h - 75, fill="#94a3b8")
        # Direction arrow
        ax1, ay1 = self.p(x + w * 0.25, y + h - 20)
        ax2, ay2 = self.p(x + w * 0.25, y + 38)
        ax3, ay3 = self.p(x + w * 0.75, y + 38)
        ax4, ay4 = self.p(x + w * 0.75, y + h - 25)
        self.path(f"M {ax1:.1f} {ay1:.1f} L {ax2:.1f} {ay2:.1f} L {ax3:.1f} {ay3:.1f} L {ax4:.1f} {ay4:.1f}", stroke="#334155", sw=2.5)
        self.path(f"M {ax4 - 10:.1f} {ay4 - 12:.1f} L {ax4:.1f} {ay4:.1f} L {ax4 + 10:.1f} {ay4 - 12:.1f}", stroke="#334155", sw=2.5)

    def chimney_and_fireplace(self, x=135, y=720, w=95, h=55, label_side="right"):
        """Exact original chimney core (95 cm east-west x 55 cm north-south) + fireplace insert."""
        # Main masonry chimney block (longest axis EAST-WEST!)
        self.rect(x, y, w, h, fill="#b45309", stroke="#78350f", sw=3)
        # Two flues side-by-side EAST-WEST
        self.rect(x + 12, y + 12, 28, 31, fill="#fef3c7", stroke="#78350f", sw=2)
        self.rect(x + 54, y + 12, 28, 31, fill="#fef3c7", stroke="#78350f", sw=2)
        # Fireplace glass hearth on west end (facing living room)
        self.rect(x - 18, y + 8, 18, h - 16, fill="#fb923c", stroke="#9a3412", sw=2)
        lx = x + w + 12 if label_side == "right" else x - 22
        anc = "start" if label_side == "right" else "end"
        self.text(lx, y + 10, "Orig. pipe (95×55 cm Ø–V)", size=15, weight="700", fill="#9a3412", anchor=anc)
        self.text(lx, y + 28, "(slanket + peis mot vest/sør)", size=13, weight="600", fill="#b45309", anchor=anc)

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

    def single_bed(self, x, y, w=200, h=100, head="right"):
        self.rect(x, y, w, h, fill="#ffffff", stroke="#64748b", sw=2, rx=4)
        if head == "right":
            self.rect(x + w - 40, y + 14, 30, h - 28, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=4)
            self.line(x + w - 56, y, x + w - 56, y + h, stroke="#cbd5e1", sw=1.5)
        else:
            self.rect(x + 14, y + 10, w - 28, 30, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=4)

    def desk(self, x, y, w=120, h=60):
        self.rect(x, y, w, h, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=2)
        self.text(x + w / 2, y + h / 2 + 6, "Pult", size=14, fill="#64748b")

    def wardrobe(self, x, y, w, h):
        self.rect(x, y, w, h, fill="#f1f5f9", stroke="#64748b", sw=1.8)
        self.line(x, y, x + w, y + h, stroke="#cbd5e1", sw=1.2)
        self.line(x + w, y, x, y + h, stroke="#cbd5e1", sw=1.2)

    def sofa_l(self, x, y, w_horiz=280, h_vert=210, depth=92, corner="bl"):
        """L-shaped sectional sofa facing north/east (corner='bl' or 'tl')."""
        if corner == "bl":
            # Vertical arm along left (west), horizontal arm along bottom (south)
            self.rect(x, y, depth, h_vert, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)
            self.rect(x, y + h_vert - depth, w_horiz, depth, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)
            # Backrests
            self.rect(x + 4, y + 4, 22, h_vert - 8, fill="#bae6fd", stroke="#0369a1", sw=1.2, rx=3)
            self.rect(x + 4, y + h_vert - 26, w_horiz - 8, 22, fill="#bae6fd", stroke="#0369a1", sw=1.2, rx=3)
        elif corner == "br":
            self.rect(x + w_horiz - depth, y, depth, h_vert, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)
            self.rect(x, y + h_vert - depth, w_horiz, depth, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)
            self.rect(x + w_horiz - 26, y + 4, 22, h_vert - 8, fill="#bae6fd", stroke="#0369a1", sw=1.2, rx=3)
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
        # Chairs top & bottom
        n_side = (seats - 2) // 2
        for i in range(n_side):
            chx = x + 28 + i * ((w - 56) / max(1, n_side - 1)) - 20
            self.rect(chx, y - 34, 40, 30, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=4)
            self.rect(chx, y + h + 4, 40, 30, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=4)
        # End chairs
        self.rect(x - 34, cy - 20, 30, 40, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=4)
        self.rect(x + w + 4, cy - 20, 30, 40, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=4)
        self.rect(x, y, w, h, fill="#fefce8", stroke="#a16207", sw=2.2, rx=4)
        self.text(cx, cy + 7, f"Spisebord ({seats} pers)", size=17, weight="600", fill="#854d0e")

    def kitchen_block(self, x_east_inner=836, y_north=760, y_south=1136, x_left=470):
        # Tall cabinets on north wall (60 cm deep)
        self.rect(x_left + 15, y_north, x_east_inner - x_left - 75, 60, fill="#f1f5f9", stroke="#475569", sw=2)
        self.text((x_left + 15 + x_east_inner - 60) / 2, y_north + 36, "Høyskap (kjøl/ovn)", size=14, fill="#475569")
        # Counter on east wall (60 cm deep)
        self.rect(x_east_inner - 60, y_north, 60, y_south - y_north - 10, fill="#f8fafc", stroke="#475569", sw=2)
        # Sink symbol
        self.rect(x_east_inner - 50, y_north + 115, 40, 65, fill="#e0f2fe", stroke="#0284c7", sw=1.6, rx=3)
        # Cooktop symbol
        self.rect(x_east_inner - 52, y_north + 235, 44, 65, fill="#1e293b", stroke="#0f172a", sw=1.5, rx=2)
        # Kitchen island (100 x 200 cm, 115 cm clearance to east counter & north cabinets)
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


def draw_outer_shell(pb: PlanBuilder, west_depth: float, wy1: float, wy2: float, show_existing_dashed=True):
    """Draw 30cm insulated outer shell for main rectangle + west extension."""
    # Exterior polygon (clockwise from NW corner of main body)
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
    # Interior polygon (30 cm inset)
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
    # Draw solid dark gray outer shell, then white interior background
    pb.poly(outer_pts, fill="#334155", stroke="#0f172a", sw=3)
    pb.poly(inner_pts, fill="#ffffff", stroke="#334155", sw=2)

    # Existing west bump-out reference dashed line (2.28m deep, y=415..822)
    if show_existing_dashed:
        ex_pts = [
            (0, 415),
            (-228, 415),
            (-228, 822),
            (0, 822),
        ]
        d = "M " + " L ".join(f"{pb.ox + x:.1f} {pb.oy + y:.1f}" for x, y in ex_pts)
        pb.path(d, stroke="#ea580c", sw=3.5, dash="14,10")


def build_alt1_floor1(pb: PlanBuilder):
    """Alternativ 1 - 1. etasje: 3.20m x 5.20m vest-tilbygg (y=410..930), Vask beholdt sør for trapp."""
    west_d, wy1, wy2 = 320, 410, 930
    draw_outer_shell(pb, west_d, wy1, wy2, show_existing_dashed=True)

    # Zone background tints
    # Social zone (living + dining + kitchen)
    pb.rect(-290, 440, 290 + 440, 460, fill="#fffbeb", opacity=0.8)  # living
    pb.rect(30, 820, 440, 316, fill="#fefce8", opacity=0.75)  # dining
    pb.rect(470, 760, 366, 376, fill="#fef3c7", opacity=0.55)  # kitchen
    # Highlight the 4.25m x 4.60m clear living rectangle west of chimney!
    pb.rect(-286, 444, 418, 452, fill="none", stroke="#0284c7", sw=3, dash="12,8")
    # Wet & service zones
    pb.rect(30, 256, 220, 178, fill="#eff6ff", opacity=0.8)  # vask
    pb.rect(550, 150, 286, 250, fill="#eff6ff", opacity=0.8)  # bad
    pb.rect(455, 225, 95, 175, fill="#eff6ff", opacity=0.8)  # wc
    pb.rect(550, 30, 286, 114, fill="#f1f5f9", opacity=0.9)  # utebod
    # Arrival & hall
    pb.rect(256, 30, 294, 195, fill="#f8fafc", opacity=0.9)
    pb.rect(256, 225, 199, 215, fill="#f8fafc", opacity=0.9)
    # Bedroom 1.04
    pb.rect(470, 408, 366, 344, fill="#f0fdf4", opacity=0.7)

    # Interior walls
    # NW stairwell (220 x 220)
    pb.wall_v(256, 30, 440, 12)
    pb.wall_h(30, 256, 256, 12)
    pb.wall_h(30, 256, 434, 14)  # wall between vask & living (TV wall!)
    # NE utebod + bad + WC
    pb.wall_v(546, 30, 404, 12)
    pb.wall_h(546, 836, 144, 12)  # utebod south wall
    pb.wall_h(450, 836, 404, 12)  # bad/wc south wall
    pb.wall_v(450, 220, 404, 12)  # wc west wall
    pb.wall_h(450, 546, 220, 12)  # wc north wall
    # Bedroom 1.04 (east mid)
    pb.wall_v(464, 404, 756, 12)
    pb.wall_h(464, 836, 756, 12)
    # Bearing beam line (dashed) from chimney to north/east
    pb.line(170, 434, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 464, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    # Doors
    pb.door(330, 30, 100, "h_right_down", wall_t=30)  # Main north entrance
    pb.door(256, 150, 85, "v_down_left", wall_t=12)  # Into NW stairwell (2-mannsbolig lockable!)
    pb.door(256, 315, 80, "v_down_left", wall_t=12)  # Into Vask
    pb.door(450, 290, 75, "v_down_right", wall_t=12)  # Into WC
    pb.door(546, 265, 80, "v_down_right", wall_t=12)  # Into Bad (clear of shower)
    pb.door(464, 420, 85, "v_down_right", wall_t=12)  # Into Sov 1.04
    pb.door(836, 55, 85, "v_down_right", wall_t=30)  # Utebod external door (east)
    pb.double_terrace_door_h(530, 1151, 160, wall_t=30, swing_down=True)  # Terrace south

    # Windows
    pb.window_v(-305, 510, 840, 30)  # Big west living window (kveldssol!)
    pb.window_h(-220, -60, 915, 30)  # South window in west wing
    pb.window_h(110, 290, 1151, 30)  # South dining window
    pb.window_v(851, 860, 1040, 30)  # Kitchen east window
    pb.window_v(851, 500, 660, 30)  # Sov 1.04 east window
    pb.window_v(851, 210, 330, 30)  # Bad east window
    pb.window_v(15, 95, 195, 30)  # Stairwell west window

    # Fixtures & furniture
    pb.stairs_u(36, 36, 212, 212)
    pb.washer_dryer(42, 270, count=2, vertical=False)
    pb.sink(174, 270, 72, 45)
    pb.tub(750, 162, 76, 165)
    pb.shower(558, 158, 90, 90)
    pb.sink(600, 348, 120, 45)
    pb.wc(765, 350, rot=90)
    pb.wc(462, 232, rot=0)
    pb.sink(462, 348, 52, 42)
    # Bedroom 1.04
    pb.double_bed(650, 520, 180, 200, head="right")
    pb.desk(650, 415, 130, 58)
    pb.wardrobe(474, 520, 58, 224)
    # Kitchen
    pb.kitchen_block(836, 764, 1132, 470)
    # Dining
    pb.dining_table(240, 1005, 240, 100, seats=8)
    # Living room (west of chimney!)
    pb.tv_bench(-185, 444, 195, 42)
    pb.sofa_l(-270, 650, w_horiz=280, h_vert=225, depth=92, corner="bl")
    pb.coffee_table(-145, 625, 130, 75)
    pb.armchair(32, 600, 76, 76)
    # Original chimney (freestanding, 95 cm east-west x 55 cm north-south!)
    pb.chimney_and_fireplace(135, 720, 95, 55, label_side="right")

    # Room labels
    pb.room_label(142, 138, "Trapp", "4,8 m²")
    pb.room_label(125, 375, "Vask", "3,9 m²")
    pb.room_label(395, 155, "Entré / Hall", "11,2 m²")
    pb.room_label(695, 92, "Utebod", "3,1 m²")
    pb.room_label(685, 285, "Bad", "7,1 m²")
    pb.text(500, 315, "WC", size=17, weight="700", fill="#1e293b")
    pb.room_label(588, 605, "Sov / Kontor", "12,3 m²")
    pb.room_label(650, 875, "Kjøkken", "14,5 m²")
    pb.text(-80, 550, "STUE ~24 m²", size=24, weight="800", fill="#0369a1")
    pb.text(-80, 578, "(4,25 × 4,60 m fritt vest for pipe)", size=17, weight="700", fill="#0284c7")
    pb.text(240, 912, "SPISESTUE ~11 m²", size=19, weight="700", fill="#854d0e")

    # Dimension chains
    pb.dim_h(0, 866, -55, "8,66 m (eksisterende bredde)", bold=True)
    pb.dim_h(-320, 0, -55, "3,20 m ny vest", color="#0284c7", bold=True)
    pb.dim_v(-385, 0, 410, "4,10 m", color="#475569")
    pb.dim_v(-385, 410, 930, "5,20 m (nytt vest-tilbygg)", color="#0284c7", bold=True)
    pb.dim_v(-385, 930, 1166, "2,36 m", color="#475569")
    pb.dim_v(925, 0, 1166, "11,66 m (eksisterende lengde — INGEN syd-tilbygg)", bold=True, text_offset=26)


def build_alt1_floor2(pb: PlanBuilder):
    """Alternativ 1 - 2. etasje: Innbygd vest-stue (3.20m x 5.20m), 3 sov + bad + bod/vask."""
    west_d, wy1, wy2 = 320, 410, 930
    draw_outer_shell(pb, west_d, wy1, wy2, show_existing_dashed=True)

    # Zone background tints
    pb.rect(-290, 440, 290 + 440, 460, fill="#fffbeb", opacity=0.8)  # living
    pb.rect(30, 820, 440, 316, fill="#fefce8", opacity=0.75)  # south-west zone
    pb.rect(-286, 444, 418, 452, fill="none", stroke="#0284c7", sw=3, dash="12,8")
    pb.rect(30, 256, 220, 178, fill="#eff6ff", opacity=0.8)  # bod/vask
    pb.rect(256, 30, 210, 226, fill="#f8fafc", opacity=0.9)  # hall
    pb.rect(256, 256, 210, 184, fill="#f8fafc", opacity=0.7)  # gang
    # East rooms: Master, Bad, Sov 2, Sov 3
    pb.rect(470, 30, 366, 345, fill="#f0fdf4", opacity=0.75)  # master
    pb.rect(470, 385, 366, 200, fill="#eff6ff", opacity=0.85)  # bad
    pb.rect(470, 597, 366, 258, fill="#f0fdf4", opacity=0.75)  # sov 2
    pb.rect(470, 867, 366, 269, fill="#f0fdf4", opacity=0.75)  # sov 3 / kitchen option

    # Interior walls
    pb.wall_v(256, 30, 440, 12)
    pb.wall_h(30, 256, 256, 12)
    pb.wall_h(30, 256, 434, 14)  # wall between bod/vask & living
    pb.wall_h(256, 464, 256, 12)  # hall / 2-mannsbolig partition!
    pb.wall_v(464, 30, 1136, 12)  # main east rooms corridor wall
    pb.wall_h(464, 836, 381, 12)  # master / bad
    pb.wall_h(464, 836, 591, 12)  # bad / sov 2
    pb.wall_h(464, 836, 861, 12)  # sov 2 / sov 3
    # Bearing beam dashed lines
    pb.line(170, 434, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 464, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    # Doors
    pb.door(256, 130, 85, "v_down_right", wall_t=12)  # From stairwell to hall
    pb.door(310, 256, 90, "h_right_down", wall_t=12)  # Hall -> gang (2-mannsbolig door!)
    pb.door(256, 315, 80, "v_down_left", wall_t=12)  # Bod/Vask
    pb.door(464, 275, 85, "v_down_right", wall_t=12)  # Master sov
    pb.door(464, 445, 80, "v_down_right", wall_t=12)  # Bad
    pb.door(464, 625, 85, "v_down_right", wall_t=12)  # Sov 2
    pb.door(464, 895, 85, "v_down_right", wall_t=12)  # Sov 3

    # Windows
    pb.window_v(-305, 510, 840, 30)
    pb.window_h(-220, -60, 915, 30)
    pb.window_h(120, 320, 1151, 30)
    pb.window_v(851, 130, 280, 30)  # Master east
    pb.window_v(851, 435, 540, 30)  # Bad east
    pb.window_v(851, 665, 795, 30)  # Sov 2 east
    pb.window_v(851, 935, 1065, 30)  # Sov 3 east
    pb.window_h(310, 415, 15, 30)  # Hall north window
    pb.window_v(15, 95, 195, 30)  # Stairwell window

    # Fixtures & furniture
    pb.stairs_u(36, 36, 212, 212)
    pb.washer_dryer(42, 270, count=2, vertical=False)
    pb.wardrobe(42, 375, 195, 48)
    # Master bedroom
    pb.double_bed(646, 55, 180, 200, head="right")
    pb.wardrobe(474, 36, 58, 225)
    # Bad 2. etg (aligned near 1. etg bad/WC riser at y=398!)
    pb.shower(734, 393, 94, 94)
    pb.sink(575, 393, 120, 46)
    pb.wc(485, 393, rot=0)
    pb.wardrobe(620, 535, 206, 44)
    # Sov 2
    pb.single_bed(626, 610, 200, 105, head="right")
    pb.desk(680, 785, 140, 58)
    pb.wardrobe(474, 735, 55, 115)
    # Sov 3 (with dashed future kitchen option over 1. etg kitchen!)
    pb.single_bed(626, 880, 200, 105, head="right")
    pb.desk(680, 1060, 140, 58)
    pb.rect(774, 872, 56, 255, fill="none", stroke="#d97706", sw=2, dash="7,5")
    # Living room 2. etg
    pb.tv_bench(-185, 444, 195, 42)
    pb.sofa_l(-270, 650, w_horiz=280, h_vert=225, depth=92, corner="bl")
    pb.coffee_table(-145, 625, 130, 75)
    pb.dining_table(240, 1005, 200, 95, seats=6)
    # Chimney (95 cm east-west x 55 cm north-south)
    pb.chimney_and_fireplace(135, 720, 95, 55, label_side="right")

    # Labels
    pb.room_label(142, 138, "Trapp", "4,8 m²")
    pb.room_label(118, 352, "Bod / Vask", "3,6 m²")
    pb.room_label(362, 100, "Hall", "4,5 m²", "(2-mannsbolig)")
    pb.room_label(680, 305, "Hovedsoverom", "12,4 m²")
    pb.room_label(610, 480, "Bad", "7,2 m²", "(rør over 1. etg)")
    pb.room_label(595, 745, "Soverom 2", "9,2 m²")
    pb.room_label(595, 1015, "Soverom 3", "9,7 m²", "(el. kjøkken utleie)")
    pb.text(-80, 550, "LOFTSTUE / HAGESTUE", size=22, weight="800", fill="#0369a1")
    pb.text(-80, 578, "~24 m² + 11 m² spis (innbygd)", size=17, weight="700", fill="#0284c7")

    # Dimensions
    pb.dim_h(0, 866, -55, "8,66 m", bold=True)
    pb.dim_h(-320, 0, -55, "3,20 m (innbygd 2. etg)", color="#0284c7", bold=True)
    pb.dim_v(925, 30, 381, "3,5 m", text_offset=24)
    pb.dim_v(925, 381, 591, "2,1 m", text_offset=24)
    pb.dim_v(925, 591, 861, "2,7 m", text_offset=24)
    pb.dim_v(925, 861, 1136, "2,8 m", text_offset=24)


def build_alt2_floor1(pb: PlanBuilder):
    """Alternativ 2 - 1. etasje: Symmetrisk 2.30m x 4.60m vest-tilbygg (y=353..813) på eksist. mur!
    4.0m x 5.9m stue NORD for original pipe + 5.0 m² Vask/bi-inngang i nordøst + innebod ved trapp."""
    west_d, wy1, wy2 = 230, 353, 813
    draw_outer_shell(pb, west_d, wy1, wy2, show_existing_dashed=True)

    # Zone background tints
    # Living room NORTH of chimney: x=[-200..390], y=[383..783] -> 4.00m x 5.90m = 23.6 m²!!
    pb.rect(-200, 383, 660, 400, fill="#fffbeb", opacity=0.85)
    pb.rect(30, 783, 440, 353, fill="#fefce8", opacity=0.75)  # dining
    pb.rect(470, 760, 366, 376, fill="#fef3c7", opacity=0.55)  # kitchen
    # Highlight the EXACT 4.00m x 5.90m clear living rectangle NORTH of original chimney!
    pb.rect(-196, 387, 586, 330, fill="none", stroke="#059669", sw=3.2, dash="12,8")
    pb.rect(-196, 717, 318, 62, fill="none", stroke="#059669", sw=2.5, dash="8,6")
    # Service & wet core (all grouped in NE + bod by stairs!)
    pb.rect(30, 250, 220, 127, fill="#eff6ff", opacity=0.85)  # innebod / garderobe
    pb.rect(546, 30, 290, 175, fill="#eff6ff", opacity=0.85)  # vaskerom / bi-inngang
    pb.rect(546, 211, 290, 210, fill="#eff6ff", opacity=0.85)  # bad
    pb.rect(450, 230, 96, 191, fill="#eff6ff", opacity=0.85)  # wc
    # Hall
    pb.rect(256, 30, 290, 353, fill="#f8fafc", opacity=0.9)
    # Bedroom 1.04
    pb.rect(470, 427, 366, 325, fill="#f0fdf4", opacity=0.7)

    # Interior walls
    pb.wall_v(256, 30, 383, 12)
    pb.wall_h(30, 256, 248, 12)  # stair south wall
    pb.wall_h(30, 256, 380, 14)  # innebod south wall (TV wall!)
    # NE compact wet core: Vask + Bad + WC
    pb.wall_v(546, 30, 424, 12)
    pb.wall_h(546, 836, 208, 12)  # vask / bad wall
    pb.wall_h(450, 836, 424, 12)  # bad / sov wall
    pb.wall_v(450, 226, 424, 12)  # wc west wall
    pb.wall_h(450, 546, 226, 12)  # wc north wall
    # Bedroom 1.04
    pb.wall_v(464, 424, 756, 12)
    pb.wall_h(464, 836, 756, 12)
    # Structural beam line (dashed)
    pb.line(170, 383, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 464, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    # Doors
    pb.door(330, 30, 100, "h_right_down", wall_t=30)  # Main north entrance
    pb.door(256, 140, 85, "v_down_left", wall_t=12)  # Stairwell (2-mannsbolig)
    pb.door(256, 275, 80, "v_down_left", wall_t=12)  # Innebod / Garderobe
    pb.door(546, 80, 85, "v_down_right", wall_t=12)  # Vaskerom from hall
    pb.door(836, 75, 90, "v_down_right", wall_t=30)  # Vaskerom bi-inngang (east!)
    pb.door(450, 295, 75, "v_down_right", wall_t=12)  # WC
    pb.door(546, 285, 80, "v_down_right", wall_t=12)  # Bad
    pb.door(464, 445, 85, "v_down_right", wall_t=12)  # Sov 1.04
    pb.double_terrace_door_h(530, 1151, 160, wall_t=30, swing_down=True)

    # Windows
    pb.window_v(-215, 435, 735, 30)  # Large symmetric west window!
    pb.window_h(-165, -45, 798, 30)  # South window in west wing
    pb.window_h(-165, -45, 368, 30)  # North window in west wing (symmetric!)
    pb.window_h(100, 300, 1151, 30)  # South dining window
    pb.window_v(15, 900, 1050, 30)  # West dining window (evening sun!)
    pb.window_v(851, 860, 1040, 30)  # Kitchen east
    pb.window_v(851, 515, 665, 30)  # Sov east
    pb.window_v(851, 255, 365, 30)  # Bad east
    pb.window_v(15, 85, 190, 30)  # Stair west

    # Fixtures & furniture
    pb.stairs_u(36, 36, 212, 206)
    pb.wardrobe(40, 260, 125, 108)
    # NE Vaskerom (5.0 m²)
    pb.washer_dryer(560, 42, count=2, vertical=False)
    pb.sink(692, 42, 85, 48)
    pb.wardrobe(560, 152, 210, 46)
    # NE Bad (6.1 m²)
    pb.tub(750, 222, 76, 165)
    pb.shower(558, 220, 88, 88)
    pb.sink(595, 368, 120, 45)
    pb.wc(660, 222, rot=0)
    # WC
    pb.wc(460, 236, rot=0)
    pb.sink(460, 366, 52, 42)
    # Bedroom 1.04
    pb.double_bed(650, 535, 180, 200, head="right")
    pb.desk(650, 435, 130, 56)
    pb.wardrobe(474, 540, 58, 206)
    # Kitchen
    pb.kitchen_block(836, 764, 1132, 470)
    # Dining (generous south-west zone!)
    pb.dining_table(235, 975, 240, 100, seats=8)
    # Living room (4.00m x 5.90m NORTH of original chimney!)
    pb.tv_bench(38, 388, 200, 42)
    pb.sofa_l(-180, 540, w_horiz=285, h_vert=220, depth=92, corner="bl")
    pb.coffee_table(-55, 530, 135, 75)
    pb.armchair(225, 515, 78, 78)
    pb.armchair(225, 615, 78, 78)
    # Original chimney (freestanding divider between living & dining, 95x55 cm east-west!)
    pb.chimney_and_fireplace(135, 720, 95, 55, label_side="right")

    # Labels
    pb.room_label(142, 135, "Trapp", "4,7 m²")
    pb.room_label(125, 315, "Bod / Gard.", "2,7 m²")
    pb.room_label(395, 155, "Entré / Hall", "10,5 m²")
    pb.room_label(695, 125, "Vask / Bi-inng.", "5,0 m²")
    pb.room_label(665, 330, "Bad", "6,1 m²")
    pb.text(498, 320, "WC", size=17, weight="700", fill="#1e293b")
    pb.room_label(588, 615, "Sov / Kontor", "11,8 m²")
    pb.room_label(650, 875, "Kjøkken", "14,5 m²")
    pb.text(90, 468, "STUE 23,6 m² (4,00 × 5,90 m)", size=22, weight="800", fill="#047857")
    pb.text(90, 494, "Helt fritt rektangel NORD for original pipe!", size=16, weight="700", fill="#059669")
    pb.text(235, 882, "SPISESTUE ~12,8 m²", size=19, weight="700", fill="#854d0e")

    # Symmetry & dimension chains
    pb.dim_h(0, 866, -55, "8,66 m (eksisterende bredde)", bold=True)
    pb.dim_h(-230, 0, -55, "2,30 m (eksist. mur!)", color="#059669", bold=True)
    pb.dim_v(-295, 0, 353, "3,53 m (symmetri!)", color="#059669", bold=True)
    pb.dim_v(-295, 353, 813, "4,60 m (vest-tilbygg)", color="#059669", bold=True)
    pb.dim_v(-295, 813, 1166, "3,53 m (symmetri!)", color="#059669", bold=True)
    pb.dim_v(925, 0, 1166, "11,66 m (eksisterende lengde — INGEN syd-tilbygg)", bold=True, text_offset=26)


def build_alt2_floor2(pb: PlanBuilder):
    """Alternativ 2 - 2. etasje: Symmetrisk 2.30m x 4.60m innbygd vest-stue + 3 sov + bad + innebod."""
    west_d, wy1, wy2 = 230, 353, 813
    draw_outer_shell(pb, west_d, wy1, wy2, show_existing_dashed=True)

    # Zone background tints
    pb.rect(-200, 383, 660, 400, fill="#fffbeb", opacity=0.85)
    pb.rect(30, 783, 440, 353, fill="#fefce8", opacity=0.75)
    pb.rect(-196, 387, 586, 330, fill="none", stroke="#059669", sw=3.2, dash="12,8")
    pb.rect(-196, 717, 318, 62, fill="none", stroke="#059669", sw=2.5, dash="8,6")
    pb.rect(30, 250, 220, 127, fill="#eff6ff", opacity=0.85)  # innebod / vask
    pb.rect(256, 30, 210, 220, fill="#f8fafc", opacity=0.9)  # hall
    pb.rect(256, 250, 210, 133, fill="#f8fafc", opacity=0.7)  # gang
    # East rooms
    pb.rect(470, 30, 366, 345, fill="#f0fdf4", opacity=0.75)  # master
    pb.rect(470, 385, 366, 200, fill="#eff6ff", opacity=0.85)  # bad
    pb.rect(470, 597, 366, 258, fill="#f0fdf4", opacity=0.75)  # sov 2
    pb.rect(470, 867, 366, 269, fill="#f0fdf4", opacity=0.75)  # sov 3

    # Interior walls
    pb.wall_v(256, 30, 383, 12)
    pb.wall_h(30, 256, 248, 12)
    pb.wall_h(30, 256, 380, 14)
    pb.wall_h(256, 464, 248, 12)  # hall / 2-mannsbolig partition
    pb.wall_v(464, 30, 1136, 12)
    pb.wall_h(464, 836, 381, 12)
    pb.wall_h(464, 836, 591, 12)
    pb.wall_h(464, 836, 861, 12)
    pb.line(170, 383, 170, 720, stroke="#94a3b8", sw=2.5, dash="8,8")
    pb.line(230, 756, 464, 756, stroke="#94a3b8", sw=2.5, dash="8,8")

    # Doors
    pb.door(256, 130, 85, "v_down_right", wall_t=12)
    pb.door(310, 248, 90, "h_right_down", wall_t=12)  # 2-mannsbolig door
    pb.door(256, 275, 80, "v_down_left", wall_t=12)  # Bod
    pb.door(464, 275, 85, "v_down_right", wall_t=12)  # Master
    pb.door(464, 445, 80, "v_down_right", wall_t=12)  # Bad
    pb.door(464, 625, 85, "v_down_right", wall_t=12)  # Sov 2
    pb.door(464, 895, 85, "v_down_right", wall_t=12)  # Sov 3

    # Windows
    pb.window_v(-215, 435, 735, 30)
    pb.window_h(-165, -45, 798, 30)
    pb.window_h(-165, -45, 368, 30)
    pb.window_h(100, 300, 1151, 30)
    pb.window_v(15, 900, 1050, 30)
    pb.window_v(851, 130, 280, 30)
    pb.window_v(851, 435, 540, 30)
    pb.window_v(851, 665, 795, 30)
    pb.window_v(851, 935, 1065, 30)
    pb.window_h(310, 415, 15, 30)
    pb.window_v(15, 85, 190, 30)

    # Fixtures & furniture
    pb.stairs_u(36, 36, 212, 206)
    pb.washer_dryer(40, 262, count=1, vertical=False)
    pb.rect(40, 326, 60, 42, fill="#f1f5f9", stroke="#64748b", sw=1.5)
    pb.double_bed(646, 55, 180, 200, head="right")
    pb.wardrobe(474, 36, 58, 225)
    pb.shower(734, 393, 94, 94)
    pb.sink(575, 393, 120, 46)
    pb.wc(485, 393, rot=0)
    pb.wardrobe(620, 535, 206, 44)
    pb.single_bed(626, 610, 200, 105, head="right")
    pb.desk(680, 785, 140, 58)
    pb.wardrobe(474, 735, 55, 115)
    pb.single_bed(626, 880, 200, 105, head="right")
    pb.desk(680, 1060, 140, 58)
    pb.rect(774, 872, 56, 255, fill="none", stroke="#d97706", sw=2, dash="7,5")
    # Living 2. etg
    pb.tv_bench(38, 388, 200, 42)
    pb.sofa_l(-180, 540, w_horiz=285, h_vert=220, depth=92, corner="bl")
    pb.coffee_table(-55, 530, 135, 75)
    pb.dining_table(235, 975, 200, 95, seats=6)
    pb.chimney_and_fireplace(135, 720, 95, 55, label_side="right")

    # Labels
    pb.room_label(142, 135, "Trapp", "4,7 m²")
    pb.room_label(162, 315, "Bod / Vask", "2,7 m²")
    pb.room_label(362, 100, "Hall", "4,4 m²", "(2-mannsbolig)")
    pb.room_label(680, 305, "Hovedsoverom", "12,4 m²")
    pb.room_label(610, 480, "Bad", "7,2 m²", "(rør over 1. etg)")
    pb.room_label(595, 745, "Soverom 2", "9,2 m²")
    pb.room_label(595, 1015, "Soverom 3", "9,7 m²", "(el. kjøkken utleie)")
    pb.text(90, 468, "LOFTSTUE / HAGESTUE 23,6 m²", size=20, weight="800", fill="#047857")
    pb.text(90, 494, "(4,00 × 5,90 m + 12,8 m² sørvest)", size=16, weight="700", fill="#059669")

    # Dimensions
    pb.dim_h(0, 866, -55, "8,66 m", bold=True)
    pb.dim_h(-230, 0, -55, "2,30 m (innbygd 2. etg)", color="#059669", bold=True)
    pb.dim_v(925, 30, 381, "3,5 m", text_offset=24)
    pb.dim_v(925, 381, 591, "2,1 m", text_offset=24)
    pb.dim_v(925, 591, 861, "2,7 m", text_offset=24)
    pb.dim_v(925, 861, 1136, "2,8 m", text_offset=24)


def make_sheet(filename: str, title: str, subtitle: str, accent: str, fn1, fn2, highlights: list[str]):
    W, H = 3100, 1730
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
        # Header banner
        f'<rect x="0" y="0" width="{W}" height="150" fill="#0f172a"/>',
        f'<rect x="0" y="144" width="{W}" height="6" fill="{accent}"/>',
        f'<text x="70" y="68" font-size="40" font-weight="800" fill="#ffffff">{esc(title)}</text>',
        f'<text x="70" y="114" font-size="24" font-weight="500" fill="#cbd5e1">{esc(subtitle)}</text>',
        # North arrow in header right
        f'<g transform="translate({W - 140}, 75)">',
        '  <circle cx="0" cy="0" r="44" fill="none" stroke="#94a3b8" stroke-width="2.5"/>',
        '  <polygon points="0,-34 -14,14 0,4 14,14" fill="#f8fafc"/>',
        '  <text x="0" y="34" font-size="20" font-weight="800" fill="#38bdf8" text-anchor="middle">N</text>',
        "</g>",
        # Floor titles
        f'<text x="780" y="215" font-size="30" font-weight="800" fill="#0f172a" text-anchor="middle">1. ETASJE (Hovedetasje)</text>',
        f'<text x="2280" y="215" font-size="30" font-weight="800" fill="#0f172a" text-anchor="middle">2. ETASJE (Soverom + Stue / Utleie-opsjon)</text>',
        # Divider line between floors
        f'<line x1="1540" y1="190" x2="1540" y2="1470" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="10,8"/>',
    ]

    pb1 = PlanBuilder(ox=480, oy=310)
    fn1(pb1)
    svg.extend(pb1.els)

    pb2 = PlanBuilder(ox=1980, oy=310)
    fn2(pb2)
    svg.extend(pb2.els)

    # Footer legend + key points
    fy = 1575
    svg.append(f'<rect x="50" y="{fy}" width="{W - 100}" height="125" fill="#ffffff" stroke="#cbd5e1" stroke-width="2" rx="12"/>')
    # Legend swatches
    svg.append(f'<line x1="90" y1="{fy + 38}" x2="155" y2="{fy + 38}" stroke="#ea580c" stroke-width="4" stroke-dasharray="12,8"/>')
    svg.append(f'<text x="170" y="{fy + 45}" font-size="19" font-weight="600" fill="#334155">Eksisterende vest-utbygg (2,28 × 4,07 m)</text>')
    svg.append(f'<rect x="610" y="{fy + 24}" width="32" height="24" fill="#b45309" stroke="#78350f" stroke-width="2"/>')
    svg.append(f'<text x="655" y="{fy + 45}" font-size="19" font-weight="600" fill="#334155">Original teglpipe (beholdes &amp; slankes, ~1,3 m fra hovedvegg vest)</text>')
    svg.append(f'<rect x="1340" y="{fy + 24}" width="36" height="24" fill="none" stroke="{accent}" stroke-width="3" stroke-dasharray="8,5"/>')
    svg.append(f'<text x="1390" y="{fy + 45}" font-size="19" font-weight="600" fill="#334155">Fri rektangulær stuesone</text>')
    # Scale bar
    svg.append(f'<line x1="2550" y1="{fy + 42}" x2="2750" y2="{fy + 42}" stroke="#0f172a" stroke-width="4"/>')
    svg.append(f'<line x1="2550" y1="{fy + 30}" x2="2550" y2="{fy + 54}" stroke="#0f172a" stroke-width="3"/>')
    svg.append(f'<line x1="2650" y1="{fy + 34}" x2="2650" y2="{fy + 50}" stroke="#0f172a" stroke-width="2"/>')
    svg.append(f'<line x1="2750" y1="{fy + 30}" x2="2750" y2="{fy + 54}" stroke="#0f172a" stroke-width="3"/>')
    svg.append(f'<text x="2650" y="{fy + 78}" font-size="19" font-weight="700" fill="#0f172a" text-anchor="middle">Målestokk: 2 meter (1 px = 1 cm)</text>')

    # Bullet highlights
    hx = 90
    for i, hl in enumerate(highlights):
        svg.append(f'<text x="{hx + i * 820}" y="{fy + 96}" font-size="20" font-weight="700" fill="#0f172a">• {esc(hl)}</text>')

    svg.append("</svg>")
    out_path = os.path.join(OUT_DIR, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    make_sheet(
        "plan_alt1_dypere_vest.svg",
        "M6 — ALTERNATIV 1: Dypere prefabrikkert vest-tilbygg (3,20 × 5,20 m)",
        "Uten syd-tilbygg • Beholder Vask sør for trapp (3,9 m²) • 4,25 × 4,60 m fri stue VEST for original pipe • 2-mannsbolig-deling i NV",
        "#0284c7",
        build_alt1_floor1,
        build_alt1_floor2,
        [
            "Stue ~24 m² (4,25 × 4,60 m vest for pipe)",
            "Vask (3,9 m²) + Utebod (3,1 m²) + Bod 2. etg (3,6 m²)",
            "Krever ~0,9 m nytt fundament vest + 25° tak / 1-løps pipe (#38)",
        ],
    )
    make_sheet(
        "plan_alt2_symmetrisk_vest.svg",
        "M6 — ALTERNATIV 2: Symmetrisk vest-tilbygg på eksisterende mur (2,30 × 4,60 m)",
        "Uten syd-tilbygg • 100 % symmetrisk vestfasade (3,53 | 4,60 | 3,53 m) • 4,00 × 5,90 m stue NORD for pipe • Vask/bi-inngang (5,0 m²) + Bod (2,7 m²)",
        "#059669",
        build_alt2_floor1,
        build_alt2_floor2,
        [
            "Stue 23,6 m² (4,00 × 5,90 m fritt NORD for pipe)",
            "Vask/bi-inng. (5,0 m²) i NØ + Innebod (2,7 m²) ved trapp",
            "Rett på eksist. 2,3 m mur + 0 pipekonflikt på tak (grønn linje #38)",
        ],
    )
