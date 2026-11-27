#!/usr/bin/env python3
"""
Generate clean, label-free 3D mathematical perspective reference images from ALL 4 CORNERS
(SW, NW, NE, SE) of Myrteveien 6 (Alternativ 1: 3,30m x 5,20m west cross-wing w/ 20° gable,
1-story north extension w/ parallel 32,7° saltak, 4x2 east kors-sprosse facade, NO north master window,
exact 95x55 cm chimney on west roof slope) to lock exact proportions for photorealistic rendering.
"""

import math
import os
import sys

sys.path.insert(0, "/home/kiro/repos/m6/scripts")
from generate_3d_perspektiv_eksakt import Camera3D, Scene3D

ART_DIR = "/home/kiro/.gemini/antigravity-cli/brain/505e5e3b-a643-4ed3-bd58-6302c2f77d03"


def add_kors_east(sc: Scene3D, x_wall, y1, y2, z1, z2, single=False, layer=3):
    x_out = x_wall + 1.5
    sc.add_poly([(x_out, y1 - 6, z1 - 6), (x_out, y2 + 6, z1 - 6), (x_out, y2 + 6, z2 + 6), (x_out, y1 - 6, z2 + 6)],
                "#ffffff", stroke="#475569", sw=1.0, layer=layer, auto_shade=False, depth_bias=-4.0)
    sc.add_poly([(x_out + 0.5, y1, z1), (x_out + 0.5, y2, z1), (x_out + 0.5, y2, z2), (x_out + 0.5, y1, z2)],
                "#475569", stroke="#1e293b", sw=1.3, layer=layer, auto_shade=False, depth_bias=-6.0)
    zm = z1 + (z2 - z1) * 0.66
    sc.add_poly([(x_out + 0.8, y1 + 2, zm), (x_out + 0.8, y2 - 2, zm), (x_out + 0.8, y2 - 2, z2 - 2), (x_out + 0.8, y1 + 2, z2 - 2)],
                "#bae6fd", stroke="none", sw=0, layer=layer, auto_shade=False, opacity=0.4, depth_bias=-7.0)
    sc.add_line((x_out + 1.2, y1, zm), (x_out + 1.2, y2, zm), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)
    if not single:
        ym = (y1 + y2) / 2.0
        sc.add_line((x_out + 1.2, ym, z1), (x_out + 1.2, ym, z2), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)


def add_kors_north(sc: Scene3D, y_wall, x1, x2, z1, z2, single=False, layer=3):
    y_out = y_wall + 1.5
    sc.add_poly([(x1 - 6, y_out, z1 - 6), (x2 + 6, y_out, z1 - 6), (x2 + 6, y_out, z2 + 6), (x1 - 6, y_out, z2 + 6)],
                "#ffffff", stroke="#475569", sw=1.0, layer=layer, auto_shade=False, depth_bias=-4.0)
    sc.add_poly([(x1, y_out + 0.5, z1), (x2, y_out + 0.5, z1), (x2, y_out + 0.5, z2), (x1, y_out + 0.5, z2)],
                "#475569", stroke="#1e293b", sw=1.3, layer=layer, auto_shade=False, depth_bias=-6.0)
    zm = z1 + (z2 - z1) * 0.66
    sc.add_poly([(x1 + 2, y_out + 0.8, zm), (x2 - 2, y_out + 0.8, zm), (x2 - 2, y_out + 0.8, z2 - 2), (x1 + 2, y_out + 0.8, z2 - 2)],
                "#bae6fd", stroke="none", sw=0, layer=layer, auto_shade=False, opacity=0.4, depth_bias=-7.0)
    sc.add_line((x1, y_out + 1.2, zm), (x2, y_out + 1.2, zm), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)
    if not single:
        xm = (x1 + x2) / 2.0
        sc.add_line((xm, y_out + 1.2, z1), (xm, y_out + 1.2, z2), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)


