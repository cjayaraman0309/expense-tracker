    # CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the dev server (port 5001)
python app.py

# Run tests
pytest

# Run a single test file
pytest tests/test_auth.py

# Install dependencies
pip install -r requirements.txt
```

## Architecture

**Spendly** is a step-by-step student project. The codebase is intentionally incomplete — most routes and the entire database layer are stubs that students implement one step at a time, guided by spec files in `Spec_0*.md`.

### Tech stack
- **Flask 3.1.3** — web framework, runs on port 5001
- **SQLite via `sqlite3` stdlib** — no ORM, raw parameterized queries only
- **Werkzeug** — password hashing (`generate_password_hash` / `check_password_hash`)
- **Jinja2** — templating (built into Flask); all templates extend `templates/base.html`
- **pytest + pytest-flask** — test suite

### Data model
Two tables in `spendly.db` (project root):

- **users**: `id`, `name`, `email` (UNIQUE), `password_hash`, `created_at`
- **expenses**: `id`, `user_id` (FK → users), `amount` (REAL), `category`, `date` (YYYY-MM-DD), `description`, `created_at`

Valid categories (fixed list): `Food`, `Transport`, `Bills`, `Health`, `Entertainment`, `Shopping`, `Other`

### Step-by-step build order
The `Spec_0N_*.md` files define the 9 implementation steps:
1. Database setup (`database/db.py` — `get_db`, `init_db`, `seed_db`)
2. Registration (POST `/register`, `create_user()`)
3. Login / logout (session management)
4. Profile page (expense list view)
5. Backend routes for profile
6. Date filter on profile
7. Add expense
8. Edit expense
9. Delete expense

### Key constraints (enforced throughout all steps)
- No SQLAlchemy or any ORM — raw `sqlite3` only
- Parameterized queries only — never f-strings or string formatting in SQL
- `PRAGMA foreign_keys = ON` on every connection (set inside `get_db()`)
- Passwords hashed with `werkzeug.security` — never stored plaintext
- All internal links use `url_for()` — never hardcoded paths
- All templates extend `base.html`
- CSS uses variables — never hardcoded hex values
- `seed_db()` must be idempotent (check before inserting)

### Current state of `app.py`
Routes `/`, `/register`, `/login` render templates. All other routes (`/logout`, `/profile`, `/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`) return placeholder strings — these are the stubs students replace.

`database/db.py` is also a stub with only comments; students implement `get_db()`, `init_db()`, `seed_db()` in Step 1.
