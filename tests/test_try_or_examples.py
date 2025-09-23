from __future__ import annotations

import os
import pytest

from try_or import try_or


class _TestBaseException(BaseException):
    """BaseException 直系で、デフォルトの exc=(Exception,) では捕捉されないことを検証するためのテスト用例外。"""
    pass


def test_returns_value_when_no_exception():
    assert try_or(lambda: 123, default=0) == 123


def test_returns_default_when_exception_with_default_exc():
    assert try_or(lambda: int("x"), default=0) == 0


def test_returns_default_when_specific_exc_tuple():
    assert try_or(lambda: int("x"), default=42, exc=(ValueError,)) == 42


def test_propagates_unlisted_exception():
    with pytest.raises(TypeError):
        try_or(lambda: 1 + "a", default=0, exc=(ValueError,))


def test_returns_default_when_value_is_none():
    assert try_or(lambda: None, default="fallback") == "fallback"


def test_identity_preserved_for_mutable_value():
    obj = []
    result = try_or(lambda: obj, default=["different"])
    assert result is obj  # 同一性保持


def test_identity_default_returned_when_value_is_none():
    default_obj = {}
    result = try_or(lambda: None, default=default_obj)
    assert result is default_obj  # default の同一性保持


def test_catches_exception_subclass_in_tuple():
    # LookupError は KeyError の基底なので捕捉される
    assert try_or(lambda: {}["missing"], default="d", exc=(LookupError,)) == "d"


def test_baseexception_like_is_not_caught_by_default():
    def raise_custom():
        raise _TestBaseException("boom")

    with pytest.raises(_TestBaseException):
        try_or(raise_custom, default=0)  # デフォルトの exc=(Exception,) では捕捉されない


def test_examples_in_readme_are_correct():
    # Fall back to default on Exception
    assert try_or(lambda: int("123"), default=0) == 123
    assert try_or(lambda: int("not-an-int"), default=0) == 0

    # Replace None to default（README 修正後を反映: import os 追加、余分な . を削除）
    assert try_or(lambda: os.environ.get("not-exist"), default="1") == "1"

    # Narrow which exceptions are caught
    assert try_or(lambda: int("x"), default=0, exc=(ValueError,)) == 0

    with pytest.raises(TypeError):
        try_or(lambda: (1 + "a"), default=0, exc=(ValueError,))

    assert try_or(lambda: (1 + "a"), default=0, exc=(ValueError, TypeError)) == 0
