"""Hand calculations for the three patch antennas, as a check on the HFSS tuning.

Textbook closed-form models only (no solver):
  size        Hammerstad transmission-line model (effective Dk + fringing length)
  Q, bandwidth, efficiency, directivity, edge resistance
              Jackson & Alexopoulos cavity-model formulas (IEEE Trans. AP, 1991)
  corner cut  dS/S = 1/(2Q)            3 dB axial-ratio bandwidth = 0.348/Q
  CP match bandwidth (VSWR 2) = sqrt(2)/Q        linear match bandwidth = 1/(sqrt(2) Q)
  feed        R(d) = R_edge sin^2(pi d / L);  a single-feed CP patch shows half of that at its CP frequency
  probe       X = 60 k0 h [ln(2 / (k0 sqrt(er) r)) - 0.5772]
  stacked     two coupled resonators:  f = (f1+f2)/2 -/+ 0.5 sqrt((f1-f2)^2 + (k f0)^2)

These formulas are known to be a few percent off for final sizes (README: about 2.7 % high in
frequency for this board), so they confirm that the simulated designs are in the right place and
behave as theory says; they do not replace the simulation.

  python sim/hand_calcs.py            # prints the tables and writes sim/HAND_CALCS.md
"""
import json
import math
import os

C0 = 299_792_458.0
ETA0 = 376.73
HERE = os.path.dirname(os.path.abspath(__file__))
F0 = 2.425e9
ER, TAND, H = 2.55, 0.0018, 1.524e-3
SIGMA_CU = 5.8e7
R_PIN = 0.25e-3


def hammerstad(f, er, h, iters=20):
    """Square patch side for resonance at f. Returns (L, eps_eff, dL), metres."""
    L = C0 / (2 * f * math.sqrt(er))
    for _ in range(iters):
        W = L
        ee = (er + 1) / 2 + (er - 1) / 2 / math.sqrt(1 + 12 * h / W)
        dL = 0.412 * h * (ee + 0.3) * (W / h + 0.264) / ((ee - 0.258) * (W / h + 0.8))
        L = C0 / (2 * f * math.sqrt(ee)) - 2 * dL
    return L, ee, dL


def res_freq(L, er, h):
    W = L
    ee = (er + 1) / 2 + (er - 1) / 2 / math.sqrt(1 + 12 * h / W)
    dL = 0.412 * h * (ee + 0.3) * (W / h + 0.264) / ((ee - 0.258) * (W / h + 0.8))
    return C0 / (2 * (L + 2 * dL) * math.sqrt(ee))


def jackson(f, er, tand, h, L, W=None):
    """Q factors, efficiency, directivity and edge resistance of a rectangular patch."""
    W = W or L
    lam = C0 / f
    k0 = 2 * math.pi / lam
    n2 = er
    c1 = 1 - 1 / n2 + 0.4 / n2 ** 2
    a2, a4, c2 = -0.16605, 0.00761, -0.0914153
    kw, kl = k0 * W, k0 * L
    p = (1 + a2 / 10 * kw ** 2 + (a2 ** 2 + 2 * a4) * 3 / 560 * kw ** 4 + c2 / 5 * kl ** 2
         + a2 * c2 / 70 * kw ** 2 * kl ** 2)
    e_hed = 1 / (1 + 0.75 * math.pi * (k0 * h) / c1 * (1 - 1 / n2) ** 3)   # space wave / (space + surface wave)
    q_sp = 1 / ((16 / 3) * (p * c1 / er) * (h / lam) * (W / L))            # radiation into space
    q_rad = q_sp * e_hed                                                    # radiation + surface wave
    q_d = 1 / tand
    rs = math.sqrt(math.pi * f * 4e-7 * math.pi / SIGMA_CU)
    q_c = math.pi * ETA0 * (h / lam) / rs
    q = 1 / (1 / q_rad + 1 / q_d + 1 / q_c)
    eff = q / q_sp
    k1h = k0 * math.sqrt(er) * h
    tanc = math.tan(k1h) / k1h
    d = 3 / (p * c1) * tanc ** 2 / (1 + math.tan(k1h) ** 2 / er)           # directivity
    r_edge = (4 / math.pi) * ETA0 * (L / W) * (h / lam) * q
    return dict(Q=q, Q_space=q_sp, Q_diel=q_d, Q_cond=q_c, eff=eff, D_dBi=10 * math.log10(d), R_edge=r_edge)


