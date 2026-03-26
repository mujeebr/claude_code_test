import logging

logger = logging.getLogger(__name__)

GREETING_TEMPLATE = "Hello {name}, welcome to Claude Code learning!"


def format_name(name: str) -> str:
    """Capitalize and return the given name.

    Args:
        name: The raw name string to format.

    Returns:
        The name with the first letter capitalized.

    Raises:
        ValueError: If name is empty or whitespace.
    """
    if not name or not name.strip():
        raise ValueError("Name must be a non-empty string.")
    return name.capitalize()


def greet(name: str) -> str:
    """Build a greeting message for the given name.

    Args:
        name: The name to greet.

    Returns:
        A formatted greeting string.

    Raises:
        ValueError: If name is empty or whitespace.
    """
    if not name or not name.strip():
        raise ValueError("Name must be a non-empty string.")
    logger.info("Greeting user: %s", name)
    return GREETING_TEMPLATE.format(name=name)
