---
name: seo-quickwin-plan
description: Turns `seo-autopilot gsc` output (quick wins, CTR gaps, content decay) into a prioritised 30-day SEO action plan with a concrete task for every page. Use when the user says "what should I fix first", "make an action plan from GSC", "prioritise my quick wins", or hands over gsc_opportunities.xlsx.
---

# GSC quick wins → 30-day action plan

## Input
`gsc_opportunities.xlsx` with sheets **Quick wins (pos 4-20)**, **CTR gaps (page 1)** and, if a previous period was given, **Content decay**.

## Steps
1. Read all sheets. One page can appear in several sheets; merge them per URL.
2. Score each URL: `potential_extra_clicks` + `lost_clicks` + the absolute `click_change` of decay rows. Sort high to low.
3. Write one concrete task per URL, based on why it is in the list:
   - Quick win on page 1 (pos 4–10): update the content for the top queries, add 3–5 internal links from strong pages using the query as anchor text, refresh the title.
   - Quick win on page 2 (pos 11–20): check that the page matches the intent of what ranks in the top 5, expand the missing sections, add internal links.
   - CTR gap: rewrite title + meta (hand off to the `seo-meta-rewrite` skill), add FAQ or review schema where it fits.
   - Decay, "Gone from results": check status code, noindex, canonical and redirects first, this is a technical fault.
   - Decay, rankings dropped: compare with the pages that overtook it and refresh the content.
   - Decay, demand fell: low priority; note the seasonality.
4. Put the tasks into four weeks: technical faults first, then the biggest click gains, then the rest. Max ~10 tasks a week.
5. Save `seo_action_plan.md` with a summary table (url, task, expected extra clicks, week) and a short "why" per task.

## Rules
- Use only the numbers in the file. Label every estimate as an estimate.
- Plain, direct language that someone can act on today.
