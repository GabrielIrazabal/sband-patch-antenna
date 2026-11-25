### Part 1: the four at nominal, rerun against the earlier HFSS run and openEMS

| Antenna | Run | Best match at | Worst return loss | Match window | Lowest RHCP gain | Worst axial ratio | Beamwidth | Hand |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cut corner, 1.5 mm | earlier HFSS | 2.4455 GHz | 15.5 dB | 66 MHz | 7.08 dBic | 4.14 dB | 72 deg | RHCP |
| | HFSS rerun | 2.4455 GHz | 15.5 dB | 66 MHz | 7.08 dBic | 4.14 dB | 72 deg | RHCP |
| | rerun minus earlier | +0.0 MHz | -0.0 dB | +0 MHz | +0.00 dB | +0.00 dB | +0 deg | |
| | openEMS, 24 Nov | 2.4500 GHz | 12.8 dB | 64 MHz | 6.80 dBic | 3.94 dB | | RHCP |
| Dual feed, 1.5 mm | earlier HFSS | 2.4250 GHz | 13.6 dB | 32 MHz | 6.75 dBic | 0.11 dB | 72 deg | RHCP |
| | HFSS rerun | 2.4250 GHz | 13.6 dB | 32 MHz | 6.75 dBic | 0.11 dB | 72 deg | RHCP |
| | rerun minus earlier | +0.0 MHz | -0.0 dB | -0 MHz | +0.00 dB | +0.00 dB | +0 deg | |
| | openEMS, 24 Nov | 2.4290 GHz | 11.0 dB | 31 MHz | 6.49 dBic | 0.07 dB | | RHCP |
| Cut corner, 3 mm | earlier HFSS | 2.3940 GHz | 19.1 dB | 131 MHz | 7.61 dBic | 2.17 dB | 73 deg | RHCP |
| | HFSS rerun | 2.3940 GHz | 19.1 dB | 131 MHz | 7.61 dBic | 2.17 dB | 73 deg | RHCP |
| | rerun minus earlier | +0.0 MHz | +0.0 dB | +0 MHz | +0.00 dB | +0.00 dB | +0 deg | |
| | openEMS, 24 Nov | 2.3870 GHz | 13.4 dB | 127 MHz | 7.32 dBic | 2.07 dB | | RHCP |
| Dual feed, 3 mm | earlier HFSS | 2.4225 GHz | 16.4 dB | 61 MHz | 7.26 dBic | 0.28 dB | 73 deg | RHCP |
| | HFSS rerun | 2.4225 GHz | 16.4 dB | 61 MHz | 7.26 dBic | 0.28 dB | 73 deg | RHCP |
| | rerun minus earlier | +0.0 MHz | +0.0 dB | -0 MHz | +0.00 dB | +0.00 dB | +0 deg | |
| | openEMS, 24 Nov | 2.4260 GHz | 17.3 dB | 57 MHz | 7.06 dBic | 0.28 dB | | RHCP |

### Every run

The last three columns compare each run with the rerun of the same antenna at nominal.

