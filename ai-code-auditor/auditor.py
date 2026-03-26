"""
auditor.py — CLI entry point for the AI Codebase Auditor.

Usage:
    python auditor.py <folder>                   # print report to terminal
    python auditor.py <folder> --output report.txt  # save to file
    python auditor.py <folder> --no-color        # terminal output without colors
"""

import argparse
import sys
from analyzer import analyze_folder
from report import print_report, save_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="auditor",
        description="AI Codebase Auditor — static analysis for Python projects",
    )
    parser.add_argument(
        "folder",
        help="Path to the folder containing Python files to audit",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Save the report to a text file instead of printing it",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored terminal output",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print(f"Scanning folder: {args.folder}\n")

    try:
        reports = analyze_folder(args.folder)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except NotADirectoryError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if not reports:
        print("No Python files found in the specified folder.")
        sys.exit(0)

    if args.output:
        save_report(reports, args.output)
    else:
        from report import format_report
        use_color = not args.no_color
        print(format_report(reports, use_color=use_color))


if __name__ == "__main__":
    main()
