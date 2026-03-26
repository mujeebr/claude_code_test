import logging
import sys

from utils import format_name, greet

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main() -> None:
    """Entry point for the application."""
    name = format_name("mujeeb")
    print(greet(name))


if __name__ == "__main__":
    sys.exit(main())
