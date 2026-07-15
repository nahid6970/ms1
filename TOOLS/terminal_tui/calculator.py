#!/usr/bin/env python3
import sys

def print_help():
    print("Simple calculator. Usage:")
    print("  python calculator.py <expression>")
    print("  python calculator.py            # interactive mode")
    print("Enter a mathematical expression to evaluate. Supports +, -, *, /, **, %, parentheses.")

def eval_expr(expr):
    try:
        # Safe eval: no built-ins, no globals
        result = eval(expr, {"__builtins__": None}, {})
        return result
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        expr = " ".join(sys.argv[1:])
        print(eval_expr(expr))
    else:
        print_help()
        while True:
            try:
                expr = input('> ')
                if expr.lower() in ('exit', 'quit'):
                    break
                print(eval_expr(expr))
            except (EOFError, KeyboardInterrupt):
                print("\nExiting.")
                break
