#!/usr/bin/env python3
"""
Exact 3D mathematical perspective projection from NORTHEAST (and close-up EAST/SE) of
Myrteveien 6 — Alternativ 2 (Catrine/Magnus):
  - 100% FLUSH continuous east wall + foundation (X=866, Y=0..1416, ZERO step or seam!)
  - 2,50 m deep 1-story north extension (6 m² Vindfang + 6 m² Vaskerom, blank flush east wall, parallel 32,7° saltak)
  - External 3,65 m east-wall basement stair (Y=1106 -> 741, entering south end of U.04):
      * 3 open top steps (Y=1106..1031) with concrete stairwell curb & sleek black handrail
      * Low horizontal 12° east-sloping roof (Y=1031..741, Z=186 -> 161 cm) parallel to horizontal siding
      * Cleanly BELOW upper-third Bad 1. etg window (124x50 cm, Z=198..248)
      * Stops 8 cm NORTH of Sov/Pult 1. etg window (Y=609..733)
  - Narrow half-width Bad 2. etg window (Y=609..671) aligned flush w/ south edge & center mullion of 1. etg
  - Aligned north Trapp windows (1. etg 62 cm at X=128..190 flush w/ 2. etg 124 cm at X=128..252)
  - 4 aligned east roof skylights & NO north window in Hovedsoverom
"""

import math
import os
import sys

sys.path.insert(0, "/home/kiro/repos/m6/scripts")
from generate_3d_perspektiv_eksakt import Camera3D, Scene3D, esc
from generate_all4_3d_refs import add_kors_east, add_kors_north

OUT_DIR = "/home/kiro/repos/m6/assets/images/drawings"
ART_DIR = "/home/kiro/.gemini/antigravity-cli/brain/505e5e3b-a643-4ed3-bd58-6302c2f77d03"


def add_top_third_east(sc: Scene3D, x_wall, y1, y2, z1, z2, layer=3):
    """Upper-third (øvre 1/3) 2-pane horizontal window (124 x 50 cm) on east wall (X = x_wall)."""
    x_out = x_wall + 1.5
    sc.add_poly([(x_out, y1 - 6, z1 - 6), (x_out, y2 + 6, z1 - 6), (x_out, y2 + 6, z2 + 6), (x_out, y1 - 6, z2 + 6)],
                "#ffffff", stroke="#475569", sw=1.0, layer=layer, auto_shade=False, depth_bias=-4.0)
    sc.add_poly([(x_out + 0.5, y1, z1), (x_out + 0.5, y2, z1), (x_out + 0.5, y2, z2), (x_out + 0.5, y1, z2)],
                "#475569", stroke="#1e293b", sw=1.3, layer=layer, auto_shade=False, depth_bias=-6.0)
    sc.add_poly([(x_out + 0.8, y1 + 2, z1 + 2), (x_out + 0.8, y2 - 2, z1 + 2), (x_out + 0.8, y2 - 2, z2 - 2), (x_out + 0.8, y1 + 2, z2 - 2)],
                "#bae6fd", stroke="none", sw=0, layer=layer, auto_shade=False, opacity=0.45, depth_bias=-7.0)
    ym = (y1 + y2) / 2.0
    sc.add_line((x_out + 1.2, ym, z1), (x_out + 1.2, ym, z2), stroke="#ffffff", sw=2.6, layer=layer, depth_bias=-9.0)


