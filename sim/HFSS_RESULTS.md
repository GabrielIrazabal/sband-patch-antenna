# HFSS cross-check results

Run overnight on 14 November 2026 with Ansys Electronics Desktop Student 2025 R2 and PyAEDT 1.9.0, following [`../HFSS_TASK.md`](../HFSS_TASK.md). 41 HFSS runs; raw outputs are in [`results_hfss/`](results_hfss), one folder per run, named like the openEMS folders.

## Summary

**HFSS agrees with openEMS. The design is confirmed within the task's limits (1 % in frequency, 0.3 dB in gain).**

For the best option (board B, PTFE, tuned for a 100 mm face), on a converged HFSS mesh:

| Quantity | HFSS | openEMS | Difference |
| --- | --- | --- | --- |
| Polarization | RHCP (32 dB above LHCP at 2.425 GHz) | RHCP | same |
| Axial ratio minimum | 0.43 dB at 2.4250 GHz | 0.18 dB at 2.4250 GHz | same frequency |
| Best match | −31.8 dB at 2.4455 GHz | −33 dB at 2.4505 GHz | −5 MHz (−0.2 %) |
| Worst S11 in the channel | −15.5 dB | −12.8 dB | HFSS 2.7 dB better |
| −10 dB bandwidth | 65.8 MHz | 63.5 MHz | +2.3 MHz |
| Worst axial ratio in the channel | 4.1 dB | 3.9 dB | +0.2 dB |
| 3 dB axial ratio bandwidth | 16.0 MHz | 12.5 MHz | +3.5 MHz |
| RHCP gain in the channel | 7.08 to 7.24 dBic | 6.80 to 7.05 dBic | HFSS 0.2 to 0.3 dB higher |
| Directivity / efficiency | 7.97 dBi / 87 % | 7.81 dBi / 88 % | +0.16 dB / −1 point |
| Half-power beamwidth | 72° / 73° | 74° | −1° to −2° |

What HFSS changes or adds:

- **Across all boards HFSS reads 0.1 to 0.4 % lower in frequency than openEMS** (3 to 10 MHz), and 0.1 to 0.3 dB higher in gain. Both are inside the agreement limits.
- **The axial ratio still misses 3 dB at the channel edges** on every cut-corner board (3.8 to 4.8 dB in HFSS, 3.4 to 4.3 dB in openEMS). This is the same conclusion as before, slightly worse.
- **Board B is more sensitive to the material than openEMS suggested.** A ±1 % error in Dk gives a worst in-channel axial ratio of 8.4 to 8.7 dB in HFSS, against 6.6 to 6.8 dB in openEMS.
- **Board A's match margin is thinner in HFSS.** Because its resonance sits 4 to 7 MHz lower and its bandwidth is narrow, the worst S11 in the channel is −8.7 dB (RO4350B on the 100 mm face) to −11.5 dB, against −10.7 to −14.3 dB in openEMS. The RO4350B board on the face does not meet −10 dB in HFSS.
- **Solder mask is the largest of the left-out effects:** about −6 to −8 MHz, which pushes the worst in-channel axial ratio from 4.1 to 6.6 dB. The SMA shifts things by −2.5 to −4 MHz and changes the gain by less than 0.05 dB. A 100 mm metal box in place of the flat sheet costs about 0.3 dB of gain and moves nothing else.
- **Gain requirement:** the best option stays above 6.5 dBic in every HFSS run at nominal dimensions, including with the box (6.79 to 6.97 dBic). It drops below 6.5 dBic at the channel edge only when the patch is 0.3 mm off or Dk is 1 % low.

What failed, was skipped or was done differently:

