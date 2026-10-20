"""Technical SEO audit crawler.

Crawls one site (same host only), respects robots.txt, and flags the issues an
SEO checks by hand every week: broken links, redirect chains, titles, meta
descriptions, H1s, canonicals, noindex, thin pages and images without alt.
"""
import time
from collections import Counter, defaultdict, deque
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import pandas as pd
import requests
from bs4 import BeautifulSoup

USER_AGENT = "seo-workhorse/1.0 (+https://github.com/meer5-seo/seo-workhorse)"
SKIP_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf", ".zip", ".mp4", ".mp3", ".css", ".js", ".ico", ".xml")

TITLE_MIN, TITLE_MAX = 30, 60
META_MIN, META_MAX = 70, 160
THIN_WORDS = 300


class Crawler:
    def __init__(self, start_url: str, max_pages: int = 200, delay: float = 0.5, session=None, respect_robots: bool = True):
        self.start = start_url
        self.host = urlparse(start_url).netloc
        self.max_pages = max_pages
        self.delay = delay
        self.session = session or requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self.robots = self._load_robots() if respect_robots else None
        self.pages = []                    # one dict per fetched URL
        self.inlinks = defaultdict(set)    # target -> pages linking to it

    def _load_robots(self):
        parsed = urlparse(self.start)
        rp = RobotFileParser()
        try:
            resp = self.session.get(f"{parsed.scheme}://{parsed.netloc}/robots.txt", timeout=10)
            rp.parse(resp.text.splitlines() if resp.status_code == 200 else [])
        except requests.RequestException:
            rp.parse([])
        return rp

    def _normalise(self, base: str, href: str) -> str | None:
        if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
            return None
        url = urldefrag(urljoin(base, href))[0]
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or parsed.netloc != self.host:
            return None
        if parsed.path.lower().endswith(SKIP_EXT):
            return None
        return url

    def crawl(self, progress=None) -> "Crawler":
        queue, seen = deque([self.start]), {self.start}
        while queue and len(self.pages) < self.max_pages:
            url = queue.popleft()
            if self.robots and not self.robots.can_fetch(USER_AGENT, url):
                self.pages.append({"url": url, "status": "blocked by robots.txt"})
                continue
            page, links = self._fetch(url)
            self.pages.append(page)
            if progress:
                progress(len(self.pages), url, page.get("status"))
            for link in links:
                self.inlinks[link].add(url)
                if link not in seen:
                    seen.add(link)
                    queue.append(link)
            if self.delay:
                time.sleep(self.delay)
        return self

    def _fetch(self, url: str):
        try:
            resp = self.session.get(url, timeout=20, allow_redirects=True)
        except requests.RequestException as exc:
            return {"url": url, "status": "error", "error": str(exc)[:200]}, []

        page = {
            "url": url,
            "status": resp.status_code,
            "final_url": resp.url,
            "redirect_hops": len(resp.history),
            "redirect_chain": " -> ".join([r.url for r in resp.history] + [resp.url]) if resp.history else "",
            "content_type": resp.headers.get("Content-Type", ""),
            "response_ms": int(resp.elapsed.total_seconds() * 1000),
        }
        if resp.status_code != 200 or "html" not in page["content_type"]:
            return page, []

        soup = BeautifulSoup(resp.text, "html.parser")
        robots_meta = soup.find("meta", attrs={"name": lambda v: v and v.lower() == "robots"})
        canonical = soup.find("link", rel=lambda v: v and "canonical" in v)
        description = soup.find("meta", attrs={"name": lambda v: v and v.lower() == "description"})
        h1s = [h.get_text(" ", strip=True) for h in soup.find_all("h1")]
        images = soup.find_all("img")
        links = {link for a in soup.find_all("a", href=True) if (link := self._normalise(resp.url, a["href"]))}

        for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
            tag.decompose()

        page.update({
            "title": soup.title.get_text(strip=True) if soup.title else "",
            "meta_description": description.get("content", "").strip() if description else "",
            "h1": " | ".join(h1s),
            "h1_count": len(h1s),
            "canonical": urljoin(resp.url, canonical["href"]) if canonical and canonical.get("href") else "",
            "noindex": bool(robots_meta and "noindex" in robots_meta.get("content", "").lower()),
            "word_count": len(soup.get_text(" ", strip=True).split()),
            "images_missing_alt": sum(1 for img in images if not img.get("alt", "").strip()),
            "internal_links_out": len(links),
        })
        return page, links


