# 1. Overview

This step replaces the empty stub in `database/db.py` with a working SQLite implementation. It is the foundational step because every subsequent feature — user authentication, the profile page, and all expense tracking operations — depends on a live database connection and populated tables. Without this step, no other step can function.

# 2. Depends on

This is Step 1 — the first step. There are no prerequisites.

# 3. Routes

No new routes are introduced in this step. All existing placeholder routes in `app.py` remain unchanged and continue returning their placeholder strings.

# 4. Database Schema

## Table A: users

| Column | SQLite Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | NOT NULL, UNIQUE |
| password_hash | TEXT | NOT NULL |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP |

## Table B: expenses

| Column | SQLite Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| user_id | INTEGER | NOT NULL, FOREIGN KEY → users(id) |
| amount | REAL | NOT NULL |
| category | TEXT | NOT NULL |
| date | TEXT | NOT NULL — must be stored in YYYY-MM-DD format |
| description | TEXT | |
| created_at | TEXT | NOT NULL, DEFAULT CURRENT_TIMESTAMP |

# 5. Functions to Implement (database/db.py)

- **`get_db()`**
  - Opens `spendly.db` in the project root
  - Sets `row_factory = sqlite3.Row` so columns are accessible by name
  - Executes `PRAGMA foreign_keys = ON` on every new connection
  - Returns the connection object

- **`init_db()`**
  - Creates the `users` table using `CREATE TABLE IF NOT EXISTS`
  - Creates the `expenses` table using `CREATE TABLE IF NOT EXISTS`
  - Safe to call multiple times without error or data loss

- **`seed_db()`**
  - Checks whether the `users` table already contains any rows — if yes, returns immediately (idempotent)
  - Otherwise inserts one demo user:
    - name: `Demo User`
    - email: `demo@spendly.com`
    - password: `demo123` hashed via `werkzeug.security.generate_password_hash`
  - Inserts 8 sample expenses linked to that demo user
  - Expenses must cover all 7 valid categories with dates spread across the current month

# 6. Changes to app.py

- Import `get_db`, `init_db`, `seed_db` from `database.db`
- On app startup, push an application context and call `init_db()` followed by `seed_db()`
- The database must be fully initialised and seeded before any route is served

# 7. Files to Change

- `database/db.py` — implement the three functions
- `app.py` — import and call `init_db()` / `seed_db()` at startup

# 8. Files to Create

None.

# 9. Dependencies

- No new pip packages required
- Use `sqlite3` from the Python standard library
- Use `werkzeug.security` (already listed in `requirements.txt`)

# 10. Categories (Fixed List)

The only valid values for `expenses.category` are:

- Food
- Transport
- Bills
- Health
- Entertainment
- Shopping
- Other

# 11. Rules for Implementation

- No SQLAlchemy or any ORM — raw `sqlite3` only
- Parameterized queries only — never use f-strings or string formatting in SQL
- `PRAGMA foreign_keys = ON` must be executed on every connection, inside `get_db()`
- `amount` must be stored as `REAL`, not `INTEGER`
- Passwords must be hashed with `generate_password_hash` from `werkzeug.security` — never store plaintext
- `seed_db()` must be idempotent — safe to call on every app startup
- All dates must be stored and handled in `YYYY-MM-DD` format

# 12. Expected Behavior

- **`get_db()`** — returns a `sqlite3.Connection` with `row_factory = sqlite3.Row` set and foreign key enforcement active; calling code can access columns by name
- **`init_db()`** — when called on a fresh environment it creates both tables; when called on an existing database it exits cleanly without modifying existing data or schema
- **`seed_db()`** — when called on an empty database it inserts one demo user and 8 sample expenses; when called on an already-seeded database it detects the existing rows and returns without inserting duplicates
- **Database constraints** — the `UNIQUE` constraint on `users.email` prevents duplicate accounts; the `FOREIGN KEY` on `expenses.user_id` prevents orphaned expense rows

# 13. Error Handling Expectations

- Inserting a duplicate email → `sqlite3.IntegrityError` raised by the UNIQUE constraint
- Inserting an expense with a non-existent `user_id` → `sqlite3.IntegrityError` raised by the foreign key constraint
- Malformed or invalid SQL queries → exceptions propagate up without being swallowed, so errors are visible during development

# 14. Definition of Done

- [ ] Database file `spendly.db` is created in the project root on app startup
- [ ] Both `users` and `expenses` tables exist with the correct schema and constraints
- [ ] Demo user `demo@spendly.com` exists with a hashed (not plaintext) password
- [ ] 8 sample expenses exist, covering all 7 valid categories
- [ ] Running the app a second time does not create duplicate seed data
- [ ] App starts without errors
- [ ] Foreign key enforcement works (inserting an expense with a bad `user_id` raises an error)
- [ ] All queries use parameterized SQL — no string formatting or f-strings in any SQL statement
