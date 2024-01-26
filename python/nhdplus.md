# Networkx graph from NHDPlus

We can create a `networkx`'s graph from NHDPlus V2.1 dataset using
[this](https://www.sciencebase.gov/catalog/item/60c92503d34e86b9389df1c9)
item from ScienceBase as follows:

```python
import pandas as pd
import networkx as nx

df = pd.read_csv(
    "https://www.sciencebase.gov/catalog/file/get/60c92503d34e86b9389df1c9?f=__disk__4a%2Ff7%2F3e%2F4af73ee0ec6d2be1221e3dde541c6fe3c195e1bf"
)
G = nx.from_pandas_edgelist(
    df, source="comid", target="tocomid", edge_attr=True, create_using=nx.DiGraph
)
```
