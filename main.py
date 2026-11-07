import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
MAX_NOTES_LEN = 2000  # Notion's hard limit per rich-text object


def load_dotenv(path=".env"):
    """Populate os.environ from a .env file without overwriting existing variables."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


load_dotenv()

ALIASES = {  # legacy variable names kept for backward compatibility
    "NOTION_TOKEN": ("NOTION_TOKEN", "NOTION_API_KEY"),
    "NOTION_DATABASE_ID": ("NOTION_DATABASE_ID", "NOTION_DB_ID", "NOTION_DATA_SOURCE_ID"),
}
TOKEN = next((os.environ[n] for n in ALIASES["NOTION_TOKEN"] if os.environ.get(n)), "")
DB_ID = next((os.environ[n] for n in ALIASES["NOTION_DATABASE_ID"] if os.environ.get(n)), "")


def _headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def api_call(method, endpoint, payload=None):
    """Call the Notion API. Return (parsed_json, None) on success, (None, message) on failure."""
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = Request(f"{API_BASE}/{endpoint}", data=body, headers=_headers(), method=method)
    try:
        return json.loads(urlopen(req).read()), None
    except HTTPError as error:
        try:
            message = json.loads(error.read()).get("message", str(error))
        except (json.JSONDecodeError, AttributeError):
            message = str(error)
        # 401/404 get action-specific text; they are easy to misread otherwise.
        if error.code == 401:
            message = "Notion rejected the token (401). Check that NOTION_TOKEN is a valid integration secret."
        elif error.code == 404 and endpoint.startswith("databases/"):
            message = ("Database not found or not shared with this integration (404). "
                       "In Notion, open the database, click '...' menu, select Connections, and add this integration.")
        return None, message
    except URLError as error:
        return None, str(error.reason)


def check_connection():
    """Fail fast with a clear message if credentials or access are broken."""
    if not TOKEN:
        print("Error: NOTION_TOKEN is not set. "
              "Create an integration at https://www.notion.so/profile/integrations and set NOTION_TOKEN to its secret.")
        return False
    if not DB_ID:
        print("Error: NOTION_DATABASE_ID is not set. "
              "Copy the database ID from its URL in Notion (the 32-char hex string) and set NOTION_DATABASE_ID.")
        return False

    db, error = api_call("GET", f"databases/{DB_ID}")
    if error:
        print("Error:", error)
        return False
    title = "".join(t.get("plain_text", "") for t in db.get("title", []))
    print(f"Connected to Notion. Database: {title or DB_ID}")
    return True


def build_page(title, link, notes):
    props = {"Title": {"title": [{"text": {"content": title}}]}}
    if link:
        props["Link"] = {"url": link}
    if notes:
        props["Notes"] = {"rich_text": [{"text": {"content": notes[:MAX_NOTES_LEN]}}]}
    return {"parent": {"database_id": DB_ID}, "properties": props}


def save_lecture(title, link, notes):
    result, error = api_call("POST", "pages", build_page(title, link, notes))
    if error:
        print("Error:", error)
        return False
    print("Saved to Notion!", f"(page id: {result.get('id')})")
    return True


def prompt_lecture():
    for attempt in range(3):
        try:
            title = input("Title: ").strip()
        except EOFError:
            return None
        if title:
            break
        print("Title is required.")
    else:
        return None
    link = ""
    notes = ""
    try:
        link = input("Link: ").strip()
        notes = input("Notes/caption (optional): ").strip()
    except EOFError:
        pass
    return title, link, notes


def main():
    if not check_connection():
        sys.exit(1)
    lecture = prompt_lecture()
    if lecture is None:
        sys.exit(1)
    sys.exit(0 if save_lecture(*lecture) else 1)


if __name__ == "__main__":
    main()
