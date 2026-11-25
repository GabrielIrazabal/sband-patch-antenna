"""Simulate the S-band patch with openEMS (free FDTD solver, runs on macOS/Linux).

Run with the Python that has openEMS installed, e.g.
  ~/opt/openEMS/venv/bin/python openems_patch.py --board plain
  ~/opt/openEMS/venv/bin/python openems_patch.py --board A --L 32.0 --feed 5.0
  ~/opt/openEMS/venv/bin/python openems_patch.py --board B --cut 2.6
  ~/opt/openEMS/venv/bin/python openems_patch.py --board B --er 3.62      # drift check

Boards
  plain  square patch, one probe on +x              (linear; sets patch size and feed position)
  A      square patch, probes on +x (J1) and +y (J2), combined with an ideal 90-degree hybrid
         in post-processing (J2 lags J1 by 90 deg -> RHCP)
  B      one probe on +x, corners at (-x,+y) and (+x,-y) truncated
         (= KiCad top-left / bottom-right in the top view)

Coordinates: ground at z=0, patch at z=h, radiates toward +z. x right, y up, seen from the front.
Polarization: IEEE, wave leaving the patch. Phasors use exp(+j w t), so RHCP toward +z is (x - j y).

Model simplifications (first-pass design accuracy, expect roughly +-1 % in frequency):
  - probe = 50-ohm lumped port on a single mesh edge line from ground to patch (thin wire)
  - copper = conducting-sheet model (5.8e7 S/m, 35 um), no solder mask, no ENIG, no connector body
  - 45-degree corner cuts are staircased by the rectangular mesh
  - free space around a bare 60 x 60 mm board (no satellite body)
"""
import argparse
import json
import os
import shutil
import sys
import time

import numpy as np

C0 = 299_792_458.0
EPS0 = 8.8541878128e-12
ETA0 = 376.730313668

DEFAULTS = dict(
    f0=2.425e9,    # Hz, design centre (placeholder until the carrier is confirmed)
    bw=20e6,       # Hz, signal bandwidth
    L=32.12,       # mm, patch side
    feed=3.46,     # mm, probe offset from centre
    feed_y=0.0,    # mm, sideways probe offset (+y); used by the 3 mm cut corner to cancel pin inductance
    cut=2.60,      # mm, corner-cut leg (board B)
    h=1.524,       # mm, RO4350B core
    G=60.0,        # mm, board / ground side
    er=3.66,       # RO4350B design Dk
    tand=0.0031,   # loss tangent near 2.5 GHz
    res=0.5,       # mm, mesh cell size across the patch
    pad=70.0,      # mm, air between board and the simulation boundary (includes the PML)
)

HERE = os.path.dirname(os.path.abspath(__file__))


def parse():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--board", choices=["plain", "A", "B"], required=True)
    for k, val in DEFAULTS.items():
        ap.add_argument(f"--{k}", type=float, default=val)
    ap.add_argument("--W", type=float, default=None,
                    help="mm, patch width along y (default = L, square). Only for --board plain")
    ap.add_argument("--Gm", type=float, default=None,
                    help="mm, side of the metal ground if larger than the board (e.g. 100 = a 1U face)")
    ap.add_argument("--both-ports", action="store_true",
                    help="board A: solve J2 as a second run instead of deriving it from J1 by symmetry")
    ap.add_argument("--pec", action="store_true", help="lossless metal instead of the copper sheet model")
    ap.add_argument("--end", type=float, default=1e-5, help="energy end criterion (1e-5 = -50 dB)")
    ap.add_argument("--threads", type=int, default=0, help="solver threads (0 = automatic)")
    ap.add_argument("--tag", default="", help="suffix for the result folder name")
    ap.add_argument("--post-only", action="store_true", help="skip the solve and re-read existing data")
    ap.add_argument("--keep", action="store_true", help="keep the raw solver files in sim/_work/")
    return ap.parse_args()


