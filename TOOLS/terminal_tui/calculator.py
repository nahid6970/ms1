# calculator.py - Simple scientific calculator similar to Casio fx-991ES
"""
A lightweight command‑line scientific calculator.
Features:
- Basic arithmetic: +, -, *, /, **, %
- Parentheses for grouping
- Functions from the Python `math` module: sin, cos, tan, asin, acos, atan,
  log (natural), log10, sqrt, factorial, degrees, radians, etc.
- Constants: pi, e
- REPL loop with `exit` or `quit` to leave.

Usage:
    python calculator.py
Enter an expression and press Enter to see the result.
"""

import math
import sys

# Allowed names for eval – map function names to math module objects
ALLOWED_NAMES = {
    name: getattr(math, name)
    for name in [
        "acos", "asin", "atan", "atan2", "ceil", "cos", "cosh", "degrees",
        "exp", "fabs", "factorial", "floor", "fmod", "frexp", "hypot",
        "ldexp", "log", "log10", "modf", "pow", "radians", "sin", "sinh",
        "sqrt", "tan", "tanh",
    ]
}
# Add constants
ALLOWED_NAMES.update({"pi": math.pi, "e": math.e})

def safe_eval(expr: str):
    """Evaluate *expr* safely using only the names defined in ALLOWED_NAMES.
    The built‑in `eval` is used with an empty globals dict and a locals dict
    containing only the permitted functions/constants.
    """
    # Replace the caret operator ^ (common in calculators) with ** for exponentiation
    expr = expr.replace('^', '**')
    try:
        return eval(expr, {"__builtins__": {}}, ALLOWED_NAMES)
    except Exception as e:
        return f"Error: {e}"

def repl():
    print("Scientific Calculator (type 'exit' or 'quit' to stop)")
    while True:
        try:
            line = input('>>> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nExiting.')
            break
        if line.lower() in ('exit', 'quit'):
            print('Goodbye!')
            break
        if not line:
            continue
        result = safe_eval(line)
        print(result)

if __name__ == "__main__":
    repl()
