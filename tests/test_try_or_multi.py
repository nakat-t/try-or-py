from __future__ import annotations

import pytest

from try_or import try_or


def test_short_circuit_on_first_success():
    calls = {"f1": 0, "f2": 0}

    def f1():
        calls["f1"] += 1
        return 123

    def f2():
        calls["f2"] += 1
        raise AssertionError("should not be evaluated when first succeeds")

    result = try_or(f1, f2, default=0)
    assert result == 123
    assert calls["f1"] == 1
    assert calls["f2"] == 0  # 後続は未評価


def test_second_used_after_allowed_exception():
    calls = {"f1": 0, "f2": 0}

    def f1():
        calls["f1"] += 1
        raise ValueError("boom")

    def f2():
        calls["f2"] += 1
        return 42

    result = try_or(f1, f2, default=0, exc=(ValueError,))
    assert result == 42
    assert calls["f1"] == 1
    assert calls["f2"] == 1


def test_second_used_after_none():
    calls = {"f1": 0, "f2": 0}

    def f1():
        calls["f1"] += 1
        return None

    def f2():
        calls["f2"] += 1
        return "x"

    result = try_or(f1, f2, default="d")
    assert result == "x"
    assert calls["f1"] == 1
    assert calls["f2"] == 1


def test_unlisted_exception_propagates_even_with_later_suppliers():
    calls = {"f1": 0, "f2": 0}

    def f1():
        calls["f1"] += 1
        raise TypeError("unexpected")

    def f2():
        calls["f2"] += 1
        return "ok"

    with pytest.raises(TypeError):
        try_or(f1, f2, default="d", exc=(ValueError,))

    # f2 is not called (f1 propagates immediately due to an uncaught exception)
    assert calls["f1"] == 1
    assert calls["f2"] == 0


def test_all_fail_returns_default_identity():
    default_obj = object()

    def f1():
        raise ValueError("boom")

    def f2():
        return None

    result = try_or(f1, f2, default=default_obj, exc=(ValueError,))
    assert result is default_obj  # default identity is preserved


def test_empty_suppliers_returns_default():
    assert try_or(default="fallback") == "fallback"


def test_exc_subclass_caught_in_any_stage():
    def f1():
        # KeyError は LookupError のサブクラス
        raise KeyError("missing")

    def f2():
        return "ok"

    result = try_or(f1, f2, default="d", exc=(LookupError,))
    assert result == "ok"


def test_identity_preserved_for_first_success_in_multi():
    obj = []

    def f1():
        return obj

    def f2():
        raise AssertionError("should not be called")

    result = try_or(f1, f2, default=["different"])
    assert result is obj  # identity preserved
