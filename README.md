# seo-workhorse

**Free, open-source automation for the SEO jobs that eat your week.**

Technical audits, keyword clustering, migration redirect maps and Search Console analysis are some of the most repetitive tasks in SEO. Most teams still do them by hand in spreadsheets, every week. `seo-workhorse` does each one with a single command and gives you a clean Excel report.

- No paid APIs, no API keys, no subscriptions
- Works with the exports you already have (Ahrefs, Semrush, Google Search Console, Screaming Frog, sitemaps)
- Includes Claude Code skills that turn the reports into rewritten metas, content briefs and a 30-day action plan

[![tests](https://github.com/meer5-seo/seo-workhorse/actions/workflows/ci.yml/badge.svg)](https://github.com/meer5-seo/seo-workhorse/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

---

## What it automates

| Command | The manual job it replaces | What you get |
|---|---|---|
| `seo-workhorse audit` | Clicking through a site, checking titles, metas, H1s, canonicals, broken links and redirects page by page | Excel with a summary, every issue ranked by priority, broken links with the page that links to them, and a full page list |
| `seo-workhorse cluster` | Sorting hundreds of keywords into topics in a spreadsheet | Topic clusters named after their biggest keyword, total volume per cluster and the search intent of every keyword |
| `seo-workhorse redirects` | Matching old URLs to new URLs one by one before a migration | A 301 map with a confidence score, a "needs review" list, and ready-to-paste `.htaccess` and nginx rules |
| `seo-workhorse gsc` | Filtering GSC exports for pages that are close to ranking, under-clicked or losing traffic | Quick wins (positions 4–20), CTR gaps on page 1, and content decay with the likely cause |

## Install

```bash
git clone https://github.com/meer5-seo/seo-workhorse.git
cd seo-workhorse
pip install -e .
```

Requires Python 3.10+. Try it on the sample data in `examples/` first.

## Usage

### 1. Technical SEO audit
```bash
seo-workhorse audit https://www.example.com --max-pages 500 -o audit.xlsx
```
Crawls the site (same domain only, respects `robots.txt`, waits between requests) and flags:
HTTP 4xx/5xx · redirect chains · missing, duplicate, too long or too short titles and meta descriptions · missing or multiple H1s · missing or cross-pointing canonicals · noindex · thin content · images without alt text · broken internal links with their source page.

### 2. Keyword clustering
```bash
seo-workhorse cluster examples/keywords.csv -o clusters.xlsx
```
Reads any keyword CSV: it finds the keyword and volume columns of Ahrefs, Semrush or GSC exports by itself. `--threshold 0.6` gives tighter clusters, `0.4` looser ones.

### 3. Migration redirect map
```bash
seo-workhorse redirects https://old-site.com/sitemap.xml new_urls.csv -o redirect_map.xlsx
```
Both inputs can be a sitemap URL, an `.xml` file, a `.csv` with a URL column or a `.txt` with one URL per line. Matching uses the URL path, the slug words and, with `--use-titles`, the page titles. A URL with no good match goes to its closest parent folder (never the homepage by default) and is flagged for review.
Output: `redirect_map.xlsx`, `redirect_map.htaccess`, `redirect_map.nginx.conf`.

### 4. Search Console quick wins and content decay
```bash
seo-workhorse gsc pages_last_3_months.csv --previous pages_previous_3_months.csv -o gsc.xlsx
```
Export the **Pages** or **Queries** table from GSC → Performance as CSV. Add `--previous` with an export from an earlier period to find decaying pages.

## Claude Code skills (optional AI layer)

The `skills/` folder holds three [Claude Code](https://claude.com/claude-code) skills that take over where the reports stop:

| Skill | Turns this | Into this |
|---|---|---|
| `seo-meta-rewrite` | Title/meta issues from `audit`, or CTR gaps from `gsc` | New titles and meta descriptions within the length limits, with the reason for each change |
| `seo-cluster-brief` | Clusters from `cluster` | One content brief per cluster: intent, H2 outline, FAQs, internal links and a GEO / AI-search note |
| `seo-quickwin-plan` | `gsc` output | A prioritised 30-day action plan with one concrete task per page |

To use them, copy the folders into your project's `.claude/skills/` (or `~/.claude/skills/`). Then ask Claude: *"rewrite the metas from audit.xlsx"*.

## Run the tests
```bash
python -m unittest discover -s tests -t . -v
```

## Contributing
Issues and pull requests are welcome, especially new checks, export formats and languages.

## License
MIT. Free for personal and commercial use.

---

## Author

**Meer Hamza** · SEO Team Lead · Berlin

10+ years in SEO, AEO and GEO across in-house and agency teams. I built these scripts to stop doing the same spreadsheet work every week, and I'm sharing them so you can stop too.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Meer%20Hamza-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)
[![Email](https://img.shields.io/badge/Email-meerhamza5%40gmail.com-D14836?logo=gmail&logoColor=white)](mailto:meerhamza5@gmail.com)

If this saved you time, a ⭐ on the repo helps others find it.