def build_alt2_ne_scene(cam: Camera3D, with_labels=True, view="ne"):
    sc = Scene3D(cam)
    sc.sun = (0.72, 0.45, 0.52) if view == "ne" else (0.62, -0.52, 0.58)
    t_main = math.tan(math.radians(32.7))
    t_stair = math.tan(math.radians(12.0))
    z_eaves = 610.0
    z_ridge = z_eaves + 433.0 * t_main  # 888 cm

    # Ground lawn + gravel driveway north
    sc.add_poly([(-500, -450, 0), (1850, -450, 0), (1850, 2300, 0), (-500, 2300, 0)],
                "#bbf7d0", stroke="none", sw=0, layer=0, auto_shade=False)
    sc.add_poly([(-350, 1280, 1), (1650, 1280, 1), (1650, 2300, 1), (-350, 2300, 1)],
                "#d6d3d1", stroke="#a8a29e", sw=1.0, layer=0, auto_shade=False)

    # Subtle glimpse of Alt 2 west cross-wing behind NW/SW corner (X=-230..0, Y=344..846)
    if view == "ne":
        sc.add_poly([(-230, 846, 40), (0, 846, 40), (0, 846, z_eaves), (-230, 846, z_eaves)], "#f1f5f9", stroke="#334155", sw=1.3, layer=1)
    else:
        sc.add_poly([(-230, 344, 40), (0, 344, 40), (0, 344, z_eaves), (-230, 344, z_eaves)], "#f1f5f9", stroke="#334155", sw=1.3, layer=1)
        # South timber deck (visible in SE view)
        sc.add_poly([(320, -240, 22), (910, -240, 22), (910, 0, 22), (320, 0, 22)], "#d6b084", stroke="#92400e", sw=1.2, layer=1)
        sc.add_poly([(320, -240, 0), (910, -240, 0), (910, -240, 22), (320, -240, 22)], "#a88358", stroke="#78350f", sw=1.0, layer=1)
        sc.add_poly([(910, -240, 0), (910, 0, 0), (910, 0, 22), (910, -240, 22)], "#b48f64", stroke="#78350f", sw=1.0, layer=1)

    # Chimney top peeking behind ridge (X=135..230, Y=391..446, Z_top=905)
    sc.add_poly([(230, 391, 800), (230, 446, 800), (230, 446, 905), (230, 391, 905)], "#475569", stroke="#1e293b", sw=1.4, layer=1)
    if view == "ne":
        sc.add_poly([(135, 446, 800), (230, 446, 800), (230, 446, 905), (135, 446, 905)], "#64748b", stroke="#1e293b", sw=1.4, layer=1)
    else:
        sc.add_poly([(135, 391, 800), (230, 391, 800), (230, 391, 905), (135, 391, 905)], "#64748b", stroke="#1e293b", sw=1.4, layer=1)

    # --- 100% FLUSH CONTINUOUS EAST WALL + 2,50 m NORTH EXTENSION (X=866, Y=0..1416) ---
    nx_w, nx_door, nx_e = 231.0, 381.0, 866.0
    nx_mid = (nx_w + nx_e) / 2.0  # 548.5
    ny_n = 1166.0 + 250.0         # 1416 cm (2,50 m north extension!)
    nz_eaves = 290.0
    nz_ridge = nz_eaves + 317.5 * t_main  # 494 cm

    # In SE view, north extension roof slope goes behind the main east wall (layer=2)
    ov_n = 26.0
    z_n_ov = nz_eaves - ov_n * t_main
    if view == "se":
        sc.add_poly([(nx_mid, 1166, nz_ridge), (nx_mid, ny_n + 26, nz_ridge), (nx_e + ov_n, ny_n + 26, z_n_ov), (nx_e + ov_n, 1166, z_n_ov)],
                    "#1e293b", stroke="#0f172a", sw=1.8, layer=2)

    # Continuous concrete plinth (Y=0..1416 — ZERO step!)
    sc.add_poly([(866, 0, 0), (866, ny_n, 0), (866, ny_n, 40), (866, 0, 40)], "#64748b", stroke="#334155", sw=1.4, layer=3)
    # Continuous L-shaped white east wall (Y=0..1416 — ZERO vertical seam!)
    sc.add_poly([
        (866, 0, 40), (866, ny_n, 40), (866, ny_n, nz_eaves),
        (866, 1166, nz_eaves), (866, 1166, z_eaves), (866, 0, z_eaves)
    ], "#ffffff", stroke="#1e293b", sw=1.8, layer=3)
    # Unbroken horizontal siding lines across entire flush east wall
    for sz in range(68, int(z_eaves) - 6, 28):
        y_end = ny_n if sz < nz_eaves - 4 else 1166.0
        sc.add_line((866.4, 0, sz), (866.4, y_end, sz), stroke="#cbd5e1", sw=0.65, layer=3, depth_bias=-2.0, opacity=0.65)

    # 4 clean vertical window axes on EAST wall (Alt 2: Bad 1.etg = upper-third 124x50 cm ABOVE stair roof, Bad 2.etg = narrow 62x145 cm!)
    for cy in [176, 456, 671, 946]:
        if cy == 946:
            # Upper-third Bad 1.etg window (Z = 198..248 cm) cleanly above the 12° stair roof (Z = 186)!
            add_top_third_east(sc, 866, cy - 62, cy + 62, 198, 248, layer=4)
        else:
            add_kors_east(sc, 866, cy - 62, cy + 62, 103, 248, layer=4)
        if cy == 671:
            # Narrow 62 cm Bad 2.etg window flushed w/ south edge (609..671)!
            add_kors_east(sc, 866, cy - 62, cy, 383, 528, single=True, layer=4)
        else:
            add_kors_east(sc, 866, cy - 62, cy + 62, 383, 528, layer=4)

    # Main NORTH gable (NE view) OR Main SOUTH gable (SE view)
    if view == "ne":
        sc.add_poly([(0, 1166, 0), (866, 1166, 0), (866, 1166, 40), (0, 1166, 40)], "#64748b", layer=3)
        sc.add_poly([(0, 1166, 40), (866, 1166, 40), (866, 1166, z_eaves), (433, 1166, z_ridge), (0, 1166, z_eaves)], "#ffffff", stroke="#1e293b", sw=1.8, layer=3)
        add_kors_north(sc, 1166, 128, 190, 103, 248, single=True, layer=4)
        add_kors_north(sc, 1166, 128, 252, 383, 528, single=False, layer=4)
        add_kors_north(sc, 1166, 375, 491, 655, 770, single=False, layer=4)
    else:
        sc.add_poly([(0, 0, 0), (866, 0, 0), (866, 0, 40), (0, 0, 40)], "#64748b", layer=3)
        sc.add_poly([(0, 0, 40), (866, 0, 40), (866, 0, z_eaves), (433, 0, z_ridge), (0, 0, z_eaves)], "#ffffff", stroke="#1e293b", sw=1.8, layer=3)
        sc.add_kors_window_south(0, 105, 235, 103, 248, layer=4)
        sc.add_kors_window_south(0, 353, 513, 42, 252, is_door=True, layer=4)
        sc.add_kors_window_south(0, 631, 761, 103, 248, layer=4)
        sc.add_kors_window_south(0, 105, 235, 383, 528, layer=4)
        sc.add_kors_window_south(0, 353, 513, 322, 532, is_door=True, layer=4)
        sc.add_line((346, -6, 425), (520, -6, 425), stroke="#0f172a", sw=2.2, layer=5, depth_bias=-12.0)
        sc.add_line((346, -6, 326), (520, -6, 326), stroke="#0f172a", sw=1.6, layer=5, depth_bias=-12.0)
        for rx in range(356, 516, 24):
            sc.add_line((rx, -6, 326), (rx, -6, 425), stroke="#1e293b", sw=1.2, layer=5, depth_bias=-12.0)
        sc.add_kors_window_south(0, 631, 761, 383, 528, layer=4)
        sc.add_kors_window_south(0, 375, 491, 655, 770, layer=4)

    # Main EAST roof slope + 4 aligned skylights
    ov_x = 866.0 + 35.0
    z_ov = z_eaves - 35.0 * t_main
    sc.add_poly([(433, -35, z_ridge), (433, 1201, z_ridge), (ov_x, 1201, z_ov), (ov_x, -35, z_ov)], "#1e293b", stroke="#0f172a", sw=2.0, layer=5)
    for sy in [176, 456, 671, 946]:
        xa, xb = 530.0, 645.0
        za = z_ridge - (xa - 433.0) * t_main + 3.0
        zb = z_ridge - (xb - 433.0) * t_main + 3.0
        sc.add_poly([(xa, sy - 55, za), (xa, sy + 55, za), (xb, sy + 55, zb), (xb, sy - 55, zb)], "#7dd3fc", stroke="#0f172a", sw=1.8, layer=6, auto_shade=False)

    # --- 1-STORY NORTH EXTENSION (2,50 m deep, Y=1166..1416, Vaskerom + Vindfang + Portico) ---
    if view == "ne":
        sc.add_poly([(nx_door, ny_n, 0), (nx_e, ny_n, 0), (nx_e, ny_n, 40), (nx_door, ny_n, 40)], "#64748b", layer=6)
        sc.add_poly([(nx_door, ny_n, 40), (nx_e, ny_n, 40), (nx_e, ny_n, nz_eaves), (nx_door, ny_n, nz_eaves)], "#ffffff", stroke="#1e293b", sw=1.8, layer=6)
        add_kors_north(sc, ny_n, 490, 625, 102, 242, single=False, layer=7)  # Vindfang full
        add_kors_north(sc, ny_n, 710, 782, 108, 240, single=True, layer=7)   # Vaskerom half
        # Portico + railing
        sc.add_poly([(nx_w, ny_n, 0), (nx_door, ny_n, 0), (nx_door, ny_n, 40), (nx_w, ny_n, 40)], "#94a3b8", layer=6)
        sc.add_poly([(nx_w, ny_n, 40), (nx_w + 16, ny_n, 40), (nx_w + 16, ny_n, nz_eaves), (nx_w, ny_n, nz_eaves)], "#ffffff", stroke="#334155", sw=1.3, layer=7)
        sc.add_poly([(nx_w + 16, ny_n, 125), (nx_door, ny_n, 125), (nx_door, ny_n, 136), (nx_w + 16, ny_n, 136)], "#ffffff", stroke="#334155", sw=1.2, layer=7)
        for rx in range(262, 376, 20):
            sc.add_line((rx, ny_n + 1, 52), (rx, ny_n + 1, 125), stroke="#475569", sw=2.0, layer=7)
        # Parallel 32,7° saltak gable + east roof slope
        sc.add_poly([(nx_w, ny_n, nz_eaves), (nx_e, ny_n, nz_eaves), (nx_mid, ny_n, nz_ridge)], "#ffffff", stroke="#1e293b", sw=1.8, layer=7)
        sc.add_poly([(nx_mid, 1166, nz_ridge), (nx_mid, ny_n + 26, nz_ridge), (nx_e + ov_n, ny_n + 26, z_n_ov), (nx_e + ov_n, 1166, z_n_ov)],
                    "#1e293b", stroke="#0f172a", sw=2.0, layer=8)
    else:
        # Visible roof overhang strip protruding past X=866 in SE view
        sc.add_poly([(866, 1166, nz_eaves), (866, ny_n + 26, nz_eaves), (866 + ov_n, ny_n + 26, z_n_ov), (866 + ov_n, 1166, z_n_ov)],
                    "#1e293b", stroke="#0f172a", sw=1.8, layer=5)

    # =========================================================================
    # HERO ELEMENT: ALT 2 EXTERNAL EAST-WALL BASEMENT STAIR + LOW 12° ROOF!
    # Y_world = 1106 (north entry) -> 741 (south end entering U.04, 8 cm clear of Sov/Pult 609..733!)
    # Top 3 steps OPEN (Y = 1106..1031), low horizontal 12° east-sloping roof (Y = 1031..741)!
    # =========================================================================
    sy_top = 1106.0      # Start of stair (60 cm south of main north wall Y=1166)
    sy_roof_n = 1031.0   # Roof begins after 3 open steps (75 cm run!)
    sy_bot = 741.0       # End of stair / bottom landing (8 cm north of Sov/Pult window 733!)
    sx_in = 866.0        # Flush against house east wall
    sx_out = 981.0       # Outer east concrete stairwell wall (1,15 m wide)
    sx_roof = 994.0      # Roof outer eave (1,28 m wide incl. subtle overhang)
    z_roof_in = 186.0    # 12 cm cleanly BELOW upper-third Bad 1.etg window (Z=198..248)!
    z_roof_out = z_roof_in - (sx_roof - sx_in) * t_stair  # 186 - 128*0.2126 = 158.8 cm!
    z_wall_h = 58.0      # Low protective concrete parapet wall along stairwell east & south

    # 1. Dark recessed stairwell pit & descending concrete steps (Y = 1106 -> 741)
    # Pit shadow floor inside curb
    sc.add_poly([(sx_in + 2, sy_bot, 2), (sx_out - 12, sy_bot, 2), (sx_out - 12, sy_top, 2), (sx_in + 2, sy_top, 2)],
                "#334155", stroke="#1e293b", sw=1.0, layer=7, auto_shade=False)
    # Visible descending concrete steps (3 open steps near top + descending steps into shadow!)
    for i in range(9):
        ya = sy_top - i * 26.0
        yb = ya - 26.0
        # Slight visual drop tone to read clearly as descending steps
        shade = "#e2e8f0" if i < 3 else ("#cbd5e1" if i < 6 else "#94a3b8")
        zt = max(2.0, 14.0 - i * 1.4)
        sc.add_poly([(sx_in + 4, yb, zt), (sx_out - 14, yb, zt), (sx_out - 14, ya, zt), (sx_in + 4, ya, zt)],
                    shade, stroke="#475569", sw=0.9, layer=7, auto_shade=False)

    # 2. Low concrete stairwell curb / side wall (east side X = sx_out, Y = sy_bot..sy_top, Z = 0..z_wall_h)
    # Inner face of east curb (visible from NE/SE)
    sc.add_poly([(sx_out - 12, sy_bot, 0), (sx_out - 12, sy_top, 0), (sx_out - 12, sy_top, z_wall_h), (sx_out - 12, sy_bot, z_wall_h)],
                "#94a3b8", stroke="#475569", sw=1.0, layer=8)
    # Outer face of east curb (X = sx_out)
    sc.add_poly([(sx_out, sy_bot, 0), (sx_out, sy_top, 0), (sx_out, sy_top, z_wall_h), (sx_out, sy_bot, z_wall_h)],
                "#64748b", stroke="#334155", sw=1.4, layer=8)
    # Top cap of east curb
    sc.add_poly([(sx_out - 12, sy_bot, z_wall_h), (sx_out, sy_bot, z_wall_h), (sx_out, sy_top, z_wall_h), (sx_out - 12, sy_top, z_wall_h)],
                "#cbd5e1", stroke="#475569", sw=1.1, layer=8)
    # Closed white wood/concrete SOUTH end wall of stairwell enclosure (Y = sy_bot, X = 866..981, Z = 0..roof!)
    z_roof_at_wall = z_roof_in - (sx_out - sx_in) * t_stair
    sc.add_poly([(sx_in, sy_bot, 0), (sx_out, sy_bot, 0), (sx_out, sy_bot, z_wall_h), (sx_in, sy_bot, z_wall_h)],
                "#475569", stroke="#1e293b", sw=1.3, layer=8)
    sc.add_poly([(sx_in, sy_bot, z_wall_h), (sx_out, sy_bot, z_wall_h), (sx_out, sy_bot, z_roof_at_wall), (sx_in, sy_bot, z_roof_in)],
                "#f8fafc", stroke="#1e293b", sw=1.5, layer=8)

    # 3. Sleek dark steel safety handrail along the 3 open top steps (Y = 1106..1031, X = sx_out - 6, Z = 58..102)
    sc.add_line((sx_out - 6, sy_top, 102), (sx_out - 6, sy_roof_n, 102), stroke="#0f172a", sw=2.4, layer=9)
    for ry in [sy_top - 4, (sy_top + sy_roof_n) / 2.0, sy_roof_n + 4]:
        sc.add_line((sx_out - 6, ry, z_wall_h), (sx_out - 6, ry, 102), stroke="#1e293b", sw=1.8, layer=9)

    # 4. Crisp white structural timber posts supporting the low 12° east roof (at Y = 1026, 886, 746)
    pw = 11.0
    for py_c in [sy_roof_n - 8, (sy_roof_n + sy_bot) / 2.0, sy_bot + 8]:
        x_p1, x_p2 = sx_out - pw, sx_out
        z_ptop = z_roof_at_wall
        # East face of post
        sc.add_poly([(x_p2, py_c - pw / 2, z_wall_h), (x_p2, py_c + pw / 2, z_wall_h), (x_p2, py_c + pw / 2, z_ptop), (x_p2, py_c - pw / 2, z_ptop)],
                    "#ffffff", stroke="#334155", sw=1.2, layer=9)
        # North/South visible face of post
        py_f = py_c + pw / 2 if view == "ne" else py_c - pw / 2
        sc.add_poly([(x_p1, py_f, z_wall_h), (x_p2, py_f, z_wall_h), (x_p2, py_f, z_ptop), (x_p1, py_f, z_ptop)],
                    "#e2e8f0", stroke="#334155", sw=1.1, layer=9)
    # Subtle glass/open wind screen OR clean horizontal fascia beam along top of posts (Z = z_roof_at_wall - 12 .. z_roof_at_wall)
    sc.add_poly([(sx_out, sy_bot, z_roof_at_wall - 11), (sx_out, sy_roof_n, z_roof_at_wall - 11), (sx_out, sy_roof_n, z_roof_at_wall), (sx_out, sy_bot, z_roof_at_wall)],
                "#ffffff", stroke="#334155", sw=1.2, layer=9)

    # 5. LOW HORIZONTAL 12° EAST-SLOPING ROOF (parallel to horizontal siding! Y = 1031..741, X = 866..994)
    roof_thick = 12.0
    # Top black roofing surface (matte black standing-seam / tile matching main roof!)
    sc.add_poly([
        (sx_in, sy_bot - 12, z_roof_in + roof_thick),
        (sx_in, sy_roof_n + 12, z_roof_in + roof_thick),
        (sx_roof, sy_roof_n + 12, z_roof_out + roof_thick),
        (sx_roof, sy_bot - 12, z_roof_out + roof_thick),
    ], "#1e293b", stroke="#0f172a", sw=2.0, layer=10, ambient=0.52)
    # Subtle roof seam lines running east-west
    for ry in range(int(sy_bot) + 25, int(sy_roof_n), 45):
        sc.add_line((sx_in + 2, ry, z_roof_in + roof_thick + 0.5), (sx_roof - 2, ry, z_roof_out + roof_thick + 0.5),
                    stroke="#334155", sw=0.9, layer=10, depth_bias=-1.0, opacity=0.7)
    # Front/East black gutter/fascia edge (X = sx_roof)
    sc.add_poly([
        (sx_roof, sy_bot - 12, z_roof_out),
        (sx_roof, sy_roof_n + 12, z_roof_out),
        (sx_roof, sy_roof_n + 12, z_roof_out + roof_thick),
        (sx_roof, sy_bot - 12, z_roof_out + roof_thick),
    ], "#0f172a", stroke="#020617", sw=1.3, layer=10)
    # North/South fascia edge of stair roof (shows the crisp 12° slope!)
    y_edge = sy_roof_n + 12 if view == "ne" else sy_bot - 12
    sc.add_poly([
        (sx_in, y_edge, z_roof_in),
        (sx_roof, y_edge, z_roof_out),
        (sx_roof, y_edge, z_roof_out + roof_thick),
        (sx_in, y_edge, z_roof_in + roof_thick),
    ], "#ffffff", stroke="#1e293b", sw=1.4, layer=10)

    if with_labels:
        if view == "ne":
            # Clean open lawn callouts strictly INSIDE left panel bounds (no edge clipping, no text on wall!)
            sc.add_line((sx_roof, 885, 165), (1080, 620, 0), stroke="#0f172a", sw=1.4, dash="4,3", layer=11)
            sc.add_text_at((1080, 620, 0), "Lavt 12° trappetak (under overlys Bad 1.etg)", dx=-120, dy=20, size=13, weight="800", fill="#0f172a", anchor="start")
            sc.add_line((sx_out, 1068, 50), (1160, 1020, 0), stroke="#0369a1", sw=1.4, dash="4,3", layer=11)
            sc.add_text_at((1160, 1020, 0), "3 åpne øverste trinn → bunn-repos syd i U.04", dx=-40, dy=28, size=13, weight="800", fill="#0369a1", anchor="middle")
            sc.add_text_at((866, 1416, 40), "100 % fluktende østvegg (2,50 m nord-tilbygg)", dx=-10, dy=48, size=13, weight="800", fill="#ea580c", anchor="start")
        else:
            # Clean open lawn callouts strictly INSIDE right panel bounds (anchor="end" so zero right-edge clipping!)
            sc.add_line((sx_roof, 840, 162), (1140, 740, 0), stroke="#0f172a", sw=1.4, dash="4,3", layer=11)
            sc.add_text_at((1140, 740, 0), "Lavt 12° trappetak (8 cm klar av Sov/Pult)", dx=85, dy=22, size=13, weight="800", fill="#0f172a", anchor="end")
            sc.add_line((866, 1300, 120), (1100, 1280, 0), stroke="#ea580c", sw=1.4, dash="4,3", layer=11)
            sc.add_text_at((1100, 1280, 0), "100 % fluktende østvegg (2,50 m nord)", dx=45, dy=24, size=13, weight="800", fill="#ea580c", anchor="end")

    return sc.render()


