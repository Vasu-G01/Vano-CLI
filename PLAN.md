# PLAN.md

Development plan for vano-cli-tool — a single-file CLI that saves resources to a Notion database.

## Current state (as of Nov 2026)

- `pyproject.toml` version is `0.1.1` (not yet uploaded to PyPI — the live release is still 0.1.0).

- `main.py` works end-to-end: interactive menu flow — on startup it prints a
  centered banner (project name `VANO-TOOL`, one-line description, GitHub link
  `https://github.com/Vasu-G01`), runs a connection check, then loops on:
  1. *Show saved resources* — queries the database (paginated, newest first)
     and renders it as an ASCII table with dynamic column widths (cp1252-safe).
  2. *Add a new resource* — the original Title / Link / Notes prompts.
  3. *Exit*.
- Socket-level guard added later: with no credentials configured, `prompt_credentials()`
  asks for `NOTION_TOKEN` and `NOTION_DATA_SOURCE_ID` (accepts a bare id, a
  dashed uuid, or a pasted database URL and extracts the 32-char id), then
  offers to write them to `.env` in the current folder before the connection
  check and menu run. Verified end-to-end with a simulated fresh user.
- v0.1.2: with an older config that holds the Notion *database* id,
  `resolve_database_id()` auto-swaps it for its data source id
  (`GET /v1/databases/{id}` returns the list) and re-checks the connection.
  Verified live with an actual stale database id. Also: all interactive
  prompts go through `ask()`, which reports "Setup interrupted" cleanly on
  piped-input EOF instead of a traceback.
- Credentials come from `.env` (user-scope env vars still win): `NOTION_TOKEN`
  and `NOTION_DATA_SOURCE_ID` (`NOTION_DATABASE_ID` / `NOTION_DB_ID` accepted
  as fallbacks).
- All Notion HTTP traffic goes through one `notion_request()` helper that
  handles `HTTPError` / `URLError` and prints the API `message`.
- `AGENTS.md` documents agent-relevant gotchas (schema, 404/401 diagnostics, API limits).

## M1 — Hygiene / cleanup

- [ ] Delete the test row "TEST - safe to delete" from the Notion database (created during connection testing).
- [ ] Rotate the integration token (it previously sat in plaintext in `main.py` on this machine), then update the `NOTION_TOKEN` user env var with the new secret.
- [x] Fill in `README.md`: expected, usage with the banner/menu session, required property schema, and the `NOTION_DATA_SOURCE_ID` env contract. (Re-check after the token rotation to see whether setup docs or the `.env` sample need further edits.)
- [x] Decide whether `requirements.txt` stays empty (stdlib only) — it stays empty; README now says so explicitly.

## M2 — CLI robustness

- [ ] Non-interactive mode for automation: `python main.py "Title" --link URL --notes "..."` while keeping the interactive prompts when args are absent.
- [ ] Input validation: warn (not fail) when `Link` is not a valid URL, since Notion will reject bad `url` values with a schema error.
- [ ] Schema self-check: on connection, read database properties and fail early with the actual property names instead of a generic "X is not a property that exists" after a failed insert.
- [ ] Optional retry on 429 rate-limit responses (Notion rate limit: ~3 requests/second).

## M3 — Feature ideas (pick what's useful, drop the rest)

- [ ] Multi-note import: read from a `.txt`/`.csv` file and save many resources in one run.
- [x] `--list` command: show recent entries from the database — shipped as menu option *1. Show saved resources* (in-menu table rather than a CLI flag; a `--list` flag can be added on top if scripted use is needed).
- [x] On startup, show the project name centered, a short description, and the GitHub link (`Vasu-G01`).
- [ ] Tag/status support if you add properties like `Subject` or `Date` to the database — then update the `props` dict, the table columns in `print_table()`/`page_values()`, and `AGENTS.md` schema section together.
- [x] Package with `pyproject.toml`: PyPI distribution name `vano-tool`, console entry point `vano` (`vano = "main:main"`), setuptools backend, `main.py` kept as the single module via `py-modules`.
- [x] Published: https://pypi.org/project/vano-tool/ (v0.1.0, wheel + sdist; verified by installing from PyPI into a clean venv and running the `vano` command end-to-end).

## Standing conventions for any change

- Keep stdlib-only unless a feature genuinely needs more (no install step today is a feature).
- Never hardcode the token or database ID; env vars only.
- Keep output cp1252-safe (Windows console).
- Update `AGENTS.md` whenever the schema, env contract, or run instructions change.
