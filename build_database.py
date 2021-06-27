"""Taken from https://github.com/simonw/til ."""
import os
import pathlib
import time
from datetime import timezone
from typing import Dict

import git
import httpx
import sqlite_utils
from sqlite_utils.db import NotFoundError

root = pathlib.Path(__file__).parent.resolve()


def created_changed_times(repo_path: str, ref: str = "main") -> Dict[str, str]:
    """Determine creation time in UTC time zone."""
    created_changed_times = {}
    repo = git.Repo(repo_path, odbt=git.GitDB)
    commits = reversed(list(repo.iter_commits(ref)))
    for commit in commits:
        dt = commit.committed_datetime
        affected_files = list(commit.stats.files.keys())
        for filepath in affected_files:
            if filepath not in created_changed_times:
                created_changed_times[filepath] = {
                    "created": dt.isoformat(),
                    "created_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            created_changed_times[filepath].update(
                {
                    "updated": dt.isoformat(),
                    "updated_utc": dt.astimezone(timezone.utc).isoformat(),
                }
            )
    return created_changed_times


def build_database(repo_path: str) -> None:
    """Build a SQLite database from TILs."""
    all_times = created_changed_times(repo_path)
    db = sqlite_utils.Database(repo_path / "tils.db")
    table = db.table("til", pk="path")
    for filepath in root.glob("*/*.md"):
        fp = filepath.open()
        title = fp.readline().lstrip("#").strip()
        body = fp.read().strip()
        path = str(filepath.relative_to(root))
        slug = filepath.stem
        parent_dir = filepath.parent.stem
        url = f"https://cheginit.github.io/til/{parent_dir}/{slug}.html"
        # Do we need to render the markdown?
        path_slug = path.replace("/", "_")
        try:
            row = table.get(path_slug)
            previous_body = row["body"]
            previous_html = row["html"]
        except (NotFoundError, KeyError):
            previous_body = None
            previous_html = None
        record = {
            "path": path_slug,
            "slug": slug,
            "topic": path.split("/")[0],
            "title": title,
            "url": url,
            "body": body,
        }
        if (body != previous_body) or not previous_html:
            retries = 0
            response = None
            while retries < 3:
                headers = {}
                token = os.environ.get("GITHUB_TOKEN")
                if token:
                    headers = {"authorization": f"Bearer {token}"}
                response = httpx.post(
                    "https://api.github.com/markdown",
                    json={
                        # mode=gfm would expand #13 issue links and suchlike
                        "mode": "markdown",
                        "text": body,
                    },
                    headers=headers,
                )
                if response.status_code == 200:
                    record["html"] = response.text
                    print(f"Rendered HTML for {path}")
                    break
                else:
                    print("  sleeping 60s")
                    time.sleep(60)
                    retries += 1
            else:
                msg = f"Could not render {path} - last response was {response.headers}"
                raise AssertionError(msg)
        record.update(all_times[path])
        with db.conn:
            table.upsert(record, alter=True)

    table.enable_fts(["title", "body"], tokenize="porter", create_triggers=True, replace=True)


if __name__ == "__main__":
    build_database(root)
