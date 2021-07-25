# Split a URL

In some cases, we want to separate base URL and payload from
a URL request, we can achieve this via Python's built-in functions:

```python
import urllib.parse as parse
from typing import Tuple, Dict

def extract_paylod(url: str)-> Tuple[str, Dict[str, str]]:
    _url = parse.urlsplit(parse.unquote(url))

    payload = dict(s.split("=") for s in _url.query.split("&"))
    base_url = parse.urlunsplit(_url._replace(query=""))
    return base_url, payload

```
