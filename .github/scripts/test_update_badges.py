import tempfile
import unittest
import urllib.error
from pathlib import Path

from update_badges import (
    BADGE_SIZE_PX,
    END_COMMENT,
    MAX_PAGES,
    START_COMMENT,
    Badge,
    fetch_all_pages,
    fetch_badges,
    render_badges,
    select_badges,
    update_readme,
    update_readme_file,
)

USER = "jane-doe"
CREDLY_BADGES_URL = f"https://www.credly.com/users/{USER}/badges.json"
EXTERNAL_BADGES_URL = f"https://www.credly.com/api/v1/users/{USER}/external_badges/open_badges/public"
PROFILE_BADGES_URL = f"https://www.credly.com/users/{USER}/badges"


def credly_item(badge_id, name, issued_at_date):
    return {
        "id": badge_id,
        "issued_at_date": issued_at_date,
        "image_url": f"https://images.credly.com/images/{badge_id}/image.png",
        "badge_template": {"name": name},
    }


def external_item(name, issued_at_date, badge_url="https://catalog-education.oracle.com/pls/certview/sharebadge?id=ABC"):
    return {
        "external_badge": {
            "badge_name": name,
            "issued_at_date": issued_at_date,
            "image_url": "https://images.credly.com/images/oci/OCI25GAIOCP_cached_image_20250902-32-4693pr.png",
            "badge_url": badge_url,
        }
    }


def page(items, current_page=1, total_pages=1):
    return {"data": items, "metadata": {"current_page": current_page, "total_pages": total_pages}}


class FakeFetch:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, url):
        self.calls.append(url)
        return self.responses[url]


def readme_with(section_content):
    return f"# Title\n\n## Certifications\n{START_COMMENT}\n{section_content}\n{END_COMMENT}\n\n## Projects\n"


class FetchAllPagesTests(unittest.TestCase):
    def test_follows_pagination_with_one_request_per_page(self):
        fetch = FakeFetch({
            "https://api/items?page=1": page([1, 2], 1, 3),
            "https://api/items?page=2": page([3, 4], 2, 3),
            "https://api/items?page=3": page([5], 3, 3),
        })

        items = fetch_all_pages("https://api/items", fetch)

        self.assertEqual(items, [1, 2, 3, 4, 5])
        self.assertEqual(len(fetch.calls), 3)

    def test_returns_empty_list_when_there_are_no_pages(self):
        fetch = FakeFetch({"https://api/items?page=1": page([], 1, 0)})

        self.assertEqual(fetch_all_pages("https://api/items", fetch), [])
        self.assertEqual(len(fetch.calls), 1)

    def test_stops_at_max_pages(self):
        responses = {f"https://api/items?page={n}": page([n], n, 1000) for n in range(1, MAX_PAGES + 2)}
        fetch = FakeFetch(responses)

        items = fetch_all_pages("https://api/items", fetch)

        self.assertEqual(len(items), MAX_PAGES)
        self.assertEqual(len(fetch.calls), MAX_PAGES)


class FetchBadgesTests(unittest.TestCase):
    def test_merges_credly_and_external_badges(self):
        fetch = FakeFetch({
            f"{CREDLY_BADGES_URL}?page=1": page([credly_item("aws-1", "AWS Certified AI Practitioner", "2026-07-27")]),
            f"{EXTERNAL_BADGES_URL}?page=1": page([external_item("OCI Generative AI Professional", "2025-09-02")]),
        })

        badges = fetch_badges(USER, fetch)

        self.assertEqual(badges, [
            Badge(
                name="AWS Certified AI Practitioner",
                image_url="https://images.credly.com/images/aws-1/image.png",
                link="https://www.credly.com/badges/aws-1",
                issued_at_date="2026-07-27",
            ),
            Badge(
                name="OCI Generative AI Professional",
                image_url="https://images.credly.com/images/oci/OCI25GAIOCP_cached_image_20250902-32-4693pr.png",
                link="https://catalog-education.oracle.com/pls/certview/sharebadge?id=ABC",
                issued_at_date="2025-09-02",
            ),
        ])
        self.assertEqual(len(fetch.calls), 2)

    def test_external_badge_without_https_url_links_to_profile(self):
        fetch = FakeFetch({
            f"{CREDLY_BADGES_URL}?page=1": page([]),
            f"{EXTERNAL_BADGES_URL}?page=1": page([
                external_item("No URL", "2025-01-01", badge_url=None),
                external_item("Script URL", "2025-01-01", badge_url="javascript:alert(1)"),
            ]),
        })

        badges = fetch_badges(USER, fetch)

        self.assertEqual([badge.link for badge in badges], [PROFILE_BADGES_URL, PROFILE_BADGES_URL])


class SelectBadgesTests(unittest.TestCase):
    def setUp(self):
        self.badges = [
            Badge("Python Essentials 1", "img", "link", "2025-02-12"),
            Badge("Introduction to IoT", "img", "link", "2025-06-02"),
            Badge("Networking Basics", "img", "link", "2025-06-02"),
            Badge("AWS Serverless", "img", "link", "2026-07-28"),
            Badge("OCI Generative AI", "img", "link", "2025-09-02"),
        ]

    def test_sorts_newest_first_keeping_order_for_same_date(self):
        names = [badge.name for badge in select_badges(self.badges, 0)]

        self.assertEqual(names, [
            "AWS Serverless",
            "OCI Generative AI",
            "Introduction to IoT",
            "Networking Basics",
            "Python Essentials 1",
        ])

    def test_limit_keeps_newest_badges(self):
        names = [badge.name for badge in select_badges(self.badges, 2)]

        self.assertEqual(names, ["AWS Serverless", "OCI Generative AI"])

    def test_zero_limit_returns_all_badges(self):
        self.assertEqual(len(select_badges(self.badges, 0)), len(self.badges))


