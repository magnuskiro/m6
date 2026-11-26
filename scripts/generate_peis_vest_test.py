#!/usr/bin/env python3
"""
Zoomed 1:50 scale test of placing a realistic fireplace insert (65 x 80 cm, e.g. Brunner / Spartherm H2O)
directly on the WEST end of the existing 95 x 55 cm east-west chimney, including a 100 cm fire-safety
radiation clearance zone, comparing three west-extension depths:
  1) 2,30 m (existing foundation, symmetric 4,60 m wide)
  2) 2,80 m (+0,50 m deeper, symmetric 4,60 m wide)
  3) 3,20 m (+0,90 m deeper, 5,20 m wide)
"""

import os

OUT_DIR = "/home/kiro/repos/m6/assets/images/drawings"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


class ZoomBuilder:
    """1 px = 1 cm. Local coords: x=0 main west outer wall, y=353..1166."""

    def __init__(self, ox: float, oy: float):
        self.ox = ox
        self.oy = oy
        self.els = []

    def p(self, x, y):
        return (self.ox + x, self.oy + y)

    def add(self, s):
        self.els.append(s)

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1, dash=None, rx=0, opacity=1.0):
        px, py = self.p(x, y)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        rxa = f' rx="{rx}"' if rx else ""
        self.add(f'<rect x="{px:.1f}" y="{py:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da}{op}{rxa}/>')

    def line(self, x1, y1, x2, y2, stroke="#2d3748", sw=2, dash=None, opacity=1.0):
        px1, py1 = self.p(x1, y1)
        px2, py2 = self.p(x2, y2)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        self.add(f'<line x1="{px1:.1f}" y1="{py1:.1f}" x2="{px2:.1f}" y2="{py2:.1f}" stroke="{stroke}" stroke-width="{sw}"{da}{op}/>')

    def poly(self, pts, fill="none", stroke="#2d3748", sw=2, dash=None, opacity=1.0):
        pts_str = " ".join(f"{self.ox + x:.1f},{self.oy + y:.1f}" for x, y in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        self.add(f'<polygon points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="miter"{da}{op}/>')

    def text(self, x, y, txt, size=20, weight="normal", fill="#1e293b", anchor="middle", rotate=0):
        px, py = self.p(x, y)
        rot = f' transform="rotate({rotate} {px:.1f} {py:.1f})"' if rotate else ""
        self.add(f'<text x="{px:.1f}" y="{py:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{rot}>{esc(txt)}</text>')

    def dim_h(self, x1, x2, y, label, color="#334155", bold=False, text_dy=-10):
        self.line(x1, y, x2, y, stroke=color, sw=2.2)
        self.line(x1, y - 12, x1, y + 12, stroke=color, sw=2.2)
        self.line(x2, y - 12, x2, y + 12, stroke=color, sw=2.2)
        self.text((x1 + x2) / 2, y + text_dy, label, size=18, weight="700" if bold else "600", fill=color)

    def dim_v(self, x, y1, y2, label, color="#334155", bold=False, text_dx=-16):
        self.line(x, y1, x, y2, stroke=color, sw=2.2)
        self.line(x - 12, y1, x + 12, y1, stroke=color, sw=2.2)
        self.line(x - 12, y2, x + 12, y2, stroke=color, sw=2.2)
        self.text(x + text_dx, (y1 + y2) / 2, label, size=18, weight="700" if bold else "600", fill=color, rotate=-90)

    def window_v(self, xc, y1, y2, wt=30):
        self.rect(xc - wt / 2, y1, wt, y2 - y1, fill="#ffffff", stroke="#334155", sw=2)
        self.line(xc - 5, y1, xc - 5, y2, stroke="#0284c7", sw=3.5)
        self.line(xc + 5, y1, xc + 5, y2, stroke="#0284c7", sw=3.5)

    def window_h(self, x1, x2, yc, wt=30):
        self.rect(x1, yc - wt / 2, x2 - x1, wt, fill="#ffffff", stroke="#334155", sw=2)
        self.line(x1, yc - 5, x2, yc - 5, stroke="#0284c7", sw=3.5)
        self.line(x1, yc + 5, x2, yc + 5, stroke="#0284c7", sw=3.5)


def draw_panel(zb: ZoomBuilder, west_d: int, wy1: int, wy2: int, title: str, badge: str, accent: str, sofa_mode: str):
    """Draw zoomed living + dining zone (x in [-west_d..480], y in [330..1166])."""
    # Panel header
    zb.text(60, 225, title, size=26, weight="800", fill="#0f172a")
    zb.rect(-180, 242, 480, 34, fill=accent, rx=17, opacity=0.14)
    zb.text(60, 265, badge, size=17, weight="700", fill=accent)

    # Outer shell of west wing + main west/south wall (cut cleanly at x=470 east & y=340 north)
    outer = [
        (0, 340),
        (470, 340),
        (470, 1166),
        (0, 1166),
        (0, wy2),
        (-west_d, wy2),
        (-west_d, wy1),
        (0, wy1),
    ]
    inner = [
        (30, 340),
        (464, 340),
        (464, 1136),
        (30, 1136),
        (30, wy2 - 30),
        (-west_d + 30, wy2 - 30),
        (-west_d + 30, wy1 + 30),
        (30, wy1 + 30),
    ]
    zb.poly(outer, fill="#334155", stroke="#0f172a", sw=2.5)
    zb.poly(inner, fill="#fffbeb", stroke="#334155", sw=2)

    # North interior wall against Vask/Bod (at y=wy1+24)
    wall_tv_y = wy1 + 24
    zb.rect(30, 340, 226, wall_tv_y - 340, fill="#eff6ff", stroke="#64748b", sw=1.5)
    zb.text(143, (340 + wall_tv_y) / 2 + 6, "Vask / Bod", size=16, weight="700", fill="#475569")
    zb.rect(30, wall_tv_y - 7, 226, 14, fill="#475569")
    # Gang north-east & Sov wall east
    zb.rect(256, 340, 208, wall_tv_y - 340, fill="#f8fafc")
    zb.rect(464, 340, 14, 420, fill="#475569")
    zb.text(360, 368, "← Gang", size=15, weight="600", fill="#64748b")

    # Existing west foundation dashed orange line (2.28m deep, y=415..822)
    zb.line(0, 415, -228, 415, stroke="#ea580c", sw=3, dash="12,8")
    zb.line(-228, 415, -228, 822, stroke="#ea580c", sw=3, dash="12,8")
    zb.line(-228, 822, 0, 822, stroke="#ea580c", sw=3, dash="12,8")

    # Windows
    zb.window_v(-west_d + 15, wy1 + 70, wy2 - 70, 30)
    zb.window_h(-west_d + 60, -45, wy2 - 15, 30)
    if wy1 < 390:
        zb.window_h(-west_d + 60, -45, wy1 + 15, 30)
    zb.window_h(100, 310, 1151, 30)
    if wy2 < 860:
        zb.window_v(15, 900, 1050, 30)

    # EXACT original chimney (95 x 55 cm east-west: x=135..230, y=720..775)
    zb.rect(135, 720, 95, 55, fill="#b45309", stroke="#78350f", sw=3)
    zb.rect(147, 732, 28, 31, fill="#fef3c7", stroke="#78350f", sw=2)
    zb.rect(189, 732, 28, 31, fill="#fef3c7", stroke="#78350f", sw=2)

    # REALISTIC fireplace insert + insulated surround DIRECTLY WEST of chimney (65 cm deep x 78 cm wide!)
    # x = 70..135, y = 709..787
    zb.rect(70, 709, 65, 78, fill="#f97316", stroke="#9a3412", sw=2.5)
    zb.rect(70, 720, 10, 56, fill="#fef08a", stroke="#9a3412", sw=1.5)  # Glass front facing west!
    zb.text(102, 753, "PEIS", size=14, weight="800", fill="#ffffff")
    zb.text(182, 704, "Orig. pipe 95×55", size=14, weight="700", fill="#9a3412")
    zb.text(102, 806, "Innsats 65×78", size=13, weight="700", fill="#c2410c")

    # 100 cm MANDATORY FIRE SAFETY / RADIATION ZONE west of fireplace glass (x = -30..70, y = 685..810)
    zb.rect(-30, 685, 100, 125, fill="#ef4444", opacity=0.14, stroke="#dc2626", sw=2.2, dash="8,5")
    zb.text(20, 738, "100 cm", size=15, weight="800", fill="#dc2626")
    zb.text(20, 758, "brannsone", size=13, weight="700", fill="#dc2626")

    # 30 cm non-combustible hearth plate
    zb.rect(40, 700, 30, 96, fill="#cbd5e1", opacity=0.55, stroke="#64748b", sw=1.2)

    # TV bench on north wall
    tv_x = -west_d + 130 if west_d >= 280 else 40
    zb.rect(tv_x, wall_tv_y + 10, 190, 40, fill="#334155", stroke="#0f172a", sw=2, rx=3)
    zb.line(tv_x + 25, wall_tv_y + 18, tv_x + 165, wall_tv_y + 18, stroke="#38bdf8", sw=4)
    zb.text(tv_x + 95, wall_tv_y + 39, "TV-VEGG", size=13, weight="700", fill="#f8fafc")

    # Sofa placement tailored to each depth
    west_in = -west_d + 30
    if sofa_mode == "230":
        # Straight 3-seater (235x92) along west wall + chaise on NORTH end (keeps south clear of 100cm fire zone!)
        sx = west_in + 14
        sy = 465
        zb.rect(sx, sy, 92, 260, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)
        zb.rect(sx, sy, 165, 92, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)  # sjeselong i nord!
        zb.rect(sx + 4, sy + 4, 22, 252, fill="#bae6fd", stroke="#0369a1", sw=1.2, rx=3)
        # Coffee table + armchair north-east
        zb.rect(sx + 118, 575, 75, 92, fill="#ffffff", stroke="#0369a1", sw=1.8, rx=8)
        zb.rect(255, 520, 80, 80, fill="#e0f2fe", stroke="#0369a1", sw=2, rx=8)
        zb.rect(255, 615, 80, 80, fill="#e0f2fe", stroke="#0369a1", sw=2, rx=8)
        # Ghost outline showing why a 260cm south-arm L-sofa collides with fire zone!
        zb.rect(sx, 675, 255, 92, fill="none", stroke="#dc2626", sw=2.2, dash="6,4")
        zb.text(sx + 128, 728, "✗ 2,6m L-sofa treffer", size=12, weight="800", fill="#dc2626")
        zb.text(sx + 128, 744, "100cm brannsone!", size=12, weight="800", fill="#dc2626")
        zb.text(115, 452, "Kun 1,70 m vest for 100cm-sone", size=15, weight="700", fill="#b45309")
    elif sofa_mode == "280":
        # Clean 2,20 m L-sofa fits clear of 100cm fire zone!
        sx = west_in + 14
        sy = 545
        zb.rect(sx, sy, 92, 220, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)
        zb.rect(sx, sy + 220 - 92, 210, 92, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)
        zb.rect(sx + 4, sy + 4, 22, 212, fill="#bae6fd", stroke="#0369a1", sw=1.2, rx=3)
        zb.rect(sx + 4, sy + 220 - 26, 202, 22, fill="#bae6fd", stroke="#0369a1", sw=1.2, rx=3)
        zb.rect(sx + 112, 540, 120, 72, fill="#ffffff", stroke="#0369a1", sw=1.8, rx=8)
        zb.rect(255, 535, 80, 80, fill="#e0f2fe", stroke="#0369a1", sw=2, rx=8)
        zb.text(45, 490, "2,20 m fritt vest for 100cm-sone", size=15, weight="700", fill="#059669")
        zb.text(45, 510, "✓ 2,1–2,2 m L-sofa går klar!", size=14, weight="700", fill="#059669")
    elif sofa_mode == "320":
        # Generous 2,60 m L-sofa fits completely clear of 100cm fire zone!
        sx = west_in + 16
        sy = 640
        zb.rect(sx, sy, 92, 235, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)
        zb.rect(sx, sy + 235 - 92, 250, 92, fill="#e0f2fe", stroke="#0369a1", sw=2.2, rx=6)
        zb.rect(sx + 4, sy + 4, 22, 227, fill="#bae6fd", stroke="#0369a1", sw=1.2, rx=3)
        zb.rect(sx + 4, sy + 235 - 26, 242, 22, fill="#bae6fd", stroke="#0369a1", sw=1.2, rx=3)
        zb.rect(sx + 115, 620, 130, 75, fill="#ffffff", stroke="#0369a1", sw=1.8, rx=8)
        zb.rect(10, 560, 80, 80, fill="#e0f2fe", stroke="#0369a1", sw=2, rx=8)
        zb.text(-35, 530, "2,60 m fritt vest for 100cm-sone", size=15, weight="700", fill="#0284c7")
        zb.text(-35, 550, "✓ Full 2,5–2,6 m L-sofa + luft!", size=14, weight="700", fill="#0284c7")

    # Dining table in south-west
    dx, dy = 235, 990 if wy2 < 860 else 1015
    zb.rect(dx - 120, dy - 50, 240, 100, fill="#fefce8", stroke="#a16207", sw=2.2, rx=4)
    zb.text(dx, dy + 6, "Spisebord (8 pers)", size=16, weight="600", fill="#854d0e")

    # KEY DIMENSION CHAINS (the whole point of this test!)
    # 1) Total interior distance from west inner wall to fireplace glass (x = 70)
    dist_glass = (70 - west_in) / 100.0
    dist_safe = (-30 - west_in) / 100.0
    zb.dim_h(west_in, 70, wy2 + 48, f"{dist_glass:.2f} m → glass", color="#0f172a", bold=True, text_dy=24)
    zb.dim_h(west_in, -30, wy2 + 102, f"{dist_safe:.2f} m (fri sone)", color=accent, bold=True, text_dy=24)
    # 2) Outer depth of west extension
    zb.dim_h(-west_d, 0, 305, f"{west_d/100:.2f} m utvendig", color=accent, bold=True, text_dy=-10)
    # 3) Passage east of chimney (x=230..464)
    zb.dim_h(230, 464, 845, "2,34 m passasje øst", color="#475569", bold=False, text_dy=-10)


def main():
    W, H = 2920, 1340
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        "<defs>",
        '  <pattern id="g50" width="50" height="50" patternUnits="userSpaceOnUse">',
        '    <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#eceae4" stroke-width="1"/>',
        "  </pattern>",
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="#faf9f6"/>',
        f'<rect width="{W}" height="{H}" fill="url(#g50)"/>',
        # Header
        f'<rect x="0" y="0" width="{W}" height="130" fill="#0f172a"/>',
        f'<rect x="0" y="124" width="{W}" height="6" fill="#ea580c"/>',
        f'<text x="60" y="58" font-size="36" font-weight="800" fill="#ffffff">M6 (#50 / #38) — Peistest: Peisinnsats RETT VEST på original pipe (95×55 cm)</text>',
        f'<text x="60" y="98" font-size="21" font-weight="500" fill="#cbd5e1">Realistisk innsats + kasse (65 × 78 cm, f.eks. Brunner/Spartherm H2O) + 100 cm brannsikkerhetsavstand foran glass — testet mot 2,30 m, 2,80 m og 3,20 m vest-dybde</text>',
        # Dividers
        f'<line x1="940" y1="160" x2="940" y2="1220" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="10,8"/>',
        f'<line x1="1910" y1="160" x2="1910" y2="1220" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="10,8"/>',
    ]

    z1 = ZoomBuilder(ox=370, oy=-20)
    draw_panel(z1, 230, 353, 813, "1. Dybde 2,30 m (eksist. mur)", "Symmetrisk 4,60 m • 0 ny grunnmur • Stram L-sofa", "#d97706", "230")
    svg.extend(z1.els)

    z2 = ZoomBuilder(ox=1370, oy=-20)
    draw_panel(z2, 280, 353, 813, "2. Dybde 2,80 m (+50 cm vest)", "Symmetrisk 4,60 m • 2,2m L-sofa går klar!", "#059669", "280")
    svg.extend(z2.els)

    z3 = ZoomBuilder(ox=2380, oy=-20)
    draw_panel(z3, 320, 410, 930, "3. Dybde 3,20 m (+90 cm vest)", "Bredde 5,20 m • God plass til 2,6m L-sofa", "#0284c7", "320")
    svg.extend(z3.els)

    # Footer
    fy = 1235
    svg.append(f'<rect x="50" y="{fy}" width="{W - 100}" height="78" fill="#ffffff" stroke="#cbd5e1" stroke-width="2" rx="10"/>')
    svg.append(f'<text x="85" y="{fy + 33}" font-size="19" font-weight="700" fill="#0f172a">Konklusjon ved peis RETT VEST på original pipe (x=70 cm frontglass):</text>')
    svg.append(f'<text x="85" y="{fy + 60}" font-size="18" font-weight="500" fill="#334155">• 2,30 m funker KUN med rett 3-seter/sjeselong i nord (ikke L-sofa mot sør)   • 2,80 m (+50 cm, fortsatt symmetrisk 4,60 m!) gir 2,20 m fritt vest for brannsone   • 3,20 m gir full 2,60 m L-sofa</text>')
    svg.append("</svg>")

    out = os.path.join(OUT_DIR, "test_peis_vest_sammenligning.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
