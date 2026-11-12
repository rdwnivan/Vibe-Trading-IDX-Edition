"""HTTP delivery for the shared personal IDX research tool."""

import asyncio
import json
from typing import Awaitable, Callable

from fastapi import Depends, FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from src.tools.idx_research_tool import DEFAULT_LOOKBACK, MAX_LOOKBACK, MAX_SYMBOLS, IDXResearchTool
from src.tools.symbol_search_tool import SymbolSearchTool


class IDXResearchRequest(BaseModel):
    """Bound request size before market-data acquisition."""

    model_config = ConfigDict(extra="forbid", strict=True)
    codes: list[str] = Field(min_length=1, max_length=MAX_SYMBOLS)
    lookback: int = Field(default=DEFAULT_LOOKBACK, ge=20, le=MAX_LOOKBACK)
    end_date: str | None = None


def register_idx_research_routes(app: FastAPI, require_auth: Callable[..., Awaitable[None]]) -> None:
    """Use the host's existing auth dependency; keep I/O off the event loop."""

    @app.get("/api/research/idx/symbols", dependencies=[Depends(require_auth)])
    async def search_symbols(query: str = Query(min_length=1, max_length=120)) -> JSONResponse:
        result = json.loads(await asyncio.to_thread(SymbolSearchTool().execute, query=query, market="idx", limit=20))
        return JSONResponse(result, status_code=200 if result["ok"] else 400)

    @app.post("/api/research/idx", dependencies=[Depends(require_auth)])
    async def research(request: IDXResearchRequest) -> JSONResponse:
        result = json.loads(await asyncio.to_thread(IDXResearchTool().execute, **request.model_dump()))
        return JSONResponse(result, status_code=200 if result["ok"] else 400)
