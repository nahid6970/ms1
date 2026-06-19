# CODE MERGE FORMAT GUIDE

When I provide code files below, return ALL modifications using ONLY this exact format.
Do NOT write prose explanations outside of comments inside the code blocks.

---

## RESPONSE FORMAT RULES

1. Each changed file starts with `@@FILE:` followed by the relative path.
2. Use `@@MODE: replace_block` to replace a specific block of code.
3. Use `@@MODE: replace_file` to replace the entire file content.
4. Use `@@MODE: insert_after` to insert code after a specific line.
5. Use `@@MODE: delete_block` to delete a block of code.
6. Every change ends with `@@END`.
7. If NO changes needed for a file, omit it entirely.

---

## FORMAT TEMPLATES

### Replace a block (most common):
```
@@FILE: path/to/file.py
@@MODE: replace_block
@@FROM:
exact original code here
(must match exactly, including indentation)
@@TO:
new replacement code here
@@END
```

### Replace entire file:
```
@@FILE: path/to/file.py
@@MODE: replace_file
@@TO:
full new file content here
@@END
```

### Insert after a specific line:
```
@@FILE: path/to/file.py
@@MODE: insert_after
@@AFTER:
the exact line to insert after
@@INSERT:
new lines to insert here
@@END
```

### Delete a block:
```
@@FILE: path/to/file.py
@@MODE: delete_block
@@FROM:
exact block to delete
@@END
```

---

## IMPORTANT RULES FOR AI

- The `@@FROM:` block MUST be an exact copy of the original code (same spacing, indentation, line breaks).
- Do NOT add line numbers.
- Do NOT use markdown code fences (``` ``` ```) inside the change blocks.
- You MAY include multiple `@@FILE:` blocks in one response.
- If a file is new (doesn't exist yet), use `@@MODE: replace_file`.

---

## EXAMPLE

User has this in `utils.py`:
```python
def greet(name):
    print("hello " + name)
```

Correct AI response:
```
@@FILE: utils.py
@@MODE: replace_block
@@FROM:
def greet(name):
    print("hello " + name)
@@TO:
def greet(name: str) -> None:
    """Greet the user by name."""
    print(f"Hello, {name}!")
@@END
```

---

## NOW, HERE ARE MY FILES:

<!-- The tool will append your file contents below this line -->