def design_name(a):
    n = f"{a.board}_L{a.L:.2f}_f{a.feed:.2f}"
    if a.board == "B":
        n += f"_c{a.cut:.2f}"
    if abs(a.feed_y) > 1e-9:
        n += f"_fy{a.feed_y:.2f}"
    if a.W is not None:
        n += f"_W{a.W:.2f}"
    n += f"_er{a.er:.2f}_h{a.h:.2f}"
    if abs(a.G - DEFAULTS["G"]) > 1e-9:
        n += f"_G{a.G:.0f}"
    if a.Gm is not None:
        n += f"_Gm{a.Gm:.0f}"
    if abs(a.f0 - DEFAULTS["f0"]) > 1:
        n += f"_f0{a.f0 / 1e9:.3f}"
    if abs(a.res - DEFAULTS["res"]) > 1e-9:
        n += f"_res{a.res:.2f}"
    if a.pec:
        n += "_pec"
    return n + (f"_{a.tag}" if a.tag else "")


# ----------------------------------------------------------------------------- model
def fill(points, res):
    """Mesh lines through every fixed point, with spacing <= res in between."""
    pts = sorted(set(round(p, 6) for p in points))
    lines = []
    for lo, hi in zip(pts[:-1], pts[1:]):
        n = max(1, int(np.ceil((hi - lo) / res - 1e-9)))
        lines.extend(np.linspace(lo, hi, n + 1)[:-1])
    lines.append(pts[-1])
    return lines


def feeds_of(a):
    f = [(a.feed, a.feed_y if a.board != "A" else 0.0)]
    if a.board == "A":
        f.append((0.0, a.feed))
    return f


def build(a, excite_port, sim_path):
    from CSXCAD import ContinuousStructure
    from openEMS import openEMS

    fc = 0.4e9
    fdtd = openEMS(NrTS=400000, EndCriteria=a.end)
    fdtd.SetGaussExcite(a.f0, fc)
    fdtd.SetBoundaryCond(["PML_8"] * 6)
    csx = ContinuousStructure()
    fdtd.SetCSX(csx)
    mesh = csx.GetGrid()
    mesh.SetDeltaUnit(1e-3)

    s, h, g, res = a.L / 2, a.h, a.G / 2, a.res
    w = s if a.W is None else a.W / 2
    gm = g if a.Gm is None else a.Gm / 2            # metal ground half-size (>= board)
    # Thirds rule at the patch edges: one mesh line a third of a cell inside the metal edge and one
    # two thirds outside. openEMS snaps the sheet to the nearest line (the inner one), and a PEC
    # sheet in FDTD acts about a third of a cell larger than its last line, so the two cancel.
    for d, half in (("x", s), ("y", w)):
        e_in, e_out = half - res / 3, half + 2 * res / 3
        fixed = [-e_out, -e_in, -a.feed, 0.0, a.feed, e_in, e_out]
        if abs(a.feed_y) > 1e-9:
            fixed += [-a.feed_y, a.feed_y]
        if a.board == "B":
            fixed += [-(half - a.cut), half - a.cut]
        mesh.AddLine(d, fill(fixed, res))
        mesh.AddLine(d, [-g, g, -gm, gm, -gm - a.pad, gm + a.pad])
    mesh.AddLine("z", np.linspace(0, h, max(4, int(np.ceil(h / 0.4))) + 1))
    mesh.AddLine("z", [-a.pad, h + a.pad])
    air_res = C0 / (a.f0 + fc) / 1e-3 / 20
    mesh.SmoothMeshLines("all", air_res, 1.4)

    kappa = 2 * np.pi * a.f0 * EPS0 * a.er * a.tand
    sub = csx.AddMaterial("substrate", epsilon=a.er, kappa=kappa)
    sub.AddBox([-g, -g, 0], [g, g, h], priority=0)

    def metal(name):
        if a.pec:
            return csx.AddMetal(name)
        return csx.AddConductingSheet(name, conductivity=5.8e7, thickness=35e-6)

    gnd = metal("gnd")
    gnd.AddBox([-gm, -gm, 0], [gm, gm, 0], priority=10)

    patch = metal("patch")
    if a.board == "B":
        c = a.cut
        xs = [-s + c, s, s, s - c, -s, -s]      # corners (-s,+s) and (+s,-s) truncated
        ys = [s, s, -s + c, -s, -s, s - c]
        patch.AddPolygon([xs, ys], "z", h, priority=10)
    else:
        patch.AddBox([-s, -w, h], [s, w, h], priority=10)

    ports = []
    for i, (x, y) in enumerate(feeds_of(a), 1):
        ports.append(fdtd.AddLumpedPort(i, 50, [x, y, 0], [x, y, h], "z",
                                        1.0 if i == excite_port else 0, priority=5))

    # time-domain E-field probes on boresight: a convention-free check of the rotation sense
    probe = csx.AddProbe("E_bore", 2)
    probe.AddBox([0, 0, h + 40.0], [0, 0, h + 40.0])

    f_ff = ff_freqs(a)
    nf2ff = fdtd.CreateNF2FFBox(frequency=f_ff)
    return fdtd, csx, ports, nf2ff


