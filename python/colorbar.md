# `colorbar` in `matplotlib` done right

Let's see how we can add a colorbar to a plot that respects the plot scale. First, let's get
Environmental Performance Index from EPI's website and then plot it:

```python
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

epi = pd.read_csv("https://epi.yale.edu/downloads/epi2020results20200604.csv")
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
world_epi = world.merge(epi[["iso", "EPI.new"]], left_on="iso_a3", right_on="iso")
world_epi = world_epi.rename(columns={"EPI.new": "Environmental Performance Index"})

column = "Environmental Performance Index"
norm = plt.Normalize(vmin=world_epi[column].min(), vmax=world_epi[column].min())
ax = world_epi.plot(column=column, figsize=(15, 10))
ax.axis(False)
```

Now, we can add the colorbar as follow:

```python
fig = ax.figure
fig.set_dpi(300)
cax = fig.add_axes(
    [
        ax.get_position().x1 + 0.01,
        ax.get_position().y0,
        0.02,
        ax.get_position().height,
    ]
)
sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
fig.colorbar(sm, cax=cax, label=column)
```
