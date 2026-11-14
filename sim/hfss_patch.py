"""Build and solve the S-band patch in Ansys HFSS through PyAEDT.

STATUS: DRAFT, NOT YET RUN. It was written on a Mac without AEDT. Expect to fix a few
PyAEDT call signatures on the first run (they change between releases); check the
installed version with `pip show pyaedt` and its docs. The geometry, coordinate
convention and pass criteria below are the parts to keep.

The design itself was done in openEMS (see openems_patch.py and README.md). This script is
the independent cross-check. PTFE boards: add --er 2.55 --tand 0.0018 and their own L/feed/cut.
--Gm 100 puts a 100 mm metal ground behind the 60 mm board (the satellite face).

Usage (Windows, AEDT Student installed, `pip install -r requirements.txt`):
  python hfss_patch.py --board plain                 # step 1: linear square patch, one feed
  python hfss_patch.py --board A                     # dual feed, J1 0 deg, J2 -90 deg (RHCP)
  python hfss_patch.py --board B                     # cut corner (TL/BR in the KiCad top view)
  python hfss_patch.py --board B --er 3.62           # drift check
  python hfss_patch.py --board B --L 31.54 --feed 5.90 --cut 3.13   # board B, RO4350B
  # the current best option: board B on PTFE, tuned for and solved on a 100 mm metal face
  python hfss_patch.py --board B --L 37.52 --feed 7.00 --cut 3.50 --er 2.55 --tand 0.0018 --Gm 100

Results go to sim/results_hfss/<design>/, named like the openEMS folders in
sim/results_openems/ so the two can be compared side by side.

Coordinates (HFSS): ground at z=0, patch at z=h, antenna radiates toward +z.
x = right and y = up when looking at the patch from the front (+z), i.e. the KiCad top
view with KiCad's y flipped. So:
  J1 at (+feed, 0), J2 at (0, +feed)
  Board B cut corners: KiCad TL/BR  ->  HFSS (-x,+y) and (+x,-y)

Polarization: IEEE, wave leaving the patch. RHCP = counter-clockwise seen from +z.
Self-check: board A with J2 lagging J1 by 90 deg MUST come out RHCP. If HFSS says LHCP,
the coordinate mapping or the source phasing is wrong; fix that before trusting board B.
"""
import argparse
import csv
import math
import os

C0 = 299_792_458.0

DEFAULTS = dict(
    f0=2.425,      # GHz, placeholder until the carrier is confirmed
    bw=20.0,       # MHz signal bandwidth
    L=31.40,       # patch side, mm (openEMS result for board A; board B uses 31.54)
    feed=5.80,     # probe offset from centre, mm (board B: 5.90)
    cut=3.13,      # corner-cut leg, mm (board B)
    h=1.524,       # RO4350B core thickness, mm
    G=60.0,        # board (substrate) side, mm
    Gm=0.0,        # metal ground side, mm. 0 = same as the board. 100 = a 100 mm satellite face
    er=3.66,       # RO4350B DESIGN Dk (not the 3.48 process value)
    tand=0.0031,   # loss tangent at 2.5 GHz
    r_pin=0.25,    # probe radius = via drill / 2, mm
    r_clear=0.8,   # ground clearance radius around the probe (via pad 0.4 + clearance 0.4), mm
)

REQ = dict(s11_db=-10.0, ar_db=3.0, gain_dbic=6.5, hpbw_deg=60.0)


def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", choices=["plain", "A", "B"], required=True)
    for k, val in DEFAULTS.items():
        ap.add_argument(f"--{k}", type=float, default=val)
    ap.add_argument("--version", default=None, help='AEDT version, e.g. "2026.1"; default = newest installed')
    ap.add_argument("--non-graphical", action="store_true")
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("--pec", action="store_true", help="lossless copper (default: finite-conductivity copper)")
    ap.add_argument("--delta-s", type=float, default=0.01, help="adaptive mesh convergence target")
    ap.add_argument("--tag", default="", help="suffix for the design and results folder name")
    ap.add_argument("--project", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "patch.aedt"))
    return ap.parse_args()


