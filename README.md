# Data Consolidation at DHS — Interactive Visualizations

Three interactive data visualizations for a Brennan Center for Justice piece on
the Department of Homeland Security's consolidation and integration of personal
data for surveillance and immigration enforcement.

## The visualizations

1. **A Protest in New York** — a scroll-driven map showing how a single phone's
   location data can be traced from a protest to a person's home, workplace, and
   daily routines.
2. **Key DHS Surveillance Technology Vendors** — a matrix of the technology
   vendors contracted by DHS components, with contract values and the agencies
   they serve.
3. **Information Sharing** — a flow diagram of how federal, state, and local
   agencies share data with DHS, including which sharing programs courts have
   blocked.

> **Naming note:** the files are numbered by build order (`viz-1/2/3`), which
> differs from the reading order in the article. In reading order, "Visual 2" is
> the vendor matrix (`viz-3-embed.html`) and "Visual 3" is the information-sharing
> diagram (`viz-2-embed.html`).

## Structure

| Path | What it is |
|------|------------|
| `index.html` | Single source of truth — all three visualizations, the article prose, CSS, JS, and embedded data live here. |
| `build-embeds.py` | Extracts each visualization from `index.html` into a standalone, self-contained embed. |
| `viz-1-embed.html`, `viz-2-embed.html`, `viz-3-embed.html` | The generated embeds, for use in an `<iframe>`. Regenerate after editing `index.html`. |
| `fonts/` | Web-font subsets (Benton Sans, Editor). |
| `viz-1/protest-lns.mp4` | Video used by the first visualization. |

## Building the embeds

After editing `index.html`, regenerate the three embeds:

```bash
python3 build-embeds.py
```

## Running locally

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/> for the full piece, or
<http://localhost:8000/viz-1-embed.html> (etc.) for an individual embed.

## Embedding

Each `viz-*-embed.html` is self-contained and can be dropped into a CMS via an
`<iframe>`. The embeds reference `fonts/` and `viz-1/protest-lns.mp4` by relative
path, so keep those alongside the embeds when hosting.

## Tech

Plain HTML, CSS, and JavaScript — no build step or package dependencies beyond
Python 3 (standard library) for the embed generator. The scroll-driven map uses
[MapLibre GL JS](https://maplibre.org/) with [OpenFreeMap](https://openfreemap.org/)
tiles, loaded from a CDN.
