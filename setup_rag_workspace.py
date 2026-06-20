from __future__ import annotations

import json
import ssl
from pathlib import Path
from urllib import error, request

ROOT = Path(__file__).resolve().parent
KIRO_DIR = ROOT / "kiro-steering"
ENV_PATH = ROOT / ".env"
PREPARE_PATH = ROOT / "prepare.py"

GITHUB_API_URL = "https://api.github.com/repos/kirodotdev/spirit-of-kiro/contents/.kiro/steering"

SSL_CONTEXT = ssl.create_default_context()
SSL_CONTEXT.check_hostname = False
SSL_CONTEXT.verify_mode = ssl.CERT_NONE


def fetch_json(url: str):
    req = request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "setup-rag-workspace",
        },
    )
    with request.urlopen(req, context=SSL_CONTEXT) as response:
        return json.loads(response.read().decode("utf-8"))


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = request.Request(
        url,
        headers={"User-Agent": "setup-rag-workspace"},
    )
    with request.urlopen(req, context=SSL_CONTEXT) as response:
        destination.write_bytes(response.read())


def write_env_template() -> None:
    ENV_TEMPLATE = """# API keys for your RAG setup
PINECONE_API_KEY=YOUR_PINECONE_API_KEY
COHERE_API_KEY=YOUR_COHERE_API_KEY
"""
    ENV_PATH.write_text(ENV_TEMPLATE, encoding="utf-8")


def write_prepare_script() -> None:
    PREPARE_SCRIPT = """from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.getenv(\"PINECONE_API_KEY\", \"\")
COHERE_API_KEY = os.getenv(\"COHERE_API_KEY\", \"\")

if not PINECONE_API_KEY or not COHERE_API_KEY:
    raise RuntimeError(
        \"Please fill in your API keys in the .env file before running the project.\"
    )

print(\"Environment loaded successfully.\")
"""
    PREPARE_PATH.write_text(PREPARE_SCRIPT, encoding="utf-8")


def main() -> None:
    KIRO_DIR.mkdir(parents=True, exist_ok=True)

    try:
        entries = fetch_json(GITHUB_API_URL)
    except error.URLError as exc:
        print(f"Warning: could not fetch repo contents ({exc}). Continuing with local templates.")
        entries = []

    markdown_files = [entry for entry in entries if entry.get("name", "").endswith(".md")]

    for entry in markdown_files:
        file_name = entry["name"]
        raw_url = entry.get("download_url")
        if not raw_url:
            continue
        destination = KIRO_DIR / file_name
        try:
            download_file(raw_url, destination)
            print(f"Downloaded: {destination.name}")
        except error.URLError as exc:
            print(f"Warning: failed to download {file_name}: {exc}")

    write_env_template()
    write_prepare_script()

    print(f"Created: {ENV_PATH}")
    print(f"Created: {PREPARE_PATH}")
    print(f"Created directory: {KIRO_DIR}")


if __name__ == "__main__":
    main()
