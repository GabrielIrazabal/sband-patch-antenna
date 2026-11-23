"""Thin board (1.524 mm) against the thick board (two bonded boards, 3.05 mm), for the cut corner and the dual feed.

All on the 60 mm board over the 100 mm metal face, HFSS, about 40,000-element mesh.
The thick designs and their HFSS runs are listed in sim/thick_design.json.

  python sim/thick_compare.py     ->  docs/thick_vs_thin.png, sim/results_hfss/thick_tables.md
"""
import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results_hfss")
F0, LO, HI = 2.425, 2.415, 2.435
HYBRID_LOSS = 0.4
THIN = {"B": "B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_mesh40k", "A": "A_L37.28_f5.80_er2.55_h1.52_Gm100_mesh40k"}


def table(path):
    rows = list(csv.reader(open(path)))
    return rows[0], [[float(v) for v in r] for r in rows[1:]]


def load(run, dual):
    d = os.path.join(RES, run)
    j = json.load(open(os.path.join(d, "summary.json")))
    hs, sp = table(os.path.join(d, "sparams.csv"))
    _, ff = table(os.path.join(d, "farfield_boresight.csv"))
    col = hs.index("dB(ActiveS(P1:1))") if dual else 1
    loss = HYBRID_LOSS if dual else 0.0
    hy = (j.get("hybrid_imbalance") or [{}])[0]
    return dict(
        j=j, f_s=[r[0] for r in sp], s11=[r[col] for r in sp], f_ff=[r[0] for r in ff], ar=[r[3] for r in ff],
        gain=[r[1] - loss for r in ff],
        s11_worst=j.get("active_s11_worst_in_band_dB", j["s11_worst_in_band_dB"]) if dual else j["s11_worst_in_band_dB"],
        bw=j["s11_10dB_band_MHz"],
        ar_worst=hy.get("axial_ratio_worst_in_band_dB") if dual else j["axial_ratio_worst_in_band_dB"],
        ar_ideal=j["axial_ratio_worst_in_band_dB"], ar_bw=j.get("axial_ratio_3dB_band_MHz"),
        g_lo=(hy.get("rhcp_gain_min_in_band_dBic", j["rhcp_gain_min_in_band_dBic"]) if dual else j["rhcp_gain_min_in_band_dBic"]) - loss,
        g_hi=j["rhcp_gain_max_in_band_dBic"] - loss, hp=min(j["hpbw_deg_phi0_phi90"]),
        eff=j["radiation_efficiency_at_f0"])


def row(label, r, height):
    arbw = "set by the coupler" if r["ar_bw"] is None else f"{r['ar_bw']:.0f} MHz"
    ok = r["s11_worst"] <= -10 and r["ar_worst"] <= 3 and r["g_lo"] >= 6.5 and r["hp"] >= 60
    return (f"| {label} | {height} | {r['s11_worst']:.1f} dB | {r['bw']:.0f} MHz | {r['ar_worst']:.2f} dB | {arbw} | "
            f"{r['g_lo']:.2f} to {r['g_hi']:.2f} dBic | {r['hp']:.0f} deg | {r['eff'] * 100:.0f} % | {'yes' if ok else 'no'} |")


S = "_er2.55_h1.52_Gm100_mesh40k"
THIN_STRESS = {   # the same cases on the thin boards, from the earlier runs
    "B": {"Dk 2.52 (-1.2 %)": "B_L37.52_f7.00_c3.50_er2.52_h1.52_Gm100_mesh40k",
          "Dk 2.58 (+1.2 %)": "B_L37.52_f7.00_c3.50_er2.58_h1.52_Gm100_mesh40k",
          "Patch 0.3 mm smaller": "B_L37.22_f7.00_c3.50" + S, "Patch 0.3 mm larger": "B_L37.82_f7.00_c3.50" + S},
    "A": {"Dk 2.52 (-1.2 %)": "A_L37.28_f5.80_er2.52_h1.52_Gm100_mesh40k",
          "Dk 2.58 (+1.2 %)": "A_L37.28_f5.80_er2.58_h1.52_Gm100_mesh40k",
          "Patch 0.3 mm smaller": "A_L36.98_f5.80" + S, "Patch 0.3 mm larger": "A_L37.58_f5.80" + S}}


