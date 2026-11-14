# Simulation

Two tools:

| Tool | State | Use |
| --- | --- | --- |
| **openEMS** ([`openems_patch.py`](openems_patch.py)) | Working. All results in this repo come from it | Free FDTD solver, scripted in Python, runs on macOS and Linux |
| **Ansys HFSS** ([`hfss_patch.py`](hfss_patch.py)) | Working (AEDT Student 2025 R2, PyAEDT 1.9). Results in [`HFSS_RESULTS.md`](HFSS_RESULTS.md) | Independent cross-check on Windows through PyAEDT |

## openEMS

### Install (macOS, what was done on Gabriel's Mac)

There is no ready-made macOS package, so it is built from source into `~/opt/openEMS`:

```bash
brew install boost hdf5 cmake
git clone --recursive https://github.com/thliebig/openEMS-Project.git ~/opt/openEMS-Project
cd ~/opt/openEMS-Project
./update_openEMS.sh ~/opt/openEMS --python --disable-GUI
```

- `--disable-GUI` skips the 3D model viewer, which needs VTK and Qt.
- The Python modules land in a virtual environment at `~/opt/openEMS/venv`.
- If the compiler fails to link with an "unknown architecture" error, Xcode and the Command Line Tools are mismatched. Prefix the build with `DEVELOPER_DIR=/Library/Developer/CommandLineTools`.

### Run

```bash
export PATH="$HOME/opt/openEMS/bin:$PATH"
~/opt/openEMS/venv/bin/python openems_patch.py --board A --L 31.40 --feed 5.80
~/opt/openEMS/venv/bin/python openems_patch.py --board B --L 31.54 --feed 5.90 --cut 3.13
~/opt/openEMS/venv/bin/python openems_patch.py --board B --L 37.56 --feed 7.0 --cut 3.8 --er 2.55 --tand 0.0018
python3 summarize.py "B_*"        # one line per result folder
```

Each run takes 5–10 minutes on an M-series Mac and writes `results_openems/<design>/`:
- `summary.json`: the numbers
- `results.png`: match, axial ratio and gain vs frequency, pattern cuts
- `sparams.csv`, `farfield_boresight.csv`, `pattern_f0.csv`

Useful options: `--er`, `--tand`, `--h` (material), `--Gm 100` (metal ground larger than the board), `--res 0.33` (finer mesh), `--both-ports` (board A: solve J2 separately), `--end 1e-4` (faster, slightly less accurate), `--threads 4`.

### The model

| Item | Model |
| --- | --- |
| Substrate | G × G × h box with εr and a conductivity equivalent to the loss tangent at f0 |
| Ground and patch | Copper sheet model (5.8e7 S/m, 35 µm); `--pec` for lossless |
| Probe | 50 Ω lumped port on one mesh line from ground to patch (a thin wire) |
| Mesh | 0.5 mm across the patch, thirds rule at the patch edges, at least 4 cells through the substrate, graded to λ/20 in air |
| Boundary | 8-cell PML, 70 mm from the board |
| Board A | J1 is solved; J2 follows by 90° rotation symmetry. The two are combined with an ideal hybrid (equal power, J2 lagging by 90°) |
| Far field | Near-to-far-field transform at f0 ± 30 MHz in 2.5 MHz steps |

Coordinates: x right, y up, z out of the patch, seen from the front. J1 is at (+feed, 0) and J2 at (0, +feed). Board B cuts the (−x,+y) and (+x,−y) corners, which are top-left and bottom-right in the KiCad top view.

**Edge meshing matters.** A mesh line goes a third of a cell inside each patch edge and one two thirds outside. With that rule reversed, the simulated patch acts about 0.5 mm too large and the resonance reads roughly 80 MHz low.

**Spin direction is checked two ways:** from the far-field RHCP and LHCP components, and from the raw field over time on boresight (Ey lags Ex by 90° for RHCP), using a Fourier sum that doesn't depend on openEMS's conventions. Both agree.

### Validation

Two published measured patches, both on εr 2.5 board, h 1.524 mm:

| Patch (L × W) | Measured | Simulated (resistance peak to best match) | Difference |
| --- | --- | --- | --- |
| 41.4 × 41.0 mm | 2.228 GHz | 2.208–2.217 GHz | −0.5 to −0.9 % |
| 41.4 × 68.58 mm | 2.200 GHz | 2.185–2.192 GHz | −0.4 to −0.7 % |

