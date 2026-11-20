"""Build and solve the S-band patch in Ansys HFSS through PyAEDT.

STATUS: runs on AEDT Student 2025 R2 with PyAEDT 1.9 (Windows). The geometry, coordinate
convention and pass criteria are the same as the openEMS model (see openems_patch.py and
README.md); this script is the independent cross-check.

PTFE boards: add --er 2.55 --tand 0.0018 and their own L/feed/cut.
--Gm 100 puts a 100 mm metal ground behind the 60 mm board (the satellite face).

Usage (Windows, AEDT Student installed, `pip install -r requirements.txt`):
  python hfss_patch.py --board plain                 # step 1: linear square patch, one feed
  python hfss_patch.py --board A                     # dual feed, J1 0 deg, J2 -90 deg (RHCP)
  python hfss_patch.py --board B                     # cut corner (TL/BR in the KiCad top view)
  python hfss_patch.py --board B --er 3.62           # drift check
  python hfss_patch.py --board B --L 31.54 --feed 5.90 --cut 3.13   # board B, RO4350B
  # the current best option: board B on PTFE, tuned for and solved on a 100 mm metal face
  python hfss_patch.py --board B --L 37.52 --feed 7.00 --cut 3.50 --er 2.55 --tand 0.0018 --Gm 100
  # stacked patch: board B's fed patch plus a second, unconnected patch on a second board above it
  python hfss_patch.py --board S --L 37.0 --feed 7.0 --cut 5.0 --L2 46.0 --cut2 6.0 --gap 4.0       --er 2.55 --tand 0.0018 --Gm 100 --ff_half 125 --ff_step 5 --s_lo 2.1 --s_hi 2.8

Board SD is board S with two feeds and no corner cuts (a stacked dual feed, driven like board A).

Board S (stacked): the lower board is board B. The upper board (same laminate, thickness --h2) sits
--gap mm above it. Its patch (side --L2, corner cuts --cut2, same two corners as the lower patch) is
on the underside, facing the lower patch (--up-side bottom, the default), or on the top (--up-side
top; needed when --gap is 0, i.e. the two boards lie on each other). --spacers adds the four corner
standoffs: nylon posts in the gap, or steel screws through both boards with metal standoffs.

Things openEMS left out (HFSS_TASK.md test 3):
  --sma    replace the lumped port with a short 50 ohm coax below the ground and a wave port
  --mask   solder mask on the top of the board, everywhere except over the patch
  --box    a metal box (Gm x Gm x box_depth) behind the board instead of a flat sheet

Results go to sim/results_hfss/<design>/, named like the openEMS folders in
sim/results_openems/ so the two can be compared side by side. By default each design is
its own AEDT project in sim/hfss_projects/; pass --project-dir to keep the (large) solver
files somewhere else, e.g. outside a synced folder.

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
import json
import math
import os
import time

C0 = 299_792_458.0
HERE = os.path.dirname(os.path.abspath(__file__))

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
    feed_y=0.0,    # boards B and S: sideways offset of the feed point (0 = on the x axis), mm
    L2=46.0,       # board S: upper (parasitic) patch side, mm
    cut2=0.0,      # board S: upper patch corner-cut leg, mm
    gap=4.0,       # board S: air gap between the two boards, mm
    h2=1.524,      # board S: upper board thickness, mm
    dx2=0.0,       # board S: upper board (and its patch) shifted sideways by this much, mm (assembly error)
    dy2=0.0,
    G2=0.0,        # board S: upper board side, mm. 0 = same as the lower board
    ff_half=0.0,   # MHz: half-width of the far-field sweep. 0 = max(30, bw)
    ff_step=2.5,   # MHz: step of the far-field sweep
    s_lo=2.20,     # GHz: S-parameter sweep start
    s_hi=2.65,     # GHz: S-parameter sweep stop
)

REQ = dict(s11_db=-10.0, ar_db=3.0, gain_dbic=6.5, hpbw_deg=60.0)

# --sma: SMA-sized coax (1.27 mm pin in PTFE); outer radius chosen for exactly 50 ohm
SMA_R_IN = 0.635
SMA_ER = 2.1
SMA_R_OUT = SMA_R_IN * math.exp(50.0 * math.sqrt(SMA_ER) / 59.96)
SMA_LEN = 5.0
# --mask: typical LPI solder mask
MASK_T, MASK_ER, MASK_TAND = 0.025, 3.8, 0.025
# --spacers (board S): standoffs at the four mounting-hole positions, this far in from each board edge
SPACER_INSET, SPACER_R, SCREW_R = 4.0, 2.5, 1.5
NYLON_ER, NYLON_TAND = 3.0, 0.02
# board A: how far a real 90 degree hybrid plus its two cables may be off (amplitude dB, phase degrees)
HYBRID_CASES = [(0.5, 3.0), (1.0, 5.0), (1.0, 10.0)]


def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", choices=["plain", "A", "B", "S", "SD"], required=True)
    for k, val in DEFAULTS.items():
        ap.add_argument(f"--{k}", type=float, default=val)
    ap.add_argument("--version", default=None, help='AEDT version, e.g. "2025.2"; default = newest installed')
    ap.add_argument("--graphical", action="store_true", help="show the AEDT window (default: non-graphical)")
    ap.add_argument("--cores", type=int, default=4)
    ap.add_argument("--pec", action="store_true", help="lossless copper (default: finite-conductivity copper)")
    ap.add_argument("--delta-s", type=float, default=0.01, help="adaptive mesh convergence target")
    ap.add_argument("--passes", type=int, default=20, help="maximum adaptive passes")
    ap.add_argument("--target-tets", type=int, default=0,
                    help="keep refining until the mesh has at least this many tetrahedra (ignores --delta-s); "
                         "40000 is near the top of what AEDT Student allows (64000)")
    ap.add_argument("--pad", type=float, default=0.0, help="air box padding in mm (default: a quarter wavelength)")
    ap.add_argument("--sma", action="store_true", help="coax + wave port below the ground instead of the lumped port")
    ap.add_argument("--mask", action="store_true", help="solder mask on the top of the board, except over the patch")
    ap.add_argument("--box", action="store_true", help="metal box behind the board instead of a flat sheet (needs --Gm)")
    ap.add_argument("--box-depth", type=float, default=100.0, help="depth of the --box, mm")
    ap.add_argument("--up-side", choices=["bottom", "top"], default="bottom",
                    help="board S: which face of the upper board carries the upper patch")
    ap.add_argument("--spacers", choices=["none", "nylon", "steel"], default="none",
                    help="board S: corner standoffs between the two boards")
    ap.add_argument("--tag", default="", help="suffix for the design and results folder name")
    ap.add_argument("--project-dir", default=os.path.join(HERE, "hfss_projects"),
                    help="folder for the AEDT project (one project per design)")
    ap.add_argument("--out", default=os.path.join(HERE, "results_hfss"), help="results folder")
    return ap.parse_args()


def design_name(a):
    """Same naming as openems_patch.py, e.g. B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100."""
    name = f"{a.board}_L{a.L:.2f}_f{a.feed:.2f}" + (f"_c{a.cut:.2f}" if a.board in ("B", "S") else "")
    if a.feed_y and a.board in ("B", "S"):
        name += f"_fy{a.feed_y:.2f}"
    if a.board in ("S", "SD"):
        name += f"_U{a.L2:.2f}_uc{a.cut2:.2f}_g{a.gap:.2f}" + ("_top" if a.up_side == "top" else "")
    name += f"_er{a.er:.2f}_h{a.h:.2f}"
    if a.Gm > a.G:
        name += f"_Gm{a.Gm:.0f}"
    if a.tag:
        name += f"_{a.tag}"
    if a.target_tets:
        name += f"_mesh{a.target_tets // 1000}k"
    return name


def aedt_name(a):
    """AEDT design names: keep to letters, digits and underscores."""
    return design_name(a).replace(".", "p")


def build(hfss, a):
    m = hfss.modeler
    m.model_units = "mm"

    mat = hfss.materials.add_material("substrate_design")
    mat.permittivity = a.er
    mat.dielectric_loss_tangent = a.tand

    G, h = a.G, a.h
    Gg = max(a.G, a.Gm)   # metal ground side (larger than the board with --Gm)
    m.create_box(origin=[-G / 2, -G / 2, 0], sizes=[G, G, h], name="substrate", material="substrate_design")

    # feed points (HFSS coordinates, see module docstring)
    feeds = [(a.feed, a.feed_y if a.board in ("B", "S") else 0.0)]
    if a.board in ("A", "SD"):
        feeds.append((0.0, a.feed))

    sheets = ["patch"]
    z_bottom = 0.0
    if a.box:
        # solid metal body behind the board; its top face is the ground. A shallow pocket under each
        # probe leaves room for the lumped port ring (pocket radius = the ground clearance).
        body = m.create_box(origin=[-Gg / 2, -Gg / 2, -a.box_depth], sizes=[Gg, Gg, a.box_depth], name="body",
                            material="pec" if a.pec else "copper")
        for i, (x, y) in enumerate(feeds, 1):
            pocket = m.create_cylinder(orientation="Z", origin=[x, y, -0.5], radius=a.r_clear, height=0.5,
                                       name=f"pocket{i}")
            m.subtract(body, [pocket], keep_originals=False)
        z_bottom = -a.box_depth
    else:
        # ground sheet with a clearance hole at each probe
        gnd = m.create_rectangle(orientation="XY", origin=[-Gg / 2, -Gg / 2, 0], sizes=[Gg, Gg], name="ground")
        for i, (x, y) in enumerate(feeds, 1):
            hole = m.create_circle(orientation="XY", origin=[x, y, 0], radius=a.r_clear, name=f"hole{i}")
            m.subtract(gnd, [hole], keep_originals=False)
        sheets.append("ground")

    # patch sheet
    s = a.L / 2
    if a.board in ("B", "S"):
        c = a.cut
        # corners (-s,+s) and (+s,-s) truncated  == KiCad top-left / bottom-right
        pts = [[-s + c, s, h], [s, s, h], [s, -s + c, h], [s - c, -s, h], [-s, -s, h], [-s, s - c, h]]
    else:
        pts = [[-s, s, h], [s, s, h], [s, -s, h], [-s, -s, h]]
    m.create_polyline(pts, close_surface=True, cover_surface=True, name="patch")

    top = h
    if a.board in ("S", "SD"):
        if a.gap <= 0 and a.up_side == "bottom":
            raise SystemExit("--gap 0 needs --up-side top (otherwise the two patches touch)")
        G2 = a.G2 if a.G2 > 0 else G
        zu = h + a.gap                      # underside of the upper board
        top = zu + a.h2
        m.create_box(origin=[-G2 / 2 + a.dx2, -G2 / 2 + a.dy2, zu], sizes=[G2, G2, a.h2], name="substrate2",
                     material="substrate_design")
        zp = zu if a.up_side == "bottom" else top
        s2, c2 = a.L2 / 2, (a.cut2 if a.board == "S" else 0.0)
        if c2 > 0:
            pts2 = [[-s2 + c2, s2, zp], [s2, s2, zp], [s2, -s2 + c2, zp], [s2 - c2, -s2, zp], [-s2, -s2, zp],
                    [-s2, s2 - c2, zp]]
        else:
            pts2 = [[-s2, s2, zp], [s2, s2, zp], [s2, -s2, zp], [-s2, -s2, zp]]
        pts2 = [[x + a.dx2, y + a.dy2, z] for x, y, z in pts2]
        m.create_polyline(pts2, close_surface=True, cover_surface=True, name="patch2")
        sheets.append("patch2")
        if a.spacers != "none":
            q = min(G, G2) / 2 - SPACER_INSET
            for i, (x, y) in enumerate([(q, q), (-q, q), (-q, -q), (q, -q)], 1):
                if a.spacers == "nylon":
                    if a.gap > 0:
                        ny = hfss.materials.add_material("nylon_spacer") if i == 1 else None
                        if ny:
                            ny.permittivity = NYLON_ER
                            ny.dielectric_loss_tangent = NYLON_TAND
                        m.create_cylinder(orientation="Z", origin=[x, y, h], radius=SPACER_R, height=a.gap,
                                          name=f"spacer{i}", material="nylon_spacer")
                else:
                    # steel screw from the ground up through both boards, metal standoff in the gap
                    scr = m.create_cylinder(orientation="Z", origin=[x, y, 0], radius=SCREW_R, height=top,
                                            name=f"screw{i}", material="pec")
                    m.subtract("substrate", [scr], keep_originals=True)
                    m.subtract("substrate2", [scr], keep_originals=True)
                    if a.gap > 0:
                        so = m.create_cylinder(orientation="Z", origin=[x, y, h], radius=SPACER_R, height=a.gap,
                                               name=f"standoff{i}", material="pec")
                        m.unite([scr, so])

    if a.mask:
        mm = hfss.materials.add_material("solder_mask")
        mm.permittivity = MASK_ER
        mm.dielectric_loss_tangent = MASK_TAND
        mask = m.create_box(origin=[-G / 2, -G / 2, h], sizes=[G, G, MASK_T], name="mask", material="solder_mask")
        opening = m.create_polyline(pts, close_surface=True, cover_surface=True, name="mask_opening")
        m.sweep_along_vector(opening, [0, 0, MASK_T])
        m.subtract(mask, [opening], keep_originals=False)

    if a.pec:
        hfss.assign_perfecte_to_sheets(sheets, name="PEC_sheets")
    else:
        # finite-conductivity copper, to match the lossy copper in the openEMS model
        hfss.assign_finite_conductivity(sheets, material="copper", name="Cu_sheets")

    # probes + ports
    ports = []
    for i, (x, y) in enumerate(feeds, 1):
        pin = m.create_cylinder(orientation="Z", origin=[x, y, 0], radius=a.r_pin, height=h,
                                name=f"pin{i}", material="pec")
        m.subtract("substrate", [pin], keep_originals=True)
        if a.sma:
            # coax below the ground: PEC cup (outer conductor + back wall), PTFE fill, 1.27 mm pin.
            # The wave port is the PTFE annulus on the back wall, de-embedded to the ground plane.
            wall = 0.5
            cup = m.create_cylinder(orientation="Z", origin=[x, y, -SMA_LEN - wall], radius=SMA_R_OUT + wall,
                                    height=SMA_LEN + wall, name=f"sma_shell{i}", material="pec")
            diel = m.create_cylinder(orientation="Z", origin=[x, y, -SMA_LEN], radius=SMA_R_OUT, height=SMA_LEN,
                                     name=f"sma_diel{i}", material="sma_ptfe")
            m.subtract(cup, [diel], keep_originals=True)
            cpin = m.create_cylinder(orientation="Z", origin=[x, y, -SMA_LEN], radius=SMA_R_IN, height=SMA_LEN,
                                     name=f"sma_pin{i}", material="pec")
            m.subtract(diel, [cpin], keep_originals=True)
            face = min(m[f"sma_diel{i}"].faces, key=lambda f: f.center[2])
            hfss.wave_port(assignment=face, integration_line=[[x + SMA_R_IN, y, -SMA_LEN], [x + SMA_R_OUT, y, -SMA_LEN]],
                           modes=1, impedance=50, name=f"P{i}", renormalize=True, deembed=SMA_LEN)
            z_bottom = min(z_bottom, -SMA_LEN - wall)
        else:
            # lumped port: annulus in the ground hole, integration line radial along +x
            ring = m.create_circle(orientation="XY", origin=[x, y, 0], radius=a.r_clear, name=f"port{i}")
            inner = m.create_circle(orientation="XY", origin=[x, y, 0], radius=a.r_pin, name=f"inner{i}")
            m.subtract(ring, [inner], keep_originals=False)
            hfss.lumped_port(assignment=f"port{i}", create_port_sheet=False, impedance=50,
                             integration_line=[[x + a.r_pin, y, 0], [x + a.r_clear, y, 0]],
                             name=f"P{i}", renormalize=True)
        ports.append(f"P{i}")

    # air box a quarter wavelength beyond everything, radiation boundary
    pad = a.pad if a.pad > 0 else C0 / (a.f0 * 1e9) / 4 * 1e3
    top = max(top, h + (MASK_T if a.mask else 0))
    m.create_box(origin=[-Gg / 2 - pad, -Gg / 2 - pad, z_bottom - pad],
                 sizes=[Gg + 2 * pad, Gg + 2 * pad, top - z_bottom + 2 * pad], name="airbox", material="vacuum")
    hfss.assign_radiation_boundary_to_objects("airbox")
    return ports


def print_messages(hfss):
    """AEDT's own warnings and errors for this design, so a failed solve explains itself in the log."""
    try:
        for msg in hfss.odesktop.GetMessages(hfss.project_name, hfss.design_name, 1):
            print("AEDT:", str(msg).strip())
    except Exception as e:
        print("could not read AEDT messages:", e)


