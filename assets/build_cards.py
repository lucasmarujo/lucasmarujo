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
    {
        "slug": "gitwallpaper",
        "name": "Git Wallpaper",
        "kind": "MOBILE APP",
        "color": "#39D353",
        "icon": "icon-gitwallpaper.png",
        "lines": ["Seu gráfico de contribuições do GitHub", "no wallpaper do Android, sempre em dia."],
        "cta": "Baixar app",
        "available": True,
    },
]

SITE_CTA = "Visitar site"
FONT = "'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
BASE = os.path.dirname(os.path.abspath(__file__))

CARD_BACKGROUND = "#0D1117"
CARD_BORDER = "#242C37"
CARD_WIDTH = 300
CARD_RADIUS = 16
CARD_PADDING = 24
TOP_HEIGHT = 152
HALF_WIDTH = CARD_WIDTH // 2
BOTTOM_HEIGHT = 68
BUTTON_GAP = 8
BUTTON_WIDTH = (CARD_WIDTH - 2 * CARD_PADDING - BUTTON_GAP) // 2
BUTTON_HEIGHT = 34
BUTTON_Y = BOTTOM_HEIGHT - CARD_PADDING - BUTTON_HEIGHT
APP_BUTTON_X = CARD_PADDING
SITE_BUTTON_X = BUTTON_GAP // 2
LABEL_Y = BUTTON_Y + 21.5
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


def top_shape():
    edge = CARD_WIDTH - 0.75
    return (
        f"M0.75 {TOP_HEIGHT + 1}V{0.75 + CARD_RADIUS:g}"
        f"A{CARD_RADIUS} {CARD_RADIUS} 0 0 1 {0.75 + CARD_RADIUS:g} 0.75H{edge - CARD_RADIUS:g}"
        f"A{CARD_RADIUS} {CARD_RADIUS} 0 0 1 {edge:g} {0.75 + CARD_RADIUS:g}V{TOP_HEIGHT + 1}"
    )


def app_half_shapes():
    bottom = BOTTOM_HEIGHT - 0.75
    corner = (
        f"V{bottom - CARD_RADIUS:g}"
        f"A{CARD_RADIUS} {CARD_RADIUS} 0 0 0 {0.75 + CARD_RADIUS:g} {bottom:g}H{HALF_WIDTH + 1}"
    )
    return f"M{HALF_WIDTH + 1} -1H0.75{corner}Z", f"M0.75 -1{corner}"


def site_half_shapes():
    bottom = BOTTOM_HEIGHT - 0.75
    edge = HALF_WIDTH - 0.75
    corner = (
        f"V{bottom - CARD_RADIUS:g}"
        f"A{CARD_RADIUS} {CARD_RADIUS} 0 0 1 {edge - CARD_RADIUS:g} {bottom:g}H-1"
    )
    return f"M-1 -1H{edge:g}{corner}Z", f"M{edge:g} -1{corner}"


def layout_label(label, button_x, icon_width):
    text_width = LABEL_CHAR_WIDTH * len(label)
    center = button_x + BUTTON_WIDTH / 2
    text_end = center - (text_width + LABEL_ICON_GAP + icon_width) / 2 + text_width
    return text_end, text_end + LABEL_ICON_GAP + icon_width / 2


