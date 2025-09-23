from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from try_or import try_or


# Set of exception classes used for generation (mutually unrelated representative examples)
EXC_CLASSES = (ValueError, TypeError, KeyError, OSError, RuntimeError)


def values_strategy() -> st.SearchStrategy:
    """None を含まない多様な値の戦略（可変/不変を混在）。"""
    return st.one_of(
        st.integers(),
        st.text(max_size=20),
        st.booleans(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.lists(st.integers(), max_size=5),
        st.dictionaries(st.text(max_size=10), st.integers(), max_size=5),
        st.tuples(st.integers(), st.integers()),
        st.binary(max_size=16),
    )


def allowed_exc_strategy() -> st.SearchStrategy:
    """try_or の exc 引数用（例外クラス or 例外クラスのタプル）。"""
    single = st.sampled_from((Exception,) + EXC_CLASSES)
    tuples = st.lists(single, min_size=1, max_size=3, unique=True).map(tuple)
    return st.one_of(single, tuples)


@given(value=values_strategy(), default=values_strategy(), exc=allowed_exc_strategy())
def test_passthrough_non_none_values_property(value, default, exc):
    # If f returns a non-None value, that value (the same object) is always returned regardless of default and exc
    result = try_or(lambda: value, default=default, exc=exc)
    assert result is value


@given(default=values_strategy(), exc=allowed_exc_strategy())
def test_none_is_replaced_by_default_property(default, exc):
    # If f returns None, default is always returned (as the identical object)
    result = try_or(lambda: None, default=default, exc=exc)
    assert result is default


@given(exc_cls=st.sampled_from(EXC_CLASSES), default=values_strategy())
def test_listed_exceptions_fallback_property(exc_cls, default):
    # If an exception listed in exc occurs, fallback to default
    def raise_exc():
        raise exc_cls("boom")

    result = try_or(raise_exc, default=default, exc=(exc_cls,))
    assert result is default


@given(
    exc_pair=st.tuples(st.sampled_from(EXC_CLASSES), st.sampled_from(EXC_CLASSES)).filter(
        lambda ab: ab[0] is not ab[1]
    ),
    default=values_strategy(),
)
def test_unlisted_exceptions_propagate_property(exc_pair, default):
    # Exceptions not included in exc are always propagated
    exc_cls, listed_cls = exc_pair

    def raise_exc():
        raise exc_cls("boom")

    with pytest.raises(exc_cls):
        try_or(raise_exc, default=default, exc=(listed_cls,))
