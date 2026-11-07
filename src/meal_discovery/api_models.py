"""Public HTTP contracts, separate from retrieval and model implementations."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SearchParams(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, str_strip_whitespace=True)
    query: str = Field(min_length=1, max_length=200)
    cuisine: str | None = Field(default=None, min_length=1, max_length=200)
    min_price: float | None = Field(default=None, ge=0, description="Dataset-normalized price, not currency")
    max_price: float | None = Field(default=None, ge=0, description="Dataset-normalized price, not currency")
    limit: int = Field(default=10, ge=1, le=50)

    @model_validator(mode="after")
    def ordered_prices(self):
        if self.min_price is not None and self.max_price is not None and self.min_price > self.max_price:
            raise ValueError("Minimum price exceeds maximum price")
        return self


class Provenance(BaseModel):
    schema_version: int
    index_version: str
    data_kind: str
    city: str
    source_database_sha256: str
    source_hashes: dict[str, str]
    products: int
    cuisines: int
    price_unit: Literal["dataset_normalized_unit"]
    historical_catalog: Literal[True]
    limitations: list[str]


class Item(BaseModel):
    vendor_id: str
    product_id: str
    name: str
    unit_price: float | None
    primary_cuisine: str


class SearchItem(Item):
    lexical_score: float


class Filters(BaseModel):
    cuisine: str | None
    min_price: float | None
    max_price: float | None


class SearchResult(BaseModel):
    query: str
    total_matches: int
    items: list[SearchItem]
    filters: Filters
    provenance: Provenance
    ranking: str


class ItemResult(BaseModel):
    item: Item
    provenance: Provenance


class Cuisine(BaseModel):
    name: str
    products: int


class CuisinesResult(BaseModel):
    cuisines: list[Cuisine]
    provenance: Provenance


class Health(BaseModel):
    status: Literal["ok", "ready"]


class Issue(BaseModel):
    location: list[str | int]
    message: str
    type: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str
    issues: list[Issue] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    error: ErrorDetail
