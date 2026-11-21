"""The four standard result plots for each tuned antenna, one PNG per plot, plus an index.

All on the 60 mm board over the 100 mm metal face, HFSS, about 40,000-element mesh.

  python sim/result_plots.py      ->  docs/results_60mm/<antenna>/1_s11.png, 2_axial_ratio.png, 3_gain.png, 4_pattern.png
                                      docs/results_60mm/README.md
"""
import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results_hfss")
OUT = os.path.join(HERE, "..", "docs", "results_60mm")
F0, LO, HI = 2.425, 2.415, 2.435
HYBRID_LOSS = 0.4

# folder, label, results_hfss run, dual feed?, height, extra parts
ANTENNAS = [
    ("cut_corner", "Cut corner", "B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_mesh40k", False, "1.5 mm", "none"),
    ("dual_feed", "Dual feed", "A_L37.28_f5.80_er2.55_h1.52_Gm100_mesh40k", True, "1.5 mm", "coupler, load, second line"),
    ("stacked_cut_corner_5mm_gap", "Stacked cut corner, 5 mm gap",
     "S_L36.26_f15.96_c6.56_fy3.07_U42.97_uc7.80_g5.00_er2.55_h1.52_Gm100_mesh40k", False, "8.0 mm", "second board, spacers"),
    ("stacked_cut_corner_3mm_gap", "Stacked cut corner, 3 mm gap",
     "S_L35.63_f15.68_c5.40_fy3.02_U42.23_uc6.42_g3.00_er2.55_h1.52_Gm100_mesh40k", False, "6.0 mm", "second board, spacers"),
    ("stacked_dual_feed", "Stacked dual feed, 5 mm gap",
     "SD_L35.04_f13.35_U41.51_uc0.00_g5.00_er2.55_h1.52_Gm100_mesh40k", True, "8.0 mm",
     "second board, spacers, coupler, load, second line"),
]


def table(path):
    rows = list(csv.reader(open(path)))
    return rows[0], [[float(v) for v in r] for r in rows[1:]]


def new_axes():
    fig, a = plt.subplots(figsize=(7.5, 5))
    a.grid(alpha=0.3)
    return fig, a


def save(fig, folder, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, folder, name), dpi=130)
    plt.close(fig)


