## Three tuned antennas, 60 mm board on the 100 mm face

| | Cut corner | Dual feed | Stacked cut corner | Stacked dual feed | Requirement |
| --- | --- | --- | --- | --- | --- |
| Worst S11 in the channel | -15.5 dB | -13.6 dB | -12.7 dB | -19.2 dB | -10 dB or lower |
| -10 dB match window | 66 MHz | 32 MHz | 206 MHz | 106 MHz | covers the channel |
| Worst axial ratio in the channel | 4.14 dB | 0.79 dB | 1.39 dB | 1.48 dB | 3 dB or lower |
| 3 dB axial-ratio window | 16.0 MHz | n/a MHz | 49.4 MHz | n/a MHz | 20 MHz or more |
| Lowest RHCP gain in the channel | 7.08 dBic | 6.75 dBic | 8.49 dBic | 8.28 dBic | 6.5 dBic or more |
| Highest RHCP gain in the channel | 7.24 dBic | 6.96 dBic | 8.56 dBic | 8.34 dBic |  |
| Directivity | 7.97 dBi | 7.97 dBi | 8.87 dBi | 8.86 dBi |  |
| Half-power beamwidth | 72 deg | 72 deg | 66 deg | 66 deg | 60 deg or wider |
| Mesh elements | 40404  | 43596  | 41212  | 45490  |  |

## Stacked patch stress tests

| Case | Worst S11 | Best axial ratio | Worst axial ratio in channel | 3 dB AR window | RHCP gain in channel | All pass |
| --- | --- | --- | --- | --- | --- | --- |
| Nominal | -12.7 dB | 0.40 dB at 2.4250 GHz | 1.39 dB | 49.4 MHz | 8.49 to 8.56 dBic | yes |
| Board Dk 2.52 (-1.2 %) | -12.6 dB | 0.68 dB at 2.4350 GHz | 2.70 dB | 49.0 MHz | 8.42 to 8.53 dBic | yes |
| Board Dk 2.58 (+1.2 %) | -13.0 dB | 0.30 dB at 2.4150 GHz | 2.20 dB | 49.2 MHz | 8.52 to 8.54 dBic | yes |
| Both patches 0.3 mm small | -12.8 dB | 0.53 dB at 2.4450 GHz | 3.62 dB | 49.7 MHz | 8.36 to 8.51 dBic | no |
| Both patches 0.3 mm large | -13.2 dB | 0.31 dB at 2.4100 GHz | 3.18 dB | 48.9 MHz | 8.48 to 8.53 dBic | no |
| Air gap 4.8 mm (-0.2) | not run | | | | | |
| Air gap 5.2 mm (+0.2) | not run | | | | | |
| Upper board 0.5 mm off in x and y | not run | | | | | |
| SMA connector modelled | not run | | | | | |
| Solder mask around the lower patch | not run | | | | | |
| Metal box behind, not a flat plate | not run | | | | | |
| Lossless copper | not run | | | | | |
| Four nylon spacers in the gap | not run | | | | | |
| Four steel screws and metal standoffs | not run | | | | | |

### On the 100 mm metal face

**Cut corner**

| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 mm | -15.5 dB | 4.14 dB | 0.43 dB at 2.4250 GHz | 16.0 MHz | 7.08 to 7.24 dBic | 7.97 dBi | 87 % | 72 deg | no |

**Dual feed** (typical coupler, 0.4 dB coupler loss included)

| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 mm | -13.6 dB | 0.79 dB | 0.08 dB at 2.4075 GHz | n/a MHz | 6.75 to 6.96 dBic | 7.97 dBi | 87 % | 72 deg | yes |

**Stacked cut corner**

| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 mm | -12.7 dB | 1.39 dB | 0.40 dB at 2.4250 GHz | 49.4 MHz | 8.49 to 8.56 dBic | 8.87 dBi | 98 % | 66 deg | yes |

**Stacked dual feed** (typical coupler, 0.4 dB coupler loss included)

| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 60 mm | -19.2 dB | 1.48 dB | 0.75 dB at 2.3800 GHz | n/a MHz | 8.28 to 8.34 dBic | 8.86 dBi | 98 % | 66 deg | yes |

### No metal behind the board (ground plane = board)

