# 📂 Sample data

Small, made-up files so you can try every tool in seconds.

| File | Use with | Looks like |
|---|---|---|
| `keywords.csv` | `seo-workhorse cluster examples/keywords.csv` | Ahrefs / Semrush keyword export (`Keyword`, `Volume`, `KD`) |
| `gsc_pages_current.csv` | `seo-workhorse gsc examples/gsc_pages_current.csv --previous examples/gsc_pages_previous.csv` | GSC Performance → Pages export, last period |
| `gsc_pages_previous.csv` | the `--previous` file above | Same export, earlier period (for content decay) |
| `old_urls.csv` | `seo-workhorse redirects examples/old_urls.csv examples/new_urls.csv` | URL list of the old site |
| `new_urls.csv` | the second argument above | URL list of the new site |

Swap in your own exports in the same format when you're ready.
