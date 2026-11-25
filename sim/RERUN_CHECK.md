# Rerun check, 24 November 2026

All four PTFE antenna options were simulated again in openEMS on the Mac and compared with the Ansys HFSS results from 14 to 21 November. For the dual feed re-tuned for the face and for both 3 mm designs, this is the first time a second solver has checked them.

Everything here is simulation. Nothing has been built or measured.

## Verdict

**Three of the four pass the requirements in both solvers. The 1.5 mm dual feed is borderline.**

The rule was strict: the worse of the two solvers has to meet each requirement across the whole 20 MHz channel (2.415 to 2.435 GHz).

| | Cut corner, 1.5 mm | Dual feed, 1.5 mm | Cut corner, 3 mm | Dual feed, 3 mm | Requirement |
| --- | --- | --- | --- | --- | --- |
| Lowest RHCP gain in channel, HFSS / openEMS | 7.08 / 6.80 dBic | 6.75 / **6.49** dBic | 7.61 / 7.32 dBic | 7.26 / 7.06 dBic | 6.5 or more |
| Worst return loss in channel, HFSS / openEMS | 15.5 / 12.8 dB | 13.6 / **11.0** dB | 19.1 / 13.4 dB | 16.4 / 17.3 dB | 10 dB or more |
| Match window, HFSS / openEMS | 66 / 64 MHz | 32 / 31 MHz | 131 / 127 MHz | 61 / 57 MHz | covers 20 MHz |
| Half-power beamwidth, HFSS / openEMS | 72° / 75° | 72° / 75° | 73° / 74° | 73° / 74° | 60° or wider |
| Hand | RHCP / RHCP | RHCP / RHCP | RHCP / RHCP | RHCP / RHCP | right-hand circular |
| Worst axial ratio in channel, HFSS / openEMS | 4.14 / 3.94 dB | 0.11 / 0.07 dB | 2.17 / 2.07 dB | 0.28 / 0.28 dB | none set (3 dB is a common target) |
| Best axial ratio at, HFSS / openEMS | 2.425 / 2.425 GHz | flat | 2.425 / 2.425 GHz | flat | |
| Strict verdict | pass, 0.3 dB gain margin | **borderline** | pass, 0.8 dB gain margin | pass, 0.6 dB gain margin | |

- Dual-feed gain has 0.4 dB taken off for the coupler. Their axial ratio is with a perfect coupler; a typical one (0.5 dB and 3° off) gives 0.8 to 0.9 dB.
- Dual-feed return loss is the patch's own, at one port. Behind a coupler the radio sees a better match, because reflections go to the coupler's load.

## What the rerun shows

- **The two solvers agree.** Both cut corners have their best polarization at exactly 2.425 GHz in both tools. openEMS reads 0.2 to 0.3 dB lower in gain than HFSS on every board, the same offset as on 14 November.
- **The 3 mm designs hold up in a second solver.** The cut corner's sideways feed offset (2.18 mm) was tuned in HFSS against a real 0.5 mm pin. openEMS models the pin as a thin wire and still gives 13.4 dB return loss and a 2.07 dB worst axial ratio.
- **The 1.5 mm dual feed has almost no margin.** In openEMS it is 0.01 dB under 6.5 dBic at the lower channel edge, and its match window clears the channel by 1.5 MHz on the low side. With a 0.3 dB coupler it would be 6.59 dBic.
- **The 1.5 mm cut corner rerun reproduced the earlier openEMS run exactly**, as it should: the solver is deterministic.

## What is still not shown by any simulation

| Gap | Affects |
| --- | --- |
| Both 1.5 mm boards fail the list if Dk is 1 % off or the patch is 0.3 mm off (HFSS stress runs, `HFSS_RESULTS.md`). The datasheet tolerance on Dk is ±0.04, which is ±1.6 % | 1.5 mm boards |
| A 0.05 to 0.10 mm air gap in the glue joint breaks the 3 mm boards (`results_hfss/thick_tables.md`) | 3 mm boards |
| Solder mask on the two bond faces, and the SMA and top solder mask at 3 mm thickness | 3 mm boards |
| A real coupler, its load and the two cables | dual feeds |
| Power handling at 1 to 3 W, and −40 to +85 °C with the datasheet's Dk drift (−115 ppm/°C) | all four |
| The UHF tape antenna on the same face, and the real satellite body | all four |
| HFSS was not rerun here: it needs the Windows laptop. See [`../HFSS_RERUN.md`](../HFSS_RERUN.md) | all four |

## Board files

Every KiCad board was measured against its simulated design on the same day and matches to 0.001 mm (patch side, corner cuts, feed position). Each 3 mm TOP and BOTTOM pair has its feed hole at the same position, and the Gerbers for the two bond faces contain no copper.

## Runs

Results are in `results_openems/`, in the four folders ending `_rerun`.

```bash
export PATH="$HOME/opt/openEMS/bin:$PATH"
PY=~/opt/openEMS/venv/bin/python
C="--er 2.55 --tand 0.0018 --Gm 100 --tag rerun"
$PY sim/openems_patch.py --board B --L 37.52 --feed 7.00 --cut 3.50 $C
$PY sim/openems_patch.py --board B --L 37.10 --feed 8.00 --feed_y 2.18 --cut 5.55 --h 3.048 $C
$PY sim/openems_patch.py --board A --L 37.28 --feed 5.80 --both-ports $C
$PY sim/openems_patch.py --board A --L 36.39 --feed 6.70 --h 3.048 --both-ports $C
```

`--feed_y` is new in `openems_patch.py`: the sideways offset of the feed, used by the 3 mm cut corner. Each run took 5 to 10 minutes.