def design_name(a):
    """Same naming as openems_patch.py, e.g. B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100."""
    name = f"{a.board}_L{a.L:.2f}_f{a.feed:.2f}" + (f"_c{a.cut:.2f}" if a.board == "B" else "")
    name += f"_er{a.er:.2f}_h{a.h:.2f}"
    if a.Gm > a.G:
        name += f"_Gm{a.Gm:.0f}"
    if a.tag:
        name += f"_{a.tag}"
    return name


def aedt_name(a):
    """AEDT design names: keep to letters, digits and underscores."""
    return design_name(a).replace(".", "p")


def build(hfss, a):
    m = hfss.modeler
    m.model_units = "mm"

    mat = hfss.materials.add_material("RO4350B_design")
    mat.permittivity = a.er
    mat.dielectric_loss_tangent = a.tand

    G, h = a.G, a.h
    Gg = max(a.G, a.Gm)   # metal ground side (larger than the board with --Gm)
    m.create_box(origin=[-G / 2, -G / 2, 0], sizes=[G, G, h], name="substrate", material="RO4350B_design")

    # feed points (HFSS coordinates, see module docstring)
    feeds = [(a.feed, 0.0)]
    if a.board == "A":
        feeds.append((0.0, a.feed))

    # ground sheet with a clearance hole at each probe
    gnd = m.create_rectangle(orientation="XY", origin=[-Gg / 2, -Gg / 2, 0], sizes=[Gg, Gg], name="ground")
    for i, (x, y) in enumerate(feeds, 1):
        hole = m.create_circle(orientation="XY", origin=[x, y, 0], radius=a.r_clear, name=f"hole{i}")
        m.subtract(gnd, [hole], keep_originals=False)

    # patch sheet
    s = a.L / 2
    if a.board == "B":
        c = a.cut
        # corners (-s,+s) and (+s,-s) truncated  == KiCad top-left / bottom-right
        pts = [[-s + c, s, h], [s, s, h], [s, -s + c, h], [s - c, -s, h], [-s, -s, h], [-s, s - c, h]]
        patch = m.create_polyline(pts, close_surface=True, cover_surface=True, name="patch")
    else:
        patch = m.create_rectangle(orientation="XY", origin=[-s, -s, h], sizes=[a.L, a.L], name="patch")

    if a.pec:
        hfss.assign_perfecte_to_sheets(["ground", "patch"], name="PEC_sheets")
    else:
        # finite-conductivity copper, to match the lossy copper in the openEMS model
        hfss.assign_finite_conductivity(["ground", "patch"], material="copper", name="Cu_sheets")

    # probes + lumped ports (annulus in the ground hole, integration line radial along +x)
    for i, (x, y) in enumerate(feeds, 1):
        pin = m.create_cylinder(orientation="Z", origin=[x, y, 0], radius=a.r_pin, height=h,
                                name=f"pin{i}", material="pec")
        m.subtract("substrate", [pin], keep_originals=True)
        ring = m.create_circle(orientation="XY", origin=[x, y, 0], radius=a.r_clear, name=f"port{i}")
        inner = m.create_circle(orientation="XY", origin=[x, y, 0], radius=a.r_pin, name=f"inner{i}")
        m.subtract(ring, [inner], keep_originals=False)
        hfss.lumped_port(assignment=f"port{i}", create_port_sheet=False, impedance=50,
                         integration_line=[[x + a.r_pin, y, 0], [x + a.r_clear, y, 0]],
                         name=f"P{i}", renormalize=True)

    # air box a quarter wavelength beyond everything, radiation boundary
    pad = C0 / (a.f0 * 1e9) / 4 * 1e3
    m.create_box(origin=[-Gg / 2 - pad, -Gg / 2 - pad, -pad], sizes=[Gg + 2 * pad, Gg + 2 * pad, h + 2 * pad],
                 name="airbox", material="vacuum")
    hfss.assign_radiation_boundary_to_objects("airbox")
    return [f"P{i}" for i in range(1, len(feeds) + 1)]


