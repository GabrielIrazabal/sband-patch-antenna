"""Print a Markdown table of every HFSS result next to its openEMS twin.

  python sim/hfss_compare.py > table.md

Reads results_hfss/*/summary.json and, where a folder of the same name exists,
results_openems/*/summary.json.
"""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def load(tool, name):
    f = os.path.join(HERE, f"results_{tool}", name, "summary.json")
    return json.load(open(f)) if os.path.exists(f) else None


def fmt(r, key, spec="%.2f"):
    if r is None or r.get(key) is None:
        return "–"
    v = r[key]
    if isinstance(v, list):
        return "/".join("%.0f" % x for x in v)
    return spec % v if isinstance(v, (int, float)) else str(v)


def gain_range(r):
    if r is None:
        return "–"
    lo = r.get("rhcp_gain_min_in_band_dBic")
    hi = r.get("rhcp_gain_max_in_band_dBic", r.get("rhcp_gain_at_f0_dBic"))
    if lo is None:
        return "–"
    return f"{lo:.2f}–{hi:.2f}" if hi is not None else f"{lo:.2f}"


COLS = [
    ("Best match (GHz)", lambda r: fmt(r, "s11_min_freq_GHz", "%.4f")),
    ("Worst S11 in channel (dB)", lambda r: fmt(r, "s11_worst_in_band_dB", "%.1f")),
    ("−10 dB BW (MHz)", lambda r: fmt(r, "s11_10dB_band_MHz", "%.1f")),
    ("AR min (dB) at (GHz)", lambda r: f"{fmt(r, 'axial_ratio_min_dB')} @ {fmt(r, 'axial_ratio_min_freq_GHz', '%.4f')}"),
    ("Worst AR in channel (dB)", lambda r: fmt(r, "axial_ratio_worst_in_band_dB")),
    ("3 dB AR BW (MHz)", lambda r: fmt(r, "axial_ratio_3dB_band_MHz", "%.1f")),
    ("RHCP gain in channel (dBic)", gain_range),
    ("Total gain at f0 (dBi)", lambda r: fmt(r, "realized_gain_total_at_f0_dBi")),
    ("Directivity (dBi)", lambda r: fmt(r, "directivity_at_f0_dBi")),
    ("Efficiency", lambda r: fmt(r, "radiation_efficiency_at_f0", "%.2f")),
    ("HPBW φ0/φ90 (°)", lambda r: fmt(r, "hpbw_deg_phi0_phi90")),
    ("Hand", lambda r: fmt(r, "hand")),
]


def main():
    names = sorted(os.path.basename(os.path.dirname(f))
                   for f in glob.glob(os.path.join(HERE, "results_hfss", "*", "summary.json")))
    print("| Run | Tool | " + " | ".join(c for c, _ in COLS) + " | Mesh (tets / passes) |")
    print("|" + " --- |" * (len(COLS) + 3))
    for n in names:
        h, o = load("hfss", n), load("openems", n)
        mesh = f"{h.get('tetrahedra', '–')} / {h.get('adaptive_passes', '–')}"
        print(f"| `{n}` | HFSS | " + " | ".join(fn(h) for _, fn in COLS) + f" | {mesh} |")
        if o:
            plain = n.startswith("plain") or n.startswith("A")
            cells = [fn(o) for _, fn in COLS]
            if plain:  # openEMS reports board A through an ideal hybrid: its AR columns are not comparable
                pass
            print("| | openEMS | " + " | ".join(cells) + " | |")


if __name__ == "__main__":
    main()