def main():
    # 1. Dual-panel presentation sheet saved to repo (NE hero + SE/East overview)
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
        f'<rect x="0" y="116" width="{W}" height="6" fill="#059669"/>',
        f'<text x="48" y="54" font-size="34" font-weight="800" fill="#ffffff">M6 (#50) — Eksakt 3D-modell NORDØST &amp; SØRØST: Alternativ 2 (Catrine)</text>',
        f'<text x="48" y="92" font-size="19" font-weight="500" fill="#cbd5e1">100 % fluktende østvegg m/ 2,50 m nord-tilbygg • 3 åpne kjellertrinn + lavt 12° øst-hellende tak rett under overlys Bad 1.etg • Bunn-repos syd i U.04</text>',

        # Left Panel Header (NE)
        f'<rect x="{p1x}" y="138" width="{pw}" height="46" fill="#d1fae5" stroke="#059669" stroke-width="1.5" rx="8"/>',
        f'<text x="{p1x + pw / 2}" y="168" font-size="20" font-weight="800" fill="#047857" text-anchor="middle">NORDØST 3/4 — 2,50 m nord-tilbygg + kjellernedgang (3 åpne trinn + 12° tak)</text>',
        f'<rect x="{p1x}" y="{py}" width="{pw}" height="{ph}" fill="url(#sky)" stroke="#cbd5e1" stroke-width="2" rx="10"/>',

        # Right Panel Header (SE)
        f'<rect x="{p2x}" y="138" width="{pw}" height="46" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5" rx="8"/>',
        f'<text x="{p2x + pw / 2}" y="168" font-size="20" font-weight="800" fill="#0369a1" text-anchor="middle">SØRØST 3/4 — Helhetlig fluktende østfasade, smalt Bad 2.etg &amp; 8 cm klaring til Sov/Pult</text>',
        f'<rect x="{p2x}" y="{py}" width="{pw}" height="{ph}" fill="url(#sky)" stroke="#cbd5e1" stroke-width="2" rx="10"/>',
    ]

    cam_ne = Camera3D(pos=(2520.0, 2750.0, 720.0), target=(480.0, 740.0, 355.0), fov_deg=35.0, cx=p1x + pw / 2.0 - 10, cy=py + ph * 0.54, width=pw * 0.96)
    cam_se = Camera3D(pos=(2520.0, -1480.0, 730.0), target=(480.0, 620.0, 365.0), fov_deg=35.0, cx=p2x + pw / 2.0 - 15, cy=py + ph * 0.54, width=pw * 0.96)

    svg.append('<g clip-path="url(#clipL)">')
    svg.extend(build_alt2_ne_scene(cam_ne, with_labels=True, view="ne"))
    svg.append("</g>")

    svg.append('<g clip-path="url(#clipR)">')
    svg.extend(build_alt2_ne_scene(cam_se, with_labels=True, view="se"))
    svg.append("</g>")

    svg.append(
        f'<text x="{W / 2}" y="1116" font-size="16" font-weight="600" fill="#475569" text-anchor="middle">'
        f'Eksakt matematisk perspektiv (1:1 koordinater) • Overlys Bad 1.etg (Z=198–248) helt over 12° trappetak (Z=186→159) • 4 linjerte takvinduer • Fluktende nord-trappevinduer'
        f'</text>'
    )
    svg.append("</svg>")

    out = os.path.join(OUT_DIR, "perspektiv_3d_nordost_alt2_eksakt.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out}")

    # 2. Also export clean label-free NE & SE reference SVGs for future photorealistic rendering!
    for tag, cam_pos, cam_tgt in [
        ("ne", (2520.0, 2780.0, 720.0), (470.0, 740.0, 355.0)),
        ("se", (2480.0, -1520.0, 730.0), (470.0, 600.0, 365.0)),
    ]:
        rw, rh = 1400, 940
        rcam = Camera3D(pos=cam_pos, target=cam_tgt, fov_deg=35.0, cx=rw / 2.0, cy=rh * 0.54, width=rw)
        rsvg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {rw} {rh}" width="{rw}" height="{rh}">',
            f'<rect width="{rw}" height="{rh}" fill="#e0f2fe"/>',
            *build_alt2_ne_scene(rcam, with_labels=False, view=tag),
            "</svg>",
        ]
        rpath = os.path.join(ART_DIR, f"ref_3d_{tag}_alt2.svg")
        with open(rpath, "w", encoding="utf-8") as f:
            f.write("\n".join(rsvg))
        print(f"Wrote {rpath}")


if __name__ == "__main__":
    main()
