"""Independent check of the KiCad boards and Gerbers against the simulated designs. Reads only.

It does not use KiCad or generate_boards.py: the .kicad_pcb files are parsed as text, and the Gerber zips
in fab/ are unpacked in memory. For each antenna option in README.md's table it checks
  - the patch: side, which corners are cut and by how much (the F.Cu polygon in the board and in the Gerber)
  - the feed: position of each plated feed hole relative to the patch centre
  - 3 mm boards: TOP and BOTTOM feed holes line up, and the two bond faces carry no copper

  python sim/check_boards.py      # prints a table; exit code 1 if anything is off by more than 0.005 mm
"""
import io
import math
import os
import re
import sys
import zipfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOL = 0.005

# name: board file, Gerber zip, patch side, corner cut, feeds as (x, y) from the patch centre in the
# simulation's axes (x right, y up, seen from the front), and whether the patch is on this board
P = "kicad/prototype_thick/"
BOARDS = [
    ("Cut corner, 1.5 mm", "kicad/Cutcorner_antenna/Cutcorner antenna.kicad_pcb", "fab/Cutcorner_antenna.zip",
     37.52, 3.50, [(7.00, 0.0)], True),
    ("Dual feed, 1.5 mm", "kicad/A_dualfeed_PTFE_face100/A_dualfeed_PTFE_face100.kicad_pcb",
     "fab/A_dualfeed_PTFE_face100.zip", 37.28, 0.0, [(5.80, 0.0), (0.0, 5.80)], True),
    ("Dual feed, 1.5 mm, -0.3 mm", "kicad/A_dualfeed_PTFE_face100_L36p98/A_dualfeed_PTFE_face100_L36p98.kicad_pcb",
     "fab/A_dualfeed_PTFE_face100_L36p98.zip", 36.98, 0.0, [(5.80, 0.0), (0.0, 5.80)], True),
    ("Dual feed, 1.5 mm, +0.3 mm", "kicad/A_dualfeed_PTFE_face100_L37p58/A_dualfeed_PTFE_face100_L37p58.kicad_pcb",
     "fab/A_dualfeed_PTFE_face100_L37p58.zip", 37.58, 0.0, [(5.80, 0.0), (0.0, 5.80)], True),
    ("Cut corner, 3 mm, TOP", P + "B_cutcorner_RHCP_PTFE_3mm_TOP/B_cutcorner_RHCP_PTFE_3mm_TOP.kicad_pcb",
     "fab/B_cutcorner_RHCP_PTFE_3mm_TOP.zip", 37.10, 5.55, [(8.00, 2.18)], True),
    ("Cut corner, 3 mm, BOTTOM", P + "B_cutcorner_RHCP_PTFE_3mm_BOTTOM/B_cutcorner_RHCP_PTFE_3mm_BOTTOM.kicad_pcb",
     "fab/B_cutcorner_RHCP_PTFE_3mm_BOTTOM.zip", 37.10, 5.55, [(8.00, 2.18)], False),
    ("Dual feed, 3 mm, TOP", P + "A_dualfeed_PTFE_3mm_TOP/A_dualfeed_PTFE_3mm_TOP.kicad_pcb",
     "fab/A_dualfeed_PTFE_3mm_TOP.zip", 36.39, 0.0, [(6.70, 0.0), (0.0, 6.70)], True),
    ("Dual feed, 3 mm, BOTTOM", P + "A_dualfeed_PTFE_3mm_BOTTOM/A_dualfeed_PTFE_3mm_BOTTOM.kicad_pcb",
     "fab/A_dualfeed_PTFE_3mm_BOTTOM.zip", 36.39, 0.0, [(6.70, 0.0), (0.0, 6.70)], False),
]
BOND_FACE = {"TOP": "B", "BOTTOM": "F"}     # the face of each 3 mm board that is glued: must have no copper


# ---------------------------------------------------------------- .kicad_pcb (S-expressions)
def parse(text):
    tok = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    stack, cur = [], []
    for t in tok:
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
        else:
            cur.append(t[1:-1] if t.startswith('"') else t)
    return cur[0]


def kids(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]


def kid(node, name):
    k = kids(node, name)
    return k[0] if k else None


