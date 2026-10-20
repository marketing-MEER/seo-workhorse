---
name: seo-cluster-brief
description: Turns keyword clusters from `seo-autopilot cluster` into content briefs (one page per cluster) with a target keyword, search intent, H2 outline, FAQs and internal links. Use when the user says "write briefs for my clusters", "content plan from keyword_clusters.xlsx", or "what pages should I create".
---

# Cluster → content brief

## Input
`keyword_clusters.xlsx` with sheets **Clusters** (one row per cluster) and **Keywords** (every keyword with its cluster and intent).

## Steps
1. Ask how many clusters to brief (default: top 10 by `total_volume`) and the site's URL, if not given.
2. For each cluster:
   - **Primary keyword**: the cluster name. **Secondary keywords**: the other keywords in the cluster.
   - **Intent and format**: informational → guide / how-to; commercial → comparison / "best X"; transactional → service or product page; mixed → check the live SERP and say what format ranks.
   - **Check for cannibalisation**: if the site already has a page for this topic (search `site:<domain> <keyword>` or the audit's All pages sheet), recommend updating it instead of a new page.
   - **Outline**: H1, 5–8 H2s that cover the secondary keywords, and 3–5 FAQs taken from the question keywords in the cluster.
   - **Internal links**: 3 related clusters this page should link to and from.
   - **AI search (GEO) note**: one short, quotable definition or answer near the top so AI Overviews and LLMs can cite it.
3. Save one Markdown file per cluster in `briefs/`, plus `briefs/index.md` with a table of all briefs ordered by volume.

## Rules
- Use only the keywords and volumes in the file. Don't make up search volumes.
- Keep the outline short and practical. A writer should be able to start right away.
