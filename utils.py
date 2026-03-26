import logging

logger = logging.getLogger(__name__)


def format_name(name: str) -> str:
    """Capitalize and return the given name.

    Args:
        name: The raw name string to format.

    Returns:
        The name with the first letter capitalized.
    """
    return name.capitalize()


def greet(name: str) -> str:
    """Build a greeting message for the given name.

    Args:
        name: The name to greet.

    Returns:
        A formatted greeting string.
    """
    logger.info("Greeting user: %s", name)
    return f"Hello {name}, welcome to Claude Code learning!"
