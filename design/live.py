"""Shared helpers for the top section: live numbers from the GitHub API and Space Mono embedded as a subset."""

import base64
import json
import os
import subprocess
import urllib.request
from io import BytesIO
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).parent
USER = "Shrivas29"


def token() -> str | None:
    if os.environ.get("GITHUB_TOKEN"):
        return os.environ["GITHUB_TOKEN"]
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def stats() -> dict:
    """Public repos, live sites (repos with a homepage) and this year's contributions."""
    query = '{ user(login: "%s") { repositories(privacy: PUBLIC, first: 100, ownerAffiliations: OWNER) { totalCount nodes { name homepageUrl } } contributionsCollection { contributionCalendar { totalContributions } } } }' % USER
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": query}).encode(), headers={"Authorization": f"bearer {token()}", "User-Agent": USER})
    data = json.load(urllib.request.urlopen(req))["data"]["user"]
    repos = data["repositories"]
    return {
        "repos": repos["totalCount"],
        "live": sum(1 for n in repos["nodes"] if n["homepageUrl"] and n["name"] != USER),
        "contributions": data["contributionsCollection"]["contributionCalendar"]["totalContributions"],
    }


def embedded_font(chars: str) -> str:
    rules = ""
    for weight, name in ((400, "SpaceMono-Regular"), (700, "SpaceMono-Bold")):
        font = TTFont(HERE / "fonts" / f"{name}.ttf")
        sub = subset.Subsetter(subset.Options(flavor="woff2", layout_features=["*"], name_IDs=["*"]))
        sub.populate(text=chars)
        sub.subset(font)
        buf = BytesIO()
        font.flavor = "woff2"
        font.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        rules += f'@font-face{{font-family:"SM";font-weight:{weight};src:url(data:font/woff2;base64,{data}) format("woff2")}}'
    return rules
