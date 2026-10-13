import html
import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

CREDLY_BASE_URL = "https://www.credly.com"
CREDLY_IMAGES_URL = "https://images.credly.com/"
CREDLY_SIZED_IMAGES_URL = "https://images.credly.com/size/80x80/"
BADGE_SIZE_PX = 80
START_COMMENT = "<!--START_SECTION:badges-->"
END_COMMENT = "<!--END_SECTION:badges-->"
SECTION_PATTERN = re.compile(f"{re.escape(START_COMMENT)}[\\s\\S]*?{re.escape(END_COMMENT)}")
MAX_PAGES = 20
REQUEST_TIMEOUT_SECONDS = 30
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
SAFE_LINK_PREFIX = "https://"

Fetch = Callable[[str], dict]


@dataclass(frozen=True)
class Badge:
    name: str
    image_url: str
    link: str
    issued_at_date: str


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.load(response)


def fetch_all_pages(url: str, fetch: Fetch) -> list:
    items = []
    for page in range(1, MAX_PAGES + 1):
        payload = fetch(f"{url}?page={page}")
        items.extend(payload["data"])
        if page >= payload["metadata"]["total_pages"]:
            break
    return items


def parse_credly_badge(item: dict) -> Badge:
    return Badge(
        name=item["badge_template"]["name"],
        image_url=item["image_url"],
        link=f"{CREDLY_BASE_URL}/badges/{item['id']}",
        issued_at_date=item["issued_at_date"],
    )


def parse_external_badge(item: dict, fallback_link: str) -> Badge:
    external_badge = item["external_badge"]
    badge_url = external_badge.get("badge_url") or ""
    return Badge(
        name=external_badge["badge_name"],
        image_url=external_badge["image_url"],
        link=badge_url if badge_url.startswith(SAFE_LINK_PREFIX) else fallback_link,
        issued_at_date=external_badge["issued_at_date"],
    )


def fetch_badges(user: str, fetch: Fetch = fetch_json) -> list[Badge]:
    credly_items = fetch_all_pages(f"{CREDLY_BASE_URL}/users/{user}/badges.json", fetch)
    external_items = fetch_all_pages(f"{CREDLY_BASE_URL}/api/v1/users/{user}/external_badges/open_badges/public", fetch)
    profile_badges_url = f"{CREDLY_BASE_URL}/users/{user}/badges"
    return [parse_credly_badge(item) for item in credly_items] + [
        parse_external_badge(item, profile_badges_url) for item in external_items
    ]


def select_badges(badges: list[Badge], limit: int) -> list[Badge]:
    newest_first = sorted(badges, key=lambda badge: badge.issued_at_date, reverse=True)
    return newest_first[:limit] if limit > 0 else newest_first


def render_badges(badges: list[Badge]) -> str:
    lines = [START_COMMENT, '<p align="left">']
    for badge in badges:
        name = html.escape(badge.name)
        link = html.escape(badge.link)
        image_url = html.escape(badge.image_url.replace(CREDLY_IMAGES_URL, CREDLY_SIZED_IMAGES_URL, 1))
        lines.append(
            f'  <a href="{link}" title="{name}">'
            f'<img src="{image_url}" alt="{name}" width="{BADGE_SIZE_PX}" height="{BADGE_SIZE_PX}"/></a>'
        )
    lines += ["</p>", END_COMMENT]
    return "\n".join(lines)


def update_readme(readme: str, badges_section: str) -> str:
    if not SECTION_PATTERN.search(readme):
        raise ValueError(f"Badges section {START_COMMENT} ... {END_COMMENT} not found in README")
    return SECTION_PATTERN.sub(lambda _: badges_section, readme, count=1)


def update_readme_file(readme_path: Path, user: str, limit: int, fetch: Fetch = fetch_json) -> bool:
    badges = select_badges(fetch_badges(user, fetch), limit)
    if not badges:
        print(f"No badges found for Credly user {user}; README left unchanged")
        return False

    with open(readme_path, encoding="utf-8", newline="") as file:
        readme = file.read()

    new_readme = update_readme(readme, render_badges(badges))
    if new_readme == readme:
        print(f"{len(badges)} badges already up to date")
        return False

    with open(readme_path, "w", encoding="utf-8", newline="") as file:
        file.write(new_readme)
    print(f"README updated with {len(badges)} badges")
    return True


def main() -> int:
    user = os.environ["CREDLY_USER"]
    limit = int(os.environ.get("NUMBER_LAST_BADGES") or 0)
    readme_path = Path(os.environ.get("README_PATH", "README.md"))
    update_readme_file(readme_path, user, limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
