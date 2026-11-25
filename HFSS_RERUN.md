# HFSS rerun and double-check

Claude: this file is the job. Rerun the four antenna options in Ansys HFSS on this Windows laptop, run the extra checks, and write the results to `sim/HFSS_RERUN_RESULTS.md`. Work through the list in order.

The scripts are the ones already used here: `sim/hfss_patch.py` and `sim/hfss_batch.py`. Check `--help` before the first run. Keep the solver cache out of any synced folder (`--project-dir`).

## Background

- On 24 November 2026 all four options were re-simulated in openEMS on the Mac. Three pass the requirements in both solvers and the 1.5 mm dual feed is borderline. Read [`sim/RERUN_CHECK.md`](sim/RERUN_CHECK.md) first.
- `main` now contains everything from the `hfss-overnight` branch plus KiCad boards and Gerbers for all four options. Work from `main`.
- The KiCad boards changed since the last HFSS session: the 3 mm boards were regenerated with KiCad 10, and the 1.5 mm cut corner is now the hand-drawn `kicad/Cutcorner_antenna`.

## The four antennas

All on JLC PTFE ZYF255DA (Dk 2.55, loss tangent 0.0018), 60 mm board on a 100 mm metal face, 2.425 GHz, channel 2.415 to 2.435 GHz.

| Antenna | Options for `hfss_patch.py` (add `--er 2.55 --tand 0.0018 --Gm 100`) |
| --- | --- |
| Cut corner, 1.5 mm | `--board B --L 37.52 --feed 7.00 --cut 3.50` |
| Dual feed, 1.5 mm | `--board A --L 37.28 --feed 5.80` |
| Cut corner, 3 mm | `--board B --L 37.10 --feed 8.00 --feed_y 2.18 --cut 5.55 --h 3.048` |
| Dual feed, 3 mm | `--board A --L 36.39 --feed 6.70 --h 3.048` |

Requirements: RHCP gain 6.5 dBic or more, return loss 10 dB or more, beamwidth 60° or wider, right-hand circular, all across the channel. Dual-feed gain has 0.4 dB taken off for the coupler.

## Part 1: rerun the four at nominal

Run each at about 40,000 tetrahedra (`--target-tets 40000`) with `--tag rerun`, so the earlier folders are not overwritten.

Numbers to compare against:

| | Cut corner, 1.5 mm | Dual feed, 1.5 mm | Cut corner, 3 mm | Dual feed, 3 mm |
| --- | --- | --- | --- | --- |
| Lowest RHCP gain in channel, earlier HFSS / openEMS | 7.08 / 6.80 dBic | 6.75 / 6.49 dBic | 7.61 / 7.32 dBic | 7.26 / 7.06 dBic |
| Worst return loss in channel, earlier HFSS / openEMS | 15.5 / 12.8 dB | 13.6 / 11.0 dB | 19.1 / 13.4 dB | 16.4 / 17.3 dB |
| Match window, earlier HFSS / openEMS | 66 / 64 MHz | 32 / 31 MHz | 131 / 127 MHz | 61 / 57 MHz |
| Worst axial ratio in channel, earlier HFSS / openEMS | 4.14 / 3.94 dB | 0.11 / 0.07 dB | 2.17 / 2.07 dB | 0.28 / 0.28 dB |
| Best match at, earlier HFSS / openEMS | 2.4455 / 2.4500 GHz | 2.4250 / 2.4290 GHz | 2.3940 / 2.3870 GHz | 2.4225 / 2.4260 GHz |

Report, for each antenna: does the rerun reproduce the earlier HFSS run (within 2 MHz and 0.1 dB), and does the strict verdict change?

## Part 2: settle the open questions

1. **Is the 1.5 mm dual feed above 6.5 dBic or not?** The two tools disagree by 0.26 dB and the requirement sits between them. Rerun it at the finest mesh the Student licence allows, and again with a larger air box (`--pad 62`, half a wavelength). Say which gain figure you trust and why.
2. **Is HFSS's higher gain the air box?** Rerun the other three with `--pad 62` and report how much the gain moves.
3. **The 3 mm boards with the things left out.** These checks were only ever done at 1.5 mm. Run both 3 mm boards with `--sma`, and with `--mask`.
4. **Solder mask in the glue joint.** The factory will put mask on both bond faces unless told not to. Model the joint as a 0.09 mm layer of Dk 3.5 between the two boards (two mask layers plus adhesive), the same way the 0.05 mm adhesive case was done, for both 3 mm boards.
5. **Temperature, with the datasheet's numbers.** ZYF255DA: Dk changes by −115 ppm/°C, in-plane expansion about 15.5 ppm/°C. Scale Dk and every patch dimension from 20 °C:

   | Temperature | Dk | Scale on L, feed and cut |
   | --- | --- | --- |
   | −40 °C | 2.5676 | 0.99907 |
   | +85 °C | 2.5309 | 1.00101 |

   Run all four at both temperatures. The earlier ±0.3 % run was an assumed figure and about half the real drift.
6. **Check the board files against the designs.** Independently confirm that each KiCad board in `README.md`'s table has the patch side, corner cuts and feed position of its simulated design, and that the B.Cu Gerber of each 3 mm TOP board and the F.Cu Gerber of each 3 mm BOTTOM board contain no copper.

## What to hand back

`sim/HFSS_RERUN_RESULTS.md`, written as you go:

1. A short plain-language verdict at the top: which of the four pass in both tools, which do not, and what changed from `sim/RERUN_CHECK.md`.
2. One table row per run.
3. For each open question in Part 2, the answer in one or two sentences, with how sure you are.

## Rules

- Do not change the KiCad boards, the Gerbers, `kicad/generate_boards.py` or `kicad/prototype_thick.py`. If a board looks wrong, report it.
- `kicad/Cutcorner_antenna` was drawn by hand. Never regenerate or overwrite it.
- Do not send messages to anyone or place orders.
- If a run fails three times, write down why and move on.
- Commit as you go. Install software and push only as far as Gabriel's prompt allows.
- This repo is public. Commit with a GitHub noreply email, and keep personal details out of it.
