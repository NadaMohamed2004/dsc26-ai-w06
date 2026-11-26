"""Offline TF-IDF search over the Hisn runbooks."""

from functools import lru_cache
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

RUNBOOK_DIR = Path(__file__).parent / "data" / "runbooks"
SNIPPET_CHARS = 200


def _parse(path: Path) -> dict:
    """Split a runbook into its front matter (id, title) and body."""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    meta: dict[str, str] = {}
    body_start = 0
    if lines and lines[0].strip() == "---":
        for number, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                body_start = number + 1
                break
            key, separator, value = line.partition(":")
            if separator:
                meta[key.strip()] = value.strip().strip("\"'")
    return {
        "id": meta.get("id", path.stem),
        "title": meta.get("title", path.stem),
        "body": "\n".join(lines[body_start:]).strip(),
    }


@lru_cache(maxsize=1)
def _index():
    docs = sorted(
        (_parse(path) for path in RUNBOOK_DIR.glob("*.md")), key=lambda d: d["id"]
    )
    # The title is the strongest signal, so it counts three times.
    texts = [f"{(d['title'] + ' ') * 3}{d['body']}" for d in docs]
    # Words give precision; character n-grams match "login" with "logins".
    vectorizers = [
        (0.6, TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)),
        (0.4, TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)),
    ]
    parts = [(weight, v, v.fit_transform(texts)) for weight, v in vectorizers]
    return docs, parts


def search_runbooks(query: str, k: int = 3) -> list[dict]:
    """Return the k best runbooks for a query, best first, ties by ID."""
    if not query or not query.strip():
        return []
    k = max(1, min(10, k))
    docs, parts = _index()
    scores = sum(
        weight * linear_kernel(vectorizer.transform([query]), matrix)[0]
        for weight, vectorizer, matrix in parts
    )
    results = [
        {
            "id": doc["id"],
            "title": doc["title"],
            "snippet": " ".join(doc["body"].split())[:SNIPPET_CHARS],
            "score": round(float(score), 8),
        }
        for doc, score in zip(docs, scores)
    ]
    results.sort(key=lambda r: (-r["score"], r["id"]))
    return results[:k]
