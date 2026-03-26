import anthropic


def read_file(file_path: str) -> str:
    """Read a Python file and return its contents."""
    with open(file_path, "r") as f:
        return f.read()


def analyze_code(file_path: str, code: str) -> None:
    """Send code to Claude and stream the explanation and suggestions."""
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from environment

    prompt = f"""Here is a Python file named `{file_path}`:

```python
{code}
```

Please:
1. Explain what this code does in simple terms
2. Suggest specific improvements (readability, performance, best practices)
"""

    print("Claude's Analysis\n" + "=" * 40)

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=64000,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print()  # newline after streaming ends
