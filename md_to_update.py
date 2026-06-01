"""
md_to_update.py
---------------
Converts a Markdown ministry update file into a full HTML page
using Logan's ministry update template layout.

USAGE (Spyder):
    Run the file. It will prompt you to enter the markdown filename.
    The .md extension is optional — it will be added automatically.

USAGE (Terminal):
    python3 md_to_update.py your-update.md

OUTPUT:
    Creates a matching HTML file in the same folder as the .md file.
    e.g. update-march2026.md → update-march2026.html

--------------------------------------------------------------------
MARKDOWN CONVENTIONS
--------------------------------------------------------------------

FRONT MATTER (required, must be at the very top):
    ---
    title: Ministry Update - March 2026
    date: 3/9/26
    intro: Opening paragraph shown below the title before the banner.
    banner: images/update-images/photo.jpg
    prev_page: page-ministryupdates-home.html
    prev_label: Back to Ministry Updates
    ---

SECTION HEADINGS:
    # Heading       →  centered h2
    ## Heading      →  left-aligned h2

REGULAR PARAGRAPHS:
    Just write normally. Separate paragraphs with a blank line.

INLINE FORMATTING:
    **bold text**
    *italic text*

SINGLE IMAGE (full width by default):
    [image: path/to/img.jpg | Caption]

TWO-COLUMN IMAGE GRID:
    [image-left:  path/to/img.jpg | Caption | Optional Heading]
    [image-right: path/to/img.jpg | Caption | Optional Heading]
    (place on consecutive lines — they pair automatically)

FULL-WIDTH IMAGE:
    [image-full: path/to/img.jpg | Caption text]

RIGHT-FLOATED IMAGE (text wraps left):
    [image-right-float: path/to/img.jpg | Alt text]

BUTTON LINK:
    [button: Button Label | https://link.com]

BULLET LIST:
    - Item one
    - Item two

HORIZONTAL DIVIDER:
    ---  (on its own line, after front matter)

SIGN-OFF:
    [signoff: Logan Augustine, 3/9/26]

BLOCK QUOTE (scripture etc.):
    > "Text here" Reference
"""

import sys
import re
import os


# ---------------------------------------------------------------------------
# Inline formatting (bold, italic)
# ---------------------------------------------------------------------------

