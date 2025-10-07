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


def is_code_like(line: str) -> bool:
    """Check if a line looks like code/log output or a Windows path."""
    return (
        re.match(r"^\s",line)
        or re.search(r"[A-Za-z]:\\", line)
        or "\\\\" in line 
        or line.strip().startswith("C:")
    )

def process_body_lines(body_lines: list[str]) -> list[str]:
    """Convert body lines into simplified HTML."""
    sec_html = []
    buffer_para = []
    pre_lines = []
    in_pre = False
    dl_open = False

    for line in body_lines:
        if is_code_like(line):
            flush_paragraph(buffer_para, sec_html)
            if dl_open:
                sec_html.append("</dl>")
                dl_open = False
            pre_lines.append(line)
            in_pre = True
            continue 
        match = re.match(r"^([^:]+):\s*(.)$", line)
        if match: 
            flush_paragraph(buffer_para, sec_html)
            if in_pre:
                flush_pre(pre_lines, sec_html)
                in_pre = False
            if not dl_open:
                sec_html.append("<dl>")
                dl_open = True
            key, val = match.group(1).strip(), match.group(2).strip()
            sec_html.append(f"<dt>{escape(key)}</dt><dd>{escape(val)}</dd>")
        else:
            if dl_open:
                sec_html.append("</dl>")
                dl_open = False
            buffer_para.append(line)

    flush_paragraph(buffer_para, sec_html)
    if in_pre:
        flush_pre(pre_lines, sec_html)
    if dl_open:
        sec_html.append("</dl>")

    return sec_html

def convert_text_to_html(text: str) -> str:
    """Main converter"""
    sections = split_sections(text)
    html_parts = []

    for sec in sections:
        sec = sec.strip()
        if not sec: 
            continue

        lines = sec.splitlines()
        title, body_lines = extract_title_and_body(lines)

        sec_html = []
        if title:
            sec_html.append(f"<h2>{escape(title)}</h2>")
        sec_html.extend(process_body_lines(body_lines))
        html_parts.append("".join(sec_html))

    return (
        "<!doctype html><html><head>" \
        "<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        "</head><body>"
        + "<hr />".join(html_parts) + 
        "</body></html>"
    )

def check_html_body_length(html_body: str):
    """Checks the length of html body"""
    query = urllib.parse.urlencode({"html": html_body})
    print(f"Converted HTML: {len(query)}")

def clean_text_from_ruleblock(text: str):
    """An incident detail often has a ruleblock text in it. Sometimes this are not required to include in the html body"""
    pattern = re.compile(r'(Rule Block\s+\d+\s+Raw\s+Logs)\n?(.*?)\n(?=Rule Block|\Z)', re.DOTALL)
    data = re.search(pattern, text)
    return re.sub(r'Rule Block 1 Raw Logs.*', '', text, flags=re.DOTALL)

def chunk_text(text: str, chunksize: int = 1600) -> list:
    """Chunk Text to convert to html body"""
    return [text[i: i+chunksize] for i in range(0, len(text), chunksize)]

if __name__ == "__main__":
    sample_text = """<Write your escalation notes here to convert to html>"""
    html = convert_text_to_html(sample_text.strip())
    with open(f"escalation_notes.html", "w", encoding='utf-8') as f:
        f.write(html)


    ### Chunk option:
    # chunks = chunk_text(sample_text)
    # first option:
    # for idx, item in enumerate(chunks, start=1):
    #     context = item
    #     if idx == 1:
    #         context = item + "\n\nAdditional Information will be provided shortly...\n"
    #     with open(f"escalation_{idx}.txt", "w", encoding="utf-8") as f:
    #         f.write(context)
    

    ### Combination
    # with open(f"escalation_combined.txt", "w", encoding="utf-8") as f:
    #     f.write(''.join(chunks[0])[0:-53] + ''.join(chunks[1:]))

    ####