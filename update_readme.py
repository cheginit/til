"""Taken from https://github.com/simonw/til ."""
"Run this after build_database.py - it needs tils.db"
import pathlib
import re
import sys

import sqlite_utils

root = pathlib.Path(__file__).parent.resolve()

index_re = re.compile(r"<!\-\- index starts \-\->.*<!\-\- index ends \-\->", re.DOTALL)
count_re = re.compile(r"count-.*-green", re.DOTALL)

COUNT_TEMPLATE = "count-{}-green"

if __name__ == "__main__":
    db = sqlite_utils.Database(root / "tils.db")
    by_topic = {}
    for row in db["til"].rows_where(order_by="created_utc"):
        by_topic.setdefault(row["topic"], []).append(row)
    index = ["<!-- index starts -->"]
    for topic, rows in by_topic.items():
        index.append(f"## {topic}\n")
        for row in rows:
            index.append(f'* [{row["title"]}]({row["url"]}) - {row["created"].split("T")[0]}')
        index.append("")
    if index[-1] == "":
        index.pop()
    index.append("<!-- index ends -->")
    if "--rewrite" in sys.argv:
        readme = root / "README.md"
        index_txt = "\n".join(index).strip()
        readme_contents = readme.open().read()
        rewritten = index_re.sub(index_txt, readme_contents)
        rewritten = count_re.sub(COUNT_TEMPLATE.format(db["til"].count), rewritten)
        readme.open("w").write(rewritten)
    else:
        print("\n".join(index))
