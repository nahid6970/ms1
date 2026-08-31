# Cyber Patcher Protocol (v5.0) - RANGE SUPPORT

I am using a local automated patcher. To optimize for large file modifications, please follow these rules:

---

## 🚀 Option A: RANGE PATCHING (Best for Large Blocks)
Use this if you are deleting or replacing a large section of code. You only need to provide the "Anchor" lines for the start and end.

```text
FILE: <relative_path>
RANGE START: <exact_first_line_of_block>
RANGE END: <exact_last_line_of_block>
REPLACE WITH:
<new_code_or_leave_empty_to_delete>
--- END RANGE ---
```

---

## 🎯 Option B: SEARCH/REPLACE (Best for Small Edits)
Use this for targeted single-line or small multi-line changes.

```text
FILE: <relative_path>
<<<<<<< SEARCH
<original_code>
=======
<updated_code>
>>>>>>> REPLACE
```

---

## Important Rules:
1.  **Anchors**: Ensure the `RANGE START` and `RANGE END` lines are unique enough to be found.
2.  **Single Block**: Provide all changes in **One Single Markdown Code Block**.
3.  **Clean Code**: Do not include conversational text inside the code block.

Please confirm you understand how to use the **RANGE** format for large deletions.
