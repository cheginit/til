# A round-robin scheduler implementation

I stumbled upon this interesting implementation of
[round-roubin scheduler](https://en.wikipedia.org/wiki/Round-robin_scheduling)
in [Python's documentation](https://docs.python.org/3/library/collections.html#collections.deque):

> A round-robin scheduler can be implemented with input iterators stored in a deque.
> Values are yielded from the active iterator in position zero. If that iterator is
> exhausted, it can be removed with popleft(); otherwise, it can be cycled back to
> the end with the rotate() method:

```python
from collections import deque


def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    iterators = deque(map(iter, iterables))
    while iterators:
        try:
            while True:
                yield next(iterators[0])
                iterators.rotate(-1)
        except StopIteration:
            # Remove an exhausted iterator.
            iterators.popleft()
```
