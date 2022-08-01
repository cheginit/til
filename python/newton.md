# Implementing Newton-Raphson algorithm with Numba

SciPy has a function called [`optimize.newton`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.newton.html)
that is an implementation of the Newton-Raphson root finding algorithm. If we pass
both `fprime` and `fprime2` arguments (first and second derivatives) it uses
Halley's method. Here we implement a more efficient but less general version of this
code using [Numba](https://numba.pydata.org/) and compare its performance with SciPy.
We find the root of $f(\theta) = \theta - \sin (\theta) - 2 A / r^2$.

```python
import functools
from typing import Tuple

import numpy as np
from numba import njit

ngjit = functools.partial(njit, cache=True, nogil=True)

@ngjit("b1(f8, f8, f8, f8)")
def within_tol(x: float, y: float, atol: float, rtol: float) -> bool:
    """Check if two float numbers are within a tolerance."""
    return bool(np.abs(x - y) <= atol + rtol * np.abs(y))


@ngjit("f8(f8, UniTuple(f8, 2))")
def func_main(theta: float, args: Tuple[float, float]) -> float:
    """The main function to find the root of."""
    area, rad = args
    return theta - np.sin(theta) - 2 * area / rad ** 2


@ngjit("f8(f8)")
def func_der1(theta: float) -> float:
    """The first derivative of the main function."""
    return 1.0 - np.cos(theta)


@ngjit("f8(f8)")
def func_der2(theta: float) -> float:
    """The second derivative of the main function."""
    return np.sin(theta)


@ngjit("f8(f8, UniTuple(f8, 2))")
def halley_solver(x0: float, args: Tuple[float, float]) -> float:
    """Find root of ``func_main`` using Halley's method."""
    p0 = np.float64(x0)
    tol = 1.48e-8
    for _ in range(50):
        fval = func_main(p0, args)
        if within_tol(fval, 0.0, tol, 0.0):
            return p0

        fder = func_der1(p0)
        if within_tol(fder, 0.0, tol, 0.0):
            return float(np.inf)
        newton_step = fval / fder

        # Since second derivative is available we can modify
        # the Newton-Raphson step based on Halley's method.
        fder2 = func_der2(p0)
        adj = 0.5 * newton_step * fder2 / fder

        if np.abs(adj) < 1:
            newton_step /= 1.0 - adj

        p0 -= newton_step
    return np.inf
```

The root of this function for $A=0.91$ and $r=2$ is approximately 1.45. We intentionally
give a far off initial guess for a better comparison.

```python
%timeit halley_solver(10000, (0.91, 2))

1.44 µs ± 1.45 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)
```

Now, let's use `optimize.newton`:

```python
from scipy import optimize

def der1(theta: float, _) -> float:
    """The first derivative of the main function."""
    return 1.0 - np.cos(theta)

def der2(theta: float, _) -> float:
    """The second derivative of the main function."""
    return np.sin(theta)

%timeit optimize.newton(func_main, 10000, fprime=der1, args=((0.91, 2),), fprime2=der2)

1.12 ms ± 43.4 µs per loop (mean ± std. dev. of 7 runs, 1,000 loops each)
```

The Numba version has almost x1000 performance improvement. Although, writing a general
version with Numba is not very straight forward, but the code can be easily adjusted
for any equation.
