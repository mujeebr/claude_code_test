"""
report.py — Formats and outputs the audit results.

Supports two output modes:
  - terminal: colored, human-readable text
  - file:     plain-text report saved to disk
"""

import textwrap
from pathlib import Path
from analyzer import FileReport


# ANSI color codes (auto-disabled when writing to file)
class Color:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    GREEN  = "\033[92m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    DIM    = "\033[2m"


def _colorize(text: str, color: str, use_color: bool = True) -> str:
    if not use_color:
        return text
    return f"{color}{text}{Color.RESET}"


def _section_header(title: str, use_color: bool = True) -> str:
    line = "─" * 60
    if use_color:
        return f"\n{Color.BOLD}{Color.CYAN}{line}\n  {title}\n{line}{Color.RESET}"
    return f"\n{line}\n  {title}\n{line}"


def _bullet_list(items: list[str], use_color: bool = True, indent: int = 4) -> str:
    lines = []
    pad = " " * indent
    for item in items:
        prefix = _colorize("•", Color.YELLOW, use_color)
        wrapped = textwrap.fill(item, width=100, subsequent_indent=pad + "  ")
        lines.append(f"{pad}{prefix} {wrapped}")
    return "\n".join(lines)


def format_report(reports: list[FileReport], use_color: bool = True) -> str:
    """Build the full audit report string."""
    lines = []

    # Title banner
    banner = "  AI CODEBASE AUDITOR — REPORT"
    lines.append(_colorize("=" * 60, Color.BOLD, use_color))
    lines.append(_colorize(banner, Color.BOLD + Color.WHITE, use_color))
    lines.append(_colorize("=" * 60, Color.BOLD, use_color))
    lines.append(f"  Files analyzed: {len(reports)}\n")

    total_issues = sum(
        (0 if r.quality_issues == ["No quality issues found."] else len(r.quality_issues)) +
        (0 if r.bugs == ["No bugs detected."] else len(r.bugs)) +
        (0 if r.improvements == ["No improvements suggested."] else len(r.improvements))
        for r in reports
        if not r.parse_error
    )
    lines.append(f"  Total findings: {total_issues}\n")

    for report in reports:
        # File header
        lines.append(_section_header(f"FILE: {report.filename}", use_color))

        if report.parse_error:
            lines.append(
                _colorize(f"    [ERROR] {report.parse_error}", Color.RED, use_color)
            )
            continue

        # Quality
        lines.append(_colorize("\n  [CODE QUALITY]", Color.GREEN + Color.BOLD, use_color))
        lines.append(_bullet_list(report.quality_issues, use_color))

        # Bugs
        lines.append(_colorize("\n  [POTENTIAL BUGS]", Color.RED + Color.BOLD, use_color))
        lines.append(_bullet_list(report.bugs, use_color))

        # Improvements
        lines.append(_colorize("\n  [IMPROVEMENTS]", Color.YELLOW + Color.BOLD, use_color))
        lines.append(_bullet_list(report.improvements, use_color))

    lines.append("\n" + _colorize("=" * 60, Color.BOLD, use_color))
    lines.append(_colorize("  Audit complete.", Color.GREEN + Color.BOLD, use_color))
    lines.append(_colorize("=" * 60, Color.BOLD, use_color) + "\n")

    return "\n".join(lines)


def print_report(reports: list[FileReport]) -> None:
    """Print the colored report to stdout."""
    print(format_report(reports, use_color=True))


def save_report(reports: list[FileReport], output_path: str) -> None:
    """Save a plain-text (no ANSI) report to a file."""
    content = format_report(reports, use_color=False)
    Path(output_path).write_text(content, encoding="utf-8")
    print(f"Report saved to: {output_path}")