def ff_freqs(a):
    return a.f0 + np.arange(-30e6, 30.1e6, 2.5e6)


# ----------------------------------------------------------------------------- post-processing
def rotation_sense(path, f0):
    """Spin direction from the raw time-domain field on boresight, with our own Fourier sum, so it
    does not depend on openEMS's far-field conventions. Returns (+1 RHCP / -1 LHCP, RHCP-LHCP in dB).
    With exp(+jwt) phasors, RHCP toward +z is (x - j y): Ey lags Ex by 90 degrees."""
    d = np.loadtxt(os.path.join(path, "E_bore"), comments="%")      # columns: t, Ex, Ey, Ez
    t, ex, ey = d[:, 0], d[:, 1], d[:, 2]
    k = np.exp(-2j * np.pi * f0 * t)
    px, py = np.sum(ex * k), np.sum(ey * k)
    er, el = abs(px + 1j * py), abs(px - 1j * py)
    return (1 if er > el else -1), 20 * np.log10(max(er, 1e-30) / max(el, 1e-30))


def run_one(a, excite_port, sim_path):
    fdtd, csx, ports, nf2ff = build(a, excite_port, sim_path)
    if not a.post_only:
        if os.path.isdir(sim_path):
            shutil.rmtree(sim_path)
        os.makedirs(sim_path)
        kw = dict(verbose=1, cleanup=False)
        if a.threads:
            kw["numThreads"] = a.threads
        fdtd.Run(sim_path, **kw)

    f_s = np.linspace(a.f0 - 0.225e9, a.f0 + 0.225e9, 901)
    f_ff = ff_freqs(a)
    out = dict(f_s=f_s, f_ff=f_ff)
    for tag, f in (("s", f_s), ("ff", f_ff)):
        for p in ports:
            p.CalcPort(sim_path, f, 50)
        out[f"inc_{tag}"] = [np.array(p.uf_inc) for p in ports]
        out[f"ref_{tag}"] = [np.array(p.uf_ref) for p in ports]
        out[f"z_{tag}"] = [np.array(p.uf_tot / p.if_tot) for p in ports]
        out[f"pinc_{tag}"] = [np.array(p.P_inc) for p in ports]
        out[f"pacc_{tag}"] = [np.array(p.P_acc) for p in ports]

    theta = np.arange(-180.0, 180.0, 2.0)
    phi = [0.0, 90.0, 270.0]        # 270 is only used to rotate J1's field into J2's (board A)
    r = nf2ff.CalcNF2FF(sim_path, f_ff, theta, phi, center=[0, 0, a.h * 1e-3], read_cached=False)
    out.update(theta=theta, phi=phi,
               Et=np.array(r.E_theta), Ep=np.array(r.E_phi),      # [freq, theta, phi]
               Prad=np.array(r.Prad), Dmax=np.array(r.Dmax))
    out["sense"], out["sense_db"] = rotation_sense(sim_path, a.f0)
    return out


def cp(Et, Ep, phi_deg):
    ph = np.deg2rad(np.asarray(phi_deg))[None, None, :]
    e = np.exp(1j * ph)
    return e * (Et + 1j * Ep) / np.sqrt(2), np.conj(e) * (Et - 1j * Ep) / np.sqrt(2)


def db10(x):
    return 10 * np.log10(np.maximum(np.abs(x), 1e-30))


def db20(x):
    return 20 * np.log10(np.maximum(np.abs(x), 1e-30))


def band_edges(f, y_db, level, f_centre):
    """Contiguous band around f_centre where y_db <= level. Returns (lo, hi) or None."""
    i = int(np.argmin(np.abs(f - f_centre)))
    if y_db[i] > level:
        return None
    lo = i
    while lo > 0 and y_db[lo - 1] <= level:
        lo -= 1
    hi = i
    while hi < len(f) - 1 and y_db[hi + 1] <= level:
        hi += 1
    return float(f[lo]), float(f[hi])


