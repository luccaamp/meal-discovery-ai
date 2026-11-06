"""Small invented fixture to verify the pipeline, never a DHRD result."""

import csv
import json
from pathlib import Path

from .benchmark import benchmark
from .dataset import CONTRACTS, prepare_dataset


def write_synthetic_source(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    tables = {
        "vendors": [("v1", "illustrative category")],
        "products": [("v1", item, f"Synthetic item {item}", "1.0") for item in ("a", "b", "c", "future")],
        "orders": [
            ("o1", "u1", "v1", "a", 0, "12:00:00"),
            ("o2", "u2", "v1", "a", 0, "13:00:00"),
            ("o2", "u2", "v1", "b", 0, "13:00:00"),
            ("o3", "u3", "v1", "c", 1, "12:00:00"),
            ("o4", "u1", "v1", "b", 2, "12:00:00"),
            ("o5", "new-user", "v1", "future", 2, "13:00:00"),
            ("o6", "u1", "v1", "c", 3, "12:00:00"),
        ],
    }
    config = {"data_kind": "synthetic", "city": "invented-test-city",
              "source_url": "synthetic://handwritten-fixture", "license": "MIT", "tables": {}}
    for name, rows in tables.items():
        path = directory / f"{name}.csv"
        with path.open("x", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(CONTRACTS[name])
            writer.writerows(rows)
        config["tables"][name] = {"path": path.name, "columns": {field: field for field in CONTRACTS[name]}}
    path = directory / "source.json"
    with path.open("x", encoding="utf-8") as stream:
        json.dump(config, stream, indent=2)
    return path


def run_demo(directory: Path) -> dict:
    if directory.exists():
        raise ValueError("Choose a new demo output directory; existing files are never overwritten")
    config = write_synthetic_source(directory / "raw")
    prepare_dataset(config, directory / "dataset.sqlite")
    result = benchmark(directory / "dataset.sqlite", train_end_day=1, eval_end_day=2, k=2)
    (directory / "benchmark.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result
