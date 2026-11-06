"""Command line entry point for the initial data audit."""

import argparse
import csv
import json
from pathlib import Path

from .audit import audit_directory


def main() -> int:
    parser = argparse.ArgumentParser(description="Meal Discovery AI data tools")
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit", help="Inventory extracted CSVs without exporting rows")
    audit.add_argument("--input-dir", type=Path, required=True)
    audit.add_argument("--output", type=Path, required=True)
    audit.add_argument("--encoding", default="utf-8-sig")
    audit.add_argument("--delimiter", default=",")
    args = parser.parse_args()
    try:
        if args.output.suffix.lower() != ".json":
            raise ValueError("Output must be a JSON file")
        if args.output.resolve().is_relative_to(args.input_dir.resolve()):
            raise ValueError("Store the report outside the source data directory")
        result = audit_directory(args.input_dir, encoding=args.encoding, delimiter=args.delimiter)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, UnicodeError, LookupError, ValueError, csv.Error) as error:
        parser.exit(2, f"Audit failed: {error}\n")
    print(f"Audited {len(result['files'])} CSV file(s). Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
