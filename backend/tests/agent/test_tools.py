import inspect
import os
from unittest.mock import patch

import pytest

from app.agent import tools
from app.agent.tools import CLASS_REGISTER, REGISTER, Interrupt


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


# read / bash 行为测试，只操作临时目录，不依赖外部环境


def test_read_returns_file_content(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello", encoding="utf-8")
    assert REGISTER["read"](path=str(f)) == "hello"


def test_read_keeps_multiline_content(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("line1\nline2\n", encoding="utf-8")
    assert REGISTER["read"](path=str(f)) == "line1\nline2\n"


def test_read_strips_bom(tmp_path):
    f = tmp_path / "bom.txt"
    f.write_text("hi", encoding="utf-8-sig")
    assert REGISTER["read"](path=str(f)) == "hi"


def test_read_accepts_chinese_content(tmp_path):
    f = tmp_path / "zh.md"
    f.write_text("你好，世界", encoding="utf-8")
    assert REGISTER["read"](path=str(f)) == "你好，世界"


def test_read_missing_file_raises(tmp_path):
    with pytest.raises(OSError, match="is not a file"):
        REGISTER["read"](path=str(tmp_path / "nope.txt"))


def test_read_directory_raises(tmp_path):
    with pytest.raises(OSError, match="is not a file"):
        REGISTER["read"](path=str(tmp_path))


def test_bash_success():
    assert REGISTER["bash"](command="echo hi") == "Return_code:0\nstdout:hi"


def test_bash_nonzero_exit_keeps_code():
    assert REGISTER["bash"](command="exit 3") == "Return_code:3\nstdout:"


def test_bash_captures_stderr():
    """getstatusoutput 把 stderr 并进 stdout，模型需要看得到报错"""
    out = REGISTER["bash"](command="echo oops >&2; exit 1")
    assert out == "Return_code:1\nstdout:oops"


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
