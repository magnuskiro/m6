#!/usr/bin/env python3
"""
Exact 3D mathematical perspective projection (pinhole camera, ArchiCAD/BIMx architectural style)
of Myrteveien 6 from Southwest 3/4 view, comparing TRUE to-scale 3D proportions of:
  - Left:  Alternativ 1 — 3,30 m deep x 5,20 m wide west cross-wing (20° gable)
  - Right: Alternativ 2B — 2,80 m deep x 4,60 m wide symmetric west cross-wing (24° gable)

Zero AI proportion distortion — every millimeter is projected from exact 3D coordinates!
Coordinate system (cm, right-handed):
  X: West -> East  (0 = main west outer wall, 866 = main east outer wall, negative = west wing)
  Y: South -> North (0 = main south outer wall, 1166 = main north outer wall, >1166 = north ext)
  Z: Up from ground C+26.4 (40 = plinth, 320 = 2nd floor, 610 = eaves, 888 = main ridge)
"""

import math
import os

OUT_DIR = "/home/kiro/repos/m6/assets/images/drawings"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def v_norm(a):
    l = math.sqrt(v_dot(a, a))
    return (a[0] / l, a[1] / l, a[2] / l) if l > 1e-9 else (0, 0, 0)


class Camera3D:
    def __init__(self, pos, target, fov_deg=34.0, cx=650.0, cy=520.0, width=1300.0):
        self.pos = pos
        self.fwd = v_norm(v_sub(target, pos))
        world_up = (0.0, 0.0, 1.0)
        self.right = v_norm(v_cross(self.fwd, world_up))
        self.up = v_cross(self.right, self.fwd)
        self.f = (width / 2.0) / math.tan(math.radians(fov_deg / 2.0))
        self.cx = cx
        self.cy = cy

    def project(self, pt):
        d = v_sub(pt, self.pos)
        zc = v_dot(d, self.fwd)
        if zc < 10.0:
            zc = 10.0
        xc = v_dot(d, self.right)
        yc = v_dot(d, self.up)
        sx = self.cx + (xc / zc) * self.f
        sy = self.cy - (yc / zc) * self.f
        return (sx, sy, zc)


