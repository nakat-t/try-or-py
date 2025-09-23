# try-or

A Python micro-library that returns try value or default.

## Example

Fall back to default on `Exception`:

```python
from try_or import try_or

# Return the computed value when no exception is raised
try_or(lambda: int("123"), default=0)
# -> 123

# Fall back to the default when an exception occurs
try_or(lambda: int("not-an-int"), default=0)
# -> 0
```

Replace `None` to default:

```python
from try_or import try_or
import os

# Return the default when the result is None
try_or(lambda: os.environ.get("not-exist"), default="1")
# -> "1"
```

Narrow which exceptions are caught:

```python
from try_or import try_or

# Only fall back on ValueError
try_or(lambda: int("x"), default=0, exc=(ValueError,))
# -> 0

# TypeError will be propagated
try_or(lambda: (1 + "a"), default=0, exc=(ValueError,))
# -> raises TypeError

# Fall back on ValueError or TypeError
try_or(lambda: (1 + "a"), default=0, exc=(ValueError,TypeError))
# -> 0
```

## Signature

This is literally the entire code.

```python
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
```

## License

MIT License
