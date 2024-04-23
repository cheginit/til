# Frechet distance with Numba

The Frechet distance is a measure of similarity between two curves. It is defined as
the minimum length of a leash required to connect a dog and its owner as they walk
without backtracking along their respective curves. The leash is allowed to vary in
length, but it cannot be longer than necessary. One of its applications is in the
comparison of trajectories in GIS. Here's an efficient implementation of the Frechet
distance using `numba`.

```python
import numpy as np
from numba import njit, prange
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]


@njit("f8(f8[:, ::1], f8[:, ::1])", fastmath=True, parallel=True)
def frechet_distance(true_coords: FloatArray, pred_coords: FloatArray)-> float:
    """Compute the discrete Fréchet distance between two lines"""
    n, m = len(true_coords), len(pred_coords)
    # Compute pairwise euclidean distance
    p = 2
    dist = np.zeros((n, m))
    for i in prange(n):
        for j in prange(m):
            dist[i, j] = np.sum(np.abs(true_coords[i] - pred_coords[j]) ** p) ** (1.0 / p)

    cost = np.full((n, m), np.inf)
    cost[0, 0] = dist[0, 0]
    for i in range(1, n):
        cost[i, 0] = max(cost[i - 1, 0], dist[i, 0])
    for j in range(1, m):
        cost[0, j] = max(cost[0, j - 1], dist[0, j])
    for i in range(1, n):
        for j in range(1, m):
            cost[i, j] = max(min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1]), dist[i, j])
    return cost[-1, -1]
```
