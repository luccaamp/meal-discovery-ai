"""Fixed-origin next-basket evaluation with no holdout interactions in training."""

from collections import defaultdict
from datetime import datetime, timezone
import json
from math import ceil, log2
from pathlib import Path
import platform
import statistics
from time import perf_counter

from .dataset import file_hash, open_dataset
from .recommendation import MODELS, Recommender


def ranking_metrics(ranked, relevant, k):
    if k < 1 or not relevant or len(ranked) != len(set(ranked)):
        raise ValueError("Metrics require nonempty targets, positive k and unique ranking")
    hits = [int(item in relevant) for item in ranked[:k]]
    dcg = sum(hit / log2(index + 2) for index, hit in enumerate(hits))
    ideal = sum(1 / log2(index + 2) for index in range(min(k, len(relevant))))
    return {"recall": sum(hits) / len(relevant), "ndcg": dcg / ideal,
            "hit_rate": float(any(hits))}


def baskets(connection, start_day, end_day):
    # Source values are always bound parameters.
    rows = connection.execute("""
        SELECT o.order_id, o.customer_id, i.vendor_id, i.product_id
        FROM orders o JOIN order_items i USING(order_id)
        WHERE o.order_day > ? AND o.order_day <= ?
        ORDER BY o.order_day, o.order_time, o.order_id, i.vendor_id, i.product_id
    """, (start_day, end_day))
    current = None
    customer = None
    items = set()
    for order, user, vendor, product in rows:
        if current is not None and current != order:
            yield customer, items
            items = set()
        current, customer = order, user
        items.add((vendor, product))
    if current is not None:
        yield customer, items


def aggregate(rows):
    if not rows:
        return {"users": 0, "recall": None, "ndcg": None, "hit_rate": None}
    return {"users": len(rows), **{metric: statistics.fmean(row[metric] for row in rows)
                                 for metric in ("recall", "ndcg", "hit_rate")}}


def benchmark(database: Path, *, train_end_day: int, eval_end_day: int,
              split: str = "validation", k: int = 10, max_users: int | None = None) -> dict:
    if train_end_day < 0 or eval_end_day <= train_end_day or k < 1:
        raise ValueError("Require 0 <= train_end_day < eval_end_day and k > 0")
    if split not in {"validation", "test"} or (max_users is not None and max_users < 1):
        raise ValueError("Invalid split or user limit")
    connection = open_dataset(database)
    try:
        manifest = json.loads(connection.execute("SELECT value FROM metadata WHERE key='manifest'").fetchone()[0])
        started = perf_counter()
        model = Recommender(baskets(connection, -1, train_end_day))
        fit_ms = (perf_counter() - started) * 1000
        targets = {}
        for customer, items in baskets(connection, train_end_day, eval_end_day):
            if customer not in targets:
                targets[customer] = items  # first future basket only, no rolling retraining
                if max_users is not None and len(targets) >= max_users:
                    break
        if not targets:
            raise ValueError("Evaluation period has no baskets")
        results = {}
        for name in MODELS:
            all_rows = []
            segments = defaultdict(list)
            latencies = []
            recommended = set()
            for customer, relevant in targets.items():
                started = perf_counter()
                ranking = model.recommend(customer, name, k)
                latencies.append((perf_counter() - started) * 1000)
                recommended.update(ranking)
                row = ranking_metrics(ranking, relevant, k)
                all_rows.append(row)
                segments["warm" if customer in model.history else "cold"].append(row)
            ordered = sorted(latencies)
            results[name] = {
                **aggregate(all_rows),
                "segments": {segment: aggregate(segments[segment]) for segment in ("warm", "cold")},
                "catalog_coverage": len(recommended) / len(model.catalog),
                "latency_ms": {"p50": statistics.median(ordered),
                               "p95": ordered[max(0, ceil(len(ordered) * .95) - 1)]},
            }
        total_targets = sum(len(items) for items in targets.values())
        unknown_targets = sum(len(items - model.catalog) for items in targets.values())
        return {
            "schema_version": 1, "data_kind": manifest["data_kind"], "city": manifest["city"],
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "python_version": platform.python_version(), "database_sha256": file_hash(database),
            "implementation_sha256": {name: file_hash(Path(__file__).with_name(name))
                                      for name in ("benchmark.py", "recommendation.py", "dataset.py")},
            "source_hashes": manifest["source_hashes"],
            "protocol": {"split": split, "train_end_day_inclusive": train_end_day,
                         "eval_end_day_inclusive": eval_end_day, "k": k,
                         "catalog": "items observed in training; no negative sampling",
                         "target": "first order basket per customer after training cutoff",
                         "repeat_items": "allowed", "frozen_training": True,
                         "geographic_filter": False, "max_users": max_users,
                         "user_selection": "chronological first basket, then order_id tie-break",
                         "item_cosine": {"shrinkage": model.shrinkage, "history_limit": model.history_limit}},
            "training": {"users": len(model.history), "items": len(model.catalog), "fit_ms": fit_ms},
            "evaluation": {"users": len(targets), "relevant_items": total_targets,
                           "targets_outside_training_catalog": unknown_targets,
                           "target_catalog_coverage": 1 - unknown_targets / total_targets},
            "models": results,
            "limitations": ["Offline first-basket prediction, not conversion or revenue.",
                            "No current availability or geographical candidate restriction.",
                            "Unknown target items remain in metric denominators as misses.",
                            "User limit, when set, is chronological and not representative sampling.",
                            "Item cosine is an inspectable reference; scale is not yet validated."],
        }
    finally:
        connection.close()