def hpbw(theta, g_db):
    i0 = int(np.argmin(np.abs(theta)))
    pk = g_db[i0]
    lo = i0
    while lo > 0 and g_db[lo - 1] >= pk - 3:
        lo -= 1
    hi = i0
    while hi < len(theta) - 1 and g_db[hi + 1] >= pk - 3:
        hi += 1
    return float(theta[hi] - theta[lo])


def analyse(a, runs):
    f_s, f_ff, theta, phi = runs[0]["f_s"], runs[0]["f_ff"], runs[0]["theta"], [0.0, 90.0]
    lo, hi = a.f0 - a.bw / 2, a.f0 + a.bw / 2
    in_s = (f_s >= lo - 1) & (f_s <= hi + 1)
    in_ff = (f_ff >= lo - 1) & (f_ff <= hi + 1)
    i0 = int(np.argmin(np.abs(f_ff - a.f0)))
    it0 = int(np.argmin(np.abs(theta)))
    res = dict(design=design_name(a), board=a.board,
               params={k: getattr(a, k) for k in DEFAULTS}, lossy_metal=not a.pec)
    curves = dict(f_s=f_s, f_ff=f_ff, theta=theta)

    r1 = runs[0]
    s11 = r1["ref_s"][0] / r1["inc_s"][0]
    curves["S11_dB"] = db20(s11)
    k = int(np.argmin(np.abs(s11)))
    res["s11_min_dB"] = float(db20(s11[k]))
    res["s11_min_freq_GHz"] = float(f_s[k] / 1e9)
    res["zin_at_s11_min_ohm"] = [float(r1["z_s"][0][k].real), float(r1["z_s"][0][k].imag)]
    res["s11_worst_in_band_dB"] = float(db20(s11[in_s]).max())
    b = band_edges(f_s, db20(s11), -10.0, f_s[k])
    res["s11_10dB_band_MHz"] = None if b is None else round((b[1] - b[0]) / 1e6, 1)
    # exp(+jwt) check: a parallel resonance is inductive just below resonance, capacitive above
    kr = int(np.argmax(r1["z_s"][0].real))
    x_lo, x_hi = r1["z_s"][0].imag[max(kr - 40, 0)], r1["z_s"][0].imag[min(kr + 40, len(f_s) - 1)]
    res["phasor_check_ok"] = bool(x_lo > x_hi)
    res["zin_r_peak_ohm"] = float(r1["z_s"][0].real[kr])
    res["zin_r_peak_freq_GHz"] = float(f_s[kr] / 1e9)
    curves["Zin_R"], curves["Zin_X"] = r1["z_s"][0].real, r1["z_s"][0].imag

    if a.board == "A":
        s21 = r1["ref_s"][1] / r1["inc_s"][0]
        if len(runs) == 2:
            r2 = runs[1]
            s22 = r2["ref_s"][1] / r2["inc_s"][1]
            s12 = r2["ref_s"][0] / r2["inc_s"][1]
            Et2, Ep2, n2 = r2["Et"][:, :, :2], r2["Ep"][:, :, :2], r2["inc_ff"][1][:, None, None]
        else:
            # J2 is J1 rotated +90 deg about z on a square patch, so its field at (theta, phi)
            # is J1's field at (theta, phi - 90): cuts phi = 0, 90 come from J1's cuts 270, 0.
            s22, s12 = s11, s21
            Et2, Ep2, n2 = r1["Et"][:, :, [2, 0]], r1["Ep"][:, :, [2, 0]], r1["inc_ff"][0][:, None, None]
        res["port2_from_symmetry"] = len(runs) == 1
        a1, a2 = 1 / np.sqrt(2), -1j / np.sqrt(2)           # ideal hybrid: J2 lags J1 by 90 deg
        b1, b2 = s11 * a1 + s12 * a2, s21 * a1 + s22 * a2
        g_in = b1 * (1 / np.sqrt(2)) + b2 * (-1j / np.sqrt(2))         # back to the hybrid input
        g_iso = b1 * (-1j / np.sqrt(2)) + b2 * (1 / np.sqrt(2))        # into the 50-ohm load
        curves.update(S22_dB=db20(s22), S21_dB=db20(s21), HybridIn_dB=db20(g_in), HybridLoad_dB=db20(g_iso))
        kf = int(np.argmin(np.abs(f_s - a.f0)))
        res["s22_min_dB"] = float(db20(s22).min())
        res["isolation_s21_at_f0_dB"] = float(db20(s21[kf]))
        res["hybrid_input_worst_in_band_dB"] = float(db20(g_in[in_s]).max())
        res["hybrid_load_power_worst_in_band_dB"] = float(db20(g_iso[in_s]).max())
        res["s11_min_freq_GHz_port2"] = float(f_s[int(np.argmin(np.abs(s22)))] / 1e9)
        n1 = r1["inc_ff"][0][:, None, None]
        Et = a1 * r1["Et"][:, :, :2] / n1 + a2 * Et2 / n2
        Ep = a1 * r1["Ep"][:, :, :2] / n1 + a2 * Ep2 / n2
        p_inc = np.full(len(f_ff), 1.0 / (2 * 50.0))
    else:
        Et, Ep = r1["Et"][:, :, :2], r1["Ep"][:, :, :2]
        p_inc = r1["pinc_ff"][0]

    ER, EL = cp(Et, Ep, phi)
    norm = (4 * np.pi / (2 * ETA0) / p_inc)[:, None, None]
    gR, gL, gT = norm * abs(ER) ** 2, norm * abs(EL) ** 2, norm * (abs(Et) ** 2 + abs(Ep) ** 2)
    aR, aL = abs(ER[:, it0, 0]), abs(EL[:, it0, 0])
    ar = db20((aR + aL) / np.maximum(abs(aR - aL), 1e-30))
    curves.update(AR_dB=ar, GR_dBic=db10(gR[:, it0, 0]), GL_dBic=db10(gL[:, it0, 0]),
                  Gtot_dBi=db10(gT[:, it0, 0]),
                  cutR_phi0=db10(gR[i0, :, 0]), cutR_phi90=db10(gR[i0, :, 1]),
                  cutT_phi0=db10(gT[i0, :, 0]), cutT_phi90=db10(gT[i0, :, 1]))

    res["realized_gain_total_at_f0_dBi"] = float(db10(gT[i0, it0, 0]))
    if a.board != "A":
        res["directivity_at_f0_dBi"] = float(db10(r1["Dmax"][i0]))
        res["radiation_efficiency_at_f0"] = float(r1["Prad"][i0] / r1["pacc_ff"][0][i0])
    if a.board == "plain":
        res["hpbw_deg_phi0_phi90"] = [hpbw(theta, curves["cutT_phi0"]), hpbw(theta, curves["cutT_phi90"])]
    else:
        res["rhcp_gain_at_f0_dBic"] = float(curves["GR_dBic"][i0])
        res["rhcp_gain_min_in_band_dBic"] = float(curves["GR_dBic"][in_ff].min())
        res["rhcp_minus_lhcp_at_f0_dB"] = float(curves["GR_dBic"][i0] - curves["GL_dBic"][i0])
        res["axial_ratio_at_f0_dB"] = float(ar[i0])
        res["axial_ratio_worst_in_band_dB"] = float(ar[in_ff].max())
        km = int(np.argmin(ar))
        res["axial_ratio_min_dB"] = float(ar[km])
        res["axial_ratio_min_freq_GHz"] = float(f_ff[km] / 1e9)
        bb = band_edges(f_ff, ar, 3.0, f_ff[km])
        res["axial_ratio_3dB_band_MHz"] = None if bb is None else round((bb[1] - bb[0]) / 1e6, 1)
        res["hpbw_deg_phi0_phi90"] = [hpbw(theta, curves["cutR_phi0"]), hpbw(theta, curves["cutR_phi90"])]
        res["hand"] = "RHCP" if curves["GR_dBic"][i0] > curves["GL_dBic"][i0] else "LHCP"
        if a.board == "B":
            res["hand_time_domain_check"] = "RHCP" if r1["sense"] > 0 else "LHCP"
            res["hand_time_domain_margin_dB"] = float(r1["sense_db"])
    return res, curves