def mesh_stats(hfss, path=None):
    """(passes, tetrahedra, last delta S) from AEDT's convergence table."""
    path = path or os.path.join(hfss.working_directory, "convergence.txt")
    hfss.odesign.ExportConvergence("Setup1", "", path, True)
    txt = open(path, errors="ignore").read()
    rows = [[c.strip() for c in ln.split("|")] for ln in txt.splitlines() if "|" in ln and ln.strip()[:1].isdigit()]
    last = rows[-1]
    return int(last[0]), int(last[1]), (float(last[2]) if len(last) > 2 and last[2] not in ("", "N/A") else None)


def solve(hfss, a, ports):
    setup = hfss.create_setup(name="Setup1")
    setup.props["Frequency"] = f"{a.f0}GHz"
    setup.props["MaximumPasses"] = a.passes
    setup.props["MaxDeltaS"] = a.delta_s
    setup.props["MinimumConvergedPasses"] = 2
    setup.update()
    if a.target_tets:
        # mesh-size-controlled refinement: adapt (no sweeps yet) until the mesh reaches the target.
        # A pass grows the mesh by at most 30 %, so the final size stays under 1.3 x target.
        setup.props["MaxDeltaS"] = 1e-5
        passes = 8
        while True:
            setup.props["MaximumPasses"] = passes
            setup.update()
            if not hfss.analyze_setup("Setup1", cores=a.cores):
                print_messages(hfss)
                raise RuntimeError("HFSS adaptive solve failed (see the AEDT message log)")
            tets = mesh_stats(hfss)[1]
            print(f"adaptive: {passes} passes, {tets} tetrahedra", flush=True)
            if tets >= a.target_tets or passes >= 40:
                break
            passes += 2 if tets * 1.69 < a.target_tets else 1
    hfss.create_linear_count_sweep(setup="Setup1", unit="GHz", start_frequency=a.s_lo, stop_frequency=a.s_hi,
                                   num_of_freq_points=int(round((a.s_hi - a.s_lo) * 2000)) + 1, name="S", sweep_type="Interpolating",
                                   save_fields=False)
    # discrete sweep with fields saved so far-field quantities can be plotted against frequency
    half = a.ff_half / 1000 if a.ff_half > 0 else max(0.03, a.bw / 1000)  # GHz
    hfss.create_linear_step_sweep(setup="Setup1", unit="GHz", start_frequency=round(a.f0 - half, 4),
                                  stop_frequency=round(a.f0 + half, 4), step_size=a.ff_step / 1000, name="FF",
                                  save_fields=True, sweep_type="Discrete")
    hfss.insert_infinite_sphere(definition="Theta-Phi", theta_start=-180, theta_stop=180, theta_step=2,
                                phi_start=0, phi_stop=90, phi_step=90, name="ff")
    if a.board in ("A", "SD"):
        # ideal hybrid: equal power, J2 lags J1 by 90 deg -> RHCP
        hfss.edit_sources({"P1:1": ("1W", "0deg"), "P2:1": ("1W", "-90deg")})
    ok = hfss.analyze_setup("Setup1", cores=a.cores)
    print_messages(hfss)
    if not ok:

        raise RuntimeError("HFSS solve failed (see the AEDT message log)")


