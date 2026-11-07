"""Read-only catalog API. No LLM, synthetic fallback, or source-data writes."""

import json
import logging
import os
from pathlib import Path
import sqlite3
from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Path as PathParam, Query, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from .api_models import (CuisinesResult, ErrorResponse, Health, ItemResult, Provenance,
                         SearchParams, SearchResult)
from .catalog import (CatalogUnavailable, catalog_cuisines, catalog_item,
                      catalog_metadata, search_catalog)

logger = logging.getLogger("meal_discovery.api")


class CatalogReader:
    def __init__(self, index: Path, *, allow_test_data=False):
        self.index = index
        self.options = {"allow_test_data": allow_test_data}

    def metadata(self):
        manifest = catalog_metadata(self.index, **self.options)
        try:
            return Provenance.model_validate(manifest).model_dump()
        except ValidationError as error:
            raise CatalogUnavailable("Invalid catalog metadata") from error

    def cuisines(self):
        return catalog_cuisines(self.index, **self.options)

    def item(self, vendor_id, product_id):
        return catalog_item(self.index, vendor_id, product_id, **self.options)

    def search(self, params):
        return search_catalog(self.index, **params.model_dump(), **self.options)


def get_reader(request: Request) -> CatalogReader:
    return request.app.state.catalog_reader


Reader = Annotated[CatalogReader, Depends(get_reader)]
Identifier = Annotated[str, PathParam(min_length=1, max_length=200)]


def create_app(index: Path | None = None) -> FastAPI:
    application = FastAPI(
        title="Meal Discovery AI", version="0.5.0",
        description="Read-only discovery over the official historical Singapore catalog. Prices are normalized dataset values, not currency. No live availability or allergy guarantees.",
        responses={422: {"model": ErrorResponse, "description": "Invalid query parameters"},
                   503: {"model": ErrorResponse, "description": "Verified catalog unavailable"}},
    )
    application.state.catalog_reader = CatalogReader(
        Path(index) if index is not None else Path(os.environ.get("MEAL_CATALOG_INDEX", "data/processed/singapore-catalog-v1.sqlite")))

    @application.middleware("http")
    async def request_trace(request: Request, call_next):
        request.state.request_id = uuid4().hex
        started = perf_counter()
        response = await call_next(request)
        elapsed = (perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["Server-Timing"] = f"app;dur={elapsed:.2f}"
        # Route template excludes item IDs; query strings and bodies are never logged here.
        route = request.scope.get("route")
        logger.info(json.dumps({"request_id": request.state.request_id, "method": request.method,
                                "route": getattr(route, "path", "unmatched"),
                                "status": response.status_code, "elapsed_ms": round(elapsed, 2)}))
        return response

    def error(request, status, code, message, issues=None):
        return JSONResponse(status_code=status, content={"error": {
            "code": code, "message": message, "request_id": request.state.request_id,
            "issues": issues or []}})

    @application.exception_handler(RequestValidationError)
    async def invalid_request(request, exception):
        issues = [{"location": list(issue["loc"]), "message": issue["msg"], "type": issue["type"]}
                  for issue in exception.errors()]
        return error(request, 422, "invalid_request", "Check the query parameters.", issues)

    async def unavailable(request, exception):
        # Never expose filesystem paths, SQL, or source rows through operational errors.
        return error(request, 503, "catalog_unavailable", "The verified catalog is unavailable. Prepare the official index and check configuration.")

    for exception_type in (CatalogUnavailable, sqlite3.Error, OSError, json.JSONDecodeError, ResponseValidationError):
        application.add_exception_handler(exception_type, unavailable)

    @application.exception_handler(ValueError)
    async def invalid_domain_query(request, exception):
        return error(request, 422, "invalid_request", str(exception))

    @application.exception_handler(StarletteHTTPException)
    async def http_error(request, exception):
        codes = {404: "not_found", 405: "method_not_allowed"}
        return error(request, exception.status_code, codes.get(exception.status_code, "http_error"), str(exception.detail))

    @application.get("/health", response_model=Health, tags=["operations"])
    def health():
        return {"status": "ok"}

    @application.get("/ready", response_model=Health, tags=["operations"])
    def ready(reader: Reader):
        reader.metadata()
        return {"status": "ready"}

    @application.get("/v1/catalog/meta", response_model=Provenance, tags=["catalog"])
    def metadata(reader: Reader):
        return reader.metadata()

    @application.get("/v1/catalog/cuisines", response_model=CuisinesResult, tags=["catalog"])
    def cuisines(reader: Reader):
        return reader.cuisines()

    @application.get("/v1/catalog/search", response_model=SearchResult, tags=["catalog"])
    def search(params: Annotated[SearchParams, Query()], reader: Reader):
        return reader.search(params)

    @application.get("/v1/catalog/items/{vendor_id}/{product_id}", response_model=ItemResult,
                     responses={404: {"model": ErrorResponse, "description": "Item not found"}}, tags=["catalog"])
    def item(vendor_id: Identifier, product_id: Identifier, reader: Reader):
        result = reader.item(vendor_id, product_id)
        if result is None:
            raise HTTPException(404, "Item not found in the historical catalog.")
        return result

    return application


app = create_app()