class Scene3D:
    def __init__(self, cam: Camera3D):
        self.cam = cam
        self.items = []  # (layer, depth, svg_str)
        # Warm late-afternoon sun from WSW
        self.sun = v_norm((-0.78, -0.45, 0.43))

    def shade_color(self, hex_col, normal, ambient=0.62):
        n = v_norm(normal)
        ndotl = max(0.0, v_dot(n, self.sun))
        fac = ambient + (1.0 - ambient) * ndotl
        r = int(hex_col[1:3], 16)
        g = int(hex_col[3:5], 16)
        b = int(hex_col[5:7], 16)
        r = min(255, max(0, int(r * fac)))
        g = min(255, max(0, int(g * fac)))
        b = min(255, max(0, int(b * fac)))
        return f"#{r:02x}{g:02x}{b:02x}"

    def add_poly(self, pts3d, fill_hex, stroke="#1e293b", sw=1.4, layer=1, auto_shade=True, ambient=0.68, opacity=1.0, depth_bias=0.0):
        proj = [self.cam.project(p) for p in pts3d]
        # Backface culling if auto_shade
        e1 = v_sub(pts3d[1], pts3d[0])
        e2 = v_sub(pts3d[2], pts3d[0])
        normal = v_cross(e1, e2)
        view_vec = v_sub(self.cam.pos, pts3d[0])
        if v_dot(normal, view_vec) < 0:
            normal = (-normal[0], -normal[1], -normal[2])
        fill = self.shade_color(fill_hex, normal, ambient) if auto_shade else fill_hex
        avg_z = sum(p[2] for p in proj) / len(proj) + depth_bias
        pstr = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in proj)
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        s = f'<polygon points="{pstr}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{op}/>'
        self.items.append((layer, avg_z, s))

    def add_line(self, p1, p2, stroke="#1e293b", sw=1.5, dash=None, layer=2, depth_bias=-5.0, opacity=1.0):
        a = self.cam.project(p1)
        b = self.cam.project(p2)
        avg_z = (a[2] + b[2]) / 2.0 + depth_bias
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1.0 else ""
        s = f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{stroke}" stroke-width="{sw}"{da}{op}/>'
        self.items.append((layer, avg_z, s))

    def add_text_at(self, pt3d, text, dx=0, dy=0, size=16, weight="700", fill="#0f172a", anchor="middle"):
        sx, sy, _ = self.cam.project(pt3d)
        s = f'<text x="{sx + dx:.1f}" y="{sy + dy:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(text)}</text>'
        self.items.append((10, 0.0, s))

    def add_kors_window_west(self, x_wall, y1, y2, z1, z2, single=False, layer=3):
        """4-pane Norwegian kors-sprosse window on a west-facing wall (x = x_wall)."""
        x_out = x_wall - 1.5
        # Outer white frame
        self.add_poly([(x_out, y1 - 6, z1 - 6), (x_out, y2 + 6, z1 - 6), (x_out, y2 + 6, z2 + 6), (x_out, y1 - 6, z2 + 6)],
                      "#ffffff", stroke="#475569", sw=1.0, layer=layer, auto_shade=False, depth_bias=-4.0)
        # Glass
        self.add_poly([(x_out - 0.5, y1, z1), (x_out - 0.5, y2, z1), (x_out - 0.5, y2, z2), (x_out - 0.5, y1, z2)],
                      "#64748b", stroke="#1e293b", sw=1.3, layer=layer, auto_shade=False, depth_bias=-6.0)
        # Subtle sky reflection tint on upper half
        zm = z1 + (z2 - z1) * 0.66
        self.add_poly([(x_out - 0.8, y1 + 2, zm), (x_out - 0.8, y2 - 2, zm), (x_out - 0.8, y2 - 2, z2 - 2), (x_out - 0.8, y1 + 2, z2 - 2)],
                      "#93c5fd", stroke="none", sw=0, layer=layer, auto_shade=False, opacity=0.45, depth_bias=-7.0)
        # Kors-sprosser (horizontal at 66% up = 34% down from top; vertical at center)
        self.add_line((x_out - 1.2, y1, zm), (x_out - 1.2, y2, zm), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)
        if not single:
            ym = (y1 + y2) / 2.0
            self.add_line((x_out - 1.2, ym, z1), (x_out - 1.2, ym, z2), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)

    def add_kors_window_south(self, y_wall, x1, x2, z1, z2, single=False, is_door=False, layer=3):
        """4-pane Norwegian kors-sprosse window or French terrace door on a south-facing wall (y = y_wall)."""
        y_out = y_wall - 1.5
        self.add_poly([(x1 - 6, y_out, z1 - 6), (x2 + 6, y_out, z1 - 6), (x2 + 6, y_out, z2 + 6), (x1 - 6, y_out, z2 + 6)],
                      "#ffffff", stroke="#475569", sw=1.0, layer=layer, auto_shade=False, depth_bias=-4.0)
        self.add_poly([(x1, y_out - 0.5, z1), (x2, y_out - 0.5, z1), (x2, y_out - 0.5, z2), (x1, y_out - 0.5, z2)],
                      "#475569", stroke="#1e293b", sw=1.3, layer=layer, auto_shade=False, depth_bias=-6.0)
        if is_door:
            # Solid bottom door panel
            self.add_poly([(x1 + 2, y_out - 0.9, z1 + 2), (x2 - 2, y_out - 0.9, z1 + 2), (x2 - 2, y_out - 0.9, z1 + 52), (x1 + 2, y_out - 0.9, z1 + 52)],
                          "#f8fafc", stroke="#64748b", sw=0.8, layer=layer, auto_shade=False, depth_bias=-8.0)
            zm = z2 - 50
        else:
            zm = z1 + (z2 - z1) * 0.66
        self.add_poly([(x1 + 2, y_out - 0.8, zm), (x2 - 2, y_out - 0.8, zm), (x2 - 2, y_out - 0.8, z2 - 2), (x1 + 2, y_out - 0.8, z2 - 2)],
                      "#bae6fd", stroke="none", sw=0, layer=layer, auto_shade=False, opacity=0.4, depth_bias=-7.0)
        self.add_line((x1, y_out - 1.2, zm), (x2, y_out - 1.2, zm), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)
        if not single:
            xm = (x1 + x2) / 2.0
            self.add_line((xm, y_out - 1.2, z1), (xm, y_out - 1.2, z2), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)

    def add_siding_west(self, x_wall, y1, y2, z1, z2, step=28, layer=2):
        z = z1 + step
        while z < z2 - 8:
            self.add_line((x_wall - 0.5, y1, z), (x_wall - 0.5, y2, z), stroke="#cbd5e1", sw=0.65, layer=layer, depth_bias=-2.0, opacity=0.65)
            z += step

    def add_siding_south(self, y_wall, x1, x2, z1, z2, step=28, layer=2):
        z = z1 + step
        while z < z2 - 8:
            self.add_line((x1, y_wall - 0.5, z), (x2, y_wall - 0.5, z), stroke="#cbd5e1", sw=0.65, layer=layer, depth_bias=-2.0, opacity=0.65)
            z += step

    def add_south_balcony(self, x1=243.0, x2=623.0, depth=215.0, z_floor=322.0, slab_t=20.0, rail_h=102.0, layer=5, columns=True):
        """Modern 2nd-floor south balcony (3,80 x 2,15 m = 8,2 m²) on 2 slim white timber columns down to south deck."""
        y0, y1 = 0.0, -depth
        z0 = z_floor - slab_t
        zr = z_floor + rail_h
        # 2 slim white timber columns down to south timber deck (Z=22..z0) at front corners!
        if columns:
            cw = 14.0
            for cx_a in [x1 + 6.0, x2 - 6.0 - cw]:
                cx_b = cx_a + cw
                cy_a, cy_b = y1 + 6.0, y1 + 6.0 + cw
                self.add_poly([(cx_a, cy_a, 22), (cx_b, cy_a, 22), (cx_b, cy_a, z0), (cx_a, cy_a, z0)], "#ffffff", stroke="#334155", sw=1.2, layer=layer)
                self.add_poly([(cx_a, cy_a, 22), (cx_a, cy_b, 22), (cx_a, cy_b, z0), (cx_a, cy_a, z0)], "#e2e8f0", stroke="#334155", sw=1.1, layer=layer)
                self.add_poly([(cx_b, cy_a, 22), (cx_b, cy_b, 22), (cx_b, cy_b, z0), (cx_b, cy_a, z0)], "#e2e8f0", stroke="#334155", sw=1.1, layer=layer)
        # Underside soffit + warm timber deck top
        self.add_poly([(x1, y1, z0), (x2, y1, z0), (x2, y0, z0), (x1, y0, z0)], "#cbd5e1", stroke="#475569", sw=1.1, layer=layer)
        self.add_poly([(x1, y1, z_floor), (x2, y1, z_floor), (x2, y0, z_floor), (x1, y0, z_floor)], "#d6b084", stroke="#78350f", sw=1.1, layer=layer, ambient=0.78)
        # Clean white fascia edges (south, west, east)
        self.add_poly([(x1, y1, z0), (x2, y1, z0), (x2, y1, z_floor), (x1, y1, z_floor)], "#ffffff", stroke="#1e293b", sw=1.5, layer=layer)
        self.add_poly([(x1, y1, z0), (x1, y0, z0), (x1, y0, z_floor), (x1, y1, z_floor)], "#f1f5f9", stroke="#1e293b", sw=1.4, layer=layer)
        self.add_poly([(x2, y1, z0), (x2, y0, z0), (x2, y0, z_floor), (x2, y1, z_floor)], "#f1f5f9", stroke="#1e293b", sw=1.4, layer=layer)
        # Sleek matte-black vertical metal balustrade railing (TEK17 height ~102 cm) along west, south, east edges
        for z_bar, sw_bar in [(zr, 2.6), (z_floor + 8.0, 1.8)]:
            self.add_line((x1 + 4, y0, z_bar), (x1 + 4, y1 + 4, z_bar), stroke="#0f172a", sw=sw_bar, layer=layer + 1)
            self.add_line((x1 + 4, y1 + 4, z_bar), (x2 - 4, y1 + 4, z_bar), stroke="#0f172a", sw=sw_bar, layer=layer + 1)
            self.add_line((x2 - 4, y1 + 4, z_bar), (x2 - 4, y0, z_bar), stroke="#0f172a", sw=sw_bar, layer=layer + 1)
        for px, py in [(x1 + 4, y1 + 4), (x2 - 4, y1 + 4), (x1 + 4, y0 - 2), (x2 - 4, y0 - 2)]:
            self.add_line((px, py, z_floor), (px, py, zr), stroke="#0f172a", sw=2.4, layer=layer + 1)
        rx = x1 + 24.0
        while rx < x2 - 12.0:
            self.add_line((rx, y1 + 4, z_floor + 8.0), (rx, y1 + 4, zr), stroke="#1e293b", sw=1.2, layer=layer + 1)
            rx += 22.0
        ry = y1 + 24.0
        while ry < y0 - 10.0:
            self.add_line((x1 + 4, ry, z_floor + 8.0), (x1 + 4, ry, zr), stroke="#1e293b", sw=1.1, layer=layer + 1)
            self.add_line((x2 - 4, ry, z_floor + 8.0), (x2 - 4, ry, zr), stroke="#1e293b", sw=1.1, layer=layer + 1)
            ry += 22.0

    def render(self):
        # Sort by (layer ascending, depth descending = painter's algorithm)
        self.items.sort(key=lambda item: (item[0], -item[1]))
        return [s for _, _, s in self.items]


