# Stacked patches and the board-size sweep

Run in Ansys HFSS (Electronics Desktop Student 2025 R2) on 19 and 20 November 2026. Everything here is simulation. Nothing has been built or measured.

All four antennas use JLC's PTFE (ZYF255DA, Dk 2.55, 1.524 mm) and are tuned for 2.425 GHz with a 20 MHz channel (2.415 to 2.435 GHz). Unless a table says otherwise, the board is 60 mm square on a 100 mm metal face, and the mesh is about 40,000 elements.

## Summary

- **There are now four tuned antennas:** cut corner, dual feed, stacked cut corner and stacked dual feed. The two stacked ones are new.
- **Stacking adds about 1.4 to 1.5 dB of gain and widens every window by about three times.** The cost is a second board held 5.0 mm above the first, which makes the antenna about 8 mm tall instead of 1.5 mm.
- **A shorter stack works nearly as well.** Re-tuned for a 3.0 mm gap (about 6.0 mm tall), the stacked cut corner gives 8.45 to 8.51 dBic and a better match, but its polarization window is 35 MHz instead of 49 MHz, so it is more sensitive to manufacturing error. See section 6.
- **On the stacked patch, the dual feed is not better than the cut corner.** With a typical coupler its axial ratio is about the same (1.48 against 1.39 dB), its gain is 0.2 dB lower, and it needs a coupler, a load and a second line.
- **Board size barely changes anything when the board sits on the 100 mm metal face.** From 50 to 100 mm, gain moves by less than 0.1 dB and beamwidth by less than 1 degree for all four. The one exception is the stacked cut corner at 50 mm, where the axial ratio rises to 3.34 dB.
- **Hand calculations agree with HFSS** within 3 % on patch size and within 10 % on bandwidth for all four. See [`HAND_CALCS.md`](HAND_CALCS.md).
- **A flat alternative was tuned afterwards:** one patch on two boards bonded with no air gap (3 mm tall). It gives 7.3 to 7.7 dBic, between the thin boards and the stacks. See [`THICK_BOARD.md`](THICK_BOARD.md).

## 1. The four antennas side by side

![Four antennas compared](results_hfss/compare_three.png)

| | Cut corner | Dual feed | Stacked cut corner | Stacked dual feed | Requirement |
| --- | --- | --- | --- | --- | --- |
| Worst S11 in the channel | −15.5 dB | −13.6 dB | −12.7 dB | −19.2 dB | −10 dB or lower |
| −10 dB match window | 66 MHz | 32 MHz | 206 MHz | 106 MHz | covers the channel |
| Worst axial ratio in the channel | 4.14 dB | 0.79 dB | 1.39 dB | 1.48 dB | 3 dB or lower |
| 3 dB axial-ratio window | 16 MHz | set by the coupler | 49 MHz | set by the coupler | 20 MHz or more |
| RHCP gain in the channel | 7.08 to 7.24 dBic | 6.75 to 6.96 dBic | 8.49 to 8.56 dBic | 8.28 to 8.34 dBic | 6.5 dBic or more |
| Half-power beamwidth | 72° | 72° | 66° | 66° | 60° or wider |
| Height | 1.5 mm | 1.5 mm | 8.0 mm | 8.0 mm | |
| Extra parts | none | coupler, load, second line | second board, spacers | all of those | |

The two dual-feed columns assume a typical 90° coupler (0.5 dB and 3° off, 0.4 dB loss). With a perfect coupler their axial ratio would be 0.1 dB and 0.9 dB.

What the rows mean, briefly:

- **S11** is how much of the transmitter's power bounces back from the antenna. −10 dB means 10 % bounces back.
- **Axial ratio** is how round the circular polarization is. 0 dB is a perfect circle. At 3 dB about 0.13 dB of signal is lost to a perfectly circular ground antenna.
- **Gain** is how much the antenna concentrates power straight ahead.

The single cut corner misses the 3 dB axial-ratio limit at the channel edges (4.14 dB) because its axial-ratio window is 16 MHz and the channel is 20 MHz. It meets the limit over the middle 16 MHz.

## 2. The stacked patch

![Stacked patch drawing](../docs/stacked_patch_drawing.png)

