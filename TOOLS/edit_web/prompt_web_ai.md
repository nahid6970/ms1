# Cyber Patcher Protocol (v3.1) - Markdown Optimized

I am using a local automated patcher. To make copying easier, please follow these rules:

## The Markdown Rule
1.  **SINGLE CODE BLOCK**: Wrap ALL code changes for ALL files in **one single** markdown code block.
2.  Do not split changes into multiple blocks.
3.  Place the `FILE:` headers inside that single block.

## Format (Example)
Update my project using this exact structure:

```text
FILE: scripts/app.py
<<<<<<< SEARCH
old_logic()
=======
new_logic()
>>>>>>> REPLACE

FILE: styles/theme.css
<<<<<<< SEARCH
background: red;
=======
background: black;
>>>>>>> REPLACE
```

## Protocol Selection
You can use `SEARCH/REPLACE` for precision or `--- FILE: path --- DELETE/ADD` for simple changes, as long as it is all inside **one** markdown block.

Please confirm you will use the **Single Block Markdown** format for all future updates.
