"""Gera os cards SVG da secao Featured Projects. Rode: python assets/build_cards.py"""
import base64
import io
import os

from PIL import Image

PROJECTS = [
    {
        "slug": "pulso",
        "name": "Pulso",
        "color": "#C2F24A",
        "icon": "icon-pulso.png",
        "lines": ["Aplicativo de treino e dieta com IA integrada", "para Android e iOS."],
        "cta": "Baixar app",
        "available": True,
    },
    {
        "slug": "lingo",
        "name": "Lingo",
        "color": "#8B96FF",
        "icon": "icon-lingo.png",
        "lines": ["Em desenvolvimento."],
        "cta": "Em breve",
        "available": False,
    },
]

FONT = "'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
BASE = os.path.dirname(os.path.abspath(__file__))


def encode_icon(filename):
    with Image.open(os.path.join(BASE, filename)) as img:
        img = img.convert("RGBA").resize((160, 160), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def render_icon(project):
    if project["icon"]:
        data = encode_icon(project["icon"])
        return (
            f'<clipPath id="clip"><rect x="32" y="30" width="62" height="62" rx="17"/></clipPath>'
            f'<image href="data:image/png;base64,{data}" x="32" y="30" width="62" height="62"'
            f' clip-path="url(#clip)" preserveAspectRatio="xMidYMid slice"/>'
        )
    return (
        f'<rect x="32" y="30" width="62" height="62" rx="17" fill="url(#icon)"/>'
        f'<text x="63" y="74" text-anchor="middle" font-family="{FONT}" font-size="30"'
        f' font-weight="700" fill="#0D1117">{project["name"][0]}</text>'
    )


def render_cta(project):
    label = project["cta"]
    if project["available"]:
        width = 8.0 * len(label) + 72
        tx = 32 + (width - 26) / 2
        ix = 32 + width - 34
        return (
            f'<rect x="32" y="172" width="{width:g}" height="38" rx="19" fill="#FFFFFF"/>'
            f'<text x="{tx:g}" y="196" text-anchor="middle" font-family="{FONT}" font-size="13"'
            f' font-weight="600" fill="#0D1117">{label}</text>'
            f'<path d="M{ix:g} 183v9m0 0l-3.5-3.5M{ix:g} 192l3.5-3.5M{ix - 5:g} 198h10" fill="none"'
            f' stroke="#0D1117" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    width = 8.2 * len(label) + 42
    return (
        f'<rect x="32.75" y="172.75" width="{width:g}" height="36.5" rx="18.25" fill="none" stroke="#30363D"/>'
        f'<text x="{32 + width / 2:g}" y="196" text-anchor="middle" font-family="{FONT}" font-size="13"'
        f' font-weight="600" fill="#6E7681">{label}</text>'
    )


def render_lines(lines):
    ys = [139, 159] if len(lines) > 1 else [149]
    return "".join(
        f'<text x="32" y="{y}" font-family="{FONT}" font-size="13.5" fill="#8B949E">{line}</text>'
        for y, line in zip(ys, lines)
    )


def render_card(project):
    color = project["color"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="440" height="226" viewBox="0 0 440 226" role="img" aria-label="{project['name']}">
  <defs>
    <linearGradient id="icon" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{color}" stop-opacity="0.9"/>
      <stop offset="1" stop-color="{color}" stop-opacity="0.55"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.9" cy="0" r="0.95">
      <stop offset="0" stop-color="{color}" stop-opacity="0.10"/>
      <stop offset="1" stop-color="{color}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="0.75" y="0.75" width="438.5" height="224.5" rx="18" fill="#0D1117" stroke="#242C37"/>
  <rect x="0.75" y="0.75" width="438.5" height="224.5" rx="18" fill="url(#glow)"/>
  {render_icon(project)}
  <text x="111" y="52" font-family="{FONT}" font-size="10" font-weight="600" letter-spacing="2.2" fill="#5B6672">MOBILE APP</text>
  <text x="110" y="81" font-family="{FONT}" font-size="28" font-weight="700" fill="{color}">{project['name']}</text>
  <line x1="32" y1="112" x2="408" y2="112" stroke="#1E252F"/>
  {render_lines(project['lines'])}
  {render_cta(project)}
</svg>
"""


if __name__ == "__main__":
    for project in PROJECTS:
        path = os.path.join(BASE, f"card-{project['slug']}.svg")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(render_card(project))
        print(f"{path} ({os.path.getsize(path) // 1024} KB)")
