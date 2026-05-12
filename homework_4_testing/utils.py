"""Testing helpers for inspecting PydanticAI message history."""

from __future__ import annotations

from typing import Any


def collect_tools(messages: list[Any]) -> list[str]:
    """Collect tool names from a PydanticAI message history.

    This helper is intentionally defensive because PydanticAI message internals can
    vary by version. It looks for parts that have tool_name or tool_call fields.
    """
    tool_names: list[str] = []

    for message in messages:
        parts = getattr(message, "parts", []) or []
        for part in parts:
            tool_name = getattr(part, "tool_name", None)
            if tool_name:
                tool_names.append(tool_name)
                continue

            tool_call = getattr(part, "tool_call", None)
            if tool_call is not None:
                name = getattr(tool_call, "name", None)
                if name:
                    tool_names.append(name)

    return tool_names