So the simulation reads slightly low, consistently. The hand formula gives 2.267 GHz for the first patch, 1.7 % high. The measured values were recalled from the literature and not re-read, so this is supporting evidence, not proof.

### Run list

Final designs:

| Folder | What |
| --- | --- |
| `A_L31.40_f5.80_er3.66_h1.52` | Board A, RO4350B |
| `B_L31.54_f5.90_c3.13_er3.66_h1.52` | Board B, RO4350B |
| `A_L37.38_f6.90_er2.55_h1.52` | Board A, PTFE |
| `B_L37.56_f7.00_c3.80_er2.55_h1.52` | Board B, PTFE |
| `B_L37.52_f7.00_c3.50_er2.55_h1.52_Gm100` | Board B, PTFE, tuned for and simulated on a 100 mm metal face |

Checks on them:

| Suffix | What |
| --- | --- |
| `er3.62`, `er3.70`, `er2.52`, `er2.58` | Dk off by ±1 % |
| `_Gm100` | 100 mm metal ground behind the 60 mm board |
| `_res0.33` | Finer mesh (board B, RO4350B) |
| `_bothports` | Board A with J2 solved separately instead of by symmetry |

Other runs:

| Folder | What |
| --- | --- |
| `plain_*` | Single-feed square patches: the gain survey across materials, thicknesses and ground sizes |
| `plain_L41.40_..._validation`, `..._validation2` | The validation cases above |
| `plain_L32.12_f3.46_..._thirds` | The hand-formula dimensions, resonating at 2.36 GHz instead of 2.425 GHz |
| `A_L31.25_*`, `B_L31.30_*`, `B_L31.60_*`, `B_L37.60_*` | Intermediate tuning steps |

### Tuning rules that worked

| To change | Adjust | Rate |
| --- | --- | --- |
| Resonant frequency | Patch side | about −70 MHz per +1 mm (RO4350B), −62 MHz per +1 mm (PTFE) |
| Input resistance | Feed offset d | R ≈ R_edge · sin²(π d / L); R_edge is about 240 Ω on RO4350B |
| Board B's circular polarization | Corner cut c | Best when c ≈ 0.95 · L · √(1 / (2Q)); Q ≈ 46 on the bare board, about 57 on a 100 mm ground |
| Board B's centre frequency | Patch side | The axial-ratio minimum sits about f0/(2Q) above the plain patch's resonance |

## HFSS (cross-check)

`hfss_patch.py` builds the same geometry in HFSS through PyAEDT. Its defaults are the RO4350B dimensions from openEMS. The results and what was learned are in [`HFSS_RESULTS.md`](HFSS_RESULTS.md).

Options match the openEMS script where they can: `--er`, `--tand`, `--h`, `--L`, `--feed`, `--cut`, `--Gm 100` (100 mm metal ground behind the board), plus `--pec` (lossless copper), `--delta-s` (mesh convergence target), `--target-tets` (refine to a mesh size instead), `--sma`, `--mask`, `--box` (things openEMS left out) and `--tag`. Results go to `results_hfss/<design>/` with the same folder names as `results_openems/`.

- **Use `--target-tets 40000` for the cut-corner boards.** The default ΔS 0.01 stops too early and puts the axial-ratio minimum up to 12.5 MHz low. The Student edition refuses meshes above 64,000 tetrahedra.
- `hfss_batch.py` runs the whole test list (`--mesh 40000` for the converged-mesh repeats) and `hfss_compare.py` prints HFSS next to openEMS.
- Keep `--project-dir` outside any synced folder such as OneDrive.

The antenna's parameters, the run order and the openEMS numbers to compare against are in [`../HFSS_TASK.md`](../HFSS_TASK.md).

Setup on Windows:
1. Install Ansys Electronics Desktop Student (free; needs a .edu account): <https://www.ansys.com/academic/students>
2. Install Python 3.10–3.12, then `pip install -r sim/requirements.txt`
3. Smoke test: `python -c "from ansys.aedt.core import Hfss; print('ok')"`

Then run `--board plain`, `--board A` and `--board B` and compare resonance, match, axial ratio and gain with the openEMS numbers. Agreement within about 1 % in frequency and 0.3 dB in gain would confirm the design. HFSS can also model what openEMS left out: the real via diameter and the SMA.
