"""Tables for sim/HFSS_RERUN_RESULTS.md: one row per HFSS run of the rerun job (HFSS_RERUN.md).

Every figure is read from sim/results_hfss/<run>/ (summary.json, sparams.csv). Conventions, the same as
sim/RERUN_CHECK.md:
  - return loss, best-match frequency and match window: S11 for the cut corners; for the dual feeds the
    active reflection at J1 with J2 lagging by 90 degrees (what a coupler's input port sees)
  - lowest RHCP gain: for the dual feeds with a typical coupler (0.5 dB, 3 degrees off) minus 0.4 dB coupler loss
  - axial ratio: for the dual feeds with a perfect coupler

  python sim/rerun_report.py      ->  prints the tables and writes sim/results_hfss/rerun_tables.md
"""
import csv
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results_hfss")
LO, HI = 2.415, 2.435
HYBRID_LOSS = 0.4

ANT = {  # key: label, folder prefix, thickness part of the folder name, earlier HFSS run, openEMS figures
    "B15": ("Cut corner, 1.5 mm", "B_", "_h1.52_", "B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_mesh40k",
            dict(gain=6.80, rl=12.8, bw=64, ar=3.94, f=2.4500)),
    "A15": ("Dual feed, 1.5 mm", "A_", "_h1.52_", "A_L37.28_f5.80_er2.55_h1.52_Gm100_mesh40k",
            dict(gain=6.49, rl=11.0, bw=31, ar=0.07, f=2.4290)),
    "B30": ("Cut corner, 3 mm", "B_", "_h3.05_", "B_L37.10_f8.00_c5.55_fy2.18_er2.55_h3.05_Gm100_mesh40k",
            dict(gain=7.32, rl=13.4, bw=127, ar=2.07, f=2.3870)),
    "A30": ("Dual feed, 3 mm", "A_", "_h3.05_", "A_L36.39_f6.70_er2.55_h3.05_Gm100_mesh40k",
            dict(gain=7.06, rl=17.3, bw=57, ar=0.28, f=2.4260)),
}
# tag: (what the run is, thickness part override)
CASES = [
    ("rerun", "Rerun, nominal"),
    ("fine", "Finest mesh"),
    ("pad62", "Air box 62 mm (half a wavelength)"),
    ("pad62fine", "Air box 62 mm and finest mesh"),
    ("sma", "With the SMA (coax and wave port)"),
    ("mask", "With solder mask on the top"),
    ("joint", "0.09 mm of Dk 3.5 in the glue joint"),
    ("m40C", "-40 C (Dk 2.5676, sizes x 0.99907)"),
    ("p85C", "+85 C (Dk 2.5309, sizes x 1.00101)"),
]


def table(path):
    rows = list(csv.reader(open(path)))
    return rows[0], [[float(v) for v in r] for r in rows[1:]]


def crossing(f0, y0, f1, y1, level):
    return f0 + (level - y0) * (f1 - f0) / (y1 - y0)


def match(freqs, s):
    """Best-match frequency, worst value in the channel and the -10 dB window around the best match (MHz)."""
    i = min(range(len(s)), key=lambda k: s[k])
    worst = max(v for f, v in zip(freqs, s) if LO - 1e-9 <= f <= HI + 1e-9)
    lo = hi = None
    for k in range(i, 0, -1):
        if s[k - 1] > -10 >= s[k]:
            lo = crossing(freqs[k - 1], s[k - 1], freqs[k], s[k], -10)
            break
    for k in range(i, len(s) - 1):
        if s[k + 1] > -10 >= s[k]:
            hi = crossing(freqs[k], s[k], freqs[k + 1], s[k + 1], -10)
            break
    bw = (hi - lo) * 1e3 if lo and hi and s[i] <= -10 else 0.0
    return freqs[i], worst, bw, (lo, hi)


def find(key, tag):
    _, pre, thick, _, _ = ANT[key]
    hits = [d for d in glob.glob(os.path.join(RES, f"{pre}*_{tag}_mesh*")) if os.path.isfile(os.path.join(d, "summary.json"))]
    if tag == "joint":
        if key.endswith("15"):      # the joint only exists in the two-board (3 mm) antennas
            return None
        thick = "_h3.14_"
    hits = [d for d in hits if thick in os.path.basename(d)]
    return os.path.basename(hits[0]) if hits else None


