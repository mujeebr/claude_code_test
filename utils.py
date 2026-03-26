import logging

logging.basicConfig(level=logging.INFO)

def format_name(name):
    return name.capitalize()

def greet(name):
    logging.info(f"Greeting user: {name}")
    return f"Hello {name}, welcome to Claude Code learning!"