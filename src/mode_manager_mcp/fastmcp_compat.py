"""Compatibility helpers for FastMCP version differences."""

from __future__ import annotations

from inspect import Parameter, signature
from typing import Any

from fastmcp import FastMCP


def create_fastmcp_app(*, name: str, version: str, instructions: str) -> FastMCP:
    """Create a FastMCP app compatible with multiple FastMCP constructor shapes.

    Different FastMCP releases have used different duplicate-handling
    keyword arguments. Prefer the modern ``on_duplicate_*`` options when
    available, fall back to older ``warn_on_duplicate_*`` booleans when
    needed, and otherwise construct the app with only the shared kwargs.
    """

    common_kwargs: dict[str, Any] = {
        "name": name,
        "version": version,
        "instructions": instructions,
    }

    modern_kwargs: dict[str, Any] = {
        "on_duplicate_resources": "warn",
        "on_duplicate_prompts": "replace",
        "include_fastmcp_meta": True,
    }

    legacy_kwargs: dict[str, Any] = {
        "warn_on_duplicate_resources": True,
        "warn_on_duplicate_prompts": False,
    }

    parameter_info = signature(FastMCP).parameters
    accepts_var_kwargs = any(param.kind is Parameter.VAR_KEYWORD for param in parameter_info.values())

    candidate_kwargs: list[dict[str, Any]] = []

    if accepts_var_kwargs or any(name in parameter_info for name in modern_kwargs):
        candidate_kwargs.append(
            {
                key: value
                for key, value in modern_kwargs.items()
                if accepts_var_kwargs or key in parameter_info
            }
        )

    if accepts_var_kwargs or any(name in parameter_info for name in legacy_kwargs):
        candidate_kwargs.append(
            {
                key: value
                for key, value in legacy_kwargs.items()
                if accepts_var_kwargs or key in parameter_info
            }
        )

    candidate_kwargs.append({})

    for extra_kwargs in candidate_kwargs:
        try:
            return FastMCP(**common_kwargs, **extra_kwargs)
        except TypeError as exc:
            message = str(exc)
            if not extra_kwargs or not any(keyword in message for keyword in extra_kwargs):
                raise

    raise RuntimeError("Unable to create FastMCP app with supported compatibility kwargs.")