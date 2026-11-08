# Vano-Tool: Resources to Notion CLI

A small command-line tool that saves resources (videos, articles, docs - anything with a title and a link) straight into a Notion database. You enter a title, a link, and optional notes, and the tool creates a new row in Notion.

## Features

- Header banner with the project name, description, and GitHub link on startup
- Guided first-run setup: if no credentials exist, `vano` asks for them and offers to save them to `.env`
- Simple menu: **view saved resources** in a clean table, or **add a new one**
- Interactive prompts for title, link, and notes when inserting
- Shows every resource, newest first, in an ASCII table (works on any Windows console)
- Saves directly to a Notion database using the Notion API
- Secrets are kept in a `.env` file, not in the code

## Requirements

- Python 3.8+
- A Notion account
- A Notion integration token

## Notion Setup

1. Go to https://www.notion.so/my-integrations and create a new integration. Copy the secret token.
2. Create a Notion database with these columns (names must match exactly):

   | Column | Type  |
   |--------|-------|
   | Title  | Title |
   | Link   | URL   |
   | Notes  | Text  |

3. Connect the integration to your database: open the database, click the `...` menu, choose **Connections**, and add your integration.
4. Run `vano` — it will ask for your secret and database (id or URL) and finish the setup for you. Advanced users can skip the prompts and instead write a `.env` themselves (see *First run* under Installation). Copy the database ID from the database URL if you go that route.

## Installation

The tool is published on PyPI. The easiest way for anyone to use it:

```bash
pipx install vano-tool   # or: pip install vano-tool
vano
```

That installs the `vano` command on your PATH. No other Python dependencies
(the tool uses only the standard library).

### First run: give it your Notion credentials (guided)

Just run the tool once — it walks you through everything:

```text
vano
==============================================================
                        VANO-TOOL
...
NOTION_TOKEN: ntn_xxxxxxxxxxxx...
Token accepted: ...xxxx
NOTION_DATA_SOURCE_ID: https://www.notion.so/my-workspace-1f2e3d4c...
Database id accepted: 1f2e3d4c...
Save these to .env in this folder for next time? (Y/n): Y
Saved to C:\Users\you\tools\.env
Connecting...
What do you want to do?
  1. Show saved resources (from Notion)
  2. Add a new resource
  3. Exit
```

Steps, one by one:

1. Run `vano`. If no credentials are found, it starts the one-time setup.
2. Paste your **integration secret** as `NOTION_TOKEN` (usually starts with `secret_` or `ntn_`).
3. Paste your **database URL or id** — the tool extracts the 32-character id for you, even from a full Notion URL.
4. Confirm `Y` to save them to `.env` in the current folder (answer `n` to keep them for this run only).
5. The tool verifies the connection and then shows the menu. From now on, `vano` starts straight at the menu.

### Prefer configuring manually?

Either set them once as user environment variables:

```bash
# Windows (run in a NEW terminal afterwards)
setx NOTION_TOKEN "your_integration_token"
setx NOTION_DATA_SOURCE_ID "your_data_source_id"
```

```bash
# macOS / Linux (add to ~/.bashrc or ~/.zshrc)
export NOTION_TOKEN="your_integration_token"
export NOTION_DATA_SOURCE_ID="your_data_source_id"
```

...or keep them in a `.env` file in whatever folder you run `vano` from:

```
NOTION_TOKEN=your_integration_token
NOTION_DATA_SOURCE_ID=your_data_source_id
```

Process environment variables take precedence over `.env` values.
Older setups using `NOTION_DATABASE_ID` or `NOTION_DB_ID` are also accepted
as fallbacks for the second variable.

### Prefer running from source?

```bash
git clone https://github.com/Vasu-G01/vano-cli-tool.git
cd vano-cli-tool
python main.py
```

No install step needed: the tool uses only the Python standard library
(`requirements.txt` is intentionally empty).

## Publishing to PyPI (maintainers)

From the repo root, with PyPI credentials ready:

```bash
pip install build twine
python -m build          # creates dist/ with the wheel and sdist
twine check dist/*       # sanity-check the metadata
twine upload dist/*      # upload (add --repository testpypi for a dry run)
```

Bump the `version` in `pyproject.toml` before every re-upload.

## Configuration

Secrets are supplied either as environment variables or through a `.env` file —
see "First run" under Installation for all options.

For **development in this repo**, keep a `.env` file next to `main.py`:

```
NOTION_TOKEN=your_integration_token
NOTION_DATA_SOURCE_ID=your_data_source_id
```

Never commit `.env` to GitHub. Make sure `.gitignore` contains:

```
.env
```

## Usage

Run the installed command:

```bash
vano
```

Or from a source checkout:

```bash
python main.py
```

Example session:

```
==============================================================
                         VANO-TOOL
           Save your resources straight into Notion
             https://github.com/Vasu-G01/vano-cli-tool
==============================================================

What do you want to do?
  1. Show saved resources (from Notion)
  2. Add a new resource
  3. Exit
Choose an option (1-3): 1

+----+--------------------------+--------------------+----------------+
| #  | Title                    | Link               | Notes          |
+----+--------------------------+--------------------+----------------+
| 1  | Intro to Python          | https://youtu.be/… | Good explana…  |
+----+--------------------------+--------------------+----------------+
1 resource(s) saved.
```

Option **2** walks through the classic prompts:

```
Title: Intro to Python Functions
Link: https://www.youtube.com/watch?v=example
Notes/caption (optional): Good explanation of default arguments
Saved to Notion!
```

The menu reappears after every action, so you can add several resources in one
run or check what is already saved.

## Project Structure

```text
vano-cli-tool/
├── main.py            # the whole CLI (banner, menu, save, list)
├── pyproject.toml     # PyPI packaging metadata (installable as `vano-tool`, command: `vano`)
├── LICENSE            # MIT license, copyright Vasu Gumber
├── .env               # secrets (not committed)
├── .gitignore
├── requirements.txt   # intentionally empty - stdlib only
├── PLAN.md            # development plan
├── AGENTS.md          # notes for AI coding agents
└── README.md
```

## Troubleshooting

- **"object not found" error:** the integration is not connected to the database. Add it under Connections.
- **"property does not exist" error:** column names in Notion must match the script exactly (`Title`, `Link`, `Notes`).
- **Invalid URL error:** the link must start with `http://` or `https://`.

## Ideas for Improvement

- Add a loop to save multiple resources in one session
- Add Status (Watched / To watch) and Date columns
- Validate links before saving
- Auto-summarize notes with an AI model

## License

MIT License - free to use, modify, and distribute.

Copyright (c) 2026 Vasu Gumber. See the [LICENSE](LICENSE) file for the full text.