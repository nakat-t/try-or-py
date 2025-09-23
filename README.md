# try-or

A Python micro-library that returns the first successful value (non-None) or a default.

## What it does

- Evaluate one or more supplier functions left-to-right.
- Return the first value that:
  - does not raise a listed exception (exc), and
  - is not None.
- If all suppliers either raise a listed exception or return None, return the default value.
- Exceptions not listed in exc are propagated.

## Examples

Fall back to default on `Exception`:

```python
from try_or import try_or

# Return the successful value when no exception is raised
try_or(lambda: int("123"), default=0)
# -> 123

# Fall back to the default when an exception occurs
try_or(lambda: int("not-an-int"), default=0)
# -> 0
```

Replace `None` with default:

```python
import os
from try_or import try_or

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
try_or(lambda: (1 + "a"), default=0, exc=(ValueError, TypeError))
# -> 0
```

Multiple suppliers (short-circuiting, lazy evaluation):

```python
import json
import os
from pathlib import Path
from try_or import try_or

config = try_or(
    # 1) Prefer env JSON
    lambda: json.loads(os.environ["APP_CONFIG_JSON"]),
    # 2) Then user config
    lambda: json.loads(Path("~/.myapp/config.json").expanduser().read_text(encoding="utf-8")),
    # 3) Then system config
    lambda: json.loads(Path("/etc/myapp/config.json").read_text(encoding="utf-8")),
    # Default if all above fail or return None
    default={"host": "localhost", "port": 8080},
)
# -> First successful non-None is returned. Later suppliers are not evaluated.
```

Empty suppliers:

```python
from try_or import try_or

try_or(default="fallback")
# -> "fallback"
```

## The code itself

```python
def try_or(
    *args: Callable[[], T | None],
    default: T,
    exc: type[BaseException] | tuple[type[BaseException], ...]=(Exception,)
) -> T:
    for f in args:
        try:
            value = f()
            if value is not None:
                return value
        except exc:
            pass
    return default
```

## License

[MIT License](./LICENSE)
