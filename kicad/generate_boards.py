"""Generate the rev-1 S-band patch boards with KiCad's Python API.

Every board is rebuilt from scratch from the numbers in BOARDS below, then zone-filled,
DRC-checked and rendered with kicad-cli. Edit BOARDS after simulation and re-run.

Run with KiCad's bundled Python (KiCad 10):
  Windows: "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" generate_boards.py
  macOS:   /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 generate_boards.py

Options:
  --variants -0.3 0 0.3   also build copies with the patch side changed by these amounts (mm)
  --gerbers               also export JLC-ready Gerber + drill zips into ../fab/
  --only A_dualfeed       build just the named board(s)
"""
import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys

import wx

import pcbnew

_APP = wx.App(False)  # pcbnew needs a wx app for footprint loading and zone filling

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

# ------------------------------------------------------------------ design numbers (mm)
# Patch, feed and cut values are from the openEMS simulations in sim/results_openems/ (2.425 GHz).
# The hand formulas in patch_calc.py read about 2.7 % high in frequency for these boards.
COMMON = dict(
    board=60.0,        # square board side
    hole_inset=4.0,    # mounting-hole centre from board edge (placeholder: confirm with Structures)
    via_drill=0.5,     # probe via drill (the feed probe is this plated via)
    via_pad=0.8,       # probe via pad diameter
    gnd_clear=0.4,     # ground-plane clearance around the probe via / SMA signal pad
)

BOARDS = {
    # ---- Rogers RO4350B, 1.52 mm (design Dk 3.66) ----
    # Square patch, two orthogonal feeds. Drive through an external 90-deg hybrid.
    # RHCP (IEEE, wave leaving the patch) when J2 lags J1 by 90 deg.
    "A_dualfeed": dict(
        title="A: DUAL-FEED (HYBRID)",
        material="RO4350B 1.52MM",
        patch=31.40,
        feed=5.80,               # probe offset from patch centre
        ports=("x", "y"),        # J1 on +x axis, J2 on +y axis (up in the top view)
        cut_corners=(),
        cut=0.0,
        back_note="RHCP: J2 LAGS J1 BY 90 DEG",
    ),
    # Single feed on +x, corners truncated on the top-left/bottom-right diagonal (top view).
    # Truncating a diagonal raises that diagonal mode's resonance, so it leads by ~90 deg at f0;
    # with TL/BR cut the field turns counter-clockwise seen from the front = RHCP.
    # Confirmed RHCP in simulation, from the far field and from the time-domain field rotation.
    "B_cutcorner_RHCP": dict(
        title="B: CUT-CORNER RHCP",
        material="RO4350B 1.52MM",
        patch=31.54,
        feed=5.90,
        ports=("x",),
        cut_corners=("TL", "BR"),
        cut=3.13,                # leg length of each truncated corner triangle
        back_note=None,
    ),
    # ---- JLC PTFE ZYF255DA, 1.52 mm (Dk 2.55, Df 0.0018): about 0.7 dB more gain ----
    "A_dualfeed_PTFE": dict(
        title="A-PTFE: DUAL-FEED (HYBRID)",
        material="ZYF255DA PTFE 1.52MM",
        patch=37.38,
        feed=6.90,
        ports=("x", "y"),
        cut_corners=(),
        cut=0.0,
        back_note="RHCP: J2 LAGS J1 BY 90 DEG",
    ),
    "B_cutcorner_RHCP_PTFE": dict(
        title="B-PTFE: CUT-CORNER RHCP",
        material="ZYF255DA PTFE 1.52MM",
        patch=37.56,
        feed=7.00,
        ports=("x",),
        cut_corners=("TL", "BR"),
        cut=3.80,
        back_note=None,
    ),
    # Same board re-tuned for mounting flat on a 100 mm metal face (a 1U side): the larger ground
    # raises Q from about 44 to 53, so the corner cut is smaller.
    "B_cutcorner_RHCP_PTFE_face100": dict(
        title="B-PTFE-F: CUT-CORNER RHCP",
        material="ZYF255DA PTFE 1.52MM",
        patch=37.52,
        feed=7.00,
        ports=("x",),
        cut_corners=("TL", "BR"),
        cut=3.50,
        back_note="TUNED FOR A 100 MM METAL FACE",
    ),
}

