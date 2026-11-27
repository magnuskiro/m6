#!/usr/bin/env python3
"""
Exact 3D mathematical perspective projection from NORTHWEST 3/4 view (standing on the driveway)
matching Magnus's exact North Facade hand sketch:
  - 1-story north extension (X=231..866, Y=1166..1376) with PARALLEL 32.7° SALTAK (peak Z=494 cm!)
  - Enclosed Utebod + Vindfang (X=381..866) + covered entry portico with wooden railing & visible 140/210 entrance door (X=231..381)
  - Right (west) of north extension: 1st-floor narrow Trapp window, 2nd-floor double kors-sprosse window, NO north window in Hovedsoverom
  - Full 3,30 m deep x 5,20 m wide enclosed west extension with 1st & 2nd floor double kors-sprosse windows on its NORTH face too!
"""

import math
import os
import sys

sys.path.insert(0, "/home/kiro/repos/m6/scripts")
from generate_3d_perspektiv_eksakt import Camera3D, Scene3D, esc

OUT_DIR = "/home/kiro/repos/m6/assets/images/drawings"


def add_kors_north(sc: Scene3D, y_wall, x1, x2, z1, z2, single=False, layer=3):
    """4-pane Norwegian kors-sprosse window on a north-facing wall (y = y_wall, facing +Y)."""
    y_out = y_wall + 1.5
    sc.add_poly([(x1 - 6, y_out, z1 - 6), (x2 + 6, y_out, z1 - 6), (x2 + 6, y_out, z2 + 6), (x1 - 6, y_out, z2 + 6)],
                "#ffffff", stroke="#475569", sw=1.0, layer=layer, auto_shade=False, depth_bias=-4.0)
    sc.add_poly([(x1, y_out + 0.5, z1), (x2, y_out + 0.5, z1), (x2, y_out + 0.5, z2), (x1, y_out + 0.5, z2)],
                "#475569", stroke="#1e293b", sw=1.3, layer=layer, auto_shade=False, depth_bias=-6.0)
    zm = z1 + (z2 - z1) * 0.66
    sc.add_poly([(x1 + 2, y_out + 0.8, zm), (x2 - 2, y_out + 0.8, zm), (x2 - 2, y_out + 0.8, z2 - 2), (x1 + 2, y_out + 0.8, z2 - 2)],
                "#bae6fd", stroke="none", sw=0, layer=layer, auto_shade=False, opacity=0.42, depth_bias=-7.0)
    sc.add_line((x1, y_out + 1.2, zm), (x2, y_out + 1.2, zm), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)
    if not single:
        xm = (x1 + x2) / 2.0
        sc.add_line((xm, y_out + 1.2, z1), (xm, y_out + 1.2, z2), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)


def add_siding_north(sc: Scene3D, y_wall, x1, x2, z1, z2, step=28, layer=2):
    z = z1 + step
    while z < z2 - 8:
        sc.add_line((x1, y_wall + 0.5, z), (x2, y_wall + 0.5, z), stroke="#cbd5e1", sw=0.65, layer=layer, depth_bias=-2.0, opacity=0.65)
        z += step


