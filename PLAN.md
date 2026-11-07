# PLAN.md

Development plan for vano-cli-tool — a single-file CLI that saves lectures to a Notion database.

## Current state (as of Nov 2026)

- `main.py` works end-to-end: prompts for Title / Link / Notes, then inserts a page into the `Vano-Tool` Notion database (verified: connection check + test insert succeeded).
- Credentials come from user-scope environment variables `NOTION_TOKEN` and `NOTION_DATABASE_ID`.
- `AGENTS.md` documents agent-relevant gotchas (schema, 404/401 diagnostics, API limits).

## M1 — Hygiene / cleanup

- [ ] Delete the test row "TEST - safe to delete" from the Notion database (created during connection testing).
- [ ] Rotate the integration token (it previously sat in plaintext in `main.py` on this machine), then update the `NOTION_TOKEN` user env var with the new secret.
- [ ] Fill in `README.md`: what the tool does, one-time Notion setup (integration + share database + env vars), usage (`python main.py`), and the required property schema.
- [ ] Decide whether `requirements.txt` stays empty (stdlib only) or gets a comment saying "no dependencies".

## M2 — CLI robustness

- [ ] Non-interactive mode for automation: `python main.py "Title" --link URL --notes "..."` while keeping the interactive prompts when args are absent.
- [ ] Input validation: warn (not fail) when `Link` is not a valid URL, since Notion will reject bad `url` values with a schema error.
- [ ] Schema self-check: on connection, read database properties and fail early with the actual property names instead of a generic "X is not a property that exists" after a failed insert.
- [ ] Optional retry on 429 rate-limit responses (Notion rate limit: ~3 requests/second).

## M3 — Feature ideas (pick what's useful, drop the rest)

- [ ] Multi-note import: read from a `.txt`/`.csv` file and save many lectures in one run.
- [ ] `--list` command: show recent entries from the database.
- [ ] Tag/status support if you add properties like `Subject` or `Date` to the database — then update the `props` dict and `AGENTS.md` schema section together.
- [ ] Package with `pyproject.toml` and a console entry point (`vano "Title"`) if this grows beyond one file.

## Standing conventions for any change

- Keep stdlib-only unless a feature genuinely needs more (no install step today is a feature).
- Never hardcode the token or database ID; env vars only.
- Keep output cp1252-safe (Windows console).
- Update `AGENTS.md` whenever the schema, env contract, or run instructions change.