A second, slightly larger patch sits on its own board 5.0 mm above the fed patch. Only the lower patch has a feed. The upper patch is excited through the air gap.

| Dimension | Stacked cut corner | Stacked dual feed |
| --- | --- | --- |
| Lower patch side | 36.26 mm | 35.04 mm |
| Lower patch corner cut | 6.56 mm | none |
| Feed distance from centre | 15.96 mm | 13.35 mm (both feeds) |
| Feed sideways offset | 3.07 mm | none |
| Upper patch side | 42.97 mm | 41.51 mm |
| Upper patch corner cut | 7.80 mm | none |
| Air gap | 5.0 mm | 5.0 mm |
| Upper board | 1.524 mm PTFE, patch on the underside | same |

What the tuning found:

- **The two patches act as one wide resonator.** The stack has two resonances about 500 MHz apart at any practical gap. The design uses the lower one. Its bandwidth is about three times a single patch's.
- **The feed has to sit near the patch edge.** The stack's resistance at resonance is lower than a single patch's, so the 50 Ω point moves outward.
- **The feed pin's own inductance limits the match** on the cut-corner version. Moving the feed 3.07 mm sideways cancels most of it. Worst S11 is −12.7 dB, which passes with 2.7 dB to spare.
- **The fine mesh read 17 MHz higher than the tuning mesh**, so the final dimensions were scaled by 0.7 % and re-solved.

The 5.0 mm gap was chosen as a practical spacer height. Section 6 re-tunes the stacked cut corner for a 3.0 mm gap.

## 3. Board-size sweep, on the 100 mm metal face

The patch dimensions stay fixed. Only the board (both boards, for the stacked designs) changes from 50 to 100 mm square. The metal face behind it stays 100 mm.

![Size sweep on the face](results_hfss/size_sweep_face.png)

| Board side | Cut corner gain | Dual feed gain | Stacked cut corner gain | Stacked dual feed gain |
| --- | --- | --- | --- | --- |
| 50 mm | 7.05 dBic | 6.74 dBic | 8.43 dBic | 8.17 dBic |
| 60 mm | 7.08 dBic | 6.75 dBic | 8.49 dBic | 8.28 dBic |
| 70 mm | 7.05 dBic | 6.75 dBic | 8.44 dBic | 8.28 dBic |
| 80 mm | 7.00 dBic | 6.72 dBic | 8.44 dBic | 8.25 dBic |
| 90 mm | 7.03 dBic | 6.70 dBic | 8.41 dBic | 8.22 dBic |
| 100 mm | 7.00 dBic | 6.68 dBic | 8.39 dBic | 8.18 dBic |

Gain is the lowest RHCP gain in the channel. Dual-feed figures include 0.4 dB coupler loss.

| Board side | Cut corner AR | Dual feed AR | Stacked cut corner AR | Stacked dual feed AR |
| --- | --- | --- | --- | --- |
| 50 mm | 3.77 dB | 0.77 dB | 3.34 dB | 1.37 dB |
| 60 mm | 4.14 dB | 0.79 dB | 1.39 dB | 1.48 dB |
| 70 mm | 4.05 dB | 0.73 dB | 1.59 dB | 1.48 dB |
| 80 mm | 3.83 dB | 0.80 dB | 1.71 dB | 1.46 dB |
| 90 mm | 4.06 dB | 0.74 dB | 1.78 dB | 1.49 dB |
| 100 mm | 4.00 dB | 0.76 dB | 1.84 dB | 1.52 dB |

AR is the worst axial ratio in the channel.

What the sweep shows:

- **Gain falls slightly as the board grows:** about 0.05 to 0.1 dB from 60 to 100 mm for all four. More dielectric around the patch holds a little more energy near the surface.
- **Match and beamwidth do not move in any way that matters.** Worst S11 stays within 1.3 dB of the 60 mm value except for the stacked dual feed, which varies from −16.1 to −19.2 dB and always passes. Beamwidth changes by less than 1°.
- **The single patches' polarization does not care about board size.** The cut corner's worst axial ratio wanders between 3.77 and 4.14 dB with no trend. That scatter (about ±0.2 dB) is the mesh, not the board.
- **The stacked cut corner's polarization does care.** Above 60 mm its axial ratio rises slowly, from 1.39 to 1.84 dB, as its best-polarization frequency slides 5 MHz low. At 50 mm it rises to 3.34 dB because that frequency jumps 15 MHz high. The 43 mm upper patch has only 3.5 mm of board around it at 50 mm, so its edge fields lose dielectric and the patch resonates higher. A 50 mm version would need its patches made about 0.6 % larger. That re-tune was not done.
- **The stacked dual feed is not affected** at 50 mm, because its polarization comes from the coupler and not from the patch's exact frequency.

