#!/usr/bin/env python3
"""更新分类文件中 GitHub 项目的 Star 数。"""

import os
import re
import json
import requests
from pathlib import Path

TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}
CATEGORIES_DIR = Path("categories")
REPO_PATTERN = re.compile(r"https://github\.com/([^/]+/[^/)\s]+)")
STAR_PATTERN = re.compile(r"(\| \[.*?\]\(https://github\.com/[^)]+\) \| )([^|]+)( \|)")


def get_stars(owner_repo: str) -> str:
    """获取仓库 Star 数，返回如 12.3k 的字符串。"""
    url = f"https://api.github.com/repos/{owner_repo}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    if resp.status_code != 200:
        return "N/A"
    stars = resp.json().get("stargazers_count", 0)
    if stars >= 1000:
        return f"{stars / 1000:.1f}k"
    return str(stars)


def update_file(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        match = STAR_PATTERN.search(line)
        if match:
            repo_match = REPO_PATTERN.search(line)
            if repo_match:
                owner_repo = repo_match.group(1)
                stars = get_stars(owner_repo)
                line = STAR_PATTERN.sub(rf"\g<1>{stars}\g<3>", line)
        new_lines.append(line)
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def main():
    for md in CATEGORIES_DIR.glob("*.md"):
        print(f"Updating {md}...")
        update_file(md)
    print("Done.")


if __name__ == "__main__":
    main()