#!/usr/bin/env python3
"""
Exact 3D mathematical perspective projection from NORTHWEST 3/4 view (standing on the driveway)
comparing TRUE to-scale 3D proportions of BOTH alternatives side-by-side:
  - Left:  Alternativ 1 — 3,30 m x 5,20 m vest-tverrfløy (20° slakt saltak, nord-verandadør) + 2,10 m nord-tilbygg
  - Right: Alternativ 2 (Catrine) — 2,30 m x 5,02 m vest-tverrfløy på eksist. mur (parallelt 32,7° saltak) + 2,50 m nord-tilbygg
"""

import math
import os
import sys

sys.path.insert(0, "/home/kiro/repos/m6/scripts")
from generate_3d_perspektiv_eksakt import Camera3D, Scene3D, esc

OUT_DIR = "/home/kiro/repos/m6/assets/images/drawings"


def add_kors_north(sc: Scene3D, y_wall, x1, x2, z1, z2, single=False, is_door=False, layer=3):
    """4-pane Norwegian kors-sprosse window or double veranda door on a north-facing wall (y = y_wall, facing +Y)."""
    y_out = y_wall + 1.5
    sc.add_poly([(x1 - 6, y_out, z1 - 6), (x2 + 6, y_out, z1 - 6), (x2 + 6, y_out, z2 + 6), (x1 - 6, y_out, z2 + 6)],
                "#ffffff", stroke="#475569", sw=1.0, layer=layer, auto_shade=False, depth_bias=-4.0)
    sc.add_poly([(x1, y_out + 0.5, z1), (x2, y_out + 0.5, z1), (x2, y_out + 0.5, z2), (x1, y_out + 0.5, z2)],
                "#475569", stroke="#1e293b", sw=1.3, layer=layer, auto_shade=False, depth_bias=-6.0)
    if is_door:
        zb = z1 + (z2 - z1) * 0.28
        sc.add_poly([(x1 + 2, y_out + 0.9, z1 + 2), (x2 - 2, y_out + 0.9, z1 + 2), (x2 - 2, y_out + 0.9, zb), (x1 + 2, y_out + 0.9, zb)],
                    "#f8fafc", stroke="#64748b", sw=1.0, layer=layer, auto_shade=False, depth_bias=-7.0)
        zm = zb + (z2 - zb) * 0.62
        sc.add_poly([(x1 + 2, y_out + 0.8, zm), (x2 - 2, y_out + 0.8, zm), (x2 - 2, y_out + 0.8, z2 - 2), (x1 + 2, y_out + 0.8, z2 - 2)],
                    "#bae6fd", stroke="none", sw=0, layer=layer, auto_shade=False, opacity=0.45, depth_bias=-7.0)
        sc.add_line((x1, y_out + 1.2, zb), (x2, y_out + 1.2, zb), stroke="#ffffff", sw=2.4, layer=layer, depth_bias=-9.0)
        sc.add_line((x1, y_out + 1.2, zm), (x2, y_out + 1.2, zm), stroke="#ffffff", sw=2.2, layer=layer, depth_bias=-9.0)
        xm = (x1 + x2) / 2.0
        sc.add_line((xm, y_out + 1.2, z1), (xm, y_out + 1.2, z2), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)
    else:
        zm = z1 + (z2 - z1) * 0.66
        sc.add_poly([(x1 + 2, y_out + 0.8, zm), (x2 - 2, y_out + 0.8, zm), (x2 - 2, y_out + 0.8, z2 - 2), (x1 + 2, y_out + 0.8, z2 - 2)],
                    "#bae6fd", stroke="none", sw=0, layer=layer, auto_shade=False, opacity=0.42, depth_bias=-7.0)
        sc.add_line((x1, y_out + 1.2, zm), (x2, y_out + 1.2, zm), stroke="#ffffff", sw=2.4, layer=layer, depth_bias=-9.0)
        if not single:
            xm = (x1 + x2) / 2.0
            sc.add_line((xm, y_out + 1.2, z1), (xm, y_out + 1.2, z2), stroke="#ffffff", sw=2.4, layer=layer, depth_bias=-9.0)


def add_siding_north(sc: Scene3D, y_wall, x1, x2, z1, z2, step=28, layer=2):
    z = z1 + step
    while z < z2 - 8:
        sc.add_line((x1, y_wall + 0.5, z), (x2, y_wall + 0.5, z), stroke="#cbd5e1", sw=0.6, layer=layer, depth_bias=-2.0, opacity=0.65)
        z += step