def render_piece(width, height, label, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{label}">
  {body}
</svg>
"""


def render_half(shapes, button):
    fill, border = shapes
    return (
        f'<path d="{fill}" fill="{CARD_BACKGROUND}"/>'
        f'<path d="{border}" fill="none" stroke="{CARD_BORDER}"/>'
        f"{button}"
    )


def render_cta(project):
    label = project["cta"]
    if project["available"]:
        color = project["color"]
        tx, ix = layout_label(label, APP_BUTTON_X, DOWNLOAD_ICON_WIDTH)
        arrow_top = BUTTON_Y + 9.5
        button = (
            f'<rect x="{APP_BUTTON_X}" y="{BUTTON_Y}" width="{BUTTON_WIDTH}" height="{BUTTON_HEIGHT}"'
            f' rx="{BUTTON_HEIGHT / 2:g}" fill="{color}"/>'
            f'<text x="{tx:g}" y="{LABEL_Y:g}" text-anchor="end" font-family="{FONT}" font-size="12.5"'
            f' font-weight="600" fill="#0D1117">{label}</text>'
            f'<path d="M{ix:g} {arrow_top:g}v9m0 0l-3.5-3.5M{ix:g} {arrow_top + 9:g}l3.5-3.5M{ix - 5:g} {arrow_top + 15:g}h10"'
            f' fill="none" stroke="#0D1117" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        )
    else:
        button = (
            f'<rect x="{APP_BUTTON_X + 0.5:g}" y="{BUTTON_Y + 0.5:g}" width="{BUTTON_WIDTH - 1}" height="{BUTTON_HEIGHT - 1}"'
            f' rx="{(BUTTON_HEIGHT - 1) / 2:g}" fill="none" stroke="#30363D"/>'
            f'<text x="{APP_BUTTON_X + BUTTON_WIDTH / 2:g}" y="{LABEL_Y:g}" text-anchor="middle" font-family="{FONT}"'
            f' font-size="12.5" font-weight="600" fill="#6E7681">{label}</text>'
        )
    return render_piece(HALF_WIDTH, BOTTOM_HEIGHT, label, render_half(app_half_shapes(), button))


def render_site_cta(project):
    color = project["color"]
    tx, ix = layout_label(SITE_CTA, SITE_BUTTON_X, SITE_ICON_WIDTH)
    icon_y = BUTTON_Y + BUTTON_HEIGHT / 2
    button = (
        f'<rect x="{SITE_BUTTON_X + 0.5:g}" y="{BUTTON_Y + 0.5:g}" width="{BUTTON_WIDTH - 1}" height="{BUTTON_HEIGHT - 1}"'
        f' rx="{(BUTTON_HEIGHT - 1) / 2:g}" fill="{color}" fill-opacity="0.06" stroke="{color}" stroke-opacity="0.5"/>'
        f'<text x="{tx:g}" y="{LABEL_Y:g}" text-anchor="end" font-family="{FONT}" font-size="12.5"'
        f' font-weight="600" fill="{color}">{SITE_CTA}</text>'
        f'<path d="M{ix - 4:g} {icon_y + 4:g}l8-8M{ix - 2:g} {icon_y - 4:g}h6v6" fill="none"'
        f' stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
    )
    return render_piece(HALF_WIDTH, BOTTOM_HEIGHT, SITE_CTA, render_half(site_half_shapes(), button))


def render_lines(lines):
    ys = [122, 141] if len(lines) > 1 else [131]
    return "".join(
        f'<text x="24" y="{y}" font-family="{FONT}" font-size="13" fill="#8B949E">{line}</text>'
        for y, line in zip(ys, lines)
    )


def render_card(project):
    color = project["color"]
    shape = top_shape()
    return render_piece(CARD_WIDTH, TOP_HEIGHT, project["name"], f"""<defs>
    <linearGradient id="icon" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{color}" stop-opacity="0.9"/>
      <stop offset="1" stop-color="{color}" stop-opacity="0.55"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.9" cy="0" r="0.95">
      <stop offset="0" stop-color="{color}" stop-opacity="0.10"/>
      <stop offset="1" stop-color="{color}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <path d="{shape}" fill="{CARD_BACKGROUND}" stroke="{CARD_BORDER}"/>
  <path d="{shape}" fill="url(#glow)"/>
  {render_icon(project)}
  <text x="90" y="43" font-family="{FONT}" font-size="9.5" font-weight="600" letter-spacing="2" fill="#5B6672">{project['kind']}</text>
  <text x="89" y="69" font-family="{FONT}" font-size="24" font-weight="700" fill="{color}">{project['name']}</text>
  <line x1="24" y1="96" x2="{CARD_WIDTH - 24}" y2="96" stroke="#1E252F"/>
  {render_lines(project['lines'])}""")


def write_svg(filename, content):
    path = os.path.join(BASE, filename)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    print(f"{path} ({os.path.getsize(path) // 1024} KB)")


if __name__ == "__main__":
    for project in PROJECTS:
        write_svg(f"card-{project['slug']}-top.svg", render_card(project))
        write_svg(f"card-{project['slug']}-app.svg", render_cta(project))
        write_svg(f"card-{project['slug']}-site.svg", render_site_cta(project))
