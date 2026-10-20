"""Command line entry point: `seo-autopilot <command>`."""
from pathlib import Path

import click

from . import __version__, audit, cluster, gsc, redirects
from .report import write_report


def _done(path: Path, sheets: dict):
    click.secho(f"\nSaved: {path}", fg="green", bold=True)
    for name, df in sheets.items():
        click.echo(f"  {name}: {len(df)} rows")


@click.group()
@click.version_option(__version__)
def main():
    """seo-autopilot: automate the slowest weekly SEO jobs.

    Built by Meer Hamza - linkedin.com/in/meerhamza-seo
    """


@main.command("audit")
@click.argument("url")
@click.option("--max-pages", default=200, show_default=True, help="Stop after this many URLs.")
@click.option("--delay", default=0.5, show_default=True, help="Seconds between requests (be polite).")
@click.option("-o", "--output", default="seo_audit.xlsx", show_default=True)
def audit_cmd(url, max_pages, delay, output):
    """Crawl a site and list technical SEO issues."""
    def progress(n, page_url, status):
        click.echo(f"[{n}/{max_pages}] {status} {page_url}")

    sheets = audit.run(url, max_pages=max_pages, delay=delay, progress=progress)
    _done(write_report(sheets, output), sheets)


@main.command("cluster")
@click.argument("keywords_csv", type=click.Path(exists=True))
@click.option("--threshold", default=0.5, show_default=True, help="0-1. Higher = tighter, smaller clusters.")
@click.option("-o", "--output", default="keyword_clusters.xlsx", show_default=True)
def cluster_cmd(keywords_csv, threshold, output):
    """Group a keyword export (Ahrefs, Semrush, GSC) into topic clusters."""
    sheets = cluster.run(keywords_csv, threshold)
    _done(write_report(sheets, output), sheets)


@main.command("redirects")
@click.argument("old_urls")
@click.argument("new_urls")
@click.option("--min-score", default=0.6, show_default=True, help="Below this a match is flagged for review.")
@click.option("--use-titles", is_flag=True, help="Also fetch each page's title to improve matching (slower).")
@click.option("-o", "--output", default="redirect_map.xlsx", show_default=True)
def redirects_cmd(old_urls, new_urls, min_score, use_titles, output):
    """Map OLD_URLS to NEW_URLS (sitemap URL, .xml, .csv or .txt) for a migration."""
    sheets = redirects.run(old_urls, new_urls, min_score, use_titles)
    out = write_report(sheets, output)
    mapping = sheets["Redirect map"]
    out.with_suffix(".htaccess").write_text(redirects.to_htaccess(mapping), encoding="utf-8")
    out.with_suffix(".nginx.conf").write_text(redirects.to_nginx(mapping), encoding="utf-8")
    _done(out, sheets)
    click.echo(f"  Also wrote {out.with_suffix('.htaccess').name} and {out.with_suffix('.nginx.conf').name}")


@main.command("gsc")
@click.argument("current_csv", type=click.Path(exists=True))
@click.option("--previous", type=click.Path(exists=True), help="Export from an earlier period, to find decaying pages.")
@click.option("--min-impressions", default=100, show_default=True)
@click.option("-o", "--output", default="gsc_opportunities.xlsx", show_default=True)
def gsc_cmd(current_csv, previous, min_impressions, output):
    """Find quick wins, CTR gaps and content decay in a Search Console export."""
    sheets = gsc.run(current_csv, previous, min_impressions)
    _done(write_report(sheets, output), sheets)


if __name__ == "__main__":
    main()
