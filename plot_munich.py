"""
Munich weather visualization — port of the R charts from
https://github.com/zonination/weather-intl to a single-city Python version.

Reads munich_raw.csv (Open-Meteo daily archive) and produces two PNGs:
  1) munich_heatmap.png   — daily mean temperature, day-of-year (x) vs year (y)
  2) munich_scatter.png   — humidity vs temperature scatter, coloured by season
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.rcParams["svg.fonttype"] = "none"  # keep text as text in the SVG
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from datetime import datetime

FORMATS = ["png", "svg", "pdf"]  # PNG for preview, SVG/PDF for Illustrator

HERE = Path(__file__).parent
RAW = HERE / "munich_raw.csv"

# Open-Meteo prepends a 2-line metadata block, so skip it.
df = pd.read_csv(RAW, skiprows=2)
df.columns = [
    "date", "temp_c", "humidity", "cloud_cover",
    "precip_mm", "pressure_hpa", "wind_kmh",
]
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year
df["doy"] = df["date"].dt.dayofyear

def season(month):
    if month in (3, 4, 5):   return "Spring"
    if month in (6, 7, 8):   return "Summer"
    if month in (9, 10, 11): return "Autumn"
    return "Winter"
df["season"] = df["date"].dt.month.map(season)

# --------------------------------------------------------------------------
# Chart 1 — heatmap (day-of-year × year, coloured by mean temperature)
# --------------------------------------------------------------------------
grid = df.pivot_table(index="year", columns="doy", values="temp_c")

# ggplot's Spectral (reversed) — blue for cold, red for hot.
spectral = LinearSegmentedColormap.from_list("spectral_r", [
    "#3288BD", "#66C2A5", "#ABDDA4", "#E6F598", "#FFFFBF",
    "#FEE08B", "#FDAE61", "#F46D43", "#D53E4F", "#9E0142",
])

fig, ax = plt.subplots(figsize=(14, 7))
# pcolormesh gives us one editable rectangle per day×year cell in the SVG,
# whereas imshow would flatten to a single raster image.
years = np.array(list(grid.index) + [grid.index.max() + 1]) - 0.5
days = np.arange(1, grid.shape[1] + 2)
im = ax.pcolormesh(days, years, grid.values, cmap=spectral, vmin=-15, vmax=30,
                   shading="flat", linewidth=0, antialiased=False)
ax.invert_yaxis()

# X axis: month labels at the first day of each month
month_starts = [datetime(2001, m, 1).timetuple().tm_yday for m in range(1, 13)]
month_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
ax.set_xticks(month_starts)
ax.set_xticklabels(month_labels)

ax.set_yticks(range(grid.index.min(), grid.index.max() + 1))
ax.set_ylabel("Year")
ax.set_xlabel("Day of year")
ax.set_title("Average daily temperature — Munich", fontsize=16, pad=15)

cbar = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
cbar.set_label("Temp (°C)")

for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(length=0)

plt.tight_layout()
for ext in FORMATS:
    plt.savefig(HERE / f"munich_heatmap.{ext}", dpi=200, bbox_inches="tight")
    print(f"wrote munich_heatmap.{ext}")
plt.close()

# --------------------------------------------------------------------------
# Chart 2 — humidity vs temperature, coloured by season, seasonal means marked
# --------------------------------------------------------------------------
season_colors = {
    "Spring": "#11BB44",
    "Summer": "#FFBB00",
    "Autumn": "#EE4444",
    "Winter": "#4488FF",
}

fig, ax = plt.subplots(figsize=(10, 8))
for s in ["Spring", "Summer", "Autumn", "Winter"]:
    sub = df[df.season == s]
    ax.scatter(
        sub.temp_c, sub.humidity,
        s=10, alpha=0.15, color=season_colors[s], label=s, edgecolors="none",
    )

means = df.groupby("season").agg(temp=("temp_c", "mean"), hum=("humidity", "mean"))
for s, row in means.iterrows():
    ax.scatter(row.temp, row.hum, s=180, color=season_colors[s],
               edgecolors="black", linewidths=1.5, zorder=5)
    ax.plot(row.temp, row.hum, marker="+", color="black",
            markersize=18, mew=1.5, zorder=6)

ax.set_xlabel("Daily average temperature (°C)")
ax.set_ylabel("Daily average humidity (%)")
ax.set_title("A typical day in Munich", fontsize=16, pad=15)
ax.set_xlim(-25, 35)
ax.set_ylim(20, 105)
ax.grid(True, linestyle=":", alpha=0.4)

leg = ax.legend(loc="lower left", frameon=True, fontsize=11)
for handle in leg.legend_handles:
    handle.set_alpha(1)
    handle.set_sizes([80])

for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()
for ext in FORMATS:
    plt.savefig(HERE / f"munich_scatter.{ext}", dpi=200, bbox_inches="tight")
    print(f"wrote munich_scatter.{ext}")
plt.close()