def find_issues(pages: pd.DataFrame) -> pd.DataFrame:
    issues = []

    def add(url, issue, detail="", priority="medium"):
        issues.append({"priority": priority, "issue": issue, "url": url, "detail": detail})

    html = pages[(pages["status"] == 200) & pages["title"].notna()] if "title" in pages.columns else pages.iloc[0:0]
    title_counts = Counter(html["title"].str.lower()) if not html.empty else Counter()
    meta_counts = Counter(html["meta_description"].str.lower()) if not html.empty else Counter()

    for _, p in pages.iterrows():
        url, status = p["url"], p["status"]
        if status == "error":
            add(url, "Request failed", p.get("error", ""), "high")
            continue
        if isinstance(status, int) and status >= 400:
            add(url, f"HTTP {status}", "Page returns an error", "high")
        if p.get("redirect_hops", 0) and p["redirect_hops"] >= 2:
            add(url, "Redirect chain", p["redirect_chain"], "medium")

    for _, p in html.iterrows():
        url, title, meta = p["url"], p["title"], p["meta_description"]
        if p["noindex"]:
            add(url, "Noindex", "Page asks search engines not to index it. Intended?", "high")
        if not title:
            add(url, "Missing title", priority="high")
        else:
            if len(title) > TITLE_MAX:
                add(url, "Title too long", f"{len(title)} chars: {title}", "low")
            elif len(title) < TITLE_MIN:
                add(url, "Title too short", f"{len(title)} chars: {title}", "low")
            if title_counts[title.lower()] > 1:
                add(url, "Duplicate title", title, "medium")
        if not meta:
            add(url, "Missing meta description", priority="medium")
        else:
            if len(meta) > META_MAX:
                add(url, "Meta description too long", f"{len(meta)} chars", "low")
            elif len(meta) < META_MIN:
                add(url, "Meta description too short", f"{len(meta)} chars", "low")
            if meta_counts[meta.lower()] > 1:
                add(url, "Duplicate meta description", meta, "medium")
        if p["h1_count"] == 0:
            add(url, "Missing H1", priority="medium")
        elif p["h1_count"] > 1:
            add(url, "Multiple H1s", p["h1"], "low")
        if not p["canonical"]:
            add(url, "Missing canonical", priority="low")
        elif p["canonical"].rstrip("/") != p["final_url"].rstrip("/"):
            add(url, "Canonical points elsewhere", p["canonical"], "medium")
        if p["word_count"] < THIN_WORDS:
            add(url, "Thin content", f"{p['word_count']} words", "medium")
        if p["images_missing_alt"]:
            add(url, "Images missing alt text", f"{p['images_missing_alt']} images", "low")

    order = {"high": 0, "medium": 1, "low": 2}
    df = pd.DataFrame(issues, columns=["priority", "issue", "url", "detail"])
    return df.sort_values(by="priority", key=lambda s: s.map(order), kind="stable")


def broken_links(crawler: Crawler, pages: pd.DataFrame) -> pd.DataFrame:
    bad = pages[pages["status"].apply(lambda s: s == "error" or (isinstance(s, int) and s >= 400))]
    rows = [
        {"broken_url": p["url"], "status": p["status"], "linked_from": src}
        for _, p in bad.iterrows()
        for src in sorted(crawler.inlinks.get(p["url"], []))
    ]
    return pd.DataFrame(rows, columns=["broken_url", "status", "linked_from"])


def run(start_url: str, max_pages: int = 200, delay: float = 0.5, progress=None, session=None) -> dict:
    crawler = Crawler(start_url, max_pages=max_pages, delay=delay, session=session).crawl(progress)
    pages = pd.DataFrame(crawler.pages)
    if "redirect_hops" in pages:
        pages["redirect_hops"] = pages["redirect_hops"].fillna(0).astype(int)
    issues = find_issues(pages)
    summary = (
        issues.groupby(["priority", "issue"]).size().reset_index(name="pages")
        .sort_values(by="priority", key=lambda s: s.map({"high": 0, "medium": 1, "low": 2}), kind="stable")
    )
    return {
        "Summary": summary,
        "Issues": issues,
        "Broken links": broken_links(crawler, pages),
        "All pages": pages,
    }
