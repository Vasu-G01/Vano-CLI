# AGENTS.md

Guidance for AI coding agents working in this repository.

## What this repo is

- Single-file CLI (`main.py`) that saves a resource (title, link, notes) to a Notion database via `https://api.notion.com/v1/pages` — standard-library `urllib` only.
- Requires two environment variables (from `.env`, with process env vars still winning): `NOTION_TOKEN` (integration secret) and `NOTION_DATA_SOURCE_ID` (`NOTION_DATABASE_ID` / `NOTION_DB_ID` accepted as fallbacks). Secrets must never be hardcoded back into source.
- No packaging, tests, CI, lint, or typecheck config exists beyond `pyproject.toml`.

## Packaging / PyPI

- `pyproject.toml` packages the single `main.py` module as distribution `vano-tool` (setuptools, `py-modules = ["main"]`) with a `vano` console script.
- Distribution name is `vano-tool`, but the module name is `main` — if a future install ever collides with another package's top-level `main` module, the fix is renaming the module (e.g. `vano_tool.py`) and updating the entry point; do not duplicate the code into a second file.
- `load_env()` reads `.env` from the module directory (dev) and the current working directory (installed) — keep both lookups when touching it.
- Release flow is documented in README.md "Publishing to PyPI": bump `version` in `pyproject.toml`, `python -m build`, `twine check dist/*`, `twine upload dist/*`.

## Running

- Run directly: `python main.py`. Reads `.env` (process env vars win) at startup; stdlib only, so there is nothing to install — `requirements.txt` is intentionally empty.
- With no credentials configured, the CLI runs a one-time interactive setup (`prompt_credentials()`): asks for `NOTION_TOKEN` and `NOTION_DATA_SOURCE_ID`, can accept a pasted database **URL** (see `extract_id()`), and offers to save to `.env` in the current working directory. Warn (not fail) on values that look off (`secret_`/`ntn_` prefix, 32-hex id).
- If the configured data source id turns out to be a *database* id (legacy `NOTION_DATABASE_ID` configs), `check_connection()` falls back to `resolve_database_id()`: `GET /v1/databases/{id}` returns its data sources and the first one is adopted. This API version distinguishes data sources from databases; do not revert to treating the ids as equivalent.
- Script is interactive: it prints a banner, runs `check_connection()` (a `page_size=1` query on the data source) and exits before the menu if credentials or access are broken, then loops on a 3-option menu (1: show saved resources as a table, 2: add a resource, 3: exit). Run it in a terminal, not non-interactively.
- README.md and requirements.txt are no longer placeholders — keep them in sync when behavior changes.

## Notion integration gotchas

- A valid integration secret is not enough — the database must be shared with the integration in Notion's UI (database → ••• menu → Connections → add integration). Notion returns 404 (not 401) for a valid token that simply lacks access, which is easy to misread as a wrong database ID.
- Distinguish errors: 401 = invalid/revoked token; 404 = token valid but database not shared; 200 with zero results from `POST /v1/search` = token valid but integration connected to nothing.
- `Notion-Version` header is pinned to `2025-09-03`; changing API behavior may require a version bump. On this version, inserts target `/v1/pages` with a `data_source_id` parent, and reads target `POST /v1/data_sources/{DS_ID}/query`.
- Console output must stay cp1252-safe (no arrows/typographic chars) — non-ASCII output crashes `print` on this Windows console.

## Notion API constraints

- Rich-text content is truncated to 2000 chars (Notion's hard limit per text object) — keep that truncation.
- The Vano-Tool database schema is: `Title` (title), `Link` (url), `Notes` (rich_text). Do not assume the title property is called `Name` — wrong property names fail with `"X is not a property that exists."` Remove/rename properties in Notion and this breaks until the code matches.
- `Link` is a `url` property and must be `None` (never empty string) when blank.
- Errors are surfaced as JSON `{message}` from the Notion API; preserve that error-printing behavior.
