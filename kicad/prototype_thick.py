"""PROTOTYPE: 3 mm thick patch boards, each made of two 1.524 mm PTFE boards bonded together.

JLC sells ZYF255DA PTFE as a two-layer 1.524 mm board, so a 3.05 mm substrate is built from two:

  TOP board     patch copper on its front, NO copper on its back (the bond face)
  BOTTOM board  NO copper on its front (the bond face), ground plane and SMA on its back

The two are bonded face to face with no air between them and aligned by the four M3 holes. Each feed is
a 0.5 mm wire soldered to the SMA centre pad, passed up through both boards and soldered to the patch.
Neither bond face has copper, so the boards sit flat on each other.

Dimensions come from sim/thick_design.json (HFSS, 60 mm board on a 100 mm metal face).
This does not touch the rev-1 boards, ../fab or generate_boards.py; it only reuses helpers from it.

Run with KiCad's bundled Python (KiCad 8 or later; last run with KiCad 10):
  "C:\\Program Files\\KiCad\\8.0\\bin\\python.exe" prototype_thick.py [--gerbers]
  macOS: /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 prototype_thick.py [--gerbers]
Output: prototype_thick/<name>_TOP/..., prototype_thick/<name>_BOTTOM/... and an SVG of each copper side.
"""
import json
import os
import subprocess

import pcbnew

import generate_boards as g

mm = pcbnew.FromMM
OUT = os.path.join(g.HERE, "prototype_thick")
DESIGN = os.path.join(g.REPO, "sim", "thick_design.json")
PIN_DRILL = 0.6     # finished hole for a 0.5 mm feed wire (the simulated probe is 0.5 mm)
PIN_PAD = 1.2       # solder pad around the wire, on the outer face only
OUTWARD = {"x": (1.0, 0.0), "y": (0.0, -1.0)}   # +y physical = up in the top view = -y in KiCad


def feed_xy(spec, axis):
    """Feed point in KiCad mm. feed_y is the simulation's sideways offset (+y = up = -y in KiCad), x port only."""
    cx, cy = g.centre()
    ux, uy = OUTWARD[axis]
    side = spec.get("feed_y", 0.0) if axis == "x" else 0.0
    return (cx + ux * spec["feed"], cy + uy * spec["feed"] - side)


def flip(fp):
    try:
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)    # KiCad 9 and later
    except AttributeError:
        fp.Flip(fp.GetPosition(), False)                               # KiCad 8


def pin_pad(board, ref, xy, layer, net):
    """Plated hole for the feed wire with copper on one outer face only, so the bond face stays bare."""
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    fp.SetPosition(g.v(*xy))
    board.Add(fp)
    pad = pcbnew.PAD(fp)
    pad.SetNumber("1")
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetSize(g.v(PIN_PAD, PIN_PAD))
    pad.SetDrillSize(g.v(PIN_DRILL, PIN_DRILL))
    ls = pcbnew.LSET()
    ls.AddLayer(layer)
    ls.AddLayer(pcbnew.F_Mask if layer == pcbnew.F_Cu else pcbnew.B_Mask)
    pad.SetLayerSet(ls)
    if hasattr(pad, "SetRemoveUnconnected"):
        # KiCad 9 and later put a plated-hole pad on every copper layer whatever the layer set says, which
        # would leave a 35 um copper ring on the bond face and hold the two boards apart. Drop the pad's
        # copper on any layer where nothing connects to it, the bond face included.
        pad.SetRemoveUnconnected(True)
        pad.SetKeepTopBottom(False)
    pad.SetPosition(g.v(*xy))
    pad.SetNet(net)
    fp.Add(pad)
    return fp


