from __future__ import annotations

from typing import Callable, TypeVar

__all__ = ["try_or"]

T = TypeVar("T")

def try_or(
    f: Callable[[], T | None],
    default: T,
    exc: type[BaseException] | tuple[type[BaseException], ...]=(Exception,)
) -> T:
    try:
        value = f()
    except exc:
        value = None
    return value if value is not None else default
