# List of authors from DOI

We can get a list of authors and their affiliations for any paper that is
published in an [AGU journal](https://agupubs.onlinelibrary.wiley.com/)
using the following code snippet. First, you need
to install ``lxml``, ``pandas``, and ``async_retriever`` libraries.

```python
from lxml import html
import pandas as pd
import async_retriever as ar

dois = [
    "10.1029/2018MS001603",
    "10.1029/2019MS001766",
    "10.1029/2018MS001583",
    "10.1029/2019MS001870",
]

base_url = "https://agupubs.onlinelibrary.wiley.com/doi/full"
urls = [f"{base_url}/{d}" for d in dois]
r = ar.retrieve(urls, "text")

def auth_xpath(n):
    return f'//*[@id="a{n}_Ctrl"]/span/text()'

def affi_xpath(n):
    return f'//*[@id="a{n}"]/p/text()'

for d, t in zip(dois, r):
    tree = html.fromstring(t)
    auth = [[tree.xpath(auth_xpath(n)), tree.xpath(affi_xpath(n))] for n in range(300)]
    auth = [(a[0], b[0] if len(b) ==1 else b[1]) for a , b in auth if len(a) == 1]
    auth_aff = pd.DataFrame(auth)
    auth_aff.to_csv(f"authors_{d.replace('/', '_')}.csv", index=False, header=False)
```

This snippet saves a list of authors and their affiliations to a ``csv`` file.
