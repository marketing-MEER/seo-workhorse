"""Keyword clustering without paid SERP APIs.

Reads a keyword export (Ahrefs, Semrush, GSC queries or any CSV with a keyword
column), groups keywords that share the same core words, names each cluster
after its biggest keyword and tags search intent.
"""
import re

import pandas as pd

from .report import find_column, to_number

STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "to", "of", "in", "on", "with", "without", "at", "by",
    "is", "are", "be", "my", "your", "me", "i", "you", "it", "this", "that", "from", "vs", "versus",
    "de", "der", "die", "das", "und", "für", "mit", "im", "in", "von",
}
# Modifiers change intent but not topic, so they are ignored when comparing keywords.
MODIFIERS = {"best", "top", "free", "cheap", "online", "near", "2024", "2025", "2026", "new", "list", "guide"}

INTENT_RULES = [
    ("transactional", r"\b(buy|price|pricing|cost|cheap|discount|coupon|deal|order|hire|book|subscribe|kaufen|preis)\b"),
    ("commercial", r"\b(best|top|review|reviews|vs|versus|compare|comparison|alternative|alternatives|tool|tools|software|agency)\b"),
    ("informational", r"\b(how|what|why|when|where|who|guide|tutorial|tips|examples|meaning|definition|learn|ideas|was|wie)\b"),
]


def stem(word: str) -> str:
    """Tiny suffix stripper so 'tools'/'tool' and 'audits'/'audit' match."""
    for suffix in ("ies", "es", "s", "ing", "ed"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)] + ("y" if suffix == "ies" else "")
    return word


def tokens(keyword: str) -> frozenset:
    words = re.findall(r"[\wäöüß]+", keyword.lower())
    core = {stem(w) for w in words if w not in STOPWORDS and w not in MODIFIERS}
    return frozenset(core or {stem(w) for w in words})


def similarity(a: frozenset, b: frozenset) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def intent(keyword: str) -> str:
    kw = keyword.lower()
    for name, pattern in INTENT_RULES:
        if re.search(pattern, kw):
            return name
    return "informational" if len(kw.split()) >= 4 else "mixed"


def load_keywords(path) -> pd.DataFrame:
    raw = pd.read_csv(path)
    kw_col = find_column(raw, ["keyword", "keywords", "query", "top queries", "queries", "search term"])
    if not kw_col:
        kw_col = raw.columns[0]
    vol_col = find_column(raw, ["volume", "search volume", "avg. monthly searches", "impressions", "sv"])
    df = pd.DataFrame({"keyword": raw[kw_col].astype(str).str.strip()})
    df["volume"] = to_number(raw[vol_col]) if vol_col else 0
    return df[df["keyword"] != ""].drop_duplicates("keyword")


def cluster(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Greedy clustering: biggest keywords become cluster hubs, the rest join the closest hub."""
    df = df.sort_values("volume", ascending=False).reset_index(drop=True)
    df["tokens"] = df["keyword"].apply(tokens)
    hubs = []  # (cluster_id, hub keyword, token set)
    assigned = []
    for _, row in df.iterrows():
        best_id, best_score = None, 0.0
        for cid, _, hub_tokens in hubs:
            score = similarity(row["tokens"], hub_tokens)
            if score > best_score:
                best_id, best_score = cid, score
        if best_id is None or best_score < threshold:
            best_id = len(hubs) + 1
            hubs.append((best_id, row["keyword"], row["tokens"]))
            best_score = 1.0
        assigned.append((best_id, round(best_score, 2)))

    df["cluster_id"] = [a[0] for a in assigned]
    df["match_score"] = [a[1] for a in assigned]
    names = {cid: name for cid, name, _ in hubs}
    df["cluster"] = df["cluster_id"].map(names)
    df["intent"] = df["keyword"].apply(intent)
    return df.drop(columns="tokens")


def summary(clustered: pd.DataFrame) -> pd.DataFrame:
    grouped = clustered.groupby(["cluster_id", "cluster"]).agg(
        keywords=("keyword", "count"),
        total_volume=("volume", "sum"),
        main_intent=("intent", lambda s: s.mode().iloc[0]),
        sample_keywords=("keyword", lambda s: " | ".join(s.head(5))),
    ).reset_index()
    return grouped.sort_values("total_volume", ascending=False)


def run(path, threshold: float = 0.5) -> dict:
    clustered = cluster(load_keywords(path), threshold)
    return {
        "Clusters": summary(clustered),
        "Keywords": clustered.sort_values(["cluster_id", "volume"], ascending=[True, False]),
    }
