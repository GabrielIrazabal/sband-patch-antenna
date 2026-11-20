"""Tables and plots for the three-antenna comparison, the stacked-patch stress tests and the board-size sweep.

Reads sim/results_hfss/*_mesh40k/summary.json (written by hfss_patch.py through hfss_batch.py) and writes
  sim/results_hfss/compare_three.png      S11, axial ratio, gain and pattern of the three tuned antennas
  sim/results_hfss/size_sweep_face.png    board size 45-100 mm on the 100 mm metal face
  sim/results_hfss/size_sweep_bare.png    board size 50-100 mm with no metal behind (ground = board)
  sim/results_hfss/sweep_tables.md        the same numbers as markdown tables

  python sim/sweep_report.py
"""
import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results_hfss")
S = json.load(open(os.path.join(HERE, "stacked_design.json")))
_dp = os.path.join(HERE, "stacked_dual_design.json")
D = json.load(open(_dp)) if os.path.exists(_dp) else None
HYBRID_LOSS = 0.4   # dB, middle of the 0.3-0.5 dB a real 90 degree hybrid loses
F0, LO, HI = 2.425, 2.415, 2.435

PRE = {
    "B": "B_L37.52_f7.00_c3.50_er2.55_h1.52",
    "A": "A_L37.28_f5.80_er2.55_h1.52",
    "S": (f"S_L{S['L']:.2f}_f{S['feed']:.2f}_c{S['cut']:.2f}_fy{S['feed_y']:.2f}_U{S['L2']:.2f}_uc{S['cut2']:.2f}"
          f"_g{S['gap']:.2f}_er2.55_h1.52"),
}
LABEL = {"B": "Cut corner", "A": "Dual feed", "S": "Stacked cut corner", "D": "Stacked dual feed"}
COLOR = {"B": "#1f77b4", "A": "#d62728", "S": "#2ca02c", "D": "#9467bd"}
SIZES = [50, 60, 70, 80, 90, 100]
KEYS = "BAS"
if D:
    PRE["D"] = f"SD_L{D['L']:.2f}_f{D['feed']:.2f}_U{D['L2']:.2f}_uc0.00_g{D['gap']:.2f}_er2.55_h1.52"
    KEYS = "BASD"
DUAL = ("A", "D")


def folder(k, G, bare=False):
    if bare:
        return f"{PRE[k]}_bareG{G}_mesh40k" if G < 100 else f"{PRE[k]}_G100_mesh40k"
    if G == 60:
        return f"{PRE[k]}_Gm100_mesh40k"
    return f"{PRE[k]}{'_Gm100' if G < 100 else ''}_G{G}_mesh40k"


def load(name):
    p = os.path.join(RES, name, "summary.json")
    return json.load(open(p)) if os.path.exists(p) else None


def curves(name):
    d = os.path.join(RES, name)
    sp = list(csv.reader(open(os.path.join(d, "sparams.csv"))))
    ff = list(csv.reader(open(os.path.join(d, "farfield_boresight.csv"))))
    pt = list(csv.reader(open(os.path.join(d, "pattern_f0.csv"))))
    col = sp[0].index("dB(ActiveS(P1:1))") if "dB(ActiveS(P1:1))" in sp[0] else 1
    return dict(f=[float(r[0]) for r in sp[1:]], s11=[float(r[col]) for r in sp[1:]],
                ff=[float(r[0]) for r in ff[1:]], g=[float(r[1]) for r in ff[1:]], ar=[float(r[3]) for r in ff[1:]],
                th=[float(r[0]) for r in pt[1:]], p0=[float(r[1]) for r in pt[1:]], p90=[float(r[3]) for r in pt[1:]])


def metrics(k, j):
    """One row of comparable numbers. Dual feed: typical hybrid (0.5 dB / 3 deg) and its loss are included."""
    if j is None:
        return None
    m = dict(s11=j.get("active_s11_worst_in_band_dB", j["s11_worst_in_band_dB"]), bw=j["s11_10dB_band_MHz"],
             ar=j["axial_ratio_worst_in_band_dB"], ar_min=j["axial_ratio_min_dB"], ar_f=j["axial_ratio_min_freq_GHz"],
             ar_bw=j["axial_ratio_3dB_band_MHz"], g_lo=j["rhcp_gain_min_in_band_dBic"], g_hi=j["rhcp_gain_max_in_band_dBic"],
             eff=j["radiation_efficiency_at_f0"], dir=j["directivity_at_f0_dBi"], hp=min(j["hpbw_deg_phi0_phi90"]),
             f_s11=j["s11_min_freq_GHz"], tets=j.get("tetrahedra"))
    if k in DUAL:
        hy = j.get("hybrid_imbalance") or []
        if hy:
            m["ar"] = hy[0]["axial_ratio_worst_in_band_dB"]
            m["g_lo"] = round(hy[0]["rhcp_gain_min_in_band_dBic"] - HYBRID_LOSS, 2)
        else:
            m["g_lo"] = round(m["g_lo"] - HYBRID_LOSS, 2)
        m["g_hi"] = round(m["g_hi"] - HYBRID_LOSS, 2)
    return m


