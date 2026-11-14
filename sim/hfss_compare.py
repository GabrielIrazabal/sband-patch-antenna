"""Print a Markdown table of every HFSS result next to its openEMS twin.

  python sim/hfss_compare.py                 # every run
  python sim/hfss_compare.py mesh40k         # only folders whose name contains "mesh40k"

Reads results_hfss/*/summary.json and, where a folder of the same name exists
(ignoring a _mesh40k suffix), results_openems/*/summary.json.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DASH = "–"


def load(tool, name):
    f = os.path.join(HERE, f"results_{tool}", name, "summary.json")
    return json.load(open(f)) if os.path.exists(f) else None


def fmt(r, key, spec="%.2f"):
    if r is None or r.get(key) is None:
        return DASH
    v = r[key]
    if isinstance(v, list):
        return "/".join("%.0f" % x for x in v)
    return spec % v if isinstance(v, (int, float)) else str(v)


def gain_range(r):
    lo = r.get("rhcp_gain_min_in_band_dBic")
    hi = r.get("rhcp_gain_max_in_band_dBic", r.get("rhcp_gain_at_f0_dBic"))
    if lo is None:
        return DASH
    return f"{lo:.2f} to {hi:.2f}" if hi is not None else f"{lo:.2f}"


COLS = [
    ("Best match (GHz)", lambda r: fmt(r, "s11_min_freq_GHz", "%.4f")),
    ("Worst S11 in channel (dB)", lambda r: fmt(r, "s11_worst_in_band_dB", "%.1f")),
    ("-10 dB BW (MHz)", lambda r: fmt(r, "s11_10dB_band_MHz", "%.1f")),
    ("AR min (dB) at (GHz)", lambda r: f"{fmt(r, 'axial_ratio_min_dB')} @ {fmt(r, 'axial_ratio_min_freq_GHz', '%.4f')}"),
    ("Worst AR in channel (dB)", lambda r: fmt(r, "axial_ratio_worst_in_band_dB")),
    ("3 dB AR BW (MHz)", lambda r: fmt(r, "axial_ratio_3dB_band_MHz", "%.1f")),
    ("RHCP gain in channel (dBic)", gain_range),
    ("Total gain at f0 (dBi)", lambda r: fmt(r, "realized_gain_total_at_f0_dBi")),
    ("Directivity (dBi)", lambda r: fmt(r, "directivity_at_f0_dBi")),
    ("Efficiency", lambda r: fmt(r, "radiation_efficiency_at_f0", "%.2f")),
    ("HPBW phi0/phi90 (deg)", lambda r: fmt(r, "hpbw_deg_phi0_phi90")),
    ("Hand", lambda r: fmt(r, "hand")),
]


def main():
    pat = sys.argv[1] if len(sys.argv) > 1 else ""
    names = sorted(os.path.basename(os.path.dirname(f))
                   for f in glob.glob(os.path.join(HERE, "results_hfss", "*", "summary.json")))
    print("| Run | Tool | " + " | ".join(c for c, _ in COLS) + " | Mesh (tets / passes) |")
    print("|" + " --- |" * (len(COLS) + 3))
    for n in names:
        if pat not in n:
            continue
        h, o = load("hfss", n), load("openems", n.replace("_mesh40k", ""))
        mesh = f"{h.get('tetrahedra', DASH)} / {h.get('adaptive_passes', DASH)}"
        for tool, r, tail in (("HFSS", h, mesh), ("openEMS", o, "")):
            if r is None:
                continue
            cells = [fn(r) for _, fn in COLS]
            if n.startswith("plain"):   # linear patch: axial ratio and RHCP columns mean nothing
                cells[3:7] = ["n/a"] * 4
                cells[-1] = "linear"
            if n.startswith("A") and tool == "openEMS":   # openEMS board A assumes an ideal hybrid by symmetry
                cells[3:6] = ["ideal"] * 3
            print(f"| {'`' + n + '`' if tool == 'HFSS' else ''} | {tool} | " + " | ".join(cells) + f" | {tail} |")


if __name__ == "__main__":
    main()
