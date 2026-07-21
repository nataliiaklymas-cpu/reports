#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenerates admin-3e561cef51.html with live counts of reports in each partner
folder. Reads the local checkout (works in GitHub Actions after actions/checkout).
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADMIN_PATH = os.path.join(ROOT, "admin-3e561cef51.html")

# (folder slug, kind) — order doesn't matter, matching is done by href.
# kind: "internal" -> "N файли"; "weekly" -> "1 тиждень · N локацій"; "files" -> "N звіт(и/ів)"
FOLDERS = [
    ("internal", "internal"),
    ("greek-house", "files"),
    ("salateira", "files"),
    ("salateira-weekly", "weekly"),
    ("muza", "files"),
    ("chornomorka", "files"),
    ("chornomorka-weekly", "weekly"),
    ("evrazia", "files"),
    ("pesto-cafe", "files"),
    ("bufet", "files"),
    ("hesburger", "files"),
    ("this-is-pivbar", "files"),
]


def uk_report_word(n):
    if n % 10 == 1 and n % 100 != 11:
        return "звіт"
    if 2 <= n % 10 <= 4 and not (11 <= n % 100 <= 14):
        return "звіти"
    return "звітів"


REPORT_EXTS = (".html", ".xlsx", ".xls", ".pdf", ".csv", ".pptx")


def count_html_files(path):
    if not os.path.isdir(path):
        return 0
    return len([f for f in os.listdir(path)
                if f.lower().endswith(REPORT_EXTS) and f.lower() != "index.html"])


def latest_week_dir(path):
    if not os.path.isdir(path):
        return None
    dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    if not dirs:
        return None
    return sorted(dirs)[-1]


def build_count(folder_slug, kind):
    path = os.path.join(ROOT, folder_slug)
    if kind == "internal":
        n = count_html_files(path)
        return "%d файли" % n if n else "—"
    if kind == "weekly":
        wk = latest_week_dir(path)
        if not wk:
            return "—"
        n = count_html_files(os.path.join(path, wk))
        return "1 тиждень \u00b7 %d локацій" % n if n else "—"
    n = count_html_files(path)
    return "%d %s" % (n, uk_report_word(n)) if n else "—"


def main():
    with open(ADMIN_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    changed = False
    for slug, kind in FOLDERS:
        count = build_count(slug, kind)
        pattern = re.compile(
            r'(<a href="%s/"><span class="t">[^<]*</span><span class="count">)[^<]*(</span></a>)'
            % re.escape(slug)
        )
        new_html, n = pattern.subn(lambda m: m.group(1) + count + m.group(2), html)
        if n == 0:
            print("WARNING: anchor not found for", slug)
        elif new_html != html:
            changed = True
        html = new_html

    with open(ADMIN_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("admin page regenerated, changed =", changed)


if __name__ == "__main__":
    main()
