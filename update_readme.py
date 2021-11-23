"""Based on https://github.com/simonw/til .

Should be run this after build_database.py - it needs tils.db
"""
import re
import sys
from pathlib import Path

import sqlite_utils

root = Path(__file__).parent.resolve()

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
        index.append(f"## {topic.replace('_', ' ').title()}\n")
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

    # Add separate readmes for each subsection
    with open("README.md") as f:
        tils = [s.split("\n") for s in f.read().split("##")[1:]]
        tils = {
            til[0].strip(): [t for t in til[2:] if len(t) > 0 and "index ends" not in t]
            for til in tils
        }
    for f, t in tils.items():
        with open(Path(f.lower().replace(" ", "_"), "README"), "w") as fp:
            til = "\n".join(t)
            fp.write(f"## {f}\n\n{til}")
