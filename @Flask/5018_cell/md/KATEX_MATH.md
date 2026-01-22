# KaTeX Math Expressions

## Overview
The spreadsheet application uses **KaTeX** (a fast, easy-to-use JavaScript library for TeX math rendering) to display mathematical expressions beautifully formatted. KaTeX is similar to Google's math rendering and supports LaTeX syntax.

## What is KaTeX?
KaTeX is a fast math typesetting library for the web. It renders LaTeX math notation into beautiful, readable mathematical expressions. It's used by Khan Academy, Wikipedia, and many other educational platforms.

## Basic Syntax

### Inline Math
Wrap your LaTeX expression with `\(` and `\)`:

```
\(expression\)
```

**Example:**
```
The formula is \(E = mc^2\)
```

**Renders as:** The formula is E = mc²

## Common Mathematical Expressions

### 1. Fractions
**Syntax:** `\(\frac{numerator}{denominator}\)`

**Examples:**
```
\(\frac{1}{2}\)          → ½
\(\frac{4c2}{8c2}\)      → 4c²/8c²
\(\frac{a+b}{c+d}\)      → (a+b)/(c+d)
\(\frac{x^2 + 1}{x - 1}\) → (x² + 1)/(x - 1)
```

### 2. Square Roots
**Syntax:** `\(\sqrt{value}\)`

**Examples:**
```
\(\sqrt{25}\)            → √25
\(\sqrt{x^2 + y^2}\)     → √(x² + y²)
\(\sqrt[3]{27}\)         → ³√27 (cube root)
\(\sqrt{\frac{a}{b}}\)   → √(a/b)
```

### 3. Exponents (Superscripts)
**Syntax:** `\(base^{exponent}\)`

**Examples:**
```
\(x^2\)                  → x²
\(2^{10}\)               → 2¹⁰
\(e^{i\pi}\)             → e^(iπ)
\(x^{2n+1}\)             → x^(2n+1)
```

### 4. Subscripts
**Syntax:** `\(base_{subscript}\)`

**Examples:**
```
\(x_1\)                  → x₁
\(a_{n+1}\)              → aₙ₊₁
\(H_2O\)                 → H₂O
```

### 5. Greek Letters
**Syntax:** `\(backslash + letter name\)`

**Examples:**
```
\(\alpha\)               → α (alpha)
\(\beta\)                → β (beta)
\(\gamma\)               → γ (gamma)
\(\Delta\)               → Δ (Delta - capital)
\(\pi\)                  → π (pi)
\(\theta\)               → θ (theta)
\(\sigma\)               → σ (sigma)
\(\omega\)               → ω (omega)
```

### 6. Mathematical Operators
**Examples:**
```
\(\times\)               → × (multiplication)
\(\div\)                 → ÷ (division)
\(\pm\)                  → ± (plus-minus)
\(\neq\)                 → ≠ (not equal)
\(\leq\)                 → ≤ (less than or equal)
\(\geq\)                 → ≥ (greater than or equal)
\(\approx\)              → ≈ (approximately)
\(\infty\)               → ∞ (infinity)
```

### 7. Summation and Products
**Examples:**
```
\(\sum_{i=1}^{n} i\)     → Σ from i=1 to n
\(\prod_{i=1}^{n} i\)    → Π from i=1 to n
\(\int_{0}^{1} x dx\)    → ∫ from 0 to 1
```

### 8. Complex Expressions
**Examples:**
```
\(\frac{-b \pm \sqrt{b^2 - 4ac}}{2a}\)
→ Quadratic formula

\(e^{i\pi} + 1 = 0\)
→ Euler's identity

\(\lim_{x \to \infty} \frac{1}{x} = 0\)
→ Limit notation

\(\binom{n}{k} = \frac{n!}{k!(n-k)!}\)
→ Binomial coefficient
```

## Quick Formatter Buttons (F3)

The Quick Formatter provides two convenient buttons for math:

### √ Button (Square Root)
- **Function:** Wraps selected text with `\(\sqrt{...}\)`
- **Usage:** Select a number or expression, press F3, click √
- **Example:** Select `25` → Click √ → `\(\sqrt{25}\)`

### a/b Button (Fraction)
- **Function:** Smart fraction converter
- **Features:**
  - Detects division patterns automatically
  - Converts `*` to `×` (times symbol)
  - Handles complex expressions with parentheses
  - Works with nested fractions

**Examples:**
```
Input: 4/8
Output: \(\frac{4}{8}\)

Input: a*b/c
Output: \(\frac{a \times b}{c}\)

Input: (a+b)/(c+d)
Output: \(\frac{a+b}{c+d}\)

Input: 5555/(1550+10)/150
Output: \(\frac{\frac{5555}{1550+10}}{150}\)
```

## Advanced Features

### Matrices
```
\(\begin{matrix}
a & b \\
c & d
\end{matrix}\)
```

### Cases (Piecewise Functions)
```
\(f(x) = \begin{cases}
x^2 & \text{if } x \geq 0 \\
-x & \text{if } x < 0
\end{cases}\)
```