def probe_x(f, er, h, r):
    k0 = 2 * math.pi * f / C0
    return 60 * k0 * h * (math.log(2 / (k0 * math.sqrt(er) * r)) - 0.5772)


def feed_offset(L, r_res, r_target=50.0):
    """Distance from the patch centre where the resonant resistance is r_target."""
    return L / math.pi * math.asin(math.sqrt(min(1.0, r_target / r_res)))


def ar_from_errors(amp_db, phase_deg):
    """Axial ratio (dB) of two equal orthogonal modes with an amplitude and a phase error."""
    g = 10 ** (amp_db / 20)
    d = math.radians(90 + phase_deg)
    s = math.sqrt(1 + g ** 4 + 2 * g ** 2 * math.cos(2 * d))
    return 10 * math.log10((1 + g ** 2 + s) / (1 + g ** 2 - s))


def pol_loss_db(ar_db):
    """Signal lost to the wrong hand, against a perfectly circular antenna at the other end."""
    r = 10 ** (ar_db / 20)
    return 10 * math.log10(1 + ((r - 1) / (r + 1)) ** 2)


def summary(name):
    p = os.path.join(HERE, "results_hfss", name, "summary.json")
    return json.load(open(p)) if os.path.exists(p) else None


def row(label, hand, hfss, unit="", fmt="{:.2f}"):
    h = fmt.format(hand) if isinstance(hand, (int, float)) else str(hand)
    s = fmt.format(hfss) if isinstance(hfss, (int, float)) else ("" if hfss is None else str(hfss))
    diff = ""
    if isinstance(hand, (int, float)) and isinstance(hfss, (int, float)) and hfss:
        diff = f"{(hand - hfss) / abs(hfss) * 100:+.1f} %" if unit not in ("dB", "dBi", "dBic") else f"{hand - hfss:+.2f} dB"
    return f"| {label} | {h} {unit} | {s} {unit} | {diff} |"


