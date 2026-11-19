"""The help centre: load the articles and find the ones that answer a question.

Retrieval is plain BM25 keyword search, so you can read exactly why an article
was or wasn't found. Real products often use embeddings; the evals work the same way.
"""

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

HELP_CENTRE_DIR = Path(__file__).parent / "data" / "help_centre"

STOP_WORDS = frozenset(
    "a an and are as at be but by can do does for from has have how i if in is it its "
    "me my no not of on or our so that the their them then there they this to was we "
    "what when where which who will with you your".split()
)


@dataclass(frozen=True)
class Article:
    id: str
    title: str
    text: str


@dataclass(frozen=True)
class Hit:
    article: Article
    score: float


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9£]+", text.lower())
    return [stem(w) for w in words if w not in STOP_WORDS]


def stem(word: str) -> str:
    """A deliberately tiny stemmer: refunds -> refund, returned -> return."""
    for suffix in ("ing", "ed", "es", "s"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def load_articles(directory: Path = HELP_CENTRE_DIR) -> list[Article]:
    articles = []
    for path in sorted(directory.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        title = text.splitlines()[0].lstrip("# ").strip()
        article_id = "-".join(path.stem.split("-")[:2])  # KB-105-refunds -> KB-105
        articles.append(Article(id=article_id, title=title, text=text))
    return articles


class HelpCentre:
    def __init__(self, articles: list[Article] | None = None, k1: float = 1.5, b: float = 0.75):
        self.articles = articles if articles is not None else load_articles()
        self.k1, self.b = k1, b
        self._docs = [tokenize(a.title + " " + a.title + " " + a.text) for a in self.articles]
        self._avg_len = sum(len(d) for d in self._docs) / max(len(self._docs), 1)
        n = len(self._docs)
        df: dict[str, int] = {}
        for doc in self._docs:
            for term in set(doc):
                df[term] = df.get(term, 0) + 1
        self._idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def get(self, article_id: str) -> Article | None:
        return next((a for a in self.articles if a.id == article_id), None)

    def search(self, query: str, k: int = 3) -> list[Hit]:
        terms = tokenize(query)
        hits = []
        for article, doc in zip(self.articles, self._docs, strict=True):
            score = 0.0
            for term in set(terms):
                tf = doc.count(term)
                if not tf:
                    continue
                norm = (
                    tf
                    * (self.k1 + 1)
                    / (tf + self.k1 * (1 - self.b + self.b * len(doc) / self._avg_len))
                )
                score += self._idf.get(term, 0.0) * norm
            if score > 0:
                hits.append(Hit(article, round(score, 3)))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]


@lru_cache(maxsize=1)
def default_help_centre() -> HelpCentre:
    return HelpCentre()
