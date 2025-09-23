from __future__ import annotations

from typing import Callable, TypeVar

__all__ = ["try_or"]

T = TypeVar("T")

def try_or(
    *args: Callable[[], T | None],
    default: T,
    exc: type[BaseException] | tuple[type[BaseException], ...] = (Exception,)
) -> T:
    for f in args:
        try:
            value = f()
            if value is not None:
                return value
        except exc:
            pass
    return default
