"""Dimensioned drawing of the stacked patch (top view and side view) from stacked_design.json.

  python sim/draw_stacked.py      # writes docs/stacked_patch_drawing.png
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle

HERE = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(HERE, "stacked_design.json")))
G, H, CU = 60.0, 1.524, 0.035


def cut_square(L, c):
    s = L / 2
    return [(-s + c, s), (s, s), (s, -s + c), (s - c, -s), (-s, -s), (-s, s - c)]


fig, (a, b) = plt.subplots(1, 2, figsize=(16, 7.6), gridspec_kw={"width_ratios": [1, 1.25]})

# ---- top view (seen from the front, x right, y up)
a.add_patch(Rectangle((-50, -50), 100, 100, fc="#d9d9d9", ec="#555", lw=1))
a.add_patch(Rectangle((-G / 2, -G / 2), G, G, fc="#f3ead2", ec="#555", lw=1))
a.add_patch(Polygon(cut_square(S["L2"], S["cut2"]), fc="#f4a261", ec="#9c4a12", lw=1.5, alpha=0.55))
a.add_patch(Polygon(cut_square(S["L"], S["cut"]), fc="#c96a1b", ec="#6b3207", lw=1.5, alpha=0.85))
a.add_patch(Circle((S["feed"], S["feed_y"]), 0.9, fc="k"))
a.plot([0], [0], "+", c="k", ms=10)
a.annotate(f"feed via\n{S['feed']:.2f} mm right, {S['feed_y']:.2f} mm up\nof the patch centre", (S["feed"], S["feed_y"]),
           (27, 30), fontsize=10, arrowprops=dict(arrowstyle="->"))
a.annotate(f"lower patch (fed)\n{S['L']:.2f} mm square\ncorner cuts {S['cut']:.2f} mm", (-6, -4), (-48, -46), fontsize=10,
           arrowprops=dict(arrowstyle="->"))
a.annotate(f"upper patch (not connected)\n{S['L2']:.2f} mm square\ncorner cuts {S['cut2']:.2f} mm", (-S["L2"] / 2 + 1.5, 12),
           (-49, 36), fontsize=10, arrowprops=dict(arrowstyle="->"))
a.text(0, -G / 2 - 3.5, "both boards 60 x 60 mm", ha="center", fontsize=10)
a.text(0, 46, "100 x 100 mm metal face", ha="center", fontsize=10)
a.text(-S["L2"] / 2 + 1, S["L2"] / 2 - 4.5, "cut", fontsize=8, rotation=45)
a.text(S["L2"] / 2 - 6, -S["L2"] / 2 + 1.5, "cut", fontsize=8, rotation=45)
a.set(xlim=(-52, 52), ylim=(-52, 52), aspect="equal", title="Top view, seen from in front of the antenna",
      xlabel="mm", ylabel="mm")

# ---- side view (vertical scale stretched 4x so the layers are visible)
K = 4.0
z1, z2 = H, H + S["gap"]
b.add_patch(Rectangle((-50, -1.2 * K), 100, 1.2 * K, fc="#bdbdbd", ec="#555"))
b.add_patch(Rectangle((-G / 2, 0), G, H * K, fc="#f3ead2", ec="#555"))
b.add_patch(Rectangle((-G / 2, z2 * K), G, H * K, fc="#f3ead2", ec="#555"))
b.plot([-G / 2, G / 2], [0, 0], c="#6b3207", lw=4, solid_capstyle="butt")
b.plot([-S["L"] / 2, S["L"] / 2], [z1 * K] * 2, c="#c96a1b", lw=4, solid_capstyle="butt")
b.plot([-S["L2"] / 2, S["L2"] / 2], [z2 * K] * 2, c="#f4a261", lw=4, solid_capstyle="butt")
b.plot([S["feed"]] * 2, [0, z1 * K], c="k", lw=2.5)
b.add_patch(Rectangle((S["feed"] - 3, -1.2 * K - 6), 6, 6, fc="#e0c040", ec="#555"))
b.text(S["feed"], -1.2 * K - 9, "SMA", ha="center", fontsize=9)
for x in (-26, 26):
    b.add_patch(Rectangle((x - 2.5, z1 * K), 5, S["gap"] * K, fc="#ffffff", ec="#888", hatch="//"))
b.text(-29.5, (z1 + S["gap"] / 2 - 1.2) * K, "spacer ", ha="right", va="center", fontsize=9)
lab = [(-49, -0.6 * K, "metal face"), (-49, H / 2 * K, "lower board"), (-49, (z2 + H / 2) * K, "upper board")]
for x, y, t in lab:
    b.text(x, y, t, va="center", fontsize=9)


def dim(x, y0, y1, text):
    b.annotate("", (x, y0 * K), (x, y1 * K), arrowprops=dict(arrowstyle="<->", lw=1))
    b.text(x + 1, (y0 + y1) / 2 * K, text, va="center", fontsize=10)


dim(36, 0, z1, f"{H} mm PTFE, Dk 2.55")
dim(36, z1, z2, f"{S['gap']:.1f} mm air")
dim(36, z2, z2 + H, f"{H} mm PTFE")
dim(-36, 0, z2 + H, "")
b.text(-37, (z2 + H) / 2 * K, f"{z2 + H:.2f} mm\ntotal", ha="right", va="center", fontsize=10)
b.annotate("lower patch, on top of the lower board", (-8, z1 * K), (-20, (z1 + 1.9) * K), fontsize=9,
           arrowprops=dict(arrowstyle="->"))
b.annotate("upper patch, on the underside of the upper board", (-10, z2 * K), (-34, (z2 + H + 1.2) * K), fontsize=9,
           arrowprops=dict(arrowstyle="->"))
b.annotate("feed via", (S["feed"], H / 2 * K), (2, -3.2 * K), fontsize=9, arrowprops=dict(arrowstyle="->"))
b.annotate("ground copper", (-20, 0), (-30, -3.2 * K), fontsize=9, arrowprops=dict(arrowstyle="->"))
b.set(xlim=(-66, 66), ylim=(-1.2 * K - 12, (z2 + H + 2.6) * K), title="Side view (heights drawn 4x taller than widths)",
      xlabel="mm")
b.set_yticks([])
fig.suptitle("Stacked patch antenna, 2.425 GHz RHCP (simulation design, not a manufacturing drawing)", fontsize=13, weight="bold")
fig.tight_layout()
out = os.path.join(HERE, "..", "docs", "stacked_patch_drawing.png")
fig.savefig(out, dpi=120, facecolor="white")
print("wrote", os.path.normpath(out))
