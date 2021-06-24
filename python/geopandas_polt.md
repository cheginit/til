# Polygon legend in GeoPandas Plot

Out of the box, GeoPandas cannot handle legends for polygons. Here's one way to
workaround this issue:

```python
from matplotlib.patches import Patch

ax = line_gdf.plot()

style = {"facecolor": "skyblue", "edgecolor": "none", "label": "Polygon"}
poly_gdf.plot(ax=ax, **style)

poly_handle = Patch(**style)
handles, _ = ax.get_legend_handles_labels()
ax.legend(handles=[*handles, poly_handle])
```
