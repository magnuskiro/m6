#!/usr/bin/env python3
"""
Exact 3D Southwest perspective comparison:
  - Left:  Alternativ 2   (2,30 × 5,02 m vest på eksist. mur, 32,7° parallelt saltak)
  - Right: Alternativ 2.5 (3,00 × 5,02 m vest, +70 cm dypere stue, 32,7° parallelt saltak — fortsatt 33 cm klar av original pipe!)
"""

import os
import sys

sys.path.insert(0, "/home/kiro/repos/m6/scripts")
from generate_3d_perspektiv_eksakt import Camera3D, build_house_3d

OUT_DIR = "/home/kiro/repos/m6/assets/images/drawings"
ART_DIR = "/home/kiro/.gemini/antigravity-cli/brain/505e5e3b-a643-4ed3-bd58-6302c2f77d03"


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
        f'<text x="60" y="56" font-size="36" font-weight="800" fill="#ffffff">M6 (#50) — Eksakt 3D-modell SØRVEST: Alternativ 2 (2,30 m) vs. Alternativ 2.5 (3,00 m)</text>',
        f'<text x="60" y="96" font-size="21" font-weight="500" fill="#cbd5e1">Identisk 3,20 | 5,02 | 3,44 m plassering og parallelt 32,7° saltak (fortsatt 33 cm klar av pipa!) • +70 cm dypere tverrfløy i Alt 2.5</text>',
        f'<rect x="40" y="160" width="1260" height="980" fill="url(#sky)" stroke="#cbd5e1" stroke-width="2" rx="12"/>',
        f'<rect x="1340" y="160" width="1260" height="980" fill="url(#sky)" stroke="#cbd5e1" stroke-width="2" rx="12"/>',
        '<clipPath id="clipL"><rect x="40" y="160" width="1260" height="980" rx="12"/></clipPath>',
        '<clipPath id="clipR"><rect x="1340" y="160" width="1260" height="980" rx="12"/></clipPath>',
    ]

    cam_pos = (-1980.0, -1750.0, 840.0)
    cam_tgt = (240.0, 480.0, 400.0)
    camL = Camera3D(cam_pos, cam_tgt, fov_deg=35.0, cx=675.0, cy=720.0, width=1220.0)
    camR = Camera3D(cam_pos, cam_tgt, fov_deg=35.0, cx=1975.0, cy=720.0, width=1220.0)

    svg.append('<g clip-path="url(#clipL)">')
    svg.extend(build_house_3d(camL, west_d=230.0, y_s=344.0, y_n=846.0, wing_deg=32.7, label_wing="2,30 m (EKSIST. MUR)"))
    svg.append("</g>")

    svg.append('<g clip-path="url(#clipR)">')
    svg.extend(build_house_3d(camR, west_d=300.0, y_s=344.0, y_n=846.0, wing_deg=32.7, label_wing="3,00 m UT MOT VEST"))
    svg.append("</g>")

    svg.append('<rect x="65" y="180" width="760" height="72" fill="#ffffff" opacity="0.94" stroke="#0284c7" stroke-width="2" rx="10"/>')
    svg.append('<text x="90" y="212" font-size="22" font-weight="800" fill="#0f172a">ALTERNATIV 2: 2,30 × 5,02 m (32,7° parallelt saltak)</text>')
    svg.append('<text x="90" y="238" font-size="16" font-weight="600" fill="#0284c7">Rett på eksisterende kjellermur • ~26 m² stue • 33 cm fri pipeklaring</text>')

    svg.append('<rect x="1365" y="180" width="840" height="72" fill="#ffffff" opacity="0.94" stroke="#059669" stroke-width="2" rx="10"/>')
    svg.append('<text x="1390" y="212" font-size="22" font-weight="800" fill="#0f172a">ALTERNATIV 2.5: 3,00 × 5,02 m (32,7° parallelt saltak)</text>')
    svg.append('<text x="1390" y="238" font-size="16" font-weight="600" fill="#059669">+0,70 m dypere (~30 m² stue, 2,49 m fri sone vest for peis) • UENDRET 33 cm pipeklaring!</text>')

    svg.append(f'<rect x="40" y="1165" width="{W - 80}" height="88" fill="#ffffff" stroke="#cbd5e1" stroke-width="2" rx="10"/>')
    svg.append('<text x="75" y="1200" font-size="19" font-weight="700" fill="#0f172a">Hvorfor Alt 2.5 (3,00 m) beholder 100 % identisk pipeklaring (33 cm):</text>')
    svg.append('<text x="75" y="1230" font-size="18" font-weight="500" fill="#334155">Gradrenna mot hovedtaket styres kun av fløybredden (5,02 m) og takvinkelen (32,7°), IKKE av dybden mot vest. Alt 2.5 gir ~30 m² stue og full 2,4 m L-sofa selv med H2O-peis rett vest på pipa!</text>')
    svg.append("</svg>")

    out = os.path.join(OUT_DIR, "perspektiv_3d_alt25_sorvest.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))
    print(f"Wrote {out}")

    # Also save a clean single-view Alt 2.5 SW reference for potential photorealistic render later
    rw, rh = 1400, 940
    rcam = Camera3D(cam_pos, cam_tgt, fov_deg=35.0, cx=rw / 2.0, cy=rh * 0.56, width=rw * 0.96)
    rsvg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {rw} {rh}" width="{rw}" height="{rh}">',
        f'<rect width="{rw}" height="{rh}" fill="#e0f2fe"/>',
        *build_house_3d(rcam, west_d=300.0, y_s=344.0, y_n=846.0, wing_deg=32.7, label_wing="3,00 m UT MOT VEST"),
        "</svg>",
    ]
    rpath = os.path.join(ART_DIR, "ref_3d_sw_alt25.svg")
    with open(rpath, "w", encoding="utf-8") as f:
        f.write("\n".join(rsvg))
    print(f"Wrote {rpath}")


if __name__ == "__main__":
    main()
