# Annotate bar plots

We can annotate a bar plot with their values as follows:

```python
import pandas as pd
import numpy as np

df = pd.DataFrame(
    np.random.randint(100, size=(10, 1)), index=np.random.randint(1e7, 1e8, size=(10,))
)

ax = df.plot.bar(legend=False)
yshift = ax.get_ylim()[1] * 0.025
for p in ax.patches:
    ax.annotate(
        p.get_height(),
        (p.get_x() + p.get_width() / 2, p.get_height() + yshift),
        ha="center",
        va="center",
    )
```