def single_patch(out):
    L, ee, dL = hammerstad(F0, ER, H)
    j = jackson(F0, ER, TAND, H, L)
    Q = j["Q"]
    b = summary("B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_mesh40k") or {}
    a = summary("A_L37.28_f5.80_er2.55_h1.52_Gm100_mesh40k") or {}
    cut = L * math.sqrt(1 / (2 * Q))
    lam = C0 / F0
    out += ["## 1. Single patch on 1.524 mm PTFE (cut corner and dual feed)", "",
            f"Effective Dk {ee:.3f}, fringing length {dL * 1e3:.2f} mm per edge, "
            f"Q {Q:.1f} (radiation {j['Q_space']:.0f}, dielectric {j['Q_diel']:.0f}, copper {j['Q_cond']:.0f}).", "",
            "| Quantity | Hand calculation | HFSS (tuned design) | Difference |", "| --- | --- | --- | --- |",
            row("Patch side, dual feed (square patch at 2.425 GHz)", L * 1e3, 37.28, "mm"),
            row("Patch side, cut corner", L * 1e3 * (1 + 1 / (4 * Q)), 37.52, "mm"),
            row("Corner-cut leg, c = L sqrt(1/2Q)", cut * 1e3, 3.50, "mm"),
            row("Feed offset, dual feed (50 ohm per port)", feed_offset(L, j["R_edge"]) * 1e3, 5.80, "mm"),
            row("Feed offset, cut corner (CP patch shows half the resistance)", feed_offset(L, j["R_edge"] / 2) * 1e3, 7.00, "mm"),
            row("3 dB axial-ratio bandwidth, cut corner (0.348/Q)", 0.348 / Q * F0 / 1e6, b.get("axial_ratio_3dB_band_MHz"), "MHz", "{:.1f}"),
            row("Match bandwidth, cut corner (sqrt2/Q)", math.sqrt(2) / Q * F0 / 1e6, b.get("s11_10dB_band_MHz"), "MHz", "{:.1f}"),
            row("Match bandwidth, dual feed (1/(sqrt2 Q))", 1 / (math.sqrt(2) * Q) * F0 / 1e6, a.get("s11_10dB_band_MHz"), "MHz", "{:.1f}"),
            row("Radiation efficiency", j["eff"] * 100, (b.get("radiation_efficiency_at_f0") or 0) * 100 or None, "%", "{:.0f}"),
            row("Directivity (infinite ground; HFSS is on the 100 mm face)", j["D_dBi"], b.get("directivity_at_f0_dBi"), "dBi"),
            row("Gain = directivity x efficiency", j["D_dBi"] + 10 * math.log10(j["eff"]), b.get("rhcp_gain_at_f0_dBic"), "dBic"),
            row("Frequency shift per mm of patch size", -F0 / (L + 2 * dL) / 1e9, -62.0 if b else None, "MHz/mm", "{:.0f}"),
            row("Frequency shift for Dk +1 %", -0.5 * 0.01 * F0 / 1e6 * (ER / ee) * ((1 + 1 / math.sqrt(1 + 12 * H / L)) / 2), -12.0, "MHz", "{:.1f}"),
            row("Feed-via reactance (0.5 mm via)", probe_x(F0, ER, H, R_PIN), None, "ohm", "{:.0f}"),
            ""]
    out += ["Polarization loss for a given axial ratio (against a perfectly circular ground antenna):", "",
            "| Axial ratio | 1 dB | 2 dB | 3 dB | 4.1 dB | 6 dB |", "| --- | --- | --- | --- | --- | --- |",
            "| Signal lost | " + " | ".join(f"{pol_loss_db(x):.2f} dB" for x in (1, 2, 3, 4.1, 6)) + " |", ""]
    out += ["Dual feed: axial ratio caused by an imperfect hybrid alone (the patch adds its own on top):", "",
            "| Hybrid error | Hand calculation | HFSS, worst in channel |", "| --- | --- | --- |"]
    hy = {(x["amplitude_dB"], x["phase_deg"]): x["axial_ratio_worst_in_band_dB"] for x in a.get("hybrid_imbalance", [])}
    for amp, ph in ((0.5, 3.0), (1.0, 5.0), (1.0, 10.0)):
        out.append(f"| {amp} dB and {ph:.0f} deg | {ar_from_errors(amp, ph):.2f} dB | {hy.get((amp, ph), '')} dB |")
    out.append("")
    return Q