def build_nw_scene(cam: Camera3D, alt: int = 1):
    sc = Scene3D(cam)
    sc.sun = (-0.65, 0.55, 0.52)
    t_main = math.tan(math.radians(32.7))
    z_eaves = 610.0
    z_ridge = z_eaves + 433.0 * t_main  # 888 cm

    if alt == 1:
        west_d = 330.0
        y_s, y_n = 236.0, 756.0       # 5,20 m wide, 4,10 m from north wall
        wing_deg = 20.0
        north_d = 210.0
    else:
        west_d = 280.0                # Alt 2 (Catrine): 2,80 m deep x 5,02 m wide!
        y_s, y_n = 344.0, 846.0       # 3,20 | 5,02 | 3,44 m
        wing_deg = 32.7               # Parallel 32,7° saltak!
        north_d = 250.0               # 2,50 m north extension (6 m² Vindfang + 6 m² Vaskerom)

    # Ground lawn + gravel driveway in north-west
    sc.add_poly([(-900, -300, 0), (1400, -300, 0), (1400, 2300, 0), (-900, 2300, 0)],
                "#bbf7d0", stroke="none", sw=0, layer=0, auto_shade=False)
    sc.add_poly([(-550, 1180, 1), (1100, 1180, 1), (1100, 2250, 1), (-550, 2250, 1)],
                "#d6d3d1", stroke="#a8a29e", sw=1, layer=0, auto_shade=False)

    # --- ENCLOSED 2-STORY WEST CROSS-WING (X = -west_d..0, Y = y_s..y_n) ---
    y_mid = (y_s + y_n) / 2.0
    half_w = (y_n - y_s) / 2.0
    t_wing = math.tan(math.radians(wing_deg))
    z_wing_ridge = z_eaves + half_w * t_wing
    x_stop = (z_wing_ridge - z_eaves) / t_main

    # West wing plinth
    sc.add_poly([(-west_d, y_s, 0), (-west_d, y_n, 0), (-west_d, y_n, 40), (-west_d, y_s, 40)], "#64748b", layer=1)
    sc.add_poly([(-west_d, y_n, 0), (0, y_n, 0), (0, y_n, 40), (-west_d, y_n, 40)], "#475569", layer=1)
    # West wing rectangular west wall (40..z_eaves)
    sc.add_poly([(-west_d, y_s, 40), (-west_d, y_n, 40), (-west_d, y_n, z_eaves), (-west_d, y_s, z_eaves)],
                "#ffffff", stroke="#1e293b", sw=1.7, layer=1)
    sc.add_siding_west(-west_d, y_s, y_n, 40, z_eaves, layer=1)
    # West wing NORTH SIDE WALL (Y = y_n)
    sc.add_poly([(-west_d, y_n, 40), (0, y_n, 40), (0, y_n, z_eaves), (-west_d, y_n, z_eaves)],
                "#f8fafc", stroke="#1e293b", sw=1.7, layer=1)
    add_siding_north(sc, y_n, -west_d, 0, 40, z_eaves, layer=1)

    # West wing windows (WEST face)
    win_half_span = 178 if alt == 1 else 170
    win_gap = 22 if alt == 1 else 18
    sc.add_kors_window_west(-west_d, y_mid - win_half_span, y_mid - win_gap, 100, 255, layer=2)
    sc.add_kors_window_west(-west_d, y_mid + win_gap, y_mid + win_half_span, 100, 255, layer=2)
    sc.add_kors_window_west(-west_d, y_mid - win_half_span, y_mid - win_gap, 380, 530, layer=2)
    sc.add_kors_window_west(-west_d, y_mid + win_gap, y_mid + win_half_span, 380, 530, layer=2)

    # West wing NORTH face (Y = y_n) — IDENTICAL double veranda door + NW SKIFERPLATTING for BOTH Alt 1 and Alt 2!
    xc_n = -west_d / 2.0
    add_kors_north(sc, y_n, xc_n - 75, xc_n + 75, 42, 252, is_door=True, layer=2)
    add_kors_north(sc, y_n, xc_n - 65, xc_n + 65, 383, 528, single=False, layer=2)
    # NW SLATE PATIO (skiferplatting, X = -west_d..0, Y = y_n..y_n+220, Z = 18) right outside north veranda door!
    sc.add_poly([(-west_d, y_n, 18), (0, y_n, 18), (0, y_n + 220, 18), (-west_d, y_n + 220, 18)],
                "#64748b", stroke="#334155", sw=1.4, layer=1, auto_shade=True, ambient=0.72)
    for gx in range(int(-west_d) + 70, 0, 70):
        sc.add_line((gx, y_n, 18.6), (gx, y_n + 220, 18.6), stroke="#334155", sw=0.75, layer=1, depth_bias=-2.0, opacity=0.6)
    for gy in range(int(y_n) + 55, int(y_n + 220), 55):
        sc.add_line((-west_d, gy, 18.6), (0, gy, 18.6), stroke="#334155", sw=0.75, layer=1, depth_bias=-2.0, opacity=0.6)
    sc.add_poly([(-west_d, y_n + 220, 0), (0, y_n + 220, 0), (0, y_n + 220, 18), (-west_d, y_n + 220, 18)],
                "#475569", stroke="#1e293b", sw=1.1, layer=1, auto_shade=True)
    sc.add_poly([(-west_d, y_n, 0), (-west_d, y_n + 220, 0), (-west_d, y_n + 220, 18), (-west_d, y_n, 18)],
                "#475569", stroke="#1e293b", sw=1.1, layer=1, auto_shade=True)

    # --- MAIN HOUSE WALLS (X=0..866, Y=0..1166) ---
    # Main West wall north of wing (X=0, Y=y_n..1166)
    sc.add_poly([(0, y_n, 0), (0, 1166, 0), (0, 1166, 40), (0, y_n, 40)], "#64748b", layer=2)
    sc.add_poly([(0, y_n, 40), (0, 1166, 40), (0, 1166, z_eaves), (0, y_n, z_eaves)], "#ffffff", stroke="#334155", sw=1.7, layer=2)
    sc.add_siding_west(0, y_n, 1166, 40, z_eaves, layer=2)
    if alt == 1:
        sc.add_kors_window_west(0, 965, 1070, 105, 245, layer=3)            # Trapp 1st
        sc.add_kors_window_west(0, 965, 1070, 385, 525, layer=3)            # Trapp 2nd
        sc.add_kors_window_west(0, 805, 875, 115, 245, single=True, layer=3)  # Vask 1st
        sc.add_kors_window_west(0, 805, 875, 395, 525, single=True, layer=3)  # Bod 2nd
    else:
        # Alt 2: single centered double kors-sprosse Trapp window in 3.20 m north flank (y_from_north=95..225 -> Y=941..1071)
        sc.add_kors_window_west(0, 941, 1071, 103, 248, layer=3)
        sc.add_kors_window_west(0, 941, 1071, 383, 528, layer=3)

    # Main North Gable wall (Y=1166, X=0..866)
    sc.add_poly([(0, 1166, 0), (866, 1166, 0), (866, 1166, 40), (0, 1166, 40)], "#64748b", layer=2)
    sc.add_poly([(0, 1166, 40), (866, 1166, 40), (866, 1166, z_eaves), (433, 1166, z_ridge), (0, 1166, z_eaves)],
                "#ffffff", stroke="#1e293b", sw=1.8, layer=2)
    add_siding_north(sc, 1166, 0, 866, 40, z_eaves, layer=2)

    # Main North Gable windows (1.etg half 62 cm at X=128..190 flush w/ west edge & center mullion of 2.etg full 124 cm at X=128..252; clear of stair mid-landing X=36..126!)
    add_kors_north(sc, 1166, 128, 190, 103, 248, single=True, layer=3)
    add_kors_north(sc, 1166, 128, 252, 383, 528, single=False, layer=3)
    add_kors_north(sc, 1166, 375, 491, 655, 770, single=False, layer=3)

    # --- MAIN WEST ROOF SLOPE + CHIMNEY + WEST WING NORTH ROOF SLOPE ---
    ov_x = -35.0
    z_ov = z_eaves + ov_x * t_main
    sc.add_poly([(ov_x, -35, z_ov), (ov_x, 1201, z_ov), (433, 1201, z_ridge), (433, -35, z_ridge)],
                "#334155", stroke="#0f172a", sw=1.8, layer=4, ambient=0.58)
    for frac in [0.18, 0.36, 0.54, 0.72, 0.88]:
        rx = ov_x + (433 - ov_x) * frac
        rz = z_ov + (z_ridge - z_ov) * frac + 0.8
        sc.add_line((rx, 0, rz), (rx, 1198, rz), stroke="#475569", sw=0.8, layer=4, depth_bias=-1.0, opacity=0.6)
    # Skylight north of west wing
    x_a, x_b = 225.0, 345.0
    z_a = z_eaves + x_a * t_main + 3.0
    z_b = z_eaves + x_b * t_main + 3.0
    sky_y1, sky_y2 = (945, 1055) if alt == 1 else (951, 1061)
    sc.add_poly([(x_a, sky_y1, z_a), (x_a, sky_y2, z_a), (x_b, sky_y2, z_b), (x_b, sky_y1, z_b)],
                "#7dd3fc", stroke="#0f172a", sw=1.8, layer=5, auto_shade=False)
    # North gable roof fascia
    sc.add_poly([(ov_x, 1201, z_ov), (433, 1201, z_ridge), (433, 1201, z_ridge + 16), (ov_x, 1201, z_ov + 16)],
                "#ffffff", stroke="#1e293b", sw=1.2, layer=5)
    sc.add_poly([(433, 1201, z_ridge), (866 + 35, 1201, z_ov), (866 + 35, 1201, z_ov + 16), (433, 1201, z_ridge + 16)],
                "#e2e8f0", stroke="#1e293b", sw=1.2, layer=5)

    # Original chimney on west slope (X=135..230, Y=391..446 — clearly behind/south of wing valley in Alt 2 too!)
    cx1, cx2, cy1, cy2 = 135.0, 230.0, 391.0, 446.0
    cz_w = z_eaves + cx1 * t_main - 2.0
    cz_e = z_eaves + cx2 * t_main - 2.0
    cz_t = 895.0
    sc.add_poly([(cx1, cy1, cz_w), (cx1, cy2, cz_w), (cx1, cy2, cz_t), (cx1, cy1, cz_t)], "#64748b", stroke="#1e293b", sw=1.4, layer=5)
    sc.add_poly([(cx1, cy2, cz_w), (cx2, cy2, cz_e), (cx2, cy2, cz_t), (cx1, cy2, cz_t)], "#475569", stroke="#1e293b", sw=1.4, layer=5)
    sc.add_poly([(cx1 - 5, cy1 - 5, cz_t), (cx2 + 5, cy1 - 5, cz_t), (cx2 + 5, cy2 + 5, cz_t), (cx1 - 5, cy2 + 5, cz_t)], "#334155", stroke="#0f172a", sw=1.3, layer=5)

    # West wing NORTH roof slope (layer=5 — sits cleanly BEHIND the layer=6 white west gable triangle!)
    ov_w = 28.0
    z_w_ov = z_eaves - ov_w * t_wing
    sc.add_poly([
        (-west_d - 28, y_mid, z_wing_ridge),
        (x_stop, y_mid, z_wing_ridge),
        (0, y_n + ov_w, z_w_ov),
        (-west_d - 28, y_n + ov_w, z_w_ov),
    ], "#1e293b", stroke="#0f172a", sw=1.8, layer=5, ambient=0.55)
    # West wing GABLE TRIANGLE on layer=6 so steep 32,7° gable stays 100% crisp!
    sc.add_poly([(-west_d, y_s, z_eaves), (-west_d, y_n, z_eaves), (-west_d, y_mid, z_wing_ridge)],
                "#ffffff", stroke="#1e293b", sw=1.7, layer=6)
    # White gable bargeboard on north verge of west wing (layer=7)
    sc.add_poly([(-west_d - 28, y_mid, z_wing_ridge), (-west_d - 28, y_n + ov_w, z_w_ov), (-west_d - 28, y_n + ov_w, z_w_ov + 14), (-west_d - 28, y_mid, z_wing_ridge + 14)],
                "#ffffff", stroke="#1e293b", sw=1.2, layer=7)
    sc.add_poly([(-west_d - 28, y_mid, z_wing_ridge), (-west_d - 28, y_s - ov_w, z_w_ov), (-west_d - 28, y_s - ov_w, z_w_ov + 14), (-west_d - 28, y_mid, z_wing_ridge + 14)],
                "#e2e8f0", stroke="#1e293b", sw=1.2, layer=7)

    # --- 1-STORY NORTH EXTENSION WITH PARALLEL 32.7° SALTAK (2,10 m in Alt 1, 2,50 m in Alt 2!) ---
    nx_w = 231.0
    nx_door = 381.0
    nx_e = 866.0
    nx_mid = (nx_w + nx_e) / 2.0  # 548.5
    ny_n = 1166.0 + north_d
    nz_eaves = 290.0
    nz_ridge = nz_eaves + 317.5 * t_main  # 494 cm

    # Porch landing & plinth
    sc.add_poly([(nx_w, 1166, 0), (nx_e, 1166, 0), (nx_e, ny_n, 0), (nx_w, ny_n, 0)], "#94a3b8", layer=7)
    sc.add_poly([(nx_w, ny_n, 0), (nx_e, ny_n, 0), (nx_e, ny_n, 40), (nx_w, ny_n, 40)], "#64748b", stroke="#334155", sw=1.2, layer=7)
    sc.add_poly([(nx_w, 1166, 0), (nx_w, ny_n, 0), (nx_w, ny_n, 40), (nx_w, 1166, 40)], "#475569", stroke="#334155", sw=1.2, layer=7)
    sc.add_poly([(nx_w, 1166, 40), (nx_door, 1166, 40), (nx_door, ny_n, 40), (nx_w, ny_n, 40)], "#cbd5e1", stroke="#64748b", sw=1.1, layer=7)
    # Entry steps on west side of covered portico
    st_y1 = 1185.0
    st_y2 = ny_n - 32.0
    sc.add_poly([(nx_w - 45, st_y1, 0), (nx_w, st_y1, 0), (nx_w, st_y2, 0), (nx_w - 45, st_y2, 0)], "#94a3b8", layer=7)
    sc.add_poly([(nx_w - 45, st_y1, 20), (nx_w, st_y1, 20), (nx_w, st_y2, 20), (nx_w - 45, st_y2, 20)], "#cbd5e1", stroke="#64748b", sw=1.1, layer=7)

    # WEST WALL OF VINDFANG (X = 381) with 140/210 ENTRANCE DOOR
    sc.add_poly([(nx_door, 1166, 40), (nx_door, ny_n, 40), (nx_door, ny_n, nz_eaves), (nx_door, 1166, nz_eaves)],
                "#f8fafc", stroke="#1e293b", sw=1.7, layer=8)
    dy_c = (1166.0 + ny_n) / 2.0
    sc.add_poly([(nx_door - 1.5, dy_c - 70, 42), (nx_door - 1.5, dy_c + 70, 42), (nx_door - 1.5, dy_c + 70, 252), (nx_door - 1.5, dy_c - 70, 252)],
                "#ffffff", stroke="#0f172a", sw=1.8, layer=8, auto_shade=False)
    sc.add_poly([(nx_door - 2.2, dy_c - 55, 155), (nx_door - 2.2, dy_c + 12, 155), (nx_door - 2.2, dy_c + 12, 236), (nx_door - 2.2, dy_c - 55, 236)],
                "#93c5fd", stroke="#334155", sw=1.1, layer=8, auto_shade=False)
    sc.add_poly([(nx_door - 2.2, dy_c + 26, 60), (nx_door - 2.2, dy_c + 60, 60), (nx_door - 2.2, dy_c + 60, 236), (nx_door - 2.2, dy_c + 26, 236)],
                "#bae6fd", stroke="#334155", sw=1.1, layer=8, auto_shade=False)
    sc.add_poly([(nx_door - 5, dy_c + 76, 185), (nx_door - 5, dy_c + 92, 185), (nx_door - 5, dy_c + 92, 212), (nx_door - 5, dy_c + 76, 212)],
                "#fbbf24", stroke="#92400e", sw=1.3, layer=8, auto_shade=False)

    # NORTH WALL OF ENCLOSED VINDFANG + UTEBOD/VASKEROM
    sc.add_poly([(nx_door, ny_n, 40), (nx_e, ny_n, 40), (nx_e, ny_n, nz_eaves), (nx_door, ny_n, nz_eaves)],
                "#ffffff", stroke="#1e293b", sw=1.8, layer=8)
    add_siding_north(sc, ny_n, nx_door, nx_e, 40, nz_eaves, layer=8)
    add_kors_north(sc, ny_n, 490, 625, 102, 242, single=False, layer=9)  # Vindfang double
    add_kors_north(sc, ny_n, 710, 782, 108, 240, single=True, layer=9)   # Bod (Alt 1) / Vaskerom (Alt 2) narrow

    # Porch column + wooden railing across front (north) of portico
    sc.add_poly([(nx_w, ny_n - 16, 40), (nx_w + 16, ny_n - 16, 40), (nx_w + 16, ny_n - 16, nz_eaves), (nx_w, ny_n - 16, nz_eaves)], "#ffffff", stroke="#334155", sw=1.3, layer=9)
    sc.add_poly([(nx_w, ny_n, 40), (nx_w + 16, ny_n, 40), (nx_w + 16, ny_n, nz_eaves), (nx_w, ny_n, nz_eaves)], "#f1f5f9", stroke="#334155", sw=1.3, layer=9)
    sc.add_poly([(nx_w + 16, ny_n, 125), (nx_door, ny_n, 125), (nx_door, ny_n, 136), (nx_w + 16, ny_n, 136)], "#ffffff", stroke="#334155", sw=1.1, layer=9)
    sc.add_poly([(nx_w + 16, ny_n, 48), (nx_door, ny_n, 48), (nx_door, ny_n, 58), (nx_w + 16, ny_n, 58)], "#ffffff", stroke="#334155", sw=1.1, layer=9)
    for rx in range(262, 376, 18):
        sc.add_line((rx, ny_n + 1, 58), (rx, ny_n + 1, 125), stroke="#475569", sw=2.0, layer=9)

    # NORTH EXTENSION SALTAK GABLE TRIANGLE + WEST ROOF SLOPE
    sc.add_poly([(nx_w, ny_n, nz_eaves), (nx_e, ny_n, nz_eaves), (nx_mid, ny_n, nz_ridge)],
                "#ffffff", stroke="#1e293b", sw=1.8, layer=9)
    ov_n = 26.0
    z_n_ov = nz_eaves - ov_n * t_main
    sc.add_poly([
        (nx_w - ov_n, 1166, z_n_ov),
        (nx_w - ov_n, ny_n + 26, z_n_ov),
        (nx_mid, ny_n + 26, nz_ridge),
        (nx_mid, 1166, nz_ridge),
    ], "#1e293b", stroke="#0f172a", sw=1.8, layer=10, ambient=0.52)
    sc.add_poly([(nx_w - ov_n, ny_n + 26, z_n_ov), (nx_mid, ny_n + 26, nz_ridge), (nx_mid, ny_n + 26, nz_ridge + 14), (nx_w - ov_n, ny_n + 26, z_n_ov + 14)],
                "#ffffff", stroke="#1e293b", sw=1.1, layer=10)
    sc.add_poly([(nx_mid, ny_n + 26, nz_ridge), (nx_e + ov_n, ny_n + 26, z_n_ov), (nx_e + ov_n, ny_n + 26, z_n_ov + 14), (nx_mid, ny_n + 26, nz_ridge + 14)],
                "#e2e8f0", stroke="#1e293b", sw=1.1, layer=10)

    # Clean callouts (placed strictly in open sky/lawn with zero wall overlap)
    if alt == 1:
        sc.add_text_at((nx_mid, ny_n + 26, nz_ridge + 85), "2,10 m nord-tilbygg (32,7°)", dx=-65, dy=-18, size=14, weight="800", fill="#0f172a", anchor="middle")
        sc.add_text_at((-west_d / 2, y_n + 40, 0), "3,30×5,20 m (20°) • Verandadør + skiferplatting NV", dx=-15, dy=58, size=13, weight="800", fill="#0369a1")
    else:
        sc.add_text_at((nx_mid, ny_n + 26, nz_ridge + 85), "2,50 m nord-tilbygg", dx=-75, dy=-34, size=14, weight="800", fill="#0f172a", anchor="middle")
        sc.add_text_at((nx_mid, ny_n + 26, nz_ridge + 85), "(6 m² Vask + 6 m² Vindfang)", dx=-75, dy=-16, size=12, weight="700", fill="#047857", anchor="middle")
        sc.add_text_at((-west_d / 2, y_n + 40, 0), "2,80×5,02 m (32,7°) • Verandadør + skiferplatting NV", dx=-15, dy=58, size=13, weight="800", fill="#059669")

    return sc.render()