def series(sol, expr):
    x = [float(v) for v in sol.primary_sweep_values]
    y = sol.get_expression_data(expr)
    if isinstance(y, tuple):  # PyAEDT >= 1.0 returns (x, y)
        y = y[1]
    return x, [float(v) for v in y]


def crossings(x, y, level):
    """x positions where y crosses `level` (linear interpolation)."""
    out = []
    for i in range(len(x) - 1):
        a0, a1 = y[i] - level, y[i + 1] - level
        if a0 == 0:
            out.append(x[i])
        elif a0 * a1 < 0:
            out.append(x[i] + (x[i + 1] - x[i]) * a0 / (a0 - a1))
    return out


def band_below(x, y, level, around):
    """(lo, hi) of the contiguous region around index `around` where y <= level. None at a sweep end."""
    if y[around] > level:
        return None, None
    cr = crossings(x, y, level)
    lo = max([c for c in cr if c <= x[around]], default=None)
    hi = min([c for c in cr if c >= x[around]], default=None)
    return lo, hi


def report(hfss, a, ports, out_dir, elapsed):
    os.makedirs(out_dir, exist_ok=True)
    rows = {}

    s_exprs = [f"dB(S({p},{p}))" for p in ports] + (["dB(S(P2,P1))"] if len(ports) == 2 else [])
    if len(ports) == 2:
        # what the hybrid's input sees with J2 lagging by 90 deg: active reflection at J1
        s_exprs.append("dB(ActiveS(P1:1))")
    sol = hfss.post.get_solution_data(expressions=s_exprs, setup_sweep_name="Setup1 : S")
    if not sol:
        s_exprs = [e for e in s_exprs if "Active" not in e]
        sol = hfss.post.get_solution_data(expressions=s_exprs, setup_sweep_name="Setup1 : S")
    for e in s_exprs:
        rows[e] = series(sol, e)

    ff_exprs = ["dB(RealizedGainRHCP)", "dB(RealizedGainLHCP)", "dB(AxialRatioValue)",
                "dB(RealizedGainTotal)", "dB(GainTotal)", "dB(DirTotal)"]
    sol = hfss.post.get_solution_data(expressions=ff_exprs, setup_sweep_name="Setup1 : FF",
                                      report_category="Far Fields", context="ff",
                                      primary_sweep_variable="Freq",
                                      variations={"Theta": ["0deg"], "Phi": ["0deg"], "Freq": ["All"]})
    ff = {e: series(sol, e) for e in ff_exprs}

    cuts = {}
    for phi in ("0deg", "90deg"):
        sol = hfss.post.get_solution_data(expressions=["dB(RealizedGainRHCP)", "dB(RealizedGainTotal)"],
                                          setup_sweep_name="Setup1 : FF",
                                          report_category="Far Fields", context="ff",
                                          primary_sweep_variable="Theta",
                                          variations={"Theta": ["All"], "Phi": [phi], "Freq": [f"{a.f0}GHz"]})
        cuts[phi] = (series(sol, "dB(RealizedGainRHCP)"), series(sol, "dB(RealizedGainTotal)"))

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
    with open(os.path.join(out_dir, "pattern_f0.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["theta_deg", "RHCP_phi0_dBic", "total_phi0_dBi", "RHCP_phi90_dBic", "total_phi90_dBi"])
        th = cuts["0deg"][0][0]
        for i in range(len(th)):
            w.writerow([th[i], cuts["0deg"][0][1][i], cuts["0deg"][1][1][i],
                        cuts["90deg"][0][1][i], cuts["90deg"][1][1][i]])

    # ---- summary against requirements
    lo, hi = a.f0 - a.bw / 2000, a.f0 + a.bw / 2000
    eps = 1e-6
    # the reflection that matters: S11 for one port, the active reflection for board A if available
    match_expr = "dB(ActiveS(P1:1))" if "dB(ActiveS(P1:1))" in rows else s_exprs[0]
    fs, s11 = rows[s_exprs[0]]
    band = [s for fq, s in zip(fs, s11) if lo - eps <= fq <= hi + eps]
    i_min = min(range(len(s11)), key=lambda i: s11[i])
    b_lo, b_hi = band_below(fs, s11, -10.0, i_min)
    fA, ar = ff["dB(AxialRatioValue)"]
    ar_band = [v for fq, v in zip(fA, ar) if lo - eps <= fq <= hi + eps]
    i_ar = min(range(len(ar)), key=lambda i: ar[i])
    ar_lo, ar_hi = band_below(fA, ar, 3.0, i_ar)
    fG, g = ff["dB(RealizedGainRHCP)"]
    g_band = [v for fq, v in zip(fG, g) if lo - eps <= fq <= hi + eps]
    gl = ff["dB(RealizedGainLHCP)"][1]
    gt = ff["dB(RealizedGainTotal)"][1]
    i0 = min(range(len(fG)), key=lambda i: abs(fG[i] - a.f0))
    eff = 10 ** ((ff["dB(GainTotal)"][1][i0] - ff["dB(DirTotal)"][1][i0]) / 10)

    def hpbw(theta, gain):
        pk = max(gain)
        cr = crossings(theta, gain, pk - 3)
        ipk = gain.index(pk)
        left = max([c for c in cr if c <= theta[ipk]], default=float("nan"))
        right = min([c for c in cr if c >= theta[ipk]], default=float("nan"))
        return right - left

    circular = a.board != "plain"
    pat = 0 if circular else 1   # plain patch is linear: use total gain for the beamwidth
    summ = {
        "design": design_name(a),
        "s11_min_dB": round(s11[i_min], 2),
        "s11_min_freq_GHz": round(fs[i_min], 4),
        "s11_worst_in_band_dB": round(max(band), 2),
        "s11_10dB_band_MHz": round((b_hi - b_lo) * 1e3, 1) if b_lo and b_hi else None,
        "s11_10dB_band_edges_GHz": [round(b_lo, 4) if b_lo else None, round(b_hi, 4) if b_hi else None],
        "axial_ratio_min_dB": round(ar[i_ar], 2),
        "axial_ratio_min_freq_GHz": round(fA[i_ar], 4),
        "axial_ratio_at_f0_dB": round(ar[i0], 2),
        "axial_ratio_worst_in_band_dB": round(max(ar_band), 2),
        "axial_ratio_3dB_band_MHz": round((ar_hi - ar_lo) * 1e3, 1) if ar_lo and ar_hi else None,
        "axial_ratio_3dB_band_edges_GHz": [round(ar_lo, 4) if ar_lo else None, round(ar_hi, 4) if ar_hi else None],
        "rhcp_gain_max_dBic": round(max(g), 2),
        "rhcp_gain_max_freq_GHz": round(fG[g.index(max(g))], 4),
        "rhcp_gain_at_f0_dBic": round(g[i0], 2),
        "rhcp_gain_min_in_band_dBic": round(min(g_band), 2),
        "rhcp_gain_max_in_band_dBic": round(max(g_band), 2),
        "realized_gain_total_at_f0_dBi": round(gt[i0], 2),
        "realized_gain_total_max_dBi": round(max(gt), 2),
        "directivity_at_f0_dBi": round(ff["dB(DirTotal)"][1][i0], 2),
        "radiation_efficiency_at_f0": round(eff, 3),
        "hpbw_deg_phi0_phi90": [round(hpbw(*cuts["0deg"][pat]), 1), round(hpbw(*cuts["90deg"][pat]), 1)],
        "rhcp_minus_lhcp_at_f0_dB": round(g[i0] - gl[i0], 1),
        "hand": "RHCP" if g[i0] > gl[i0] else "LHCP",
        "solve_minutes": round(elapsed / 60, 1),
        "options": {k: v for k, v in vars(a).items() if k not in ("project_dir", "out")},
    }
    if len(ports) == 2:
        fs2, s21 = rows["dB(S(P2,P1))"]
        k = min(range(len(fs2)), key=lambda i: abs(fs2[i] - a.f0))
        summ["isolation_s21_at_f0_dB"] = round(s21[k], 1)
        if match_expr != s_exprs[0]:
            act = rows[match_expr][1]
            summ["active_s11_worst_in_band_dB"] = round(
                max(s for fq, s in zip(fs, act) if lo - eps <= fq <= hi + eps), 2)
    try:  # input impedance at port 1 (for tuning the feed position)
        zs = hfss.post.get_solution_data(expressions=["re(Z(P1,P1))", "im(Z(P1,P1))"],
                                         setup_sweep_name="Setup1 : S")
        zr, zx = series(zs, "re(Z(P1,P1))")[1], series(zs, "im(Z(P1,P1))")[1]
        k0 = min(range(len(fs)), key=lambda i: abs(fs[i] - a.f0))
        summ["z_in_at_f0_ohm"] = [round(zr[k0], 1), round(zx[k0], 1)]
        summ["z_in_at_s11_min_ohm"] = [round(zr[i_min], 1), round(zx[i_min], 1)]
        with open(os.path.join(out_dir, "zin.csv"), "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["freq_GHz", "re_Zin_ohm", "im_Zin_ohm"])
            for i in range(0, len(fs), 10):
                w.writerow([fs[i], round(zr[i], 2), round(zx[i], 2)])
    except Exception as e:
        print("impedance export skipped:", e)
    hyb_lines = []
    if a.board in ("A", "SD"):
        # a real hybrid is not perfect: J2's power off by d dB and its phase off by p degrees from -90
        try:
            summ["hybrid_imbalance"] = []
            for d, p in HYBRID_CASES:
                worst_ar, min_g = -1e9, 1e9
                for sd, sp in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                    hfss.edit_sources({"P1:1": (f"{10 ** (-sd * d / 20):.5f}W", "0deg"),
                                       "P2:1": (f"{10 ** (sd * d / 20):.5f}W", f"{-90 + sp * p}deg")})
                    sol = hfss.post.get_solution_data(
                        expressions=["dB(AxialRatioValue)", "dB(RealizedGainRHCP)"], setup_sweep_name="Setup1 : FF",
                        report_category="Far Fields", context="ff", primary_sweep_variable="Freq",
                        variations={"Theta": ["0deg"], "Phi": ["0deg"], "Freq": ["All"]})
                    fq, arc = series(sol, "dB(AxialRatioValue)")
                    gc = series(sol, "dB(RealizedGainRHCP)")[1]
                    inb = [i for i, v in enumerate(fq) if lo - eps <= v <= hi + eps]
                    worst_ar = max(worst_ar, max(arc[i] for i in inb))
                    min_g = min(min_g, min(gc[i] for i in inb))
                summ["hybrid_imbalance"].append({"amplitude_dB": d, "phase_deg": p,
                                                 "axial_ratio_worst_in_band_dB": round(worst_ar, 2),
                                                 "rhcp_gain_min_in_band_dBic": round(min_g, 2)})
                hyb_lines.append(f"hybrid off by {d} dB and {p} deg (worst sign): axial ratio {worst_ar:.2f} dB, "
                                 f"RHCP gain at least {min_g:.2f} dBic in band (before the hybrid's own loss)")
        except Exception as e:
            print("hybrid imbalance cases skipped:", e)
        hfss.edit_sources({"P1:1": ("1W", "0deg"), "P2:1": ("1W", "-90deg")})
    try:  # mesh size and convergence, if this AEDT version exports it
        summ["adaptive_passes"], summ["tetrahedra"], summ["final_delta_s"] = mesh_stats(
            hfss, os.path.join(out_dir, "convergence.txt"))
    except Exception as e:
        print("convergence export skipped:", e)

    with open(os.path.join(out_dir, "summary.json"), "w") as fh:
        json.dump(summ, fh, indent=1)

    lines = [
        f"design: {design_name(a)}",
        f"S11 minimum: {s11[i_min]:.1f} dB at {fs[i_min]:.4f} GHz",
        f"worst S11 in {lo:.3f}-{hi:.3f} GHz: {max(band):.1f} dB (need <= {REQ['s11_db']})",
        f"-10 dB bandwidth: {summ['s11_10dB_band_MHz']} MHz",
        f"axial ratio minimum: {ar[i_ar]:.2f} dB at {fA[i_ar]:.4f} GHz; 3 dB bandwidth {summ['axial_ratio_3dB_band_MHz']} MHz",
        f"worst axial ratio in band: {max(ar_band):.2f} dB (need <= {REQ['ar_db']})",
        f"RHCP realized gain in band: {min(g_band):.2f} to {max(g_band):.2f} dBic (need >= {REQ['gain_dbic']})",
        f"total realized gain at f0: {gt[i0]:.2f} dBi; directivity {summ['directivity_at_f0_dBi']} dBi; "
        f"radiation efficiency {eff * 100:.0f} %",
        f"RHCP minus LHCP at f0: {g[i0] - gl[i0]:.1f} dB -> {summ['hand']}",
        f"HPBW phi=0: {summ['hpbw_deg_phi0_phi90'][0]:.0f} deg, phi=90: {summ['hpbw_deg_phi0_phi90'][1]:.0f} deg "
        f"(need >= {REQ['hpbw_deg']})",
    ]
    if "isolation_s21_at_f0_dB" in summ:
        lines.append(f"port isolation S21 at f0: {summ['isolation_s21_at_f0_dB']} dB")
    if "tetrahedra" in summ:
        lines.append(f"mesh: {summ['tetrahedra']} tetrahedra after {summ['adaptive_passes']} passes, "
                     f"delta S {summ.get('final_delta_s')}")
    if "z_in_at_f0_ohm" in summ:
        lines.append(f"input impedance at f0: {summ['z_in_at_f0_ohm'][0]} {summ['z_in_at_f0_ohm'][1]:+} j ohm; "
                     f"at the S11 minimum: {summ['z_in_at_s11_min_ohm'][0]} {summ['z_in_at_s11_min_ohm'][1]:+} j ohm")
    lines += hyb_lines
    lines.append(f"solve time: {elapsed / 60:.1f} min")
    text = "\n".join(lines)
    with open(os.path.join(out_dir, "summary.txt"), "w") as fh:
        fh.write(text + "\n")
    print(text)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 4, figsize=(20, 4))
        for e in s_exprs:
            ax[0].plot(*rows[e], label=e)
        ax[0].axhline(-10, ls="--", c="k", lw=0.8)
        ax[0].axvspan(lo, hi, alpha=0.1)
        ax[0].set(xlabel="GHz", ylabel="dB", title="S-parameters")
        ax[0].legend()
        ax[1].plot(fA, ar)
        ax[1].axhline(3, ls="--", c="k", lw=0.8)
        ax[1].axvspan(lo, hi, alpha=0.1)
        ax[1].set(xlabel="GHz", ylabel="dB", title="Axial ratio at boresight", ylim=(0, max(10, min(40, max(ar)))))
        ax[2].plot(fG, g, label="RHCP")
        ax[2].plot(fG, gt, label="total")
        ax[2].axvspan(lo, hi, alpha=0.1)
        ax[2].set(xlabel="GHz", ylabel="dBi(c)", title="Realized gain at boresight")
        ax[2].legend()
        for phi, c in cuts.items():
            ax[3].plot(*c[pat], label=f"phi={phi}")
        ax[3].set(xlabel="theta (deg)", ylabel="dBi(c)", ylim=(-30, 10),
                  title=f"{'RHCP' if circular else 'Total'} realized gain at {a.f0} GHz")
        ax[3].legend()
        fig.suptitle(design_name(a) + " (HFSS)")
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, "results.png"), dpi=110)
    except Exception as e:  # plots are a convenience
        print("plotting skipped:", e)