def stacked(out, q_single, S):
    """S: dict with the tuned stacked dimensions and the names of the HFSS runs to compare with."""
    L1, L2, gap = S["L"] * 1e-3, S["L2"] * 1e-3, S["gap"] * 1e-3
    # resonator 1: the lower patch on its own board. resonator 2: the upper patch over ground, with the
    # lower board and the air gap in series as its substrate.
    f1 = res_freq(L1, ER, H)
    h2 = H + gap
    er2 = h2 / (H / ER + gap)
    f2 = res_freq(L2, er2, h2)
    lin = S.get("linear")           # HFSS run without corner cuts: the two coupled resonances
    out += ["## 2. Stacked patch", "",
            f"Lower patch {S['L']:.2f} mm on 1.524 mm PTFE; upper patch {S['L2']:.2f} mm, {S['gap']:.1f} mm of air above "
            "the lower board, on the underside of a second 1.524 mm PTFE board.", "",
            "There is no closed-form design formula for a stacked pair, so the check is in two parts: (a) does a "
            "two-coupled-resonator model explain where HFSS puts the resonances, and (b) do the corner cut, "
            "axial-ratio bandwidth and feed correction follow from the measured Q the same way they do for the "
            "single patch.", "",
            f"(a) Each patch alone, by the Hammerstad model: lower {f1 / 1e9:.3f} GHz, upper {f2 / 1e9:.3f} GHz "
            f"(upper patch substrate: {h2 * 1e3:.2f} mm thick, series-capacitor Dk {er2:.2f}).", ""]
    if lin:
        flo, fhi = lin["dips"]
        f1l = res_freq(lin["L"] * 1e-3, ER, H) / 1e9
        f2l = res_freq(lin["L2"] * 1e-3, er2, h2) / 1e9
        k = math.sqrt(max(0.0, (fhi - flo) ** 2 - (f2l - f1l) ** 2)) / ((fhi + flo) / 2)
        out += [f"HFSS, a pair without corner cuts ({lin['L']:.2f} / {lin['L2']:.2f} mm): resonances at {flo:.3f} and "
                f"{fhi:.3f} GHz. By hand the two patches alone are at {f1l:.3f} and {f2l:.3f} GHz. Coupling pushes a "
                f"pair of resonances apart but keeps their sum: {f1l + f2l:.3f} GHz by hand against {flo + fhi:.3f} GHz "
                f"in HFSS ({((f1l + f2l) / (flo + fhi) - 1) * 100:+.1f} %, the same sign and size as the single-patch "
                f"formula error). The split needs a coupling coefficient of about {k * 100:.0f} %, which is strong: "
                "the two resonances cannot be merged into one wide band at this gap, so the antenna works on the "
                "lower one alone.", ""]
        q = flo * 1e3 / (math.sqrt(2) * lin["bw10"])
        cut_frac = math.sqrt(1 / (2 * q))
        rho = None
        if S.get("feed_y"):
            phi = math.atan2(S["feed_y"], S["feed"])
            rho = math.cos(math.radians(45) - phi) / math.cos(math.radians(45) + phi)
        D = (rho + 1 / rho) if rho else 2.0
        out += [f"(b) Q from the HFSS match bandwidth of the uncut pair ({lin['bw10']:.0f} MHz at -10 dB): "
                f"Q = f / (sqrt2 x BW) = {q:.1f}, against {q_single:.1f} for the single patch.", "",
                "| Quantity | Hand calculation | HFSS (tuned design) | Difference |", "| --- | --- | --- | --- |",
                row("3 dB axial-ratio bandwidth (0.348/Q)", 0.348 / q * F0 / 1e6, S.get("ar_bw"), "MHz", "{:.1f}"),
                row("CP match bandwidth (sqrt2/Q)", math.sqrt(2) / q * F0 / 1e6, S.get("s11_bw"), "MHz", "{:.0f}"),
                row("Corner cut / patch side, feed on the centre line: sqrt(1/2Q)", cut_frac, S.get("cut_frac_sym"), "", "{:.3f}"),
                ]
        if rho:
            out += [row(f"Mode-coupling ratio for the feed {S['feed_y']:.2f} mm off the centre line", rho, None, "", "{:.2f}"),
                    row("Corner cut / patch side with that feed: sqrt((rho + 1/rho)/2 x 1/2Q)", cut_frac * math.sqrt(D / 2), S["cut"] / S["L"], "", "{:.3f}"),
                    row("Shift of the CP frequency caused by moving the feed: (rho - 1) f / 2Q", (rho - 1) * F0 / (2 * q) / 1e6, S.get("fy_shift"), "MHz", "{:.0f}")]
        out += [row("Feed-via reactance", probe_x(F0, ER, H, R_PIN), S.get("x_sym"), "ohm", "{:.0f}"), ""]
    jd = jackson(F0, er2, 0.0005, h2, L2)
    out += [f"Directivity of a patch on a substrate of Dk {er2:.2f}: {jd['D_dBi']:.1f} dBi by the same formula "
            f"(single patch on PTFE: {jackson(F0, ER, TAND, H, hammerstad(F0, ER, H)[0])['D_dBi']:.1f} dBi). "
            f"HFSS gives {S.get('dir', '?')} dBi for the stacked patch on the 100 mm face. "
            "The stack is more directive because most of its field is in air, so the radiating patch is physically larger.", ""]