def build_house_3d(cam: Camera3D, west_d: float, y_s: float, y_n: float, wing_deg: float, label_wing: str, balcony=(243.0, 623.0, 215.0, True)):
    """Build exact 3D geometry of Myrteveien 6 from SW 3/4 view."""
    sc = Scene3D(cam)
    t_main = math.tan(math.radians(32.7))
    z_eaves = 610.0
    z_ridge = z_eaves + 433.0 * t_main  # 888 cm

    # Ground lawn plane & south timber terrace
    sc.add_poly([(-700, -500, 0), (1300, -500, 0), (1300, 1800, 0), (-700, 1800, 0)],
                "#bbf7d0", stroke="none", sw=0, layer=0, auto_shade=False)
    # Gravel driveway north-west
    sc.add_poly([(-700, 1180, 1), (1050, 1180, 1), (1050, 1750, 1), (-700, 1750, 1)],
                "#d6d3d1", stroke="#a8a29e", sw=1, layer=0, auto_shade=False)
    # South timber terrace deck (Z = 22) along main south gable (centered veranda door)
    sc.add_poly([(0, -240, 22), (910, -240, 22), (910, 0, 22), (0, 0, 22)],
                "#d6b084", stroke="#92400e", sw=1.3, layer=1, auto_shade=True, ambient=0.75)
    sc.add_poly([(0, -240, 0), (910, -240, 0), (910, -240, 22), (0, -240, 22)],
                "#a88358", stroke="#78350f", sw=1.1, layer=1, auto_shade=True)
    sc.add_poly([(0, -240, 0), (0, 0, 0), (0, 0, 22), (0, -240, 22)],
                "#b48f64", stroke="#78350f", sw=1.1, layer=1, auto_shade=True)

    # --- 1-STORY NORTH EXTENSION (Y=1166..1376, X=0..866, saltak facing north) ---
    # West side of north extension (covered portico X=0..250, enclosed from X=250..866)
    sc.add_poly([(0, 1166, 0), (0, 1376, 0), (0, 1376, 40), (0, 1166, 40)], "#64748b", layer=1)
    sc.add_poly([(250, 1166, 40), (250, 1376, 40), (250, 1376, 290), (250, 1166, 290)], "#f8fafc", layer=1)
    # Corner column at (8, 1368)
    sc.add_poly([(0, 1358, 40), (16, 1358, 40), (16, 1358, 290), (0, 1358, 290)], "#ffffff", layer=1)
    sc.add_poly([(0, 1358, 40), (0, 1374, 40), (0, 1374, 290), (0, 1358, 290)], "#f1f5f9", layer=1)
    # West slope of north-extension saltak (eaves Z=285 at X=-15, ridge Z=405 at X=433)
    sc.add_poly([(-18, 1166, 285), (-18, 1392, 285), (433, 1392, 405), (433, 1166, 405)], "#334155", stroke="#0f172a", sw=1.6, layer=2)

    # --- MAIN HOUSE WALLS (X=0..866, Y=0..1166) ---
    # Main West Wall (split visually into north of wing, south of wing — or one clean plane behind wing!)
    sc.add_poly([(0, 0, 0), (0, 1166, 0), (0, 1166, 40), (0, 0, 40)], "#64748b", stroke="#334155", sw=1.2, layer=1)
    sc.add_poly([(0, 0, 40), (0, 1166, 40), (0, 1166, z_eaves), (0, 0, z_eaves)], "#ffffff", stroke="#334155", sw=1.6, layer=1)
    sc.add_siding_west(0, 0, y_s, 40, z_eaves, layer=1)
    sc.add_siding_west(0, y_n, 1166, 40, z_eaves, layer=1)

    # Main South Gable Wall (Y=0, X=0..866)
    sc.add_poly([(0, 0, 0), (866, 0, 0), (866, 0, 40), (0, 0, 40)], "#64748b", stroke="#334155", sw=1.2, layer=1)
    sc.add_poly([(0, 0, 40), (866, 0, 40), (866, 0, z_eaves), (433, 0, z_ridge), (0, 0, z_eaves)], "#ffffff", stroke="#334155", sw=1.8, layer=1)
    sc.add_siding_south(0, 0, 866, 40, z_eaves, layer=1)

    # Main wall windows (exact room alignment!)
    # South-west recessed main wall (Y in [0..y_s]): Dining 1st & 2nd
    ym_sw = y_s / 2.0
    sc.add_kors_window_west(0, ym_sw - 58, ym_sw + 58, 105, 250, layer=2)
    sc.add_kors_window_west(0, ym_sw - 58, ym_sw + 58, 385, 530, layer=2)
    # North-west recessed main wall (Y in [y_n..1166]): Stairwell + Vask/Bod
    sc.add_kors_window_west(0, 965, 1070, 105, 245, layer=2)  # Stair 1st
    sc.add_kors_window_west(0, 965, 1070, 385, 525, layer=2)  # Stair 2nd
    if 1166 - y_n > 370:
        sc.add_kors_window_west(0, 805, 875, 115, 245, single=True, layer=2)  # Vask 1st
        sc.add_kors_window_west(0, 805, 875, 395, 525, single=True, layer=2)  # Bod 2nd

    # Main South Gable — 100% SYMMETRIC around EXISTING centered veranda doors (x=353..513 in BOTH 1st & 2nd floor!)
    sc.add_kors_window_south(0, 105, 235, 105, 250, layer=2)                # Dining 1st (left)
    sc.add_kors_window_south(0, 353, 513, 42, 252, is_door=True, layer=2)   # EXISTING centered veranda door 1st!
    sc.add_kors_window_south(0, 631, 761, 105, 250, layer=2)                # Kitchen 1st (right)
    sc.add_kors_window_south(0, 105, 235, 385, 530, layer=2)                # Opphold 2nd (left)
    sc.add_kors_window_south(0, 353, 513, 322, 532, is_door=True, layer=2)  # EXISTING centered veranda door 2nd!
    bx1, bx2, bdepth, bcols = balcony
    sc.add_south_balcony(bx1, bx2, depth=bdepth, z_floor=322.0, layer=4, columns=bcols)
    sc.add_kors_window_south(0, 631, 761, 385, 530, layer=2)                # Sov 3 2nd (right, 3.1m wide)
    sc.add_kors_window_south(0, 375, 491, 655, 770, layer=2)                # Loft gable (centered!)

    # --- MAIN WEST ROOF SLOPE (with 35 cm overhang) ---
    ov_x = -35.0
    z_ov = z_eaves + ov_x * t_main
    sc.add_poly([(ov_x, -35, z_ov), (ov_x, 1201, z_ov), (433, 1201, z_ridge), (433, -35, z_ridge)],
                "#334155", stroke="#0f172a", sw=2.0, layer=3, ambient=0.58)
    # Roof course lines
    for frac in [0.15, 0.30, 0.45, 0.60, 0.75, 0.90]:
        rx = ov_x + (433 - ov_x) * frac
        rz = z_ov + (z_ridge - z_ov) * frac + 0.8
        sc.add_line((rx, -32, rz), (rx, 1198, rz), stroke="#475569", sw=0.8, layer=3, depth_bias=-1.0, opacity=0.6)
    # Roof fascia on south gable
    sc.add_poly([(ov_x, -35, z_ov), (433, -35, z_ridge), (433, -35, z_ridge + 16), (ov_x, -35, z_ov + 16)],
                "#ffffff", stroke="#1e293b", sw=1.2, layer=4)
    sc.add_poly([(433, -35, z_ridge), (866 + 35, -35, z_ov), (866 + 35, -35, z_ov + 16), (433, -35, z_ridge + 16)],
                "#e2e8f0", stroke="#1e293b", sw=1.2, layer=4)
    # 2 flush skylights on west slope
    for sy1, sy2 in [(90, 200), (945, 1055)]:
        x_a, x_b = 225.0, 345.0
        z_a = z_eaves + x_a * t_main + 3.0
        z_b = z_eaves + x_b * t_main + 3.0
        sc.add_poly([(x_a, sy1, z_a), (x_a, sy2, z_a), (x_b, sy2, z_b), (x_b, sy1, z_b)],
                    "#7dd3fc", stroke="#0f172a", sw=2.0, layer=4, auto_shade=False)

    # --- EXACT ORIGINAL CHIMNEY ON WEST ROOF SLOPE (X=135..230, Y=391..446, Z_top=895) ---
    cx1, cx2, cy1, cy2 = 135.0, 230.0, 391.0, 446.0
    cz_w = z_eaves + cx1 * t_main - 2.0
    cz_e = z_eaves + cx2 * t_main - 2.0
    cz_t = 895.0
    # West face of chimney
    sc.add_poly([(cx1, cy1, cz_w), (cx1, cy2, cz_w), (cx1, cy2, cz_t), (cx1, cy1, cz_t)], "#64748b", stroke="#1e293b", sw=1.6, layer=5, ambient=0.6)
    # South face of chimney (95 cm wide east-west!)
    sc.add_poly([(cx1, cy1, cz_w), (cx2, cy1, cz_e), (cx2, cy1, cz_t), (cx1, cy1, cz_t)], "#475569", stroke="#1e293b", sw=1.6, layer=5, ambient=0.55)
    # Chimney cap
    sc.add_poly([(cx1 - 5, cy1 - 5, cz_t), (cx2 + 5, cy1 - 5, cz_t), (cx2 + 5, cy2 + 5, cz_t), (cx1 - 5, cy2 + 5, cz_t)], "#334155", stroke="#0f172a", sw=1.4, layer=5)

    # --- ENCLOSED 2-STORY WEST CROSS-WING (EXACT DEPTH west_d, Y in [y_s..y_n]) ---
    y_mid = (y_s + y_n) / 2.0
    half_w = (y_n - y_s) / 2.0
    t_wing = math.tan(math.radians(wing_deg))
    z_wing_ridge = z_eaves + half_w * t_wing
    x_stop = (z_wing_ridge - z_eaves) / t_main

    # West wing plinth
    sc.add_poly([(-west_d, y_s, 0), (-west_d, y_n, 0), (-west_d, y_n, 40), (-west_d, y_s, 40)], "#64748b", stroke="#334155", sw=1.2, layer=6)
    sc.add_poly([(-west_d, y_s, 0), (0, y_s, 0), (0, y_s, 40), (-west_d, y_s, 40)], "#475569", stroke="#334155", sw=1.2, layer=6)

    # West wing WEST GABLE WALL (X = -west_d)
    sc.add_poly([(-west_d, y_s, 40), (-west_d, y_n, 40), (-west_d, y_n, z_eaves), (-west_d, y_mid, z_wing_ridge), (-west_d, y_s, z_eaves)],
                "#ffffff", stroke="#1e293b", sw=2.0, layer=6)
    sc.add_siding_west(-west_d, y_s, y_n, 40, z_eaves, layer=6)
    # West wing SOUTH SIDE WALL (Y = y_s, EXACT DEPTH west_d!)
    sc.add_poly([(-west_d, y_s, 40), (0, y_s, 40), (0, y_s, z_eaves), (-west_d, y_s, z_eaves)],
                "#f8fafc", stroke="#1e293b", sw=2.0, layer=6)
    sc.add_siding_south(y_s, -west_d, 0, 40, z_eaves, layer=6)

    # West wing windows (paired kors-sprosser on west gable + FULL double kors-sprosse on south side wall!)
    w_span = y_n - y_s
    win_w = 155.0 if w_span >= 500 else 140.0
    gap = 45.0
    sc.add_kors_window_west(-west_d, y_mid - gap / 2 - win_w, y_mid - gap / 2, 100, 255, layer=7)
    sc.add_kors_window_west(-west_d, y_mid + gap / 2, y_mid + gap / 2 + win_w, 100, 255, layer=7)
    sc.add_kors_window_west(-west_d, y_mid - gap / 2 - win_w, y_mid - gap / 2, 380, 530, layer=7)
    sc.add_kors_window_west(-west_d, y_mid + gap / 2, y_mid + gap / 2 + win_w, 380, 530, layer=7)

    # South side wall of west wing — symmetric double kors-sprosse windows in BOTH 1st & 2nd floor
    xc_s = -west_d / 2.0
    hw_s = 68.0 if west_d >= 260 else 60.0
    sc.add_kors_window_south(y_s, xc_s - hw_s, xc_s + hw_s, 105, 250, layer=7)
    sc.add_kors_window_south(y_s, xc_s - hw_s, xc_s + hw_s, 385, 530, layer=7)

    # West wing ROOF (South slope + North slope meeting main roof cleanly at exact 3D valley!)
    ov_w = 30.0
    z_w_ov = z_eaves - ov_w * t_wing
    # South roof slope of west cross-wing: from (-west_d-30, y_s-ov_w, z_w_ov) to (0, y_s, z_eaves) to (x_stop, y_mid, z_wing_ridge) to (-west_d-30, y_mid, z_wing_ridge)
    sc.add_poly([
        (-west_d - 30, y_s - ov_w, z_w_ov),
        (0, y_s - ov_w, z_w_ov),
        (x_stop, y_mid, z_wing_ridge),
        (-west_d - 30, y_mid, z_wing_ridge),
    ], "#1e293b", stroke="#0f172a", sw=2.0, layer=8, ambient=0.52)
    # North roof slope (behind west gable wall -> layer=5 so it never overlaps the front gable triangle!)
    sc.add_poly([
        (-west_d - 30, y_mid, z_wing_ridge),
        (x_stop, y_mid, z_wing_ridge),
        (0, y_n + ov_w, z_w_ov),
        (-west_d - 30, y_n + ov_w, z_w_ov),
    ], "#334155", stroke="#0f172a", sw=1.8, layer=5, ambient=0.60)
    # White gable bargeboard on west wing
    sc.add_poly([(-west_d - 30, y_s - ov_w, z_w_ov), (-west_d - 30, y_mid, z_wing_ridge), (-west_d - 30, y_mid, z_wing_ridge + 14), (-west_d - 30, y_s - ov_w, z_w_ov + 14)],
                "#ffffff", stroke="#1e293b", sw=1.2, layer=9)
    sc.add_poly([(-west_d - 30, y_mid, z_wing_ridge), (-west_d - 30, y_n + ov_w, z_w_ov), (-west_d - 30, y_n + ov_w, z_w_ov + 14), (-west_d - 30, y_mid, z_wing_ridge + 14)],
                "#f1f5f9", stroke="#1e293b", sw=1.2, layer=9)

    # --- 3D DIMENSION CALLOUTS directly in world space ---
    # Depth arrow along south side of west wing (at Z = 10, Y = y_s - 55)
    sc.add_line((-west_d, y_s - 55, 10), (0, y_s - 55, 10), stroke="#0284c7", sw=3.2, layer=9)
    sc.add_line((-west_d, y_s - 35, 10), (-west_d, y_s - 75, 10), stroke="#0284c7", sw=2.6, layer=9)
    sc.add_line((0, y_s - 35, 10), (0, y_s - 75, 10), stroke="#0284c7", sw=2.6, layer=9)
    sc.add_text_at((-west_d / 2, y_s - 105, 10), label_wing, dx=16, dy=22, size=19, weight="800", fill="#0369a1")

    # Width arrow along west face of west wing (at X = -west_d - 65, Z = 10)
    sc.add_line((-west_d - 65, y_s, 10), (-west_d - 65, y_n, 10), stroke="#0f172a", sw=2.6, layer=9)
    sc.add_line((-west_d - 45, y_s, 10), (-west_d - 85, y_s, 10), stroke="#0f172a", sw=2.2, layer=9)
    sc.add_line((-west_d - 45, y_n, 10), (-west_d - 85, y_n, 10), stroke="#0f172a", sw=2.2, layer=9)
    sc.add_text_at((-west_d - 115, y_mid, 10), f"{(y_n - y_s)/100:.2f} m bred", dy=6, size=18, weight="800", fill="#0f172a", anchor="end")

    # Main south width arrow (8.66 m)
    sc.add_line((0, -295, 10), (866, -295, 10), stroke="#475569", sw=2.2, layer=9)
    sc.add_line((0, -275, 10), (0, -315, 10), stroke="#475569", sw=2.0, layer=9)
    sc.add_line((866, -275, 10), (866, -315, 10), stroke="#475569", sw=2.0, layer=9)
    sc.add_text_at((433, -345, 10), "8,66 m hovedbredde", dy=18, size=17, weight="700", fill="#334155")

    # Chimney callout cleanly above chimney
    sc.add_text_at((182, 418, 920), "Orig. pipe (på vestflate)", dy=-10, size=15, weight="800", fill="#9a3412")

    return sc.render()


