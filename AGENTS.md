# AGENTS.md

Guidance for AI coding agents working in this repository.

## What this repo is

- Single-file CLI (`main.py`) that saves a lecture (title, link, notes) to a Notion database via `https://api.notion.com/v1/pages` — standard-library `urllib` only.
- Requires two environment variables set at user scope on this machine: `NOTION_TOKEN` (integration secret) and `NOTION_DATABASE_ID`. Secrets must never be hardcoded back into source.
- No packaging, tests, CI, lint, or typecheck config exists. `README.md` and `requirements.txt` are currently empty files — placeholders, not documentation.

## Running

- Run directly: `python main.py`. Reads env vars at startup; stdlib only, so there is nothing to install — `requirements.txt` is intentionally empty.
- Script is interactive: it prompts for Title / Link / Notes on stdin, so run it in a terminal, not non-interactively. It runs `check_connection()` first (GET on the database) and exits before prompting if credentials or access are broken.

## Notion integration gotchas

- A valid integration secret is not enough — the database must be shared with the integration in Notion's UI (database → ••• menu → Connections → add integration). Notion returns 404 (not 401) for a valid token that simply lacks access, which is easy to misread as a wrong database ID.
- Distinguish errors: 401 = invalid/revoked token; 404 = token valid but database not shared; 200 with zero results from `POST /v1/search` = token valid but integration connected to nothing.
- `Notion-Version` header is pinned to `2022-06-28`; changing API behavior may require a version bump.
- Console output must stay cp1252-safe (no arrows/typographic chars) — non-ASCII output crashes `print` on this Windows console.

## Notion API constraints

- Rich-text content is truncated to 2000 chars (Notion's hard limit per text object) — keep that truncation.
- The Vano-Tool database schema is: `Title` (title), `Link` (url), `Notes` (rich_text). Do not assume the title property is called `Name` — wrong property names fail with `"X is not a property that exists."` Remove/rename properties in Notion and this breaks until the code matches.
- `Link` is a `url` property and must be `None` (never empty string) when blank.
- Errors are surfaced as JSON `{message}` from the Notion API; preserve that error-printing behavior.