def main():
    W, H = 2400, 1140
    pw, ph = 1140, 880
    py = 195
    p1x, p2x = 40, 1220

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        "<defs>",
        '  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">',
        '    <stop offset="0%" stop-color="#bae6fd"/>',
        '    <stop offset="68%" stop-color="#f0f9ff"/>',
        '    <stop offset="100%" stop-color="#fef3c7"/>',
        "  </linearGradient>",
        f'  <clipPath id="clipL"><rect x="{p1x}" y="{py}" width="{pw}" height="{ph}" rx="10"/></clipPath>',
        f'  <clipPath id="clipR"><rect x="{p2x}" y="{py}" width="{pw}" height="{ph}" rx="10"/></clipPath>',
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="#f8fafc"/>',
        f'<rect x="0" y="0" width="{W}" height="122" fill="#0f172a"/>',
        f'<rect x="0" y="116" width="{W}" height="6" fill="#0284c7"/>',
        f'<text x="48" y="54" font-size="34" font-weight="800" fill="#ffffff">M6 (#50) — Eksakt 3D-modell NORDVEST: Alternativ 1 vs. Alternativ 2</text>',
        f'<text x="48" y="92" font-size="19" font-weight="500" fill="#cbd5e1">Identisk kameravinkel fra oppkjørselen (null AI-forvrengning) — sammenligner 3,30×5,20 m (20°) + 2,10 m nord mot 2,80×5,02 m (32,7°) + 2,50 m nord</text>',

        # Left Panel Header
        f'<rect x="{p1x}" y="138" width="{pw}" height="46" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5" rx="8"/>',
        f'<text x="{p1x + pw / 2}" y="168" font-size="20" font-weight="800" fill="#0369a1" text-anchor="middle">ALTERNATIV 1 — 3,30 × 5,20 m vest (20° slakt saltak) + 2,10 m nord-tilbygg</text>',
        f'<rect x="{p1x}" y="{py}" width="{pw}" height="{ph}" fill="url(#sky)" stroke="#cbd5e1" stroke-width="2" rx="10"/>',

        # Right Panel Header
        f'<rect x="{p2x}" y="138" width="{pw}" height="46" fill="#d1fae5" stroke="#059669" stroke-width="1.5" rx="8"/>',
        f'<text x="{p2x + pw / 2}" y="168" font-size="20" font-weight="800" fill="#047857" text-anchor="middle">ALTERNATIV 2 (Catrine) — 2,80 × 5,02 m vest (parallelt 32,7° saltak) + 2,50 m nord-tilbygg</text>',
        f'<rect x="{p2x}" y="{py}" width="{pw}" height="{ph}" fill="url(#sky)" stroke="#cbd5e1" stroke-width="2" rx="10"/>',
    ]

    cam_l = Camera3D(pos=(-1820.0, 3150.0, 740.0), target=(220.0, 780.0, 380.0), fov_deg=35.0, cx=p1x + pw / 2.0 + 18, cy=py + ph * 0.54, width=pw * 0.96)
    cam_r = Camera3D(pos=(-1820.0, 3150.0, 740.0), target=(220.0, 780.0, 380.0), fov_deg=35.0, cx=p2x + pw / 2.0 + 18, cy=py + ph * 0.54, width=pw * 0.96)

    svg.append('<g clip-path="url(#clipL)">')
    svg.extend(build_nw_scene(cam_l, alt=1))
    svg.append("</g>")

    svg.append('<g clip-path="url(#clipR)">')
    svg.extend(build_nw_scene(cam_r, alt=2))
    svg.append("</g>")

    # Footer bar
    svg.append(
        f'<text x="{W / 2}" y="1116" font-size="16" font-weight="600" fill="#475569" text-anchor="middle">'
        f'Eksakt matematisk perspektiv (1:1 koordinater) • Begge viser parallelt 32,7° nord-tilbygg, portico m/ inngangsdør 140/210, tett nordvegg på Hovedsoverom og fluktende trappevinduer'
        f'</text>'
    )
    svg.append("</svg>")

    out = os.path.join(OUT_DIR, "perspektiv_3d_nordvest_eksakt.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
