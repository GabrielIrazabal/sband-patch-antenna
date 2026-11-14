"""Print one line per openEMS result folder (reads results_openems/*/summary.json)."""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
pat = sys.argv[1] if len(sys.argv) > 1 else "*"
keys = [("s11_min_freq_GHz", "f_S11min", "%.4f"), ("s11_worst_in_band_dB", "S11band", "%.1f"),
        ("s11_10dB_band_MHz", "BW10", "%s"), ("zin_r_peak_ohm", "Rpk", "%.0f"),
        ("isolation_s21_at_f0_dB", "iso", "%.1f"),
        ("axial_ratio_min_dB", "ARmin", "%.2f"), ("axial_ratio_min_freq_GHz", "f_AR", "%.4f"),
        ("axial_ratio_worst_in_band_dB", "ARband", "%.2f"), ("axial_ratio_3dB_band_MHz", "ARbw", "%s"),
        ("rhcp_gain_at_f0_dBic", "GR_f0", "%.2f"), ("rhcp_gain_min_in_band_dBic", "GRmin", "%.2f"),
        ("realized_gain_total_at_f0_dBi", "Gtot", "%.2f"), ("directivity_at_f0_dBi", "D", "%.2f"),
        ("radiation_efficiency_at_f0", "eff", "%.3f"), ("hpbw_deg_phi0_phi90", "HPBW", "%s"),
        ("hand", "hand", "%s"), ("hand_time_domain_check", "handTD", "%s")]
for d in sorted(glob.glob(os.path.join(HERE, "results_openems", pat))):
    f = os.path.join(d, "summary.json")
    if not os.path.exists(f):
        continue
    r = json.load(open(f))
    print(os.path.basename(d))
    print("   " + "  ".join(f"{lab}={fmt % r[k]}" for k, lab, fmt in keys if r.get(k) is not None))
