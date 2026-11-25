# HFSS rerun and double-check: results

Run on 24 and 25 November 2026 on the Windows laptop (Ansys Electronics Desktop Student 2025 R2), following [`../HFSS_RERUN.md`](../HFSS_RERUN.md). 28 HFSS runs (the 24 the task asks for and four extra) and one check of the board files. Everything here is simulation. Nothing has been built or measured.

All four antennas are on JLC PTFE ZYF255DA (Dk 2.55, loss tangent 0.0018), a 60 mm board on a 100 mm metal face, 2.425 GHz, channel 2.415 to 2.435 GHz. Requirements: RHCP gain 6.5 dBic or more, return loss 10 dB or more, beamwidth 60° or wider, right-hand circular, all across the channel. Dual-feed gain has 0.4 dB taken off for the coupler.

## Verdict

**At nominal nothing changes: three of the four pass in both tools, and the 1.5 mm dual feed is borderline.** The new checks split the four more clearly than that.

| | Cut corner, 1.5 mm | Dual feed, 1.5 mm | Cut corner, 3 mm | Dual feed, 3 mm |
| --- | --- | --- | --- | --- |
| Nominal, lowest gain, HFSS / openEMS | 7.08 / 6.80 dBic | 6.75 / 6.49 dBic | 7.61 / 7.32 dBic | 7.26 / 7.06 dBic |
| Nominal, strict verdict (worse of the two tools) | pass | borderline | pass | pass |
| Lowest gain in the checks the task asked for | 6.73 dBic (+85 °C) | 6.43 dBic (+85 °C) | 7.49 dBic (glue joint) | 7.12 dBic (glue joint, larger air box) |
| Worst return loss in those checks | 13.3 dB (+85 °C) | 9.8 dB (+85 °C) | 18.5 dB (top mask) | 11.9 dB (glue joint) |
| Holds gain, match, beamwidth and hand in all of them | yes | **no** | yes | yes |
| Extra run: SMA and glue joint together, the boards as drawn | | | 7.44 dBic, 21.5 dB: holds | 6.99 dBic, 10.8 dB: holds, narrowly |
| Extra run: the same plus solder mask on top | | | 7.29 dBic, 18.7 dB: holds | 6.83 dBic, **9.0 dB: does not hold** |
| Worst axial ratio in any run here (no requirement set) | 6.13 dB (−40 °C) | 0.14 dB | 5.51 dB (SMA, mask and joint together) | 0.34 dB (glue joint) |

What changed from [`RERUN_CHECK.md`](RERUN_CHECK.md):

- **The earlier HFSS numbers are confirmed.** All four reruns reproduce them exactly.
- **The 1.5 mm dual feed goes from "borderline" to "does not hold".** At nominal HFSS puts it at 6.70 to 6.78 dBic whatever the mesh or air box, so the 6.49 dBic in openEMS is not a meshing accident in HFSS. But with the datasheet's temperature drift it fails in HFSS too: 9.9 dB return loss and 6.50 dBic at −40 °C, 9.8 dB and 6.43 dBic at +85 °C. Its 32 MHz match window is too narrow for a ±6 MHz drift.
- **The 1.5 mm cut corner keeps its gain and match over temperature** (6.73 dBic and 13.3 dB at worst), but its axial ratio goes to about 6 dB at both extremes.
- **Both 3 mm boards pass every check that was asked for**: larger air box, SMA, solder mask on top, mask and adhesive in the glue joint, −40 °C and +85 °C. The dual feed's axial ratio never moves. The cut corner's rises to 3.05 dB with top mask, 3.23 dB at +85 °C and 4.10 dB with the mask-and-adhesive joint.
- **The left-out effects all pull the 3 mm boards down in frequency**, and they add. The task asked for them one at a time, so four extra runs put them together. As drawn (SMA and the mask-and-adhesive joint, no mask on the patch side) the cut corner moves −10 MHz and the dual feed −15 MHz, and both still hold, the dual feed with only 0.8 dB of return loss to spare. With solder mask on top as well, the shift is −20 to −24 MHz and the dual feed's return loss is 9.0 dB, under the requirement. See "The left-out effects together" below.
- **HFSS's higher gain is not the air box.** A box twice as deep moves the gain by −0.14 to +0.02 dB.
- **The board files match the designs.**

## Part 1: the four at nominal

Each run at about 40,000 mesh elements, tagged `rerun`.