The reason board size matters so little here is that the 100 mm metal face is the ground plane in every case. The board size only changes how much dielectric surrounds the patch. Section 4 removes the metal face, so the ground plane shrinks with the board.

Full tables with S11, directivity, efficiency and beamwidth for every size are in [`results_hfss/sweep_tables.md`](results_hfss/sweep_tables.md).

## 4. Board-size sweep, no metal behind the board

Same sweep with the 100 mm metal face removed, so the board's own copper is the whole ground plane. The 100 mm row is the same model as the 100 mm row in section 3. No 60 or 80 mm bare boards were run.

![Size sweep, bare board](results_hfss/size_sweep_bare.png)

Lowest RHCP gain in the channel:

| Board side | Cut corner | Dual feed | Stacked cut corner | Stacked dual feed |
| --- | --- | --- | --- | --- |
| 50 mm | 5.78 dBic | 5.47 dBic | 6.57 dBic | 5.95 dBic |
| 70 mm | 6.55 dBic | 6.34 dBic | 7.82 dBic | 7.63 dBic |
| 90 mm | 6.90 dBic | 6.61 dBic | 8.19 dBic | 8.03 dBic |
| 100 mm | 7.00 dBic | 6.68 dBic | 8.39 dBic | 8.18 dBic |

Worst axial ratio in the channel:

| Board side | Cut corner | Dual feed | Stacked cut corner | Stacked dual feed |
| --- | --- | --- | --- | --- |
| 50 mm | 6.71 dB | 0.76 dB | 5.94 dB | 1.21 dB |
| 70 mm | 4.04 dB | 0.76 dB | 2.21 dB | 1.50 dB |
| 90 mm | 3.78 dB | 0.77 dB | 1.85 dB | 1.48 dB |
| 100 mm | 4.00 dB | 0.76 dB | 1.84 dB | 1.52 dB |

Worst S11 in the channel:

| Board side | Cut corner | Dual feed | Stacked cut corner | Stacked dual feed |
| --- | --- | --- | --- | --- |
| 50 mm | −15.2 dB | −9.6 dB | −13.8 dB | −7.7 dB |
| 70 mm | −14.4 dB | −14.0 dB | −12.1 dB | −14.5 dB |
| 90 mm | −15.2 dB | −13.9 dB | −12.1 dB | −15.8 dB |
| 100 mm | −15.6 dB | −13.1 dB | −12.3 dB | −16.4 dB |

Half-power beamwidth (narrower cut):

| Board side | Cut corner | Dual feed | Stacked cut corner | Stacked dual feed |
| --- | --- | --- | --- | --- |
| 50 mm | 91° | 90° | 76° | 78° |
| 70 mm | 82° | 82° | 74° | 74° |
| 90 mm | 75° | 75° | 69° | 69° |
| 100 mm | 73° | 73° | 66° | 67° |

What the sweep shows:

- **Gain rises with ground size.** From 50 to 100 mm it rises 1.2 dB on the single patches and 1.8 to 2.2 dB on the stacked ones. About two thirds of that comes between 50 and 70 mm.
- **The beam narrows as the ground grows**, from about 90° to 73° on the single patches and from about 77° to 66° on the stacked ones. Every case passes the 60° requirement.
- **Directivity is the cause.** It rises from 6.8 to 7.9 dBi on the single patches and from 7.5 to 8.8 dBi on the stacked ones. Efficiency stays between 87 and 98 %.
- **At 50 mm the designs are also detuned.** The dual feeds lose their match (−9.6 and −7.7 dB) and the cut corners lose their circular polarization (6.7 and 5.9 dB). These designs were tuned for the 100 mm face. A re-tune for a 50 mm bare board would recover match and polarization, but not the 1.1 to 1.3 dB of directivity.
- **From 70 mm up, nothing is detuned.** Match and axial ratio are within about 0.4 dB of the 100 mm values, apart from the mesh scatter on the single cut corner.
- **A 60 mm bare board was not run at this mesh.** By interpolation it would sit about 0.4 dB below the 70 mm gain figures.

