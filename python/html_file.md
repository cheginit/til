# Extract links from a web page

We can find links of some file with a specific from a web page using
`regex` and `requests`. For example, let's find all `.xlsx` files from
the National Inventory of Dams:

```python
import re
import requests

base_url = "https://nid.sec.usace.army.mil/ords"
payload = {"p": "105:19:2471489473329::NO:::"}
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cookie": "ORA_WWV_APP_105=ORA_WWV-8Qgo2VSIyLWBcP6QrHFhMvQf",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
}
page = requests.get(f"{base_url}/f", params=payload, headers=headers)
xlsx = [t.rsplit(";", 1)[1] for t in re.findall('href="(.*xlsx)"', page.text)]
```
