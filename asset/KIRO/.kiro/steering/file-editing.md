# File Editing Method

When editing files that may have Windows line endings (CRLF) or Unicode characters (e.g. box-drawing chars like ──),
the `strReplace` tool will fail to match. Use a Python script instead:

```python
path = 'path/to/file.py'
data = open(path, 'rb').read().decode('utf-8')
data = data.replace('old string', 'new string')
open(path, 'wb').write(data.encode('utf-8'))
```

Run via the `shell` tool with `python3 -c "..."`.
Split large edits into multiple shell calls rather than one large script.