def apply_inline(text):
    """Convert **bold** and *italic* to HTML."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text


# ---------------------------------------------------------------------------
# Front matter parser
# ---------------------------------------------------------------------------

def parse_front_matter(text):
    """Extract YAML-style front matter from between --- delimiters."""
    meta = {}
    body = text
    pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
    match = pattern.match(text)
    if match:
        for line in match.group(1).splitlines():
            if ':' in line:
                key, _, value = line.partition(':')
                meta[key.strip()] = value.strip()
        body = text[match.end():]
    else:
        print("Warning: No front matter found. Using default values.")
        print("Add a --- block at the top of your .md file for title, banner, etc.")
    return meta, body


# ---------------------------------------------------------------------------
# Special line detector
# ---------------------------------------------------------------------------

def is_special_line(line):
    """Returns True if a line should NOT be absorbed into a paragraph."""
    if not line:
        return True
    if line == '---':
        return True
    if re.match(r'^#{1,6} ', line):
        return True
    if re.match(r'^\[image', line):
        return True
    if re.match(r'^\[button:', line):
        return True
    if re.match(r'^\[signoff:', line):
        return True
    if line.startswith('- '):
        return True
    if line.startswith('> '):
        return True
    return False


# ---------------------------------------------------------------------------
# Body converter
# ---------------------------------------------------------------------------

def convert_body(body):
    """Convert markdown body lines into HTML blocks."""
    lines = body.splitlines()
    html_blocks = []
    i = 0
    pending_left = None

    while i < len(lines):
        line = lines[i].strip()

        # blank line
        if not line:
            i += 1
            continue

        # horizontal rule
        if line == '---':
            if pending_left:
                html_blocks.append(_close_grid(pending_left))
                pending_left = None
            html_blocks.append('<hr />')
            i += 1
            continue

        # [image: path | caption]  →  full width single image
        m = re.match(r'\[image:\s*(.+?)\s*\|\s*(.+?)\s*\]', line)
        if m:
            if pending_left:
                html_blocks.append(_close_grid(pending_left))
                pending_left = None
            html_blocks.append(_full_image(m.group(1), m.group(2)))
            i += 1
            continue

        # [image-left: path | caption | heading?]
        m = re.match(r'\[image-left:\s*(.+?)\s*\|\s*(.+?)(?:\s*\|\s*(.+?))?\s*\]', line)
        if m:
            pending_left = (m.group(1).strip(), m.group(2).strip(), (m.group(3) or '').strip())
            i += 1
            continue

        # [image-right: path | caption | heading?]
        m = re.match(r'\[image-right:\s*(.+?)\s*\|\s*(.+?)(?:\s*\|\s*(.+?))?\s*\]', line)
        if m:
            right = (m.group(1).strip(), m.group(2).strip(), (m.group(3) or '').strip())
            if pending_left:
                html_blocks.append(_two_col_grid(pending_left, right))
                pending_left = None
            else:
                html_blocks.append(_full_image(right[0], right[1]))
            i += 1
            continue

        # [image-full: path | caption]
        m = re.match(r'\[image-full:\s*(.+?)\s*\|\s*(.+?)\s*\]', line)
        if m:
            if pending_left:
                html_blocks.append(_close_grid(pending_left))
                pending_left = None
            html_blocks.append(_full_image(m.group(1).strip(), m.group(2).strip()))
            i += 1
            continue

        # [image-right-float: path | alt]
        m = re.match(r'\[image-right-float:\s*(.+?)\s*\|\s*(.+?)\s*\]', line)
        if m:
            html_blocks.append(
                f'<img class="image right" src="{m.group(1).strip()}" '
                f'alt="{m.group(2).strip()}" />'
            )
            i += 1
            continue

        # [button: label | url]
        m = re.match(r'\[button:\s*(.+?)\s*\|\s*(.+?)\s*\]', line)
        if m:
            html_blocks.append(
                f'<div style="text-align:center; margin:1.5em 0;">'
                f'<ul class="actions" style="margin:0;">'
                f'<li><a href="{m.group(2).strip()}" class="button large" '
                f'target="_blank">{m.group(1).strip()}</a></li>'
                f'</ul></div>'
            )
            i += 1
            continue

        # [signoff: name]
        m = re.match(r'\[signoff:\s*(.+?)\s*\]', line)
        if m:
            html_blocks.append(
                f'<div style="text-align:right; margin-top:3em;">'
                f'<p>In Christ,</p>'
                f'<p>{m.group(1).strip()}</p>'
                f'</div>'
            )
            i += 1
            continue

        # > blockquote (scripture)
        if line.startswith('> '):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('> '):
                quote_lines.append(apply_inline(lines[i].strip()[2:]))
                i += 1
            html_blocks.append(
                f'<blockquote style="border-left:4px solid rgba(46,186,174,0.5); '
                f'padding-left:1.25em; margin:1.5em 0; font-style:italic; color:#666;">'
                f'{" ".join(quote_lines)}'
                f'</blockquote>'
            )
            continue

        # # Centered section heading
        if line.startswith('# '):
            heading = apply_inline(line[2:].strip())
            html_blocks.append(
                f'<div style="text-align:center;"><h2>{heading}</h2></div>'
            )
            i += 1
            continue

        # ## Left-aligned subheading
        if line.startswith('## '):
            heading = apply_inline(line[3:].strip())
            html_blocks.append(f'<h2>{heading}</h2>')
            i += 1
            continue

        # Bullet list
        if line.startswith('- '):
            items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                items.append(f'<li>{apply_inline(lines[i].strip()[2:])}</li>')
                i += 1
            html_blocks.append('<ul>\n' + '\n'.join(items) + '\n</ul>')
            continue

        # Regular paragraph — absorb consecutive non-special lines
        para_lines = []
        while i < len(lines):
            l = lines[i].strip()
            if is_special_line(l):
                break
            para_lines.append(apply_inline(l))
            i += 1
        if para_lines:
            html_blocks.append(f'<p>{" ".join(para_lines)}</p>')
        continue

    # close any unclosed image-left
    if pending_left:
        html_blocks.append(_close_grid(pending_left))

    return '\n\n'.join(html_blocks)


# ---------------------------------------------------------------------------
# HTML snippet helpers
# ---------------------------------------------------------------------------

def _col_cell(src, caption, heading=''):
    heading_html = f'<h2>{heading}</h2>\n' if heading else ''
    caption_html = (
        f'<p style="font-size:0.8em; margin-top:0.5em; color:#888;">{caption}</p>'
        if caption else ''
    )
    return (
        f'<div style="text-align:center;">\n'
        f'{heading_html}'
        f'<img src="{src}" alt="{caption}" '
        f'style="width:100%; height:360px; object-fit:cover; border-radius:6px; '
        f'border:2px solid rgba(160,160,160,0.4);" />\n'
        f'{caption_html}\n'
        f'</div>'
    )

def _two_col_grid(left, right):
    return (
        f'<div style="display:grid; grid-template-columns:1fr 1fr; '
        f'gap:1.5em; align-items:start; margin:2em 0;">\n'
        f'{_col_cell(*left)}\n{_col_cell(*right)}\n</div>'
    )

def _close_grid(left):
    return (
        f'<div style="display:grid; grid-template-columns:1fr 1fr; '
        f'gap:1.5em; align-items:start; margin:2em 0;">\n'
        f'{_col_cell(*left)}\n<div></div>\n</div>'
    )

def _full_image(src, caption):
    caption_html = (
        f'<p style="font-size:0.8em; text-align:center; color:#888; '
        f'margin-top:-1.5em; margin-bottom:2em;">{caption}</p>'
        if caption else ''
    )
    return (
        f'<span class="image featured">\n'
        f'<img src="{src}" alt="{caption}" />\n'
        f'</span>\n{caption_html}'
    )


# ---------------------------------------------------------------------------
# Full HTML page assembler
# ---------------------------------------------------------------------------

def build_page(meta, body_html):
    title      = meta.get('title',      'Ministry Update')
    intro      = meta.get('intro',      '')
    banner     = meta.get('banner',     '')
    prev_page  = meta.get('prev_page',  'page-ministryupdates-home.html')
    prev_label = meta.get('prev_label', 'Back to Ministry Updates')

    banner_html = (
        f'<span class="image featured">'
        f'<img src="{banner}" alt="Ministry Banner" /></span>'
        if banner else ''
    )

    intro_html = (
        f'<div style="text-align:center;"><p>{apply_inline(intro)}</p></div><hr />'
        if intro else ''
    )

    return f"""<!DOCTYPE HTML>