In short: with the antenna on the satellite's metal face, the board can be any size from 60 to 100 mm with almost no change. Without metal behind it, a bigger board is worth up to about 2 dB.

## 5. Stress tests on the stacked cut corner

Each row changes one thing on the tuned stacked cut corner (60 mm board on the 100 mm face) and re-solves it.

| Case | Worst S11 | Worst axial ratio in channel | Best axial ratio at | RHCP gain in channel | All pass |
| --- | --- | --- | --- | --- | --- |
| Nominal | −12.7 dB | 1.39 dB | 2.425 GHz | 8.49 to 8.56 dBic | yes |
| Board Dk 2.52 (−1.2 %) | −12.6 dB | 2.70 dB | 2.435 GHz | 8.42 to 8.53 dBic | yes |
| Board Dk 2.58 (+1.2 %) | −13.0 dB | 2.20 dB | 2.415 GHz | 8.52 to 8.54 dBic | yes |
| Both patches 0.3 mm small | −12.8 dB | 3.62 dB | 2.445 GHz | 8.36 to 8.51 dBic | no |
| Both patches 0.3 mm large | −13.2 dB | 3.18 dB | 2.410 GHz | 8.48 to 8.53 dBic | no |
| Air gap 4.8 mm (−0.2 mm) | −12.8 dB | 1.41 dB | 2.425 GHz | 8.46 to 8.53 dBic | yes |
| Air gap 5.2 mm (+0.2 mm) | −12.5 dB | 1.56 dB | 2.425 GHz | 8.48 to 8.55 dBic | yes |
| Upper board 0.5 mm off in x and y | −12.6 dB | 1.40 dB | 2.425 GHz | 8.48 to 8.54 dBic | yes |
| Four nylon spacers in the gap | −12.4 dB | 1.29 dB | 2.425 GHz | 8.45 to 8.51 dBic | yes |
| Four steel screws and metal standoffs | −11.1 dB | 2.35 dB | 2.415 GHz | 8.28 to 8.31 dBic | yes |
| SMA connector modelled | −13.6 dB | 1.36 dB | 2.425 GHz | 8.48 to 8.55 dBic | yes |
| Solder mask around the lower patch | −12.6 dB | 1.73 dB | 2.420 GHz | 8.49 to 8.53 dBic | yes |
| Metal box behind, not a flat plate | −12.6 dB | 1.26 dB | 2.425 GHz | 8.21 to 8.29 dBic | yes |
| Lossless copper | −12.8 dB | 1.50 dB | 2.425 GHz | 8.52 to 8.59 dBic | yes |

The spacers and screws sit at the four board corners, 4 mm in from each edge and clear of the upper patch.

What the tests show:

- **The gap and the alignment of the upper board are not critical.** A 0.2 mm gap error or a 0.5 mm sideways error changes the axial ratio by less than 0.2 dB and the gain by less than 0.03 dB. Ordinary spacers and screw-hole tolerances are good enough.
- **Nylon spacers have no measurable effect** (0.1 dB in axial ratio, 0.04 dB in gain).
- **Steel screws with metal standoffs cost something but still pass:** axial ratio 2.35 dB instead of 1.39 dB, gain 0.2 dB lower, worst S11 −11.1 dB. Nylon hardware is the better choice. If steel is needed, the patches could be re-tuned with the screws in the model.
- **The connector, solder mask and lossless copper change little.** Solder mask moves the best-polarization frequency 5 MHz low, against 7.5 MHz on the single cut corner.
- **A metal box behind the board instead of a flat plate lowers gain by 0.27 dB** (8.21 to 8.29 dBic). The single cut corner lost a similar amount.
- **Gain and match hold in every case.** Gain stays above 8.21 dBic and worst S11 between −11.1 and −13.6 dB.
- **Polarization is the weak point, as on the single cut corner, but with three times the margin.** A ±1.2 % Dk error still passes (2.70 dB worst). A 0.3 mm error on both patches at once does not (3.18 to 3.62 dB), because it moves the best-polarization frequency by 15 to 20 MHz. JLC's etch tolerance is usually better than 0.3 mm, and ordering ±0.3 mm size variants covers the rest.
- For comparison, the single cut corner's axial ratio is 4.14 dB at nominal and reaches 8.4 to 8.7 dB with the same 1.2 % Dk error (see [`HFSS_RESULTS.md`](HFSS_RESULTS.md)).

