## Four tuned antennas, 60 mm board on the 100 mm face

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
| Air gap 4.8 mm (-0.2) | -12.8 dB | 0.19 dB at 2.4250 GHz | 1.41 dB | 48.8 MHz | 8.46 to 8.53 dBic | yes |
| Air gap 5.2 mm (+0.2) | -12.5 dB | 0.72 dB at 2.4250 GHz | 1.56 dB | 49.3 MHz | 8.48 to 8.55 dBic | yes |
| Upper board 0.5 mm off in x and y | -12.6 dB | 0.39 dB at 2.4250 GHz | 1.40 dB | 49.5 MHz | 8.48 to 8.54 dBic | yes |
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
| 50 mm | -15.5 dB | 3.77 dB | 0.03 dB at 2.4250 GHz | 15.9 MHz | 7.05 to 7.25 dBic | 7.99 dBi | 87 % | 73 deg | no |
| 60 mm | -15.5 dB | 4.14 dB | 0.43 dB at 2.4250 GHz | 16.0 MHz | 7.08 to 7.24 dBic | 7.97 dBi | 87 % | 72 deg | no |
| 70 mm | -15.6 dB | 4.05 dB | 0.36 dB at 2.4250 GHz | 16.0 MHz | 7.05 to 7.22 dBic | 7.94 dBi | 87 % | 73 deg | no |
| 80 mm | -15.5 dB | 3.83 dB | 0.20 dB at 2.4250 GHz | 16.0 MHz | 7.00 to 7.19 dBic | 7.92 dBi | 87 % | 73 deg | no |
| 90 mm | -15.5 dB | 4.06 dB | 0.39 dB at 2.4250 GHz | 16.0 MHz | 7.03 to 7.20 dBic | 7.92 dBi | 87 % | 73 deg | no |
| 100 mm | -15.6 dB | 4.00 dB | 0.31 dB at 2.4250 GHz | 16.0 MHz | 7.00 to 7.17 dBic | 7.89 dBi | 87 % | 73 deg | no |

**Dual feed** (typical coupler, 0.4 dB coupler loss included)

| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 50 mm | -13.1 dB | 0.77 dB | 0.09 dB at 2.4150 GHz | n/a MHz | 6.74 to 6.97 dBic | 8.00 dBi | 87 % | 72 deg | yes |
| 60 mm | -13.6 dB | 0.79 dB | 0.08 dB at 2.4075 GHz | n/a MHz | 6.75 to 6.96 dBic | 7.97 dBi | 87 % | 72 deg | yes |
| 70 mm | -13.4 dB | 0.73 dB | 0.04 dB at 2.4225 GHz | n/a MHz | 6.75 to 6.94 dBic | 7.96 dBi | 87 % | 73 deg | yes |
| 80 mm | -13.6 dB | 0.80 dB | 0.11 dB at 2.4050 GHz | n/a MHz | 6.72 to 6.92 dBic | 7.93 dBi | 87 % | 73 deg | yes |
| 90 mm | -13.6 dB | 0.74 dB | 0.05 dB at 2.4200 GHz | n/a MHz | 6.70 to 6.91 dBic | 7.93 dBi | 87 % | 73 deg | yes |
| 100 mm | -13.1 dB | 0.76 dB | 0.08 dB at 2.4300 GHz | n/a MHz | 6.68 to 6.86 dBic | 7.88 dBi | 87 % | 73 deg | yes |

**Stacked cut corner**

| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 50 mm | -14.0 dB | 3.34 dB | 0.25 dB at 2.4400 GHz | 48.1 MHz | 8.43 to 8.59 dBic | 8.88 dBi | 97 % | 66 deg | no |
| 60 mm | -12.7 dB | 1.39 dB | 0.40 dB at 2.4250 GHz | 49.4 MHz | 8.49 to 8.56 dBic | 8.87 dBi | 98 % | 66 deg | yes |
| 70 mm | -12.4 dB | 1.59 dB | 0.66 dB at 2.4250 GHz | 49.4 MHz | 8.44 to 8.48 dBic | 8.83 dBi | 98 % | 66 deg | yes |
| 80 mm | -12.3 dB | 1.71 dB | 0.68 dB at 2.4200 GHz | 49.8 MHz | 8.44 to 8.48 dBic | 8.83 dBi | 98 % | 66 deg | yes |
| 90 mm | -12.3 dB | 1.78 dB | 0.82 dB at 2.4200 GHz | 49.2 MHz | 8.41 to 8.45 dBic | 8.81 dBi | 98 % | 66 deg | yes |
| 100 mm | -12.3 dB | 1.84 dB | 0.75 dB at 2.4200 GHz | 49.5 MHz | 8.39 to 8.42 dBic | 8.78 dBi | 98 % | 66 deg | yes |

**Stacked dual feed** (typical coupler, 0.4 dB coupler loss included)

| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 50 mm | -16.8 dB | 1.37 dB | 0.68 dB at 2.3950 GHz | n/a MHz | 8.17 to 8.35 dBic | 8.87 dBi | 97 % | 66 deg | yes |
| 60 mm | -19.2 dB | 1.48 dB | 0.75 dB at 2.3800 GHz | n/a MHz | 8.28 to 8.34 dBic | 8.86 dBi | 98 % | 66 deg | yes |
| 70 mm | -16.9 dB | 1.48 dB | 0.74 dB at 2.3800 GHz | n/a MHz | 8.28 to 8.32 dBic | 8.84 dBi | 98 % | 66 deg | yes |
| 80 mm | -16.1 dB | 1.46 dB | 0.73 dB at 2.3800 GHz | n/a MHz | 8.25 to 8.29 dBic | 8.82 dBi | 98 % | 66 deg | yes |
| 90 mm | -16.1 dB | 1.49 dB | 0.75 dB at 2.3800 GHz | n/a MHz | 8.22 to 8.26 dBic | 8.79 dBi | 98 % | 67 deg | yes |
| 100 mm | -16.4 dB | 1.52 dB | 0.77 dB at 2.3800 GHz | n/a MHz | 8.18 to 8.22 dBic | 8.75 dBi | 98 % | 67 deg | yes |

### No metal behind the board (ground plane = board)

**Cut corner**

| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100 mm | -15.6 dB | 4.00 dB | 0.31 dB at 2.4250 GHz | 16.0 MHz | 7.00 to 7.17 dBic | 7.89 dBi | 87 % | 73 deg | no |

**Dual feed** (typical coupler, 0.4 dB coupler loss included)

| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100 mm | -13.1 dB | 0.76 dB | 0.08 dB at 2.4300 GHz | n/a MHz | 6.68 to 6.86 dBic | 7.88 dBi | 87 % | 73 deg | yes |

**Stacked cut corner**

| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100 mm | -12.3 dB | 1.84 dB | 0.75 dB at 2.4200 GHz | 49.5 MHz | 8.39 to 8.42 dBic | 8.78 dBi | 98 % | 66 deg | yes |

**Stacked dual feed** (typical coupler, 0.4 dB coupler loss included)

| Board side | Worst S11 | Worst axial ratio | Best axial ratio at | 3 dB AR window | RHCP gain in channel | Directivity | Efficiency | Beamwidth | All pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 100 mm | -16.4 dB | 1.52 dB | 0.77 dB at 2.3800 GHz | n/a MHz | 8.18 to 8.22 dBic | 8.75 dBi | 98 % | 67 deg | yes |

