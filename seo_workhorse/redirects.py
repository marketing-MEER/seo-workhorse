"""Site migration redirect mapper.

Matches every old URL to the most similar new URL and writes a 301 map with a
confidence score, ready for .htaccess, nginx or a CSV import.
"""
import re
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

from .report import find_column

USER_AGENT = "seo-workhorse/1.0 (+https://github.com/marketing-MEER/seo-workhorse)"
NOISE = {"html", "htm", "php", "aspx", "index", "www", "en", "de", "page", "p",
         "a", "an", "the", "and", "or", "of", "to", "in", "for", "is", "what", "how", "why", "us"}


def load_urls(source: str) -> list[str]:
    """Read URLs from a sitemap URL, a .xml file, a .csv (url column) or a .txt (one per line)."""
    if source.startswith(("http://", "https://")):
        resp = requests.get(source, headers={"User-Agent": USER_AGENT}, timeout=30)
        resp.raise_for_status()
        return _parse_sitemap(resp.content)
    path = Path(source)
    if path.suffix.lower() == ".xml":
        return _parse_sitemap(path.read_bytes())
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
        col = find_column(df, ["url", "address", "urls", "page", "top pages", "old url", "new url"]) or df.columns[0]
        return [u for u in df[col].dropna().astype(str).str.strip() if u]
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _parse_sitemap(content: bytes) -> list[str]:
    root = ET.fromstring(content)
    urls = [el.text.strip() for el in root.iter() if el.tag.endswith("loc") and el.text]
    # A sitemap index lists other sitemaps: follow them.
    if root.tag.endswith("sitemapindex"):
        nested = []
        for sm in urls:
            nested.extend(load_urls(sm))
        return nested
    return urls


def path_of(url: str) -> str:
    parsed = urlparse(url if "://" in url else "https://x" + ("" if url.startswith("/") else "/") + url)
    return parsed.path.rstrip("/") or "/"


def slug_words(url: str) -> list[str]:
    words = re.findall(r"[a-z0-9äöüß]+", path_of(url).lower())
    return [w for w in words if w not in NOISE]


def score(old: str, new: str, old_title: str = "", new_title: str = "") -> float:
    old_path, new_path = path_of(old), path_of(new)
    if old_path == new_path:
        return 1.0
    if old_path.rsplit("/", 1)[-1] == new_path.rsplit("/", 1)[-1] and old_path != "/":
        return 0.95
    a, b = slug_words(old), slug_words(new)
    words = SequenceMatcher(None, " ".join(sorted(a)), " ".join(sorted(b))).ratio()
    order = SequenceMatcher(None, " ".join(a), " ".join(b)).ratio()
    last = SequenceMatcher(None, a[-1] if a else "", b[-1] if b else "").ratio()
    result = 0.4 * words + 0.2 * order + 0.4 * last
    # "about-us" vs "about": one final slug fully contains the other's words.
    old_last = set(re.findall(r"[a-z0-9äöüß]+", old_path.rsplit("/", 1)[-1].lower())) - NOISE
    new_last = set(re.findall(r"[a-z0-9äöüß]+", new_path.rsplit("/", 1)[-1].lower())) - NOISE
    shorter = min(old_last, new_last, key=len)
    if shorter and (old_last <= new_last or new_last <= old_last) and max(len(w) for w in shorter) >= 4:
        result = max(result, 0.75)
    if old_title and new_title:
        title = SequenceMatcher(None, old_title.lower(), new_title.lower()).ratio()
        result = 0.5 * result + 0.5 * title
    return round(min(result, 0.99), 3)


def fetch_titles(urls: list[str]) -> dict:
    titles = {}
    for url in urls:
        try:
            resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")
            h1 = soup.find("h1")
            titles[url] = (soup.title.get_text(strip=True) if soup.title else "") or (h1.get_text(strip=True) if h1 else "")
        except requests.RequestException:
            titles[url] = ""
    return titles


def build_map(old_urls: list[str], new_urls: list[str], min_score: float = 0.6, use_titles: bool = False) -> pd.DataFrame:
    titles = fetch_titles(old_urls + new_urls) if use_titles else {}
    new_paths = {path_of(u): u for u in new_urls}
    rows = []
    for old in old_urls:
        best, best_score = None, -1.0
        for new in new_urls:
            s = score(old, new, titles.get(old, ""), titles.get(new, ""))
            if s > best_score:
                best, best_score = new, s
                if s == 1.0:
                    break
        status = "ok" if best_score >= min_score else "review"
        if status == "review":
            best = _fallback_parent(old, new_paths) or best
        rows.append({
            "old_url": old,
            "new_url": best,
            "confidence": best_score,
            "status": status,
            "note": "Same path, no redirect needed" if path_of(old) == path_of(best)
            else ("Low confidence: mapped to closest parent, check by hand" if status == "review" else ""),
        })
    return pd.DataFrame(rows).sort_values(["status", "confidence"], ascending=[False, True])


def _fallback_parent(old: str, new_paths: dict) -> str | None:
    """Walk up the old path until a folder exists on the new site (avoids dumping everything on /)."""
    parts = path_of(old).strip("/").split("/")
    while parts:
        parts.pop()
        candidate = "/" + "/".join(parts) if parts else "/"
        if candidate in new_paths:
            return new_paths[candidate]
    return None


def _needs_redirect(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["old_url"].map(path_of) != df["new_url"].map(path_of)]


def to_htaccess(df: pd.DataFrame) -> str:
    lines = ["# 301 redirects generated by seo-workhorse"]
    for _, r in _needs_redirect(df).iterrows():
        lines.append(f"Redirect 301 {path_of(r['old_url'])} {r['new_url']}")
    return "\n".join(lines) + "\n"


def to_nginx(df: pd.DataFrame) -> str:
    lines = ["# 301 redirects generated by seo-workhorse (put inside the server block)"]
    for _, r in _needs_redirect(df).iterrows():
        lines.append(f"location = {path_of(r['old_url'])} {{ return 301 {r['new_url']}; }}")
    return "\n".join(lines) + "\n"


def run(old_source: str, new_source: str, min_score: float = 0.6, use_titles: bool = False) -> dict:
    mapping = build_map(load_urls(old_source), load_urls(new_source), min_score, use_titles)
    return {
        "Redirect map": mapping,
        "Needs review": mapping[mapping["status"] == "review"],
    }
