"""
Munich, faceted by year — 'A typical day' small-multiples in the style of
zonination/weather-intl, but 21 years of Munich instead of 24 cities.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.rcParams["svg.fonttype"] = "none"
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.stats import gaussian_kde

HERE = Path(__file__).parent
RAW = HERE / "munich_raw.csv"
FORMATS = ["png", "svg", "pdf"]

df = pd.read_csv(RAW, skiprows=2)
df.columns = ["date", "temp_c", "humidity", "cloud_cover",
              "precip_mm", "pressure_hpa", "wind_kmh"]
df["date"] = pd.to_datetime(df["date"])
df["year"] = df["date"].dt.year

def season(m):
    if m in (3, 4, 5):   return "Spring"
    if m in (6, 7, 8):   return "Summer"
    if m in (9, 10, 11): return "Autumn"
    return "Winter"
df["season"] = df["date"].dt.month.map(season)

years = sorted(df["year"].unique())
season_colors = {"Spring": "#11BB44", "Summer": "#FFBB00",
                 "Autumn": "#EE4444", "Winter": "#4488FF"}

# Global axis limits so every panel is comparable
XLIM = (-20, 35)
YLIM = (25, 105)

ncols = 4
nrows = int(np.ceil(len(years) / ncols))

fig, axes = plt.subplots(
    nrows, ncols,
    figsize=(ncols * 4.2, nrows * 3.6),
    sharex=True, sharey=True,
)
fig.patch.set_facecolor("#EAEAEA")
fig.patch.set_gid("page-bg")

# Grid for KDE contours
xx, yy = np.meshgrid(np.linspace(*XLIM, 120), np.linspace(*YLIM, 120))
grid_pts = np.vstack([xx.ravel(), yy.ravel()])

for idx, ax in enumerate(axes.flat):
    if idx >= len(years):
        ax.set_visible(False)
        continue

    yr = years[idx]
    sub = df[df.year == yr]

    ax.set_facecolor("#FBFBFB")
    ax.patch.set_gid("panel-bg")
    ax.grid(True, color="white", linewidth=1.2)
    ax.set_axisbelow(True)
    for gl in ax.get_xgridlines() + ax.get_ygridlines():
        gl.set_gid("gridline")

    # Season-coloured scatter
    for s in ["Spring", "Summer", "Autumn", "Winter"]:
        pts = sub[sub.season == s]
        ax.scatter(pts.temp_c, pts.humidity, s=14, alpha=0.35,
                   color=season_colors[s], edgecolors="none")

    # Density contours over the whole year (matches geom_density2d)
    xy = np.vstack([sub.temp_c.values, sub.humidity.values])
    try:
        kde = gaussian_kde(xy)
        zz = kde(grid_pts).reshape(xx.shape)
        ax.contour(xx, yy, zz, levels=8, colors="black", linewidths=0.4, alpha=0.35)
    except Exception:
        pass

    # Seasonal means: filled dot + black outline + crosshair
    means = sub.groupby("season").agg(temp=("temp_c", "mean"),
                                      hum=("humidity", "mean"))
    for s, row in means.iterrows():
        sc = ax.scatter(row.temp, row.hum, s=140, color=season_colors[s],
                        edgecolors="black", linewidths=1.2, zorder=5)
        sc.set_gid("mean-outline")
        ln, = ax.plot(row.temp, row.hum, marker="+", color="black",
                      markersize=16, mew=1.2, zorder=6)
        ln.set_gid("mean-cross")

    # Title bar
    ax.set_title("")
    t = ax.text(0.5, 1.02, str(yr), transform=ax.transAxes,
                ha="center", va="bottom",
                fontsize=11, color="#333",
                bbox=dict(facecolor="#D8D8D8", edgecolor="none",
                          boxstyle="round,pad=0.4"))
    t.set_gid("title-label")

    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.tick_params(labelsize=8, length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

# Shared axis labels
fig.supxlabel("Daily Average Temperature (°C)", fontsize=13, y=0.03)
fig.supylabel("Daily Average Humidity (%)", fontsize=13, x=0.01)

# Suptitle
fig.suptitle("A Typical Day in Munich — by year",
             fontsize=20, y=0.995, color="#222")

# Legend
handles = [plt.Line2D([], [], marker="o", linestyle="",
                      color=season_colors[s], markersize=10, label=s)
           for s in ["Spring", "Summer", "Autumn", "Winter"]]
fig.legend(handles=handles, loc="center right", frameon=False,
           fontsize=12, bbox_to_anchor=(0.995, 0.5))

plt.subplots_adjust(left=0.06, right=0.94, top=0.94, bottom=0.06,
                    wspace=0.15, hspace=0.35)

for ext in FORMATS:
    plt.savefig(HERE / f"munich_by_year.{ext}",
                dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"wrote munich_by_year.{ext}")
plt.close()
