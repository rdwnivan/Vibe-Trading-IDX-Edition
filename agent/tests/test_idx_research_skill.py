"""The IDX method must be discoverable and usable by the existing skill tool."""

import json
import asyncio
from pathlib import Path

from src.agent.skills import SkillsLoader
from src.tools.load_skill_tool import LoadSkillTool


def loader(tmp_path):
    return SkillsLoader(
        Path(__file__).resolve().parents[1] / "src" / "skills",
        user_skills_dir=tmp_path,
    )


def test_idx_method_is_discoverable_for_agent_selection(tmp_path):
    descriptions = loader(tmp_path).get_descriptions()
    assert "idx-research:" in descriptions
    assert ".JK" in descriptions.split("idx-research:", 1)[1].splitlines()[0]


def test_idx_method_loads_completely_in_one_tool_result(tmp_path):
    result = json.loads(LoadSkillTool(loader(tmp_path)).execute(name="idx-research"))
    assert result["status"] == "ok"
    assert result["complete"] is True
    assert result["mode"] == "document"
    assert "idx_research" in result["content"]
    assert "get_stock_profile" in result["content"]


def test_idx_method_exposes_separate_snapshot_and_evidence_instructions(tmp_path):
    tool = LoadSkillTool(loader(tmp_path))
    snapshot = json.loads(tool.execute(name="idx-research", section="Profil snapshot opsional"))
    evidence = json.loads(tool.execute(name="idx-research", section="Jawaban berbukti"))
    assert snapshot["status"] == evidence["status"] == "ok"
    assert "publication_time" in snapshot["content"]
    assert "financial_currency" in snapshot["content"]
    assert "dataset_fingerprint" in evidence["content"]
    assert "unavailable" in evidence["content"]


def test_idx_method_loads_over_mcp_without_an_llm(monkeypatch, tmp_path):
    from fastmcp import Client
    import mcp_server

    monkeypatch.setattr(mcp_server, "_skills_loader", loader(tmp_path))

    async def call():
        async with Client(mcp_server.mcp) as client:
            return await client.call_tool("load_skill", {"name": "idx-research"})

    result = json.loads(asyncio.run(call()).content[0].text)
    assert result["status"] == "ok"
    assert result["complete"] is True
    assert "Profil snapshot opsional" in result["content"]
