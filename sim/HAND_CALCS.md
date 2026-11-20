# Hand calculations against HFSS

Closed-form textbook models, used as a check that the simulated designs are where theory says they should be. Formulas and sources are in `sim/hand_calcs.py`. Design frequency 2.425 GHz, PTFE ZYF255DA (Dk 2.55, loss tangent 0.0018), 1.524 mm.

## 1. Single patch on 1.524 mm PTFE (cut corner and dual feed)

Effective Dk 2.412, fringing length 0.77 mm per edge, Q 53.5 (radiation 66, dielectric 556, copper 1136).

| Quantity | Hand calculation | HFSS (tuned design) | Difference |
| --- | --- | --- | --- |
| Patch side, dual feed (square patch at 2.425 GHz) | 38.25 mm | 37.28 mm | +2.6 % |
| Patch side, cut corner | 38.43 mm | 37.52 mm | +2.4 % |
| Corner-cut leg, c = L sqrt(1/2Q) | 3.70 mm | 3.50 mm | +5.7 % |
| Feed offset, dual feed (50 ohm per port) | 4.98 mm | 5.80 mm | -14.2 % |
| Feed offset, cut corner (CP patch shows half the resistance) | 7.27 mm | 7.00 mm | +3.9 % |
| 3 dB axial-ratio bandwidth, cut corner (0.348/Q) | 15.8 MHz | 16.0 MHz | -1.4 % |
| Match bandwidth, cut corner (sqrt2/Q) | 64.1 MHz | 65.8 MHz | -2.5 % |
| Match bandwidth, dual feed (1/(sqrt2 Q)) | 32.1 MHz | 32.4 MHz | -1.0 % |
| Radiation efficiency | 81 % | 87 % | -7.3 % |
| Directivity (infinite ground; HFSS is on the 100 mm face) | 7.12 dBi | 7.97 dBi | -0.85 dB |
| Gain = directivity x efficiency | 6.18 dBic | 7.24 dBic | -1.06 dB |
| Frequency shift per mm of patch size | -61 MHz/mm | -62 MHz/mm | +1.7 % |
| Frequency shift for Dk +1 % | -11.7 MHz | -12.0 MHz | +2.7 % |
| Feed-via reactance (0.5 mm via) | 19 ohm |  ohm |  |

Polarization loss for a given axial ratio (against a perfectly circular ground antenna):

| Axial ratio | 1 dB | 2 dB | 3 dB | 4.1 dB | 6 dB |
| --- | --- | --- | --- | --- | --- |
| Signal lost | 0.01 dB | 0.06 dB | 0.13 dB | 0.23 dB | 0.45 dB |

Dual feed: axial ratio caused by an imperfect hybrid alone (the patch adds its own on top):

| Hybrid error | Hand calculation | HFSS, worst in channel |
| --- | --- | --- |
| 0.5 dB and 3 deg | 0.68 dB | 0.79 dB |
| 1.0 dB and 5 deg | 1.26 dB | 1.37 dB |
| 1.0 dB and 10 deg | 1.83 dB | 1.93 dB |

## 2. Stacked patch

Lower patch 36.26 mm on 1.524 mm PTFE; upper patch 42.97 mm, 5.0 mm of air above the lower board, on the underside of a second 1.524 mm PTFE board.

There is no closed-form design formula for a stacked pair, so the check is in two parts: (a) does a two-coupled-resonator model explain where HFSS puts the resonances, and (b) do the corner cut, axial-ratio bandwidth and feed correction follow from the measured Q the same way they do for the single patch.

(a) Each patch alone, by the Hammerstad model: lower 2.556 GHz, upper 2.755 GHz (upper patch substrate: 6.52 mm thick, series-capacitor Dk 1.17).

HFSS, a pair without corner cuts (35.00 / 41.50 mm): resonances at 2.421 and 2.979 GHz. By hand the two patches alone are at 2.646 and 2.838 GHz. Coupling pushes a pair of resonances apart but keeps their sum: 5.484 GHz by hand against 5.400 GHz in HFSS (+1.6 %, the same sign and size as the single-patch formula error). The split needs a coupling coefficient of about 19 %, which is strong: the two resonances cannot be merged into one wide band at this gap, so the antenna works on the lower one alone.

(b) Q from the HFSS match bandwidth of the uncut pair (96 MHz at -10 dB): Q = f / (sqrt2 x BW) = 17.9, against 53.5 for the single patch.

