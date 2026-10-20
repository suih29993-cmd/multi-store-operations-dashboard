# -*- coding: utf-8 -*-
"""Assemble the minimal public artifact used by static hosting providers."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
DEPLOY = ROOT / "deploy" / "cloudflare"
ALLOWED_FILES = {"index.html", "_headers", "robots.txt"}
PRIVATE_MARKERS = (
    "C:" + "\\" + "Users" + "\\",
    "C:" + "/" + "Users/",
    "/" + "Users/",
    "file" + "://",
)


def main() -> None:
    dashboard = ROOT / "dashboard.html"
    html = dashboard.read_text(encoding="utf-8")
    if "__DASHBOARD_DATA__" in html:
        raise SystemExit("dashboard.html contains an unresolved data placeholder")
    if "合成演示数据" not in html and "Synthetic demo data" not in html:
        raise SystemExit("dashboard.html is missing the synthetic-data marker")

    lowered = html.lower()
    leaked = [marker for marker in PRIVATE_MARKERS if marker.lower() in lowered]
    if leaked:
        raise SystemExit(f"dashboard.html contains private path markers: {leaked}")

    PUBLIC.mkdir(parents=True, exist_ok=True)
    unexpected = sorted(path.name for path in PUBLIC.iterdir() if path.name not in ALLOWED_FILES)
    if unexpected:
        raise SystemExit(f"public/ contains unexpected entries: {unexpected}")

    shutil.copyfile(dashboard, PUBLIC / "index.html")
    shutil.copyfile(DEPLOY / "_headers", PUBLIC / "_headers")
    shutil.copyfile(DEPLOY / "robots.txt", PUBLIC / "robots.txt")
    print(f"prepared {PUBLIC}")


if __name__ == "__main__":
    main()
