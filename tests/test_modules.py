import functools
import http.server
import tempfile
import threading
import unittest
from pathlib import Path

from seo_workhorse import audit, cluster, gsc, redirects
from seo_workhorse.report import write_report

HERE = Path(__file__).parent
EXAMPLES = HERE.parent / "examples"


class GscTest(unittest.TestCase):
    def test_quick_wins_ctr_gaps_and_decay(self):
        sheets = gsc.run(EXAMPLES / "gsc_pages_current.csv", EXAMPLES / "gsc_pages_previous.csv")
        wins = sheets["Quick wins (pos 4-20)"]["key"].tolist()
        self.assertIn("https://example.com/blog/seo-audit-guide/", wins)
        self.assertNotIn("https://example.com/", wins)  # position 2 is not a quick win
        self.assertIn("https://example.com/blog/backlinks/", sheets["CTR gaps (page 1)"]["key"].tolist())
        decayed = sheets["Content decay"].set_index("key")
        self.assertIn("https://example.com/blog/technical-seo-checklist/", decayed.index)
        self.assertIn("Gone from results", decayed.loc["https://example.com/blog/schema-markup/", "likely_cause"])
        self.assertNotIn("https://example.com/blog/meta-descriptions/", decayed.index)


class ClusterTest(unittest.TestCase):
    def test_related_keywords_share_a_cluster(self):
        kw = cluster.run(EXAMPLES / "keywords.csv")["Keywords"].set_index("keyword")
        self.assertEqual(kw.loc["seo audit tool", "cluster"], "seo audit")
        self.assertEqual(kw.loc["free keyword research tool", "cluster"], kw.loc["keyword research tool", "cluster"])
        self.assertNotEqual(kw.loc["backlink checker", "cluster"], kw.loc["seo audit", "cluster"])
        self.assertEqual(kw.loc["buy backlinks", "intent"], "transactional")
        self.assertEqual(kw.loc["how to do keyword research", "intent"], "informational")


class RedirectTest(unittest.TestCase):
    def test_map(self):
        sheets = redirects.run(str(EXAMPLES / "old_urls.csv"), str(EXAMPLES / "new_urls.csv"))
        m = sheets["Redirect map"].set_index("old_url")["new_url"]
        self.assertEqual(m["https://old-site.com/services/seo-audit.html"], "https://new-site.com/services/seo-audit/")
        self.assertEqual(m["https://old-site.com/blog/2021/05/keyword-research-guide"], "https://new-site.com/blog/keyword-research-guide/")
        self.assertEqual(m["https://old-site.com/about-us.html"], "https://new-site.com/about/")
        self.assertEqual(m["https://old-site.com/contact.php"], "https://new-site.com/contact/")
        # Unrelated page falls back to the closest parent folder, not a random page.
        self.assertEqual(m["https://old-site.com/blog/2020/03/press-release-launch"], "https://new-site.com/blog/")
        self.assertEqual(m["https://old-site.com/blog/2022/08/what-is-technical-seo"], "https://new-site.com/blog/technical-seo-explained/")
        htaccess = redirects.to_htaccess(sheets["Redirect map"])
        self.assertIn("Redirect 301 /services/seo-audit.html https://new-site.com/services/seo-audit/", htaccess)
        self.assertNotIn("Redirect 301 / https://new-site.com/\n", htaccess)
        self.assertIn("Redirect 301 /contact.php https://new-site.com/contact/", htaccess)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class AuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = functools.partial(QuietHandler, directory=str(HERE / "site"))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_crawl_finds_issues(self):
        sheets = audit.run(self.base + "/index.html", max_pages=10, delay=0)
        found = set(zip(sheets["Issues"]["issue"], sheets["Issues"]["url"]))
        post, copy = self.base + "/blog/post.html", self.base + "/blog/copy.html"
        self.assertIn(("HTTP 404", self.base + "/missing.html"), found)
        self.assertIn(("Duplicate title", post), found)
        self.assertIn(("Duplicate meta description", copy), found)
        self.assertIn(("Noindex", copy), found)
        self.assertIn(("Canonical points elsewhere", copy), found)
        self.assertIn(("Multiple H1s", post), found)
        self.assertIn(("Missing meta description", self.base + "/index.html"), found)
        self.assertIn(("Images missing alt text", self.base + "/index.html"), found)
        self.assertIn(self.base + "/index.html", sheets["Broken links"]["linked_from"].tolist())
        self.assertFalse(any("other-site.com" in u for u in sheets["All pages"]["url"]))


class ReportTest(unittest.TestCase):
    def test_writes_xlsx(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = write_report(cluster.run(EXAMPLES / "keywords.csv"), Path(tmp) / "out.xlsx")
            self.assertTrue(out.exists() and out.stat().st_size > 0)


if __name__ == "__main__":
    unittest.main()
