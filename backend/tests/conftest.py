from unittest.mock import MagicMock

import pytest

from app.agent import tools


@pytest.fixture
def tavily_mock(monkeypatch) -> MagicMock:
    """
    模拟 tavily client ，避免访问真实互联网
    """
    client = MagicMock()
    monkeypatch.setattr(tools, "_get_tavily_client", lambda: client)
    return client