| Antenna | Run | Best match at | Worst return loss | Match window | Lowest RHCP gain | Worst axial ratio | Beamwidth | Hand |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cut corner, 1.5 mm | earlier HFSS | 2.4455 GHz | 15.5 dB | 66 MHz | 7.08 dBic | 4.14 dB | 72° | RHCP |
| | HFSS rerun | 2.4455 GHz | 15.5 dB | 66 MHz | 7.08 dBic | 4.14 dB | 72° | RHCP |
| | rerun minus earlier | 0.0 MHz | 0.0 dB | 0 MHz | 0.00 dB | 0.00 dB | 0° | |
| | openEMS, 24 Nov | 2.4500 GHz | 12.8 dB | 64 MHz | 6.80 dBic | 3.94 dB | | RHCP |
| Dual feed, 1.5 mm | earlier HFSS | 2.4250 GHz | 13.6 dB | 32 MHz | 6.75 dBic | 0.11 dB | 72° | RHCP |
| | HFSS rerun | 2.4250 GHz | 13.6 dB | 32 MHz | 6.75 dBic | 0.11 dB | 72° | RHCP |
| | rerun minus earlier | 0.0 MHz | 0.0 dB | 0 MHz | 0.00 dB | 0.00 dB | 0° | |
| | openEMS, 24 Nov | 2.4290 GHz | 11.0 dB | 31 MHz | 6.49 dBic | 0.07 dB | | RHCP |
| Cut corner, 3 mm | earlier HFSS | 2.3940 GHz | 19.1 dB | 131 MHz | 7.61 dBic | 2.17 dB | 73° | RHCP |
| | HFSS rerun | 2.3940 GHz | 19.1 dB | 131 MHz | 7.61 dBic | 2.17 dB | 73° | RHCP |
| | rerun minus earlier | 0.0 MHz | 0.0 dB | 0 MHz | 0.00 dB | 0.00 dB | 0° | |
| | openEMS, 24 Nov | 2.3870 GHz | 13.4 dB | 127 MHz | 7.32 dBic | 2.07 dB | | RHCP |
| Dual feed, 3 mm | earlier HFSS | 2.4225 GHz | 16.4 dB | 61 MHz | 7.26 dBic | 0.28 dB | 73° | RHCP |
| | HFSS rerun | 2.4225 GHz | 16.4 dB | 61 MHz | 7.26 dBic | 0.28 dB | 73° | RHCP |
| | rerun minus earlier | 0.0 MHz | 0.0 dB | 0 MHz | 0.00 dB | 0.00 dB | 0° | |
| | openEMS, 24 Nov | 2.4260 GHz | 17.3 dB | 57 MHz | 7.06 dBic | 0.28 dB | | RHCP |

- **Does the rerun reproduce the earlier HFSS run (within 2 MHz and 0.1 dB)?** Yes, for all four, and exactly: 0.0 MHz, 0.00 dB, and the same number of mesh elements. HFSS gives the same answer for the same inputs on the same machine, so this confirms the stored results and that the scripts on `main` still build the same models. It is not independent evidence about the antennas. The runs with a finer mesh and a larger air box below are: they move the best match by 1 to 4 MHz and the gain by 0.02 to 0.14 dB.
- **Does the strict verdict change?** No. Cut corner 1.5 mm: pass. Dual feed 1.5 mm: borderline (HFSS 6.75, openEMS 6.49 dBic). Cut corner 3 mm: pass. Dual feed 3 mm: pass.

How the numbers are taken, the same way as in `RERUN_CHECK.md`: for the dual feeds, return loss, best match and match window are the reflection seen at J1 with J2 driven 90° behind it; gain is with a typical coupler (0.5 dB and 3° off) minus 0.4 dB; axial ratio is with a perfect coupler.

## Part 2: the open questions

### 1. Is the 1.5 mm dual feed above 6.5 dBic?

**At nominal, yes in HFSS and by a stable 0.2 to 0.3 dB; but the margin is smaller than the temperature drift, so it should not be counted as passing.** Fairly sure.

| Run | Mesh elements | Best match at | Lowest gain in channel | Worst return loss |
| --- | --- | --- | --- | --- |
| Nominal (40,000 target) | 43,596 | 2.4250 GHz | 6.75 dBic | 13.6 dB |
| Finest mesh | 58,212 | 2.4260 GHz | 6.70 dBic | 12.8 dB |
| Air box 62 mm | 46,473 | 2.4230 GHz | 6.77 dBic | 12.1 dB |
| Air box 62 mm and finest mesh | 54,758 | 2.4235 GHz | 6.78 dBic | 12.6 dB |
| openEMS, 24 November | | 2.4290 GHz | 6.49 dBic | 11.0 dB |

