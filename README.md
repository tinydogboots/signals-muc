# Signals MUC

A pair of small in-browser data-viz tools for Munich weather. Everything runs
client-side — no server, no build step. Open the site, drop a file, twist a
slider, export SVG.

## The tools

**Glitch Studio** — 21 years of Munich daily temperature/humidity, faceted by
year. Live SVG filters (Slice, Displace, Wash, RGB Split, Noise, Blocks),
recolourable dots, tweakable frame. Exports fully-editable SVG.

**Wind Field** — Compass-driven vector field over an artboard you supply.
Drop in an SVG or PNG; anything dark becomes an obstacle and the wind curves
around it. A rotatable compass sets the base wind direction. Density scales
near obstacles (denser wind = tighter arrows), and can drive a colour harmony
(mono / analogous / complementary / split / triad / tetrad) applied to the
background.

## Running locally

Any static HTTP server works. Example:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000/

## Files

- `index.html` — tab shell
- `glitch.html` — Glitch Studio
- `wind.html` — Wind Field
- `munich_by_year.svg` — base chart consumed by Glitch Studio
- `plot_munich.py`, `plot_munich_by_year.py` — Python scripts that regenerate
  the base charts from Open-Meteo data (optional; only needed if you want to
  reproduce the SVG)

## Data

Munich temperature, humidity and wind: Open-Meteo historical archive
(free, no key). Station: München (48.14 N, 11.58 E).
