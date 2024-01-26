# General function for running functions asynchronously

We use the this following snippet for running any function
asynchronously:

```python
import asyncio
import nest_asyncio
import functools
import contextvars
from typing import Callable, Any, TypeVar

T = TypeVar("T")


async def run_in_threadpool(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Mock Sync function for Async call.Any
    Code from https://github.com/encode/starlette/blob/master/starlette/concurrency.py
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    nest_asyncio.apply(loop)
    asyncio.set_event_loop(loop)
    # Ensure we run in the same context
    child = functools.partial(func, *args, **kwargs)
    context = contextvars.copy_context()
    func = context.run
    args = (child,)
    return await loop.run_in_executor(None, func, *args)
```
