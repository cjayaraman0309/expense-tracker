# Overview

This step converts the `/login` stub into a functional login handler that supports both `GET` and `POST`. On a valid `POST` it verifies the submitted credentials against the `users` table, stores the authenticated user's `id` in `session["user_id"]`, and redirects to the landing page (a dedicated dashboard does not yet exist). It also replaces the `/logout` stub with a real implementation that clears the session and redirects to `/`. After this step the app can distinguish logged-in users from guests, which is a prerequisite for all expense features.

# Depends on

- Step 01 — Database Setup (`users` table must exist)
- Step 02 — Registration (`create_user` and password hashing must be in place; at least one user must exist to log in against)

# Routes

- `GET /login` — renders the login form — public
- `POST /login` — validates credentials, sets session, redirects — public
- `GET /logout` — clears the session and redirects to `/` — public (no login required)

# Database changes

- No new tables or columns
- The `users` table from Step 01 already stores `email` and `password_hash`
- One new helper function to add to `database/db.py`:
  - `get_user_by_email(email)`
    - Queries the `users` table by email
    - Returns the matching user row, or `None` if not found
    - Must live in `database/db.py` — not defined inline inside the route

# Templates

- Modify `templates/login.html`:
  - Add a `POST` form with `email` and `password` input fields
  - Set the form `action` to `url_for('login')` and `method` to `"post"`
  - Add a block to display flashed error messages
  - Add a link to `/register` for new users who do not yet have an account

# Files to change

- `app.py` — implement `login()` as a `GET`+`POST` handler; implement `logout()`
- `database/db.py` — add `get_user_by_email()` helper
- `templates/login.html` — add the `POST` form and flash message display

# Files to create

None.

# New dependencies

- None — `werkzeug.security.check_password_hash` is already available via the existing `werkzeug` install

# Rules for implementation

- No SQLAlchemy or any ORM — use raw `sqlite3` via `get_db()`
- Parameterised queries only — never use f-strings in SQL
- Verify passwords with `werkzeug.security.check_password_hash`
- The session key for the logged-in user must be `session["user_id"]` (integer)
- Use `flask.session` — do not roll a custom session mechanism
- On a failed login show a generic flash error: `"Invalid email or password."` — do not reveal which field was wrong
- After successful login redirect to `url_for("landing")` until a dashboard route exists
- `logout()` must call `session.clear()` then redirect to `url_for("landing")`
- All templates must extend `base.html`
- Use CSS variables — never hardcode hex values
- Use `url_for()` for every internal link — never hardcode paths

# Definition of done

- [ ] `GET /login` renders the login form with email and password fields
- [ ] Submitting with valid credentials (`demo@spendly.com` / `demo123`) sets `session["user_id"]` and redirects to `/`
- [ ] Submitting with a wrong password shows `"Invalid email or password."` flash and stays on the login page
- [ ] Submitting with an unregistered email shows the same generic error flash
- [ ] `GET /logout` clears the session and redirects to `/`
- [ ] After logout, `session["user_id"]` is no longer present
- [ ] The `/logout` route no longer returns the raw stub string
