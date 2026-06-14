import aiosqlite
import json
from pathlib import Path
from backend.utils.logger import get_logger

logger = get_logger(__name__)

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "reviews.db"


async def get_db() -> aiosqlite.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Create tables if they don't exist"""
    db = await get_db()
    try:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                type        TEXT NOT NULL,
                repo        TEXT NOT NULL,
                reference   TEXT NOT NULL,
                title       TEXT,
                verdict     TEXT,
                score       INTEGER,
                priority    TEXT,
                result      TEXT NOT NULL,
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        await db.commit()
        logger.info("Database initialized")
    finally:
        await db.close()


async def save_review(
    review_type: str,
    repo: str,
    reference: str,
    title: str,
    result: dict,
) -> int:
    """
    Save a review to the database.
    review_type: pr_review | commit_review | issue_review
    reference:   PR number, commit SHA, or issue number
    """
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            INSERT INTO reviews (type, repo, reference, title, verdict, score, priority, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                review_type,
                repo,
                str(reference),
                title,
                result.get("verdict"),
                result.get("score") or result.get("clarity_score"),
                result.get("priority"),
                json.dumps(result),
            ),
        )
        await db.commit()
        review_id = cursor.lastrowid
        logger.info(f"Review saved to DB — id: {review_id} type: {review_type} repo: {repo}")
        return review_id
    finally:
        await db.close()


async def get_reviews(
    repo: str = None,
    review_type: str = None,
    limit: int = 50,
) -> list[dict]:
    """Fetch reviews with optional filters"""
    db = await get_db()
    try:
        conditions = []
        params = []

        if repo:
            conditions.append("repo = ?")
            params.append(repo)
        if review_type:
            conditions.append("type = ?")
            params.append(review_type)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        cursor = await db.execute(
            f"""
            SELECT id, type, repo, reference, title, verdict, score, priority, created_at
            FROM reviews
            {where}
            ORDER BY created_at DESC
            LIMIT ?
            """,
            params,
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def get_review_by_id(review_id: int) -> dict | None:
    """Fetch a single review with full result"""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM reviews WHERE id = ?", (review_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        data = dict(row)
        data["result"] = json.loads(data["result"])
        return data
    finally:
        await db.close()


async def get_stats(repo: str = None) -> dict:
    db = await get_db()
    try:
        where = "WHERE repo = ?" if repo else ""
        params = [repo] if repo else []

        cursor = await db.execute(
            f"SELECT COUNT(*) as total FROM reviews {where}", params
        )
        total = (await cursor.fetchone())["total"]

        cursor = await db.execute(
            f"""
            SELECT verdict, COUNT(*) as count
            FROM reviews
            {where}
            GROUP BY verdict
            """,
            params,
        )
        verdicts = {row["verdict"]: row["count"] for row in await cursor.fetchall()}

        # fix — separate query without AND
        score_where = "WHERE score IS NOT NULL" if not repo else "WHERE repo = ? AND score IS NOT NULL"
        score_params = [repo] if repo else []
        cursor = await db.execute(
            f"SELECT AVG(score) as avg_score FROM reviews {score_where}",
            score_params,
        )
        avg_score = (await cursor.fetchone())["avg_score"]

        cursor = await db.execute(
            f"""
            SELECT type, COUNT(*) as count
            FROM reviews
            {where}
            GROUP BY type
            """,
            params,
        )
        by_type = {row["type"]: row["count"] for row in await cursor.fetchall()}

        return {
            "total_reviews": total,
            "average_score": round(avg_score, 1) if avg_score else 0,
            "by_verdict": verdicts,
            "by_type": by_type,
        }
    finally:
        await db.close()