- **58,212 elements is the finest mesh the Student licence allowed here.** The limit is 64,000 and HFSS refines in steps of up to about 25 %, so the next step would have gone over.
- **Where the 0.26 dB between the tools comes from.** At the centre of the channel the two differ by 0.14 dB (7.36 against 7.22 dBic before the coupler). At the lower channel edge they differ by about 0.27 dB (7.16 against 6.89 dBic), and the extra is match: openEMS puts the best match 4 MHz higher, so its lower edge is further down the slope (11.0 dB return loss against 13.5 dB, which is 0.16 dB more reflected power). With the match difference taken out, HFSS reads 0.10 to 0.12 dB higher than openEMS right across the channel.
- **Which figure to trust.** For the gain at the centre of the channel, HFSS: about 6.9 to 7.0 dBic after the coupler. It does not move with mesh or air box (±0.04 dB), and it models the real 0.5 mm feed pin. For the lowest gain in the channel, neither to better than about ±0.15 dB, because that number depends on where the best match lands, and 4 MHz is 0.16 %, well inside the accuracy of either tool and of the board's Dk. A real board will sit somewhere between 6.5 and 6.8 dBic at its worse channel edge if nothing else is off.
- **Why that is not a pass.** The same board loses 0.25 dB at −40 °C and 0.32 dB at +85 °C (item 5), and 0.37 dB with solder mask over it (run of 14 November). Any one of those takes it to 6.4 to 6.5 dBic and under 10 dB return loss.

### 2. Is HFSS's higher gain the air box?

**No. Fairly sure.** With the air box padded to 62 mm (half a wavelength) instead of a quarter:

| Antenna | Lowest gain, quarter-wave box | Lowest gain, half-wave box | Change | Directivity | Efficiency | Best match moves |
| --- | --- | --- | --- | --- | --- | --- |
| Cut corner, 1.5 mm | 7.08 dBic | 7.03 dBic | −0.05 dB | 7.97 to 7.89 dBi | 87.1 to 88.6 % | −1.5 MHz |
| Dual feed, 1.5 mm | 6.75 dBic | 6.77 dBic | +0.02 dB | 7.97 to 7.94 dBi | 87.1 to 88.9 % | −2.0 MHz |
| Cut corner, 3 mm | 7.61 dBic | 7.56 dBic | −0.05 dB | 7.96 to 7.83 dBi | 94.8 to 96.6 % | −4.0 MHz |
| Dual feed, 3 mm | 7.26 dBic | 7.12 dBic | −0.14 dB | 7.98 to 7.83 dBi | 94.8 to 96.2 % | −4.0 MHz |

- The larger box lowers the directivity by 0.03 to 0.15 dB and raises the efficiency by about 1.5 points, and the two nearly cancel. HFSS is still 0.2 to 0.3 dB above openEMS on three boards, and 0.06 dB above it on the 3 mm dual feed.
- The box does move the frequency by 1.5 to 4 MHz, and with it the cut corners' worst axial ratio (4.14 to 4.65 dB at 1.5 mm, 2.17 to 2.61 dB at 3 mm). That is a fair measure of how well either HFSS setup pins the frequency: a few MHz.
- What the 0.1 to 0.2 dB between the tools is, once match is taken out, these runs do not say. Candidates are the far-field calculation, the copper-loss model and the feed model. It is small against the 0.4 dB assumed for the coupler.

### 3. The 3 mm boards with the SMA and with solder mask

**Both still meet the requirements with either. Fairly sure; one mesh each.**

| 3 mm antenna | Case | Best match moves | Lowest gain | Worst return loss | Worst axial ratio |
| --- | --- | --- | --- | --- | --- |
| Cut corner | nominal | 0 | 7.61 dBic | 19.1 dB | 2.17 dB |
| Cut corner | with the SMA | +3.0 MHz | 7.60 dBic | 21.0 dB | 2.03 dB |
| Cut corner | with solder mask on top | −8.5 MHz | 7.58 dBic | 18.5 dB | 3.05 dB |
| Dual feed | nominal | 0 | 7.26 dBic | 16.4 dB | 0.28 dB |
| Dual feed | with the SMA | −4.5 MHz | 7.17 dBic | 13.7 dB | 0.31 dB |
| Dual feed | with solder mask on top | −9.0 MHz | 7.16 dBic | 12.8 dB | 0.26 dB |

