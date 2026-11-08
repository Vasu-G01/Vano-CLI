import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BANNER_WIDTH = 62
PROJECT_NAME = "VANO-TOOL"
PROJECT_DESC = "Save your resources straight into Notion"
PROJECT_GITHUB = "https://github.com/Vasu-G01/vano-cli-tool"


def load_env():
    # Dev: .env next to main.py. Installed (pip/pipx): .env in the working directory.
    seen = set()
    for env_file in (Path(__file__).parent / ".env", Path.cwd() / ".env"):
        if env_file in seen or not env_file.is_file():
            continue
        seen.add(env_file)
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"'))


load_env()

TOKEN = os.environ.get("NOTION_TOKEN")
DS_ID = (
    os.environ.get("NOTION_DATA_SOURCE_ID")
    or os.environ.get("NOTION_DATABASE_ID")
    or os.environ.get("NOTION_DB_ID")
)

if not TOKEN or not DS_ID:
    # Credentials are still missing - main() runs the interactive first-run setup.
    pass


def safe_text(text):
    """Make a string safe to print on a cp1252 Windows console."""
    return str(text).encode("cp1252", errors="replace").decode("cp1252")


def notion_request(path, body):
    """POST to the Notion API and return parsed JSON, or None after printing the error."""
    req = Request(
        f"https://api.notion.com{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Notion-Version": "2025-09-03",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req) as response:
            return json.load(response)
    except HTTPError as error:
        try:
            message = json.loads(error.read()).get("message", str(error))
        except (json.JSONDecodeError, AttributeError):
            message = str(error)
        print("Error:", safe_text(message))
    except URLError as error:
        print("Error:", error.reason)
    return None


def show_banner():
    print("=" * BANNER_WIDTH)
    print(PROJECT_NAME.center(BANNER_WIDTH))
    print(safe_text(PROJECT_DESC).center(BANNER_WIDTH))
    print(safe_text(PROJECT_GITHUB).center(BANNER_WIDTH))
    print("=" * BANNER_WIDTH)


def check_connection():
    """Verify credentials and access before showing the menu (page_size=1 query)."""
    data = notion_request(
        f"/v1/data_sources/{DS_ID}/query",
        {"page_size": 1},
    )
    if data is None:
        raise SystemExit(
            "Could not reach the Notion database. Check NOTION_TOKEN, "
            "NOTION_DATA_SOURCE_ID, and that the database is shared with your integration."
        )


UUID_RE = re.compile(r"[0-9a-fA-F]{32}")


def extract_id(value):
    """Accept a bare id, a dashed uuid, or a pasted Notion URL and return the id."""
    value = value.strip().replace("-", "")
    match = UUID_RE.search(value)
    return match.group(0) if match else None


def prompt_credentials():
    """Interactive first-run setup: collect credentials when none are configured."""
    global TOKEN, DS_ID
    print()
    print("No Notion credentials found yet. One-time setup:")
    print("  1. NOTION_TOKEN - the integration secret from notion.so/my-integrations")
    print("  2. NOTION_DATA_SOURCE_ID - the id of the database shared with that")
    print("     integration (paste the bare id, uuid, or the database URL)")
    print()
    while not TOKEN:
        value = input("NOTION_TOKEN: ").strip()
        if not value:
            print("This value is required.")
            continue
        if not (value.startswith("secret_") or value.startswith("ntn_")):
            print("Note: Notion integration secrets usually start with 'secret_' or 'ntn_'.")
        TOKEN = value
        print(f"Token accepted: ...{TOKEN[-4:]}")
    while not DS_ID:
        value = input("NOTION_DATA_SOURCE_ID: ").strip()
        extracted = extract_id(value)
        if not extracted:
            print("That does not look like a Notion id or URL. Paste the database")
            print("URL or the 32-character id from it.")
            continue
        DS_ID = extracted
        print(f"Database id accepted: {DS_ID}")
    maybe_save_env()


