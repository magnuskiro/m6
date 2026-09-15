import json
import math
import subprocess
import os

def main():
    with open('/tmp/omrader.json') as f:
        data = json.load(f)
    with open('/tmp/addr_map.json') as f:
        addr_map = json.load(f)

    # Specific custom labels
    addr_map['140/1247'] = ['Trollheggveien 8 (Tomt)']
    addr_map['141/25'] = ['Myrteveien 5A / 5B']

    # Origin: Myrteveien 6 approximate center
    lat0, lon0 = 59.2666356, 10.4757783
    lat_scale = 111320
    lon_scale = 111320 * math.cos(math.radians(lat0))

    # Canvas dimensions
    width = 1600
    height = 1200
    padding = 70

    # Collect coordinates
    features = data['features']
    
    # Filter features within 130m radius of center
    included_features = []
    for feat in features:
        geom = feat['geometry']
        pts = []
        if geom['type'] == 'Polygon':
            pts = geom['coordinates'][0]
        elif geom['type'] == 'MultiPolygon':
            pts = geom['coordinates'][0][0]
        
        within = False
        for p in pts:
            x_m = (p[0] - lon0) * lon_scale
            y_m = (p[1] - lat0) * lat_scale
            if math.hypot(x_m, y_m) <= 125:
                within = True
                break
        if within:
            included_features.append(feat)

    # Define bounding box in meters
    min_x = -135
    max_x = 125
    min_y = -120
    max_y = 105

    span_x = max_x - min_x
    span_y = max_y - min_y

    scale = min((width - 2 * padding) / span_x, (height - 2 * padding) / span_y)

    def to_svg(lon, lat):
        x_m = (lon - lon0) * lon_scale
        y_m = (lat - lat0) * lat_scale
        sx = padding + (x_m - min_x) * scale
        sy = height - (padding + (y_m - min_y) * scale)
        return sx, sy

    # Updated Categories per user instruction:
    # Direkte grensenaboer: 140/1008, 140/995, 140/1014, 141/1, 140/1247 (Trollheggveien 8 tomt)
    # Gjenboere: 140/361, 140/762, 141/25, 140/373, 141/276, 141/46, 141/65
    # (Removed 140/1009 [Øvre Bogenvei 29], 141/94 [Trollheggveien 10], 141/64 [Trollheggveien 11] -> now neutral)
    # Ekskludert: 141/47 (Myrteveien 8B)
    
    grensenaboer = {'140/1008', '140/995', '140/1014', '141/1', '140/1247'}
    gjenboere = {'140/361', '140/762', '141/25', '140/373', '141/276', '141/46', '141/65'}
    ekskludert = set()

    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    svg_parts.append('''<defs>
      <pattern id="excluded-hatch" width="12" height="12" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
        <line x1="0" y1="0" x2="0" y2="12" stroke="#f43f5e" stroke-width="2.5" opacity="0.65"/>
      </pattern>
      <pattern id="grid-dots" width="40" height="40" patternUnits="userSpaceOnUse">
        <circle cx="2" cy="2" r="1.2" fill="#cbd5e1" opacity="0.6"/>
      </pattern>
    </defs>''')

    # Background
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="#f8fafc"/>')
    svg_parts.append(f'<rect width="{width}" height="{height}" fill="url(#grid-dots)"/>')

    poly_elements = []
    label_elements = []
    processed_labels = set()

    for feat in included_features:
        props = feat['properties']
        gnr = props.get('gardsnummer')
        bnr = props.get('bruksnummer')
        mat = f'{gnr}/{bnr}'

        geom = feat['geometry']
        polygons = []
        if geom['type'] == 'Polygon':
            polygons = [geom['coordinates']]
        elif geom['type'] == 'MultiPolygon':
            polygons = geom['coordinates']

        if mat == '140/371':
            fill = '#10b981'
            fill_opacity = '0.35'
            stroke = '#059669'
            stroke_width = '4'
            stroke_dash = 'none'
            category = 'tiltak'
        elif mat in ekskludert:
            fill = 'url(#excluded-hatch)'
            fill_opacity = '1'
            stroke = '#e11d48'
            stroke_width = '3'
            stroke_dash = '4,4'
            category = 'ekskludert'
        elif mat in grensenaboer:
            fill = '#3b82f6'
            fill_opacity = '0.28'
            stroke = '#1d4ed8'
            stroke_width = '3'
            stroke_dash = 'none'
            category = 'grensenabo'
        elif mat in gjenboere:
            fill = '#f59e0b'
            fill_opacity = '0.28'
            stroke = '#d97706'
            stroke_width = '2.5'
            stroke_dash = 'none'
            category = 'gjenboer'
        else:
            fill = '#ffffff'
            fill_opacity = '0.6'
            stroke = '#94a3b8'
            stroke_width = '1.2'
            stroke_dash = 'none'
            category = 'andre'

        all_svg_pts = []
        for poly in polygons:
            outer_ring = poly[0]
            svg_pts = [to_svg(pt[0], pt[1]) for pt in outer_ring]
            all_svg_pts.extend(svg_pts)
            pts_str = ' '.join([f'{x:.1f},{y:.1f}' for x, y in svg_pts])
            poly_elements.append(
                f'<polygon points="{pts_str}" fill="{fill}" fill-opacity="{fill_opacity}" stroke="{stroke}" stroke-width="{stroke_width}" stroke-dasharray="{stroke_dash}"/>'
            )

        if all_svg_pts and mat not in processed_labels:
            processed_labels.add(mat)
            avg_x = sum(p[0] for p in all_svg_pts) / len(all_svg_pts)
            avg_y = sum(p[1] for p in all_svg_pts) / len(all_svg_pts)

            # Manual centroid nudges for optimal aesthetic placement
            if mat == '140/371':
                avg_x += 10
                avg_y -= 5
            elif mat == '141/1':
                avg_x = to_svg(10.4746, 59.2657)[0]
                avg_y = to_svg(10.4746, 59.2657)[1]
            elif mat == '140/1008':
                avg_x = to_svg(10.4764, 59.2668)[0]
                avg_y = to_svg(10.4764, 59.2668)[1]
            elif mat == '140/1247':
                avg_x = to_svg(10.4760, 59.26615)[0]
                avg_y = to_svg(10.4760, 59.26615)[1]
            elif mat == '141/276':
                avg_y -= 10

            addrs = addr_map.get(mat, [])
            addr_text = addrs[0] if addrs else f'Gnr/Bnr {mat}'
            
            if category == 'tiltak':
                badge_bg = '#047857'
                text_color = '#ffffff'
                sub_color = '#d1fae5'
                title = 'TILTAKSEIENDOM'
                badge_w = 175
                badge_h = 56
                label_elements.append(f'''
                <g transform="translate({avg_x - badge_w/2:.1f}, {avg_y - badge_h/2:.1f})">
                  <rect width="{badge_w}" height="{badge_h}" rx="10" fill="{badge_bg}" stroke="#ffffff" stroke-width="2"/>
                  <text x="{badge_w/2}" y="19" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="11" fill="{sub_color}" letter-spacing="1">★ {title} ★</text>
                  <text x="{badge_w/2}" y="36" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="15" fill="{text_color}">{addr_text}</text>
                  <text x="{badge_w/2}" y="49" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="500" font-size="11" fill="{sub_color}">Gnr {mat} • 3 752 m²</text>
                </g>
                ''')
            elif category == 'ekskludert':
                badge_w = 160
                badge_h = 44
                label_elements.append(f'''
                <g transform="translate({avg_x - badge_w/2:.1f}, {avg_y - badge_h/2:.1f})">
                  <rect width="{badge_w}" height="{badge_h}" rx="8" fill="#ffe4e6" stroke="#e11d48" stroke-width="1.8"/>
                  <text x="{badge_w/2}" y="18" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="13" fill="#be123c" text-decoration="line-through">{addr_text}</text>
                  <text x="{badge_w/2}" y="33" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="600" font-size="10" fill="#e11d48">EKSKLUDERT (Gnr {mat})</text>
                </g>
                ''')
            elif category in ['grensenabo', 'gjenboer']:
                badge_bg = '#1e293b'
                border_col = '#3b82f6' if category == 'grensenabo' else '#f59e0b'
                type_label = 'GRENSENABO' if category == 'grensenabo' else 'GJENBOER'
                type_col = '#60a5fa' if category == 'grensenabo' else '#fbbf24'
                badge_w = 155
                badge_h = 42
                label_elements.append(f'''
                <g transform="translate({avg_x - badge_w/2:.1f}, {avg_y - badge_h/2:.1f})">
                  <rect width="{badge_w}" height="{badge_h}" rx="8" fill="{badge_bg}" stroke="{border_col}" stroke-width="1.8"/>
                  <text x="{badge_w/2}" y="17" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="12.5" fill="#ffffff">{addr_text}</text>
                  <text x="{badge_w/2}" y="32" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="600" font-size="10" fill="{type_col}">{type_label} • Gnr {mat}</text>
                </g>
                ''')
            elif category == 'andre' and addrs:
                badge_w = 120
                badge_h = 24
                label_elements.append(f'''
                <g transform="translate({avg_x - badge_w/2:.1f}, {avg_y - badge_h/2:.1f})">
                  <rect width="{badge_w}" height="{badge_h}" rx="5" fill="#ffffff" fill-opacity="0.9" stroke="#cbd5e1" stroke-width="1"/>
                  <text x="{badge_w/2}" y="16" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="600" font-size="11" fill="#64748b">{addr_text}</text>
                </g>
                ''')

    svg_parts.extend(poly_elements)

    # Street names along corridors
    mv_x, mv_y = to_svg(10.4752, 59.2669)
    svg_parts.append(f'''
    <g transform="translate({mv_x:.1f}, {mv_y:.1f}) rotate(-3)">
      <rect x="-95" y="-14" width="190" height="26" rx="6" fill="#0f172a" fill-opacity="0.92"/>
      <text x="0" y="4" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="13" fill="#38bdf8" letter-spacing="2">MYRTEVEIEN</text>
    </g>
    ''')

    th_x, th_y = to_svg(10.4749, 59.2666)
    svg_parts.append(f'''
    <g transform="translate({th_x:.1f}, {th_y:.1f}) rotate(74)">
      <rect x="-110" y="-14" width="220" height="26" rx="6" fill="#0f172a" fill-opacity="0.92"/>
      <text x="0" y="4" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="13" fill="#38bdf8" letter-spacing="2">TROLLHEGGVEIEN</text>
    </g>
    ''')

    ob_x, ob_y = to_svg(10.4770, 59.2661)
    svg_parts.append(f'''
    <g transform="translate({ob_x:.1f}, {ob_y:.1f}) rotate(-45)">
      <rect x="-105" y="-14" width="210" height="26" rx="6" fill="#0f172a" fill-opacity="0.92"/>
      <text x="0" y="4" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="13" fill="#38bdf8" letter-spacing="2">ØVRE BOGENVEI</text>
    </g>
    ''')

    svg_parts.extend(label_elements)

    # Header Card (Top Left)
    svg_parts.append('''
    <g transform="translate(45, 45)">
      <rect width="460" height="125" rx="14" fill="#0f172a" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
      <text x="24" y="36" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="20" fill="#ffffff">NABOOVERSIKT — MYRTEVEIEN 6</text>
      <text x="24" y="60" font-family="'Plus Jakarta Sans', sans-serif" font-weight="600" font-size="13" fill="#38bdf8">Tønsberg kommune • Gnr 140 / Bnr 371 • Tolvsrød</text>
      <text x="24" y="82" font-family="'Plus Jakarta Sans', sans-serif" font-weight="500" font-size="12" fill="#94a3b8">Nabovarsling jf. Plan- og bygningsloven § 21-3 (DiBK 5154)</text>
      <text x="24" y="103" font-family="'Plus Jakarta Sans', sans-serif" font-weight="500" font-size="11" fill="#cbd5e1">Kartgrunnlag: Kartverket / Matrikkelen (Geonorge API 2026)</text>
    </g>
    ''')

    # Legend Card (Top Right)
    svg_parts.append('''
    <g transform="translate(1080, 45)">
      <rect width="475" height="185" rx="14" fill="#0f172a" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
      <text x="24" y="34" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="16" fill="#ffffff">TEGNFORKLARING / NABOSTATUS</text>
      
      <!-- Tiltak -->
      <rect x="24" y="52" width="28" height="20" rx="4" fill="#10b981" fill-opacity="0.5" stroke="#059669" stroke-width="2.5"/>
      <text x="64" y="67" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="13" fill="#34d399">Tiltakseiendom (Myrteveien 6)</text>

      <!-- Grensenaboer -->
      <rect x="24" y="87" width="28" height="20" rx="4" fill="#3b82f6" fill-opacity="0.4" stroke="#1d4ed8" stroke-width="2.5"/>
      <text x="64" y="102" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="13" fill="#60a5fa">Direkte grensenabo (Varsles)</text>
      <text x="64" y="116" font-family="'Plus Jakarta Sans', sans-serif" font-weight="400" font-size="10.5" fill="#94a3b8">Myrteveien 2, Trollheggveien 8 (tomt), Øvre Bogenvei 31 &amp; 33B, Ulvikveien 23/33</text>

      <!-- Gjenboere -->
      <rect x="24" y="132" width="28" height="20" rx="4" fill="#f59e0b" fill-opacity="0.4" stroke="#d97706" stroke-width="2.5"/>
      <text x="64" y="147" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="13" fill="#fbbf24">Gjenboer over vei (Varsles)</text>
      <text x="64" y="161" font-family="'Plus Jakarta Sans', sans-serif" font-weight="400" font-size="10.5" fill="#94a3b8">Myrteveien 1, 3, 5A/5B, 8A; Trollheggveien 6, 7, 9</text>

    </g>
    ''')

    # North Arrow & Scale Bar (Bottom Left)
    svg_parts.append(f'''
    <g transform="translate(45, {height - 145})">
      <rect width="260" height="100" rx="12" fill="#0f172a" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
      <g transform="translate(50, 48)">
        <circle cx="0" cy="0" r="28" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>
        <path d="M 0 -22 L 6 0 L -6 0 Z" fill="#ef4444"/>
        <path d="M 0 22 L 6 0 L -6 0 Z" fill="#94a3b8"/>
        <text x="0" y="-10" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="800" font-size="11" fill="#ffffff">N</text>
      </g>
      <g transform="translate(110, 48)">
        <text x="0" y="-8" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="12" fill="#ffffff">Målestokk ~ 1:500</text>
        <line x1="0" y1="5" x2="{50 * scale / 10:.1f}" y2="5" stroke="#38bdf8" stroke-width="4"/>
        <line x1="0" y1="0" x2="0" y2="10" stroke="#ffffff" stroke-width="2"/>
        <line x1="{50 * scale / 10:.1f}" y1="0" x2="{50 * scale / 10:.1f}" y2="10" stroke="#ffffff" stroke-width="2"/>
        <text x="0" y="24" font-family="'Plus Jakarta Sans', sans-serif" font-weight="600" font-size="10" fill="#94a3b8">0</text>
        <text x="{50 * scale / 10:.1f}" y="24" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-weight="600" font-size="10" fill="#94a3b8">50 m</text>
      </g>
    </g>
    ''')

    svg_parts.append('</svg>')

    svg_content = '\n'.join(svg_parts)
    svg_path = 'assets/images/nabokart_m6.svg'
    png_path = 'assets/images/nabokart_m6.png'
    
    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    print(f'Generated SVG: {svg_path}')

    cmd = ['inkscape', svg_path, '-o', png_path, '--export-area-page', '--export-width=1600']
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f'Rendered PNG: {png_path}')
    else:
        print('Inkscape warning/error:', res.stderr)

if __name__ == '__main__':
    main()