def build_ne_ref():
    """Northeast 3/4 exact 3D model (East 4x2 facade + North gable w/ parallel 32.7° saltak & NO north master window)."""
    W, H = 1400, 940
    cam = Camera3D(pos=(2480.0, 2760.0, 720.0), target=(440.0, 720.0, 360.0), fov_deg=35.0, cx=W / 2.0, cy=H * 0.54, width=W)
    sc = Scene3D(cam)
    sc.sun = (0.72, 0.45, 0.52)
    t_main = math.tan(math.radians(32.7))
    z_eaves = 610.0
    z_ridge = z_eaves + 433.0 * t_main

    # Ground + gravel north
    sc.add_poly([(-500, -400, 0), (1600, -400, 0), (1600, 2100, 0), (-500, 2100, 0)], "#bbf7d0", stroke="none", sw=0, layer=0, auto_shade=False)
    sc.add_poly([(-300, 1250, 1), (1500, 1250, 1), (1500, 2100, 1), (-300, 2100, 1)], "#d6d3d1", stroke="none", sw=0, layer=0, auto_shade=False)

    # Subtle glimpse of west extension behind NW corner (X=-330..0, Y=236..756)
    sc.add_poly([(-330, 756, 40), (0, 756, 40), (0, 756, z_eaves), (-330, 756, z_eaves)], "#f1f5f9", stroke="#334155", sw=1.4, layer=1)
    add_kors_north(sc, 756, -230, -95, 385, 530, layer=1)

    # Chimney top peeking behind ridge (X=135..230, Y=391..446, Z_top=905)
    sc.add_poly([(230, 391, 800), (230, 446, 800), (230, 446, 905), (230, 391, 905)], "#475569", stroke="#1e293b", sw=1.4, layer=1)
    sc.add_poly([(135, 446, 800), (230, 446, 800), (230, 446, 905), (135, 446, 905)], "#64748b", stroke="#1e293b", sw=1.4, layer=1)

    # Main EAST wall + 1-story NORTH EXTENSION east wall as ONE 100% FLUSH CONTINUOUS UNBROKEN PLANE (X=866, Y=0..1376)!
    nx_w, nx_door, nx_e = 231.0, 381.0, 866.0
    nx_mid = (nx_w + nx_e) / 2.0
    ny_n, nz_eaves = 1376.0, 290.0
    nz_ridge = nz_eaves + 317.5 * t_main  # 494 cm!
    # Continuous concrete plinth from south corner (Y=0) all the way to north-extension corner (Y=1376) — ZERO step!
    sc.add_poly([(866, 0, 0), (866, ny_n, 0), (866, ny_n, 40), (866, 0, 40)], "#64748b", stroke="#334155", sw=1.4, layer=2)
    # Continuous L-shaped white east facade plane (Y=0..1376 flush at X=866!) — ZERO vertical seam at Y=1166!
    sc.add_poly([
        (866, 0, 40), (866, ny_n, 40), (866, ny_n, nz_eaves),
        (866, 1166, nz_eaves), (866, 1166, z_eaves), (866, 0, z_eaves)
    ], "#ffffff", stroke="#1e293b", sw=1.8, layer=2)
    # Continuous horizontal siding lines running unbroken across Y=0..1376 (below Z=290) and Y=0..1166 (above Z=290)
    for sz in range(68, int(z_eaves) - 6, 28):
        y_end = ny_n if sz < nz_eaves - 4 else 1166.0
        sc.add_line((866.4, 0, sz), (866.4, y_end, sz), stroke="#cbd5e1", sw=0.65, layer=2, depth_bias=-2.0, opacity=0.65)
    # 4 clean vertical kors-sprosse axes on EAST wall (Y = 176, 456, 671, 946) — Bad 2.etg (609..671) flush w/ south edge!
    for cy in [176, 456, 671, 946]:
        add_kors_east(sc, 866, cy - 62, cy + 62, 105, 250, layer=3)
        if cy == 671:
            add_kors_east(sc, 866, cy - 62, cy, 385, 530, single=True, layer=3)
        else:
            add_kors_east(sc, 866, cy - 62, cy + 62, 385, 530, layer=3)
    # SINGLE centered 110/210 door on the FLUSH east wall of north extension (Y=1222..1320)
    sc.add_poly([(nx_e + 1.5, 1222, 42), (nx_e + 1.5, 1320, 42), (nx_e + 1.5, 1320, 248), (nx_e + 1.5, 1222, 248)], "#f8fafc", stroke="#334155", sw=1.6, layer=3, auto_shade=False)
    sc.add_poly([(nx_e + 2.0, 1236, 155), (nx_e + 2.0, 1306, 155), (nx_e + 2.0, 1306, 232), (nx_e + 2.0, 1236, 232)], "#bae6fd", stroke="#475569", sw=1.0, layer=3, auto_shade=False)

    # Main NORTH gable (Y=1166, X=0..866)
    sc.add_poly([(0, 1166, 0), (866, 1166, 0), (866, 1166, 40), (0, 1166, 40)], "#64748b", layer=2)
    sc.add_poly([(0, 1166, 40), (866, 1166, 40), (866, 1166, z_eaves), (433, 1166, z_ridge), (0, 1166, z_eaves)], "#ffffff", stroke="#1e293b", sw=1.8, layer=2)
    # NO north bedroom window on east/left! 1.etg half 62 cm (128..190) flush w/ west edge & center mullion of 2.etg full 124 cm (128..252) + attic centered!
    add_kors_north(sc, 1166, 128, 190, 103, 248, single=True, layer=3)
    add_kors_north(sc, 1166, 128, 252, 383, 528, single=False, layer=3)
    add_kors_north(sc, 1166, 375, 491, 655, 770, single=False, layer=3)

    # Main EAST roof slope (with 4 skylights aligned directly over the 4 vertical east window axes!)
    ov_x = 866.0 + 35.0
    z_ov = z_eaves - 35.0 * t_main
    sc.add_poly([(433, -35, z_ridge), (433, 1201, z_ridge), (ov_x, 1201, z_ov), (ov_x, -35, z_ov)], "#1e293b", stroke="#0f172a", sw=2.0, layer=4)
    for sy in [176, 456, 671, 946]:
        xa, xb = 530.0, 645.0
        za = z_ridge - (xa - 433.0) * t_main + 3.0
        zb = z_ridge - (xb - 433.0) * t_main + 3.0
        sc.add_poly([(xa, sy - 55, za), (xa, sy + 55, za), (xb, sy + 55, zb), (xb, sy - 55, zb)], "#7dd3fc", stroke="#0f172a", sw=1.8, layer=5, auto_shade=False)

    # 1-STORY NORTH EXTENSION (X=231..866, Y=1166..1376) north wall + portico + PARALLEL 32.7° SALTAK!
    # North wall of enclosed Utebod + Vindfang
    sc.add_poly([(nx_door, ny_n, 0), (nx_e, ny_n, 0), (nx_e, ny_n, 40), (nx_door, ny_n, 40)], "#64748b", layer=6)
    sc.add_poly([(nx_door, ny_n, 40), (nx_e, ny_n, 40), (nx_e, ny_n, nz_eaves), (nx_door, ny_n, nz_eaves)], "#ffffff", stroke="#1e293b", sw=1.8, layer=6)
    add_kors_north(sc, ny_n, 490, 625, 102, 242, single=False, layer=7)
    add_kors_north(sc, ny_n, 710, 782, 108, 240, single=True, layer=7)
    # Portico + railing on right (west) side of north extension
    sc.add_poly([(nx_w, ny_n, 0), (nx_door, ny_n, 0), (nx_door, ny_n, 40), (nx_w, ny_n, 40)], "#94a3b8", layer=6)
    sc.add_poly([(nx_w, ny_n, 40), (nx_w + 16, ny_n, 40), (nx_w + 16, ny_n, nz_eaves), (nx_w, ny_n, nz_eaves)], "#ffffff", stroke="#334155", sw=1.3, layer=7)
    sc.add_poly([(nx_w + 16, ny_n, 125), (nx_door, ny_n, 125), (nx_door, ny_n, 136), (nx_w + 16, ny_n, 136)], "#ffffff", stroke="#334155", sw=1.2, layer=7)
    for rx in range(262, 376, 20):
        sc.add_line((rx, ny_n + 1, 52), (rx, ny_n + 1, 125), stroke="#475569", sw=2.0, layer=7)
    # Parallel 32.7° saltak gable triangle + EAST roof slope
    sc.add_poly([(nx_w, ny_n, nz_eaves), (nx_e, ny_n, nz_eaves), (nx_mid, ny_n, nz_ridge)], "#ffffff", stroke="#1e293b", sw=1.8, layer=7)
    ov_n = 26.0
    z_n_ov = nz_eaves - ov_n * t_main
    sc.add_poly([(nx_mid, 1166, nz_ridge), (nx_mid, ny_n + 26, nz_ridge), (nx_e + ov_n, ny_n + 26, z_n_ov), (nx_e + ov_n, 1166, z_n_ov)],
                "#1e293b", stroke="#0f172a", sw=2.0, layer=8)

    save_svg(os.path.join(ART_DIR, "ref_3d_ne_alt1.svg"), W, H, sc.render())