def build_nw_scene(cam: Camera3D, west_d=330.0, y_s=236.0, y_n=756.0, wing_deg=20.0):
    sc = Scene3D(cam)
    # Soft morning/afternoon northwest light
    sc.sun = (-0.65, 0.55, 0.52)
    t_main = math.tan(math.radians(32.7))
    z_eaves = 610.0
    z_ridge = z_eaves + 433.0 * t_main  # 888 cm

    # Ground lawn + curved gravel driveway in north-west
    sc.add_poly([(-900, -300, 0), (1400, -300, 0), (1400, 2200, 0), (-900, 2200, 0)],
                "#bbf7d0", stroke="none", sw=0, layer=0, auto_shade=False)
    sc.add_poly([(-550, 1180, 1), (1100, 1180, 1), (1100, 2150, 1), (-550, 2150, 1)],
                "#d6d3d1", stroke="#a8a29e", sw=1, layer=0, auto_shade=False)

    # --- ENCLOSED 2-STORY WEST CROSS-WING (back/right in NW view, X=-west_d..0, Y=y_s..y_n) ---
    y_mid = (y_s + y_n) / 2.0
    half_w = (y_n - y_s) / 2.0
    t_wing = math.tan(math.radians(wing_deg))
    z_wing_ridge = z_eaves + half_w * t_wing
    x_stop = (z_wing_ridge - z_eaves) / t_main

    # West wing plinth
    sc.add_poly([(-west_d, y_s, 0), (-west_d, y_n, 0), (-west_d, y_n, 40), (-west_d, y_s, 40)], "#64748b", layer=1)
    sc.add_poly([(-west_d, y_n, 0), (0, y_n, 0), (0, y_n, 40), (-west_d, y_n, 40)], "#475569", layer=1)
    # West wing WEST GABLE wall (X = -west_d)
    sc.add_poly([(-west_d, y_s, 40), (-west_d, y_n, 40), (-west_d, y_n, z_eaves), (-west_d, y_mid, z_wing_ridge), (-west_d, y_s, z_eaves)],
                "#ffffff", stroke="#1e293b", sw=1.8, layer=1)
    sc.add_siding_west(-west_d, y_s, y_n, 40, z_eaves, layer=1)
    # West wing NORTH SIDE WALL (Y = y_n, EXACT 3.30 m width!)
    sc.add_poly([(-west_d, y_n, 40), (0, y_n, 40), (0, y_n, z_eaves), (-west_d, y_n, z_eaves)],
                "#f8fafc", stroke="#1e293b", sw=1.8, layer=1)
    add_siding_north(sc, y_n, -west_d, 0, 40, z_eaves, layer=1)

    # West wing windows (west face + NORTH face as sketched by Magnus!)
    sc.add_kors_window_west(-west_d, y_mid - 178, y_mid - 22, 100, 255, layer=2)
    sc.add_kors_window_west(-west_d, y_mid + 22, y_mid + 178, 100, 255, layer=2)
    sc.add_kors_window_west(-west_d, y_mid - 178, y_mid - 22, 380, 530, layer=2)
    sc.add_kors_window_west(-west_d, y_mid + 22, y_mid + 178, 380, 530, layer=2)
    # NORTH face of west wing: 1st & 2nd floor double kors-sprosse windows!
    xc_n = -west_d / 2.0
    add_kors_north(sc, y_n, xc_n - 68, xc_n + 68, 105, 250, layer=2)
    add_kors_north(sc, y_n, xc_n - 68, xc_n + 68, 385, 530, layer=2)

    # --- MAIN HOUSE WALLS (X=0..866, Y=0..1166) ---
    # Main West wall (X=0, Y=y_n..1166 visible in front of wing)
    sc.add_poly([(0, y_n, 0), (0, 1166, 0), (0, 1166, 40), (0, y_n, 40)], "#64748b", layer=2)
    sc.add_poly([(0, y_n, 40), (0, 1166, 40), (0, 1166, z_eaves), (0, y_n, z_eaves)], "#ffffff", stroke="#334155", sw=1.8, layer=2)
    sc.add_siding_west(0, y_n, 1166, 40, z_eaves, layer=2)
    sc.add_kors_window_west(0, 965, 1070, 105, 245, layer=3)  # Stair 1st
    sc.add_kors_window_west(0, 965, 1070, 385, 525, layer=3)  # Stair 2nd
    sc.add_kors_window_west(0, 805, 875, 115, 245, single=True, layer=3)  # Vask 1st
    sc.add_kors_window_west(0, 805, 875, 395, 525, single=True, layer=3)  # Bod 2nd

    # Main North Gable wall (Y=1166, X=0..866)
    sc.add_poly([(0, 1166, 0), (866, 1166, 0), (866, 1166, 40), (0, 1166, 40)], "#64748b", layer=2)
    sc.add_poly([(0, 1166, 40), (866, 1166, 40), (866, 1166, z_eaves), (433, 1166, z_ridge), (0, 1166, z_eaves)],
                "#ffffff", stroke="#1e293b", sw=2.0, layer=2)
    add_siding_north(sc, 1166, 0, 866, 40, z_eaves, layer=2)

    # Main North Gable windows (EXACT match to Magnus's sketch!)
    # Note: in world X (0=west, 866=east): x_plot = 866 - X!
    # Right of north extension (west side, X=0..231): narrow 1st-floor window X=92..166
    add_kors_north(sc, 1166, 92, 166, 108, 245, single=True, layer=3)
    # 2nd floor double kors-sprosse window above right slope of north extension: x_plot=585..720 -> X=146..281
    add_kors_north(sc, 1166, 146, 281, 385, 530, single=False, layer=3)
    # Centered loft gable window: X=375..491
    add_kors_north(sc, 1166, 375, 491, 655, 770, single=False, layer=3)
    # NO north window in Hovedsoverom (east side X=450..866)!

    # --- MAIN WEST ROOF SLOPE + CHIMNEY + WEST WING NORTH ROOF SLOPE ---
    ov_x = -35.0
    z_ov = z_eaves + ov_x * t_main
    sc.add_poly([(ov_x, -35, z_ov), (ov_x, 1201, z_ov), (433, 1201, z_ridge), (433, -35, z_ridge)],
                "#334155", stroke="#0f172a", sw=2.0, layer=4, ambient=0.58)
    for frac in [0.18, 0.36, 0.54, 0.72, 0.88]:
        rx = ov_x + (433 - ov_x) * frac
        rz = z_ov + (z_ridge - z_ov) * frac + 0.8
        sc.add_line((rx, 0, rz), (rx, 1198, rz), stroke="#475569", sw=0.8, layer=4, depth_bias=-1.0, opacity=0.6)
    # Skylight north of west wing
    x_a, x_b = 225.0, 345.0
    z_a = z_eaves + x_a * t_main + 3.0
    z_b = z_eaves + x_b * t_main + 3.0
    sc.add_poly([(x_a, 945, z_a), (x_a, 1055, z_a), (x_b, 1055, z_b), (x_b, 945, z_b)],
                "#7dd3fc", stroke="#0f172a", sw=2.0, layer=5, auto_shade=False)
    # North gable roof fascia
    sc.add_poly([(ov_x, 1201, z_ov), (433, 1201, z_ridge), (433, 1201, z_ridge + 16), (ov_x, 1201, z_ov + 16)],
                "#ffffff", stroke="#1e293b", sw=1.2, layer=5)
    sc.add_poly([(433, 1201, z_ridge), (866 + 35, 1201, z_ov), (866 + 35, 1201, z_ov + 16), (433, 1201, z_ridge + 16)],
                "#e2e8f0", stroke="#1e293b", sw=1.2, layer=5)

    # Original chimney on west slope (behind west wing from NW view, X=135..230, Y=391..446)
    cx1, cx2, cy1, cy2 = 135.0, 230.0, 391.0, 446.0
    cz_w = z_eaves + cx1 * t_main - 2.0
    cz_e = z_eaves + cx2 * t_main - 2.0
    cz_t = 895.0
    sc.add_poly([(cx1, cy1, cz_w), (cx1, cy2, cz_w), (cx1, cy2, cz_t), (cx1, cy1, cz_t)], "#64748b", stroke="#1e293b", sw=1.5, layer=5)
    sc.add_poly([(cx1, cy2, cz_w), (cx2, cy2, cz_e), (cx2, cy2, cz_t), (cx1, cy2, cz_t)], "#475569", stroke="#1e293b", sw=1.5, layer=5)
    sc.add_poly([(cx1 - 5, cy1 - 5, cz_t), (cx2 + 5, cy1 - 5, cz_t), (cx2 + 5, cy2 + 5, cz_t), (cx1 - 5, cy2 + 5, cz_t)], "#334155", stroke="#0f172a", sw=1.4, layer=5)

    # West wing NORTH roof slope (facing viewer!)
    ov_w = 30.0
    z_w_ov = z_eaves - ov_w * t_wing
    sc.add_poly([
        (-west_d - 30, y_mid, z_wing_ridge),
        (x_stop, y_mid, z_wing_ridge),
        (0, y_n + ov_w, z_w_ov),
        (-west_d - 30, y_n + ov_w, z_w_ov),
    ], "#1e293b", stroke="#0f172a", sw=2.0, layer=5, ambient=0.55)
    sc.add_poly([(-west_d - 30, y_mid, z_wing_ridge), (-west_d - 30, y_n + ov_w, z_w_ov), (-west_d - 30, y_n + ov_w, z_w_ov + 14), (-west_d - 30, y_mid, z_wing_ridge + 14)],
                "#ffffff", stroke="#1e293b", sw=1.2, layer=6)

    # --- 1-STORY NORTH EXTENSION WITH PARALLEL 32.7° SALTAK (FOREGROUND HERO!) ---
    # World X = 231..866 (width 635 cm, ridge at X = 231 + 317.5 = 548.5, peak Z = 290 + 204 = 494 cm!)
    # Enclosed Utebod + Vindfang: X = 381..866, Y = 1166..1376
    # Covered Portico + Railing + 140/210 Entrance Door (facing WEST at X = 381!): X = 231..381, Y = 1166..1376
    nx_w = 231.0
    nx_door = 381.0
    nx_e = 866.0
    nx_mid = (nx_w + nx_e) / 2.0  # 548.5
    ny_n = 1376.0
    nz_eaves = 290.0
    nz_ridge = nz_eaves + 317.5 * t_main  # 494 cm (exact parallel 32.7°!)

    # Porch landing & plinth (X = 231..866, Y = 1166..1376)
    sc.add_poly([(nx_w, 1166, 0), (nx_e, 1166, 0), (nx_e, ny_n, 0), (nx_w, ny_n, 0)], "#94a3b8", layer=6)
    sc.add_poly([(nx_w, ny_n, 0), (nx_e, ny_n, 0), (nx_e, ny_n, 40), (nx_w, ny_n, 40)], "#64748b", stroke="#334155", sw=1.2, layer=6)
    sc.add_poly([(nx_w, 1166, 0), (nx_w, ny_n, 0), (nx_w, ny_n, 40), (nx_w, 1166, 40)], "#475569", stroke="#334155", sw=1.2, layer=6)
    sc.add_poly([(nx_w, 1166, 40), (nx_door, 1166, 40), (nx_door, ny_n, 40), (nx_w, ny_n, 40)], "#cbd5e1", stroke="#64748b", sw=1.1, layer=6)
    # Entry steps on the west side of the covered portico (leading up from driveway!)
    sc.add_poly([(nx_w - 45, 1185, 0), (nx_w, 1185, 0), (nx_w, 1345, 0), (nx_w - 45, 1345, 0)], "#94a3b8", layer=6)
    sc.add_poly([(nx_w - 45, 1185, 20), (nx_w, 1185, 20), (nx_w, 1345, 20), (nx_w - 45, 1345, 20)], "#cbd5e1", stroke="#64748b", sw=1.1, layer=6)

    # WEST WALL OF VINDFANG (X = 381, Y = 1166..1376) with VISIBLE 140/210 ENTRANCE DOOR!
    sc.add_poly([(nx_door, 1166, 40), (nx_door, ny_n, 40), (nx_door, ny_n, nz_eaves), (nx_door, 1166, nz_eaves)],
                "#f8fafc", stroke="#1e293b", sw=1.8, layer=7)
    # 140/210 Entrance Door (white paneled door + glass side-light!)
    sc.add_poly([(nx_door - 1.5, 1205, 42), (nx_door - 1.5, 1345, 42), (nx_door - 1.5, 1345, 252), (nx_door - 1.5, 1205, 252)],
                "#ffffff", stroke="#0f172a", sw=2.0, layer=7, auto_shade=False)
    # Main door leaf (1205..1300) + glass sidelight (1305..1342)
    sc.add_poly([(nx_door - 2.2, 1220, 155), (nx_door - 2.2, 1286, 155), (nx_door - 2.2, 1286, 236), (nx_door - 2.2, 1220, 236)],
                "#93c5fd", stroke="#334155", sw=1.2, layer=7, auto_shade=False)
    sc.add_poly([(nx_door - 2.2, 1306, 60), (nx_door - 2.2, 1338, 60), (nx_door - 2.2, 1338, 236), (nx_door - 2.2, 1306, 236)],
                "#bae6fd", stroke="#334155", sw=1.2, layer=7, auto_shade=False)
    # Warm wall lantern beside door
    sc.add_poly([(nx_door - 5, 1352, 185), (nx_door - 5, 1368, 185), (nx_door - 5, 1368, 212), (nx_door - 5, 1352, 212)],
                "#fbbf24", stroke="#92400e", sw=1.4, layer=7, auto_shade=False)

    # NORTH WALL OF ENCLOSED VINDFANG + UTEBOD (Y = 1376, X = 381..866)
    sc.add_poly([(nx_door, ny_n, 40), (nx_e, ny_n, 40), (nx_e, ny_n, nz_eaves), (nx_door, ny_n, nz_eaves)],
                "#ffffff", stroke="#1e293b", sw=2.0, layer=7)
    add_siding_north(sc, ny_n, nx_door, nx_e, 40, nz_eaves, layer=7)
    # Windows on north extension north wall (exact match to Magnus's sketch!)
    add_kors_north(sc, ny_n, 490, 625, 102, 242, single=False, layer=8)  # Vindfang double kors-sprosse
    add_kors_north(sc, ny_n, 710, 782, 108, 240, single=True, layer=8)   # Utebod narrow single window

    # Porch corner column + classic railing on NORTH side of portico (as sketched!)
    sc.add_poly([(nx_w, ny_n - 16, 40), (nx_w + 16, ny_n - 16, 40), (nx_w + 16, ny_n - 16, nz_eaves), (nx_w, ny_n - 16, nz_eaves)], "#ffffff", stroke="#334155", sw=1.4, layer=8)
    sc.add_poly([(nx_w, ny_n, 40), (nx_w + 16, ny_n, 40), (nx_w + 16, ny_n, nz_eaves), (nx_w, ny_n, nz_eaves)], "#f1f5f9", stroke="#334155", sw=1.4, layer=8)
    # Wooden railing across front (north) of portico (X = 247..381, Z = 50..135)
    sc.add_poly([(nx_w + 16, ny_n, 125), (nx_door, ny_n, 125), (nx_door, ny_n, 136), (nx_w + 16, ny_n, 136)], "#ffffff", stroke="#334155", sw=1.2, layer=8)
    sc.add_poly([(nx_w + 16, ny_n, 48), (nx_door, ny_n, 48), (nx_door, ny_n, 58), (nx_w + 16, ny_n, 58)], "#ffffff", stroke="#334155", sw=1.2, layer=8)
    for rx in range(262, 376, 18):
        sc.add_line((rx, ny_n + 1, 58), (rx, ny_n + 1, 125), stroke="#475569", sw=2.2, layer=8)

    # NORTH EXTENSION SALTAK GABLE TRIANGLE (Y = 1376, X = 231..866, peak at X = 548.5, Z = 494!)
    sc.add_poly([(nx_w, ny_n, nz_eaves), (nx_e, ny_n, nz_eaves), (nx_mid, ny_n, nz_ridge)],
                "#ffffff", stroke="#1e293b", sw=2.0, layer=8)
    # West roof slope of north extension saltak (facing viewer!)
    ov_n = 26.0
    z_n_ov = nz_eaves - ov_n * t_main
    sc.add_poly([
        (nx_w - ov_n, 1166, z_n_ov),
        (nx_w - ov_n, ny_n + 26, z_n_ov),
        (nx_mid, ny_n + 26, nz_ridge),
        (nx_mid, 1166, nz_ridge),
    ], "#1e293b", stroke="#0f172a", sw=2.0, layer=9, ambient=0.52)
    # White gable bargeboards on north extension saltak
    sc.add_poly([(nx_w - ov_n, ny_n + 26, z_n_ov), (nx_mid, ny_n + 26, nz_ridge), (nx_mid, ny_n + 26, nz_ridge + 14), (nx_w - ov_n, ny_n + 26, z_n_ov + 14)],
                "#ffffff", stroke="#1e293b", sw=1.2, layer=9)
    sc.add_poly([(nx_mid, ny_n + 26, nz_ridge), (nx_e + ov_n, ny_n + 26, z_n_ov), (nx_e + ov_n, ny_n + 26, z_n_ov + 14), (nx_mid, ny_n + 26, nz_ridge + 14)],
                "#e2e8f0", stroke="#1e293b", sw=1.2, layer=9)

    # Callouts cleanly positioned in clear space (sky/lawn/driveway)
    sc.add_text_at((nx_w - 60, 1340, 20), "Inngangsdør 140/210 (under portico)", dx=40, dy=42, size=18, weight="800", fill="#c2410c", anchor="start")
    sc.add_text_at((nx_mid, ny_n + 26, nz_ridge + 75), "32,7° parallelt saltak (nord-tilbygg)", dx=-45, dy=-12, size=17, weight="800", fill="#0f172a")
    sc.add_text_at((-west_d / 2, y_n + 40, 0), "3,30 m vest-tilbygg (dobbeltvinduer nord)", dy=52, size=17, weight="800", fill="#0369a1")
    sc.add_text_at((433, 1166, z_ridge + 42), "Ingen nordvindu på Hovedsov (bak gavlen)", dx=-180, dy=10, size=15, weight="700", fill="#475569", anchor="end")

    return sc.render()


