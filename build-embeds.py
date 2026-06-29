#!/usr/bin/env python3
"""Extract each visualization from index.html into a standalone embed file.

Uses marker-based extraction (resilient to line-number drift) instead of
hardcoded ranges. For each viz, finds the opening comment marker and tracks
<div> depth to find the matching close.
"""
import re
from pathlib import Path

PROJECT = Path("/Users/nassereledroos/_dev/bcj/data-integration")
SRC = PROJECT / "index.html"


def find_matching_close(html: str, open_pos: int) -> int:
    """Given position of an opening <div...>, return position just after its
    matching </div>. Tracks nested divs."""
    # Skip past the opening tag
    tag_end = html.index(">", open_pos) + 1
    depth = 1
    pos = tag_end
    # Match either <div ...> or </div>
    pattern = re.compile(r"</?div\b", re.IGNORECASE)
    while depth > 0:
        m = pattern.search(html, pos)
        if not m:
            raise ValueError("Unbalanced <div> when extracting viz block")
        if m.group(0).startswith("</"):
            depth -= 1
        else:
            depth += 1
        pos = html.index(">", m.start()) + 1
    return pos


def extract_viz(html: str, marker_regex: str) -> str:
    """Find the comment marker and the <div> immediately following it; return
    the full block (marker + div + everything until matching close)."""
    m = re.search(marker_regex, html)
    if not m:
        raise ValueError(f"Marker not found: {marker_regex}")
    marker_start = m.start()
    div_open = html.index("<div", m.end())
    close_end = find_matching_close(html, div_open)
    return html[marker_start:close_end]


def build_embeds():
    html = SRC.read_text()

    # Slice 1: from start through </head>
    head_end = html.index("</head>") + len("</head>")
    head = html[:head_end]

    # Slice 2: script onward through end of file
    script_marker = html.index("<!-- JAVASCRIPT LOGIC -->")
    script_to_end = html[script_marker:]

    # Each viz block (comment + matching div tree)
    viz1 = extract_viz(html, r"<!-- VIZ 1: FULL-SCREEN LOCATION TIMELINE -->")
    viz2 = extract_viz(html, r"<!-- VIZ 2: FEDERAL DATA HUB \(Vertical Sankey\) -->")
    viz3 = extract_viz(html, r"<!-- VIZ 3: SURVEILLANCE VENDOR MATRIX -->")

    embed_style = """
<style>
    /* Embed-mode: hide article header and prose containers */
    body { margin: 0; padding: 0; background: #fff; }
    .container { display: none !important; }
    header, footer { display: none !important; }
</style>
"""

    def assemble(name: str, viz_block: str, body_class: str, label: str, needs_maplibre: bool):
        head_with_style = head.replace("</head>", embed_style + "</head>", 1)
        if not needs_maplibre:
            # MapLibre GL (~200KB JS + CSS) is only used by the Viz 1 map.
            # The shared script block guards its init with a typeof check,
            # so the other embeds can safely skip loading it.
            head_with_style = re.sub(
                r'[ \t]*<!-- MapLibre GL JS[^\n]*-->\n'
                r'[ \t]*<link[^\n]*maplibre-gl[^\n]*\n'
                r'[ \t]*<script[^\n]*maplibre-gl[^\n]*\n',
                '',
                head_with_style,
            )
            # CSS rules targeting .maplibregl-* class names remain in the head
            # but are inert without the library; only the loader tags matter.
            if 'maplibre-gl.js' in head_with_style or 'maplibre-gl.css' in head_with_style:
                raise RuntimeError(f"{name}: MapLibre strip failed")
        body_open_tag = f'<body class="embed-mode {body_class}">\n'
        out = (
            head_with_style
            + "\n"
            + body_open_tag
            + viz_block
            + "\n"
            + script_to_end
        )
        # Sanity: must end with </html>
        if not out.rstrip().endswith("</html>"):
            raise RuntimeError(f"{name} doesn't end with </html>")
        if "<body" not in out:
            raise RuntimeError(f"{name} missing <body> tag")
        (PROJECT / name).write_text(out)
        print(f"Wrote {name} ({len(out):,} bytes) — {label}")

    assemble("viz-1-embed.html", viz1, "embed-viz-1", "scrollytelling map", needs_maplibre=True)
    assemble("viz-2-embed.html", viz2, "embed-viz-2", "Sankey diagram", needs_maplibre=False)
    assemble("viz-3-embed.html", viz3, "embed-viz-3", "vendor matrix", needs_maplibre=False)


if __name__ == "__main__":
    build_embeds()
