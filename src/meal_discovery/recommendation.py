"""Inspectable training-only reference recommenders, not production-scale ANN."""

from collections import Counter, defaultdict
from math import sqrt

Item = tuple[str, str]
MODELS = ("popularity", "repeat", "item_cosine")


class Recommender:
    def __init__(self, training_baskets, *, shrinkage: float = 10.0, history_limit: int = 20):
        if shrinkage < 0 or history_limit < 1:
            raise ValueError("Invalid similarity parameters")
        self.shrinkage = shrinkage
        self.history_limit = history_limit
        self.popularity = Counter()
        self.history = defaultdict(Counter)
        self.item_users = defaultdict(set)
        for customer, items in training_baskets:
            unique = set(items)
            self.popularity.update(unique)
            self.history[customer].update(unique)
            for item in unique:
                self.item_users[item].add(customer)
        if not self.popularity:
            raise ValueError("Training period has no items")
        self.catalog = frozenset(self.popularity)
        self.fallback = sorted(self.catalog, key=lambda item: (-self.popularity[item], item))

    def recommend(self, customer: str, model: str, k: int) -> list[Item]:
        if model not in MODELS or k < 1:
            raise ValueError("Unknown model or invalid k")
        history = self.history.get(customer, Counter())
        if model == "popularity" or not history:
            return self.fallback[:k]
        if model == "repeat":
            ranked = sorted(history, key=lambda item: (-history[item], -self.popularity[item], item))
        else:
            scores = defaultdict(float)
            seeds = sorted(history, key=lambda item: (-history[item], item))[:self.history_limit]
            for seed in seeds:
                common_users = Counter()
                for peer in sorted(self.item_users[seed]):
                    common_users.update(self.history[peer].keys())
                for item, overlap in common_users.items():
                    if item == seed:
                        continue
                    cosine = overlap / sqrt(len(self.item_users[seed]) * len(self.item_users[item]))
                    scores[item] += cosine * overlap / (overlap + self.shrinkage)
            ranked = sorted(scores, key=lambda item: (-scores[item], -self.popularity[item], item))
        # Repeats are allowed; use deterministic popularity backfill without duplicate IDs.
        result = ranked[:k]
        selected = set(result)
        for item in self.fallback:
            if len(result) >= k:
                break
            if item not in selected:
                result.append(item)
                selected.add(item)
        return result