def load(run, dual):
    d = os.path.join(RES, run)
    j = json.load(open(os.path.join(d, "summary.json")))
    hs, sp = table(os.path.join(d, "sparams.csv"))
    col = hs.index("dB(ActiveS(P1:1))") if dual else 1
    f_best, worst, bw, edges = match([r[0] for r in sp], [r[col] for r in sp])
    hy = (j.get("hybrid_imbalance") or [{}])[0]
    if dual:
        g_lo = hy["rhcp_gain_min_in_band_dBic"] - HYBRID_LOSS
        g_hi = j["rhcp_gain_max_in_band_dBic"] - HYBRID_LOSS
    else:
        g_lo, g_hi = j["rhcp_gain_min_in_band_dBic"], j["rhcp_gain_max_in_band_dBic"]
    return dict(run=run, f=f_best, rl=-worst, bw=bw, edges=edges, g_lo=g_lo, g_hi=g_hi,
                ar=j["axial_ratio_worst_in_band_dB"], ar_f=j["axial_ratio_min_freq_GHz"],
                ar_typ=hy.get("axial_ratio_worst_in_band_dB"), hp=min(j["hpbw_deg_phi0_phi90"]), hand=j["hand"],
                tets=j.get("tetrahedra"), eff=j["radiation_efficiency_at_f0"], dir=j["directivity_at_f0_dBi"],
                pad=j["options"].get("pad", 0.0), minutes=j.get("solve_minutes"))


def passes(r):
    return r["g_lo"] >= 6.5 and r["rl"] >= 10 and r["hp"] >= 60 and r["hand"] == "RHCP"


def fmt(r, base=None):
    d = ""
    if base:
        d = f" | {(r['f'] - base['f']) * 1e3:+.1f} MHz | {r['g_lo'] - base['g_lo']:+.2f} dB"
    return (f"{r['f']:.4f} GHz | {r['rl']:.1f} dB | {r['bw']:.0f} MHz | {r['g_lo']:.2f} to {r['g_hi']:.2f} dBic | "
            f"{r['ar']:.2f} dB | {r['hp']:.0f} deg | {r['hand']} | {r['tets']}{d} | {'pass' if passes(r) else 'FAIL'}")


def main():
    out = []
    base = {k: load(v[3], k.startswith("A")) for k, v in ANT.items()}

    out += ["### Part 1: the four at nominal, rerun against the earlier HFSS run and openEMS", "",
            "| Antenna | Run | Best match at | Worst return loss | Match window | Lowest RHCP gain | Worst axial ratio | Beamwidth | Hand |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for k, (label, _, _, _, oe) in ANT.items():
        b = base[k]
        out.append(f"| {label} | earlier HFSS | {b['f']:.4f} GHz | {b['rl']:.1f} dB | {b['bw']:.0f} MHz | {b['g_lo']:.2f} dBic | "
                   f"{b['ar']:.2f} dB | {b['hp']:.0f} deg | {b['hand']} |")
        run = find(k, "rerun")
        if run:
            r = load(run, k.startswith("A"))
            out.append(f"| | HFSS rerun | {r['f']:.4f} GHz | {r['rl']:.1f} dB | {r['bw']:.0f} MHz | {r['g_lo']:.2f} dBic | "
                       f"{r['ar']:.2f} dB | {r['hp']:.0f} deg | {r['hand']} |")
            out.append(f"| | rerun minus earlier | {(r['f'] - b['f']) * 1e3:+.1f} MHz | {r['rl'] - b['rl']:+.1f} dB | "
                       f"{r['bw'] - b['bw']:+.0f} MHz | {r['g_lo'] - b['g_lo']:+.2f} dB | {r['ar'] - b['ar']:+.2f} dB | "
                       f"{r['hp'] - b['hp']:+.0f} deg | |")
        out.append(f"| | openEMS, 24 Nov | {oe['f']:.4f} GHz | {oe['rl']:.1f} dB | {oe['bw']:.0f} MHz | {oe['gain']:.2f} dBic | "
                   f"{oe['ar']:.2f} dB | | RHCP |")
    out.append("")

    out += ["### Every run", "",
            "The last three columns compare each run with the rerun of the same antenna at nominal.", "",
            "| Antenna | Case | Best match at | Worst return loss | Match window | RHCP gain in channel | Worst axial ratio | "
            "Beamwidth | Hand | Mesh elements | Shift of best match | Change in lowest gain | Requirements |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    missing = []
    for k, (label, *_rest) in ANT.items():
        nominal = find(k, "rerun")
        ref = load(nominal, k.startswith("A")) if nominal else None
        for tag, what in CASES:
            run = find(k, tag)
            if not run:
                if not (tag in ("fine", "pad62fine") and k != "A15") and not (tag in ("sma", "mask", "joint") and k.endswith("15")):
                    missing.append(f"{label}: {what}")
                continue
            r = load(run, k.startswith("A"))
            if k.endswith("15") and tag in ("sma", "mask"):
                what += " (earlier run, 14 Nov)"
            out.append(f"| {label} | {what} | " + fmt(r, ref if tag != "rerun" and ref else None).replace(
                f"{r['tets']} | ", f"{r['tets']} | " if tag != "rerun" and ref else f"{r['tets']} | | | ") + " |")
    out.append("")
    if missing:
        out += ["Not run or failed: " + "; ".join(missing) + ".", ""]
    text = "\n".join(out)
    with open(os.path.join(RES, "rerun_tables.md"), "w", encoding="utf-8") as fh:
        fh.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
