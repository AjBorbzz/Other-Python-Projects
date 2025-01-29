import os
from dotenv import load_dotenv, find_dotenv

def load_env():
    """Load environment variables from a .env file."""
    load_dotenv(find_dotenv())

def get_api_key(key_name):
    """Retrieves the specified API key from environment variables.
    Args:
        key_name: the name of the API key

    Returns:
        The value of the API key.

    Raises:
        KeyError: If the API Key is not found in the environment
    """
    load_env()
    try:
        return os.environ[key_name]
    except KeyError:
        raise KeyError(f"API Key: '{key_name}' is not found in environment variables.")
    

def get_claude_api_key():
    """Retrieves the claude API key from environment variables."""
    return get_api_key("CLAUDE_API_KEY")

def get_serper_api_key():
    """Retrieves the Serper API Key from environment variables."""
    return get_api_key("SERPER_API_KEY")

def wrap_text(text, max_width=80):
    """
    Wraps text to a specific maximum width (80).

    Args:
        text: The text to wrap.
        max_width (Default=80): The maximum width of each line.

    Returns:
        The wrapped text.
    """
    lines = []
    current_line = ""
    for word in text.split():
        if len(current_line) + len(word) + 1 > max_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line += " " + word if current_line else word
        
    if current_line:
        lines.append(current_line)
    return "\n".join(lines)

def pretty_print_result(result):
    """
    Wraps the given result to a maximum line width of 80 characters.

    Args:
      result: The string to be formatted.

    Returns:
      The formatted string with lines wrapped at 80 characters.
    """
    return wrap_text(result)
