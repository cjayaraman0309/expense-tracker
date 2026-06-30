# Overview

This step upgrades the existing stub `GET /register` route into a fully functional registration flow that handles both `GET` and `POST`. The form accepts four fields: `name`, `email`, `password`, and `confirm_password`. On successful registration the user receives a flash success message and is redirected to `/login`. This route is the entry point for all authenticated features — a user must register before they can log in, access their profile, or manage expenses.

# Depends on

- Step 01 — Database setup (`users` table, `get_db()`)

# Routes

- `GET /register` — renders the registration form — public
  - Already exists as a stub; this step upgrades it in place
- `POST /register` — processes the submitted form, validates all input, inserts a new user, and redirects to `/login` — public

# Database changes

- No new tables or columns
- The existing `users` table covers all requirements
- One new helper function to add to `database/db.py`:
  - `create_user(name, email, password)`
    - Hashes the password using `werkzeug.security.generate_password_hash`
    - Inserts a new row into the `users` table
    - Returns the `id` of the newly created user
    - Raises `sqlite3.IntegrityError` if the email is already taken (UNIQUE constraint)

# Templates

- Modify `templates/register.html`:
  - Set the form `action` to `url_for('register')` and `method` to `"post"`
  - Add `name` attributes to all inputs: `name`, `email`, `password`, `confirm_password`
  - Add a block to display flashed messages (e.g. "Email already registered", "Passwords do not match")
  - Keep all existing visual design unchanged

# Files to change

- `app.py` — upgrade `register()` to handle `GET` and `POST`; add `flash` and `redirect` logic
- `database/db.py` — add the `create_user()` helper
- `templates/register.html` — wire up form `action`/`method` and flash message display

# Files to create

None.

# New dependencies

- None — uses `werkzeug.security` (already installed) and Flask's built-in `flash`, `redirect`, `url_for`

# Rules for implementation

- No SQLAlchemy or any ORM
- Parameterised queries only — never use f-strings in SQL
- Hash passwords with `werkzeug.security.generate_password_hash` — never store plaintext
- `app.secret_key` must be set in `app.py` for `flash()` to work (use a hardcoded dev string for now)
- Server-side validation must check in this exact order:
  1. All fields are non-empty
  2. `password == confirm_password`
  3. Email is not already registered (catch `sqlite3.IntegrityError`)
- On any validation failure: re-render the form with a flashed error message — do not redirect
- On success: flash a success message and redirect to `url_for('login')`
- Use `abort(405)` if an unsupported HTTP method reaches the route
- All templates must extend `base.html`
- Use CSS variables — never hardcode hex values
- Use `url_for()` for every internal link — never hardcode URLs

# Definition of done

- [ ] `GET /register` renders the registration form without errors
- [ ] Submitting with all valid fields creates a new user in `users` and redirects to `/login`
- [ ] Submitting with mismatched passwords re-renders the form with an error, no DB insert
- [ ] Submitting with an already-registered email re-renders with "Email already registered"
- [ ] Submitting with any empty field re-renders with a validation error
- [ ] Password is stored as a hash — never plaintext — verifiable by inspecting `spendly.db`
- [ ] No duplicate user is created on repeated valid submissions with the same email
