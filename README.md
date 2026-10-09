# Demongo

A batteries-included Flask starter template: SQLAlchemy with pluggable database
providers, migrations, session-based auth (register/login/logout/password
reset), a thin service layer, and a Bootstrap UI — meant to be cloned as the
base for new projects, not extended in place.

## Features

- **App factory** (`app/__init__.py`) with a `wsgi.py` composition root — no
  circular imports, extensions and app-specific config are wired together in
  one place.
- **Pluggable database provider** — set `DATABASE_PROVIDER` to `sqlite`,
  `mysql`, or `postgresql` and the connection URI is built automatically from
  the matching block of settings. No code changes required to switch.
- **Migrations** via Flask-Migrate / Alembic (`migrations/`), with dated
  revision filenames.
- **Auth system** (`app/blueprints/auth.py`): register, login, logout,
  password reset request + reset, all backed by a service layer
  (`app/services/auth.py`) that takes typed `*In` dataclasses and returns
  typed `*Out` dataclasses — routes stay thin (forms, flash, redirect only).
- **User model** (`app/models/user.py`) with `is_active` / `is_staff` /
  `is_superuser`, plus audit tables: `PasswordResetToken` (hashed,
  single-use, expiring tokens) and `UserRegistrationHistory`.
- **CSRF-protected forms** via Flask-WTF, **Bootstrap 5** UI (CDN, no build
  step) with a shared layout, flash-message macro, and 403/404/500 error
  pages.
- **Outbound email** (`app/helpers/mail_helper.py`) via Flask-Mail — the password
  reset flow sends a real HTML+text email. With no `MAIL_SERVER` configured
  it "sends" without connecting to SMTP and logs the subject/body instead,
  so a fresh clone still works with zero setup.
- **Role-based authorization** (`app/decorators.py`): `@staff_required` /
  `@superuser_required` — anonymous users get redirected to login (like
  `@login_required`), authenticated-but-unauthorized users get a 403.
- **Caching** (`app/helpers/cache_helper.py`) via Flask-Caching — in-process
  `SimpleCache` by default, switch to `RedisCache` with one setting.
- **Rate limiting** via Flask-Limiter — login/register/password-reset are
  throttled per IP out of the box.
- **Background jobs** (`app/helpers/redis_helper.py`) via RQ —
  `get_queue().enqueue(...)`. Needs a running Redis + `rq worker`; nothing in
  the base app depends on it, it's just wired up and ready.
- **File uploads** (`app/helpers/upload_helper.py`) — extension allowlist +
  collision-safe filenames, saved under `static/uploads/`. Size is
  capped globally via `MAX_CONTENT_LENGTH` (413 above the limit).
- **i18n** via Flask-Babel — `en` (source) and `tr` (translated) out of the
  box, a `/set-locale/<locale>` route, and a language switcher in the navbar.
- **Health check** at `/health` (pings the database).
- **`flask shell`** pre-loaded with `db` and the models.
- Fully typed (`Mapped[...]`, `-> None` / `-> Flask` everywhere) and
  `ruff`-formatted (120-column line length).