## 6. Shorter stack: 3 mm gap

With a 5.0 mm gap the stacked antenna is about 8.0 mm tall (1.5 + 5.0 + 1.5 mm). The CubeSat Design Specification limits parts on a side face to 6.5 mm beyond the rails, so 8.0 mm may not fit. The deployer's own limit has not been checked. This section re-tunes the stacked cut corner for a 3.0 mm gap, about 6.0 mm tall.

![Stacked cut corner, 3 mm gap](../docs/stacked_cut_corner_3mm_results.png)

| Dimension | 3 mm gap | 5 mm gap |
| --- | --- | --- |
| Lower patch side | 35.63 mm | 36.26 mm |
| Lower patch corner cut | 5.40 mm | 6.56 mm |
| Feed distance from centre | 15.68 mm | 15.96 mm |
| Feed sideways offset | 3.02 mm | 3.07 mm |
| Upper patch side | 42.23 mm | 42.97 mm |
| Upper patch corner cut | 6.42 mm | 7.80 mm |
| Total height | 6.0 mm | 8.0 mm |

| | 3 mm gap | 5 mm gap | Single cut corner | Requirement |
| --- | --- | --- | --- | --- |
| Worst S11 in the channel | −26.3 dB | −12.7 dB | −15.5 dB | −10 dB or lower |
| −10 dB match window | 146 MHz | 206 MHz | 66 MHz | covers the channel |
| Worst axial ratio in the channel | 1.87 dB | 1.39 dB | 4.14 dB | 3 dB or lower |
| 3 dB axial-ratio window | 35 MHz | 49 MHz | 16 MHz | 20 MHz or more |
| RHCP gain in the channel | 8.45 to 8.51 dBic | 8.49 to 8.56 dBic | 7.08 to 7.24 dBic | 6.5 dBic or more |
| Half-power beamwidth | 68° | 66° | 72° | 60° or wider |

The same stress tests on both gaps. Each cell is the worst axial ratio in the channel, then the lowest RHCP gain.

| Case | 3 mm gap | 5 mm gap |
| --- | --- | --- |
| Nominal | 1.87 dB, 8.45 dBic | 1.39 dB, 8.49 dBic |
| Board Dk 2.52 (−1.2 %) | 3.56 dB, 8.36 dBic | 2.70 dB, 8.42 dBic |
| Board Dk 2.58 (+1.2 %) | 3.33 dB, 8.38 dBic | 2.20 dB, 8.52 dBic |
| Both patches 0.3 mm small | 4.95 dB, 8.17 dBic | 3.62 dB, 8.36 dBic |
| Both patches 0.3 mm large | 4.72 dB, 8.24 dBic | 3.18 dB, 8.48 dBic |
| Four nylon spacers | 1.79 dB, 8.46 dBic | 1.29 dB, 8.45 dBic |

Worst S11 stays between −21.8 and −27.6 dB in every 3 mm case.

What this shows:

- **The 3 mm stack keeps the gain.** It is 0.04 dB below the 5 mm stack and 1.3 dB above the single cut corner.
- **Its match is better**, −26.3 dB against −12.7 dB. At 2.425 GHz the feed reads 45.5 + 0.3j Ω, against 34.2 + 11.6j Ω with the 5 mm gap.
- **Its polarization window is about 30 % narrower** (35 against 49 MHz), and the frequency shifts caused by Dk and size errors are the same. So the same errors use up more of the window: a 1.2 % Dk error gives 3.3 to 3.6 dB, just over the 3 dB limit, where the 5 mm stack stays under it.
- **The gain requirement holds in every case.** The RHCP gain figures already include the polarization loss, and the lowest is 8.17 dBic. An axial ratio of 3.6 dB costs 0.18 dB against a perfectly circular ground antenna, and 5.0 dB costs 0.33 dB.
- **It is still much less sensitive than the single cut corner**, which reaches 8.4 to 8.7 dB with the same Dk error.
- A 2 mm gap (5.0 mm tall) was looked at once without re-tuning. Gain was 7.8 to 7.9 dBic. It was not taken further.

