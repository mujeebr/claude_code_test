import sys
import os
import anthropic
from helper import read_file, analyze_code


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_python_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    if not file_path.endswith(".py"):
        print("Warning: File does not have a .py extension.")

    print(f"Reading: {file_path}\n")

    try:
        code = read_file(file_path)
        if not code.strip():
            print("Error: File is empty.")
            sys.exit(1)
        analyze_code(file_path, code)
    except anthropic.AuthenticationError:
        print("Error: Invalid API key. Set ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)
    except anthropic.APIConnectionError:
        print("Error: Could not connect to the API. Check your internet connection.")
        sys.exit(1)
    except anthropic.RateLimitError:
        print("Error: Rate limit reached. Please wait a moment and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