def layers_of(node):
    out = []
    for key in ("layer", "layers"):
        for k in kids(node, key):
            out += [x for x in k[1:] if isinstance(x, str)]
    return out


def on_layer(node, layer):
    side = layer[0]
    return any(x == layer or x == "*.Cu" or x == f"{side}&B.Cu" or x == "F&B.Cu" for x in layers_of(node))


def pts(node):
    p = kid(node, "pts")
    return [(float(x[1]), float(x[2])) for x in kids(p, "xy")] if p else []


def board_info(path):
    root = parse(open(path, encoding="utf-8").read())
    info = dict(polys={"F.Cu": [], "B.Cu": []}, holes=[], copper={"F.Cu": [], "B.Cu": []}, edge=[])
    for item in root[1:]:
        if not isinstance(item, list):
            continue
        kind = item[0]
        if kind in ("gr_poly", "gr_rect", "gr_line", "gr_circle", "gr_arc"):
            if "Edge.Cuts" in layers_of(item):
                for key in ("start", "end"):
                    k = kid(item, key)
                    if k:
                        info["edge"].append((float(k[1]), float(k[2])))
                info["edge"] += pts(item)
            for lay in ("F.Cu", "B.Cu"):
                if lay in layers_of(item):
                    info["copper"][lay].append(kind)
                    if kind == "gr_poly":
                        info["polys"][lay].append(pts(item))
                    if kind == "gr_rect":
                        (x0, y0), (x1, y1) = [(float(kid(item, k)[1]), float(kid(item, k)[2])) for k in ("start", "end")]
                        info["polys"][lay].append([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        elif kind in ("segment", "arc"):
            for lay in ("F.Cu", "B.Cu"):
                if lay in layers_of(item):
                    info["copper"][lay].append(kind)
        elif kind == "zone":
            if kid(item, "keepout") is None:
                for lay in ("F.Cu", "B.Cu"):
                    if lay in layers_of(item):
                        info["copper"][lay].append("zone")
        elif kind == "via":
            at = kid(item, "at")
            info["holes"].append(dict(kind="via", xy=(float(at[1]), float(at[2])), drill=float(kid(item, "drill")[1])))
            for lay in ("F.Cu", "B.Cu"):
                info["copper"][lay].append("via pad")
        elif kind == "footprint":
            at = kid(item, "at")
            fx, fy = float(at[1]), float(at[2])
            rot = math.radians(float(at[3])) if len(at) > 3 else 0.0
            ref = next((p[2] for p in kids(item, "property") if p[1] == "Reference"), "?")
            for pad in kids(item, "pad"):
                pa = kid(pad, "at")
                px, py = float(pa[1]), float(pa[2])
                x = fx + px * math.cos(rot) + py * math.sin(rot)       # KiCad rotates footprints clockwise in y-down axes
                y = fy - px * math.sin(rot) + py * math.cos(rot)
                # A mounting hole (np_thru_hole) has no copper. A plated pad with "remove unused layers" set and
                # "keep end layers" off is plotted only on layers where copper connects to it, so it adds none of
                # its own to an empty face; the Gerber check below confirms what is actually plotted.
                stripped = (kid(pad, "remove_unused_layers") or [0, "no"])[1] == "yes" and                            (kid(pad, "keep_end_layers") or [0, "yes"])[1] == "no"
                for lay in ("F.Cu", "B.Cu"):
                    if on_layer(pad, lay) and pad[2] != "np_thru_hole" and not stripped:
                        info["copper"][lay].append(f"pad {ref}.{pad[1]}")
                dr = kid(pad, "drill")
                if dr and pad[2] == "thru_hole":
                    d = next((float(v) for v in dr[1:] if isinstance(v, str) and re.fullmatch(r"[\d.]+", v)), 0.0)
                    info["holes"].append(dict(kind=f"pad {ref}", xy=(x, y), drill=d))
    return info


# ---------------------------------------------------------------- Gerber
def gerber_layers(zip_path):
    """{'F': text, 'B': text} for the two copper Gerbers in a JLC zip."""
    out = {}
    with zipfile.ZipFile(zip_path) as z:
        for n in z.namelist():
            low = n.lower()
            for side, ends in (("F", ("-f_cu.gtl", "-f_cu.gbr", ".gtl")), ("B", ("-b_cu.gbl", "-b_cu.gbr", ".gbl"))):
                if low.endswith(ends):       # by ending only: a board called B_cutcorner contains "b_cu" in every name
                    out[side] = z.read(n).decode("ascii", "ignore")
    return out


def gerber_shapes(text):
    """Regions (lists of points, mm), and counts of draws and flashes, from a copper Gerber."""
    m = re.search(r"%FSLAX(\d)(\d)Y(\d)(\d)\*%", text)
    scale = 10 ** int(m.group(2))
    unit = 25.4 if "%MOIN*%" in text else 1.0
    regions, draws, flashes, cur, in_region = [], 0, 0, [], False
    x = y = 0.0
    body = re.sub(r"%[^%]*%", "", text)          # drop the extended commands (apertures, attributes)
    for cmd in body.replace("\n", "").replace("\r", "").split("*"):
        if not cmd:
            continue
        if cmd == "G36":
            in_region, cur = True, []
            continue
        if cmd == "G37":
            in_region = False
            if len(cur) >= 3:
                regions.append(cur)
            continue
        mm = re.fullmatch(r"(?:G0?[123])?(?:X(-?\d+))?(?:Y(-?\d+))?(?:I-?\d+)?(?:J-?\d+)?(D0?[123])?", cmd)
        if not mm or (mm.group(1) is None and mm.group(2) is None and mm.group(3) is None):
            continue
        if mm.group(1) is not None:
            x = int(mm.group(1)) / scale * unit
        if mm.group(2) is not None:
            y = int(mm.group(2)) / scale * unit
        op = (mm.group(3) or "D01").replace("D0", "D")
        if in_region:
            cur.append((x, y))
        elif op == "D1":
            draws += 1
        elif op == "D3":
            flashes += 1
    return regions, draws, flashes


# ---------------------------------------------------------------- geometry
def patch_dims(poly):
    """Side, the cut leg at each corner (TL, TR, BL, BR in a y-down top view) and the centre of a patch polygon."""
    pts_ = [p for i, p in enumerate(poly) if p != poly[i - 1]]
    xs, ys = [p[0] for p in pts_], [p[1] for p in pts_]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    cuts = {}
    for name, (cx, cy) in (("TL", (x0, y0)), ("TR", (x1, y0)), ("BL", (x0, y1)), ("BR", (x1, y1))):
        if any(abs(p[0] - cx) < 1e-6 and abs(p[1] - cy) < 1e-6 for p in pts_):
            cuts[name] = 0.0
        else:
            on_x = min(abs(p[0] - cx) for p in pts_ if abs(p[1] - cy) < 1e-6)      # nearest vertex along the horizontal edge
            on_y = min(abs(p[1] - cy) for p in pts_ if abs(p[0] - cx) < 1e-6)      # and along the vertical edge
            cuts[name] = (on_x, on_y)
    return dict(w=x1 - x0, h=y1 - y0, cuts=cuts, centre=((x0 + x1) / 2, (y0 + y1) / 2), n=len(pts_))


def biggest(polys):
    return max(polys, key=lambda p: (max(q[0] for q in p) - min(q[0] for q in p)) * (max(q[1] for q in p) - min(q[1] for q in p)))


def check_patch(d, side, cut, y_up, problems, where):
    if abs(d["w"] - side) > TOL or abs(d["h"] - side) > TOL:
        problems.append(f"{where}: patch is {d['w']:.3f} x {d['h']:.3f} mm, design {side:.2f}")
    # top-left and bottom-right in the top view. In a Gerber y points up, so top = max y: swap the names.
    names = {"TL": "BL", "BR": "TR", "TR": "BR", "BL": "TL"} if y_up else {k: k for k in ("TL", "TR", "BL", "BR")}
    for corner in ("TL", "TR", "BL", "BR"):
        got = d["cuts"][names[corner]]
        want = cut if corner in ("TL", "BR") else 0.0
        legs = (got, got) if got == 0.0 else got
        if any(abs(g - want) > TOL for g in legs):
            problems.append(f"{where}: corner {corner} cut is {legs[0]:.3f}/{legs[1]:.3f} mm, design {want:.2f}")


def main():
    bad = 0
    feed_pos = {}
    print("| Board | Patch in the KiCad file | Patch in the Gerber | Feed holes, from the patch centre | Copper on the faces | Result |")
    print("| --- | --- | --- | --- | --- | --- |")
    for name, pcb, zp, side, cut, feeds, has_patch in BOARDS:
        problems = []
        info = board_info(os.path.join(REPO, pcb))
        ex, ey = [p[0] for p in info["edge"]], [p[1] for p in info["edge"]]
        board_c = ((min(ex) + max(ex)) / 2, (min(ey) + max(ey)) / 2)
        board_size = (max(ex) - min(ex), max(ey) - min(ey))
        if abs(board_size[0] - 60) > TOL or abs(board_size[1] - 60) > TOL:
            problems.append(f"board is {board_size[0]:.3f} x {board_size[1]:.3f} mm, expected 60")
        gl = gerber_layers(os.path.join(REPO, zp))
        if has_patch:
            d = patch_dims(biggest(info["polys"]["F.Cu"]))
            check_patch(d, side, cut, False, problems, "KiCad")
            centre = d["centre"]
            if math.dist(centre, board_c) > TOL:
                problems.append(f"patch centre is {math.dist(centre, board_c):.3f} mm off the board centre")
            cut_txt = "no cuts" if not cut else "cuts " + ", ".join(
                f"{k} {v[0]:.3f}" for k, v in d["cuts"].items() if v != 0.0)
            k_txt = f"{d['w']:.3f} x {d['h']:.3f} mm, {cut_txt}"
            regions, _, _ = gerber_shapes(gl["F"])
            g = patch_dims(biggest(regions))
            check_patch(g, side, cut, True, problems, "Gerber")
            g_txt = f"{g['w']:.3f} x {g['h']:.3f} mm" + ("" if not cut else ", cuts " + ", ".join(
                f"{v[0]:.3f}" for v in g["cuts"].values() if v != 0.0))
        else:
            centre = board_c
            k_txt = g_txt = "none (ground board)"
        # feed holes: plated holes closest to each design feed point
        f_txt = []
        for fx, fy in feeds:
            want = (centre[0] + fx, centre[1] - fy)
            hole = min((h for h in info["holes"] if h["drill"] < 1.5), key=lambda h: math.dist(h["xy"], want))
            got = (hole["xy"][0] - centre[0], -(hole["xy"][1] - centre[1]))
            f_txt.append(f"({got[0]:.3f}, {got[1]:.3f})")
            if math.dist(hole["xy"], want) > TOL:
                problems.append(f"feed hole at {f_txt[-1]}, design ({fx:.2f}, {fy:.2f})")
            feed_pos.setdefault(name.rsplit(",", 1)[0], []).append((name, (hole["xy"][0] - board_c[0], hole["xy"][1] - board_c[1])))
        # copper on each face
        c_txt = []
        for face in ("F", "B"):
            regions, draws, flashes = gerber_shapes(gl[face])
            n_k = len(info["copper"][face + ".Cu"])
            n_g = len(regions) + draws + flashes
            c_txt.append(f"{face}.Cu: {n_k} items in KiCad, {n_g} in the Gerber")
            part = name.rsplit(" ", 1)[-1]
            if BOND_FACE.get(part) == face and (n_k or n_g):
                problems.append(f"bond face {face}.Cu has copper: {info['copper'][face + '.Cu'][:4]}, Gerber {n_g} objects")
        bad += bool(problems)
        print(f"| {name} | {k_txt} | {g_txt} | {', '.join(f_txt)} | {'; '.join(c_txt)} | "
              f"{'matches' if not problems else 'MISMATCH: ' + '; '.join(problems)} |")
    print()
    for pair, items in feed_pos.items():
        tops = [p for n, p in items if n.endswith("TOP")]
        bots = [p for n, p in items if n.endswith("BOTTOM")]
        if tops and bots:
            worst = max(math.dist(a, b) for a, b in zip(tops, bots))
            print(f"{pair}: TOP and BOTTOM feed holes differ by at most {worst:.4f} mm, measured from each board's centre.")
            bad += worst > TOL
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