def stacked_dual(out, S, D):
    """Stacked dual feed: sizes and feed position predicted by hand from the uncut reference pair, then HFSS."""
    lin = S["linear"]
    flo = lin["dips"][0]
    q = flo * 1e3 / (math.sqrt(2) * lin["bw10"])
    scale = flo / (F0 / 1e9)                       # resonance scales inversely with size
    mesh = 1.007                                   # the 40,000-element mesh reads 0.7 % higher than the tuning mesh
    L1, L2 = lin["L"] * scale * mesh, lin["L2"] * scale * mesh
    r_edge = lin["r_res"] / math.sin(math.pi * lin["feed"] / lin["L"]) ** 2
    feed = L1 / math.pi * math.asin(math.sqrt(min(1.0, 50.0 / r_edge)))
    h2 = H + S["gap"] * 1e-3
    er2 = h2 / (H / ER + S["gap"] * 1e-3)
    q_up = jackson(F0, er2, 0.0005, h2, L2 * 1e-3)["Q"]
    j = summary(D.get("hfss_run", "")) or {}
    hy = {(x["amplitude_dB"], x["phase_deg"]): x["axial_ratio_worst_in_band_dB"] for x in j.get("hybrid_imbalance", [])}
    out += ["## 3. Stacked dual feed", "",
            "Same two boards as the stacked patch, but square patches with no corner cuts and two feeds on the "
            "lower patch, driven 90 degrees apart by a coupler (as on the single dual feed).", "",
            f"Hand steps: (1) the uncut reference pair ({lin['L']:.2f} / {lin['L2']:.2f} mm) resonates at {flo:.3f} GHz in HFSS, "
            f"so scale both patches by {scale:.4f} for 2.425 GHz, and by {mesh} more because the fine mesh reads 0.7 % "
            f"higher than the mesh that pair was solved on. (2) That pair showed {lin['r_res']:.1f} ohm at resonance with the "
            f"feed {lin['feed']:.1f} mm from the centre; R = R_edge sin^2(pi d / L) gives R_edge = {r_edge:.1f} ohm and the "
            "50 ohm point. (3) Bandwidth from Q; axial ratio from the coupler error formula, which does not depend on "
            "the patch.", "",
            f"The stack's Q of {q:.1f} lies between the Jackson value for the upper patch alone on its air substrate "
            f"({q_up:.1f}) and for the lower patch alone on PTFE (53.5), as it should for a coupled pair.", "",
            "| Quantity | Hand calculation | HFSS (tuned design) | Difference |", "| --- | --- | --- | --- |",
            row("Lower patch side", L1, D.get("L"), "mm"),
            row("Upper patch side", L2, D.get("L2"), "mm"),
            row("Feed offset for 50 ohm", feed, D.get("feed"), "mm"),
            row("Match bandwidth, 1/(sqrt2 Q)", F0 / 1e6 / (math.sqrt(2) * q), j.get("s11_10dB_band_MHz"), "MHz", "{:.0f}"),
            row("Axial ratio, coupler off by 0.5 dB and 3 deg", ar_from_errors(0.5, 3), hy.get((0.5, 3.0)), "dB"),
            row("Axial ratio, coupler off by 1 dB and 5 deg", ar_from_errors(1.0, 5), hy.get((1.0, 5.0)), "dB"),
            row("Axial ratio, coupler off by 1 dB and 10 deg", ar_from_errors(1.0, 10), hy.get((1.0, 10.0)), "dB"),
            row("Gain at the patch = stacked directivity x efficiency", S.get("dir", 8.87) + 10 * math.log10(0.977),
                j.get("rhcp_gain_at_f0_dBic"), "dBic"),
            ""]


