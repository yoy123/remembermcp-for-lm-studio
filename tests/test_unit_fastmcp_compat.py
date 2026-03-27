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


def test_create_fastmcp_app_falls_back_to_warn_flags(monkeypatch: Any) -> None:
    captured: list[dict[str, Any]] = []

    class DummyFastMCP:
        def __init__(
            self,
            *,
            name: str,
            version: str,
            instructions: str,
            warn_on_duplicate_resources: bool = True,
            warn_on_duplicate_prompts: bool = True,
        ) -> None:
            captured.append(
                {
                    "name": name,
                    "version": version,
                    "instructions": instructions,
                    "warn_on_duplicate_resources": warn_on_duplicate_resources,
                    "warn_on_duplicate_prompts": warn_on_duplicate_prompts,
                }
            )

    monkeypatch.setattr("mode_manager_mcp.fastmcp_compat.FastMCP", DummyFastMCP)

    create_fastmcp_app(name="Mode Manager MCP", version="1.0.0", instructions="hello")

    assert captured == [
        {
            "name": "Mode Manager MCP",
            "version": "1.0.0",
            "instructions": "hello",
            "warn_on_duplicate_resources": True,
            "warn_on_duplicate_prompts": False,
        }
    ]


def test_create_fastmcp_app_falls_back_to_common_kwargs(monkeypatch: Any) -> None:
    captured: list[dict[str, Any]] = []

    class DummyFastMCP:
        def __init__(self, *, name: str, version: str, instructions: str) -> None:
            captured.append(
                {
                    "name": name,
                    "version": version,
                    "instructions": instructions,
                }
            )

    monkeypatch.setattr("mode_manager_mcp.fastmcp_compat.FastMCP", DummyFastMCP)

    create_fastmcp_app(name="Mode Manager MCP", version="1.0.0", instructions="hello")

    assert captured == [
        {
            "name": "Mode Manager MCP",
            "version": "1.0.0",
            "instructions": "hello",
        }
    ]