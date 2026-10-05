import inspect
import app.agent.tools as tools
from app.agent.tools import CLASS_REGISTER, REGISTER, Interrupt
import pytest
from unittest.mock import patch
import os


# 结构校验
def test_registries_not_empty():
    """校验注册器存在"""
    assert CLASS_REGISTER, "CLASS_REGISTER 为空？模块没导入成功？"
    assert REGISTER, "REGISTER 为空？"


def test_every_tool_class_has_matching_impl():
    """校验class都有对应的函数"""
    for cls_name in CLASS_REGISTER:
        assert cls_name.lower() in REGISTER, (
            f"工具类 {cls_name} 缺少对应实现函数 {cls_name.lower()}"
        )


@pytest.mark.parametrize("cls_name", sorted(CLASS_REGISTER))
def test_signature_matches_model_fields(cls_name):
    """
    验证：
    pydantic 模型字段与函数签名参数一一对应
    """
    model, fn = CLASS_REGISTER[cls_name], REGISTER[cls_name.lower()]
    params = {
        name: p
        for name, p in inspect.signature(fn).parameters.items()
        if p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
    }
    assert set(params) == set(model.model_fields), (
        f"{cls_name}: 模型字段 {set(model.model_fields)} 与函数参数 {set(params)} 不一致"
    )
    for name, field in model.model_fields.items():
        if field.is_required():
            assert params[name].default is inspect.Parameter.empty, (
                f"{cls_name}.{name} 是必填字段，但函数参数却给了默认值"
            )


# 行为测试，不连接真实互联网
def test_ask_question_raises_interrupt():
    with pytest.raises(Interrupt) as ei:
        REGISTER["ask_question"](question="今天天气如何？")
    assert ei.value.kind == "ask_user"
    assert ei.value.payload == "今天天气如何？"


def test_web_search(tavily_mock):
    tavily_mock.search.return_value = {"results": [{"title": "hi"}]}
    out = REGISTER["web_search"](question="q")
    assert out == str({"results": [{"title": "hi"}]})
    tavily_mock.search.assert_called_once_with("q")


def test_web_extract(tavily_mock):
    tavily_mock.extract.return_value = {
        "results": [{"url": "https://x.com", "raw_content": "ok"}]
    }
    out = REGISTER["web_extract"](urls=["https://x.com"])
    assert out == [{"url": "https://x.com", "raw_content": "ok"}]
    tavily_mock.extract.assert_called_once_with(
        urls=["https://x.com"], include_images=False
    )


def test_client_is_lazy_singleton(monkeypatch):
    """懒加载只构造一次；monkeypatch 结束后自动还原全局 _tavily_client / 环境变量。"""
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    monkeypatch.setattr(tools, "_tavily_client", None)  # 先重置再测
    with patch.object(tools, "TavilyClient", return_value=object()) as ctor:
        c1, c2 = tools._get_tavily_client(), tools._get_tavily_client()
        assert c1 is c2
        assert ctor.call_count == 1
        assert ctor.call_args.kwargs == {"api_key": "test-key"}


# 冒烟测试（默认跳过）

LIVE_CASES = [
    pytest.param("web_search", {"question": "tavily api"}, id="web_search"),
    pytest.param("web_extract", {"urls": ["https://example.com"]}, id="web_extract"),
]


@pytest.mark.integration
@pytest.mark.skipif(not os.getenv("TAVILY_API_KEY"), reason="未配置 TAVILY_API_KEY")
@pytest.mark.parametrize(("fn_name", "kwargs"), LIVE_CASES)
def test_live_tool_reachable(fn_name, kwargs):
    """逐一真实调用一次，验证 key 有效、网络通、返回非空。"""
    out = REGISTER[fn_name](**kwargs)
    assert out, f"{fn_name} 真实调用返回为空"
