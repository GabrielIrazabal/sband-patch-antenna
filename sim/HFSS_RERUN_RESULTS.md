# HFSS rerun and double-check: results

**In progress.** Started 24 November 2026 on the Windows laptop (Ansys Electronics Desktop Student 2025 R2), following [`../HFSS_RERUN.md`](../HFSS_RERUN.md). This file is filled in as runs finish. Everything here is simulation.

## Done so far

- **Part 1, the four at nominal: all four reruns reproduce the earlier HFSS runs exactly** (0.0 MHz, 0.00 dB, same mesh size). HFSS is deterministic for the same inputs, so this confirms the stored results and the scripts, not the physics. Table in [`results_hfss/rerun_tables.md`](results_hfss/rerun_tables.md).
- **Part 2, item 6, board files: all eight boards match their designs** to 0.001 mm in the KiCad file and in the Gerber, and the bond-face copper Gerbers of the 3 mm boards are empty. Table in [`results_hfss/board_check.md`](results_hfss/board_check.md), script [`check_boards.py`](check_boards.py).

## Still running

Part 2, items 1 to 5: 20 runs queued in the order of the task file.
