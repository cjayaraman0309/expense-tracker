from datetime import datetime

from database.db import get_db


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT name, email, created_at FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    dt = datetime.strptime(row["created_at"][:10], "%Y-%m-%d")
    return {
        "name": row["name"],
        "email": row["email"],
        "member_since": dt.strftime("%B %Y"),
    }


def get_summary_stats(user_id):
    conn = get_db()
    row = conn.execute(
        "SELECT SUM(amount), COUNT(*) FROM expenses WHERE user_id = ?", (user_id,)
    ).fetchone()
    total = row[0] or 0.0
    count = row[1] or 0
    if count == 0:
        conn.close()
        return {"total_spent": 0, "transaction_count": 0, "top_category": "—"}
    top = conn.execute(
        "SELECT category FROM expenses WHERE user_id = ? "
        "GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return {
        "total_spent": total,
        "transaction_count": count,
        "top_category": top["category"] if top else "—",
    }


def get_recent_transactions(user_id, limit=10):
    conn = get_db()
    rows = conn.execute(
        "SELECT date, description, category, amount FROM expenses "
        "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_category_breakdown(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT category AS name, SUM(amount) AS amount FROM expenses "
        "WHERE user_id = ? GROUP BY category ORDER BY amount DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    if not rows:
        return []
    total = sum(r["amount"] for r in rows)
    result = [
        {"name": r["name"], "amount": r["amount"], "pct": round(r["amount"] / total * 100)}
        for r in rows
    ]
    diff = 100 - sum(item["pct"] for item in result)
    if diff != 0:
        result[0]["pct"] += diff
    return result
