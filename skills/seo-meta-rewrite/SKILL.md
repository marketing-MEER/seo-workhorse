---
name: seo-meta-rewrite
description: Rewrites the titles and meta descriptions that `seo-autopilot audit` or `seo-autopilot gsc` flagged (missing, duplicate, too long, too short, or low CTR). Use when the user says "fix my titles", "rewrite metas from the audit", "write new meta descriptions", or hands over seo_audit.xlsx / gsc_opportunities.xlsx.
---

# SEO meta rewrite

Turn flagged pages into ready-to-paste title tags and meta descriptions.

## Input
- `seo_audit.xlsx` → sheet **Issues**, rows where `issue` is one of: Missing title, Title too long, Title too short, Duplicate title, Missing meta description, Meta description too long/short, Duplicate meta description.
- or `gsc_opportunities.xlsx` → sheet **CTR gaps (page 1)** (pages that rank but don't get clicked).

## Steps
1. Read the sheet with pandas and group rows by URL (one page can have several issues).
2. For each URL, read the page (fetch it, or use the `title`, `h1` and `meta_description` columns from **All pages**). Work out the main keyword: the H1, the URL slug, and for GSC rows the top query.
3. Write for each page:
   - **Title**: 50–60 characters, main keyword near the start, one clear benefit or hook, brand at the end only if it fits.
   - **Meta description**: 140–155 characters, answers the search intent, includes the keyword once, ends with a reason to click. No "Discover", "Unlock", "Elevate" or other filler.
   - Every title and description must be unique across the site.
4. For CTR-gap pages, explain in one line what changed and why (e.g. "added the year and the number of examples to match what ranks above").
5. Save `meta_rewrites.xlsx` with columns: url, issue, old_title, new_title, new_title_length, old_meta, new_meta, new_meta_length, reason.

## Rules
- Never invent facts, prices, numbers or claims that are not on the page.
- Keep the page's language (German page → German tags).
- Count characters and fix anything outside the limits before saving.