def maybe_save_env():
    """Offer to write the just-entered credentials to .env in the current folder."""
    choice = input("Save these to .env in this folder for next time? (Y/n): ").strip().lower()
    if choice not in ("", "y", "yes"):
        os.environ["NOTION_TOKEN"] = TOKEN
        os.environ["NOTION_DATA_SOURCE_ID"] = DS_ID
        print("Credentials kept in memory for this run only.")
        return
    env_path = Path.cwd() / ".env"
    os.environ["NOTION_TOKEN"] = TOKEN
    os.environ["NOTION_DATA_SOURCE_ID"] = DS_ID
    lines = []
    if env_path.is_file():  # keep unrelated keys that may already be there
        keys = ("NOTION_TOKEN", "NOTION_DATA_SOURCE_ID", "NOTION_DATABASE_ID", "NOTION_DB_ID")
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not any(line.strip().startswith(k + "=") for k in keys):
                lines.append(line)
    lines.append(f"NOTION_TOKEN={TOKEN}")
    lines.append(f"NOTION_DATA_SOURCE_ID={DS_ID}")
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved to {env_path}. It is already covered by .gitignore in this repo.")


def save_resource(title, link, notes):
    props = {
        "Title": {"title": [{"text": {"content": title}}]},
        "Link": {"url": link or None},
        "Notes": {"rich_text": [{"text": {"content": notes[:2000]}}]},
    }
    body = {
        "parent": {"type": "data_source_id", "data_source_id": DS_ID},
        "properties": props,
    }
    result = notion_request("/v1/pages", body)
    if result is not None:
        print("Saved to Notion!")


def page_values(page):
    """Pull (title, link, notes) out of a queried Notion page."""
    props = page.get("properties", {})
    title_parts = props.get("Title", {}).get("title") or []
    title = "".join(part.get("plain_text", "") for part in title_parts)
    link = props.get("Link", {}).get("url") or ""
    notes_parts = props.get("Notes", {}).get("rich_text") or []
    notes = "".join(part.get("plain_text", "") for part in notes_parts)
    return title, link, notes


def fetch_all_resources():
    """Query every saved page from the database, newest first. Returns None on error."""
    rows = []
    start_cursor = None
    while True:
        body = {
            "page_size": 100,
            "sorts": [{"timestamp": "created_time", "direction": "descending"}],
        }
        if start_cursor:
            body["start_cursor"] = start_cursor
        data = notion_request(f"/v1/data_sources/{DS_ID}/query", body)
        if data is None:
            return None
        rows.extend(page_values(page) for page in data.get("results", []))
        if data.get("has_more") and data.get("next_cursor"):
            start_cursor = data["next_cursor"]
        else:
            return rows


def print_table(rows):
    """Print rows of (title, link, notes) as an ASCII table with dynamic widths."""
    headers = ["#", "Title", "Link", "Notes"]
    caps = {0: 4, 1: 40, 2: 45, 3: 45}
    numbered = [
        [str(i), title, link, notes]
        for i, (title, link, notes) in enumerate(rows, start=1)
    ]
    widths = [len(h) for h in headers]
    for col in range(len(headers)):
        for row in numbered:
            widths[col] = min(caps[col], max(widths[col], len(safe_text(row[col]))))

    def clip(value, width):
        value = safe_text(value)
        return value if len(value) <= width else value[: width - 3] + "..."

    separator = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(separator)
    print("| " + " | ".join(h.ljust(w) for h, w in zip(headers, widths)) + " |")
    print(separator)
    for row in numbered:
        print("| " + " | ".join(clip(v, w).ljust(w) for v, w in zip(row, widths)) + " |")
    print(separator)
    print(f"{len(numbered)} resource(s) saved.")


def show_resources():
    rows = fetch_all_resources()
    if rows is None:
        return
    if not rows:
        print("No Resources saved yet.")
        return
    print()
    print_table(rows)


def add_resource():
    title = input("Title: ").strip()
    link = input("Link: ").strip()
    notes = input("Notes/caption (optional): ").strip()
    if not title:
        print("Title is required.")
        return
    save_resource(title, link, notes)


def show_menu():
    print()
    print("What do you want to do?")
    print("  1. Show saved Resources (from Notion)")
    print("  2. Add a new Resource")
    print("  3. Exit")


def main():
    show_banner()
    if not TOKEN or not DS_ID:
        prompt_credentials()
    check_connection()
    while True:
        show_menu()
        choice = input("Choose an option (1-3): ").strip()
        if choice == "1":
            show_resources()
        elif choice == "2":
            add_resource()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