def main():
    a = parse()
    if a.box and a.sma:
        raise SystemExit("--box and --sma are not supported together")
    if not any(k.startswith("ANSYSEM") and "ROOT" in k for k in os.environ):
        # a shell opened before AEDT was installed doesn't have its variables yet: read them from the registry
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
                for i in range(winreg.QueryInfoKey(key)[1]):
                    k, v, _ = winreg.EnumValue(key, i)
                    if k.startswith("ANSYSEM") and "ROOT" in k:
                        os.environ[k] = v
        except Exception as e:
            print("could not read the AEDT install path from the registry:", e)
    from ansys.aedt.core import Hfss  # imported late so --help works without AEDT

    os.makedirs(a.project_dir, exist_ok=True)
    project = os.path.join(a.project_dir, aedt_name(a) + ".aedt")
    for stale in (project, project + ".lock"):
        if os.path.exists(stale):
            os.remove(stale)
    hfss = Hfss(project=project, design=aedt_name(a), solution_type="Modal", version=a.version,
                non_graphical=not a.graphical, new_desktop=True, student_version=True)
    try:
        if a.sma:
            mp = hfss.materials.add_material("sma_ptfe")
            mp.permittivity = SMA_ER
            mp.dielectric_loss_tangent = 0.0004
        ports = build(hfss, a)
        hfss.save_project()
        t0 = time.time()
        solve(hfss, a, ports)
        report(hfss, a, ports, os.path.join(a.out, design_name(a)), time.time() - t0)
        hfss.save_project()
    finally:
        hfss.release_desktop(close_projects=True, close_desktop=True)


if __name__ == "__main__":
    main()
