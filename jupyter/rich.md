# Rich extension

The `rich` library has an IPython extension that prettifies
cell outputs in Jupyter Notebooks. You can add this line
to your IPython profile to enable this extension by default
for all notebooks:

```python
try:
    import rich
    c.InteractiveShellApp.extensions.append('rich')
except ImportError:
    pass
```


The default location for the profile is
`~/.ipython/profile_default/ipython_config.py`