class RenderBadgesTests(unittest.TestCase):
    def test_renders_every_badge_with_fixed_size(self):
        badges = [
            Badge("AWS", "https://images.credly.com/images/aws/blob", "https://www.credly.com/badges/aws", "2026-07-28"),
            Badge(
                "OCI",
                "https://images.credly.com/images/oci/OCI25GAIOCP_cached_image.png",
                "https://catalog-education.oracle.com/pls/certview/sharebadge?id=ABC",
                "2025-09-02",
            ),
        ]

        section = render_badges(badges)

        self.assertEqual(section, "\n".join([
            START_COMMENT,
            '<p align="left">',
            '  <a href="https://www.credly.com/badges/aws" title="AWS">'
            f'<img src="https://images.credly.com/size/80x80/images/aws/blob" alt="AWS" width="{BADGE_SIZE_PX}" height="{BADGE_SIZE_PX}"/></a>',
            '  <a href="https://catalog-education.oracle.com/pls/certview/sharebadge?id=ABC" title="OCI">'
            f'<img src="https://images.credly.com/size/80x80/images/oci/OCI25GAIOCP_cached_image.png" alt="OCI" width="{BADGE_SIZE_PX}" height="{BADGE_SIZE_PX}"/></a>',
            "</p>",
            END_COMMENT,
        ]))

    def test_escapes_html_in_names_and_urls(self):
        badge = Badge('Data "Pro" <AI> & ML', "https://images.credly.com/images/x/a.png", "https://site/?a=1&b=2", "2025-01-01")

        section = render_badges([badge])

        self.assertIn('title="Data &quot;Pro&quot; &lt;AI&gt; &amp; ML"', section)
        self.assertIn('href="https://site/?a=1&amp;b=2"', section)
        self.assertNotIn("<AI>", section)


class UpdateReadmeTests(unittest.TestCase):
    def test_replaces_only_the_badges_section(self):
        readme = readme_with("[![Old](https://old.png)](https://old)")

        updated = update_readme(readme, f"{START_COMMENT}\nNEW\n{END_COMMENT}")

        self.assertEqual(updated, readme_with("NEW"))

    def test_handles_replacement_with_backslashes(self):
        updated = update_readme(readme_with("old"), f"{START_COMMENT}\nC:\\path\\1\n{END_COMMENT}")

        self.assertEqual(updated, readme_with("C:\\path\\1"))

    def test_raises_when_markers_are_missing(self):
        with self.assertRaises(ValueError):
            update_readme("# Title\n", f"{START_COMMENT}\nNEW\n{END_COMMENT}")


class UpdateReadmeFileTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.readme_path = Path(self.temp_dir.name) / "README.md"
        self.original = readme_with("[![Old](https://old.png)](https://old)")
        self.readme_path.write_bytes(self.original.encode("utf-8"))
        self.fetch = FakeFetch({
            f"{CREDLY_BADGES_URL}?page=1": page([credly_item("aws-1", "AWS", "2026-07-27")]),
            f"{EXTERNAL_BADGES_URL}?page=1": page([external_item("OCI", "2025-09-02")]),
        })

    def tearDown(self):
        self.temp_dir.cleanup()

    def read_readme(self):
        return self.readme_path.read_bytes().decode("utf-8")

    def test_writes_all_badges_and_is_idempotent(self):
        changed = update_readme_file(self.readme_path, USER, 0, self.fetch)
        first_run = self.read_readme()
        changed_again = update_readme_file(self.readme_path, USER, 0, self.fetch)

        self.assertTrue(changed)
        self.assertFalse(changed_again)
        self.assertEqual(self.read_readme(), first_run)
        self.assertIn('alt="AWS"', first_run)
        self.assertIn('alt="OCI"', first_run)
        self.assertEqual(first_run.count(f'width="{BADGE_SIZE_PX}" height="{BADGE_SIZE_PX}"'), 2)
        self.assertTrue(first_run.endswith("## Projects\n"))

    def test_leaves_readme_unchanged_when_no_badges_are_found(self):
        fetch = FakeFetch({
            f"{CREDLY_BADGES_URL}?page=1": page([]),
            f"{EXTERNAL_BADGES_URL}?page=1": page([]),
        })

        changed = update_readme_file(self.readme_path, USER, 0, fetch)

        self.assertFalse(changed)
        self.assertEqual(self.read_readme(), self.original)

    def test_leaves_readme_unchanged_when_credly_request_fails(self):
        def failing_fetch(url):
            raise urllib.error.URLError("timeout")

        with self.assertRaises(urllib.error.URLError):
            update_readme_file(self.readme_path, USER, 0, failing_fetch)

        self.assertEqual(self.read_readme(), self.original)


if __name__ == "__main__":
    unittest.main()
