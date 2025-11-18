#!/usr/bin/env python3
"""
Lightweight smoke tests for SafarSavvy transport data.

These checks ensure that every published route (1–22 plus 2A) in
`data/transport/uet_bus_routes.md` has both Morning and Afternoon
tables so the RAG chatbot always has structured context to cite.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
ROUTE_FILE = REPO_ROOT / "data" / "transport" / "uet_bus_routes.md"
EXPECTED_ROUTES = [
    "1",
    "2",
    "2A",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
    "22",
]

ROUTE_BLOCK_RE = re.compile(
    r"## Route ([0-9A-Za-z]+)\s+—[^\n]*\n(.*?)(?=\n## Route|\Z)", re.S
)


@dataclass
class RouteCheck:
    has_morning: bool
    has_afternoon: bool
    table_count: int
    snippet: str


def load_route_sections(markdown: str) -> Dict[str, RouteCheck]:
    sections: Dict[str, RouteCheck] = {}
    for match in ROUTE_BLOCK_RE.finditer(markdown):
        route_id = match.group(1).strip()
        body = match.group(2)
        has_morning = "**Morning" in body
        has_afternoon = "**Afternoon" in body
        table_count = body.count("| # | Stop |")
        snippet = "\n".join(body.strip().splitlines()[:6])
        sections[route_id] = RouteCheck(
            has_morning=has_morning,
            has_afternoon=has_afternoon,
            table_count=table_count,
            snippet=snippet,
        )
    return sections


def run_checks() -> Tuple[int, str]:
    if not ROUTE_FILE.exists():
        return 1, f"Route data file missing: {ROUTE_FILE}"

    contents = ROUTE_FILE.read_text(encoding="utf-8")
    sections = load_route_sections(contents)

    missing_routes = [r for r in EXPECTED_ROUTES if r not in sections]
    missing_morning = [
        r for r, check in sections.items() if r in EXPECTED_ROUTES and not check.has_morning
    ]
    missing_afternoon = [
        r for r, check in sections.items() if r in EXPECTED_ROUTES and not check.has_afternoon
    ]
    missing_tables = [
        r for r, check in sections.items() if r in EXPECTED_ROUTES and check.table_count < 2
    ]

    failures = []
    if missing_routes:
        failures.append(f"Routes not found: {', '.join(missing_routes)}")
    if missing_morning:
        failures.append(f"Routes missing Morning tables: {', '.join(missing_morning)}")
    if missing_afternoon:
        failures.append(f"Routes missing Afternoon tables: {', '.join(missing_afternoon)}")
    if missing_tables:
        failures.append(
            "Routes missing at least one stop table: "
            + ", ".join(missing_tables)
        )

    if failures:
        detail_lines = []
        for failure in failures:
            detail_lines.append(failure)
        return 1, "\n".join(detail_lines)

    return 0, f"All {len(EXPECTED_ROUTES)} routes passed structure checks."


def main() -> None:
    code, message = run_checks()
    print(message)
    sys.exit(code)


if __name__ == "__main__":
    main()

