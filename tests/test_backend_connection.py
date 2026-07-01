import pytest
from app import app as flask_app
from database.db import get_db
from database.queries import (
    get_category_breakdown,
    get_recent_transactions,
    get_summary_stats,
    get_user_by_id,
)


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def seed_user_id():
    conn = get_db()
    row = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()
    conn.close()
    return row["id"]


@pytest.fixture
def empty_user():
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Test Empty", "empty@test.local", "x"),
    )
    uid = cursor.lastrowid
    conn.commit()
    conn.close()
    yield uid
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = ?", (uid,))
    conn.commit()
    conn.close()


# ── get_user_by_id ────────────────────────────────────────────────────


def test_get_user_by_id_valid(seed_user_id):
    user = get_user_by_id(seed_user_id)
    assert user is not None
    assert user["name"] == "Demo User"
    assert user["email"] == "demo@spendly.com"
    # member_since formatted as "Month YYYY"
    assert user["member_since"].count(" ") == 1
    month, year = user["member_since"].split()
    assert year.isdigit() and len(year) == 4


def test_get_user_by_id_missing():
    assert get_user_by_id(999999) is None


# ── get_summary_stats ─────────────────────────────────────────────────


def test_get_summary_stats_with_expenses(seed_user_id):
    stats = get_summary_stats(seed_user_id)
    assert stats["total_spent"] == pytest.approx(3748.0)
    assert stats["transaction_count"] == 8
    assert stats["top_category"] == "Bills"


def test_get_summary_stats_no_expenses(empty_user):
    stats = get_summary_stats(empty_user)
    assert stats == {"total_spent": 0, "transaction_count": 0, "top_category": "—"}


# ── get_recent_transactions ───────────────────────────────────────────


def test_get_recent_transactions_with_expenses(seed_user_id):
    txs = get_recent_transactions(seed_user_id)
    assert len(txs) == 8
    # Newest date first
    dates = [tx["date"] for tx in txs]
    assert dates == sorted(dates, reverse=True)
    # Required keys present
    for tx in txs:
        assert {"date", "description", "category", "amount"}.issubset(tx.keys())


def test_get_recent_transactions_no_expenses(empty_user):
    assert get_recent_transactions(empty_user) == []


def test_get_recent_transactions_respects_limit(seed_user_id):
    txs = get_recent_transactions(seed_user_id, limit=3)
    assert len(txs) == 3


# ── get_category_breakdown ────────────────────────────────────────────


def test_get_category_breakdown_with_expenses(seed_user_id):
    cats = get_category_breakdown(seed_user_id)
    assert len(cats) == 7
    # Ordered by amount descending
    amounts = [c["amount"] for c in cats]
    assert amounts == sorted(amounts, reverse=True)
    # pct values are integers summing to 100
    pcts = [c["pct"] for c in cats]
    assert all(isinstance(p, int) for p in pcts)
    assert sum(pcts) == 100


def test_get_category_breakdown_no_expenses(empty_user):
    assert get_category_breakdown(empty_user) == []


# ── /profile route ────────────────────────────────────────────────────


def test_profile_unauthenticated(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_authenticated(client, seed_user_id):
    with client.session_transaction() as sess:
        sess["user_id"] = seed_user_id
        sess["user_name"] = "Demo User"
    response = client.get("/profile")
    assert response.status_code == 200
    body = response.data.decode()
    assert "Demo User" in body
    assert "demo@spendly.com" in body
    assert "₹" in body