- **The mesh setting in the task (ΔS 0.01) was not fine enough for the cut-corner boards.** It stopped at 13,000 to 30,000 tetrahedra and put the axial-ratio minimum 2.5 to 12.5 MHz too low. See [Mesh convergence](#mesh-convergence). All board B runs were therefore repeated with the mesh forced to about 40,000 tetrahedra (`--target-tets 40000`, folders ending `_mesh40k`). The tables below use those. The ΔS 0.01 runs are kept and listed in the full table.
- **A ΔS 0.002 run failed three times:** it reached 70,307 tetrahedra and the Student edition stops at 64,000. The 40,000-tetrahedra run replaces it.
- **Board A on RO4350B, bare, and the Test 5 thick boards were run at ΔS 0.01 only.** They are single-mode patches, which are much less mesh-sensitive, and their meshes already reached 20,000 to 51,000 tetrahedra.
- **AEDT hung twice at the start of a solve and failed to launch once.** Each run passed when repeated. The batch runner now has a watchdog for this.
- **One project per design** in [`hfss_projects/`](hfss_projects) instead of a single `sim/patch.aedt`, so that one bad run cannot damage the others. The solver caches are not in the repo.
- **Nothing was changed** in the KiCad boards, the Gerbers or `kicad/generate_boards.py`.

Which tool to trust, and how sure:

- **Frequency: neither clearly.** They differ by 0.2 to 0.3 %, which is less than either tool's expected accuracy (about 1 %) and less than the uncertainty in the PTFE's Dk. HFSS models the real 0.5 mm via; openEMS uses a thin wire. I would use the HFSS numbers for the match and treat the two as equally good for the axial-ratio frequency. Confidence: moderate.
- **Gain: take the middle, ±0.2 dB.** HFSS is 0.15 to 0.3 dB higher. Its air box ends a quarter wavelength from the metal, which is the usual minimum and can bias gain by 0.1 to 0.2 dB; openEMS has more space (70 mm) and an absorbing layer. Confidence: moderate.
- **Note on real boards.** The openEMS validation suggested real boards land 10 to 20 MHz above openEMS. HFSS sits slightly below openEMS, and solder mask and the SMA push it lower again by up to about 10 MHz. These point in opposite directions, so the nominal board and the size variants are all still worth ordering. This is not settled by simulation; a VNA measurement will settle it.

## Mesh convergence

Best option, same model, more adaptive passes:

| Mesh (tetrahedra) | Setting | Best match (GHz) | Axial ratio minimum | Worst axial ratio in channel | RHCP gain in channel (dBic) |
| --- | --- | --- | --- | --- | --- |
| 15,800 | ΔS 0.01 (the task's setting) | 2.4420 | 0.75 dB at 2.4175 GHz | 6.2 dB | 6.87 to 7.18 |
| 22,796 | ΔS 0.005 (`_fine`) | 2.4435 | 0.49 dB at 2.4200 GHz | 5.1 dB | 7.02 to 7.25 |
| 40,404 | 18 passes (`_mesh40k`) | 2.4455 | 0.43 dB at 2.4250 GHz | 4.1 dB | 7.08 to 7.24 |
| 70,307 | ΔS 0.002 | not solved: over the Student limit | | | |
| openEMS | | 2.4505 | 0.18 dB at 2.4250 GHz | 3.9 dB | 6.80 to 7.05 |

- The result is still moving by about 2 MHz per step at 40,000 tetrahedra, so the HFSS frequencies carry roughly ±3 MHz of mesh uncertainty. The far-field sweep is in 2.5 MHz steps, so axial-ratio frequencies are quantized to that.
- The openEMS suggestion for the finer mesh was "the same within about 2 MHz". HFSS at ΔS 0.005 moved 1.5 MHz in match and 2.5 MHz in axial ratio, but had not finished converging.

## Test 0: script check

| Run | Quantity | HFSS | openEMS |
| --- | --- | --- | --- |
| Plain patch, RO4350B, 31.40 mm | Resonance (best match) | 2.4170 GHz | 2.4245 GHz |
| | −10 dB bandwidth | 38.6 MHz | 36.5 MHz |
| | Gain at 2.425 GHz | 5.89 dBi | 5.82 dBi |
| | Directivity / efficiency | 6.81 dBi / 84 % | 6.73 dBi / 82 % |
| Board A, RO4350B | Hand with J2 lagging by 90° | **RHCP**, 36 dB above LHCP | RHCP |
| | Port isolation at 2.425 GHz | −37.9 dB | −39.2 dB |
| | Axial ratio in the channel (ideal hybrid) | 0.2 to 0.3 dB | 0.2 to 0.3 dB (both ports solved) |

Both checks pass. The coordinates are not mirrored.

## Test 1: the best option

See the summary table. Plot: [`results_hfss/B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_mesh40k/results.png`](results_hfss/B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_mesh40k/results.png).

## Test 2: stress the best option

All at about 40,000 tetrahedra. "Shift" is relative to the Test 1 run.

| Change | Best match (GHz) | Axial ratio minimum | Worst S11 in channel | Worst axial ratio in channel | RHCP gain in channel (dBic) | What openEMS suggested |
| --- | --- | --- | --- | --- | --- | --- |
| None (Test 1) | 2.4455 | 0.43 dB at 2.4250 | −15.5 dB | 4.1 dB | 7.08 to 7.24 | |
| Dk 1 % low (2.52) | 2.4575 (+12 MHz) | 0.64 dB at 2.4375 (+12.5 MHz) | −10.0 dB | 8.4 dB | 6.09 to 7.25 | ±11 MHz; worst axial ratio 6.6 to 6.8 dB |
| Dk 1 % high (2.58) | 2.4335 (−12 MHz) | 0.59 dB at 2.4100 (−15 MHz) | −14.8 dB | 8.7 dB | 6.53 to 7.14 | |
| Patch 0.3 mm smaller (37.22) | 2.4630 (+17.5 MHz) | 0.70 dB at 2.4425 (+17.5 MHz) | −8.0 dB | 10.4 dB | 5.48 to 7.09 | −62 MHz per +1 mm |
| Patch 0.3 mm larger (37.82) | 2.4280 (−17.5 MHz) | 0.60 dB at 2.4050 (−20 MHz) | −15.9 dB | 10.6 dB | 6.20 to 7.01 | |
| Bare board (37.56 mm, cut 3.80, no face) | 2.4480 | 0.66 dB at 2.4225 | −13.4 dB | 4.1 dB | 6.33 to 6.45 | 6.12 to 6.30 dBic; 0.27 dB at centre, 3.4 dB at edges |
| Lossless copper | 2.4470 | 0.45 dB at 2.4250 | −15.6 dB | 4.2 dB | 7.22 to 7.46 | |
| Dk −0.3 % (2.542) | 2.4495 (+4 MHz) | 0.40 dB at 2.4275 (+2.5 MHz) | −14.4 dB | 5.0 dB | 6.85 to 7.24 | not simulated |
| Dk +0.3 % (2.558) | 2.4425 (−3 MHz) | 0.22 dB at 2.4200 (−5 MHz) | −15.3 dB | 5.3 dB | 6.98 to 7.23 | not simulated |

- **Patch size:** −58 MHz per +1 mm from the match, −62 MHz per +1 mm from the axial ratio. openEMS: −62.
- **Copper loss:** about 0.2 dB of gain (efficiency 87 % with copper, 92 % without).
- **Temperature (assumed ±0.3 % in Dk):** the design stays above 6.5 dBic and the axial ratio at the channel edge rises from 4.1 to about 5 dB (0.3 dB of polarization loss).
- **The bare board's axial-ratio minimum is 2.5 MHz low and 0.66 dB instead of 0.27 dB.** That is within mesh uncertainty.

## Test 3: what openEMS left out

Added to the best option one at a time, at about 40,000 tetrahedra.

| Addition | Best match | Worst S11 in channel | Axial ratio minimum | Worst axial ratio in channel | RHCP gain in channel (dBic) | Change |
| --- | --- | --- | --- | --- | --- | --- |
| None (Test 1) | 2.4455 GHz | −15.5 dB | 0.43 dB at 2.4250 GHz | 4.1 dB | 7.08 to 7.24 | |
| SMA: 5 mm of 50 Ω coax and a wave port | 2.4415 GHz | −18.2 dB | 0.32 dB at 2.4225 GHz | 4.3 dB | 7.08 to 7.27 | −4 MHz match, −2.5 MHz axial ratio, gain unchanged |
| Solder mask around the patch | 2.4395 GHz | −14.8 dB | 0.52 dB at 2.4175 GHz | 6.6 dB | 6.80 to 7.16 | −6 MHz match, −7.5 MHz axial ratio, −0.3 dB gain at the upper channel edge |
| 100 mm metal cube behind the board | 2.4455 GHz | −15.6 dB | 0.48 dB at 2.4250 GHz | 4.1 dB | 6.79 to 6.97 | no frequency change, −0.3 dB gain, beam 2° to 3° wider |

How each was modeled:

- **SMA:** a coax with the SMA's 1.27 mm pin in PTFE, outer radius set for 50 Ω, 5 mm long, below the ground, with the wave port de-embedded to the ground plane. The connector's body, flange and solder joint are not modeled.
- **Solder mask:** 25 µm, εr 3.8, loss tangent 0.025, on the top of the board everywhere except over the patch. These are typical values, not JLC's. If JLC can leave the mask off the whole top side, this shift disappears.
- **Box:** a solid 100 × 100 × 100 mm metal block with its top face as the ground. A real 1U body with solar panels will differ.

## Test 4: the other four boards

Board B rows and the board A rows on the face and on PTFE are at about 40,000 tetrahedra. Board A on bare RO4350B is at ΔS 0.01 (36,443 tetrahedra). Board A assumes an ideal hybrid in both tools and its gain excludes the hybrid's 0.3 to 0.5 dB loss.

| Board | Mounting | Quantity | HFSS | openEMS |
| --- | --- | --- | --- | --- |
| A, RO4350B (31.40 / 5.80) | bare | Best match / worst S11 / bandwidth | 2.4170 GHz / −10.5 dB / 38.5 MHz | 2.4245 GHz / −13.5 dB / 35.5 MHz |
| | | RHCP gain in channel | 5.65 to 5.94 dBic | 5.64 to 5.75 dBic |
| | | Isolation | −37.9 dB | −39.2 dB |
| | 100 mm face | Best match / worst S11 / bandwidth | 2.4190 GHz / **−8.7 dB** / 21.4 MHz | 2.4240 GHz / −10.7 dB / 26.0 MHz |
| | | RHCP gain in channel | 5.89 to 6.18 dBic | 5.90 to 6.04 dBic |
| B, RO4350B (31.54 / 5.90 / 3.13) | bare | Best match / worst S11 / bandwidth | 2.4460 GHz / −14.5 dB / 73.1 MHz | 2.4525 GHz / −12.2 dB / 69 MHz |
| | | Axial ratio minimum / worst in channel | 0.68 dB at 2.4225 GHz / 4.2 dB | 0.21 dB at 2.4250 GHz / 3.5 dB |
| | | RHCP gain in channel | 5.71 to 5.85 dBic | 5.51 to 5.68 dBic |
| | 100 mm face | Best match / worst S11 / bandwidth | 2.4465 GHz / −14.2 dB / 69.7 MHz | 2.4520 GHz / −12.1 dB / 68 MHz |
| | | Axial ratio minimum / worst in channel | 1.59 dB at 2.4225 GHz / 4.8 dB | 1.47 dB at 2.4250 GHz / 4.3 dB |
| | | RHCP gain in channel | 6.09 to 6.28 dBic | 5.96 to 6.11 dBic |
| A, PTFE (37.38 / 6.90) | bare | Best match / worst S11 / bandwidth | 2.4185 GHz / −11.5 dB / 40.7 MHz | 2.4250 GHz / −14.3 dB / 37.5 MHz |
| | | RHCP gain in channel | 6.37 to 6.61 dBic | 6.31 to 6.43 dBic |
| | | Isolation | −36.9 dB | −38.8 dB |
| | 100 mm face | Best match / worst S11 / bandwidth | 2.4215 GHz / −10.3 dB / 28.7 MHz | 2.4260 GHz / −11.8 dB / 31.0 MHz |
| | | RHCP gain in channel | 6.98 to 7.17 dBic | 6.78 to 6.93 dBic |
| B, PTFE (37.56 / 7.00 / 3.80) | bare | Best match / worst S11 / bandwidth | 2.4480 GHz / −13.4 dB / 75.5 MHz | 2.4550 GHz / −11.6 dB / 71 MHz |
| | | Axial ratio minimum / worst in channel | 0.66 dB at 2.4225 GHz / 4.1 dB | 0.27 dB at 2.4250 GHz / 3.4 dB |
| | | RHCP gain in channel | 6.33 to 6.45 dBic | 6.12 to 6.30 dBic |
| | 100 mm face | Best match / worst S11 / bandwidth | 2.4510 GHz / −13.4 dB / 72.9 MHz | 2.4560 GHz / −11.5 dB / 71 MHz |
| | | Axial ratio minimum / worst in channel | 1.14 dB at 2.4250 GHz / 3.8 dB | 1.29 dB at 2.4275 GHz / 4.1 dB |
| | | RHCP gain in channel | 7.04 to 7.16 dBic | 6.74 to 6.94 dBic |

- HFSS confirms the gain ranking: RO4350B does not reach 6.5 dBic in any run (5.7 to 6.3 dBic); PTFE reaches it on the 100 mm face (7.0 to 7.2 dBic) and is just under it on the bare board (6.3 to 6.6 dBic).
- HFSS confirms that the 100 mm face detunes board B's polarization (best axial ratio 1.1 to 1.6 dB with the bare-board cut) and that the re-tuned `face100` board fixes it (0.43 dB).
- Board A's worst S11 is the weak point described in the summary. Moving its resonance up by about 5 MHz (a patch roughly 0.08 mm smaller) would centre it in HFSS, but that is inside the gap between the two tools, so no change is recommended before a measurement.

## Test 5: thicker board (3.05 mm)

Plain patches at ΔS 0.01 (19,672 to 50,623 tetrahedra).

| Material | Mounting | Best match (GHz), HFSS / openEMS | −10 dB bandwidth (MHz), HFSS / openEMS | Gain at 2.425 GHz (dBi), HFSS / openEMS | Efficiency, HFSS / openEMS |
| --- | --- | --- | --- | --- | --- |
| RO4350B (30.66 / 5.70) | bare | 2.4070 / 2.4165 | 74.5 / 61.0 | 6.38 / 6.23 | 93 % / 91 % |
| | 100 mm face | 2.4110 / 2.4145 | 54.2 / 55.0 | 6.88 / 6.76 | 90 % / 89 % |
| PTFE (36.44 / 6.70) | bare | 2.4110 / 2.4215 | 74.0 / 59.5 | 6.93 / 6.71 | 96 % / 94 % |
| | 100 mm face | 2.4215 / 2.4235 | 63.1 / 57.5 | 7.72 / 7.52 | 95 % / 94 % |

- Gain agrees within 0.12 to 0.22 dB. HFSS confirms that thicker PTFE on the face is the only configuration comfortably above 7 dBi.
- The two bare-board runs differ most in frequency (−0.4 %) and bandwidth (+13 to +14 MHz). They also have the coarsest meshes (19,672 and 22,783 tetrahedra), so part of that is probably mesh. I am less sure of these two rows than of the rest.

## Dual feed re-tuned for the 100 mm face, against the best option

Added after the overnight run. The PTFE dual-feed board in the repo (37.38 / 6.90 mm) was tuned on the bare board, so on the 100 mm face its match only just passed (−10.3 dB). It was re-tuned in HFSS for the face and then given the same stress tests as the best option. **This is a simulation-only design: the KiCad board, the Gerbers and `generate_boards.py` were not changed.**

Tuning (PTFE, 100 mm face, about 40,000 tetrahedra):

| Patch / feed (mm) | Best match | Worst S11 in channel | Input impedance at best match | RHCP gain in channel (dBic) |
| --- | --- | --- | --- | --- |
| 37.38 / 6.90 (the repo's board) | −13.2 dB at 2.4215 GHz | −10.3 dB | not recorded | 6.98 to 7.17 |
| 37.34 / 6.40 | −16.3 dB at 2.4230 GHz | −11.7 dB | 63 − 12j Ω | 7.07 to 7.25 |
| 37.31 / 5.80 | −23.8 dB at 2.4230 GHz | −12.3 dB | 55 − 4j Ω | 7.13 to 7.36 |
| **37.28 / 5.80 (tuned)** | **−23.8 dB at 2.4250 GHz** | **−13.5 dB** | 56 − 4j Ω | **7.16 to 7.36** |

- The feed was stopped at 5.80 mm. Below that, `generate_boards.py` moves both SMAs out and adds traces the model does not have. A perfect 50 Ω match would need about 5.5 mm and would gain less than 0.1 dB.
- Mesh check: at 58,212 tetrahedra the best match moves to 2.4260 GHz and the worst S11 to −12.8 dB. The dual-feed runs' ΔS (0.010 to 0.023) is higher than the cut-corner runs', so treat their frequencies as ±2 MHz.
- −13.5 dB at the channel edges is close to the limit for this board thickness: the match bandwidth is 32 MHz against a 20 MHz channel.

Side by side at nominal dimensions. Board A's gain is shown before and after the hybrid's 0.3 to 0.5 dB loss:

| Quantity | Dual feed, tuned (A, 37.28 / 5.80) | Cut corner (B, 37.52 / 7.00 / 3.50) | Requirement |
| --- | --- | --- | --- |
| Best match | −23.8 dB at 2.4250 GHz | −31.8 dB at 2.4455 GHz | |
| Worst S11 in channel | −13.5 dB | −15.5 dB | ≤ −10 dB |
| −10 dB bandwidth | 32.4 MHz | 65.8 MHz | |
| Worst axial ratio in channel | 0.11 dB (ideal hybrid); 0.8 dB (hybrid off by 0.5 dB, 3°); 1.4 dB (1 dB, 5°); 1.9 dB (1 dB, 10°) | 4.14 dB | ≤ 3 dB |
| RHCP gain in channel | 7.16 to 7.36 dBic at the patch; 6.7 to 7.1 dBic after the hybrid | 7.08 to 7.24 dBic | ≥ 6.5 dBic |
| Radiation efficiency | 87 % | 87 % | |
| Half-power beamwidth | 73° / 73° | 72° / 73° | ≥ 60° |
| Port isolation | −46 dB | one port | |

Plot: [`results_hfss/compare_A_vs_B.png`](results_hfss/compare_A_vs_B.png).

The same stress tests. Each cell is worst S11 / worst axial ratio / lowest RHCP gain in the channel. Board A's axial ratio is for a hybrid off by 0.5 dB and 3°, and its gain is at the patch (subtract 0.3 to 0.5 dB for the hybrid):

| Case | Dual feed, tuned | Cut corner |
| --- | --- | --- |
| Nominal | −13.5 dB / 0.8 dB / 7.16 dBic | −15.5 dB / 4.1 dB / 7.08 dBic |
| Dk 1 % low (2.52) | −7.4 dB / 0.8 dB / 6.48 dBic | −10.0 dB / 8.4 dB / 6.09 dBic |
| Dk 1 % high (2.58) | −7.3 dB / 0.8 dB / 6.47 dBic | −14.8 dB / 8.7 dB / 6.53 dBic |
| Patch 0.3 mm small | −5.8 dB / 0.8 dB / 5.98 dBic | −8.0 dB / 10.4 dB / 5.48 dBic |
| Patch 0.3 mm large | −5.9 dB / 0.7 dB / 6.10 dBic | −16.0 dB / 10.6 dB / 6.20 dBic |
| With the SMA | −11.1 dB / 0.7 dB / 6.99 dBic (match 4 MHz lower) | −18.2 dB / 4.3 dB / 7.08 dBic |
| With solder mask | −9.2 dB / 0.7 dB / 6.78 dBic (match 8 MHz lower) | −14.8 dB / 6.6 dB / 6.80 dBic |
| On a 100 mm metal box | −13.5 dB / 0.7 dB / 6.90 dBic | −15.6 dB / 4.1 dB / 6.79 dBic |
| Lossless copper | −12.4 dB / 0.8 dB / 7.33 dBic | −15.6 dB / 4.2 dB / 7.22 dBic |

What this shows:

- **The dual feed keeps its circular polarization in every case** (under 1 dB with a typical hybrid, under 2 dB with a poor one). The cut corner's axial ratio goes to 8 to 11 dB with a 1 % Dk error or a 0.3 mm size error.
- **The dual feed is not more tolerant in signal strength.** The same errors detune its narrower match, so its gain at the patch drops to 6.0 to 6.5 dBic, and to about 5.5 to 6.2 dBic after the hybrid. The cut corner drops to 5.5 to 6.5 dBic. Both fall to about 6.5 dBic or below at a channel edge when the frequency is off by about 17 MHz.
- **At nominal dimensions the two deliver about the same RHCP gain** once the hybrid's loss is counted (6.7 to 7.1 against 7.08 to 7.24 dBic). The cut corner is ahead by 0.1 to 0.4 dB.
- **With a hybrid, the radio sees a good match even when the patch is detuned,** because the two equal reflections go to the hybrid's load, not back to the radio. The power is still lost, which is what the gain figures show.
- Not modelled: the hybrid itself, the two cables (1 mm of length mismatch in PTFE coax is about 4° of phase), and the board that carries the hybrid.

Recommendation, moderately sure: choose the dual feed if the 3 dB axial-ratio requirement is firm, or if the ground station cannot tolerate polarization that varies from board to board. Choose the cut corner if signal strength is what matters and one cable is worth more than clean polarization. Either way, order size variants and measure, because both need the frequency to land within about ±10 MHz.

Runs: `results_hfss/A_L37.28_f5.80_*` and `A_L3?.?8_f5.80_*` (group `TA` in `hfss_batch.py`, run with `--mesh 40000`), plus the tuning steps `A_L37.34_f6.40_*` and `A_L37.31_f5.80_*`. They are not in the table under "Every run".

## How to reproduce

```
pip install -r sim/requirements.txt
python sim/hfss_batch.py --project-dir C:\hfss_work               # the task's list at ΔS 0.01
python sim/hfss_batch.py --project-dir C:\hfss_work --mesh 40000  # the same list at about 40,000 tetrahedra
python sim/hfss_compare.py                                        # the table below
```

- Keep `--project-dir` outside OneDrive or any other synced folder; the solver cache is large and changes constantly.
- `hfss_patch.py` changes from the draft: PyAEDT 1.9 argument names, `summary.json` in the openEMS format, `--sma`, `--mask`, `--box`, `--target-tets`, `--passes`, `--pad`, non-graphical by default, and it prints AEDT's own error messages.
- The S-parameter sweep uses 901 points (0.5 MHz) instead of 451, to match the openEMS bandwidth resolution.

## Every run

`_mesh40k` rows are the converged-mesh repeats. Rows without it use the task's ΔS 0.01 unless the name says otherwise (`_fine` is ΔS 0.005; `_vfine` is the same solve as the best option's `_mesh40k`). openEMS rows appear where a folder of the same name exists in `results_openems/`. For the plain patches, gain is the total (linear) gain.

| Run | Tool | Best match (GHz) | Worst S11 in channel (dB) | -10 dB BW (MHz) | AR min (dB) at (GHz) | Worst AR in channel (dB) | 3 dB AR BW (MHz) | RHCP gain in channel (dBic) | Total gain at f0 (dBi) | Directivity (dBi) | Efficiency | HPBW phi0/phi90 (deg) | Hand | Mesh (tets / passes) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `A_L31.40_f5.80_er3.66_h1.52` | HFSS | 2.4170 | -10.5 | 38.5 | 0.23 @ 2.4000 | 0.30 | – | 5.65 to 5.94 | 5.89 | 6.82 | 0.84 | 90/90 | RHCP | 36443 / 17 |
|  | openEMS | 2.4245 | -13.5 | 35.5 | ideal | ideal | ideal | 5.64 to 5.75 | 5.75 | – | – | 88/88 | RHCP |  |
| `A_L31.40_f5.80_er3.66_h1.52_Gm100` | HFSS | 2.4200 | -8.9 | 21.6 | 0.21 @ 2.4100 | 0.27 | – | 5.92 to 6.19 | 6.16 | 7.56 | 0.78 | 75/75 | RHCP | 54940 / 20 |
|  | openEMS | 2.4240 | -10.7 | 26.0 | ideal | ideal | ideal | 5.90 to 6.04 | 6.04 | – | – | 74/76 | RHCP |  |
| `A_L31.40_f5.80_er3.66_h1.52_Gm100_mesh40k` | HFSS | 2.4190 | -8.7 | 21.4 | 0.19 @ 2.4075 | 0.27 | – | 5.89 to 6.18 | 6.15 | 7.56 | 0.79 | 75/75 | RHCP | 42218 / 18 |
|  | openEMS | 2.4240 | -10.7 | 26.0 | ideal | ideal | ideal | 5.90 to 6.04 | 6.04 | – | – | 74/76 | RHCP |  |
| `A_L37.38_f6.90_er2.55_h1.52` | HFSS | 2.4190 | -11.8 | 40.7 | 0.16 @ 2.4100 | 0.22 | – | 6.39 to 6.61 | 6.59 | 7.15 | 0.90 | 86/86 | RHCP | 50336 / 20 |
|  | openEMS | 2.4250 | -14.3 | 37.5 | ideal | ideal | ideal | 6.31 to 6.43 | 6.43 | – | – | 84/84 | RHCP |  |
| `A_L37.38_f6.90_er2.55_h1.52_Gm100` | HFSS | 2.4210 | -10.2 | 28.6 | 0.23 @ 2.4125 | 0.27 | – | 6.97 to 7.18 | 7.17 | 7.99 | 0.87 | 73/72 | RHCP | 39428 / 19 |
|  | openEMS | 2.4260 | -11.8 | 31.0 | ideal | ideal | ideal | 6.78 to 6.93 | 6.93 | – | – | 74/72 | RHCP |  |
| `A_L37.38_f6.90_er2.55_h1.52_Gm100_mesh40k` | HFSS | 2.4215 | -10.3 | 28.7 | 0.21 @ 2.4125 | 0.26 | – | 6.98 to 7.17 | 7.16 | 7.99 | 0.87 | 73/72 | RHCP | 41957 / 20 |
|  | openEMS | 2.4260 | -11.8 | 31.0 | ideal | ideal | ideal | 6.78 to 6.93 | 6.93 | – | – | 74/72 | RHCP |  |
| `A_L37.38_f6.90_er2.55_h1.52_mesh40k` | HFSS | 2.4185 | -11.5 | 40.7 | 0.19 @ 2.4100 | 0.24 | – | 6.37 to 6.61 | 6.58 | 7.15 | 0.90 | 86/86 | RHCP | 44160 / 18 |
|  | openEMS | 2.4250 | -14.3 | 37.5 | ideal | ideal | ideal | 6.31 to 6.43 | 6.43 | – | – | 84/84 | RHCP |  |
| `B_L31.54_f5.90_c3.13_er3.66_h1.52` | HFSS | 2.4420 | -13.4 | 76.7 | 0.26 @ 2.4150 | 5.99 | 19.1 | 5.60 to 5.86 | 5.93 | 6.85 | 0.84 | 88/90 | RHCP | 15619 / 12 |
|  | openEMS | 2.4525 | -12.2 | 69.0 | 0.21 @ 2.4250 | 3.47 | 15.0 | 5.51 to 5.68 | 5.68 | 6.72 | 0.84 | 88/88 | RHCP |  |
| `B_L31.54_f5.90_c3.13_er3.66_h1.52_Gm100` | HFSS | 2.4445 | -13.3 | 72.4 | 2.11 @ 2.4200 | 6.00 | 11.8 | 5.96 to 6.22 | 6.28 | 7.51 | 0.79 | 75/76 | RHCP | 21815 / 15 |
|  | openEMS | 2.4520 | -12.1 | 68.0 | 1.47 @ 2.4250 | 4.28 | 12.5 | 5.96 to 6.11 | 6.14 | 7.38 | 0.80 | 74/76 | RHCP |  |
| `B_L31.54_f5.90_c3.13_er3.66_h1.52_Gm100_mesh40k` | HFSS | 2.4465 | -14.2 | 69.7 | 1.59 @ 2.4225 | 4.75 | 13.6 | 6.09 to 6.28 | 6.31 | 7.53 | 0.78 | 75/76 | RHCP | 42131 / 21 |
|  | openEMS | 2.4520 | -12.1 | 68.0 | 1.47 @ 2.4250 | 4.28 | 12.5 | 5.96 to 6.11 | 6.14 | 7.38 | 0.80 | 74/76 | RHCP |  |
| `B_L31.54_f5.90_c3.13_er3.66_h1.52_mesh40k` | HFSS | 2.4460 | -14.5 | 73.1 | 0.68 @ 2.4225 | 4.24 | 18.1 | 5.71 to 5.85 | 5.86 | 6.80 | 0.83 | 90/90 | RHCP | 46951 / 23 |
|  | openEMS | 2.4525 | -12.2 | 69.0 | 0.21 @ 2.4250 | 3.47 | 15.0 | 5.51 to 5.68 | 5.68 | 6.72 | 0.84 | 88/88 | RHCP |  |
| `B_L37.22_f7.00_c3.50_er2.55_h1.52_Gm100` | HFSS | 2.4620 | -8.2 | 62.9 | 0.72 @ 2.4425 | 10.21 | 15.1 | 5.56 to 7.13 | 7.09 | 7.96 | 0.87 | 74/72 | RHCP | 37066 / 18 |
| `B_L37.22_f7.00_c3.50_er2.55_h1.52_Gm100_mesh40k` | HFSS | 2.4630 | -8.0 | 63.2 | 0.70 @ 2.4425 | 10.40 | 15.2 | 5.48 to 7.09 | 7.05 | 7.95 | 0.87 | 74/72 | RHCP | 46124 / 20 |
| `B_L37.52_f7.00_c3.50_er2.52_h1.52_Gm100` | HFSS | 2.4560 | -10.7 | 63.4 | 0.69 @ 2.4350 | 7.86 | 15.3 | 6.28 to 7.30 | 7.25 | 7.99 | 0.87 | 73/72 | RHCP | 30344 / 16 |
| `B_L37.52_f7.00_c3.50_er2.52_h1.52_Gm100_mesh40k` | HFSS | 2.4575 | -10.0 | 63.4 | 0.64 @ 2.4375 | 8.44 | 15.3 | 6.09 to 7.25 | 7.20 | 7.97 | 0.87 | 74/72 | RHCP | 46241 / 19 |
| `B_L37.52_f7.00_c3.50_er2.54_h1.52_Gm100_er2.542` | HFSS | 2.4460 | -14.8 | 68.1 | 0.45 @ 2.4225 | 4.49 | 16.2 | 7.06 to 7.23 | 7.24 | 7.95 | 0.88 | 72/73 | RHCP | 17713 / 13 |
| `B_L37.52_f7.00_c3.50_er2.54_h1.52_Gm100_er2.542_mesh40k` | HFSS | 2.4495 | -14.4 | 64.8 | 0.40 @ 2.4275 | 5.01 | 15.8 | 6.85 to 7.24 | 7.24 | 7.97 | 0.87 | 73/73 | RHCP | 50419 / 22 |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100` | HFSS | 2.4420 | -14.2 | 69.6 | 0.75 @ 2.4175 | 6.23 | 16.1 | 6.87 to 7.18 | 7.23 | 7.95 | 0.88 | 72/73 | RHCP | 15800 / 12 |
|  | openEMS | 2.4505 | -12.8 | 63.5 | 0.18 @ 2.4250 | 3.94 | 12.5 | 6.80 to 7.05 | 7.05 | 7.81 | 0.88 | 74/74 | RHCP |  |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_box` | HFSS | 2.4420 | -14.5 | 70.2 | 0.69 @ 2.4175 | 5.84 | 16.5 | 6.71 to 6.98 | 7.02 | 7.71 | 0.88 | 74/75 | RHCP | 17811 / 11 |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_box_mesh40k` | HFSS | 2.4455 | -15.6 | 66.1 | 0.48 @ 2.4250 | 4.11 | 16.2 | 6.79 to 6.97 | 6.97 | 7.68 | 0.87 | 75/75 | RHCP | 41154 / 17 |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_fine` | HFSS | 2.4435 | -15.1 | 66.9 | 0.49 @ 2.4200 | 5.06 | 16.1 | 7.02 to 7.25 | 7.26 | 7.97 | 0.88 | 72/73 | RHCP | 22796 / 15 |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_mask` | HFSS | 2.4375 | -14.1 | 71.2 | 0.97 @ 2.4125 | 7.50 | 16.0 | 6.70 to 7.14 | 7.25 | 7.96 | 0.87 | 72/73 | RHCP | 29794 / 8 |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_mask_mesh40k` | HFSS | 2.4395 | -14.8 | 68.2 | 0.52 @ 2.4175 | 6.57 | 16.3 | 6.80 to 7.16 | 7.21 | 7.96 | 0.86 | 72/73 | RHCP | 44083 / 11 |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_mesh40k` | HFSS | 2.4455 | -15.5 | 65.8 | 0.43 @ 2.4250 | 4.14 | 16.0 | 7.08 to 7.24 | 7.25 | 7.97 | 0.87 | 72/73 | RHCP | 40404 / 18 |
|  | openEMS | 2.4505 | -12.8 | 63.5 | 0.18 @ 2.4250 | 3.94 | 12.5 | 6.80 to 7.05 | 7.05 | 7.81 | 0.88 | 74/74 | RHCP |  |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_pec` | HFSS | 2.4430 | -14.9 | 66.6 | 0.80 @ 2.4200 | 5.42 | 15.3 | 7.20 to 7.46 | 7.48 | 7.95 | 0.93 | 72/73 | RHCP | 17680 / 13 |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_pec_mesh40k` | HFSS | 2.4470 | -15.6 | 64.6 | 0.45 @ 2.4250 | 4.20 | 15.4 | 7.22 to 7.46 | 7.46 | 7.96 | 0.92 | 73/73 | RHCP | 47279 / 19 |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_sma` | HFSS | 2.4405 | -18.1 | 66.5 | 0.21 @ 2.4225 | 4.72 | 16.1 | 7.06 to 7.29 | 7.29 | 7.95 | 0.87 | 72/73 | RHCP | 32375 / 14 |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_sma_mesh40k` | HFSS | 2.4415 | -18.2 | 65.7 | 0.32 @ 2.4225 | 4.33 | 16.0 | 7.08 to 7.27 | 7.28 | 7.94 | 0.87 | 72/73 | RHCP | 41039 / 16 |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_vfine` | HFSS | 2.4455 | -15.5 | 65.8 | 0.43 @ 2.4250 | 4.14 | 16.0 | 7.08 to 7.24 | 7.25 | 7.97 | 0.87 | 72/73 | RHCP | 40404 / 18 |
| `B_L37.52_f7.00_c3.50_er2.56_h1.52_Gm100_er2.558` | HFSS | 2.4405 | -14.5 | 68.8 | 0.64 @ 2.4175 | 6.46 | 16.1 | 6.86 to 7.20 | 7.25 | 7.96 | 0.88 | 72/73 | RHCP | 23275 / 14 |
| `B_L37.52_f7.00_c3.50_er2.56_h1.52_Gm100_er2.558_mesh40k` | HFSS | 2.4425 | -15.3 | 66.4 | 0.22 @ 2.4200 | 5.32 | 16.1 | 6.98 to 7.23 | 7.25 | 7.97 | 0.87 | 72/73 | RHCP | 44253 / 18 |
| `B_L37.52_f7.00_c3.50_er2.58_h1.52_Gm100` | HFSS | 2.4320 | -14.3 | 71.1 | 1.21 @ 2.4050 | 9.75 | 15.5 | 6.38 to 7.03 | 7.33 | 7.96 | 0.87 | 72/74 | RHCP | 23482 / 16 |
| `B_L37.52_f7.00_c3.50_er2.58_h1.52_Gm100_mesh40k` | HFSS | 2.4335 | -14.8 | 68.2 | 0.59 @ 2.4100 | 8.69 | 16.0 | 6.53 to 7.14 | 7.30 | 7.96 | 0.87 | 72/74 | RHCP | 42264 / 20 |
| `B_L37.56_f7.00_c3.80_er2.55_h1.52` | HFSS | 2.4440 | -11.7 | 81.3 | 0.64 @ 2.4125 | 6.17 | 20.2 | 6.17 to 6.40 | 6.50 | 7.18 | 0.90 | 85/86 | RHCP | 13408 / 11 |
|  | openEMS | 2.4550 | -11.6 | 71.0 | 0.27 @ 2.4250 | 3.37 | 15.0 | 6.12 to 6.30 | 6.30 | 7.05 | 0.90 | 84/84 | RHCP |  |
| `B_L37.56_f7.00_c3.80_er2.55_h1.52_Gm100` | HFSS | 2.4470 | -11.7 | 78.7 | 2.12 @ 2.4175 | 5.90 | 12.7 | 6.80 to 6.99 | 7.07 | 7.92 | 0.88 | 72/74 | RHCP | 14940 / 12 |
|  | openEMS | 2.4560 | -11.5 | 71.0 | 1.29 @ 2.4275 | 4.08 | 12.5 | 6.74 to 6.94 | 6.96 | 7.81 | 0.88 | 72/74 | RHCP |  |
| `B_L37.56_f7.00_c3.80_er2.55_h1.52_Gm100_mesh40k` | HFSS | 2.4510 | -13.4 | 72.9 | 1.14 @ 2.4250 | 3.77 | 15.9 | 7.04 to 7.16 | 7.18 | 7.97 | 0.87 | 72/73 | RHCP | 41766 / 19 |
|  | openEMS | 2.4560 | -11.5 | 71.0 | 1.29 @ 2.4275 | 4.08 | 12.5 | 6.74 to 6.94 | 6.96 | 7.81 | 0.88 | 72/74 | RHCP |  |
| `B_L37.56_f7.00_c3.80_er2.55_h1.52_mesh40k` | HFSS | 2.4480 | -13.4 | 75.5 | 0.66 @ 2.4225 | 4.07 | 19.0 | 6.33 to 6.45 | 6.46 | 7.14 | 0.90 | 86/87 | RHCP | 40072 / 19 |
|  | openEMS | 2.4550 | -11.6 | 71.0 | 0.27 @ 2.4250 | 3.37 | 15.0 | 6.12 to 6.30 | 6.30 | 7.05 | 0.90 | 84/84 | RHCP |  |
| `B_L37.82_f7.00_c3.50_er2.55_h1.52_Gm100` | HFSS | 2.4265 | -16.3 | 70.8 | 1.07 @ 2.4000 | 11.39 | – | 6.08 to 6.92 | 7.39 | 7.98 | 0.87 | 71/74 | RHCP | 24237 / 17 |
| `B_L37.82_f7.00_c3.50_er2.55_h1.52_Gm100_mesh40k` | HFSS | 2.4280 | -15.9 | 68.1 | 0.60 @ 2.4050 | 10.55 | 16.1 | 6.20 to 7.01 | 7.35 | 7.96 | 0.87 | 72/74 | RHCP | 46920 / 20 |
| `plain_L30.66_f5.70_er3.66_h3.05` | HFSS | 2.4070 | -12.3 | 74.5 | n/a | n/a | n/a | n/a | 6.38 | 6.79 | 0.93 | 89/91 | linear | 22783 / 16 |
|  | openEMS | 2.4165 | -13.7 | 61.0 | n/a | n/a | n/a | n/a | 6.23 | 6.69 | 0.91 | 90/88 | linear |  |
| `plain_L30.66_f5.70_er3.66_h3.05_Gm100` | HFSS | 2.4110 | -10.8 | 54.2 | n/a | n/a | n/a | n/a | 6.88 | 7.54 | 0.90 | 79/74 | linear | 44210 / 17 |
|  | openEMS | 2.4145 | -12.5 | 55.0 | n/a | n/a | n/a | n/a | 6.76 | 7.32 | 0.89 | 78/72 | linear |  |
| `plain_L31.40_f5.80_er3.66_h1.52` | HFSS | 2.4170 | -10.5 | 38.6 | n/a | n/a | n/a | n/a | 5.89 | 6.81 | 0.84 | 89/91 | linear | 40738 / 20 |
|  | openEMS | 2.4245 | -13.7 | 36.5 | n/a | n/a | n/a | n/a | 5.82 | 6.73 | 0.82 | 88/88 | linear |  |
| `plain_L36.44_f6.70_er2.55_h3.05` | HFSS | 2.4110 | -13.5 | 74.0 | n/a | n/a | n/a | n/a | 6.93 | 7.16 | 0.96 | 84/89 | linear | 19672 / 14 |
|  | openEMS | 2.4215 | -14.6 | 59.5 | n/a | n/a | n/a | n/a | 6.71 | 7.05 | 0.94 | 82/84 | linear |  |
| `plain_L36.44_f6.70_er2.55_h3.05_Gm100` | HFSS | 2.4215 | -15.9 | 63.1 | n/a | n/a | n/a | n/a | 7.72 | 7.99 | 0.95 | 74/72 | linear | 50623 / 20 |
|  | openEMS | 2.4235 | -17.4 | 57.5 | n/a | n/a | n/a | n/a | 7.52 | 7.81 | 0.94 | 74/72 | linear |  |
