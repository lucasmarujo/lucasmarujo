import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from build_cards import (
    APP_PILL_X,
    BASE,
    BUTTON_WIDTH,
    CARD_WIDTH,
    DOWNLOAD_ICON_WIDTH,
    LABEL_CHAR_WIDTH,
    PILL_WIDTH,
    PROJECTS,
    SITE_CTA,
    SITE_ICON_WIDTH,
    SITE_PILL_X,
    layout_label,
    render_card,
    render_cta,
    render_site_cta,
)

README = Path(BASE).parent / "README.md"
SITES = {
    "pulso": "https://pulso.marujo.dev",
    "acelera": "https://acelera.marujo.dev",
    "orkai": "https://orkai.marujo.dev",
}
BASE64_DATA = re.compile(r"base64,[A-Za-z0-9+/=]+")


def project(**overrides):
    return {**PROJECTS[0], **overrides}


def svg_root(content):
    return ET.fromstring(content)


def readme_text():
    return README.read_text(encoding="utf-8")


def asset_text(filename):
    return (Path(BASE) / filename).read_text(encoding="utf-8")


class RenderCardTests(unittest.TestCase):
    def test_renders_valid_svg_with_project_content(self):
        for item in PROJECTS:
            with self.subTest(slug=item["slug"]):
                card = render_card(item)

                self.assertEqual(svg_root(card).get("width"), str(CARD_WIDTH))
                self.assertIn(f">{item['name']}</text>", card)
                self.assertIn(f">{item['kind']}</text>", card)
                self.assertIn(item["color"], card)
                for line in item["lines"]:
                    self.assertIn(f">{line}</text>", card)

    def test_card_does_not_embed_buttons(self):
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


class RenderButtonTests(unittest.TestCase):
    def test_button_pair_spans_exactly_one_card_width(self):
        app = svg_root(render_cta(PROJECTS[0]))
        site = svg_root(render_site_cta(PROJECTS[0]))

        self.assertEqual(int(app.get("width")) + int(site.get("width")), CARD_WIDTH)
        self.assertEqual(BUTTON_WIDTH * 2, CARD_WIDTH)

    def test_pills_leave_gap_between_app_and_site_buttons(self):
        gap = (BUTTON_WIDTH - (APP_PILL_X + PILL_WIDTH)) + SITE_PILL_X

        self.assertGreater(gap, 0)
        self.assertLessEqual(SITE_PILL_X + PILL_WIDTH, BUTTON_WIDTH)

    def test_available_cta_is_filled_with_project_color_and_download_icon(self):
        button = render_cta(PROJECTS[2])

        self.assertIn('fill="#FF5F87"', button)
        self.assertIn(">Baixar CLI</text>", button)
        self.assertIn("<path", button)

    def test_unavailable_cta_is_outlined_without_icon(self):
        button = render_cta(project(cta="Em breve", available=False))

        self.assertIn('fill="none" stroke="#30363D"', button)
        self.assertIn(">Em breve</text>", button)
        self.assertNotIn("<path", button)

    def test_site_cta_uses_project_color(self):
        for item in PROJECTS:
            with self.subTest(slug=item["slug"]):
                button = render_site_cta(item)

                self.assertIn(f'fill="{item["color"]}">{SITE_CTA}</text>', button)
                self.assertIn(f'stroke="{item["color"]}"', button)
                svg_root(button)

    def test_label_and_icon_stay_inside_pill(self):
        cases = [(item["cta"], APP_PILL_X, DOWNLOAD_ICON_WIDTH) for item in PROJECTS]
        cases.append((SITE_CTA, SITE_PILL_X, SITE_ICON_WIDTH))
        for label, pill_x, icon_width in cases:
            with self.subTest(label=label):
                text_end, icon_center = layout_label(label, pill_x, icon_width)

                self.assertGreater(text_end - LABEL_CHAR_WIDTH * len(label), pill_x + 17)
                self.assertLess(icon_center + icon_width / 2, pill_x + PILL_WIDTH - 17)


class GeneratedAssetsTests(unittest.TestCase):
    def test_committed_svgs_match_generator(self):
        for item in PROJECTS:
            slug = item["slug"]
            expected = {
                f"card-{slug}.svg": render_card(item),
                f"btn-{slug}-app.svg": render_cta(item),
                f"btn-{slug}-site.svg": render_site_cta(item),
            }
            for filename, content in expected.items():
                with self.subTest(filename=filename):
                    self.assertEqual(
                        BASE64_DATA.sub("base64,", asset_text(filename)),
                        BASE64_DATA.sub("base64,", content),
                    )


class ReadmeTests(unittest.TestCase):
    def test_references_card_and_both_buttons_of_every_project(self):
        readme = readme_text()
        for item in PROJECTS:
            slug = item["slug"]
            with self.subTest(slug=slug):
                self.assertIn(f'src="assets/card-{slug}.svg" width="32%"', readme)
                self.assertIn(f'src="assets/btn-{slug}-app.svg" width="16%"', readme)
                self.assertIn(f'src="assets/btn-{slug}-site.svg" width="16%"', readme)

    def test_site_buttons_link_to_project_sites(self):
        readme = readme_text()
        for slug, url in SITES.items():
            with self.subTest(slug=slug):
                self.assertRegex(readme, rf'<a href="{re.escape(url)}"[^>]*><img src="assets/btn-{slug}-site\.svg"')

    def test_app_button_links_to_same_destination_as_card(self):
        readme = readme_text()
        for item in PROJECTS:
            slug = item["slug"]
            with self.subTest(slug=slug):
                card_href = re.search(rf'<a href="([^"]+)"[^>]*><img src="assets/card-{slug}\.svg"', readme).group(1)
                app_href = re.search(rf'<a href="([^"]+)"[^>]*><img src="assets/btn-{slug}-app\.svg"', readme).group(1)

                self.assertEqual(card_href, app_href)

    def test_button_pair_has_no_whitespace_between_links(self):
        readme = readme_text()
        for item in PROJECTS:
            slug = item["slug"]
            with self.subTest(slug=slug):
                self.assertRegex(readme, rf'btn-{slug}-app\.svg"[^>]*/></a><a href=')

    def test_cards_row_order_puts_orkai_right_of_instablock(self):
        readme = readme_text()
        positions = [readme.index(f"assets/card-{slug}.svg") for slug in ("pulso", "acelera", "orkai")]

        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
