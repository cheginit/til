# Adding breakpoints for debugging

Python 3.7+ provides a convenient way for adding breakpoints without importing `pdb` explicitly.
You can just add `breakpoint()`, a Python built-in function, and it automatically drops you to
debug mode. Under the hood, it calls `sys.breakpointhook()`.
You can more information
[here](https://docs.python.org/3/library/functions.html#breakpoint).
