# Timing a Function

As an alternative to `timeit`, we can use
[`profilehooks`](https://github.com/mgedmin/profilehooks) library to check runtime
of a function. For example, let's compare performace of `cytoolz` for flattening a nested list
with a simple list comprehension, for a single run.

```python
from profilehooks import timecall
import cytoolz as tlz
import time

nl = [[1, "2", "3"], [4, 5]] * 20_000_000

@timecall(immediate=True, timer=time.perf_counter)
def conc_tlz(nested_list):
    return list(tlz.concat(nested_list))

_ = conc_tlz(nl)

@timecall(immediate=True, timer=time.perf_counter)
def conc_lc(nested_list):
    return [x for y in nested_list for x in y]

_ = conc_lc(nl)
```
