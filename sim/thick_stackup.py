"""Cross-section sketch of the 3 mm board (two bonded 1.524 mm boards). Not to scale vertically.

  python sim/thick_stackup.py     ->  docs/thick_stackup.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    fig, a = plt.subplots(figsize=(10, 4.2))
    cu, ptfe = "#c8782a", "#e9e4d4"
    a.add_patch(Rectangle((0, 0), 60, 1.5, fc=ptfe, ec="k", lw=0.8))            # bottom board
    a.add_patch(Rectangle((0, 1.62), 60, 1.5, fc=ptfe, ec="k", lw=0.8))         # top board
    a.add_patch(Rectangle((0, 1.5), 60, 0.12, fc="#7fb2e5", ec="none"))         # bond line
    a.add_patch(Rectangle((0, -0.14), 60, 0.14, fc=cu, ec="none"))              # ground
    a.add_patch(Rectangle((11.5, 3.12), 37, 0.14, fc=cu, ec="none"))            # patch
    a.add_patch(Rectangle((37.6, -0.3), 0.8, 3.75, fc="#555", ec="none"))       # feed wire
    a.add_patch(Rectangle((34.5, -2.6), 7, 2.3, fc="#d9c36a", ec="k", lw=0.8))  # SMA
    a.add_patch(Rectangle((36.6, -4.6), 2.8, 2.0, fc="#d9c36a", ec="k", lw=0.8))
    notes = [((22, 3.26), (14, 5.2), "patch copper (front of the TOP board)"),
             ((6, 2.4), (-2, 4.2), "TOP board, 1.524 mm PTFE, no copper on its back"),
             ((52, 1.56), (63, 2.6), "bond line: no copper, no air"),
             ((8, 0.7), (-2, -1.6), "BOTTOM board, 1.524 mm PTFE, no copper on its front"),
             ((52, -0.07), (63, -1.2), "ground copper (back of the BOTTOM board)"),
             ((38, 2.0), (63, 4.3), "0.5 mm feed wire, soldered at both ends"),
             ((41.5, -1.5), (63, -3.4), "surface-mount SMA")]
    for xy, xt, text in notes:
        a.annotate(text, xy=xy, xytext=xt, fontsize=9, ha="left",
                   arrowprops=dict(arrowstyle="-", lw=0.7), va="center")
    a.set(xlim=(-4, 104), ylim=(-5.2, 5.9))
    a.set_title("3 mm patch board: two 1.524 mm boards bonded, one patch (cross-section, height not to scale)", fontsize=11)
    a.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, "..", "docs", "thick_stackup.png"), dpi=130)


if __name__ == "__main__":
    main()