def fmt(v, nd=2):
    return "n/a" if v is None else (f"{v:.{nd}f}" if isinstance(v, float) else str(v))


def passes(m):
    return m["s11"] <= -10 and m["ar"] <= 3 and m["g_lo"] >= 6.5 and m["hp"] >= 60


def compare_plot():
    fig, ax = plt.subplots(2, 2, figsize=(14, 9.5))
    for k in KEYS:
        c = curves(folder(k, 60))
        lab = LABEL[k]
        ax[0, 0].plot(c["f"], c["s11"], color=COLOR[k], label=lab)
        ax[0, 1].plot(c["ff"], c["ar"], color=COLOR[k], label=lab + (" (perfect coupler)" if k in DUAL else ""))
        g = [v - (HYBRID_LOSS if k in DUAL else 0) for v in c["g"]]
        ax[1, 0].plot(c["ff"], g, color=COLOR[k], label=lab + (f" (after {HYBRID_LOSS} dB coupler loss)" if k in DUAL else ""))
        ax[1, 1].plot(c["th"], [v - (HYBRID_LOSS if k in DUAL else 0) for v in c["p0"]], color=COLOR[k], label=lab)
    for a in (ax[0, 0], ax[0, 1], ax[1, 0]):
        a.axvspan(LO, HI, color="k", alpha=0.08)
        a.set_xlabel("Frequency (GHz)")
        a.grid(alpha=0.3)
    ax[0, 0].axhline(-10, ls="--", c="k", lw=0.8)
    ax[0, 0].set(title="Match (S11). Lower is better; need -10 dB or lower in the grey channel", ylabel="dB",
                 xlim=(2.25, 2.60), ylim=(-35, 0))
    ax[0, 1].axhline(3, ls="--", c="k", lw=0.8)
    ax[0, 1].set(title="Axial ratio straight ahead. Lower is better; need 3 dB or lower", ylabel="dB",
                 xlim=(2.36, 2.49), ylim=(0, 10))
    ax[1, 0].axhline(6.5, ls="--", c="k", lw=0.8)
    ax[1, 0].set(title="RHCP gain straight ahead. Higher is better; need 6.5 dBic or more", ylabel="dBic",
                 xlim=(2.36, 2.49), ylim=(4, 9.5))
    ax[1, 1].set(title="RHCP gain against angle at 2.425 GHz", xlabel="Angle off the patch's axis (deg)", ylabel="dBic",
                 xlim=(-90, 90), ylim=(-10, 10))
    ax[1, 1].grid(alpha=0.3)
    for a in ax.flat:
        a.legend(fontsize=9)
    fig.suptitle("Four tuned antennas on the 100 mm metal face (HFSS, about 40,000-element mesh)", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "compare_three.png"), dpi=120)
    plt.close(fig)


def sweep(bare):
    data = {k: {} for k in KEYS}
    for k in KEYS:
        for G in SIZES:
            m = metrics(k, load(folder(k, G, bare)))
            if m:
                data[k][G] = m
    return data


