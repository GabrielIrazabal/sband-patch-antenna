"""First-cut patch dimensions (Balanis transmission-line + cavity models).
Placeholders only: the openEMS/HFSS sim sets the final numbers."""
import math

C = 299_792_458.0

def eps_eff(er, h, w):
    return (er + 1) / 2 + (er - 1) / 2 * (1 + 12 * h / w) ** -0.5

def delta_l(er, h, w):
    ee = eps_eff(er, h, w)
    return 0.412 * h * (ee + 0.3) * (w / h + 0.264) / ((ee - 0.258) * (w / h + 0.8))

def square_patch_side(f, er, h):
    """Side L of a square patch (W = L) resonant at f. h, L in metres."""
    L = C / (2 * f * math.sqrt(er))
    for _ in range(50):
        L = C / (2 * f * math.sqrt(eps_eff(er, h, L))) - 2 * delta_l(er, h, L)
    return L

def j0(x):
    # series is fine for the small arguments here (k0*L < 3)
    s, term, k = 0.0, 1.0, 0
    while abs(term) > 1e-15:
        s += term
        k += 1
        term *= -(x / 2) ** 2 / (k * k)
    return s

def edge_resistance(f, w, L):
    k0 = 2 * math.pi * f / C
    n = 4000
    i1 = i12 = 0.0
    for i in range(1, n):
        th = math.pi * i / n
        c, s = math.cos(th), math.sin(th)
        a = (math.sin(k0 * w / 2 * c) / c) ** 2 * s ** 3 if abs(c) > 1e-12 else (k0 * w / 2) ** 2 * s ** 3
        i1 += a
        i12 += a * j0(k0 * L * s)
    d = math.pi / n
    g1 = i1 * d / (120 * math.pi ** 2)
    g12 = i12 * d / (120 * math.pi ** 2)
    return 1 / (2 * (g1 + g12))

def feed_offset_from_centre(f, w, L, z0=50.0):
    r_edge = edge_resistance(f, w, L)
    y0 = L / math.pi * math.acos(math.sqrt(z0 / r_edge))  # inset from the radiating edge
    return L / 2 - y0, r_edge

def bandwidth_vswr2(f, er, h, w_over_l=1.0):
    lam0 = C / f
    return 3.771 * (er - 1) / er ** 2 * (h / lam0) * w_over_l

def corner_cut(L, frac_bw):
    q = 1 / (math.sqrt(2) * frac_bw)        # VSWR-2 bandwidth -> Q
    ds = L * L / (2 * q)                    # Sharma & Gupta: dS/S = 1/(2Q)
    return math.sqrt(ds), q                 # two triangles of area c^2/2

if __name__ == "__main__":
    f, er, h = 2.425e9, 3.66, 1.524e-3
    L = square_patch_side(f, er, h)
    x0, r_edge = feed_offset_from_centre(f, L, L)
    bw = bandwidth_vswr2(f, er, h)
    c, q = corner_cut(L, bw)
    print(f"L = {L*1e3:.2f} mm, edge R = {r_edge:.0f} ohm, 50-ohm feed {x0*1e3:.2f} mm from centre")
    print(f"BW(VSWR<2) = {bw*100:.2f} % = {bw*f/1e6:.1f} MHz, Q = {q:.0f}, corner cut leg = {c*1e3:.2f} mm")
