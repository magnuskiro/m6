#!/usr/bin/env python3
"""
Side-by-side exact 3D comparison of 2nd-floor south balcony options on Myrteveien 6:
  - Left:  Klassisk utkraget balkong  3,20 × 1,60 m (5,1 m², ingen søyler — som dagens balkong)
  - Right: Moderne balkong på 2 søyler 3,80 × 2,15 m (8,2 m², 4-pers bord + overbygd sone i 1. etg)
"""

import os
import sys

sys.path.insert(0, "/home/kiro/repos/m6/scripts")
from generate_3d_perspektiv_eksakt import Camera3D, build_house_3d

OUT_DIR = "/home/kiro/repos/m6/assets/images/drawings"


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
        f'<rect x="0" y="0" width="{W}" height="130" fill="#0f172a"/>',
        f'<rect x="0" y="124" width="{W}" height="6" fill="#059669"/>',
        f'<text x="60" y="56" font-size="36" font-weight="800" fill="#ffffff">M6 (#50) — Balkong-sammenligning 2. etg sør: 1,60 m utkraget vs. 2,15 m på 2 søyler</text>',
        f'<text x="60" y="96" font-size="21" font-weight="500" fill="#cbd5e1">Identisk hus (Alt 2: 2,80 × 5,02 m, 32,7°) og kameravinkel — kun balkongdybde (1,60 m vs. 2,15 m) og søyler varieres</text>',
        f'<rect x="40" y="160" width="1260" height="980" fill="url(#sky)" stroke="#cbd5e1" stroke-width="2" rx="12"/>',
        f'<rect x="1340" y="160" width="1260" height="980" fill="url(#sky)" stroke="#cbd5e1" stroke-width="2" rx="12"/>',
        '<clipPath id="clipL"><rect x="40" y="160" width="1260" height="980" rx="12"/></clipPath>',
        '<clipPath id="clipR"><rect x="1340" y="160" width="1260" height="980" rx="12"/></clipPath>',
    ]

    # Slightly more south-facing SW 3/4 camera so both balcony depth & south gable proportions read crystal clearly!
    cam_pos = (-1680.0, -2100.0, 820.0)
    cam_tgt = (280.0, 340.0, 390.0)
    camL = Camera3D(cam_pos, cam_tgt, fov_deg=35.0, cx=675.0, cy=715.0, width=1220.0)
    camR = Camera3D(cam_pos, cam_tgt, fov_deg=35.0, cx=1975.0, cy=715.0, width=1220.0)

    svg.append('<g clip-path="url(#clipL)">')
    svg.extend(build_house_3d(camL, west_d=280.0, y_s=344.0, y_n=846.0, wing_deg=32.7,
                              label_wing="2,80 m vest", balcony=(273.0, 593.0, 160.0, False)))
    svg.append("</g>")

    svg.append('<g clip-path="url(#clipR)">')
    svg.extend(build_house_3d(camR, west_d=280.0, y_s=344.0, y_n=846.0, wing_deg=32.7,
                              label_wing="2,80 m vest", balcony=(243.0, 623.0, 215.0, True)))
    svg.append("</g>")

    svg.append('<rect x="65" y="180" width="840" height="72" fill="#ffffff" opacity="0.94" stroke="#0284c7" stroke-width="2" rx="10"/>')
    svg.append('<text x="90" y="212" font-size="22" font-weight="800" fill="#0f172a">KLASSISK UTKRAGET: 3,20 × 1,60 m (5,1 m²)</text>')
    svg.append('<text x="90" y="238" font-size="16" font-weight="600" fill="#0284c7">Ingen søyler på markterrassen • Kafébord + 2 stoler • Som dagens 1947-balkong</text>')

    svg.append('<rect x="1365" y="180" width="880" height="72" fill="#ffffff" opacity="0.94" stroke="#059669" stroke-width="2" rx="10"/>')
    svg.append('<text x="1390" y="212" font-size="22" font-weight="800" fill="#0f172a">MODERNE PÅ 2 SØYLER: 3,80 × 2,15 m (8,2 m²)</text>')
    svg.append('<text x="1390" y="238" font-size="16" font-weight="600" fill="#059669">4-pers spisebord/lounge • Flukter med flankevinduene • Overbygd sone over 1. etg-dør</text>')

    svg.append(f'<rect x="40" y="1165" width="{W - 80}" height="88" fill="#ffffff" stroke="#cbd5e1" stroke-width="2" rx="10"/>')
    svg.append('<text x="75" y="1200" font-size="19" font-weight="700" fill="#0f172a">Direkte sammenligning (eksakt 3D-skala):</text>')
    svg.append('<text x="75" y="1230" font-size="18" font-weight="500" fill="#334155">Venstre (1,60 m): Lett, luftig og uten søyler — men trang til mer enn 2 stoler. Høyre (2,15 m): +60 % større areal (8,2 m²), fullverdig uteplass i 2. etg + tørt overbygg utenfor 1. etg!</text>')
    svg.append("</svg>")

    out = os.path.join(OUT_DIR, "perspektiv_3d_balkong_sammenligning.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