ORIGIN = (100.0, 100.0)    # board top-left in the KiCad sheet

# Connector: Wurth WR-SMA 60312102114405, surface-mount vertical SMA jack (KiCad stock footprint).
# It solders flat to the bottom ground, so no legs pass through the patch.
SMA_FOOTPRINT = "SMA_Wurth_60312102114405_Vertical"
SMA_DIRECT_MIN_FEED = 5.8   # mm; 8.12 mm courtyards rotated 45 deg clear each other only beyond this
SMA_OFFSET_CENTRE = 8.2     # mm from patch centre when the SMAs must move out (axis-aligned courtyards clear)
SMA_TRACE_WIDTH = 1.2       # mm; probe-to-SMA trace on the bottom layer (fits the 2.4 mm pad gap)

mm = pcbnew.FromMM


# ------------------------------------------------------------------ tool locations
def footprint_root():
    for var in ("KICAD10_FOOTPRINT_DIR", "KICAD9_FOOTPRINT_DIR", "KICAD_FOOTPRINT_DIR"):
        if os.environ.get(var) and os.path.isdir(os.environ[var]):
            return os.environ[var]
    candidates = [
        "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints",
        "/usr/share/kicad/footprints",
        "/usr/local/share/kicad/footprints",
    ]
    candidates += sorted(glob.glob(r"C:\Program Files\KiCad\*\share\kicad\footprints"), reverse=True)
    for c in candidates:
        if os.path.isdir(c):
            return c
    sys.exit("KiCad footprint library not found: set KICAD10_FOOTPRINT_DIR")


def kicad_cli():
    found = shutil.which("kicad-cli")
    if found:
        return found
    candidates = ["/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli", "/usr/bin/kicad-cli"]
    candidates += sorted(glob.glob(r"C:\Program Files\KiCad\*\bin\kicad-cli.exe"), reverse=True)
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None


FP_ROOT = footprint_root()


