"""
Scraper for Indonesian Wikipedia page tracking school food poisoning incidents.
Uses only Python standard library — no pip installs required.

Usage:
    python wiki_scraper.py [--url URL] [--output OUTPUT]
"""

import csv
import sys
import re
import argparse
import urllib.request
from html.parser import HTMLParser

DEFAULT_URL = "https://id.wikipedia.org/wiki/Daftar_kasus_keracunan_makanan_massal_di_dunia"

COLUMNS = [
    "tanggal_kejadian",
    "provinsi",
    "kabupaten_kota",
    "tempat_sekolah",
    "bergejala",
    "meninggal",
]


def _distribute(text: str, n: int) -> list[str]:
    """Divide a numeric total evenly across n rows, preserving the unit label.

    Returns a list of n strings. The first (n-1) rows get the floor share;
    the last row absorbs the remainder so the values always sum to the original.

    e.g. "236 Siswa", n=6  ->  ["39 Siswa", "39 Siswa", "39 Siswa",
                                 "39 Siswa", "39 Siswa", "41 Siswa"]
    If no number is found (vague text), every row gets the original text.
    """
    m = re.search(r"[\d.,]+", text)
    if not m:
        return [text] * n
    # Handle Indonesian thousand-separator dot: "1.333" -> 1333
    num_str = m.group().replace(".", "").replace(",", ".")
    try:
        total = round(float(num_str))   # treat total as integer
    except ValueError:
        return [text] * n
    unit = text[m.end():].strip()
    base      = total // n
    remainder = total % n
    def fmt(val: int) -> str:
        return f"{val} {unit}".strip() if unit else str(val)
    return [fmt(base)] * (n - 1) + [fmt(base + remainder)]


class TableParser(HTMLParser):
    """SAX-style parser that extracts all tables, handling rowspan/colspan.

    For aggregate columns (bergejala, meninggal — col index >= 4), a rowspan
    means one shared total across multiple school rows.  We store the value
    only on the *first* row of the span and leave the rest blank, so the total
    is not mistakenly repeated for every school.
    """

    # Columns that carry aggregate totals — do NOT propagate their rowspan
    AGGREGATE_COLS = {4, 5}

    def __init__(self):
        super().__init__()
        self.tables: list[dict] = []
        self.current_grid: dict | None = None
        self.current_row: int = 0
        self.col_cursor: int = 0
        self.table_depth: int = 0
        self.in_cell: bool = False
        self.cell_rowspan: int = 1
        self.cell_colspan: int = 1
        self.cell_text: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table":
            self.table_depth += 1
            if self.table_depth == 1:
                self.current_grid = {}
                self.current_row = 0
        elif self.table_depth == 1:
            if tag == "tr":
                self.col_cursor = 0
            elif tag in ("td", "th"):
                grid = self.current_grid
                while grid.get(self.current_row, {}).get(self.col_cursor) is not None:
                    self.col_cursor += 1
                self.cell_rowspan = int(attrs.get("rowspan", 1))
                self.cell_colspan = int(attrs.get("colspan", 1))
                self.in_cell = True
                self.cell_text = []

    def handle_endtag(self, tag):
        if tag == "table":
            if self.table_depth == 1:
                self.tables.append(self.current_grid)
                self.current_grid = None
            self.table_depth -= 1
        elif self.table_depth == 1:
            if tag == "tr":
                self.current_row += 1
            elif tag in ("td", "th") and self.in_cell:
                text = re.sub(r"\s+", " ", "".join(self.cell_text)).strip()
                text = re.sub(r"\s*\[\d+\]\s*$", "", text).strip()
                # Pre-compute distribution list once for aggregate columns.
                dist = (
                    _distribute(text, self.cell_rowspan)
                    if self.cell_rowspan > 1
                    else None
                )
                for r in range(self.cell_rowspan):
                    for c in range(self.cell_colspan):
                        row = self.current_row + r
                        col = self.col_cursor + c
                        if col in self.AGGREGATE_COLS and dist is not None:
                            # r-th element: last row gets base + remainder
                            self.current_grid.setdefault(row, {})[col] = dist[r]
                        else:
                            self.current_grid.setdefault(row, {})[col] = text
                self.col_cursor += self.cell_colspan
                self.in_cell = False
                self.cell_text = []

    def handle_data(self, data):
        if self.in_cell and self.table_depth == 1:
            self.cell_text.append(data)


def fetch_page(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; WikiScraper/1.0; educational use)"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")


def find_incident_table(tables: list[dict]) -> dict | None:
    """Return the table whose first two rows contain the expected column headers."""
    for grid in tables:
        all_text = " ".join(
            grid.get(r, {}).get(c, "")
            for r in range(3)
            for c in range(7)
        )
        if "Tanggal Kejadian" in all_text and "Provinsi" in all_text:
            return grid
    return None


def grid_to_records(grid: dict) -> list[dict]:
    records = []
    for row_idx in sorted(grid.keys()):
        if row_idx < 2:          # skip the two header rows
            continue
        row = grid[row_idx]
        if len(row) < 6:
            continue
        records.append({COLUMNS[i]: row.get(i, "").strip() for i in range(len(COLUMNS))})
    return records


def save_csv(records: list[dict], path: str):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)
    print(f"Saved {len(records)} records to {path}")


def main():
    parser = argparse.ArgumentParser(description="Scrape food poisoning table from Indonesian Wikipedia")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--output", default="/Users/macbook/dataviz_tableau/dataviz_tableau/dataset/keracunan-mbg.csv")
    args = parser.parse_args()

    print(f"Fetching: {args.url}")
    html = fetch_page(args.url)

    table_parser = TableParser()
    table_parser.feed(html)

    grid = find_incident_table(table_parser.tables)
    if grid is None:
        print("ERROR: Could not find the incident table on the page.", file=sys.stderr)
        sys.exit(1)

    records = grid_to_records(grid)
    if not records:
        print("WARNING: No data rows found.", file=sys.stderr)
        sys.exit(1)

    print(f"Parsed {len(records)} rows.")
    save_csv(records, args.output)

    print("\nPreview (first 5 rows):")
    for rec in records[:5]:
        print(rec)


if __name__ == "__main__":
    main()
