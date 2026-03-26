"""
analyzer.py — Reads Python files and runs static + heuristic analysis.

Instead of calling an external API, this module uses AST (Abstract Syntax Tree)
parsing and regex-based heuristics to simulate structured code reasoning.
"""

import ast
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FileReport:
    filename: str
    quality_issues: list[str] = field(default_factory=list)
    bugs: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    parse_error: Optional[str] = None


def collect_python_files(folder: str) -> list[Path]:
    """Recursively collect all .py files under the given folder."""
    root = Path(folder)
    if not root.exists():
        raise FileNotFoundError(f"Folder not found: {folder}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder}")
    return sorted(root.rglob("*.py"))


def analyze_file(filepath: Path) -> FileReport:
    """Run all analysis passes on a single Python file."""
    report = FileReport(filename=str(filepath))

    try:
        source = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        report.parse_error = f"Could not read file: {e}"
        return report

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as e:
        report.parse_error = f"SyntaxError: {e}"
        return report

    report.quality_issues = _check_quality(source, tree, filepath)
    report.bugs = _check_bugs(source, tree)
    report.improvements = _check_improvements(source, tree)

    return report


# ---------------------------------------------------------------------------
# Quality checks
# ---------------------------------------------------------------------------

def _check_quality(source: str, tree: ast.AST, filepath: Path) -> list[str]:
    issues = []

    # Long lines
    for i, line in enumerate(source.splitlines(), start=1):
        if len(line) > 120:
            issues.append(f"Line {i} exceeds 120 characters ({len(line)} chars)")

    # Missing module-level docstring
    if not (isinstance(tree, ast.Module) and ast.get_docstring(tree)):
        issues.append("Module is missing a top-level docstring")

    # Functions/classes without docstrings
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                issues.append(
                    f"{'Function' if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else 'Class'} "
                    f"'{node.name}' (line {node.lineno}) is missing a docstring"
                )

    # Overly long functions (> 50 lines)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_lines = (node.end_lineno or node.lineno) - node.lineno
            if func_lines > 50:
                issues.append(
                    f"Function '{node.name}' (line {node.lineno}) is {func_lines} lines long — consider splitting it"
                )

    # Unused imports (simple heuristic: import name not referenced elsewhere)
    imported_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name.split(".")[0]
                imported_names.append((name, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                name = alias.asname or alias.name
                imported_names.append((name, node.lineno))

    for name, lineno in imported_names:
        # Count occurrences outside import lines
        occurrences = len(re.findall(rf'\b{re.escape(name)}\b', source))
        if occurrences <= 1:
            issues.append(f"Import '{name}' (line {lineno}) may be unused")

    if not issues:
        issues.append("No quality issues found.")
    return issues


# ---------------------------------------------------------------------------
# Bug detection
# ---------------------------------------------------------------------------

def _check_bugs(source: str, tree: ast.AST) -> list[str]:
    bugs = []

    # Mutable default arguments
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in node.args.defaults + node.args.kw_defaults:
                if default is not None and isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    bugs.append(
                        f"Function '{node.name}' (line {node.lineno}) uses a mutable default argument — use None instead"
                    )

    # Bare except clauses
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.type is None:
            bugs.append(f"Bare 'except:' clause at line {node.lineno} — catch specific exceptions")

    # Comparison to None using == instead of `is`
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(comparator, ast.Constant) and comparator.value is None:
                    bugs.append(
                        f"Line {node.lineno}: use 'is None' / 'is not None' instead of '== None' or '!= None'"
                    )

    # Open() without context manager
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "open":
                # Check if this call is inside a `with` statement
                # Simple heuristic: look for assignment not in With block
                parent_types = [type(n).__name__ for n in ast.walk(tree)]
                if "With" not in parent_types:
                    bugs.append(f"Line {node.lineno}: 'open()' call may not use a context manager — prefer 'with open(...)'")

    # assert used for runtime validation
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            bugs.append(
                f"Line {node.lineno}: 'assert' used — assertions are disabled with -O flag; use explicit checks for runtime validation"
            )

    if not bugs:
        bugs.append("No bugs detected.")
    return bugs


# ---------------------------------------------------------------------------
# Improvement suggestions
# ---------------------------------------------------------------------------

def _check_improvements(source: str, tree: ast.AST) -> list[str]:
    suggestions = []

    # For-loop building a list that could be a list comprehension
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            body = node.body
            if (
                len(body) == 1
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Call)
            ):
                call = body[0].value
                if isinstance(call.func, ast.Attribute) and call.func.attr == "append":
                    suggestions.append(
                        f"Line {node.lineno}: for-loop with .append() could be replaced with a list comprehension"
                    )

    # Missing type hints on function signatures
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = node.args.args
            missing_hints = [a.arg for a in args if a.annotation is None and a.arg != "self"]
            if missing_hints or node.returns is None:
                suggestions.append(
                    f"Function '{node.name}' (line {node.lineno}) is missing type hints"
                )

    # os.path usage — suggest pathlib
    if re.search(r'\bos\.path\b', source):
        suggestions.append("Consider replacing 'os.path' usage with 'pathlib.Path' for cleaner path handling")

    # String concatenation in a loop
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            for child in ast.walk(node):
                if isinstance(child, ast.AugAssign) and isinstance(child.op, ast.Add):
                    if isinstance(child.value, ast.Constant) and isinstance(child.value.value, str):
                        suggestions.append(
                            f"Line {node.lineno}: string concatenation in a loop — use ''.join(...) instead"
                        )

    # print() used instead of logging
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                suggestions.append(
                    f"Line {node.lineno}: consider replacing 'print()' with the 'logging' module for production code"
                )
                break  # one suggestion per file is enough

    if not suggestions:
        suggestions.append("No improvements suggested.")
    return suggestions


def analyze_folder(folder: str) -> list[FileReport]:
    """Entry point: collect and analyze all Python files in the given folder."""
    files = collect_python_files(folder)
    return [analyze_file(f) for f in files]