def cell(run, dual):
    if not run or not os.path.exists(os.path.join(RES, run, "summary.json")):
        return "not run", ""
    r = load(run, dual)
    ok = r["s11_worst"] <= -10 and r["ar_worst"] <= 3 and r["g_lo"] >= 6.5
    return f"{r['s11_worst']:.1f} dB, {r['ar_worst']:.2f} dB, {r['g_lo']:.2f} to {r['g_hi']:.2f} dBic", "pass" if ok else "fail"


def stress_rows(T, key, dual):
    out = []
    for label, run in T.get("stress", {}).get(key, []):
        thin, thin_ok = cell(THIN_STRESS[key].get(label), dual)
        if label not in THIN_STRESS[key]:
            thin = "does not apply (one board)"
        thick, thick_ok = cell(run, dual)
        out.append(f"| {label} | {thin} | {thin_ok} | {thick} | {thick_ok} |")
    return out


def main():
    T = json.load(open(os.path.join(HERE, "thick_design.json")))
    thick = {}
    for v in T["boards"].values():
        thick["B" if v.get("cut") else "A"] = v["hfss_run"]
    names = {"B": "Cut corner", "A": "Dual feed"}
    data = {k: (load(THIN[k], k == "A"), load(thick[k], k == "A")) for k in "BA"}

    fig, ax = plt.subplots(2, 3, figsize=(15, 8.5))
    for i, k in enumerate("BA"):
        thin, thk = data[k]
        for r, lab, c in ((thin, "1.5 mm board", "C0"), (thk, "3 mm board (two bonded)", "C3")):
            ax[i][0].plot(r["f_s"], r["s11"], c, lw=2, label=lab)
            ax[i][1].plot(r["f_ff"], r["ar"], c, lw=2, label=lab + (", perfect coupler" if k == "A" else ""))
            ax[i][2].plot(r["f_ff"], r["gain"], c, lw=2, label=lab)
            if k == "A":
                ax[i][1].plot([LO, HI], [r["ar_worst"]] * 2, c, lw=2.5, ls=":", label=lab + ", typical coupler")
        ax[i][0].axhline(-10, ls="--", c="k", lw=0.8)
        ax[i][1].axhline(3, ls="--", c="k", lw=0.8)
        ax[i][2].axhline(6.5, ls="--", c="k", lw=0.8)
        ax[i][0].set(title=f"{names[k]}: match (need -10 dB or lower)", ylabel="S11 (dB)", xlim=(2.3, 2.55), ylim=(-35, 0))
        ax[i][1].set(title=f"{names[k]}: axial ratio (need 3 dB or lower)", ylabel="Axial ratio (dB)", xlim=(2.37, 2.48), ylim=(0, 8))
        ax[i][2].set(title=f"{names[k]}: RHCP gain (need 6.5 dBic or more)"
                           + (f"\nafter {HYBRID_LOSS} dB coupler loss" if k == "A" else ""),
                     ylabel="RHCP gain (dBic)", xlim=(2.37, 2.48), ylim=(5, 9))
        for a in ax[i]:
            a.axvspan(LO, HI, color="0.85")
            a.grid(alpha=0.3)
            a.set_xlabel("Frequency (GHz)")
            a.legend(fontsize=8)
    fig.suptitle("Thin board against the 3 mm board (two 1.524 mm PTFE boards bonded, no air gap)\n"
                 "HFSS, 60 mm board on a 100 mm metal face; grey band = the 2.415 to 2.435 GHz channel", fontsize=12)
    fig.tight_layout()
    out_png = os.path.join(HERE, "..", "docs", "thick_vs_thin.png")
    fig.savefig(out_png, dpi=130)

    md = ["| Antenna | Height | Worst S11 | Match window | Worst axial ratio | 3 dB AR window | RHCP gain in channel | Beamwidth | Efficiency | Meets all four |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k in "BA":
        md.append(row(names[k] + ", thin", data[k][0], "1.5 mm"))
        md.append(row(names[k] + ", 3 mm", data[k][1], "3.0 mm"))
    for k in "BA":
        sr = stress_rows(T, k, k == "A")
        if sr:
            md += ["", f"Stress tests, {names[k].lower()}:", "",
                   "Each cell is worst S11, worst axial ratio, RHCP gain in the channel.", "",
                   "| Case | Thin board | | 3 mm board | |", "| --- | --- | --- | --- | --- |"] + sr
    text = "\n".join(md)
    with open(os.path.join(RES, "thick_tables.md"), "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
