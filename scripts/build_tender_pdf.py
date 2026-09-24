import os
import re
import base64
import subprocess
import markdown

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
docs_dir = os.path.join(repo_root, "docs")
assets_dir = os.path.join(repo_root, "assets", "images")

md_path = os.path.join(docs_dir, "ANBUDSFORESPORSEL_GRUNNARBEIDER_NORD.md")
pdf_path = os.path.join(docs_dir, "ANBUDSFORESPORSEL_GRUNNARBEIDER_NORD.pdf")
img_path = os.path.join(assets_dir, "planskisse_anleggsomraade_nord.png")

with open(md_path, "r", encoding="utf-8") as f:
    md_content = f.read()

# Encode image to base64
with open(img_path, "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode("utf-8")
img_data_uri = f"data:image/png;base64,{img_b64}"

# Replace image markdown with embedded image
md_content = re.sub(
    r'!\[Planskisse Anleggsområde Nord\]\([^)]+\)',
    f'<div style="text-align:center; margin: 15px 0;"><img src="{img_data_uri}" style="max-width:100%; border:1px solid #cbd5e1; border-radius:6px; box-shadow:0 2px 6px rgba(0,0,0,0.08);"/></div>',
    md_content
)

# Replace mermaid diagram with clean HTML representation
mermaid_pattern = r'```mermaid[\s\S]*?```'
mermaid_replacement = """
<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:12px; margin:15px 0; font-family:monospace; font-size:12px; color:#334155;">
  <strong>Fremdriftsrekkefølge i anlegget:</strong><br>
  1. Rigg & Fjerning av masser ➔ 2. Utgraving Drensgrøft & Underbygd Kjeller ➔ 3. Pukksåle & Betongarbeid (Kjeller C+24,4 & Trapp) ➔ 4. Doyma-hylse & Ny Vannledning til U.11 ➔ 5. Drenering, Knetteplast & XPS 100-150mm ➔ 6. Tilkobling rør #96 & Kum ➔ 7. Gangvei, Bærelag Innkjøring & Planering
</div>
"""
md_content = re.sub(mermaid_pattern, mermaid_replacement, md_content)

# Convert Markdown to HTML
html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

# Signature section
sig_html = """
<div style="margin-top: 40px; page-break-inside: avoid; border-top: 2px solid #0f172a; padding-top: 20px;">
  <div style="display: flex; justify-content: space-between; margin-top: 30px;">
    <div style="width: 45%;">
      <p><strong>For Tiltakshaver (Magnus Kirø):</strong></p>
      <div style="margin-top: 40px; border-bottom: 1px solid #64748b;"></div>
      <p style="font-size: 11px; color: #64748b; margin-top: 4px;">Dato / Sted / Signatur</p>
    </div>
    <div style="width: 45%;">
      <p><strong>For Valgt Entreprenør:</strong></p>
      <div style="margin-top: 40px; border-bottom: 1px solid #64748b;"></div>
      <p style="font-size: 11px; color: #64748b; margin-top: 4px;">Dato / Sted / Signatur & Firma</p>
    </div>
  </div>
</div>
"""

# Complete HTML document with professional CSS
full_html = f"""<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="UTF-8">
<title>Anbudsforespørsel - Grunnarbeider Nord & Vest - Myrteveien 6</title>
<style>
  @page {{
    size: A4;
    margin: 18mm 18mm 22mm 18mm;
    @bottom-right {{
      content: counter(page);
    }}
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.45;
    font-size: 11pt;
  }}
  h1 {{
    font-size: 20pt;
    color: #0f172a;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 8px;
    margin-top: 0;
    margin-bottom: 12px;
  }}
  h2 {{
    font-size: 14pt;
    color: #0369a1;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 4px;
    margin-top: 24px;
    margin-bottom: 10px;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 11.5pt;
    color: #0f172a;
    margin-top: 16px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }}
  p, li {{
    margin-top: 4px;
    margin-bottom: 6px;
  }}
  ul, ol {{
    padding-left: 22px;
    margin-top: 4px;
    margin-bottom: 8px;
  }}
  blockquote {{
    background: #f0f9ff;
    border-left: 4px solid #0284c7;
    margin: 12px 0;
    padding: 8px 14px;
    font-size: 10.5pt;
    color: #0c4a6e;
    border-radius: 0 4px 4px 0;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 10pt;
    page-break-inside: avoid;
  }}
  th, td {{
    border: 1px solid #cbd5e1;
    padding: 6px 9px;
    text-align: left;
  }}
  th {{
    background: #f1f5f9;
    font-weight: 600;
    color: #0f172a;
  }}
  tr:nth-child(even) td {{
    background: #f8fafc;
  }}
  hr {{
    border: 0;
    border-top: 1px solid #e2e8f0;
    margin: 20px 0;
  }}
  strong {{
    color: #0f172a;
  }}
</style>
</head>
<body>
{html_body}
{sig_html}
</body>
</html>
"""

temp_html_path = os.path.join(docs_dir, "tender_temp.html")
with open(temp_html_path, "w", encoding="utf-8") as f:
    f.write(full_html)

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [
    chrome_path,
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    temp_html_path
]

res = subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(temp_html_path):
    os.remove(temp_html_path)

if os.path.exists(pdf_path):
    size_kb = os.path.getsize(pdf_path) // 1024
    print(f"Successfully generated PDF: {pdf_path} ({size_kb} KB)")
else:
    print(f"Failed to generate PDF. Chrome error: {res.stderr}")