def ground(board, gnd_net):
    """Ground plane over the whole back, pulled back 0.5 mm from each mounting hole."""
    import math
    x0, y0 = g.ORIGIN
    s, i = g.COMMON["board"], g.COMMON["hole_inset"]
    z = pcbnew.ZONE(board)
    z.SetLayer(pcbnew.B_Cu)
    z.SetNet(gnd_net)
    z.SetLocalClearance(mm(g.COMMON["gnd_clear"]))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetMinThickness(mm(0.2))
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_NEVER)
    z.SetZoneName("GND_plane")
    ol = z.Outline()
    ol.NewOutline()
    for x, y in [(x0, y0), (x0 + s, y0), (x0 + s, y0 + s), (x0, y0 + s)]:
        ol.Append(mm(x), mm(y))
    board.Add(z)
    for hx, hy in [(x0 + i, y0 + i), (x0 + s - i, y0 + i), (x0 + s - i, y0 + s - i), (x0 + i, y0 + s - i)]:
        k = pcbnew.ZONE(board)                 # keep-out so the pour stays clear of the unplated hole
        k.SetIsRuleArea(True)
        if hasattr(k, "SetDoNotAllowZoneFills"):
            k.SetDoNotAllowZoneFills(True)          # KiCad 9 and later
        else:
            k.SetDoNotAllowCopperPour(True)         # KiCad 8
        k.SetDoNotAllowTracks(False)
        k.SetDoNotAllowVias(False)
        k.SetDoNotAllowPads(False)
        k.SetDoNotAllowFootprints(False)
        k.SetLayer(pcbnew.B_Cu)
        ko = k.Outline()
        ko.NewOutline()
        for n in range(36):
            a = 2 * math.pi * n / 36
            ko.Append(mm(hx + 2.1 * math.cos(a)), mm(hy + 2.1 * math.sin(a)))
        board.Add(k)


def new_board(name, copper_sides):
    out_dir = os.path.join(OUT, name)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name + ".kicad_pcb")
    for ext in (".kicad_pcb", ".kicad_pro", ".kicad_prl"):
        if os.path.exists(os.path.join(out_dir, name + ext)):
            os.remove(os.path.join(out_dir, name + ext))
    board = pcbnew.NewBoard(path)
    board.SetCopperLayerCount(2)
    board.GetDesignSettings().SetBoardThickness(mm(1.524 + copper_sides * 0.035))
    g.add_outline(board)
    g.add_holes(board)
    return board, path


def build_top(name, spec):
    board, path = new_board(name + "_TOP", 1)
    sig = g.add_net(board, "PATCH")
    g.add_patch(board, sig, spec["patch"], spec["cut"], spec["cut_corners"])
    cx, cy = g.centre()
    for n, axis in enumerate(spec["ports"], 1):
        pin_pad(board, f"P{n}", feed_xy(spec, axis), pcbnew.F_Cu, sig)
    # No solder mask anywhere on the front (mask around the patch shifted the thin boards 6 to 8 MHz in HFSS)
    # and no silkscreen: ink cannot sit in a mask opening, and the back of this board is the bond face.
    # The matching BOTTOM board carries the labels.
    g.add_bare_top(board)
    board.BuildConnectivity()
    pcbnew.SaveBoard(path, board)
    return path


def build_bottom(name, spec):
    board, path = new_board(name + "_BOTTOM", 1)
    gnd = g.add_net(board, "GND")
    cx, cy = g.centre()
    for n, axis in enumerate(spec["ports"], 1):
        sig = g.add_net(board, f"FEED{n}")      # the feeds only join at the patch, which is on the TOP board
        ux, uy = OUTWARD[axis]
        xy = feed_xy(spec, axis)
        fp = g.load_fp("Connector_Coaxial", g.SMA_FOOTPRINT)
        board.Add(fp)
        fp.SetPosition(g.v(*xy))
        flip(fp)
        fp.SetOrientationDegrees(45)
        fp.SetReference(f"J{n}")
        fp.Reference().SetPosition(g.v(xy[0] + ux * 7.0, xy[1] + uy * 7.0))
        fp.Reference().SetTextAngleDegrees(0)
        fp.SetValue("Wurth WR-SMA 60312102114405")
        for p in fp.Pads():
            p.SetNet(sig if p.GetNumber() == "1" else gnd)
        pin_pad(board, f"P{n}", xy, pcbnew.B_Cu, sig)
    ground(board, gnd)
    x0, y0 = g.ORIGIN
    s = g.COMMON["board"]
    g.add_text(board, f"PROTO 3MM  {spec['title']}  BOTTOM", (cx, y0 + 9.5), pcbnew.B_SilkS, 1.0, True)
    dims = f"TOP BOARD: L={spec['patch']:.2f} FEED={spec['feed']:.2f}"
    if spec.get("feed_y"):
        dims += f"/{spec['feed_y']:.2f}"
    if spec["cut_corners"]:
        dims += f" CUT={spec['cut']:.2f}"
    g.add_text(board, dims, (cx, y0 + 12.0), pcbnew.B_SilkS, 0.9, True)
    g.add_text(board, "ZYF255DA PTFE 1.52MM  ENIG  NO COPPER ON FRONT", (cx, y0 + s - 7.5), pcbnew.B_SilkS, 1.0, True)
    if spec.get("back_note"):
        g.add_text(board, spec["back_note"], (cx, y0 + s - 10.5), pcbnew.B_SilkS, 1.0, True)
    board.BuildConnectivity()
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(path, board)
    return path


