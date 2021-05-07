# Interacting with system's clipboard

You can access your system's clipboard using `tkinter` library.

```python
import tkinter as tk

root = tk.Tk()
root.withdraw()
```

Now you can have access to your systems clipboard. Just copy some text to your
clipboard then you can retrieve it like so:

```python
txt = root.clipboard_get()
```

After you're done with the process, you should close the access as follows:

```python
root.destroy()
```

This only works for Linux-based systems, if you MacOS or Windows you have to use
another approach. You can find more info
[here](https://github.com/mattvonrocketstein/smash/blob/master/smashlib/ipy3x/lib/clipboard.py).
