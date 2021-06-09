# Function progress with Rich

We can use `rich` and `timeit` to create a visually appealing decorator for
tracking a function's progress:

```python
from rich.live import Live
import functools
from timeit import default_timer as timer
import datetime

def live_display(console, current, total, msg):
    def decorator_live_display(func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            with Live(console=console, screen=False, auto_refresh=False) as live:
                live.update(f"({current}/{total}) {msg} ...", refresh=True)
                start = timer()
                value = func(*args, **kwargs)
                end = timer()
                elapsed = datetime.timedelta(seconds=end - start)
                live.update(
                    f"({current}/{total}) {msg} [:heavy_check_mark:] ({elapsed})",
                    refresh=True,
                )
            return value

        return wrapper_decorator

    return decorator_live_display
```

Then we can decorate a function like so:

```python
from rich.console import Console
from time import sleep

console = Console()

@live_display(console, 1, 7, "Doing a fancy job!")
sleeping_beauty(t):
    sleep(t)
    return t

_ = sleeping_beauty(5)
```
