"""IDX search delivery with synthetic Yahoo responses, no account access."""

import json

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
import pytest

from backtest.engines._market_hooks import _detect_market
from backtest.loaders import yahoo_client
from src.api.idx_research_routes import register_idx_research_routes
from src.tools import symbol_search_tool as ss


@pytest.fixture
def client(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("IDX search must not access connectors or other providers")

    monkeypatch.setattr(ss, "_search_selected_connector", forbidden)
    monkeypatch.setattr(ss, "_search_eastmoney", forbidden)
    monkeypatch.setattr(ss, "_enrich_us_cik", forbidden)
    app = FastAPI()

    async def allowed():
        return None

    register_idx_research_routes(app, allowed)
    return TestClient(app)


def test_ambiguous_query_requires_selection_of_supported_idx_identity(client, monkeypatch):
    monkeypatch.setattr(yahoo_client, "search", lambda query: [
        {"symbol": "BBCA", "quoteType": "EQUITY", "exchange": "NMS"},
        {"symbol": "BBCA.JK", "shortname": "Synthetic Bank", "quoteType": "EQUITY", "exchange": "JKT"},
        {"symbol": "BBCA-W.JK", "quoteType": "EQUITY", "exchange": "JKT"},
        {"symbol": "BBRI.JK", "quoteType": "ETF", "exchange": "JKT"},
        {"symbol": "TLKM.JK", "quoteType": "EQUITY", "exchange": "NMS"},
    ])
    result = client.get("/api/research/idx/symbols", params={"query": "BBCA"})
    assert result.status_code == 200
    assert result.json()["data"]["candidates"] == [{
        "symbol": "BBCA.JK", "name": "Synthetic Bank", "market": "id", "type": "equity",
        "exchange": "JKT", "source": "yahoo", "venue": "IDX", "currency": "IDR",
    }]
    assert _detect_market("BBCA") == "us_equity"


def test_empty_search_is_distinct_from_provider_failure(client, monkeypatch):
    monkeypatch.setattr(yahoo_client, "search", lambda query: [])
    data = client.get("/api/research/idx/symbols", params={"query": "missing"}).json()["data"]
    assert data["candidates"] == []
    assert data["sources"] == {"yahoo": "ok"}


def test_provider_failure_remains_visible(client, monkeypatch):
    def unavailable(query):
        raise RuntimeError("Synthetic outage")

    monkeypatch.setattr(yahoo_client, "search", unavailable)
    data = client.get("/api/research/idx/symbols", params={"query": "bank"}).json()["data"]
    assert data["candidates"] == []
    assert "Synthetic outage" in data["sources"]["yahoo"]


@pytest.mark.parametrize("query", ["", " " , "x" * 121])
def test_invalid_query_is_rejected_before_provider(client, monkeypatch, query):
    def forbidden(query):
        raise AssertionError("Invalid request must not search")

    monkeypatch.setattr(yahoo_client, "search", forbidden)
    assert client.get("/api/research/idx/symbols", params={"query": query}).status_code in (400, 422)


def test_search_requires_auth_before_provider(monkeypatch):
    app = FastAPI()

    async def denied():
        raise HTTPException(401, "Authentication required")

    register_idx_research_routes(app, denied)
    assert TestClient(app).get("/api/research/idx/symbols", params={"query": "BBCA"}).status_code == 401


def test_invalid_scope_is_rejected():
    assert json.loads(ss.SymbolSearchTool().execute(query="BBCA", market="unknown"))["ok"] is False
