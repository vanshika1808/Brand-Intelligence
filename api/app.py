"""
api/app.py — FastAPI backend for the Brand Intelligence dashboard

Endpoints:
    GET /api/brands                      → all brands
    GET /api/overview?brand_id=1         → summary stats (mentions, sentiment %)
    GET /api/mentions?brand_id=1&limit=20 → recent mentions
    GET /api/sentiment?brand_id=1        → positive / neutral / negative counts
    GET /api/top-topics?brand_id=1       → top words from mention titles
    GET /api/mentions-over-time?brand_id=1 → daily mention counts (last 30 days)
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, case
from datetime import datetime, timedelta
from collections import Counter
import re

from database.db import SessionLocal
from database.models import Brand, Product, Mention

app = FastAPI(title="Brand Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session():
    return SessionLocal()


# ── /api/brands ───────────────────────────────────────────────────────────────
@app.get("/api/brands")
def get_brands():
    db = get_session()
    try:
        brands = db.query(Brand).all()
        return [{"id": b.id, "name": b.brand_name} for b in brands]
    finally:
        db.close()


# ── /api/overview ─────────────────────────────────────────────────────────────
@app.get("/api/overview")
def get_overview(brand_id: int = Query(...)):
    db = get_session()
    try:
        q = db.query(Mention).filter(Mention.brand_id == brand_id)
        total = q.count()

        positive = q.filter(Mention.sentiment == "positive").count()
        negative = q.filter(Mention.sentiment == "negative").count()
        neutral  = total - positive - negative

        # Average rating across all mentions that have one
        avg_rating = db.query(func.avg(Mention.rating)).filter(
            Mention.brand_id == brand_id,
            Mention.rating.isnot(None)
        ).scalar()

        # Source breakdown
        sources = db.query(
            Mention.source, func.count(Mention.id)
        ).filter(
            Mention.brand_id == brand_id
        ).group_by(Mention.source).all()

        return {
            "total_mentions": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "positive_pct": round(positive / total * 100, 1) if total else 0,
            "negative_pct": round(negative / total * 100, 1) if total else 0,
            "neutral_pct":  round(neutral  / total * 100, 1) if total else 0,
            "avg_rating": round(float(avg_rating), 2) if avg_rating else None,
            "sources": {s: c for s, c in sources},
        }
    finally:
        db.close()


# ── /api/mentions ─────────────────────────────────────────────────────────────
@app.get("/api/mentions")
def get_mentions(
    brand_id: int = Query(...),
    source: str = Query(None),
    sentiment: str = Query(None),
    limit: int = Query(20),
    offset: int = Query(0),
):
    db = get_session()
    try:
        q = db.query(Mention, Product.product_name).join(
            Product, Mention.product_id == Product.id
        ).filter(Mention.brand_id == brand_id)

        if source:
            q = q.filter(Mention.source == source)
        if sentiment:
            q = q.filter(Mention.sentiment == sentiment)

        q = q.order_by(Mention.created_at.desc())
        rows = q.offset(offset).limit(limit).all()

        return [
            {
                "id": m.id,
                "product": pname,
                "source": m.source,
                "title": m.title,
                "content": m.content,
                "author": m.author,
                "rating": m.rating,
                "sentiment": m.sentiment,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m, pname in rows
        ]
    finally:
        db.close()


# ── /api/sentiment ────────────────────────────────────────────────────────────
@app.get("/api/sentiment")
def get_sentiment(brand_id: int = Query(...)):
    db = get_session()
    try:
        rows = db.query(
            Mention.sentiment, func.count(Mention.id)
        ).filter(
            Mention.brand_id == brand_id
        ).group_by(Mention.sentiment).all()

        total = sum(c for _, c in rows)
        return {
            "breakdown": [
                {
                    "sentiment": s or "unanalysed",
                    "count": c,
                    "pct": round(c / total * 100, 1) if total else 0,
                }
                for s, c in rows
            ],
            "total": total,
        }
    finally:
        db.close()


# ── /api/top-topics ───────────────────────────────────────────────────────────
STOPWORDS = {
    "the", "a", "an", "is", "it", "in", "of", "and", "to", "for",
    "this", "that", "i", "my", "with", "on", "are", "was", "not",
    "but", "very", "good", "product", "from", "have", "has", "be",
    "as", "at", "by", "or", "so", "if", "its", "just", "get",
}

@app.get("/api/top-topics")
def get_top_topics(brand_id: int = Query(...), top_n: int = Query(10)):
    db = get_session()
    try:
        mentions = db.query(Mention.title, Mention.content).filter(
            Mention.brand_id == brand_id
        ).all()

        words = []
        for title, content in mentions:
            text = f"{title or ''} {content or ''}".lower()
            tokens = re.findall(r"\b[a-z]{4,}\b", text)
            words.extend(t for t in tokens if t not in STOPWORDS)

        counter = Counter(words)
        return [
            {"topic": word, "count": cnt}
            for word, cnt in counter.most_common(top_n)
        ]
    finally:
        db.close()


# ── /api/mentions-over-time ───────────────────────────────────────────────────
@app.get("/api/mentions-over-time")
def get_mentions_over_time(brand_id: int = Query(...), days: int = Query(30)):
    db = get_session()
    try:
        since = datetime.utcnow() - timedelta(days=days)
        rows = db.query(
            func.date(Mention.created_at).label("day"),
            func.count(Mention.id).label("count"),
        ).filter(
            Mention.brand_id == brand_id,
            Mention.created_at >= since,
        ).group_by("day").order_by("day").all()

        return [{"date": str(r.day), "count": r.count} for r in rows]
    finally:
        db.close()