def solve(hfss, a, ports):
    setup = hfss.create_setup(name="Setup1")
    setup.props["Frequency"] = f"{a.f0}GHz"
    setup.props["MaximumPasses"] = 20
    setup.props["MaxDeltaS"] = a.delta_s
    setup.update()
    hfss.create_linear_count_sweep(setup="Setup1", units="GHz", start_frequency=2.20, stop_frequency=2.65,
                                   num_of_freq_points=451, name="S", sweep_type="Interpolating",
                                   save_fields=False)
    # discrete sweep with fields saved so far-field quantities can be plotted against frequency
    half = max(0.03, a.bw / 1000)  # GHz
    hfss.create_linear_step_sweep(setup="Setup1", unit="GHz", start_frequency=round(a.f0 - half, 4),
                                  stop_frequency=round(a.f0 + half, 4), step_size=0.0025, name="FF",
                                  save_fields=True, sweep_type="Discrete")
    hfss.insert_infinite_sphere(definition="Theta-Phi", x_start=-180, x_stop=180, x_step=2,
                                y_start=0, y_stop=90, y_step=90, name="ff")
    if a.board == "A":
        # ideal hybrid: equal power, J2 lags J1 by 90 deg -> RHCP
        hfss.edit_sources({"P1:1": ("1W", "0deg"), "P2:1": ("1W", "-90deg")})
    hfss.analyze_setup("Setup1", cores=a.cores)


def series(sol, expr):
    """PyAEDT has renamed these accessors across versions; try both."""
    x = list(sol.primary_sweep_values)
    try:
        y = list(sol.data_real(expr))
    except Exception:
        y = list(sol.get_expression_data(expr)[1])
    return x, y


