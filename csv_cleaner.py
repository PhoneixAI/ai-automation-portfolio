"""Clean a CSV file, normalize whitespace/email values, and remove duplicates.

Usage: python csv_cleaner.py input.csv cleaned.csv
The script emits a sibling JSON report. It does not upload data anywhere.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def clean_csv(source: Path, destination: Path) -> dict[str, int | str]:
    with source.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("CSV must have a header row")
        headers = [field.strip() for field in reader.fieldnames]
        rows: list[dict[str, str]] = []
        seen: set[str] = set()
        duplicate_count = 0
        for raw in reader:
            row = {key.strip(): (value or "").strip() for key, value in raw.items() if key is not None for key in [key]}
            if "email" in row:
                row["email"] = row["email"].lower()
            identity = row.get("email") or "|".join(row.get(header, "") for header in headers)
            if identity in seen:
                duplicate_count += 1
                continue
            seen.add(identity)
            rows.append({header: row.get(header, "") for header in headers})

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    report = {
        "source": str(source),
        "destination": str(destination),
        "rows_written": len(rows),
        "duplicates_removed": duplicate_count,
    }
    report_path = destination.with_suffix(destination.suffix + ".report.json")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python csv_cleaner.py input.csv cleaned.csv", file=sys.stderr)
        return 2
    try:
        report = clean_csv(Path(sys.argv[1]), Path(sys.argv[2]))
    except (OSError, ValueError, csv.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