| Antenna | Case | Best match at | Worst return loss | Match window | RHCP gain in channel | Worst axial ratio | Beamwidth | Hand | Mesh elements | Shift of best match | Change in lowest gain | Requirements |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cut corner, 1.5 mm | Rerun, nominal | 2.4455 GHz | 15.5 dB | 66 MHz | 7.08 to 7.24 dBic | 4.14 dB | 72 deg | RHCP | 40404 | | | pass |
| Cut corner, 1.5 mm | Air box 62 mm (half a wavelength) | 2.4440 GHz | 15.5 dB | 66 MHz | 7.03 to 7.24 dBic | 4.65 dB | 73 deg | RHCP | 47290 | -1.5 MHz | -0.05 dB | pass |
| Cut corner, 1.5 mm | With the SMA (coax and wave port) (earlier run, 14 Nov) | 2.4415 GHz | 18.2 dB | 66 MHz | 7.08 to 7.27 dBic | 4.33 dB | 72 deg | RHCP | 41039 | -4.0 MHz | +0.00 dB | pass |
| Cut corner, 1.5 mm | With solder mask on the top (earlier run, 14 Nov) | 2.4395 GHz | 14.8 dB | 68 MHz | 6.80 to 7.16 dBic | 6.57 dB | 72 deg | RHCP | 44083 | -6.0 MHz | -0.28 dB | pass |
| Cut corner, 1.5 mm | 0.09 mm of Dk 3.5 in the glue joint | 2.3815 GHz | 19.4 dB | 133 MHz | 7.49 to 7.67 dBic | 4.10 dB | 73 deg | RHCP | 43858 | -64.0 MHz | +0.41 dB | pass |
| Dual feed, 1.5 mm | Rerun, nominal | 2.4250 GHz | 13.6 dB | 32 MHz | 6.75 to 6.96 dBic | 0.11 dB | 72 deg | RHCP | 43596 | | | pass |
| Dual feed, 1.5 mm | Finest mesh | 2.4260 GHz | 12.8 dB | 32 MHz | 6.70 to 6.94 dBic | 0.14 dB | 73 deg | RHCP | 58212 | +1.0 MHz | -0.05 dB | pass |
| Dual feed, 1.5 mm | Air box 62 mm (half a wavelength) | 2.4230 GHz | 12.1 dB | 32 MHz | 6.77 to 7.00 dBic | 0.13 dB | 72 deg | RHCP | 46473 | -2.0 MHz | +0.02 dB | pass |
| Dual feed, 1.5 mm | Air box 62 mm and finest mesh | 2.4235 GHz | 12.6 dB | 32 MHz | 6.78 to 6.98 dBic | 0.14 dB | 72 deg | RHCP | 54758 | -1.5 MHz | +0.03 dB | pass |
| Dual feed, 1.5 mm | With the SMA (coax and wave port) (earlier run, 14 Nov) | 2.4210 GHz | 11.0 dB | 32 MHz | 6.58 to 6.87 dBic | 0.04 dB | 73 deg | RHCP | 41250 | -4.0 MHz | -0.17 dB | pass |
| Dual feed, 1.5 mm | With solder mask on the top (earlier run, 14 Nov) | 2.4165 GHz | 9.1 dB | 32 MHz | 6.38 to 6.89 dBic | 0.06 dB | 73 deg | RHCP | 40595 | -8.5 MHz | -0.37 dB | FAIL |
| Dual feed, 1.5 mm | 0.09 mm of Dk 3.5 in the glue joint | 2.4105 GHz | 11.9 dB | 62 MHz | 7.12 to 7.32 dBic | 0.34 dB | 72 deg | RHCP | 47470 | -14.5 MHz | +0.37 dB | pass |
| Cut corner, 3 mm | Rerun, nominal | 2.3940 GHz | 19.1 dB | 131 MHz | 7.61 to 7.67 dBic | 2.17 dB | 73 deg | RHCP | 49915 | | | pass |
| Cut corner, 3 mm | Air box 62 mm (half a wavelength) | 2.3900 GHz | 19.3 dB | 131 MHz | 7.56 to 7.62 dBic | 2.61 dB | 73 deg | RHCP | 42218 | -4.0 MHz | -0.05 dB | pass |
| Cut corner, 3 mm | With the SMA (coax and wave port) | 2.3970 GHz | 21.0 dB | 129 MHz | 7.60 to 7.66 dBic | 2.03 dB | 73 deg | RHCP | 44479 | +3.0 MHz | -0.01 dB | pass |
| Cut corner, 3 mm | With solder mask on the top | 2.3855 GHz | 18.5 dB | 132 MHz | 7.58 to 7.67 dBic | 3.05 dB | 72 deg | RHCP | 45926 | -8.5 MHz | -0.03 dB | pass |
| Cut corner, 3 mm | 0.09 mm of Dk 3.5 in the glue joint | 2.3815 GHz | 19.4 dB | 133 MHz | 7.49 to 7.67 dBic | 4.10 dB | 73 deg | RHCP | 43858 | -12.5 MHz | -0.12 dB | pass |
| Dual feed, 3 mm | Rerun, nominal | 2.4225 GHz | 16.4 dB | 61 MHz | 7.26 to 7.32 dBic | 0.28 dB | 73 deg | RHCP | 49873 | | | pass |
| Dual feed, 3 mm | Air box 62 mm (half a wavelength) | 2.4185 GHz | 14.4 dB | 61 MHz | 7.12 to 7.22 dBic | 0.31 dB | 73 deg | RHCP | 51335 | -4.0 MHz | -0.14 dB | pass |
| Dual feed, 3 mm | With the SMA (coax and wave port) | 2.4180 GHz | 13.7 dB | 61 MHz | 7.17 to 7.25 dBic | 0.31 dB | 72 deg | RHCP | 42235 | -4.5 MHz | -0.09 dB | pass |
| Dual feed, 3 mm | With solder mask on the top | 2.4135 GHz | 12.8 dB | 62 MHz | 7.16 to 7.32 dBic | 0.26 dB | 72 deg | RHCP | 40024 | -9.0 MHz | -0.10 dB | pass |
| Dual feed, 3 mm | 0.09 mm of Dk 3.5 in the glue joint | 2.4105 GHz | 11.9 dB | 62 MHz | 7.12 to 7.32 dBic | 0.34 dB | 72 deg | RHCP | 47470 | -12.0 MHz | -0.14 dB | pass |

Not run or failed: Cut corner, 1.5 mm: -40 C (Dk 2.5676, sizes x 0.99907); Cut corner, 1.5 mm: +85 C (Dk 2.5309, sizes x 1.00101); Dual feed, 1.5 mm: -40 C (Dk 2.5676, sizes x 0.99907); Dual feed, 1.5 mm: +85 C (Dk 2.5309, sizes x 1.00101); Cut corner, 3 mm: -40 C (Dk 2.5676, sizes x 0.99907); Cut corner, 3 mm: +85 C (Dk 2.5309, sizes x 1.00101); Dual feed, 3 mm: -40 C (Dk 2.5676, sizes x 0.99907); Dual feed, 3 mm: +85 C (Dk 2.5309, sizes x 1.00101).

