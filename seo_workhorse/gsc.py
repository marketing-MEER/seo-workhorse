"""Google Search Console quick wins, CTR gaps and content decay.

Input: a GSC Performance export (Pages or Queries tab, CSV). Optionally a second
export for an earlier period to find pages that are losing clicks.
"""
import pandas as pd

from .report import find_column, to_number

# Rough organic CTR by position (industry averages, desktop + mobile).
# Used only as a benchmark to spot titles/snippets that under-perform.
EXPECTED_CTR = {1: 0.28, 2: 0.16, 3: 0.11, 4: 0.08, 5: 0.06, 6: 0.05, 7: 0.04, 8: 0.033, 9: 0.027, 10: 0.024}

KEY_COLUMNS = ["top pages", "page", "pages", "url", "top queries", "query", "queries"]


def load_gsc(path) -> pd.DataFrame:
    """Read a GSC export and normalise it to key, clicks, impressions, ctr, position."""
    raw = pd.read_csv(path)
    key = find_column(raw, KEY_COLUMNS)
    clicks = find_column(raw, ["clicks"])
    impressions = find_column(raw, ["impressions"])
    position = find_column(raw, ["position", "avg. position", "average position"])
    if not all([key, clicks, impressions, position]):
        raise ValueError(
            f"{path}: expected columns like 'Top pages' / 'Top queries', 'Clicks', 'Impressions', "
            f"'Position'. Found: {list(raw.columns)}"
        )
    df = pd.DataFrame({
        "key": raw[key].astype(str),
        "clicks": to_number(raw[clicks]),
        "impressions": to_number(raw[impressions]),
        "position": to_number(raw[position]),
    })
    df["ctr"] = (df["clicks"] / df["impressions"].where(df["impressions"] > 0)).fillna(0)
    return df


def expected_ctr(position: float) -> float:
    if position < 1:
        return EXPECTED_CTR[1]
    if position <= 10:
        return EXPECTED_CTR[max(1, round(position))]
    return 0.01 if position <= 20 else 0.003


def quick_wins(df: pd.DataFrame, min_impressions: int = 100) -> pd.DataFrame:
    """Rows ranking 4-20 with real demand: the cheapest traffic you can get."""
    wins = df[(df["position"] >= 4) & (df["position"] <= 20) & (df["impressions"] >= min_impressions)].copy()
    # Clicks you would get at position 3, minus clicks you get now.
    wins["potential_extra_clicks"] = (wins["impressions"] * EXPECTED_CTR[3] - wins["clicks"]).clip(lower=0).round()
    wins["action"] = wins["position"].apply(
        lambda p: "Page 1 bottom: refresh content, add internal links, tighten title"
        if p <= 10 else "Page 2: expand content to match intent, build internal + external links"
    )
    return _fmt(wins.sort_values("potential_extra_clicks", ascending=False))


def ctr_gaps(df: pd.DataFrame, min_impressions: int = 100, ratio: float = 0.5) -> pd.DataFrame:
    """Rows on page 1 whose CTR is below `ratio` x the expected CTR: rewrite title/meta."""
    page1 = df[(df["position"] <= 10) & (df["impressions"] >= min_impressions)].copy()
    page1["expected_ctr"] = page1["position"].apply(expected_ctr)
    gaps = page1[page1["ctr"] < page1["expected_ctr"] * ratio].copy()
    gaps["lost_clicks"] = (gaps["impressions"] * gaps["expected_ctr"] - gaps["clicks"]).round()
    gaps["action"] = "Rewrite title + meta description (check SERP features stealing clicks)"
    gaps["expected_ctr"] = (gaps["expected_ctr"] * 100).round(1)
    return _fmt(gaps.sort_values("lost_clicks", ascending=False))


def decay(current: pd.DataFrame, previous: pd.DataFrame, min_drop: float = 0.2, min_clicks: int = 20) -> pd.DataFrame:
    """Rows that lost at least `min_drop` of their clicks between two periods."""
    merged = previous.merge(current, on="key", how="left", suffixes=("_before", "_now")).fillna(0)
    merged = merged[merged["clicks_before"] >= min_clicks]
    merged["click_change"] = merged["clicks_now"] - merged["clicks_before"]
    merged["change_pct"] = (merged["click_change"] / merged["clicks_before"] * 100).round(1)
    merged["position_change"] = (merged["position_now"] - merged["position_before"]).round(1)
    lost = merged[merged["change_pct"] <= -min_drop * 100].copy()
    lost["likely_cause"] = lost.apply(_decay_cause, axis=1)
    cols = ["key", "clicks_before", "clicks_now", "click_change", "change_pct",
            "position_before", "position_now", "position_change",
            "impressions_before", "impressions_now", "likely_cause"]
    lost[["position_before", "position_now"]] = lost[["position_before", "position_now"]].round(1)
    return lost[cols].sort_values("click_change")


def _decay_cause(row) -> str:
    if row["clicks_now"] == 0 and row["impressions_now"] == 0:
        return "Gone from results: check status code, noindex, canonical, redirects"
    if row["position_change"] >= 3:
        return "Rankings dropped: competitors updated, refresh content + check intent"
    if row["impressions_now"] < row["impressions_before"] * 0.7:
        return "Demand fell: seasonality or lower search volume"
    return "CTR fell at similar rank: SERP features / AI overview, or weaker snippet"


def _fmt(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["ctr"] = (out["ctr"] * 100).round(2)
    out["position"] = out["position"].round(1)
    return out.rename(columns={"ctr": "ctr_pct", "expected_ctr": "expected_ctr_pct"})


def run(current_path, previous_path=None, min_impressions: int = 100) -> dict:
    current = load_gsc(current_path)
    sheets = {
        "Quick wins (pos 4-20)": quick_wins(current, min_impressions),
        "CTR gaps (page 1)": ctr_gaps(current, min_impressions),
    }
    if previous_path:
        sheets["Content decay"] = decay(current, load_gsc(previous_path))
    return sheets
