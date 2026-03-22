"""Conftest for smoke tests.

Skips all smoke tests automatically when the stack is not running.
"""

import httpx
import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Skip all smoke tests if services aren't running."""
    try:
        httpx.get("http://localhost:8001/", timeout=2)
    except httpx.ConnectError:
        for item in items:
            item.add_marker(pytest.mark.skip(reason="Stack not running — start with `uv run hhh up`"))
