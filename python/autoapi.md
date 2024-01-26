# Recursive AutoAPI for Sphinx

I was looking for automatic generation of API for several submodules when I
found out about this useful Sphinx extension called
[AutoAPI](https://github.com/readthedocs/sphinx-autoapi). Setting it up is pretty
straightforward. For example, here's how I setup my `docs/source/conf.py` file:

```python
extensions = [
    ...,
    "autoapi.extension",
    ...,
]

autoapi_dirs = [
    "../../pygeoogc",
    "../../pygeoutils",
    "../../pynhd",
    "../../pygeohydro",
    "../../py3dep",
    "../../pydaymet",
]

autoapi_ignore = [
    "**ipynb_checkpoints**",
    "**tests**",
    "**setup**",
    "**generate_pip**",
    "**conf**",
]

autoapi_options = [
    "members",
    "inherited-members",
    "undoc-members",
    # 'private-members',
    "show-inheritance",
    # 'show-module-summary',
    # 'special-members',
    # 'imported-members',
]
```

It's just as easy as that. You can check out the results
[here](https://hyriver.readthedocs.io/en/latest/autoapi/index.html)
