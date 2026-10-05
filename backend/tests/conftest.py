import pytest
import app.agent.tools as tools
from unittest.mock import MagicMock


@pytest.fixture
def tavily_mock(monkeypatch) -> MagicMock:
    """
    模拟 tavily client ，避免访问真实互联网
    """
    client = MagicMock()
    monkeypatch.setattr(tools, "_get_tavily_client", lambda: client)
    return client
