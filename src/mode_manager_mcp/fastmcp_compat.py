"""Compatibility helpers for FastMCP version differences."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP


def create_fastmcp_app(*, name: str, version: str, instructions: str) -> FastMCP:
    """Create a FastMCP app compatible with FastMCP v2 and v3.

    FastMCP v3 removed legacy keyword arguments such as
    ``on_duplicate_resources``, ``on_duplicate_prompts``, and
    ``include_fastmcp_meta``. This helper first tries the v2-style
    initialization and gracefully falls back to the v3-compatible API.
    """

    common_kwargs: dict[str, Any] = {
        "name": name,
        "version": version,
        "instructions": instructions,
    }

    legacy_kwargs: dict[str, Any] = {
        "on_duplicate_resources": "warn",
        "on_duplicate_prompts": "replace",
        "include_fastmcp_meta": True,
    }

    try:
        return FastMCP(**common_kwargs, **legacy_kwargs)
    except TypeError as exc:
        message = str(exc)
        if not any(keyword in message for keyword in legacy_kwargs):
            raise

    return FastMCP(
        **common_kwargs,
        on_duplicate="replace",
    )