def write_outputs(a, res, curves, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "summary.json"), "w") as fh:
        json.dump(res, fh, indent=2)
    s_cols = [k for k in ("S11_dB", "S22_dB", "S21_dB", "HybridIn_dB", "HybridLoad_dB") if k in curves]
    z_cols = ["Zin_R", "Zin_X"]
    np.savetxt(os.path.join(out_dir, "sparams.csv"),
               np.column_stack([curves["f_s"] / 1e9] + [curves[k] for k in s_cols + z_cols]),
               delimiter=",", header="freq_GHz," + ",".join(s_cols + z_cols), comments="", fmt="%.5f")
    f_cols = ["AR_dB", "GR_dBic", "GL_dBic", "Gtot_dBi"]
    np.savetxt(os.path.join(out_dir, "farfield_boresight.csv"),
               np.column_stack([curves["f_ff"] / 1e9] + [curves[k] for k in f_cols]),
               delimiter=",", header="freq_GHz," + ",".join(f_cols), comments="", fmt="%.5f")
    c_cols = ["cutR_phi0", "cutR_phi90", "cutT_phi0", "cutT_phi90"]
    np.savetxt(os.path.join(out_dir, "pattern_f0.csv"),
               np.column_stack([curves["theta"]] + [curves[k] for k in c_cols]),
               delimiter=",", header="theta_deg," + ",".join(c_cols), comments="", fmt="%.4f")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    lo, hi = (a.f0 - a.bw / 2) / 1e9, (a.f0 + a.bw / 2) / 1e9
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.4))
    labels = dict(S11_dB="S11 (J1)", S22_dB="S22 (J2)", S21_dB="S21 (J1 to J2)",
                  HybridIn_dB="reflection at hybrid input", HybridLoad_dB="power into hybrid load")
    for k in s_cols:
        ax[0].plot(curves["f_s"] / 1e9, curves[k], label=labels[k])
    ax[0].axhline(-10, ls="--", c="k", lw=0.8)
    ax[0].axvspan(lo, hi, alpha=0.12, color="tab:green")
    ax[0].set(xlabel="frequency (GHz)", ylabel="dB", title="Match", ylim=(-40, 0))
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)
    f = curves["f_ff"] / 1e9
    if a.board == "plain":
        ax[1].plot(f, curves["Gtot_dBi"], label="realized gain")
        ax[1].set(xlabel="frequency (GHz)", ylabel="dBi", title="Gain at boresight")
    else:
        ax[1].plot(f, curves["AR_dB"], c="tab:red", label="axial ratio (dB)")
        ax[1].axhline(3, ls="--", c="tab:red", lw=0.8)
        ax[1].set(xlabel="frequency (GHz)", ylabel="axial ratio (dB)", ylim=(0, 12),
                  title="Circular polarization at boresight")
        t = ax[1].twinx()
        t.plot(f, curves["GR_dBic"], c="tab:blue", label="RHCP gain")
        t.plot(f, curves["GL_dBic"], c="tab:blue", ls=":", label="LHCP gain")
        t.set_ylabel("realized gain (dBic)")
        t.legend(fontsize=8, loc="lower right")
    ax[1].axvspan(lo, hi, alpha=0.12, color="tab:green")
    ax[1].legend(fontsize=8, loc="upper left")
    ax[1].grid(alpha=0.3)
    key = "cutT" if a.board == "plain" else "cutR"
    ax[2].plot(curves["theta"], curves[key + "_phi0"], label="phi = 0 cut")
    ax[2].plot(curves["theta"], curves[key + "_phi90"], label="phi = 90 cut")
    pk = max(curves[key + "_phi0"].max(), curves[key + "_phi90"].max())
    ax[2].axhline(pk - 3, ls="--", c="k", lw=0.8)
    ax[2].set(xlabel="angle from boresight (deg)", ylabel="dBi" if a.board == "plain" else "dBic",
              title=f"Pattern at {a.f0 / 1e9:.3f} GHz", ylim=(pk - 30, pk + 2), xlim=(-180, 180))
    ax[2].legend(fontsize=8)
    ax[2].grid(alpha=0.3)
    fig.suptitle(res["design"], fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "results.png"), dpi=110)
    plt.close(fig)


def main():
    a = parse()
    name = design_name(a)
    work = os.path.join(HERE, "_work", name)
    out_dir = os.path.join(HERE, "results_openems", name)
    t0 = time.time()
    n_runs = 2 if (a.board == "A" and a.both_ports) else 1
    runs = [run_one(a, i + 1, os.path.join(work, f"port{i + 1}")) for i in range(n_runs)]
    res, curves = analyse(a, runs)
    res["solve_minutes"] = round((time.time() - t0) / 60, 1)
    write_outputs(a, res, curves, out_dir)
    if not a.keep and not a.post_only:
        shutil.rmtree(work, ignore_errors=True)
    print("RESULT " + json.dumps(res))


if __name__ == "__main__":
    sys.exit(main())
