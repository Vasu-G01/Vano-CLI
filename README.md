# Vano-Tool: Resources to Notion CLI

A small command-line tool that saves resources (videos, articles, docs - anything with a title and a link) straight into a Notion database. You enter a title, a link, and optional notes, and the tool creates a new row in Notion.

## Features

- Header banner with the project name, description, and GitHub link on startup
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
4. Copy the database ID from the database URL.

## Installation

```bash
git clone https://github.com/Vasu-G01/vano-cli-tool.git
cd vano-cli-tool
```

No install step needed: the tool uses only the Python standard library
(`requirements.txt` is intentionally empty).

Once published, you can also install it straight from PyPI (this also gives you
the `vano` command on your PATH):

```bash
pipx install vano-tool   # or: pip install vano-tool
vano
```

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

Create a `.env` file in the project folder, next to `main.py`:

```
NOTION_TOKEN=your_integration_token
NOTION_DATA_SOURCE_ID=your_data_source_id
```

Older setups using `NOTION_DATABASE_ID` or `NOTION_DB_ID` are also accepted as a
fallback for the second variable. Process environment variables take precedence
over values in `.env`.

Never commit `.env` to GitHub. Make sure `.gitignore` contains:

```
.env
```

## Usage

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