Not done for the 3 mm version: the gap, misalignment, steel-screw, connector, solder-mask and box tests, the board-size sweep, and a 3 mm version of the stacked dual feed.

## 7. Hand calculations

[`HAND_CALCS.md`](HAND_CALCS.md) has every formula, input and result. [`hand_calcs.py`](hand_calcs.py) reproduces the numbers.

| Quantity | Hand calculation | HFSS | Difference |
| --- | --- | --- | --- |
| Single dual-feed patch side | 38.25 mm | 37.28 mm | +2.6 % |
| Single cut-corner patch side | 38.43 mm | 37.52 mm | +2.4 % |
| Single cut-corner axial-ratio window | 15.8 MHz | 16.0 MHz | −1 % |
| Single cut-corner match window | 64.1 MHz | 65.8 MHz | −3 % |
| Single dual-feed match window | 32.1 MHz | 32.4 MHz | −1 % |
| Stacked cut-corner axial-ratio window | 47.3 MHz | 49.4 MHz | −4 % |
| Stacked cut-corner match window | 192 MHz | 206 MHz | −7 % |
| Stacked cut size, as a fraction of the patch side | 0.174 | 0.181 | −4 % |
| Stacked dual-feed lower patch side | 35.19 mm | 35.04 mm | +0.4 % |
| Stacked dual-feed upper patch side | 41.72 mm | 41.51 mm | +0.5 % |
| Stacked dual-feed feed position | 13.45 mm | 13.35 mm | +0.8 % |
| Stacked dual-feed match window | 96 MHz | 106 MHz | −10 % |
| Stacked dual-feed gain at the patch | 8.77 dBic | 8.74 dBic | +0.03 dB |
| Stacked dual-feed axial ratio, typical coupler | 0.68 dB | 1.48 dB | −0.8 dB |
| 3 mm stack: match window | 142 MHz | 146 MHz | −3 % |
| 3 mm stack: cut size, as a fraction of the patch side | 0.149 | 0.152 | −1 % |

The stacked hand calculations take the coupling between the two patches (about 19 to 20 %) from a first HFSS mapping run. They are a check on the tuning, not an independent prediction of it.

The one real disagreement is the last row. The hand formula assumes the two feeds are isolated from each other. On the stacked patch they are coupled at −27 dB (against −45 dB on the single patch), and that adds about 0.8 dB of axial ratio.

## 8. What this does not show

- **Nothing has been built or measured.** HFSS agreed with openEMS within 0.4 % in frequency on the single patches. Neither has been checked against a real board from this project.
- **The stacked designs were solved at one mesh size** (about 40,000 elements, near the Student licence's 64,000 limit). Run-to-run scatter is about ±0.2 dB in axial ratio and ±0.03 dB in gain.
- **The spacers and screws that hold the upper board are not designed.** Section 5 tests their electrical effect only.
- **The coupler for the dual-feed designs is not designed.** Its error and loss are assumed typical values.
- **The allowed antenna height on the satellite is not confirmed.** Only two gaps were tuned (5.0 and 3.0 mm). A gap between them, or a thinner upper board, might give a better trade and was not tried.
- **2.425 GHz is still an assumed carrier.**
- **The rev-1 KiCad boards and Gerbers are unchanged.** No air-gap stacked board has been drawn. (Prototype boards for the bonded 3 mm design are in `kicad/prototype_thick/`.)

## How to reproduce

```
python sim/hfss_batch.py --only SZ  --mesh 40000   # board sizes on the 100 mm face
python sim/hfss_batch.py --only SZB --mesh 40000   # board sizes with no metal behind
python sim/hfss_batch.py --only TS  --mesh 40000   # stacked cut corner: nominal, Dk, patch size
python sim/hfss_batch.py --only TSK --mesh 40000   # stacked cut corner: gap, misalignment, spacers
python sim/hfss_batch.py --only TSD --mesh 40000   # stacked dual feed
python sim/sweep_report.py                          # plots and tables
python sim/hand_calcs.py                            # hand calculations
```
