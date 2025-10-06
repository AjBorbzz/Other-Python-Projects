"""
Simple converter from Plain text to HTML
Features:
 Splits sections on lines containing only '---'
 Treats the first non-empty line of each section as a heading
 Converts "Key: Value" lines to <div><strong>key:</strong> Value</div>
 Groups normal lines into paragraphs (<p>)
 Detects code/log lines (Indented or Windows paths with backslashes) and wraps them in <pre>
 Escapes HTML characters
"""

from html import escape
import re 
import urllib.parse
# Import some test text


def split_sections(text: str) -> list[str]:
    """Split into sections on lines that contain only --- (with optional surrounding spaces)"""
    return re.split(r'(?m)^[ \t]*-{3,}[ \t]*$', text)

def extract_title_and_body(lines: list[str]) -> tuple[str | None, list[str]]:
    """Extract the first non-empty line as the title and the rest as body lines"""
    for i, line in enumerate(lines):
        if line.strip():
            return line.strip(), lines[i + 1: ]
    return None, []