<!--
    Future Imperfect by HTML5 UP
    Generated by md_to_update.py
-->
<html>
    <head>
        <title>{title}</title>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
        <link rel="stylesheet" href="assets/css/main.css" />
    </head>
    <body class="single is-preload slim-page">

        <div id="wrapper">

            <!-- Header -->
            <header id="header">
                <h1><a href="index.html">Logan Augustine: Ministry Portfolio</a></h1>
                <nav class="links">
                    <ul>
                        <li><a href="page-single.html">Objective, Philosophy, and Experience</a></li>
                        <li><a href="page-ministryupdates-home.html">Ministry Updates</a></li>
                        <li><a href="page-resources.html">Resources/Projects</a></li>
                    </ul>
                </nav>
                <nav class="main">
                    <ul>
                        <li class="search">
                            <a class="fa-search" href="#search">Search</a>
                            <form id="search" method="get" action="#">
                                <input type="text" name="query" placeholder="Search" />
                            </form>
                        </li>
                        <li class="menu">
                            <a class="fa-bars" href="#menu">Menu</a>
                        </li>
                    </ul>
                </nav>
            </header>

            <!-- Menu -->
            <section id="menu">
                <section>
                    <form class="search" method="get" action="#">
                        <input type="text" name="query" placeholder="Search" />
                    </form>
                </section>
                <section>
                    <ul class="links">
                        <li><a href="page-single.html"><h3>Objective &amp; Philosophy</h3></a></li>
                        <li><a href="page-ministryupdates-home.html"><h3>Ministry Updates</h3></a></li>
                        <li><a href="page-resources.html"><h3>Resources/Projects</h3></a></li>
                    </ul>
                </section>
            </section>

            <!-- Main -->
            <div id="main">
                <article class="post">

                    <!-- BANNER TITLE BLOCK -->
                    <header>
                        <div class="title">
                            <div style="text-align:center;">
                                <h2><a href="#">{title}</a></h2>
                                <p style="margin-bottom:0;">A ministry update from Logan Augustine. Much Love!</p>
                            </div>
                        </div>
                    </header>

                    {intro_html}
                    {banner_html}

                    <!-- BODY CONTENT -->
                    {body_html}

                    <footer>
                        <ul class="actions pagination">
                            <li><a href="{prev_page}" class="button large previous">{prev_label}</a></li>
                        </ul>
                    </footer>

                </article>
            </div>

            <!-- Footer -->
            <section id="footer">
                <ul class="icons">
                    <li><a href="#" class="icon brands fa-twitter"><span class="label">Twitter</span></a></li>
                    <li><a href="#" class="icon brands fa-facebook-f"><span class="label">Facebook</span></a></li>
                    <li><a href="#" class="icon brands fa-instagram"><span class="label">Instagram</span></a></li>
                    <li><a href="#" class="icon solid fa-rss"><span class="label">RSS</span></a></li>
                    <li><a href="#" class="icon solid fa-envelope"><span class="label">Email</span></a></li>
                </ul>
                <p class="copyright">&copy; Untitled. Design: <a href="http://html5up.net">HTML5 UP</a>.</p>
            </section>

        </div>

        <script src="assets/js/jquery.min.js"></script>
        <script src="assets/js/browser.min.js"></script>
        <script src="assets/js/breakpoints.min.js"></script>
        <script src="assets/js/util.js"></script>
        <script src="assets/js/main.js"></script>

    </body>
</html>
"""


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def get_input_path():
    """Get the markdown file path — works in both Spyder and Terminal."""
    if len(sys.argv) > 1:
        return sys.argv[1]

    print("=" * 50)
    print("  Ministry Update Converter")
    print("=" * 50)
    print()
    filename = input("Enter your Markdown filename (e.g. update-march2026): ").strip()
    filename = filename.strip('"').strip("'")
    if not filename.endswith('.md'):
        filename += '.md'
    return filename


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    input_path = get_input_path()

    if not os.path.exists(input_path):
        print(f"\nFile not found: '{input_path}'")
        print(f"Make sure the file is in: {os.getcwd()}")
        return

    print(f"\nReading: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        raw = f.read()

    meta, body   = parse_front_matter(raw)
    body_html    = convert_body(body)
    page_html    = build_page(meta, body_html)
    output_path  = os.path.splitext(input_path)[0] + '.html'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(page_html)

    print(f"Success! Generated: {output_path}")
    print(f"\nNext steps:")
    print(f"  1. Open {output_path} in VS Code and preview with Live Server")
    print(f"  2. When happy, run push.py to deploy to GitHub Pages")


if __name__ == "__main__":
    main()