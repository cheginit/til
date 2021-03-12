# Customizing logging configuration

Although we can use `logging.basicConfig` to customize a logger, doing so will affect all
the loggers that are loaded during runtime. So it's best to adjust the configurations
locally. So, instead of doing:

```python
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="")
```

we can use:

```python
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(""))
logger.handlers = [handler]
```