def main():
    W, H = 2640, 1280
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        "<defs>",
        '  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">',
        '    <stop offset="0%" stop-color="#bae6fd"/>',
        '    <stop offset="65%" stop-color="#f0f9ff"/>',
        '    <stop offset="100%" stop-color="#fef3c7"/>',
        "  </linearGradient>",
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="#f8fafc"/>',
        # Header
        f'<rect x="0" y="0" width="{W}" height="130" fill="#0f172a"/>',
        f'<rect x="0" y="124" width="{W}" height="6" fill="#0284c7"/>',
        f'<text x="60" y="56" font-size="36" font-weight="800" fill="#ffffff">M6 (#50) — Eksakt 3D-sammenligning SØRVEST: Alternativ 1 vs. Alternativ 2</text>',
        f'<text x="60" y="96" font-size="21" font-weight="500" fill="#cbd5e1">Matematisk 3D-projeksjon fra eksakt samme sørvest-kamera • Alt 1 (3,30 × 5,20 m, 20° tak) vs. Alt 2 (3,00 × 5,02 m, 32,7° parallelt saltak)</text>',
        # Left panel backdrop
        f'<rect x="40" y="160" width="1260" height="980" fill="url(#sky)" stroke="#cbd5e1" stroke-width="2" rx="12"/>',
        # Right panel backdrop
        f'<rect x="1340" y="160" width="1260" height="980" fill="url(#sky)" stroke="#cbd5e1" stroke-width="2" rx="12"/>',
        # Clip paths
        '<clipPath id="clipL"><rect x="40" y="160" width="1260" height="980" rx="12"/></clipPath>',
        '<clipPath id="clipR"><rect x="1340" y="160" width="1260" height="980" rx="12"/></clipPath>',
    ]

    # Exact same elevated SW 3/4 camera for BOTH panels (pulled back so full house & 8,66m width fit with clean margin!)
    cam_pos = (-1980.0, -1750.0, 840.0)
    cam_tgt = (240.0, 480.0, 400.0)

    camL = Camera3D(cam_pos, cam_tgt, fov_deg=35.0, cx=675.0, cy=720.0, width=1220.0)
    camR = Camera3D(cam_pos, cam_tgt, fov_deg=35.0, cx=1975.0, cy=720.0, width=1220.0)

    svg.append('<g clip-path="url(#clipL)">')
    svg.extend(build_house_3d(camL, west_d=330.0, y_s=236.0, y_n=756.0, wing_deg=20.0, label_wing="3,30 m UT MOT VEST"))
    svg.append("</g>")

    svg.append('<g clip-path="url(#clipR)">')
    svg.extend(build_house_3d(camR, west_d=300.0, y_s=344.0, y_n=846.0, wing_deg=32.7, label_wing="3,00 m UT MOT VEST"))
    svg.append("</g>")

    # Panel banners
    svg.append('<rect x="65" y="180" width="760" height="72" fill="#ffffff" opacity="0.94" stroke="#0284c7" stroke-width="2" rx="10"/>')
    svg.append('<text x="90" y="212" font-size="22" font-weight="800" fill="#0f172a">ALTERNATIV 1: 3,30 × 5,20 m (20° slakt saltak)</text>')
    svg.append('<text x="90" y="238" font-size="16" font-weight="600" fill="#0284c7">Netto stue ~24,0 m² (ekskl. bokhylle + 120 gang) • Verandadør nord • 28 cm klar av pipe</text>')

    svg.append('<rect x="1365" y="180" width="840" height="72" fill="#ffffff" opacity="0.94" stroke="#059669" stroke-width="2" rx="10"/>')
    svg.append('<text x="1390" y="212" font-size="22" font-weight="800" fill="#0f172a">ALTERNATIV 2: 3,00 × 5,02 m (32,7° parallelt saltak)</text>')
    svg.append('<text x="1390" y="238" font-size="16" font-weight="600" fill="#059669">Netto stue ~25,0 m² (ekskl. bokhylle + 120 gang) • Samme takvinkel som hovedtak • 33 cm klar av pipe</text>')

    # Footer
    svg.append(f'<rect x="40" y="1165" width="{W - 80}" height="88" fill="#ffffff" stroke="#cbd5e1" stroke-width="2" rx="10"/>')
    svg.append('<text x="75" y="1200" font-size="19" font-weight="700" fill="#0f172a">Direkte volum- og taksammenligning (eksakt 3D-projeksjon):</text>')
    svg.append('<text x="75" y="1230" font-size="18" font-weight="500" fill="#334155">Venstre: Alt 1 (3,30 × 5,20 m, 20° slakere tak, ~24,0 m² netto stue). Høyre: Alt 2 (3,00 × 5,02 m, 3,20 | 5,02 | 3,44 m -> parallelt 32,7° saltak som hovedtaket, 33 cm klar av pipa og ~25,0 m² netto stue!).</text>')
    svg.append("</svg>")

    out = os.path.join(OUT_DIR, "perspektiv_3d_eksakt_dybde.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
