"""One four-plot sheet per stacked antenna, from the HFSS results already in results_hfss/.

  python sim/stacked_sheets.py      ->  docs/stacked_cut_corner_results.png, docs/stacked_dual_feed_results.png
"""
import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results_hfss")
DOCS = os.path.join(HERE, "..", "docs")
F0, LO, HI = 2.425, 2.415, 2.435
HYBRID_LOSS = 0.4

SHEETS = [
    ("S_L36.26_f15.96_c6.56_fy3.07_U42.97_uc7.80_g5.00_er2.55_h1.52_Gm100_mesh40k", "Stacked cut corner",
     "stacked_cut_corner_results.png", False),
    ("SD_L35.04_f13.35_U41.51_uc0.00_g5.00_er2.55_h1.52_Gm100_mesh40k", "Stacked dual feed",
     "stacked_dual_feed_results.png", True),
]


def table(path):
    rows = list(csv.reader(open(path)))
    return rows[0], [[float(v) for v in r] for r in rows[1:]]


def sheet(name, label, out, dual):
    d = os.path.join(RES, name)
    j = json.load(open(os.path.join(d, "summary.json")))
    hs, sp = table(os.path.join(d, "sparams.csv"))
    _, ff = table(os.path.join(d, "farfield_boresight.csv"))
    _, pt = table(os.path.join(d, "pattern_f0.csv"))
    col = hs.index("dB(ActiveS(P1:1))") if dual else 1
    loss = HYBRID_LOSS if dual else 0.0
    hy = (j.get("hybrid_imbalance") or [{}])[0]

    fig, ax = plt.subplots(2, 2, figsize=(13, 9))
    a = ax[0, 0]
    a.plot([r[0] for r in sp], [r[col] for r in sp], color="C0", lw=2)
    a.axhline(-10, ls="--", c="k", lw=0.8)
    a.axvspan(LO, HI, color="0.85")
    worst = j.get("active_s11_worst_in_band_dB", j["s11_worst_in_band_dB"])
    a.set(title=f"1. Match (S11). Need -10 dB or lower in the grey channel\n"
                f"worst in channel {worst:.1f} dB, -10 dB window {j['s11_10dB_band_MHz']:.0f} MHz",
          xlabel="Frequency (GHz)", ylabel="dB", xlim=(2.25, 2.6), ylim=(-35, 0))

    a = ax[0, 1]
    a.plot([r[0] for r in ff], [r[3] for r in ff], color="C0", lw=2, label="perfect coupler" if dual else None)
    a.axhline(3, ls="--", c="k", lw=0.8)
    a.axvspan(LO, HI, color="0.85")
    if dual:
        v = hy.get("axial_ratio_worst_in_band_dB")
        a.plot([LO, HI], [v, v], color="C3", lw=2.5, label="typical coupler (0.5 dB, 3 deg off), worst case")
        a.legend(fontsize=9)
        note = f"worst in channel {j['axial_ratio_worst_in_band_dB']:.2f} dB (perfect coupler), {v:.2f} dB (typical)"
    else:
        note = (f"worst in channel {j['axial_ratio_worst_in_band_dB']:.2f} dB, "
                f"3 dB window {j['axial_ratio_3dB_band_MHz']:.0f} MHz")
    a.set(title="2. Axial ratio straight ahead. Need 3 dB or lower\n" + note,
          xlabel="Frequency (GHz)", ylabel="dB", xlim=(2.36, 2.49), ylim=(0, 8))

    a = ax[1, 0]
    a.plot([r[0] for r in ff], [r[1] - loss for r in ff], color="C0", lw=2)
    a.axhline(6.5, ls="--", c="k", lw=0.8)
    a.axvspan(LO, HI, color="0.85")
    g_lo = (hy.get("rhcp_gain_min_in_band_dBic", j["rhcp_gain_min_in_band_dBic"]) if dual
            else j["rhcp_gain_min_in_band_dBic"]) - loss
    g_hi = j["rhcp_gain_max_in_band_dBic"] - loss
    a.set(title="3. RHCP gain straight ahead. Need 6.5 dBic or more\n"
                f"{g_lo:.2f} to {g_hi:.2f} dBic in channel" + (f" (after {HYBRID_LOSS} dB coupler loss)" if dual else ""),
          xlabel="Frequency (GHz)", ylabel="dBic", xlim=(2.36, 2.49), ylim=(6, 9))

    a = ax[1, 1]
    a.plot([r[0] for r in pt], [r[1] - loss for r in pt], color="C0", lw=2, label="horizontal cut")
    a.plot([r[0] for r in pt], [r[3] - loss for r in pt], color="C1", lw=2, ls="--", label="vertical cut")
    hp = j["hpbw_deg_phi0_phi90"]
    a.legend(fontsize=9)
    a.set(title="4. Gain against angle, 2.425 GHz. Beam must be 60 deg or wider\n"
                f"half-power beamwidth {hp[0]:.0f} and {hp[1]:.0f} deg",
          xlabel="Angle off the patch's axis (deg)", ylabel="dBic", xlim=(-90, 90), ylim=(-10, 10))
    for a in ax.flat:
        a.grid(alpha=0.3)
    fig.suptitle(f"{label}: 60 mm board on the 100 mm metal face (HFSS, {j.get('tetrahedra')} mesh elements)",
                 fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(DOCS, out), dpi=120)
    plt.close(fig)
    print(out, round(worst, 1), round(g_lo, 2), round(g_hi, 2))


for s in SHEETS:
    sheet(*s)