def report(hfss, a, ports, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    rows = {}

    s_exprs = [f"dB(S({p},{p}))" for p in ports] + (["dB(S(P2,P1))"] if len(ports) == 2 else [])
    sol = hfss.post.get_solution_data(expressions=s_exprs, setup_sweep_name="Setup1 : S")
    for e in s_exprs:
        rows[e] = series(sol, e)

    ff_exprs = ["dB(RealizedGainRHCP)", "dB(RealizedGainLHCP)", "dB(AxialRatioValue)"]
    sol = hfss.post.get_solution_data(expressions=ff_exprs, setup_sweep_name="Setup1 : FF",
                                      report_category="Far Fields", context="ff",
                                      primary_sweep_variable="Freq",
                                      variations={"Theta": ["0deg"], "Phi": ["0deg"], "Freq": ["All"]})
    ff = {e: series(sol, e) for e in ff_exprs}

    cuts = {}
    for phi in ("0deg", "90deg"):
        sol = hfss.post.get_solution_data(expressions=["dB(RealizedGainRHCP)"], setup_sweep_name="Setup1 : FF",
                                          report_category="Far Fields", context="ff",
                                          primary_sweep_variable="Theta",
                                          variations={"Theta": ["All"], "Phi": [phi], "Freq": [f"{a.f0}GHz"]})
        cuts[phi] = series(sol, "dB(RealizedGainRHCP)")

    # ---- write CSVs
    with open(os.path.join(out_dir, "sparams.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["freq_GHz"] + s_exprs)
        f = rows[s_exprs[0]][0]
        for i in range(len(f)):
            w.writerow([f[i]] + [rows[e][1][i] for e in s_exprs])
    with open(os.path.join(out_dir, "farfield_boresight.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["freq_GHz"] + ff_exprs)
        f = ff[ff_exprs[0]][0]
        for i in range(len(f)):
            w.writerow([f[i]] + [ff[e][1][i] for e in ff_exprs])

    # ---- summary against requirements
    lo, hi = a.f0 - a.bw / 2000, a.f0 + a.bw / 2000
    fs, s11 = rows[s_exprs[0]]
    band = [s for fq, s in zip(fs, s11) if lo <= fq <= hi]
    i_min = min(range(len(s11)), key=lambda i: s11[i])
    fA, ar = ff["dB(AxialRatioValue)"]
    ar_band = [v for fq, v in zip(fA, ar) if lo <= fq <= hi]
    fG, g = ff["dB(RealizedGainRHCP)"]
    g_band = [v for fq, v in zip(fG, g) if lo <= fq <= hi]
    fL, gl = ff["dB(RealizedGainLHCP)"]

    def hpbw(theta, gain):
        pk = max(gain)
        inside = [t for t, gg in zip(theta, gain) if gg >= pk - 3]
        return max(inside) - min(inside) if inside else float("nan")

    lines = [
        f"design: {design_name(a)}",
        f"S11 minimum: {s11[i_min]:.1f} dB at {fs[i_min]:.4f} GHz",
        f"worst S11 in {lo:.3f}-{hi:.3f} GHz: {max(band):.1f} dB (need <= {REQ['s11_db']})",
        f"worst axial ratio in band: {max(ar_band):.2f} dB (need <= {REQ['ar_db']})",
        f"min RHCP realized gain in band: {min(g_band):.2f} dBic (need >= {REQ['gain_dbic']})",
        f"RHCP minus LHCP at f0: {g[len(g) // 2] - gl[len(gl) // 2]:.1f} dB (positive = RHCP, as intended)",
        f"HPBW phi=0: {hpbw(*cuts['0deg']):.0f} deg, phi=90: {hpbw(*cuts['90deg']):.0f} deg (need >= {REQ['hpbw_deg']})",
    ]
    if len(ports) == 2:
        fs2, s21 = rows["dB(S(P2,P1))"]
        lines.append(f"port isolation S21 at f0: {s21[min(range(len(fs2)), key=lambda i: abs(fs2[i] - a.f0))]:.1f} dB")
    text = "\n".join(lines)
    with open(os.path.join(out_dir, "summary.txt"), "w") as fh:
        fh.write(text + "\n")
    print(text)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 3, figsize=(15, 4))
        for e in s_exprs:
            ax[0].plot(*rows[e], label=e)
        ax[0].axhline(-10, ls="--", c="k", lw=0.8)
        ax[0].axvspan(lo, hi, alpha=0.1)
        ax[0].set(xlabel="GHz", ylabel="dB", title="S-parameters")
        ax[0].legend()
        ax[1].plot(fA, ar)
        ax[1].axhline(3, ls="--", c="k", lw=0.8)
        ax[1].axvspan(lo, hi, alpha=0.1)
        ax[1].set(xlabel="GHz", ylabel="dB", title="Axial ratio at boresight")
        for phi, (t, gg) in cuts.items():
            ax[2].plot(t, gg, label=f"phi={phi}")
        ax[2].set(xlabel="theta (deg)", ylabel="dBic", title=f"RHCP realized gain at {a.f0} GHz")
        ax[2].legend()
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, "results.png"), dpi=120)
    except Exception as e:  # plots are a convenience
        print("plotting skipped:", e)


def main():
    a = parse()
    from ansys.aedt.core import Hfss  # imported late so --help works without AEDT

    hfss = Hfss(project=a.project, design=aedt_name(a), solution_type="Modal", version=a.version,
                non_graphical=a.non_graphical, new_desktop=True, student_version=True)
    try:
        ports = build(hfss, a)
        solve(hfss, a, ports)
        report(hfss, a, ports, os.path.join(os.path.dirname(a.project), "results_hfss", design_name(a)))
        hfss.save_project()
    finally:
        hfss.release_desktop(close_projects=False, close_desktop=a.non_graphical)


if __name__ == "__main__":
    main()
