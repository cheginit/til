# Check if `None`

Using `if x: statement` to check if `x` is `None` might have unintended consequences.

```python
x = ''
if x:
    print("Without is")

if x is not None:
    print("With is")
```

The first if-block won't print anything but the second will work as expected. We get
similar result with `x = 0`.
