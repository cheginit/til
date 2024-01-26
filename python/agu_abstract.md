# Extracting Abstracts For an AGU Session

We can extract titles and requested presentation formats from the AGU web page
for a session as follows:

```python
import requests
from lxml import html

url = "https://agu.confex.com/agu/fm21/h/sessions/viewsession.cgi"
params = {
    "RecordType": "Session",
    "Recordid": "125520",
    "Field0Name": "password",
    "Field0Value": "*cookie",
    "Hash": "0fb450efc41f35c181addb926543f8d8",
}
r = requests.get(url, params=params)

root = html.fromstring(r.text)

xpath = '//div/div/b[contains(text(),"Requested Presentation Format")]/parent::*/text()'
formats = [x.strip() for x in root.xpath(xpath)]

xpath = '//div/div/b[contains(text(),"Abstract ID#")]/parent::*/text()'
titles = [x.strip() for x in root.xpath(xpath)]

abstracts = pd.DataFrame({"Titles": titles, "Format": formats})
```