# ------------------------------------------------------------------ geometry helpers
def v(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def centre():
    s = COMMON["board"]
    return ORIGIN[0] + s / 2, ORIGIN[1] + s / 2


def add_net(board, name):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    return net


def add_outline(board):
    x0, y0 = ORIGIN
    s = COMMON["board"]
    pts = [(x0, y0), (x0 + s, y0), (x0 + s, y0 + s), (x0, y0 + s)]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(v(*a))
        seg.SetEnd(v(*b))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(mm(0.1))
        board.Add(seg)


def patch_polygon(side, cut, cut_corners):
    """Square patch of `side`, with the named corners ('TL','TR','BR','BL', top view) truncated by `cut`."""
    cx, cy = centre()
    a = side / 2
    corners = {"TL": (-a, -a), "TR": (a, -a), "BR": (a, a), "BL": (-a, a)}   # KiCad y points down
    order = ["TL", "TR", "BR", "BL"]
    pts = []
    for i, k in enumerate(order):
        x, y = corners[k]
        if k in cut_corners:
            px, py = corners[order[i - 1]]
            nx, ny = corners[order[(i + 1) % 4]]
            pts.append((x + (px - x) / side * cut, y + (py - y) / side * cut))
            pts.append((x + (nx - x) / side * cut, y + (ny - y) / side * cut))
        else:
            pts.append((x, y))
    return [(cx + x, cy + y) for x, y in pts]


def add_patch(board, net, side, cut, cut_corners):
    pts = patch_polygon(side, cut, cut_corners)
    for layer in (pcbnew.F_Cu, pcbnew.F_Mask):   # copper + identical mask opening = bare patch
        shp = pcbnew.PCB_SHAPE(board)
        shp.SetShape(pcbnew.SHAPE_T_POLY)
        shp.SetPolyPoints([v(*p) for p in pts])
        shp.SetFilled(True)
        shp.SetWidth(0)
        shp.SetLayer(layer)
        if layer == pcbnew.F_Cu:
            shp.SetNet(net)
        board.Add(shp)


def load_fp(lib, name):
    return pcbnew.FootprintLoad(os.path.join(FP_ROOT, lib + ".pretty"), name)


def add_feed(board, ref, probe_xy, outward, offset, sig_net, gnd_net):
    """Surface-mount vertical SMA on the bottom, fed by a plated via (the probe) up to the patch.

    offset == 0: the SMA centre pad sits on the probe (via in pad).
    offset > 0:  the SMA sits `offset` mm further out along `outward`, joined to the probe by a short
                 bottom-layer trace that runs through the gap between the SMA's two ground pads.
    """
    sx, sy = probe_xy[0] + outward[0] * offset, probe_xy[1] + outward[1] * offset
    fp = load_fp("Connector_Coaxial", SMA_FOOTPRINT)
    board.Add(fp)                             # must be on a board before flipping
    fp.SetPosition(v(sx, sy))
    fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    # The footprint's open channel (no ground pad) runs along its local x axis.
    if offset > 0:
        fp.SetOrientationDegrees(0 if abs(outward[0]) > abs(outward[1]) else 90)
    else:
        fp.SetOrientationDegrees(45)          # diamond: lets two SMAs sit closer together
    fp.SetReference(ref)
    fp.Reference().SetPosition(v(sx + outward[0] * 7.0, sy + outward[1] * 7.0))   # label outside the body
    fp.Reference().SetTextAngleDegrees(0)
    fp.SetValue("Wurth WR-SMA 60312102114405")
    for p in fp.Pads():
        p.SetNet(sig_net if p.GetNumber() == "1" else gnd_net)

    via = pcbnew.PCB_VIA(board)
    via.SetPosition(v(*probe_xy))
    via.SetDrill(mm(COMMON["via_drill"]))
    via.SetWidth(mm(COMMON["via_pad"]))
    via.SetNet(sig_net)
    board.Add(via)

    if offset > 0:
        trk = pcbnew.PCB_TRACK(board)
        trk.SetStart(v(*probe_xy))
        trk.SetEnd(v(sx, sy))
        trk.SetWidth(mm(SMA_TRACE_WIDTH))
        trk.SetLayer(pcbnew.B_Cu)
        trk.SetNet(sig_net)
        board.Add(trk)


def add_holes(board):
    x0, y0 = ORIGIN
    s, i = COMMON["board"], COMMON["hole_inset"]
    for n, (x, y) in enumerate([(x0 + i, y0 + i), (x0 + s - i, y0 + i),
                                (x0 + s - i, y0 + s - i), (x0 + i, y0 + s - i)], 1):
        fp = load_fp("MountingHole", "MountingHole_3.2mm_M3")
        fp.SetPosition(v(x, y))
        fp.SetReference(f"H{n}")
        fp.Reference().SetVisible(False)
        board.Add(fp)


def add_ground(board, gnd_net):
    x0, y0 = ORIGIN
    s = COMMON["board"]
    z = pcbnew.ZONE(board)
    z.SetLayer(pcbnew.B_Cu)
    z.SetNet(gnd_net)
    z.SetLocalClearance(mm(COMMON["gnd_clear"]))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetMinThickness(mm(0.2))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
    z.SetZoneName("GND_plane")
    ol = z.Outline()
    ol.NewOutline()
    for x, y in [(x0, y0), (x0 + s, y0), (x0 + s, y0 + s), (x0, y0 + s)]:
        ol.Append(mm(x), mm(y))
    board.Add(z)


def add_text(board, text, xy, layer, size=1.2, mirrored=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(v(*xy))
    t.SetLayer(layer)
    t.SetMirrored(mirrored)
    t.SetTextSize(v(size, size))
    t.SetTextThickness(mm(size * 0.15))
    board.Add(t)


# ------------------------------------------------------------------ build
def build(name, spec):
    out_dir = os.path.join(HERE, name)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name + ".kicad_pcb")
    for ext in (".kicad_pcb", ".kicad_pro", ".kicad_prl"):
        old = os.path.join(out_dir, name + ext)
        if os.path.exists(old):
            os.remove(old)
    board = pcbnew.NewBoard(path)
    board.SetCopperLayerCount(2)
    # Material is chosen on the JLC order (see spec["material"]); this is the finished thickness.
    board.GetDesignSettings().SetBoardThickness(mm(1.524 + 2 * 0.035))

    gnd = add_net(board, "GND")
    sig = add_net(board, "PATCH")
    add_outline(board)
    add_patch(board, sig, spec["patch"], spec["cut"], spec["cut_corners"])
    cx, cy = centre()
    f = spec["feed"]
    outward = {"x": (1.0, 0.0), "y": (0.0, -1.0)}   # +y physical = up in the top view = -y in KiCad
    # One SMA always sits on its probe. Two SMAs (board A) only fit on their probes when the feed is
    # at least SMA_DIRECT_MIN_FEED from centre; otherwise move them out to SMA_OFFSET_CENTRE.
    two = len(spec["ports"]) == 2
    offset = 0.0 if (not two or f >= SMA_DIRECT_MIN_FEED) else SMA_OFFSET_CENTRE - f
    for n, axis in enumerate(spec["ports"], 1):
        ux, uy = outward[axis]
        add_feed(board, f"J{n}", (cx + ux * f, cy + uy * f), (ux, uy), offset, sig, gnd)
    add_holes(board)
    add_ground(board, gnd)

    x0, y0 = ORIGIN
    s = COMMON["board"]
    add_text(board, f"SSI S-BAND PATCH REV1  {spec['title']}", (cx, y0 + 7.5), pcbnew.F_SilkS)
    dims = f"L={spec['patch']:.2f} FEED={spec['feed']:.2f}"
    if spec["cut_corners"]:
        dims += f" CUT={spec['cut']:.2f}"
    add_text(board, dims, (cx, y0 + s - 7.5), pcbnew.F_SilkS, 1.0)
    add_text(board, f"{spec.get('material', 'RO4350B 1.52MM')}  ENIG  NO MASK ON PATCH", (cx, y0 + s - 7.5),
             pcbnew.B_SilkS, 1.0, True)
    if spec.get("back_note"):
        add_text(board, spec["back_note"], (cx, y0 + s - 11), pcbnew.B_SilkS, 1.0, True)

    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(path, board)
    return path


def check_and_render(cli, name, path, gerbers):
    import json
    out_dir = os.path.dirname(path)
    report = os.path.join(out_dir, "drc.json")
    subprocess.run([cli, "pcb", "drc", "--severity-all", "--refill-zones", "--save-board",
                    "--format", "json", "-o", report, path], capture_output=True)
    with open(report) as fh:
        d = json.load(fh)
    os.remove(report)
    n_v, n_u = len(d["violations"]), len(d["unconnected_items"])
    status = "DRC clean" if n_v == n_u == 0 else f"DRC: {n_v} violations, {n_u} unconnected"
    renders = os.path.join(REPO, "docs", "renders")
    os.makedirs(renders, exist_ok=True)
    for side in ("top", "bottom"):
        subprocess.run([cli, "pcb", "render", "--side", side, "--width", "900", "--height", "900",
                        "--quality", "basic", "--background", "opaque",
                        "-o", os.path.join(renders, f"{name}_{side}.png"), path], capture_output=True)
    if gerbers:
        fab = os.path.join(REPO, "fab", name)
        shutil.rmtree(fab, ignore_errors=True)
        os.makedirs(fab)
        layers = "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts"
        subprocess.run([cli, "pcb", "export", "gerbers", "--layers", layers, "-o", fab + os.sep, path],
                       capture_output=True)
        subprocess.run([cli, "pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th",
                        "-o", fab + os.sep, path], capture_output=True)
        shutil.make_archive(fab, "zip", fab)
        status += f"; gerbers -> fab/{name}.zip"
    return status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", nargs="*", type=float, default=[],
                    help="patch-side offsets in mm, e.g. -0.3 0 0.3")
    ap.add_argument("--gerbers", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    args = ap.parse_args()

    cli = kicad_cli()
    if cli is None:
        print("kicad-cli not found: boards are saved but zones, DRC and renders are skipped")

    jobs = []
    for name, spec in BOARDS.items():
        if args.only and name not in args.only:
            continue
        if args.variants:
            for d in args.variants:
                s = dict(spec, patch=round(spec["patch"] + d, 3))
                jobs.append((f"{name}_L{s['patch']:.2f}".replace(".", "p"), s))
        else:
            jobs.append((name, spec))

    for name, spec in jobs:
        path = build(name, spec)
        msg = check_and_render(cli, name, path, args.gerbers) if cli else "saved"
        print(f"{name}: {msg}")


if __name__ == "__main__":
    main()