def stacked_short(out, S, G):
    """Stacked cut corner re-tuned for a smaller gap (G). No uncut reference pair was solved at this gap, so Q
    comes from the HFSS axial-ratio bandwidth and the check is whether the cut and the match bandwidth agree with it."""
    gap = G["gap"] * 1e-3
    h2 = H + gap
    er2 = h2 / (H / ER + gap)
    q = 0.348 * F0 / 1e6 / G["ar_bw"]
    q5 = S["linear"]["dips"][0] * 1e3 / (math.sqrt(2) * S["linear"]["bw10"])
    phi = math.atan2(G["feed_y"], G["feed"])
    rho = math.cos(math.radians(45) - phi) / math.cos(math.radians(45) + phi)
    cut = math.sqrt((rho + 1 / rho) / 2 / (2 * q))
    jd = jackson(F0, er2, 0.0005, h2, G["L2"] * 1e-3)
    out += [f"## 4. Stacked cut corner with a {G['gap']:.1f} mm gap", "",
            f"Lower patch {G['L']:.2f} mm, upper patch {G['L2']:.2f} mm, {G['gap']:.1f} mm of air between the boards "
            f"(about {(2 * H + gap) * 1e3:.1f} mm tall in total).", "",
            f"No uncut pair was solved at this gap, so Q is taken from the HFSS axial-ratio bandwidth "
            f"({G['ar_bw']:.1f} MHz): Q = 0.348 f / BW = {q:.1f}, against {q5:.1f} at the 5 mm gap. A smaller gap "
            "stores more energy for the same radiated power, so Q rises and every bandwidth shrinks. The check is "
            "whether the corner cut and the match bandwidth HFSS arrived at agree with that Q.", "",
            "| Quantity | Hand calculation | HFSS (tuned design) | Difference |", "| --- | --- | --- | --- |",
            row("CP match bandwidth (sqrt2/Q)", math.sqrt(2) / q * F0 / 1e6, G.get("s11_bw"), "MHz", "{:.0f}"),
            row(f"Mode-coupling ratio for the feed {G['feed_y']:.2f} mm off the centre line", rho, None, "", "{:.2f}"),
            row("Lower corner cut / patch side: sqrt((rho + 1/rho)/2 x 1/2Q)", cut, G["cut"] / G["L"], "", "{:.3f}"),
            row("Upper corner cut / patch side, same formula", cut, G["cut2"] / G["L2"], "", "{:.3f}"),
            row("Cut needed relative to the 5 mm design: sqrt(Q5/Q3)", math.sqrt(q5 / q), (G["cut"] / G["L"]) / (S["cut"] / S["L"]), "", "{:.3f}"),
            row(f"Directivity, patch on a substrate of Dk {er2:.2f} (infinite ground)", jd["D_dBi"], G.get("dir"), "dBi"),
            "",
            "Polarization loss if a tolerance pushes the axial ratio past 3 dB: "
            + ", ".join(f"{x} dB costs {pol_loss_db(x):.2f} dB" for x in (3.3, 3.6, 4.7, 5.0)) + ".", ""]


def main(S=None):
    out = ["# Hand calculations against HFSS", "",
           "Closed-form textbook models, used as a check that the simulated designs are where theory says they "
           "should be. Formulas and sources are in `sim/hand_calcs.py`. Design frequency 2.425 GHz, PTFE "
           "ZYF255DA (Dk 2.55, loss tangent 0.0018), 1.524 mm.", ""]
    q = single_patch(out)
    sp = os.path.join(HERE, "stacked_design.json")
    if S is None and os.path.exists(sp):
        S = json.load(open(sp))
    if S:
        stacked(out, q, S)
        dp = os.path.join(HERE, "stacked_dual_design.json")
        if os.path.exists(dp):
            stacked_dual(out, S, json.load(open(dp)))
        gp = os.path.join(HERE, "stacked_design_g3.json")
        if os.path.exists(gp):
            stacked_short(out, S, json.load(open(gp)))
    text = "\n".join(out)
    print(text)
    with open(os.path.join(HERE, "HAND_CALCS.md"), "w", encoding="utf-8") as fh:
        fh.write(text + "\n")


if __name__ == "__main__":
    main()
