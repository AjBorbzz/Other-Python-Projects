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

def flush_paragraph(buffer: list[str], html_parts: list[str]) -> None:
    """Flush paragragh buffer into HTML and clear it."""
    if buffer:
        para_text = " ".join(line.strip() for line in buffer)
        html_parts.append(f"<p>{escape(para_text)}</p>")
        buffer.clear()

def flush_pre(pre_lines: list[str], html_parts: list[str]) -> None:
    """Flush preformatted block into HTML and clear it."""
    if pre_lines:
        html_parts.append(f"<pre>{escape('\n'.join(pre_lines))}</pre>")
        pre_lines.clear()


