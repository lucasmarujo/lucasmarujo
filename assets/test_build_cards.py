import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from build_cards import (
    APP_BUTTON_X,
    BASE,
    BOTTOM_HEIGHT,
    BUTTON_GAP,
    BUTTON_HEIGHT,
    BUTTON_WIDTH,
    BUTTON_Y,
    CARD_PADDING,
    CARD_WIDTH,
    DOWNLOAD_ICON_WIDTH,
    HALF_WIDTH,
    LABEL_CHAR_WIDTH,
    PROJECTS,
    SITE_BUTTON_X,
    SITE_CTA,
    SITE_ICON_WIDTH,
    TOP_HEIGHT,
    app_half_shapes,
    layout_label,
    render_card,
    render_cta,
    render_site_cta,
    site_half_shapes,
    top_shape,
)

README = Path(BASE).parent / "README.md"
SITES = {
    "pulso": "https://pulso.marujo.dev",
    "acelera": "https://acelera.marujo.dev",
    "orkai": "https://orkai.marujo.dev",
}
PIECES = ("top", "app", "site")
BASE64_DATA = re.compile(r"base64,[A-Za-z0-9+/=]+")


def project(**overrides):
    return {**PROJECTS[0], **overrides}


def svg_size(content):
    root = ET.fromstring(content)
    return int(root.get("width")), int(root.get("height"))


def readme_text():
    return README.read_text(encoding="utf-8")


def featured_projects(readme):
    return readme[readme.index("## 🚀 Featured Projects"):]


def asset_text(filename):
    return (Path(BASE) / filename).read_text(encoding="utf-8")


def rendered_pieces(item):
    return {"top": render_card(item), "app": render_cta(item), "site": render_site_cta(item)}


class RenderCardTests(unittest.TestCase):
    def test_renders_valid_svg_with_project_content(self):
        for item in PROJECTS:
            with self.subTest(slug=item["slug"]):
                card = render_card(item)

                self.assertEqual(svg_size(card), (CARD_WIDTH, TOP_HEIGHT))
                self.assertIn(f">{item['name']}</text>", card)
                self.assertIn(f">{item['kind']}</text>", card)
                self.assertIn(item["color"], card)
                for line in item["lines"]:
                    self.assertIn(f">{line}</text>", card)

    def test_top_does_not_embed_buttons(self):
        for item in PROJECTS:
            with self.subTest(slug=item["slug"]):
                card = render_card(item)

                self.assertNotIn(item["cta"], card)
                self.assertNotIn(SITE_CTA, card)

    def test_falls_back_to_initial_when_project_has_no_icon(self):
        card = render_card(project(icon=None))

        self.assertNotIn("<image", card)
        self.assertIn(">P</text>", card)

    def test_single_description_line_is_vertically_centered(self):
        card = render_card(project(lines=["Uma linha só."]))

        self.assertIn('y="131" font-family', card)
        self.assertEqual(card.count('font-size="13" fill="#8B949E"'), 1)


class CardShapeTests(unittest.TestCase):
    def test_top_is_open_at_the_bottom_so_it_joins_the_halves(self):
        shape = top_shape()

        self.assertTrue(shape.startswith(f"M0.75 {TOP_HEIGHT + 1}V"))
        self.assertTrue(shape.endswith(f"V{TOP_HEIGHT + 1}"))

    def test_app_half_extends_past_the_top_and_right_seams(self):
        fill, border = app_half_shapes()

        self.assertTrue(fill.startswith(f"M{HALF_WIDTH + 1} -1H0.75"))
        self.assertTrue(border.startswith("M0.75 -1"))
        self.assertTrue(border.endswith(f"H{HALF_WIDTH + 1}"))

    def test_site_half_extends_past_the_top_and_left_seams(self):
        fill, border = site_half_shapes()

        self.assertTrue(fill.startswith("M-1 -1H"))
        self.assertTrue(border.startswith(f"M{HALF_WIDTH - 0.75:g} -1"))
        self.assertTrue(border.endswith("H-1"))

    def test_halves_together_span_the_card_width(self):
        self.assertEqual(HALF_WIDTH * 2, CARD_WIDTH)

    def test_every_card_has_the_same_size(self):
        sizes = {
            tuple(svg_size(content) for content in rendered_pieces(item).values())
            for item in PROJECTS
        }

        self.assertEqual(sizes, {((CARD_WIDTH, TOP_HEIGHT), (HALF_WIDTH, BOTTOM_HEIGHT), (HALF_WIDTH, BOTTOM_HEIGHT))})


