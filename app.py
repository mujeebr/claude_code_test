import logging
import sys

from utils import format_name, greet

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def main() -> None:
    """Entry point for the application."""
    try:
        name = format_name("mujeeb")
        print(greet(name))
    except ValueError as e:
        logger.error("Invalid input: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