Not included yet: Docker (see [Roadmap](#roadmap)).

## Requirements

- Python 3.14+ (see `.python-version`)
- [uv](https://docs.astral.sh/uv/)
- Redis — optional. Only needed if you switch caching/rate-limiting to Redis
  or actually run the RQ queue; everything else works without it.

## Quickstart

```bash
git clone <this-repo-url>
cd demongo

uv sync                     # installs dependencies into .venv
cp .env.example .env        # defaults to SQLite — no external services needed

uv run flask db upgrade     # create the database tables
uv run flask run            # http://127.0.0.1:5000
```

That's it — `wsgi.py` is auto-discovered by the Flask CLI, so no `FLASK_APP`
or `--app` flag is needed for `flask run` / `flask db ...` / `flask shell`.

## Configuration

All settings live in `settings.py` and are read from the environment (via
`python-decouple`), with working defaults for everything — see
`.env.example` for the full, documented list. The only one you're likely to
touch on day one is `DATABASE_PROVIDER`.

### Switching database providers

```bash
# .env
DATABASE_PROVIDER=mysql        # or: sqlite (default) | postgresql
```

MySQL and PostgreSQL drivers are optional extras (kept out of the default
install so a plain `uv sync` doesn't pull in a C extension you don't need):

```bash
uv sync --extra mysql          # installs pymysql
uv sync --extra postgresql     # installs psycopg2-binary
```

Then fill in the matching `MYSQL_*` / `POSTGRESQL_*` variables in `.env`.
Need something even more custom? Set `SQLALCHEMY_DATABASE_URI` directly and
it overrides `DATABASE_PROVIDER` entirely.

## Migrations

```bash
uv run flask db upgrade                       # apply migrations
uv run flask db migrate -m "add something"     # after changing a model
uv run flask db upgrade                       # apply the new migration
```

Revision files are named `<date>_<time>-<hash>_<message>.py` so `ls
migrations/versions/` sorts chronologically.

## Project structure

```
app/
├── blueprints/         # routes (main, auth, profile, materials, calculator, recipes) — thin, HTTP-only
├── services/            # business logic, called from blueprints
│   ├── auth.py           #   AuthService — login/register/password reset
│   ├── material.py        #   MaterialService — raw-material catalogue CRUD
│   ├── recipe.py           #   RecipeService — save/list/price bonsai recipes
│   └── schemas/           #   typed *In / *Out dataclasses + result enums per service
├── models/               # SQLAlchemy models
│   ├── _base.py           #   BaseModel: id, created_at, updated_at
│   ├── user.py             #   User, PasswordResetToken, UserRegistrationHistory
│   ├── material.py          #   Material
│   └── recipe.py             #   ProductRecipe, RecipeItem
├── forms/                # Flask-WTF forms (HTTP-layer validation + CSRF)
├── helpers/               # small standalone utilities, each independent:
│   ├── time_helpers.py     #   utcnow()
│   ├── sqlalchemy_helpers.py #  DATABASE_PROVIDER -> connection URI
│   ├── cache_helper.py      #   Flask-Caching facade (cache_get/set/delete)
│   ├── redis_helper.py      #   raw redis connection + RQ get_queue()
│   ├── upload_helper.py     #   save_upload() — validated file uploads
│   ├── mail_helper.py       #   send_mail() — generic Flask-Mail wrapper (no DB, so it's a helper, not a service)
│   └── costing_helpers.py    #  calculate_costing() — the pricing formula, pure arithmetic
├── enums.py               # enums stored in database columns (MaterialCategory)
├── commands.py            # flask CLI commands (seed-materials)
├── decorators.py          # @staff_required / @superuser_required
├── templates/
│   ├── layouts/master.html #  Bootstrap shell: title/css/content/js blocks
│   ├── macros/              #  reusable Jinja macros (e.g. flash messages)
│   ├── partials/             #  structural includes (errors/, navbar-style pieces)
│   ├── emails/                # templates rendered by services, not routes
│   └── blueprints/            # one folder per blueprint, mirrors app/blueprints/
├── translations/          # Babel catalogs (en source, tr translated)
├── extensions.py         # extension instances + their pure .init_app() calls
├── error_handlers.py      # 403/404/500 handlers
└── __init__.py              # create_app() factory

static/        # CSS/JS/uploads — lives next to app/, not inside it (not Python)
├── assets/      # your CSS/JS — tracked in git
└── uploads/      # user-uploaded files at runtime — gitignored

settings.py    # env-backed config (Settings class)
wsgi.py        # composition root: app = create_app(settings)
migrations/    # Alembic
babel.cfg      # pybabel extraction config
```

### A note on the architecture

- `extensions.py` only instantiates extensions and calls their generic
  `.init_app()` — it has zero business knowledge (no blueprint names, no
  model imports).
- App-specific wiring (e.g. `login_manager.login_view = "auth.login"`) lives
  in `create_app()`, the one place allowed to know about both extensions and
  blueprints.
- Blueprints don't touch the database directly — they call a service method
  with an `*In` DTO and act on the `*Out` DTO it returns.

## Useful commands

```bash
uv run flask run              # dev server
uv run flask shell            # REPL with db and the models preloaded
uv run flask seed-materials   # starter raw-material catalogue for the calculator
uv run flask db upgrade       # apply migrations
uv run ruff check .           # lint
uv run ruff format .          # format
```

`GET /health` returns `{"status": "ok"}` (200) if the app and its database
connection are both up, `{"status": "error"}` (503) otherwise.

## Mail

`send_mail()` (`app/helpers/mail_helper.py`) is a thin, generic wrapper
around Flask-Mail — it's a helper, not a service: it never touches the
database. Domain services (e.g. `AuthService`) own their own templates and
call `send_mail(to, subject, text_body, html_body)` directly.

Configure real delivery via the `MAIL_*` variables in `.env` (see
`.env.example`). With `MAIL_SERVER` unset, `MAIL_SUPPRESS_SEND` defaults to
`True`: `mail.send()` is called but never opens an SMTP connection, and the
subject + body are logged instead — so password reset works out of the box
on a fresh clone, and starts sending for real the moment you configure an
SMTP server.

## Authorization

`app/decorators.py` has two route decorators built on `User.is_staff` /
`User.is_superuser`:

```python
from app.decorators import staff_required


@app.route("/admin-ish-thing")
@staff_required
def admin_ish_thing(): ...
```

Anonymous visitors are redirected to login (same as `@login_required`);
logged-in users who fail the check get a 403. Add more of these the same way
if you need finer-grained roles later.

## Caching

`app/helpers/cache_helper.py` wraps Flask-Caching:

```python
from app.helpers.cache_helper import cache_get, cache_set, cache_get_or_set

cache_set("key", value, timeout=60)
cache_get("key")
cache_get_or_set("key", lambda: expensive_computation(), timeout=300)
```

`CACHE_TYPE=SimpleCache` (in-process) by default — zero setup, but not
shared across workers/processes. Set `CACHE_TYPE=RedisCache` to point it at
`REDIS_URL` instead.

## Rate limiting

Flask-Limiter is wired up in `app/extensions.py` and applied per-route in
`app/blueprints/auth.py`:

```python
@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login(): ...
```

Storage is in-memory (`memory://`, per-process) by default; set
`RATELIMIT_STORAGE_URI=redis://...` to share limits across workers.

## Background jobs

`app/helpers/redis_helper.py` gives you an RQ queue:

```python
from app.helpers.redis_helper import get_queue

get_queue().enqueue(some_function, arg1, arg2)
```

This needs an actual Redis server and a running worker to process anything
(`rq worker` — see the [RQ docs](https://python-rq.org)); nothing in the
base app depends on it, so a fresh clone works fine without either running.
`some_function` must live in an importable module (not a script's
`__main__`) — that's an RQ requirement, not ours.

## File uploads

```python
from app.helpers.upload_helper import save_upload, UploadError

try:
    filename = save_upload(request.files["photo"])  # -> "photo-a1b2c3d4.png"
except UploadError as exc:
    flash(str(exc), "danger")
```

Validates the extension against an allowlist (`png`, `jpg`, `jpeg`, `gif`,
`webp`, `pdf` by default — pass `allowed_extensions={...}` to override),
generates a collision-safe filename, and saves under
`static/uploads/`. Request size is capped globally by
`MAX_CONTENT_LENGTH` (5 MB by default) — Flask rejects anything bigger with
a 413 before your view even runs.

## Internationalization

`en` (source language, matches the strings actually written in the code)
and `tr` are wired up via Flask-Babel. `{{ get_locale() }}` drives
`<html lang="...">`, and `GET /set-locale/<locale>` (used by the navbar
switcher) stores the choice in the session.

To translate a string:

```python
from flask_babel import gettext as _  # eager — inside a request
from flask_babel import lazy_gettext as _l  # lazy — module-level (e.g. form field labels)
```

```jinja
{{ _('Some text') }}
```

After adding or changing translatable strings:

```bash
uv run pybabel extract -F babel.cfg -k _l -o messages.pot .
uv run pybabel update -i messages.pot -d app/translations
# fill in the empty msgstr "" entries in app/translations/tr/LC_MESSAGES/messages.po
uv run pybabel compile -d app/translations
```

To add a new language: `uv run pybabel init -i messages.pot -d app/translations -l <code>`,
translate, compile, then add `<code>` to `LANGUAGES` in `.env`.

## Cost calculator

A unit-cost and sale-price calculator for a workshop that builds artificial
bonsai trees — the first business feature layered on top of the boilerplate.
Everything below is behind `@login_required`.

| Page | What it does |
| --- | --- |
| `/materials` | Raw-material catalogue (name, category, unit, unit cost) with full CRUD |
| `/calculator` | Pick materials and quantities, add labor/overhead/margin/tax, see the price update live, save the recipe |
| `/recipes` | Saved recipes, with a detail page and re-editing in the calculator |

```bash
uv run flask seed-materials          # ten example materials to start from
uv run flask seed-materials --force  # also reset the unit cost of ones already there
```

### The formula

`app/helpers/costing_helpers.py` owns it, as pure arithmetic — no database,
no request, so it can be called from a route, `flask shell`, or a job alike:

```
total_material_cost = Σ (quantity × unit_cost)
labor_cost          = labor_hours × hourly_rate
overhead_cost       = (total_material_cost + labor_cost) × overhead_% / 100
net_cost            = total_material_cost + labor_cost + overhead_cost
price_before_tax    = net_cost × (1 + profit_margin_% / 100)
suggested_price     = price_before_tax × (1 + tax_% / 100)
```

`static/assets/js/calculator.js` mirrors it for the live summary card — keep
the two in step. The browser's numbers are a preview and nothing more:
`RecipeService.save()` re-reads every unit cost from the database and
recomputes all totals, so a tampered POST body can't set its own price.

### Two deliberate choices

- **`RecipeItem.unit_cost_snapshot`** — a saved recipe stores the unit cost
  it was priced at. Repricing a material later changes future calculations,
  never the history of one already saved.
- **Materials are soft-deleted when in use** — deleting a material that a
  saved recipe references would break that recipe, so it's deactivated
  instead (hidden from the picker, still shown on the recipes that use it).
  Unused materials are deleted outright.

## Roadmap

- [ ] `docker-compose.yml` for a local MySQL/PostgreSQL/Redis to test against
- [ ] GitHub Actions CI (lint + test)

## License

MIT — see [LICENSE](LICENSE).