def one(folder, label, run, dual, height, parts):
    d = os.path.join(RES, run)
    j = json.load(open(os.path.join(d, "summary.json")))
    hs, sp = table(os.path.join(d, "sparams.csv"))
    _, ff = table(os.path.join(d, "farfield_boresight.csv"))
    _, pt = table(os.path.join(d, "pattern_f0.csv"))
    os.makedirs(os.path.join(OUT, folder), exist_ok=True)
    col = hs.index("dB(ActiveS(P1:1))") if dual else 1
    loss = HYBRID_LOSS if dual else 0.0
    hy = (j.get("hybrid_imbalance") or [{}])[0]
    f_ff = [r[0] for r in ff]
    pad = 0.005
    xlim_ff = (min(f_ff) - pad, max(f_ff) + pad)

    s11 = j.get("active_s11_worst_in_band_dB", j["s11_worst_in_band_dB"])
    bw = j["s11_10dB_band_MHz"]
    ar = hy.get("axial_ratio_worst_in_band_dB") if dual else j["axial_ratio_worst_in_band_dB"]
    ar_ideal = j["axial_ratio_worst_in_band_dB"]
    ar_bw = j.get("axial_ratio_3dB_band_MHz")
    g_lo = (hy.get("rhcp_gain_min_in_band_dBic", j["rhcp_gain_min_in_band_dBic"]) if dual else j["rhcp_gain_min_in_band_dBic"]) - loss
    g_hi = j["rhcp_gain_max_in_band_dBic"] - loss
    hp = j["hpbw_deg_phi0_phi90"]

    fig, a = new_axes()
    a.plot([r[0] for r in sp], [r[col] for r in sp], color="C0", lw=2)
    a.axhline(-10, ls="--", c="k", lw=0.8)
    a.axvspan(LO, HI, color="0.85")
    a.set(title=f"{label}: match (S11)\nneed -10 dB or lower in the grey channel; worst {s11:.1f} dB, window {bw:.0f} MHz",
          xlabel="Frequency (GHz)", ylabel="S11 (dB)", xlim=(2.25, 2.6), ylim=(-35, 0))
    save(fig, folder, "1_s11.png")

    fig, a = new_axes()
    a.plot(f_ff, [r[3] for r in ff], color="C0", lw=2, label="perfect coupler" if dual else None)
    a.axhline(3, ls="--", c="k", lw=0.8)
    a.axvspan(LO, HI, color="0.85")
    if dual:
        a.plot([LO, HI], [ar, ar], color="C3", lw=2.5, label="typical coupler (0.5 dB, 3 deg off), worst case")
        a.legend(fontsize=9)
        note = f"worst {ar_ideal:.2f} dB with a perfect coupler, {ar:.2f} dB with a typical one"
    else:
        note = f"worst {ar:.2f} dB in the channel, 3 dB window {ar_bw:.0f} MHz"
    a.set(title=f"{label}: axial ratio straight ahead\nneed 3 dB or lower; {note}",
          xlabel="Frequency (GHz)", ylabel="Axial ratio (dB)", xlim=xlim_ff, ylim=(0, 8))
    save(fig, folder, "2_axial_ratio.png")

    fig, a = new_axes()
    a.plot(f_ff, [r[1] - loss for r in ff], color="C0", lw=2)
    a.axhline(6.5, ls="--", c="k", lw=0.8)
    a.axvspan(LO, HI, color="0.85")
    a.set(title=f"{label}: RHCP gain straight ahead\nneed 6.5 dBic or more; {g_lo:.2f} to {g_hi:.2f} dBic in the channel"
                + (f" (after {HYBRID_LOSS} dB coupler loss)" if dual else ""),
          xlabel="Frequency (GHz)", ylabel="RHCP gain (dBic)", xlim=xlim_ff, ylim=(5, 9))
    save(fig, folder, "3_gain.png")

    fig, a = new_axes()
    a.plot([r[0] for r in pt], [r[1] - loss for r in pt], color="C0", lw=2, label="horizontal cut")
    a.plot([r[0] for r in pt], [r[3] - loss for r in pt], color="C1", lw=2, ls="--", label="vertical cut")
    a.legend(fontsize=9)
    a.set(title=f"{label}: RHCP gain against angle at 2.425 GHz\nbeam must be 60 deg or wider; "
                f"half-power beamwidth {hp[0]:.0f} and {hp[1]:.0f} deg",
          xlabel="Angle off the patch's axis (deg)", ylabel="RHCP gain (dBic)", xlim=(-90, 90), ylim=(-10, 10))
    save(fig, folder, "4_pattern.png")

    ok = s11 <= -10 and ar <= 3 and g_lo >= 6.5 and min(hp) >= 60
    return dict(folder=folder, label=label, s11=s11, bw=bw, ar=ar, ar_bw=ar_bw, g_lo=g_lo, g_hi=g_hi, hp=min(hp),
                height=height, parts=parts, ok=ok, dual=dual, run=run)


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = [one(*a) for a in ANTENNAS]
    md = ["# Results on the 60 mm board", "",
          "Four plots for each tuned antenna, each in its own file. Ansys HFSS, about 40,000-element mesh, 60 mm "
          "square PTFE board (Dk 2.55, 1.524 mm) on a 100 mm metal face, 2.425 GHz, channel 2.415 to 2.435 GHz. "
          "Simulation only: nothing has been built or measured.", "",
          f"Dual-feed figures assume a typical 90 degree coupler (0.5 dB and 3 degrees off, {HYBRID_LOSS} dB loss).", "",
          "| Antenna | Worst S11 | Match window | Worst axial ratio | 3 dB AR window | RHCP gain in channel | Beamwidth | Height | Extra parts | Meets all four |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        arbw = "set by the coupler" if r["dual"] else f"{r['ar_bw']:.0f} MHz"
        md.append(f"| [{r['label']}]({r['folder']}/) | {r['s11']:.1f} dB | {r['bw']:.0f} MHz | {r['ar']:.2f} dB | {arbw} | "
                  f"{r['g_lo']:.2f} to {r['g_hi']:.2f} dBic | {r['hp']:.0f} deg | {r['height']} | {r['parts']} | "
                  f"{'yes' if r['ok'] else 'no'} |")
    md += ["", "Requirements: S11 -10 dB or lower, axial ratio 3 dB or lower, RHCP gain 6.5 dBic or more, beamwidth 60 "
           "degrees or wider, all across the channel.", ""]
    for r in rows:
        md += [f"## {r['label']}", "", f"HFSS run: `{r['run']}`", "",
               f"| Match | Axial ratio |", "| --- | --- |",
               f"| ![S11]({r['folder']}/1_s11.png) | ![Axial ratio]({r['folder']}/2_axial_ratio.png) |", "",
               f"| Gain | Pattern |", "| --- | --- |",
               f"| ![Gain]({r['folder']}/3_gain.png) | ![Pattern]({r['folder']}/4_pattern.png) |", ""]
    with open(os.path.join(OUT, "README.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    for r in rows:
        print(f"{r['label']:32s} S11 {r['s11']:6.1f}  AR {r['ar']:.2f}  gain {r['g_lo']:.2f}..{r['g_hi']:.2f}  HPBW {r['hp']:.0f}  ok={r['ok']}")


if __name__ == "__main__":
    main()
