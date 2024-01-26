# Parallel with Dask and Joblib

We can run a function parallel using `dask`, `joblib`, and `cytoolz` as follows:

```python
from dask.distributed import Client, LocalCluster
import joblib
import cytoolz as tlz

cluster = LocalCluster(processes=False, threads_per_worker=None)
client = Client(cluster)


def func(args):
    return do_somthing_with_args


per_proc = 5
args_list = [args1, args2, ...]

with joblib.parallel_backend("dask"):
    results = joblib.Parallel(verbose=1)(
        joblib.delayed(func)(args) for args in tlz.partition_all(per_proc, args_list)
    )
```

where `per_proc` is the number of arguments per process. Therefore, in this example,
each process runs `func([args1, args2, args3, args4, args5])`. Alternatively, you can
use `*` to expand the list like so:

```python
def func(arg1, arg2, arg3, arg4, arg5):
    return do_somthing_with_args


with joblib.parallel_backend("dask"):
    results = joblib.Parallel(verbose=1)(
        joblib.delayed(func)(*args) for args in tlz.partition_all(per_proc, args_list)
    )
```

Also, we could have directly used `Client()` with `joblib` like so:

```python
with Client(), joblib.parallel_backend("dask"):
    results = joblib.Parallel(verbose=1)(
        joblib.delayed(func)(args) for args in tlz.partition_all(per_proc, args_list)
    )
```

The difference is that the latter approach spawns a new schedueler every time
the code reaches this line of code whereas the former creates only one schedueler. The
former approach is useful for cases where you have several such parallel runs in your code.