def export_svg(cli, path, copper, overlay, mirror):
    """Preview picture. KiCad draws copper over silkscreen in one SVG, which hides the text on a ground plane,
    so the copper and the silkscreen/paste are exported separately and the second is laid over the first.
    The BOTTOM board is mirrored: it is drawn as seen from the back."""
    base = os.path.splitext(path)[0]
    parts = []
    for n, layers in enumerate((copper, overlay)):
        tmp = f"{base}_{n}.svg"
        subprocess.run([cli, "pcb", "export", "svg", "--layers", layers + ",Edge.Cuts", "--page-size-mode", "2",
                        "--exclude-drawing-sheet", "-o", tmp, path] + (["--mirror"] if mirror else []),
                       capture_output=True)
        if not os.path.exists(tmp):
            return False
        parts.append(open(tmp, encoding="utf-8").read())
        os.remove(tmp)
    under = parts[0][:parts[0].rindex("</svg>")]
    over = parts[1][parts[1].index("<g "):]
    with open(base + ".svg", "w", encoding="utf-8") as fh:
        fh.write(under + over)
    return True


def check(cli, path, copper, overlay, mirror=False):
    out_dir = os.path.dirname(path)
    report = os.path.join(out_dir, "drc.json")
    # Refill through kicad-cli so the ground pour obeys the board-edge clearance, as generate_boards.py does.
    subprocess.run([cli, "pcb", "drc", "--severity-all", "--refill-zones", "--save-board",
                    "--format", "json", "-o", report, path], capture_output=True)
    d = json.load(open(report))
    os.remove(report)
    # The feed hole sits under the SMA centre pad on purpose (the wire is soldered there), so KiCad's
    # "plated hole inside a courtyard" check is expected on the BOTTOM boards and is not counted.
    viol = [x["type"] for x in d["violations"] if x["type"] != "pth_inside_courtyard"]
    unc = len(d["unconnected_items"])
    svg = export_svg(cli, path, copper, overlay, mirror)
    return ("DRC clean" if not viol and not unc else f"DRC: {sorted(set(viol))}, {unc} unconnected") +            ("; svg" if svg else "; no svg")


def export_gerbers(cli, path):
    """JLC-ready Gerber and drill zip in ../fab/, the same layer set as the rev-1 boards."""
    import shutil
    name = os.path.splitext(os.path.basename(path))[0]
    fab = os.path.join(g.REPO, "fab", name)
    shutil.rmtree(fab, ignore_errors=True)
    os.makedirs(fab)
    layers = "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts"
    subprocess.run([cli, "pcb", "export", "gerbers", "--layers", layers, "-o", fab + os.sep, path], capture_output=True)
    subprocess.run([cli, "pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th",
                    "-o", fab + os.sep, path], capture_output=True)
    shutil.make_archive(fab, "zip", fab)
    return f"; gerbers -> fab/{name}.zip"


def main():
    import sys
    gerbers = "--gerbers" in sys.argv
    designs = json.load(open(DESIGN))
    cli = g.kicad_cli()
    os.makedirs(OUT, exist_ok=True)
    for name, d in designs["boards"].items():
        spec = dict(title=d["title"], patch=d["L"], feed=d["feed"], cut=d.get("cut", 0.0),
                    cut_corners=("TL", "BR") if d.get("cut") else (), ports=tuple(d["ports"]),
                    back_note=d.get("back_note"), feed_y=d.get("feed_y", 0.0))
        top = build_top(name, spec)
        bot = build_bottom(name, spec)
        for label, path, args in (("_TOP", top, ("F.Cu", "F.SilkS")), ("_BOTTOM", bot, ("B.Cu", "B.SilkS,B.Paste", True))):
            msg = check(cli, path, *args) if cli else "saved"
            if cli and gerbers:
                msg += export_gerbers(cli, path)
            print(name + label + ":", msg)


if __name__ == "__main__":
    main()
