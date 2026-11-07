# Vano-Tool: Lecture Notes to Notion CLI

A small command-line tool that saves lectures (for example, YouTube videos) straight into a Notion database. You enter a title, a link, and optional notes, and the tool creates a new row in Notion.

## Features

- Interactive prompts for title, link, and notes
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
4. Copy the data source ID: open **Manage data sources**, click the `...` next to your data source, and choose **Copy data source ID**.

## Installation

```bash
git clone <your-repo-url>
cd vano-cli-tool
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project folder:

```
NOTION_TOKEN=your_integration_token
NOTION_DATA_SOURCE_ID=your_data_source_id
```

Never commit `.env` to GitHub. Make sure `.gitignore` contains:

```
.env
```

## Usage

```bash
python lectures.py
```

Example session:

```
Title: Intro to Python Functions
Link: https://www.youtube.com/watch?v=example
Notes/caption (optional): Good explanation of default arguments
Saved to Notion!
```

## Project Structure

```
lecture-notion/
├── lectures.py        # main CLI script
├── .env               # secrets (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

## Troubleshooting

- **"object not found" error:** the integration is not connected to the database. Add it under Connections.
- **"property does not exist" error:** column names in Notion must match the script exactly (`Title`, `Link`, `Notes`).
- **Invalid URL error:** the link must start with `http://` or `https://`.

## Ideas for Improvement

- Add a loop to save multiple lectures in one session
- Add Status (Watched / To watch) and Date columns
- Validate links before saving
- Auto-summarize notes with an AI model

## License

MIT