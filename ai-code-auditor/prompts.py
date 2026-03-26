"""
Prompt templates for simulating Claude-style code analysis reasoning.
Each function returns a structured prompt string used by the analyzer.
"""


def code_quality_prompt(filename: str, code: str) -> str:
    return f"""
You are a senior Python code reviewer. Analyze the following file for code quality issues.

File: {filename}
---
{code}
---

Check for:
1. PEP 8 style violations (naming, spacing, line length)
2. Missing or poor docstrings/comments
3. Overly complex functions (too many lines or responsibilities)
4. Hardcoded values that should be constants or config
5. Unused imports or variables

Respond with a concise bullet list of issues found. If none, say "No quality issues found."
"""


def bug_detection_prompt(filename: str, code: str) -> str:
    return f"""
You are a Python bug hunter. Review the following code for potential bugs and runtime errors.

File: {filename}
---
{code}
---

Look for:
1. Unhandled exceptions (file I/O, type errors, index errors)
2. Mutable default arguments (e.g., def foo(x=[]))
3. Off-by-one errors in loops
4. Incorrect use of == vs `is` for None/boolean checks
5. Missing return statements or inconsistent return types
6. Resource leaks (unclosed files, connections)

Respond with a concise bullet list of bugs found. If none, say "No bugs detected."
"""


def improvement_prompt(filename: str, code: str) -> str:
    return f"""
You are a Python performance and design expert. Suggest improvements for the following code.

File: {filename}
---
{code}
---

Suggest:
1. Use of list/dict comprehensions where applicable
2. Replacing repetitive code with helper functions
3. Better use of Python standard library (pathlib, collections, itertools)
4. Type hints for function signatures
5. More Pythonic patterns

Respond with a concise bullet list of suggestions. If none, say "No improvements suggested."
"""
