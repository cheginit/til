# Check for Jupyter Kernel

Sometimes we need to check if a code being run within a Jupyter kernel,
not iPython terminal. This function works well for these instances:

```python
def is_jupyter_kernel():
    """Check if the code is running in a Jupyter kernel (not IPython terminal)."""
    try:
        from IPython import get_ipython

        ipython = get_ipython()
    except (ImportError, NameError):
        return False
    if ipython is None:
        return False
    return "Terminal" not in ipython.__class__.__name__
```

