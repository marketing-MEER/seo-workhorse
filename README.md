<div align="center">

# 🐴 seo-workhorse

### Free, open-source automation for the SEO jobs that eat your week.

Technical audits · Keyword clustering · Migration redirect maps · Search Console quick wins

[![tests](https://github.com/marketing-MEER/seo-workhorse/actions/workflows/ci.yml/badge.svg)](https://github.com/marketing-MEER/seo-workhorse/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![No API keys](https://img.shields.io/badge/API%20keys-none%20needed-brightgreen)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Meer%20Hamza-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)

[🚀 Quick start](#-quick-start) · [🧰 The tools](#-the-tools) · [🤖 Claude skills](#-claude-code-skills-ai-layer) · [❓ FAQ](#-faq) · [👤 Author](#-author)

</div>

---

## 💡 Why this exists

Every SEO team repeats the same spreadsheet work every week:

- 🔍 clicking through a site to check titles, metas, H1s and broken links
- 🗂️ sorting hundreds of keywords into topics by hand
- 🔀 matching old URLs to new URLs one by one before a migration
- 📉 filtering Search Console exports for pages that are close to page 1

**seo-workhorse turns each of these into one command and a clean, formatted Excel report.** You keep the thinking; the tool does the grunt work.

✅ **Free and MIT licensed**   ✅ **No API keys or subscriptions**   ✅ **Works with the exports you already have** (Ahrefs, Semrush, Google Search Console, sitemaps)

---

## 🚀 Quick start

```bash
git clone https://github.com/marketing-MEER/seo-workhorse.git
cd seo-workhorse
pip install -e .
```

Try every tool on the sample data in [`examples/`](examples/) before you use your own:

```bash
seo-workhorse gsc examples/gsc_pages_current.csv --previous examples/gsc_pages_previous.csv
seo-workhorse cluster examples/keywords.csv
seo-workhorse redirects examples/old_urls.csv examples/new_urls.csv
seo-workhorse audit https://books.toscrape.com --max-pages 15
```

> [!TIP]
> Run `seo-workhorse --help` or `seo-workhorse <tool> --help` to see every option.
> If the `seo-workhorse` command isn't found, use `python -m seo_workhorse` instead.

---

## 🧰 The tools

| | Tool | Replaces this manual job | You get |
|---|---|---|---|
| 🔍 | [`audit`](#-audit--technical-seo-crawler) | Checking pages one by one for technical issues | Every issue, ranked by priority |
| 🗂️ | [`cluster`](#️-cluster--keyword-clustering) | Grouping keywords into topics in a spreadsheet | Topic clusters + search intent |
| 🔀 | [`redirects`](#-redirects--migration-redirect-mapper) | Matching old and new URLs before a migration | 301 map + `.htaccess` + nginx rules |
| 📈 | [`gsc`](#-gsc--search-console-quick-wins--content-decay) | Filtering GSC exports for opportunities | Quick wins, CTR gaps, decaying pages |

---

### 🔍 `audit` · Technical SEO crawler

Crawls your website like a search engine would and lists every technical issue it finds, sorted by priority.

```bash
seo-workhorse audit https://www.example.com --max-pages 500 -o audit.xlsx
```

**What it checks**

| Priority | Checks |
|---|---|
| 🔴 High | HTTP 4xx / 5xx errors · failed requests · `noindex` pages · missing titles |
| 🟠 Medium | Duplicate titles and meta descriptions · missing meta descriptions · missing H1 · canonical pointing to another URL · redirect chains (2+ hops) · thin content (under 300 words) |
| 🟡 Low | Titles outside 30–60 characters · meta descriptions outside 70–160 characters · multiple H1s · missing canonical · images without alt text |

**Options**

| Option | Default | What it does |
|---|---|---|
| `--max-pages` | `200` | Stop after this many URLs |
| `--delay` | `0.5` | Seconds between requests, so you don't overload the server |
| `-o`, `--output` | `seo_audit.xlsx` | Where to save the report |

**The Excel report has 4 sheets:** `Summary` (issue counts) · `Issues` (one row per issue and page) · `Broken links` (the broken URL **and the page that links to it**) · `All pages` (status, title, meta, H1, canonical, word count, response time).

<details>
<summary>📄 Example: real Summary sheet from a 15-page crawl</summary>

| priority | issue | pages |
|---|---|---|
| medium | Duplicate title | 2 |
| medium | Missing meta description | 10 |
| medium | Thin content | 8 |
| low | Meta description too long | 5 |
| low | Missing canonical | 15 |
| low | Title too long | 2 |

</details>

> [!NOTE]
> The crawler stays on the same domain, respects `robots.txt` and identifies itself with its own user agent. Only crawl sites you own or have permission to audit.

---

### 🗂️ `cluster` · Keyword clustering

Groups a keyword list into topic clusters, names each cluster after its biggest keyword and tags the search intent of every keyword. It needs no SERP API.

```bash
seo-workhorse cluster keywords.csv -o clusters.xlsx
```

**Input:** any CSV export. The tool finds the keyword and volume columns by itself:

| Source | Columns it recognises |
|---|---|
| Ahrefs / Semrush | `Keyword` + `Volume` / `Search Volume` |
| Google Keyword Planner | `Keyword` + `Avg. monthly searches` |
| Google Search Console | `Top queries` / `Query` + `Impressions` |

**How it works**
1. It cleans each keyword: it removes filler words ("the", "for", "how to") and modifiers ("best", "free", "2026") and treats singular and plural as the same word.
2. It sorts keywords by volume. The biggest one starts the first cluster.
3. Each next keyword joins the cluster it shares the most core words with, or starts a new cluster if the overlap is below the threshold.
4. Intent is tagged from trigger words: 💰 transactional (*buy, price, hire*) · 🛒 commercial (*best, vs, review, tool*) · 📚 informational (*how, what, guide*) · 🔀 mixed.

**Options**

| Option | Default | What it does |
|---|---|---|
| `--threshold` | `0.5` | 0–1. Higher means tighter, smaller clusters. Try `0.4` for broader topics |
| `-o`, `--output` | `keyword_clusters.xlsx` | Where to save the report |

<details>
<summary>📄 Example: real output from <code>examples/keywords.csv</code></summary>

| cluster | keywords | total volume | main intent | sample keywords |
|---|---|---|---|---|
| keyword research | 5 | 35,480 | commercial | keyword research · keyword research tool · free keyword research tool · how to do keyword research |
| seo audit | 6 | 17,980 | mixed | seo audit · seo audit tool · free seo audit · website seo audit · technical seo audit |
| backlink checker | 2 | 15,700 | mixed | backlink checker · free backlink checker |
| best seo tools | 3 | 11,390 | commercial | best seo tools · seo tools free · seo tools comparison |
| internal linking | 3 | 4,910 | mixed | internal linking · internal linking strategy · internal links seo |

</details>

> [!TIP]
> Clustering compares the words in each keyword, not live Google results. Synonyms like "what is seo" and "seo meaning" can end up in separate clusters, so check the biggest clusters before you plan content around them.

---

### 🔀 `redirects` · Migration redirect mapper

Matches every old URL to the most similar new URL and writes a 301 redirect map, ready to paste into your server config.

```bash
seo-workhorse redirects https://old-site.com/sitemap.xml new_urls.csv -o redirect_map.xlsx
```

**Input:** both URL lists can be a **sitemap URL**, an **`.xml` file**, a **`.csv`** with a URL column (Screaming Frog `Address` works), or a **`.txt`** with one URL per line.

**How matching works**

| Match | Confidence | Example |
|---|---|---|
| Same path | 1.00 → no redirect needed | `/contact/` → `/contact/` |
| Same final slug | 0.95 | `/services/seo-audit.html` → `/services/seo-audit/` |
| One slug contains the other | 0.75 | `/about-us.html` → `/about/` |
| Word similarity of the path | 0–0.99 | `/blog/2022/08/what-is-technical-seo` → `/blog/technical-seo-explained/` |

When no match reaches `--min-score`, the URL goes to its **closest parent folder** (e.g. `/blog/`) instead of the homepage, and is flagged for review.

**Options**

| Option | Default | What it does |
|---|---|---|
| `--min-score` | `0.6` | Matches below this are flagged `review` |
| `--use-titles` | off | Also fetches every page's `<title>` to improve matching (slower) |
| `-o`, `--output` | `redirect_map.xlsx` | Where to save the report |

**You get 3 files:** `redirect_map.xlsx` (full map and a "Needs review" sheet) · `redirect_map.htaccess` (Apache) · `redirect_map.nginx.conf` (nginx)

<details>
<summary>📄 Example: real <code>.htaccess</code> output from the sample data</summary>

```apache
# 301 redirects generated by seo-workhorse
Redirect 301 /blog/2020/03/press-release-launch https://new-site.com/blog/
Redirect 301 /blog/2022/01/internal-linking-tips https://new-site.com/blog/internal-linking/
Redirect 301 /blog/2022/08/what-is-technical-seo https://new-site.com/blog/technical-seo-explained/
Redirect 301 /blog/2021/05/keyword-research-guide https://new-site.com/blog/keyword-research-guide/
Redirect 301 /services/seo-audit.html https://new-site.com/services/seo-audit/
Redirect 301 /services/link-building.html https://new-site.com/services/link-building/
Redirect 301 /about-us.html https://new-site.com/about/
Redirect 301 /contact.php https://new-site.com/contact/
```

</details>

> [!IMPORTANT]
> Always review the `Needs review` sheet before going live. A wrong redirect can cost more traffic than a missing one.

---

### 📈 `gsc` · Search Console quick wins & content decay

Reads a Google Search Console export and finds the pages where a small fix brings the most clicks.

```bash
seo-workhorse gsc pages_last_3_months.csv --previous pages_previous_3_months.csv -o gsc.xlsx
```

**How to export from GSC:** Performance → set the date range → **Pages** (or **Queries**) tab → Export → CSV. For content decay, export a second file for the earlier period and pass it with `--previous`.

**You get 3 sheets**

| Sheet | Finds | The rule |
|---|---|---|
| 🎯 **Quick wins** | Pages that are close to the top | Position 4–20, 100+ impressions. Ranked by extra clicks if the page reached position 3 |
| ✍️ **CTR gaps** | Page-1 results people don't click | CTR is under half of the typical CTR for that position, so the title and meta need a rewrite |
| 📉 **Content decay** | Pages losing traffic *(needs `--previous`)* | Lost 20%+ of clicks. Each row gets a likely cause |

**Likely causes for decay**

| Signal | Likely cause |
|---|---|
| 0 impressions now | 🛠️ Technical fault: check status code, `noindex`, canonical, redirects |
| Position dropped 3+ | 🏁 Competitors overtook you: refresh the content |
| Impressions down 30%+ | 📅 Demand fell: seasonality or lower search volume |
| Same rank, fewer clicks | 🤖 SERP features or AI Overviews taking clicks, or a weaker snippet |

**Options**

| Option | Default | What it does |
|---|---|---|
| `--previous` | — | Earlier-period export, enables the decay sheet |
| `--min-impressions` | `100` | Ignore rows with less demand than this |
| `-o`, `--output` | `gsc_opportunities.xlsx` | Where to save the report |

<details>
<summary>📄 Example: real Quick wins output from the sample data</summary>

| page | clicks | impressions | position | CTR % | potential extra clicks |
|---|---|---|---|---|---|
| /blog/seo-audit-guide/ | 85 | 12,000 | 6.4 | 0.71 | 1,235 |
| /blog/backlinks/ | 30 | 8,800 | 4.6 | 0.34 | 938 |
| /blog/internal-linking/ | 40 | 6,500 | 11.8 | 0.62 | 675 |
| /blog/technical-seo-checklist/ | 15 | 4,200 | 14.5 | 0.36 | 447 |

</details>

> [!NOTE]
> Expected CTR per position is based on typical industry averages (about 28% at #1 down to about 2.4% at #10). It's a benchmark for spotting outliers, not an exact forecast.

---

## 🤖 Claude Code skills (AI layer)

The reports show you **what** to fix. The skills in [`skills/`](skills/) let [Claude Code](https://claude.com/claude-code) do the follow-up work:

| Skill | Input | Output |
|---|---|---|
| ✍️ [`seo-meta-rewrite`](skills/seo-meta-rewrite/SKILL.md) | Title/meta issues from `audit`, or CTR gaps from `gsc` | New titles (50–60 chars) and meta descriptions (140–155 chars), with the reason for each change |
| 📝 [`seo-cluster-brief`](skills/seo-cluster-brief/SKILL.md) | Clusters from `cluster` | One content brief per cluster: intent, H2 outline, FAQs, internal links and a GEO / AI-search note |
| 🗓️ [`seo-quickwin-plan`](skills/seo-quickwin-plan/SKILL.md) | Output from `gsc` | A prioritised 30-day action plan with one concrete task per page |

**Set up:** copy the folders inside `skills/` into `.claude/skills/` in your project (or `~/.claude/skills/` for all projects). Then just ask:

```text
rewrite the titles and metas flagged in audit.xlsx
write content briefs for the top 10 clusters in clusters.xlsx
turn gsc.xlsx into a 30-day action plan
```

---

## 🔄 A typical weekly workflow

```text
Monday     📈  seo-workhorse gsc        → pick this week's quick wins
           🗓️  seo-quickwin-plan        → turn them into tasks
Tuesday    🔍  seo-workhorse audit      → fix new technical issues
           ✍️  seo-meta-rewrite         → rewrite the weak titles and metas
Monthly    🗂️  seo-workhorse cluster    → plan new content
           📝  seo-cluster-brief        → hand the briefs to writers
Migration  🔀  seo-workhorse redirects  → 301 map before launch day
```

---

## 📁 Project structure

```text
seo-workhorse/
├── seo_workhorse/        # the Python package
│   ├── cli.py            # the seo-workhorse command
│   ├── audit.py          # 🔍 technical crawler
│   ├── cluster.py        # 🗂️ keyword clustering
│   ├── redirects.py      # 🔀 redirect mapper
│   ├── gsc.py            # 📈 Search Console analysis
│   └── report.py         # shared Excel writer
├── skills/               # 🤖 Claude Code skills
├── examples/             # sample CSVs to try every tool
└── tests/                # automated tests (run on every push)
```

---

## 🗺️ Roadmap

- [ ] Hreflang and structured data (schema) checks in `audit`
- [ ] Orphan page detection (compare crawl with sitemap)
- [ ] Internal linking suggestions from cluster data
- [ ] Core Web Vitals via the free PageSpeed Insights API
- [ ] More languages for intent detection

Got an idea? [Open an issue](https://github.com/marketing-MEER/seo-workhorse/issues). 🙌

---

## ❓ FAQ

<details>
<summary><b>Do I need to know Python?</b></summary>

No. Install Python 3.10+ once, run the 3 install commands above, and then use the commands as shown. Every result is an Excel file.
</details>

<details>
<summary><b>Does it cost anything or need API keys?</b></summary>

No. It's free, MIT licensed and uses no paid APIs. The Claude skills need Claude Code, but they're optional.
</details>

<details>
<summary><b>Will the crawler get my site blocked?</b></summary>

It waits 0.5 seconds between requests by default and follows `robots.txt`. For large or sensitive sites, raise `--delay` and tell your dev team before you crawl.
</details>

<details>
<summary><b>Does it work for non-English sites?</b></summary>

Yes. The audit and redirect tools work for any language. Clustering and intent detection work best in English and already know some German trigger words (*kaufen*, *Preis*, *wie*).
</details>

<details>
<summary><b>Is my data sent anywhere?</b></summary>

No. Everything runs on your own computer. Only `audit` and `redirects --use-titles` make requests, and only to the site you give them.
</details>

---

## 🧪 Run the tests

```bash
python -m unittest discover -s tests -t . -v
```

Tests run automatically on GitHub for Python 3.10 and 3.12 on every push.

## 🤝 Contributing

Issues and pull requests are welcome, especially new checks, export formats and languages. If this saved you time, a ⭐ helps other SEOs find it.

## 📄 License

[MIT](LICENSE). Free for personal and commercial use.

---

## 👤 Author

<table>
<tr>
<td>

**Meer Hamza** · SEO Team Lead · Berlin 🇩🇪

10+ years in SEO, AEO and GEO across in-house and agency teams.
I built these tools to stop doing the same spreadsheet work every week, and I'm sharing them so you can stop too.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/meerhamza-seo)
[![Email](https://img.shields.io/badge/Email-meerhamza5%40gmail.com-D14836?logo=gmail&logoColor=white)](mailto:meerhamza5@gmail.com)

</td>
</tr>
</table>

<div align="center">

**If seo-workhorse saved you an afternoon, give it a ⭐**

</div>