def build_se_ref():
    """Southeast 3/4 exact 3D model (Clean 1947 south gable w/ timber deck + 4x2 East facade w/ 3 skylights + North ext right)."""
    W, H = 1400, 940
    cam = Camera3D(pos=(2320.0, -1520.0, 740.0), target=(430.0, 560.0, 380.0), fov_deg=35.0, cx=W / 2.0, cy=H * 0.56, width=W)
    sc = Scene3D(cam)
    sc.sun = (0.55, -0.65, 0.52)
    t_main = math.tan(math.radians(32.7))
    z_eaves = 610.0
    z_ridge = z_eaves + 433.0 * t_main

    sc.add_poly([(-600, -600, 0), (1600, -600, 0), (1600, 1900, 0), (-600, 1900, 0)], "#bbf7d0", stroke="none", sw=0, layer=0, auto_shade=False)
    # South timber terrace deck
    sc.add_poly([(320, -240, 22), (910, -240, 22), (910, 0, 22), (320, 0, 22)], "#d6b084", stroke="#92400e", sw=1.3, layer=1)
    sc.add_poly([(320, -240, 0), (910, -240, 0), (910, -240, 22), (320, -240, 22)], "#a88358", stroke="#78350f", sw=1.1, layer=1)
    sc.add_poly([(910, -240, 0), (910, 0, 0), (910, 0, 22), (910, -240, 22)], "#b48f64", stroke="#78350f", sw=1.1, layer=1)

    # Subtle glimpse of 3.30m west extension behind SW corner (X=-330..0, Y=236)
    sc.add_poly([(-330, 236, 40), (0, 236, 40), (0, 236, z_eaves), (-330, 236, z_eaves)], "#f1f5f9", stroke="#334155", sw=1.4, layer=1)
    sc.add_kors_window_south(236, -230, -95, 105, 250, layer=1)
    sc.add_kors_window_south(236, -230, -95, 385, 530, layer=1)

    # Chimney peeking slightly behind main ridge
    sc.add_poly([(230, 391, 810), (230, 446, 810), (230, 446, 905), (230, 391, 905)], "#475569", stroke="#1e293b", sw=1.4, layer=1)
    sc.add_poly([(135, 391, 810), (230, 391, 810), (230, 391, 905), (135, 391, 905)], "#64748b", stroke="#1e293b", sw=1.4, layer=1)

    # 1-story north extension roof (X=548.5..892, Y=1166..1396, parallel 32.7° saltak!) — layer=2 so it sits BEHIND the main east wall!
    nz_eaves = 290.0
    nz_ridge = nz_eaves + 317.5 * t_main
    sc.add_poly([(548.5, 1166, nz_ridge), (548.5, 1396, nz_ridge), (892, 1396, nz_eaves - 26 * t_main), (892, 1166, nz_eaves - 26 * t_main)],
                "#1e293b", stroke="#0f172a", sw=1.8, layer=2)
    # Visible roof overhang strip protruding past X=866 (X=866..892, Y=1166..1396) on layer=5
    sc.add_poly([(866, 1166, nz_eaves), (866, 1396, nz_eaves), (892, 1396, nz_eaves - 26 * t_main), (892, 1166, nz_eaves - 26 * t_main)],
                "#1e293b", stroke="#0f172a", sw=1.8, layer=5)

    # Main SOUTH GABLE (Y=0, X=0..866) — 100% SYMMETRIC around EXISTING centered veranda doors (x=353..513 in 1st & 2nd)!
    sc.add_poly([(0, 0, 0), (866, 0, 0), (866, 0, 40), (0, 0, 40)], "#64748b", layer=3)
    sc.add_poly([(0, 0, 40), (866, 0, 40), (866, 0, z_eaves), (433, 0, z_ridge), (0, 0, z_eaves)], "#ffffff", stroke="#1e293b", sw=2.0, layer=3)
    sc.add_kors_window_south(0, 105, 235, 105, 250, layer=4)
    sc.add_kors_window_south(0, 353, 513, 42, 252, is_door=True, layer=4)
    sc.add_kors_window_south(0, 631, 761, 105, 250, layer=4)
    sc.add_kors_window_south(0, 105, 235, 385, 530, layer=4)
    sc.add_kors_window_south(0, 353, 513, 322, 532, is_door=True, layer=4)
    sc.add_line((346, -6, 425), (520, -6, 425), stroke="#0f172a", sw=2.4, layer=5, depth_bias=-12.0)
    sc.add_line((346, -6, 326), (520, -6, 326), stroke="#0f172a", sw=1.8, layer=5, depth_bias=-12.0)
    for rx in range(356, 516, 24):
        sc.add_line((rx, -6, 326), (rx, -6, 425), stroke="#1e293b", sw=1.3, layer=5, depth_bias=-12.0)
    sc.add_kors_window_south(0, 631, 761, 385, 530, layer=4)
    sc.add_kors_window_south(0, 375, 491, 655, 770, layer=4)

    # Main EAST WALL + 1-story NORTH EXTENSION east wall as ONE 100% FLUSH CONTINUOUS UNBROKEN PLANE (X=866, Y=0..1376)!
    sc.add_poly([(866, 0, 0), (866, 1376, 0), (866, 1376, 40), (866, 0, 40)], "#64748b", stroke="#334155", sw=1.4, layer=3)
    sc.add_poly([
        (866, 0, 40), (866, 1376, 40), (866, 1376, nz_eaves),
        (866, 1166, nz_eaves), (866, 1166, z_eaves), (866, 0, z_eaves)
    ], "#f8fafc", stroke="#1e293b", sw=2.0, layer=3)
    for sz in range(68, int(z_eaves) - 6, 28):
        y_end = 1376.0 if sz < nz_eaves - 4 else 1166.0
        sc.add_line((866.4, 0, sz), (866.4, y_end, sz), stroke="#cbd5e1", sw=0.65, layer=3, depth_bias=-2.0, opacity=0.65)
    for cy in [176, 456, 671, 946]:
        add_kors_east(sc, 866, cy - 62, cy + 62, 105, 250, layer=4)
        if cy == 671:
            add_kors_east(sc, 866, cy - 62, cy, 385, 530, single=True, layer=4)
        else:
            add_kors_east(sc, 866, cy - 62, cy + 62, 385, 530, layer=4)
    sc.add_poly([(866 + 1.5, 1222, 42), (866 + 1.5, 1320, 42), (866 + 1.5, 1320, 248), (866 + 1.5, 1222, 248)], "#f8fafc", stroke="#334155", sw=1.5, layer=4, auto_shade=False)
    sc.add_poly([(866 + 2.0, 1236, 155), (866 + 2.0, 1306, 155), (866 + 2.0, 1306, 232), (866 + 2.0, 1236, 232)], "#bae6fd", stroke="#475569", sw=1.0, layer=4, auto_shade=False)

    # Main EAST roof slope (with 4 skylights aligned directly over the 4 vertical east window axes!)
    ov_x = 866.0 + 35.0
    z_ov = z_eaves - 35.0 * t_main
    sc.add_poly([(433, -35, z_ridge), (433, 1201, z_ridge), (ov_x, 1201, z_ov), (ov_x, -35, z_ov)], "#1e293b", stroke="#0f172a", sw=2.0, layer=5)
    for sy in [176, 456, 671, 946]:
        xa, xb = 530.0, 645.0
        za = z_ridge - (xa - 433.0) * t_main + 3.0
        zb = z_ridge - (xb - 433.0) * t_main + 3.0
        sc.add_poly([(xa, sy - 55, za), (xa, sy + 55, za), (xb, sy + 55, zb), (xb, sy - 55, zb)], "#7dd3fc", stroke="#0f172a", sw=1.8, layer=6, auto_shade=False)

    save_svg(os.path.join(ART_DIR, "ref_3d_se_alt1.svg"), W, H, sc.render())


def save_svg(path, W, H, els):
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        f'<rect width="{W}" height="{H}" fill="#e0f2fe"/>',
        *els,
        "</svg>",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print("Wrote", path)


if __name__ == "__main__":
    build_ne_ref()
    build_se_ref()