- **SMA** (5 mm of 50 Ω coax with the SMA's 1.27 mm pin, and a wave port, in place of the lumped port): a shift of +3 MHz on the cut corner and −4.5 MHz on the dual feed, and under 0.1 dB of gain. The same size as at 1.5 mm (−2.5 to −4 MHz).
- **Solder mask over the top, open over the patch**: −8.5 to −9 MHz and 0.03 to 0.10 dB of gain. Also the same size as at 1.5 mm (−6 to −8.5 MHz). The cut corner's axial ratio goes from 2.17 to 3.05 dB.
- The current 3 mm TOP boards have no mask at all on the front (`kicad/prototype_thick/README.md`), so the mask run is the pessimistic case for them.

### 4. Solder mask in the glue joint

**A 0.09 mm layer of Dk 3.5 between the boards moves both 3 mm antennas down about 12 MHz. Both still meet the requirements; the cut corner's axial ratio goes to 4.1 dB. Fairly sure about the size of the shift, less sure the layer is modelled well.**

| 3 mm antenna | Best match moves | Lowest gain | Worst return loss | Worst axial ratio |
| --- | --- | --- | --- | --- |
| Cut corner, nominal | 0 | 7.61 dBic | 19.1 dB | 2.17 dB |
| Cut corner, 0.09 mm of Dk 3.5 in the joint | −12.5 MHz | 7.49 dBic | 19.4 dB | 4.10 dB |
| Dual feed, nominal | 0 | 7.26 dBic | 16.4 dB | 0.28 dB |
| Dual feed, 0.09 mm of Dk 3.5 in the joint | −12.0 MHz | 7.12 dBic | 11.9 dB | 0.34 dB |

- Modelled the same way as the earlier 0.05 mm adhesive case: the layer is folded into one substrate of the total thickness (3.138 mm) with the series-averaged Dk (2.570). The field under a patch runs straight from patch to ground, so layers in the stack act like capacitors in series. This ignores the fringing field at the patch edge and assumes the layer is even and has no air in it.
- For scale: 0.05 mm of Dk 3.0 adhesive alone gave about −5 MHz, and 0.05 mm of air gave +24 MHz (`results_hfss/thick_tables.md`).
- Dk 3.5 and 0.09 mm are the task's figures for two mask layers plus adhesive. The real mask and adhesive are not chosen.

### The left-out effects together (extra, not in the task list)

**The SMA, top mask and joint layer each move the 3 mm boards down in frequency, and the shifts add. As drawn, both boards still meet the requirements; with top mask added, the dual feed does not. Fairly sure of the shifts; one mesh each.**

| 3 mm antenna | Case | Best match moves | Lowest gain | Worst return loss | Worst axial ratio | Requirements |
| --- | --- | --- | --- | --- | --- | --- |
| Cut corner | SMA and joint layer, no top mask (as drawn) | −10.0 MHz | 7.44 dBic | 21.5 dB | 4.18 dB | pass |
| Cut corner | SMA, joint layer and top mask | −20.5 MHz | 7.29 dBic | 18.7 dB | 5.51 dB | pass |
| Dual feed | SMA and joint layer, no top mask (as drawn) | −15.0 MHz | 6.99 dBic | 10.8 dB | 0.30 dB | pass |
| Dual feed | SMA, joint layer and top mask | −24.0 MHz | 6.83 dBic | 9.0 dB | 0.31 dB | **fail** |

- **The single shifts add up.** Dual feed: −4.5 (SMA) and −12 (joint) make −16.5 against −15 simulated; with −9 for top mask, −25.5 against −24. Cut corner: +3 and −12.5 make −9.5 against −10; with −8.5 for mask, −18 against −20.5.
- **"As drawn" means** the current `kicad/prototype_thick` boards: no mask on the patch side of the TOP boards, and the factory's default mask on both bond faces, which the 0.09 mm joint layer stands for.
- **The dual feed has the least room.** Its match window is 61 MHz wide, so it tolerates about 15 to 20 MHz of shift before return loss reaches 10 dB. The joint and the SMA use most of that before temperature (±6 MHz) or any tolerance is counted.
- **The cut corner's gain and match have plenty of room, but its polarization does not.** Its axial ratio is 4.2 dB as drawn and 5.5 dB with top mask. No requirement is set on axial ratio; 5.5 dB costs about 0.4 dB against a perfectly circular ground antenna, and that loss is already inside the RHCP gain figure.
- **These shifts are systematic, so they could be tuned out** by making the patch about 0.15 to 0.4 mm smaller (the boards move about 64 MHz per mm), or reduced by leaving mask off the bond faces. Nothing was re-tuned here. The README's note points the other way (the simulations read 10 to 20 MHz low against two published measured patches), so the two partly cancel, and only a measured board will settle which wins.

### 5. Temperature, with the datasheet's numbers

**Each board drifts about −6 MHz at −40 °C and +6 MHz at +85 °C. Three of the four still meet the requirements at both extremes; the 1.5 mm dual feed does not. Fairly sure of the drift, since it follows directly from the datasheet figures.**

Dk scaled by −115 ppm/°C and L, feed and cut by 15.5 ppm/°C from 20 °C. The sideways feed offset of the 3 mm cut corner was scaled too. Board thickness, board outline and loss tangent were left alone.

| Antenna | Temperature | Best match moves | Lowest gain | Worst return loss | Worst axial ratio | Requirements |
| --- | --- | --- | --- | --- | --- | --- |
| Cut corner, 1.5 mm | −40 °C | −5.0 MHz | 6.87 dBic | 15.1 dB | 6.13 dB | pass |
| Cut corner, 1.5 mm | 20 °C (nominal) | 0 | 7.08 dBic | 15.5 dB | 4.14 dB | pass |
| Cut corner, 1.5 mm | +85 °C | +6.0 MHz | 6.73 dBic | 13.3 dB | 5.91 dB | pass |
| Dual feed, 1.5 mm | −40 °C | −6.5 MHz | 6.50 dBic | 9.9 dB | 0.10 dB | **fail** |
| Dual feed, 1.5 mm | 20 °C (nominal) | 0 | 6.75 dBic | 13.6 dB | 0.11 dB | pass |
| Dual feed, 1.5 mm | +85 °C | +6.5 MHz | 6.43 dBic | 9.8 dB | 0.07 dB | **fail** |
| Cut corner, 3 mm | −40 °C | −6.0 MHz | 7.61 dBic | 19.1 dB | 2.82 dB | pass |
| Cut corner, 3 mm | 20 °C (nominal) | 0 | 7.61 dBic | 19.1 dB | 2.17 dB | pass |
| Cut corner, 3 mm | +85 °C | +6.5 MHz | 7.58 dBic | 19.5 dB | 3.23 dB | pass |
| Dual feed, 3 mm | −40 °C | −5.5 MHz | 7.18 dBic | 13.9 dB | 0.32 dB | pass |
| Dual feed, 3 mm | 20 °C (nominal) | 0 | 7.26 dBic | 16.4 dB | 0.28 dB | pass |
| Dual feed, 3 mm | +85 °C | +6.0 MHz | 7.21 dBic | 15.8 dB | 0.31 dB | pass |

- **The drift is about 0.1 MHz per °C, or 12 MHz from −40 to +85 °C.** Hand check: frequency goes as 1/(L√Dk), so it drifts by 115/2 − 15.5 = 42 ppm/°C, which is +6.6 MHz at +85 °C and −6.1 MHz at −40 °C. The runs give +6.0 to +6.5 and −5.0 to −6.5 MHz.
- **This is twice the earlier assumed case** (Dk ±0.3 %, about ±4 MHz, in `HFSS_RESULTS.md`).
- **1.5 mm dual feed:** 9.9 dB and 6.50 dBic at −40 °C, 9.8 dB and 6.43 dBic at +85 °C. It misses the match requirement at both ends and the gain requirement at the hot end.
- **1.5 mm cut corner:** gain and match hold (6.73 dBic and 13.3 dB at worst). Its axial ratio at the channel edge goes from 4.1 dB to about 6 dB, which costs about 0.45 dB against a perfectly circular ground antenna; that loss is already inside the RHCP gain figure.
- **3 mm boards:** gain moves by under 0.1 dB and return loss stays above 13 dB. The cut corner's axial ratio is 2.82 dB cold and 3.23 dB hot.
- The satellite will not sit at either extreme for long, and these are steady-state cases with the whole board at one temperature.

### 6. Board files against the designs

**Every board in the README table matches its simulated design, and the bond faces of the 3 mm boards have no copper. Sure.**

[`check_boards.py`](check_boards.py) reads the `.kicad_pcb` files as text and unpacks the Gerber zips in `fab/` itself. It does not use KiCad, `generate_boards.py` or `prototype_thick.py`, and it changes nothing. Full output in [`results_hfss/board_check.md`](results_hfss/board_check.md).

| Board | Patch side | Corner cuts | Feed holes from the patch centre (x right, y up) | Matches the design |
| --- | --- | --- | --- | --- |
| Cut corner, 1.5 mm (`Cutcorner_antenna`, hand-drawn) | 37.520 mm | 3.500 mm, top-left and bottom-right | (7.000, 0.000) | yes |
| Dual feed, 1.5 mm (`A_dualfeed_PTFE_face100`) | 37.280 mm | none | (5.800, 0.000) and (0.000, 5.800) | yes |
| Its −0.3 and +0.3 mm variants | 36.980 and 37.580 mm | none | same | yes |
| Cut corner, 3 mm, TOP and BOTTOM | 37.100 mm | 5.550 mm, top-left and bottom-right | (8.000, 2.180) | yes |
| Dual feed, 3 mm, TOP and BOTTOM | 36.390 mm | none | (6.700, 0.000) and (0.000, 6.700) | yes |

- Patch dimensions were measured twice: from the copper polygon in the KiCad file and from the copper region in the F.Cu Gerber. They agree to 0.001 mm.
- TOP and BOTTOM feed holes of each 3 mm pair are at the same position (0.0000 mm apart, measured from each board's centre).
- **Bond faces:** the B.Cu Gerber of each 3 mm TOP board and the F.Cu Gerber of each 3 mm BOTTOM board contain no drawn, flashed or filled copper at all. In the KiCad files the only objects on those layers are the mounting holes (no copper) and the feed pad, which is set to drop its copper on layers where nothing connects to it.
- Two things noticed, neither a mismatch: the feed pad on each 3 mm TOP board is not flashed on F.Cu either, which is harmless because the hole sits inside the patch copper; and on each 3 mm BOTTOM board the feed hole has its own 1.2 mm pad under the SMA's centre pad on B.Cu, as intended.

## Every run

One row per run. The shift and gain-change columns compare each run with the nominal rerun of the same antenna. "Requirements" is gain, return loss, beamwidth and hand; axial ratio is not in it.

| Antenna | Case | Best match at | Worst return loss | Match window | RHCP gain in channel | Worst axial ratio | Beamwidth | Hand | Mesh elements | Shift of best match | Change in lowest gain | Requirements |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cut corner, 1.5 mm | Rerun, nominal | 2.4455 GHz | 15.5 dB | 66 MHz | 7.08 to 7.24 dBic | 4.14 dB | 72° | RHCP | 40404 | | | pass |
| Cut corner, 1.5 mm | Air box 62 mm (half a wavelength) | 2.4440 GHz | 15.5 dB | 66 MHz | 7.03 to 7.24 dBic | 4.65 dB | 73° | RHCP | 47290 | -1.5 MHz | -0.05 dB | pass |
| Cut corner, 1.5 mm | With the SMA (coax and wave port) (earlier run, 14 Nov) | 2.4415 GHz | 18.2 dB | 66 MHz | 7.08 to 7.27 dBic | 4.33 dB | 72° | RHCP | 41039 | -4.0 MHz | +0.00 dB | pass |
| Cut corner, 1.5 mm | With solder mask on the top (earlier run, 14 Nov) | 2.4395 GHz | 14.8 dB | 68 MHz | 6.80 to 7.16 dBic | 6.57 dB | 72° | RHCP | 44083 | -6.0 MHz | -0.28 dB | pass |
| Cut corner, 1.5 mm | -40 C (Dk 2.5676, sizes x 0.99907) | 2.4405 GHz | 15.1 dB | 67 MHz | 6.87 to 7.21 dBic | 6.13 dB | 72° | RHCP | 40559 | -5.0 MHz | -0.21 dB | pass |
| Cut corner, 1.5 mm | +85 C (Dk 2.5309, sizes x 1.00101) | 2.4515 GHz | 13.3 dB | 65 MHz | 6.73 to 7.28 dBic | 5.91 dB | 72° | RHCP | 45322 | +6.0 MHz | -0.35 dB | pass |
| Dual feed, 1.5 mm | Rerun, nominal | 2.4250 GHz | 13.6 dB | 32 MHz | 6.75 to 6.96 dBic | 0.11 dB | 72° | RHCP | 43596 | | | pass |
| Dual feed, 1.5 mm | Finest mesh | 2.4260 GHz | 12.8 dB | 32 MHz | 6.70 to 6.94 dBic | 0.14 dB | 73° | RHCP | 58212 | +1.0 MHz | -0.05 dB | pass |
| Dual feed, 1.5 mm | Air box 62 mm (half a wavelength) | 2.4230 GHz | 12.1 dB | 32 MHz | 6.77 to 7.00 dBic | 0.13 dB | 72° | RHCP | 46473 | -2.0 MHz | +0.02 dB | pass |
| Dual feed, 1.5 mm | Air box 62 mm and finest mesh | 2.4235 GHz | 12.6 dB | 32 MHz | 6.78 to 6.98 dBic | 0.14 dB | 72° | RHCP | 54758 | -1.5 MHz | +0.03 dB | pass |
| Dual feed, 1.5 mm | With the SMA (coax and wave port) (earlier run, 14 Nov) | 2.4210 GHz | 11.0 dB | 32 MHz | 6.58 to 6.87 dBic | 0.04 dB | 73° | RHCP | 41250 | -4.0 MHz | -0.17 dB | pass |
| Dual feed, 1.5 mm | With solder mask on the top (earlier run, 14 Nov) | 2.4165 GHz | 9.1 dB | 32 MHz | 6.38 to 6.89 dBic | 0.06 dB | 73° | RHCP | 40595 | -8.5 MHz | -0.37 dB | FAIL |
| Dual feed, 1.5 mm | -40 C (Dk 2.5676, sizes x 0.99907) | 2.4185 GHz | 9.9 dB | 32 MHz | 6.50 to 6.92 dBic | 0.10 dB | 73° | RHCP | 40089 | -6.5 MHz | -0.25 dB | FAIL |
| Dual feed, 1.5 mm | +85 C (Dk 2.5309, sizes x 1.00101) | 2.4315 GHz | 9.8 dB | 32 MHz | 6.43 to 6.93 dBic | 0.07 dB | 73° | RHCP | 48339 | +6.5 MHz | -0.32 dB | FAIL |
| Cut corner, 3 mm | Rerun, nominal | 2.3940 GHz | 19.1 dB | 131 MHz | 7.61 to 7.67 dBic | 2.17 dB | 73° | RHCP | 49915 | | | pass |
| Cut corner, 3 mm | Air box 62 mm (half a wavelength) | 2.3900 GHz | 19.3 dB | 131 MHz | 7.56 to 7.62 dBic | 2.61 dB | 73° | RHCP | 42218 | -4.0 MHz | -0.05 dB | pass |
| Cut corner, 3 mm | With the SMA (coax and wave port) | 2.3970 GHz | 21.0 dB | 129 MHz | 7.60 to 7.66 dBic | 2.03 dB | 73° | RHCP | 44479 | +3.0 MHz | -0.01 dB | pass |
| Cut corner, 3 mm | With solder mask on the top | 2.3855 GHz | 18.5 dB | 132 MHz | 7.58 to 7.67 dBic | 3.05 dB | 72° | RHCP | 45926 | -8.5 MHz | -0.03 dB | pass |
| Cut corner, 3 mm | 0.09 mm of Dk 3.5 in the glue joint | 2.3815 GHz | 19.4 dB | 133 MHz | 7.49 to 7.67 dBic | 4.10 dB | 73° | RHCP | 43858 | -12.5 MHz | -0.12 dB | pass |
| Cut corner, 3 mm | SMA and glue-joint layer together, no top mask: the boards as drawn (extra run) | 2.3840 GHz | 21.5 dB | 131 MHz | 7.44 to 7.66 dBic | 4.18 dB | 73° | RHCP | 41239 | -10.0 MHz | -0.17 dB | pass |
| Cut corner, 3 mm | SMA, top mask and glue-joint layer together (extra run) | 2.3735 GHz | 18.7 dB | 133 MHz | 7.29 to 7.62 dBic | 5.51 dB | 72° | RHCP | 41145 | -20.5 MHz | -0.32 dB | pass |
| Cut corner, 3 mm | -40 C (Dk 2.5676, sizes x 0.99907) | 2.3880 GHz | 19.1 dB | 131 MHz | 7.61 to 7.69 dBic | 2.82 dB | 72° | RHCP | 41852 | -6.0 MHz | +0.00 dB | pass |
| Cut corner, 3 mm | +85 C (Dk 2.5309, sizes x 1.00101) | 2.4005 GHz | 19.5 dB | 131 MHz | 7.58 to 7.72 dBic | 3.23 dB | 72° | RHCP | 46113 | +6.5 MHz | -0.03 dB | pass |
| Dual feed, 3 mm | Rerun, nominal | 2.4225 GHz | 16.4 dB | 61 MHz | 7.26 to 7.32 dBic | 0.28 dB | 73° | RHCP | 49873 | | | pass |
| Dual feed, 3 mm | Air box 62 mm (half a wavelength) | 2.4185 GHz | 14.4 dB | 61 MHz | 7.12 to 7.22 dBic | 0.31 dB | 73° | RHCP | 51335 | -4.0 MHz | -0.14 dB | pass |
| Dual feed, 3 mm | With the SMA (coax and wave port) | 2.4180 GHz | 13.7 dB | 61 MHz | 7.17 to 7.25 dBic | 0.31 dB | 72° | RHCP | 42235 | -4.5 MHz | -0.09 dB | pass |
| Dual feed, 3 mm | With solder mask on the top | 2.4135 GHz | 12.8 dB | 62 MHz | 7.16 to 7.32 dBic | 0.26 dB | 72° | RHCP | 40024 | -9.0 MHz | -0.10 dB | pass |
| Dual feed, 3 mm | 0.09 mm of Dk 3.5 in the glue joint | 2.4105 GHz | 11.9 dB | 62 MHz | 7.12 to 7.32 dBic | 0.34 dB | 72° | RHCP | 47470 | -12.0 MHz | -0.14 dB | pass |
| Dual feed, 3 mm | SMA and glue-joint layer together, no top mask: the boards as drawn (extra run) | 2.4075 GHz | 10.8 dB | 62 MHz | 6.99 to 7.23 dBic | 0.30 dB | 73° | RHCP | 46327 | -15.0 MHz | -0.27 dB | pass |
| Dual feed, 3 mm | SMA, top mask and glue-joint layer together (extra run) | 2.3985 GHz | 9.0 dB | 62 MHz | 6.83 to 7.19 dBic | 0.31 dB | 72° | RHCP | 41972 | -24.0 MHz | -0.43 dB | FAIL |
| Dual feed, 3 mm | -40 C (Dk 2.5676, sizes x 0.99907) | 2.4170 GHz | 13.9 dB | 61 MHz | 7.18 to 7.30 dBic | 0.32 dB | 73° | RHCP | 49081 | -5.5 MHz | -0.08 dB | pass |
| Dual feed, 3 mm | +85 C (Dk 2.5309, sizes x 1.00101) | 2.4285 GHz | 15.8 dB | 62 MHz | 7.21 to 7.34 dBic | 0.31 dB | 72° | RHCP | 44390 | +6.0 MHz | -0.05 dB | pass |

Two runs stalled part-way and solved on their second attempt (the two glue-joint runs): once because the laptop went to sleep, once because Ansys sat idle. No run failed three times.

## What this does not show

- **Nothing has been built or measured.** The two tools agree with each other to a few MHz and 0.3 dB; neither has been checked against a board from this project.
- **Every HFSS run is one mesh**, except the 1.5 mm dual feed. From the mesh and air-box runs, expect about ±0.05 dB in gain, ±2 to 4 MHz in frequency and ±0.5 dB in a cut corner's worst axial ratio from the setup alone.
- **Tolerances were not rerun.** Dk ±1.2 % and the patch ±0.3 mm (`HFSS_RESULTS.md`, `results_hfss/thick_tables.md`) shift things by 13 to 19 MHz, more than temperature or any left-out effect here, and they stack on top.
- **Air in the glue joint** remains the largest single risk for the 3 mm boards (+24 MHz for 0.05 mm) and was not rerun.
- **A real coupler, its load and the two cables** for the dual feeds; the 0.4 dB and the 0.5 dB / 3° are assumed.
- **The UHF tape antenna on the same face, the real satellite body, and power handling.**
- **2.425 GHz is still an assumed carrier.**

One housekeeping note: `main` was built from `hfss-overnight` one commit before its tip. The last commit there (`ddf63ae`: a written report on the 3 mm boards, `sim/THICK_BOARD.md`, and three dual-feed runs with an air film or adhesive in the joint) is on `hfss-overnight` only. Nothing was merged here.

## How to reproduce

```
C="--er 2.55 --tand 0.0018 --Gm 100 --target-tets 40000 --project-dir <a folder that is not synced>"
python sim/hfss_patch.py --board B --L 37.52 --feed 7.00 --cut 3.50 $C --tag rerun
python sim/hfss_patch.py --board A --L 37.28 --feed 5.80 $C --tag rerun
python sim/hfss_patch.py --board B --L 37.10 --feed 8.00 --feed_y 2.18 --cut 5.55 --h 3.048 --ff_half 60 --ff_step 5 $C --tag rerun
python sim/hfss_patch.py --board A --L 36.39 --feed 6.70 --h 3.048 --ff_half 60 --ff_step 5 $C --tag rerun
python sim/rerun_report.py      # the tables above, into sim/results_hfss/rerun_tables.md
python sim/check_boards.py      # the board check
```

The other runs add to those four lines:

| Case | Added options |
| --- | --- |
| Finest mesh | `--target-tets 50000` in place of 40000, `--tag fine` |
| Larger air box | `--pad 62 --tag pad62` |
| SMA | `--sma --tag sma` |
| Solder mask on top | `--mask --tag mask` |
| Glue joint | `--h 3.138 --er 2.5700 --tag joint` |
| −40 °C | `--er 2.5676 --tag m40C`, and L, feed, feed_y and cut multiplied by 0.99907 |
| +85 °C | `--er 2.5309 --tag p85C`, and L, feed, feed_y and cut multiplied by 1.00101 |
| SMA and glue joint together (extra) | `--sma --h 3.138 --er 2.5700 --tag smajoint` |
| SMA, top mask and glue joint together (extra) | `--sma --mask --h 3.138 --er 2.5700 --tag allthree` |

Each result folder's `summary.json` records the exact options used.