| Quantity | Hand calculation | HFSS (tuned design) | Difference |
| --- | --- | --- | --- |
| 3 dB axial-ratio bandwidth (0.348/Q) | 47.3 MHz | 49.4 MHz | -4.3 % |
| CP match bandwidth (sqrt2/Q) | 192 MHz | 206 MHz | -6.9 % |
| Corner cut / patch side, feed on the centre line: sqrt(1/2Q) | 0.167  | 0.166  | +0.8 % |
| Mode-coupling ratio for the feed 3.07 mm off the centre line | 1.48  |   |  |
| Corner cut / patch side with that feed: sqrt((rho + 1/rho)/2 x 1/2Q) | 0.174  | 0.181  | -4.0 % |
| Shift of the CP frequency caused by moving the feed: (rho - 1) f / 2Q | 32 MHz | 40 MHz | -19.1 % |
| Feed-via reactance | 19 ohm | 25 ohm | -25.4 % |

Directivity of a patch on a substrate of Dk 1.17: 9.0 dBi by the same formula (single patch on PTFE: 7.1 dBi). HFSS gives 8.87 dBi for the stacked patch on the 100 mm face. The stack is more directive because most of its field is in air, so the radiating patch is physically larger.

## 3. Stacked dual feed

Same two boards as the stacked patch, but square patches with no corner cuts and two feeds on the lower patch, driven 90 degrees apart by a coupler (as on the single dual feed).

Hand steps: (1) the uncut reference pair (35.00 / 41.50 mm) resonates at 2.421 GHz in HFSS, so scale both patches by 0.9984 for 2.425 GHz, and by 1.007 more because the fine mesh reads 0.7 % higher than the mesh that pair was solved on. (2) That pair showed 44.6 ohm at resonance with the feed 12.0 mm from the centre; R = R_edge sin^2(pi d / L) gives R_edge = 57.5 ohm and the 50 ohm point. (3) Bandwidth from Q; axial ratio from the coupler error formula, which does not depend on the patch.

The stack's Q of 17.9 lies between the Jackson value for the upper patch alone on its air substrate (11.0) and for the lower patch alone on PTFE (53.5), as it should for a coupled pair.

| Quantity | Hand calculation | HFSS (tuned design) | Difference |
| --- | --- | --- | --- |
| Lower patch side | 35.19 mm | 35.04 mm | +0.4 % |
| Upper patch side | 41.72 mm | 41.51 mm | +0.5 % |
| Feed offset for 50 ohm | 13.45 mm | 13.35 mm | +0.8 % |
| Match bandwidth, 1/(sqrt2 Q) | 96 MHz | 106 MHz | -9.7 % |
| Axial ratio, coupler off by 0.5 dB and 3 deg | 0.68 dB | 1.48 dB | -0.80 dB |
| Axial ratio, coupler off by 1 dB and 5 deg | 1.26 dB | 2.06 dB | -0.80 dB |
| Axial ratio, coupler off by 1 dB and 10 deg | 1.83 dB | 2.47 dB | -0.64 dB |
| Gain at the patch = stacked directivity x efficiency | 8.77 dBic | 8.74 dBic | +0.03 dB |

## 4. Stacked cut corner with a 3.0 mm gap

Lower patch 35.63 mm, upper patch 42.23 mm, 3.0 mm of air between the boards (about 6.0 mm tall in total).

No uncut pair was solved at this gap, so Q is taken from the HFSS axial-ratio bandwidth (35.0 MHz): Q = 0.348 f / BW = 24.1, against 17.9 at the 5 mm gap. A smaller gap stores more energy for the same radiated power, so Q rises and every bandwidth shrinks. The check is whether the corner cut and the match bandwidth HFSS arrived at agree with that Q.

| Quantity | Hand calculation | HFSS (tuned design) | Difference |
| --- | --- | --- | --- |
| CP match bandwidth (sqrt2/Q) | 142 MHz | 146 MHz | -2.6 % |
| Mode-coupling ratio for the feed 3.02 mm off the centre line | 1.48  |   |  |
| Lower corner cut / patch side: sqrt((rho + 1/rho)/2 x 1/2Q) | 0.149  | 0.152  | -1.4 % |
| Upper corner cut / patch side, same formula | 0.149  | 0.152  | -1.7 % |
| Cut needed relative to the 5 mm design: sqrt(Q5/Q3) | 0.860  | 0.838  | +2.7 % |
| Directivity, patch on a substrate of Dk 1.26 (infinite ground) | 8.84 dBi | 8.70 dBi | +0.14 dB |

Polarization loss if a tolerance pushes the axial ratio past 3 dB: 3.3 dB costs 0.15 dB, 3.6 dB costs 0.18 dB, 4.7 dB costs 0.29 dB, 5.0 dB costs 0.33 dB.

