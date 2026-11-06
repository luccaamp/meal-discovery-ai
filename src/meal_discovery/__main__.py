"""Reproducible data preparation and recommendation experiments."""

import argparse
import csv
import json
from pathlib import Path
import sqlite3

from .audit import audit_directory
from .benchmark import benchmark
from .dataset import prepare_dataset


def write_report(path: Path, result: dict):
    if path.suffix.lower() != ".json":
        raise ValueError("Report must end in .json")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Meal Discovery AI data tools")
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit", help="Inventory extracted CSVs without exporting rows")
    audit.add_argument("--input-dir", type=Path, required=True)
    audit.add_argument("--output", type=Path, required=True)
    audit.add_argument("--encoding", default="utf-8-sig")
    audit.add_argument("--delimiter", default=",")
    prepare = commands.add_parser("prepare", help="Validate explicit CSV mappings and create a SQLite dataset")
    prepare.add_argument("--config", type=Path, required=True)
    prepare.add_argument("--output", type=Path, required=True)
    evaluate = commands.add_parser("benchmark", help="Evaluate fixed-origin next-basket recommendation")
    evaluate.add_argument("--database", type=Path, required=True)
    evaluate.add_argument("--train-end-day", type=int, required=True)
    evaluate.add_argument("--eval-end-day", type=int, required=True)
    evaluate.add_argument("--split", choices=("validation", "test"), default="validation")
    evaluate.add_argument("--k", type=int, default=10)
    evaluate.add_argument("--max-users", type=int)
    evaluate.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "audit":
            if args.output.resolve().is_relative_to(args.input_dir.resolve()):
                raise ValueError("Store the report outside the source data directory")
            result = audit_directory(args.input_dir, encoding=args.encoding, delimiter=args.delimiter)
            write_report(args.output, result)
            print(f"Audited {len(result['files'])} CSV file(s). Report: {args.output}")
        elif args.command == "prepare":
            result = prepare_dataset(args.config, args.output)
            print(f"Dataset ({result['data_kind']}): {args.output}. Counts: {result['counts']}")
        elif args.command == "benchmark":
            if args.output.exists() or args.output.suffix.lower() != ".json":
                raise ValueError("Choose a new .json report path")
            result = benchmark(args.database, train_end_day=args.train_end_day,
                               eval_end_day=args.eval_end_day, split=args.split, k=args.k,
                               max_users=args.max_users)
            write_report(args.output, result)
            print(f"Benchmark ({result['data_kind']}, {args.split}): {args.output}")
    except (OSError, UnicodeError, LookupError, ValueError, TypeError, csv.Error, sqlite3.Error) as error:
        parser.exit(2, f"Operation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
