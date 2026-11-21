# Results on the 60 mm board

Four plots for each tuned antenna, each in its own file. Ansys HFSS, about 40,000-element mesh, 60 mm square PTFE board (Dk 2.55, 1.524 mm) on a 100 mm metal face, 2.425 GHz, channel 2.415 to 2.435 GHz. Simulation only: nothing has been built or measured.

Dual-feed figures assume a typical 90 degree coupler (0.5 dB and 3 degrees off, 0.4 dB loss).

| Antenna | Worst S11 | Match window | Worst axial ratio | 3 dB AR window | RHCP gain in channel | Beamwidth | Height | Extra parts | Meets all four |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Cut corner](cut_corner/) | -15.5 dB | 66 MHz | 4.14 dB | 16 MHz | 7.08 to 7.24 dBic | 72 deg | 1.5 mm | none | no |
| [Dual feed](dual_feed/) | -13.6 dB | 32 MHz | 0.79 dB | set by the coupler | 6.75 to 6.96 dBic | 72 deg | 1.5 mm | coupler, load, second line | yes |
| [Stacked cut corner, 5 mm gap](stacked_cut_corner_5mm_gap/) | -12.7 dB | 206 MHz | 1.39 dB | 49 MHz | 8.49 to 8.56 dBic | 66 deg | 8.0 mm | second board, spacers | yes |
| [Stacked cut corner, 3 mm gap](stacked_cut_corner_3mm_gap/) | -26.3 dB | 146 MHz | 1.87 dB | 35 MHz | 8.45 to 8.51 dBic | 68 deg | 6.0 mm | second board, spacers | yes |
| [Stacked dual feed, 5 mm gap](stacked_dual_feed/) | -19.2 dB | 106 MHz | 1.48 dB | set by the coupler | 8.28 to 8.34 dBic | 66 deg | 8.0 mm | second board, spacers, coupler, load, second line | yes |

Requirements: S11 -10 dB or lower, axial ratio 3 dB or lower, RHCP gain 6.5 dBic or more, beamwidth 60 degrees or wider, all across the channel.

## Cut corner

HFSS run: `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100_mesh40k`

| Match | Axial ratio |
| --- | --- |
| ![S11](cut_corner/1_s11.png) | ![Axial ratio](cut_corner/2_axial_ratio.png) |

| Gain | Pattern |
| --- | --- |
| ![Gain](cut_corner/3_gain.png) | ![Pattern](cut_corner/4_pattern.png) |

## Dual feed

HFSS run: `A_L37.28_f5.80_er2.55_h1.52_Gm100_mesh40k`

| Match | Axial ratio |
| --- | --- |
| ![S11](dual_feed/1_s11.png) | ![Axial ratio](dual_feed/2_axial_ratio.png) |

| Gain | Pattern |
| --- | --- |
| ![Gain](dual_feed/3_gain.png) | ![Pattern](dual_feed/4_pattern.png) |

## Stacked cut corner, 5 mm gap

HFSS run: `S_L36.26_f15.96_c6.56_fy3.07_U42.97_uc7.80_g5.00_er2.55_h1.52_Gm100_mesh40k`

| Match | Axial ratio |
| --- | --- |
| ![S11](stacked_cut_corner_5mm_gap/1_s11.png) | ![Axial ratio](stacked_cut_corner_5mm_gap/2_axial_ratio.png) |

| Gain | Pattern |
| --- | --- |
| ![Gain](stacked_cut_corner_5mm_gap/3_gain.png) | ![Pattern](stacked_cut_corner_5mm_gap/4_pattern.png) |

## Stacked cut corner, 3 mm gap

HFSS run: `S_L35.63_f15.68_c5.40_fy3.02_U42.23_uc6.42_g3.00_er2.55_h1.52_Gm100_mesh40k`

| Match | Axial ratio |
| --- | --- |
| ![S11](stacked_cut_corner_3mm_gap/1_s11.png) | ![Axial ratio](stacked_cut_corner_3mm_gap/2_axial_ratio.png) |

| Gain | Pattern |
| --- | --- |
| ![Gain](stacked_cut_corner_3mm_gap/3_gain.png) | ![Pattern](stacked_cut_corner_3mm_gap/4_pattern.png) |

## Stacked dual feed, 5 mm gap

HFSS run: `SD_L35.04_f13.35_U41.51_uc0.00_g5.00_er2.55_h1.52_Gm100_mesh40k`

| Match | Axial ratio |
| --- | --- |
| ![S11](stacked_dual_feed/1_s11.png) | ![Axial ratio](stacked_dual_feed/2_axial_ratio.png) |

| Gain | Pattern |
| --- | --- |
| ![Gain](stacked_dual_feed/3_gain.png) | ![Pattern](stacked_dual_feed/4_pattern.png) |
