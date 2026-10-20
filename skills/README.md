# 🤖 Claude Code skills

These skills let [Claude Code](https://claude.com/claude-code) take the Excel reports from seo-workhorse and do the follow-up writing and planning.

| Skill | Use after | Ask Claude |
|---|---|---|
| ✍️ [`seo-meta-rewrite`](seo-meta-rewrite/SKILL.md) | `audit` or `gsc` | "rewrite the titles and metas flagged in audit.xlsx" |
| 📝 [`seo-cluster-brief`](seo-cluster-brief/SKILL.md) | `cluster` | "write content briefs for the top 10 clusters" |
| 🗓️ [`seo-quickwin-plan`](seo-quickwin-plan/SKILL.md) | `gsc` | "turn gsc.xlsx into a 30-day action plan" |

## Install

Copy the three folders into one of these:

- `.claude/skills/` inside your project (this project only)
- `~/.claude/skills/` (all your projects)

Claude picks the right skill from what you ask.
