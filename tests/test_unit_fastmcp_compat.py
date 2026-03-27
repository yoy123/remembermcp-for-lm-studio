from typing import Any

from mode_manager_mcp.fastmcp_compat import create_fastmcp_app


def test_create_fastmcp_app_uses_legacy_kwargs_when_supported(monkeypatch: Any) -> None:
    captured: list[dict[str, Any]] = []

    class DummyFastMCP:
        def __init__(self, **kwargs: Any) -> None:
            captured.append(kwargs)

    monkeypatch.setattr("mode_manager_mcp.fastmcp_compat.FastMCP", DummyFastMCP)

    create_fastmcp_app(name="Mode Manager MCP", version="1.0.0", instructions="hello")

    assert captured == [
        {
            "name": "Mode Manager MCP",
            "version": "1.0.0",
            "instructions": "hello",
            "on_duplicate_resources": "warn",
            "on_duplicate_prompts": "replace",
            "include_fastmcp_meta": True,
        }
    ]


def test_create_fastmcp_app_falls_back_for_fastmcp_v3(monkeypatch: Any) -> None:
    captured: list[dict[str, Any]] = []

    class DummyFastMCP:
        def __init__(self, **kwargs: Any) -> None:
            if "on_duplicate_resources" in kwargs:
                raise TypeError("FastMCP() no longer accepts `on_duplicate_resources`.")
            captured.append(kwargs)

    monkeypatch.setattr("mode_manager_mcp.fastmcp_compat.FastMCP", DummyFastMCP)

    create_fastmcp_app(name="Mode Manager MCP", version="1.0.0", instructions="hello")

    assert captured == [
        {
            "name": "Mode Manager MCP",
            "version": "1.0.0",
            "instructions": "hello",
            "on_duplicate": "replace",
        }
    ]