class RenderButtonTests(unittest.TestCase):
    def test_buttons_sit_inside_the_card_padding(self):
        self.assertEqual(APP_BUTTON_X, CARD_PADDING)
        self.assertEqual(SITE_BUTTON_X + BUTTON_WIDTH, HALF_WIDTH - CARD_PADDING)
        self.assertEqual(BUTTON_Y + BUTTON_HEIGHT, BOTTOM_HEIGHT - CARD_PADDING)
        self.assertGreater(BUTTON_Y, 0)

    def test_buttons_are_split_evenly_around_the_seam(self):
        self.assertEqual(HALF_WIDTH - (APP_BUTTON_X + BUTTON_WIDTH), SITE_BUTTON_X)
        self.assertEqual(SITE_BUTTON_X * 2, BUTTON_GAP)

    def test_available_cta_is_filled_with_project_color_and_download_icon(self):
        button = render_cta(PROJECTS[2])

        self.assertIn('rx="17" fill="#FF5F87"', button)
        self.assertIn(">Baixar CLI</text>", button)
        self.assertIn('stroke="#0D1117" stroke-width="1.8"', button)

    def test_unavailable_cta_is_outlined_without_icon(self):
        button = render_cta(project(cta="Em breve", available=False))

        self.assertIn('fill="none" stroke="#30363D"', button)
        self.assertIn(">Em breve</text>", button)
        self.assertNotIn("stroke-width", button)

    def test_site_cta_uses_project_color(self):
        for item in PROJECTS:
            with self.subTest(slug=item["slug"]):
                button = render_site_cta(item)

                self.assertIn(f'fill="{item["color"]}">{SITE_CTA}</text>', button)
                self.assertIn(f'stroke="{item["color"]}" stroke-opacity="0.5"', button)

    def test_label_and_icon_stay_inside_button(self):
        cases = [(item["cta"], APP_BUTTON_X, DOWNLOAD_ICON_WIDTH) for item in PROJECTS]
        cases.append((SITE_CTA, SITE_BUTTON_X, SITE_ICON_WIDTH))
        radius = BUTTON_HEIGHT / 2
        for label, button_x, icon_width in cases:
            with self.subTest(label=label):
                text_end, icon_center = layout_label(label, button_x, icon_width)

                self.assertGreater(text_end - LABEL_CHAR_WIDTH * len(label), button_x + radius / 2)
                self.assertLess(icon_center + icon_width / 2, button_x + BUTTON_WIDTH - radius / 2)


class GeneratedAssetsTests(unittest.TestCase):
    def test_committed_svgs_match_generator(self):
        for item in PROJECTS:
            for piece, content in rendered_pieces(item).items():
                filename = f"card-{item['slug']}-{piece}.svg"
                with self.subTest(filename=filename):
                    self.assertEqual(
                        BASE64_DATA.sub("base64,", asset_text(filename)),
                        BASE64_DATA.sub("base64,", content),
                    )

    def test_no_stale_card_assets_are_left_behind(self):
        expected = {f"card-{item['slug']}-{piece}.svg" for item in PROJECTS for piece in PIECES}
        on_disk = {path.name for path in Path(BASE).glob("*.svg")}

        self.assertEqual(on_disk, expected)


class ReadmeTests(unittest.TestCase):
    def test_references_all_pieces_of_every_card(self):
        readme = readme_text()
        for item in PROJECTS:
            slug = item["slug"]
            with self.subTest(slug=slug):
                self.assertIn(f'src="assets/card-{slug}-top.svg" width="32%" align="top"', readme)
                self.assertIn(f'src="assets/card-{slug}-app.svg" width="16%" align="top"', readme)
                self.assertIn(f'src="assets/card-{slug}-site.svg" width="16%" align="top"', readme)

    def test_every_card_piece_is_top_aligned_to_avoid_gaps(self):
        images = re.findall(r"<img [^>]*>", featured_projects(readme_text()))

        self.assertEqual(len(images), len(PROJECTS) * len(PIECES))
        for image in images:
            with self.subTest(image=image):
                self.assertIn('align="top"', image)

    def test_site_buttons_link_to_project_sites(self):
        readme = readme_text()
        for slug, url in SITES.items():
            with self.subTest(slug=slug):
                self.assertRegex(readme, rf'<a href="{re.escape(url)}"[^>]*><img src="assets/card-{slug}-site\.svg"')

    def test_app_button_links_to_same_destination_as_card(self):
        readme = readme_text()
        for item in PROJECTS:
            slug = item["slug"]
            with self.subTest(slug=slug):
                top_href = re.search(rf'<a href="([^"]+)"[^>]*><img src="assets/card-{slug}-top\.svg"', readme).group(1)
                app_href = re.search(rf'<a href="([^"]+)"[^>]*><img src="assets/card-{slug}-app\.svg"', readme).group(1)

                self.assertEqual(top_href, app_href)

    def test_card_halves_have_no_whitespace_between_links(self):
        readme = readme_text()
        for item in PROJECTS:
            slug = item["slug"]
            with self.subTest(slug=slug):
                self.assertRegex(readme, rf'card-{slug}-app\.svg"[^>]*/></a><a href=')

    def test_cards_row_order_puts_orkai_right_of_instablock(self):
        readme = readme_text()
        positions = [readme.index(f"assets/card-{slug}-top.svg") for slug in ("pulso", "acelera", "orkai")]

        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
