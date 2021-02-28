# Parsing XMLs in Python safely

Suppose we want to find values of a specific field from a `xml` webpage. For example,
let's extract units of some of the attributes that are available in [this](https://www.sciencebase.gov/catalog/item/5669a79ee4b08895842a1d47)
from ScienceBase. Here's how we can achieve this using [defusedxml](https://github.com/tiran/defusedxml)
and [PyGeoOGC](https://github.com/cheginit/pygeoogc) safely:

```python

import pygeoogc as ogc
import defusedxml.cElementTree as ET
import pandas as pd

# A list of urls and payloads of the tagret XMLs
urls = [
    ('https://www.sciencebase.gov/catalog/file/get/57867b1be4b0e02680c14ff6',
    {'f': '__disk__e9/8b/ec/e98becc07c2de2b27396f1baefb29fa233b8f0f7'}),
    ('https://www.sciencebase.gov/catalog/file/get/5785595ce4b0e02680bf2fd8',
    {'f': '__disk__e7/8b/7d/e78b7dbf4c31e60de6696697e62c04ee688a56d3'}),
    ('https://www.sciencebase.gov/catalog/file/get/57dafd3ae4b090824ffc32f1',
    {'f': '__disk__9b/e6/04/9be604f55425b2691158260123a914cd0efae0da'}),
    ('https://www.sciencebase.gov/catalog/file/get/573b5344e4b0dae0d5e3ad9c',
    {'f': '__disk__9f/5c/50/9f5c50b2f0da613b0969c574716d13b67903e274'}),
    ('https://www.sciencebase.gov/catalog/file/get/57ffb392e4b0824b2d16f4c6',
    {'f': '__disk__dc/e8/d6/dce8d6f3b41e9ec33f9364a352e5e73055cfdc92'})
]

# Async retrieval
xmls = ogc.async_requests(urls, "text", max_workers=len(urls))

# Parsing the results and converting to a Pandas dataframe
units = []
for xml in xmls:
    root = ET.fromstring(xml)
    for item in root.findall('./eainfo/detailed/attr'):
        for v in item.find("attrdomv"):
            if v.tag == "rdom":
                for u in v.findall("attrunit"):
                    units.append((item.find("attrlabl").text, u.text.lower()))
units = pd.DataFrame(units, columns=["attr", "unit"])
```

The first five rows of the obtained dataframe is show below:
|    | attr      | unit    |
|---:|:----------|:--------|
|  0 | CAT_HLR_1 | percent |
|  1 | CAT_HLR_2 | percent |
|  2 | CAT_HLR_3 | percent |
|  3 | CAT_HLR_4 | percent |
|  4 | CAT_HLR_5 | percent |
