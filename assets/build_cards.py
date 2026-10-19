"""Gera os cards SVG da secao Featured Projects. Rode: python assets/build_cards.py"""
import base64
import io
import os

from PIL import Image

PROJECTS = [
    {
        "slug": "pulso",
        "name": "Pulso",
        "kind": "MOBILE APP",
        "color": "#C2F24A",
        "icon": "icon-pulso.png",
        "lines": ["Aplicativo de treino e dieta com IA", "integrada para Android e iOS."],
        "cta": "Baixar app",
        "available": True,
    },
    {
        "slug": "acelera",
        "name": "Instablock",
        "kind": "MOBILE APP",
        "color": "#3FCECB",
        "icon": "icon-acelera.png",
        "lines": ["Bloqueador de apps para manter o foco", "e controlar o tempo de tela no Android."],
        "cta": "Baixar app",
        "available": True,
    },
    {
        "slug": "orkai",
        "name": "Orkai CLI",
        "kind": "DEV TOOL",
        "color": "#FF5F87",
        "icon": "icon-orkai.png",
        "lines": ["Orquestre vários agentes de IA em", "vários projetos, de um terminal só."],
        "cta": "Baixar CLI",
        "available": True,
    },
]

SITE_CTA = "Visitar site"
FONT = "'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
BASE = os.path.dirname(os.path.abspath(__file__))

CARD_WIDTH = 300
CARD_HEIGHT = 166
BUTTON_WIDTH = CARD_WIDTH // 2
BUTTON_HEIGHT = 36
BUTTON_GAP = 3
PILL_WIDTH = BUTTON_WIDTH - BUTTON_GAP / 2 - 1.5
APP_PILL_X = 0.75
SITE_PILL_X = BUTTON_GAP / 2 + 0.75
LABEL_CHAR_WIDTH = 5.8
LABEL_ICON_GAP = 7
DOWNLOAD_ICON_WIDTH = 10
SITE_ICON_WIDTH = 8


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
            f'<clipPath id="clip"><rect x="24" y="24" width="52" height="52" rx="14"/></clipPath>'
            f'<image href="data:image/png;base64,{data}" x="24" y="24" width="52" height="52"'
            f' clip-path="url(#clip)" preserveAspectRatio="xMidYMid slice"/>'
        )
    return (
        f'<rect x="24" y="24" width="52" height="52" rx="14" fill="url(#icon)"/>'
        f'<text x="50" y="59" text-anchor="middle" font-family="{FONT}" font-size="26"'
        f' font-weight="700" fill="#0D1117">{project["name"][0]}</text>'
    )


def layout_label(label, pill_x, icon_width):
    text_width = LABEL_CHAR_WIDTH * len(label)
    center = pill_x + PILL_WIDTH / 2
    text_end = center - (text_width + LABEL_ICON_GAP + icon_width) / 2 + text_width
    return text_end, text_end + LABEL_ICON_GAP + icon_width / 2


def render_button(label, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{BUTTON_WIDTH}" height="{BUTTON_HEIGHT}" viewBox="0 0 {BUTTON_WIDTH} {BUTTON_HEIGHT}" role="img" aria-label="{label}">
  {body}
</svg>
"""


def render_cta(project):
    label = project["cta"]
    if project["available"]:
        color = project["color"]
        tx, ix = layout_label(label, APP_PILL_X, DOWNLOAD_ICON_WIDTH)
        return render_button(label, (
            f'<rect x="{APP_PILL_X:g}" y="0.75" width="{PILL_WIDTH:g}" height="34.5" rx="17.25" fill="{color}" stroke="{color}"/>'
            f'<text x="{tx:g}" y="22.5" text-anchor="end" font-family="{FONT}" font-size="12.5"'
            f' font-weight="600" fill="#0D1117">{label}</text>'
            f'<path d="M{ix:g} 10.5v9m0 0l-3.5-3.5M{ix:g} 19.5l3.5-3.5M{ix - 5:g} 25.5h10" fill="none"'
            f' stroke="#0D1117" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        ))
    return render_button(label, (
        f'<rect x="{APP_PILL_X:g}" y="0.75" width="{PILL_WIDTH:g}" height="34.5" rx="17.25" fill="none" stroke="#30363D"/>'
        f'<text x="{APP_PILL_X + PILL_WIDTH / 2:g}" y="22.5" text-anchor="middle" font-family="{FONT}" font-size="12.5"'
        f' font-weight="600" fill="#6E7681">{label}</text>'
    ))


def render_site_cta(project):
    color = project["color"]
    tx, ix = layout_label(SITE_CTA, SITE_PILL_X, SITE_ICON_WIDTH)
    return render_button(SITE_CTA, (
        f'<rect x="{SITE_PILL_X:g}" y="0.75" width="{PILL_WIDTH:g}" height="34.5" rx="17.25" fill="#0D1117"'
        f' stroke="{color}" stroke-opacity="0.45"/>'
        f'<text x="{tx:g}" y="22.5" text-anchor="end" font-family="{FONT}" font-size="12.5"'
        f' font-weight="600" fill="{color}">{SITE_CTA}</text>'
        f'<path d="M{ix - 4:g} 22l8-8M{ix - 2:g} 14h6v6" fill="none"'
        f' stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    ))


def render_lines(lines):
    ys = [122, 141] if len(lines) > 1 else [131]
    return "".join(
        f'<text x="24" y="{y}" font-family="{FONT}" font-size="13" fill="#8B949E">{line}</text>'
        for y, line in zip(ys, lines)
    )


def render_card(project):
    color = project["color"]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_WIDTH}" height="{CARD_HEIGHT}" viewBox="0 0 {CARD_WIDTH} {CARD_HEIGHT}" role="img" aria-label="{project['name']}">
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
  <rect x="0.75" y="0.75" width="{CARD_WIDTH - 1.5:g}" height="{CARD_HEIGHT - 1.5:g}" rx="16" fill="#0D1117" stroke="#242C37"/>
  <rect x="0.75" y="0.75" width="{CARD_WIDTH - 1.5:g}" height="{CARD_HEIGHT - 1.5:g}" rx="16" fill="url(#glow)"/>
  {render_icon(project)}
  <text x="90" y="43" font-family="{FONT}" font-size="9.5" font-weight="600" letter-spacing="2" fill="#5B6672">{project['kind']}</text>
  <text x="89" y="69" font-family="{FONT}" font-size="24" font-weight="700" fill="{color}">{project['name']}</text>
  <line x1="24" y1="96" x2="{CARD_WIDTH - 24}" y2="96" stroke="#1E252F"/>
  {render_lines(project['lines'])}
</svg>
"""


def write_svg(filename, content):
    path = os.path.join(BASE, filename)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    print(f"{path} ({os.path.getsize(path) // 1024} KB)")


if __name__ == "__main__":
    for project in PROJECTS:
        write_svg(f"card-{project['slug']}.svg", render_card(project))
        write_svg(f"btn-{project['slug']}-app.svg", render_cta(project))
        write_svg(f"btn-{project['slug']}-site.svg", render_site_cta(project))