def main():
    W, H = 1900, 1260
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'style="font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">',
        "<defs>",
        '  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">',
        '    <stop offset="0%" stop-color="#bae6fd"/>',
        '    <stop offset="68%" stop-color="#f0f9ff"/>',
        '    <stop offset="100%" stop-color="#fef3c7"/>',
        "  </linearGradient>",
        "</defs>",
        f'<rect width="{W}" height="{H}" fill="#f8fafc"/>',
        f'<rect x="0" y="0" width="{W}" height="125" fill="#0f172a"/>',
        f'<rect x="0" y="119" width="{W}" height="6" fill="#ea580c"/>',
        f'<text x="55" y="54" font-size="34" font-weight="800" fill="#ffffff">M6 (#50) — Eksakt 3D-perspektiv NORDVEST (synkronisert med nordfasade-skissen!)</text>',
        f'<text x="55" y="92" font-size="20" font-weight="500" fill="#cbd5e1">Viser 32,7° parallelt saltak på nord-tilbygg, synlig inngangsdør 140/210 under portico, rekkverk, ingen nordvindu på hovedsov og eksakt 3,30 m vest-tilbygg</text>',
        f'<rect x="40" y="150" width="{W - 80}" height="1070" fill="url(#sky)" stroke="#cbd5e1" stroke-width="2" rx="12"/>',
        f'<clipPath id="clipNW"><rect x="40" y="150" width="{W - 80}" height="1070" rx="12"/></clipPath>',
    ]

    # Pulled-back elevated NW 3/4 camera so full gable peak, north extension, steps & 3.30m west wing fit with clean margin!
    cam = Camera3D(pos=(-1780.0, 3080.0, 740.0), target=(220.0, 760.0, 380.0), fov_deg=35.0, cx=W / 2.0 + 30, cy=725.0, width=1760.0)
    svg.append('<g clip-path="url(#clipNW)">')
    svg.extend(build_nw_scene(cam))
    svg.append("</g>")
    svg.append("</svg>")

    out = os.path.join(OUT_DIR, "perspektiv_3d_nordvest_eksakt.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