def sweep_plot(data, bare, path):
    panels = [("g_lo", "Lowest RHCP gain in the channel (dBic)", 6.5, "higher is better"),
              ("ar", "Worst axial ratio in the channel (dB)", 3.0, "lower is better"),
              ("s11", "Worst S11 in the channel (dB)", -10.0, "lower is better"),
              ("ar_f", "Frequency of best axial ratio (GHz), cut-corner designs", F0, "should stay at 2.425"),
              ("dir", "Directivity at 2.425 GHz (dBi)", None, ""),
              ("hp", "Half-power beamwidth, narrower cut (deg)", 60.0, "need 60 or wider")]
    fig, ax = plt.subplots(2, 3, figsize=(17, 9))
    for a, (key, title, line, note) in zip(ax.flat, panels):
        for k in KEYS:
            gs = sorted(data[k])
            if key == "ar_f" and k in ("A", "SD"):
                continue        # a dual feed's axial ratio is flat, so its "best" frequency means nothing
            if gs:
                a.plot(gs, [data[k][g][key] for g in gs], "o-", color=COLOR[k], label=LABEL[k])
        if line is not None:
            a.axhline(line, ls="--", c="k", lw=0.8)
        a.set(title=title + (f"\n({note})" if note else ""), xlabel="Board side (mm)")
        a.grid(alpha=0.3)
        a.legend(fontsize=9)
    where = "no metal behind the board (ground plane = board size)" if bare else "board on the 100 mm metal face"
    fig.suptitle(f"Board size sweep, patch dimensions unchanged: {where}", fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def sweep_table(data, title):
    out = [f"### {title}", ""]
    for k in KEYS:
        if not data[k]:
            continue
        out += [f"**{LABEL[k]}**" + (" (typical coupler, 0.4 dB coupler loss included)" if k in DUAL else ""), "",
                "| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |",
                "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for G in sorted(data[k]):
            m = data[k][G]
            out.append(f"| {G} mm | {fmt(m['s11'], 1)} dB | {fmt(m['ar'])} dB | {fmt(m['ar_min'])} dB at {m['ar_f']:.4f} GHz | "
                       f"{fmt(m['ar_bw'], 1)} MHz | {fmt(m['g_lo'])} to {fmt(m['g_hi'])} dBic | {fmt(m['dir'])} dBi | "
                       f"{m['eff'] * 100:.0f} % | {m['hp']:.0f} deg | {'yes' if passes(m) else 'no'} |")
        out.append("")
    return out


def stress_table():
    base = PRE["S"]
    d = dict(S)
    cases = [("Nominal", f"{base}_Gm100"),
             ("Board Dk 2.52 (-1.2 %)", base.replace("er2.55", "er2.52") + "_Gm100"),
             ("Board Dk 2.58 (+1.2 %)", base.replace("er2.55", "er2.58") + "_Gm100"),
             ("Both patches 0.3 mm small", base.replace(f"L{d['L']:.2f}", f"L{d['L'] - 0.3:.2f}").replace(f"U{d['L2']:.2f}", f"U{d['L2'] - 0.3:.2f}") + "_Gm100"),
             ("Both patches 0.3 mm large", base.replace(f"L{d['L']:.2f}", f"L{d['L'] + 0.3:.2f}").replace(f"U{d['L2']:.2f}", f"U{d['L2'] + 0.3:.2f}") + "_Gm100"),
             ("Air gap 4.8 mm (-0.2)", base.replace(f"g{d['gap']:.2f}", f"g{d['gap'] - 0.2:.2f}") + "_Gm100"),
             ("Air gap 5.2 mm (+0.2)", base.replace(f"g{d['gap']:.2f}", f"g{d['gap'] + 0.2:.2f}") + "_Gm100"),
             ("Upper board 0.5 mm off in x and y", f"{base}_Gm100_shift0.5"),
             ("SMA connector modelled", f"{base}_Gm100_sma"),
             ("Solder mask around the lower patch", f"{base}_Gm100_mask"),
             ("Metal box behind, not a flat plate", f"{base}_Gm100_box"),
             ("Lossless copper", f"{base}_Gm100_pec"),
             ("Four nylon spacers in the gap", f"{base}_Gm100_nylon"),
             ("Four steel screws and metal standoffs", f"{base}_Gm100_steel")]
    out = ["| Case | Worst S11 | Best axial ratio | Worst axial ratio in channel | 3 dB AR window | RHCP gain in channel | All pass |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    for label, name in cases:
        m = metrics("S", load(name + "_mesh40k"))
        if not m:
            out.append(f"| {label} | not run | | | | | |")
            continue
        out.append(f"| {label} | {fmt(m['s11'], 1)} dB | {fmt(m['ar_min'])} dB at {m['ar_f']:.4f} GHz | {fmt(m['ar'])} dB | "
                   f"{fmt(m['ar_bw'], 1)} MHz | {fmt(m['g_lo'])} to {fmt(m['g_hi'])} dBic | {'yes' if passes(m) else 'no'} |")
    return out


def main():
    out = ["## Four tuned antennas, 60 mm board on the 100 mm face", "",
           "| | " + " | ".join(LABEL[k] for k in KEYS) + " | Requirement |", "| --- |" + " --- |" * (len(KEYS) + 1)]
    ms = {k: metrics(k, load(folder(k, 60))) for k in KEYS}
    rows = [("Worst S11 in the channel", "s11", "dB", 1, "-10 dB or lower"), ("-10 dB match window", "bw", "MHz", 0, "covers the channel"),
            ("Worst axial ratio in the channel", "ar", "dB", 2, "3 dB or lower"), ("3 dB axial-ratio window", "ar_bw", "MHz", 1, "20 MHz or more"),
            ("Lowest RHCP gain in the channel", "g_lo", "dBic", 2, "6.5 dBic or more"), ("Highest RHCP gain in the channel", "g_hi", "dBic", 2, ""),
            ("Directivity", "dir", "dBi", 2, ""), ("Half-power beamwidth", "hp", "deg", 0, "60 deg or wider"), ("Mesh elements", "tets", "", 0, "")]
    for label, key, unit, nd, req in rows:
        out.append(f"| {label} | " + " | ".join(f"{fmt(float(ms[k][key]), nd) if ms[k][key] is not None else 'n/a'} {unit}" for k in KEYS) + f" | {req} |")
    out += ["", "## Stacked patch stress tests", ""] + stress_table() + [""]
    compare_plot()
    for bare, title, png in ((False, "On the 100 mm metal face", "size_sweep_face.png"),
                             (True, "No metal behind the board (ground plane = board)", "size_sweep_bare.png")):
        data = sweep(bare)
        if any(len(v) > 1 for v in data.values()):
            sweep_plot(data, bare, os.path.join(RES, png))
        out += sweep_table(data, title)
    with open(os.path.join(RES, "sweep_tables.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