### Aligned Equations
```
\(\begin{aligned}
x &= a + b \\
y &= c + d
\end{aligned}\)
```

## Common Use Cases

### 1. Chemistry
```
\(H_2O\)                 → Water
\(CO_2\)                 → Carbon dioxide
\(C_6H_{12}O_6\)         → Glucose
```

### 2. Physics
```
\(F = ma\)               → Newton's second law
\(E = mc^2\)             → Einstein's mass-energy
\(v = \frac{d}{t}\)      → Velocity formula
```

### 3. Statistics
```
\(\mu = \frac{\sum x}{n}\)           → Mean
\(\sigma = \sqrt{\frac{\sum(x-\mu)^2}{n}\)  → Standard deviation
```

### 4. Algebra
```
\(ax^2 + bx + c = 0\)    → Quadratic equation
\((a+b)^2 = a^2 + 2ab + b^2\)  → Binomial expansion
```

## Tips and Best Practices

### 1. Always Use Delimiters
- ✅ Correct: `\(x^2\)`
- ❌ Wrong: `x^2` (won't render)

### 2. Use Curly Braces for Multi-Character Exponents
- ✅ Correct: `\(x^{10}\)` → x¹⁰
- ❌ Wrong: `\(x^10\)` → x¹0 (only first character is superscript)

### 3. Escape Special Characters
- Use `\{` and `\}` for literal braces
- Use `\_` for literal underscore

### 4. Test Complex Expressions
- Start simple and build up
- Use parentheses to group terms
- Check rendering in preview mode

## Implementation Details

### How It Works
1. **Detection:** The regex `/\\\((.*?)\\\)/g` finds all `\(...\)` patterns
2. **Rendering:** KaTeX library converts LaTeX to HTML/CSS
3. **Display:** Rendered math appears inline with text
4. **Fallback:** If KaTeX fails, original text is shown

### Files Involved
- **templates/index.html** - Loads KaTeX CSS and JS from CDN
- **static/script.js** - Parses and renders math expressions (regex: `/\\\((.*?)\\\)/g`)
- **export_static.py** - Includes KaTeX in static exports with special handling:
  - Regex: `/\\\((.*?)\\\)/g` (with proper Python string escaping)
  - Removes newlines from KaTeX output to prevent `<br>` tag insertion
  - Adds integrity hashes for security

### CDN Version
- **KaTeX v0.16.9** from jsdelivr CDN
- Includes integrity hash for security (SHA-384)
- Loaded synchronously to ensure availability during parsing

### Performance
- KaTeX is extremely fast (faster than MathJax)
- Renders math synchronously
- No page reflow or flashing
- SVG-based rendering for crisp display at any size

## Troubleshooting

### Math Not Rendering?
1. Check delimiters: Must be `\(` and `\)` (backslash + parenthesis)
2. Verify syntax: Use valid LaTeX commands
3. Check browser console for errors
4. Ensure KaTeX CDN is loaded (check network tab)

### Common Errors
- **Missing closing delimiter:** `\(x^2` → Add `\)`
- **Invalid LaTeX:** `\(x^^2\)` → Use `\(x^2\)` or `\(x^{2}\)`
- **Unescaped characters:** Use `\\` for backslash in strings

### Static Export Issues (Fixed)
**Issue:** Square root and other complex symbols showed only the content (e.g., just "3" instead of √3)

**Cause:** KaTeX generates SVG with newlines in the path data. The export script was converting these newlines to `<br>` tags, breaking the SVG syntax.

**Solution:** The export script now removes newlines from KaTeX output before processing, preventing `<br>` tag insertion into SVG paths.

**Status:** ✅ Fixed - All KaTeX expressions now render correctly in static HTML exports

## Resources

### Learn More LaTeX
- [KaTeX Documentation](https://katex.org/docs/supported.html)
- [LaTeX Math Symbols](https://www.overleaf.com/learn/latex/List_of_Greek_letters_and_math_symbols)
- [KaTeX Function Support](https://katex.org/docs/support_table.html)

### Quick Reference
- **Fractions:** `\frac{a}{b}`
- **Square Root:** `\sqrt{x}`
- **Exponent:** `x^{n}`
- **Subscript:** `x_{n}`
- **Greek:** `\alpha`, `\beta`, `\gamma`, etc.
- **Operators:** `\times`, `\div`, `\pm`, `\neq`

## Examples in Context

### Math Quiz
```
Question: Solve \(\frac{4c^2}{8c^2}\)
Answer: \(\frac{1}{2}\)
```

### Science Notes
```
Newton's Law: \(F = ma\)
Where:
- \(F\) = Force
- \(m\) = Mass
- \(a\) = Acceleration
```

### Statistics Table
```
Mean: \(\mu = \frac{\sum x}{n}\)
Variance: \(\sigma^2 = \frac{\sum(x-\mu)^2}{n}\)
Standard Deviation: \(\sigma = \sqrt{\sigma^2}\)
```

---

**Note:** KaTeX works in both the live application and static HTML exports, making your mathematical content portable and shareable!
