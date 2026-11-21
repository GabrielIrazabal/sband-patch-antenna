# Prototype: 3 mm patch boards

**Status: prototype drawings for discussion.** Nothing here has been ordered, no Gerbers have been exported, and the rev-1 boards, `fab/` and `generate_boards.py` are unchanged. The dimensions come from simulation only.

## What this is

JLC sells the PTFE (ZYF255DA) as a 1.524 mm two-layer board. A patch on a board twice as thick has about twice the bandwidth and about 0.4 to 0.5 dB more gain (see [`sim/THICK_BOARD.md`](../../sim/THICK_BOARD.md)). So each antenna here is built from two 1.524 mm boards bonded face to face, with one patch on top:

![Cross-section](../../docs/thick_stackup.png)

| Folder | What is on it |
| --- | --- |
| `B_cutcorner_RHCP_PTFE_3mm_TOP` | Cut-corner patch on the front. No copper on the back. |
| `B_cutcorner_RHCP_PTFE_3mm_BOTTOM` | No copper on the front. Ground plane and one SMA on the back. |
| `A_dualfeed_PTFE_3mm_TOP` | Square patch on the front. No copper on the back. |
| `A_dualfeed_PTFE_3mm_BOTTOM` | No copper on the front. Ground plane and two SMAs on the back. |

Each folder has the KiCad board and an SVG picture. The BOTTOM pictures are drawn as seen from the back. All four boards report `DRC clean`.

## Dimensions

| | Cut corner (B-3MM) | Dual feed (A-3MM) |
| --- | --- | --- |
| Board | 60 mm square, M3 holes 4 mm in from each edge | same |
| Patch side | 37.10 mm | 36.39 mm |
| Corner cut | 5.55 mm, top-left and bottom-right in the top view | none |
| Feed | 8.00 mm right of centre and 2.18 mm up | J1 6.70 mm right of centre, J2 6.70 mm above centre |
| Feed hole | 0.6 mm, for a 0.5 mm wire | same |
| Connector | Würth 60312102114405 surface-mount SMA | two of the same |

The cut-corner feed sits 2.18 mm off the centre line on purpose. The feed wire through 3 mm of board adds inductance, and the sideways offset cancels it.

On the dual feed, RHCP needs J2 to lag J1 by 90°, the same as the rev-1 board A. The coupler is still an external part.

## How it goes together

1. Bond the TOP board onto the BOTTOM board with a thin, even layer of adhesive, using the four M3 holes to line them up. There must be no air between them.
2. Solder the SMA to the back of the BOTTOM board.
3. Pass a 0.5 mm wire through the feed hole in both boards. Solder it to the SMA centre pad at the back and to the patch at the front, and trim it flush.

## Open points before any order

- **The bond matters more than anything else in the build.** In simulation a 0.05 mm air film between the boards moves the cut corner's axial ratio from 2.2 dB to 6.5 dB, and a 0.10 mm air film detunes the dual feed by about 49 MHz. A 0.05 mm adhesive layer of Dk 3.0 changes little (cut corner 2.6 dB). Screws alone will not guarantee zero air. The adhesive, its thickness and its Dk are not chosen.
- **The feed hole is plated but has a pad on one face only**, so that both bond faces stay bare and flat. JLC may ask about a plated hole with no pad on one side. The alternative is an unplated hole in both boards; the wire carries the signal either way.
- **Each board has copper on one side only.** Check that JLC will build ZYF255DA with one side fully etched.
- **The cut corner is still sensitive to tolerances.** With Dk ±1.2 % or the patch ±0.3 mm its axial ratio goes to 4.2 to 5.6 dB. If it is built, it needs −0.3 and +0.3 mm variants like rev 1. These are not drawn.
- **These files were written with KiCad 8.0.** The rev-1 boards were generated with a newer KiCad, which will open these files; the reverse is not true.
- **The simulation has a 0.5 mm feed pin and no SMA, solder mask or adhesive.** On the thin board the SMA moved the result by −2.5 to −4 MHz and solder mask by −6 to −8 MHz (`sim/HFSS_RESULTS.md`). Neither check has been repeated at this thickness. The cut corner's axial-ratio window has about ±6 MHz to spare, so those shifts matter for it.

## Regenerating

```
"C:\Program Files\KiCad\8.0\bin\python.exe" kicad/prototype_thick.py
```

Dimensions are read from [`sim/thick_design.json`](../../sim/thick_design.json).
