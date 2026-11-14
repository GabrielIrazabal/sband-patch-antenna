# HFSS task: rebuild the patch antenna in Ansys and test it

Claude: this file is the whole job. Build the antenna below in Ansys HFSS, run the tests in order, and write the results to `sim/HFSS_RESULTS.md`. Work through the list without stopping to ask questions.

The antenna was designed and tuned in openEMS on a Mac. HFSS has never been run on it. Your job is an independent check: does HFSS give the same numbers?

## 1. What the antenna is

A right-hand circularly polarized patch antenna for the S-band link of a 1U CubeSat. It is a single circuit board: a copper square (the patch) on the front, solid copper (the ground) on the back, fed by one pin from a connector on the back. Two clipped corners on the patch make it circularly polarized.

### Requirements

| Requirement | Target |
| --- | --- |
| Centre frequency | 2.425 GHz (assumed; the exact carrier is not confirmed) |
| Channel | 20 MHz: 2.415 to 2.435 GHz |
| Match | Return loss at least 10 dB (S11 at most −10 dB) across the channel, 50 Ω |
| Polarization | Right-hand circular. Aim for axial ratio at most 3 dB across the channel |
| Gain | At least 6.5 dBic RHCP, ideally 7 or more |
| Half-power beamwidth | At least 60° |
| Power | At least 3 W |
| Temperature | −40 to +85 °C |
| Connector | SMA |

### Parameters of the antenna to build (the best option so far)

Board B, cut corners, on PTFE, tuned for mounting on a 100 mm metal satellite face. KiCad name: `B_cutcorner_RHCP_PTFE_face100`.

| Parameter | Value |
| --- | --- |
| Board (substrate) | 60 × 60 mm, 1.524 mm thick |
| Board material | JLC ZYF255DA PTFE: εr 2.55, loss tangent 0.0018 |
| Patch | Square, 37.52 mm side, centred on the board, on the top face (z = 1.524 mm) |
| Clipped corners | Two opposite corners cut at 45°, 3.50 mm along each edge |
| Which corners | (−x, +y) and (+x, −y) |
| Ground | Copper over the whole back of the board (z = 0) |
| Satellite face | The ground extended to a 100 × 100 mm metal sheet, centred, at z = 0 |
| Feed position | x = +7.00 mm, y = 0, measured from the patch centre |
| Feed pin | 0.25 mm radius (a 0.5 mm plated via), from ground to patch |
| Ground clearance around the pin | 0.8 mm radius |
| Port | 50 Ω lumped port across the ring between pin and ground |
| Copper | 35 µm, 5.8e7 S/m, on patch and ground |
| Connector (not in the openEMS model) | Würth WR-SMA 60312102114405, surface mount, on the back |

### Coordinates and polarization

- x is right, y is up, z points out of the patch, looking at the patch from the front.
- KiCad's top view has y pointing down, so the clipped corners are KiCad top-left and bottom-right.
- RHCP is the IEEE convention for the wave leaving the patch: counter-clockwise rotation seen from in front of the antenna.
- The antenna must come out RHCP. If HFSS says LHCP, the coordinates are mirrored; fix that before anything else.

### Simulation settings

| Setting | Value |
| --- | --- |
| Adaptive solve frequency | 2.425 GHz |
| Convergence | Max ΔS 0.01, up to 20 passes |
| S-parameter sweep | 2.20 to 2.65 GHz, interpolating |
| Far-field sweep | 2.395 to 2.455 GHz in 2.5 MHz steps, fields saved |
| Air box | A quarter wavelength (31 mm) beyond the metal on every side, radiation boundary |
| Far-field outputs | RHCP and LHCP realized gain and axial ratio straight ahead (θ = 0); gain cuts at φ = 0° and 90° |

## 2. How to build it

`sim/hfss_patch.py` builds, solves and reports all of the above through PyAEDT. It has never been run, so expect to fix some PyAEDT call names against the installed version. Keep the geometry, coordinates and folder naming.

```
pip install -r sim/requirements.txt
python sim/hfss_patch.py --board B --L 37.52 --feed 7.00 --cut 3.50 --er 2.55 --tand 0.0018 --Gm 100
```

Options: `--L` patch side, `--feed` feed offset, `--cut` corner cut, `--h` thickness, `--er` and `--tand` material, `--Gm` metal ground side, `--pec` lossless copper, `--delta-s` convergence, `--tag` name suffix. Results go to `sim/results_hfss/<design>/`. The HFSS project is `sim/patch.aedt`.

If the script can't be made to work, build the same geometry by hand in HFSS from the table above.

## 3. Tests, in order

### Test 0: check the script on simple cases

```
python sim/hfss_patch.py --board plain
python sim/hfss_patch.py --board A
```

- The plain patch (RO4350B, 31.40 mm, feed 5.80 mm) should resonate near 2.4245 GHz, with about 36.5 MHz of −10 dB bandwidth and 5.8 dBi.
- Board A (two feeds, the second lagging by 90°) must report RHCP.

### Test 1: the best option

The command in section 2. Compare with openEMS:

| Quantity | openEMS |
| --- | --- |
| Best match | −33 dB at 2.4505 GHz |
| Worst S11 in the channel | −12.8 dB |
| −10 dB bandwidth | 63.5 MHz |
| Axial ratio minimum | 0.18 dB at 2.425 GHz |
| Worst axial ratio in the channel | 3.9 dB |
| 3 dB axial ratio bandwidth | 12.5 MHz |
| RHCP gain in the channel | 6.80 to 7.05 dBic |
| Directivity / radiation efficiency | 7.81 dBi / 88 % |
| Half-power beamwidth | 74° |

### Test 2: stress the best option

Each is the Test 1 command with one change.

| Test | Change | What openEMS suggests |
| --- | --- | --- |
| Finer mesh | `--delta-s 0.005 --tag fine` | Same as Test 1 within about 2 MHz |
| Material 1 % low / high | `--er 2.52`, `--er 2.58` | Axial ratio minimum moves about ±11 MHz; worst in channel 6.6 to 6.8 dB |
| Patch 0.3 mm smaller / larger | `--L 37.22`, `--L 37.82` | About −62 MHz per +1 mm |
| Bare board, no satellite face | `--L 37.56 --cut 3.80`, no `--Gm` | 6.12 to 6.30 dBic; axial ratio 0.27 dB at centre, 3.4 dB at channel edges |
| Lossless copper | `--pec --tag pec` | Shows how much gain the copper costs |
| Temperature drift | `--er 2.542`, `--er 2.558` (±0.3 %, an assumed figure; this PTFE's real temperature coefficient is not known) | Not simulated in openEMS |

### Test 3: what openEMS left out

Add these to the best option one at a time. Report the change in frequency, match, axial ratio and gain.

1. The SMA: a short 50 Ω coax below the ground with a wave port, replacing the lumped port.
2. Solder mask on the top of the board, everywhere except over the patch.
3. A 100 × 100 × 100 mm metal box behind the board in place of the flat sheet.

### Test 4: the other four boards

All are 60 × 60 × 1.524 mm. RO4350B is εr 3.66, loss tangent 0.0031. Board A has two feeds, at (+feed, 0) and (0, +feed), driven with equal power and the second lagging by 90°.

| Board | Material | Patch | Feed | Cut | openEMS: worst S11 | −10 dB BW | RHCP gain bare / on 100 mm face | Axial ratio centre / edges |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | RO4350B | 31.40 | 5.80 | none | −13.5 dB | 35.5 MHz | 5.6–5.8 / 5.9–6.0 dBic | set by the hybrid |
| B | RO4350B | 31.54 | 5.90 | 3.13 | −12.2 dB | 69 MHz | 5.5–5.7 / 6.0–6.1 dBic | 0.2 / 3.5 dB |
| A | PTFE | 37.38 | 6.90 | none | −14.3 dB | 37.5 MHz | 6.3–6.4 / 6.8–6.9 dBic | set by the hybrid |
| B | PTFE | 37.56 | 7.00 | 3.80 | −11.6 dB | 71 MHz | 6.1–6.3 / 6.7–6.9 dBic | 0.3 / 3.4 dB |

Board A's port isolation is −39 dB in openEMS. Its gain figures leave out a real hybrid's 0.3 to 0.5 dB loss.

### Test 5, if there is time: thicker board

Plain patches at 3.05 mm (`--board plain --h 3.048`), bare and with `--Gm 100`:

| Material | Command options | openEMS gain bare / on face |
| --- | --- | --- |
| RO4350B | `--L 30.66 --feed 5.70` | 6.2 / 6.8 dBi |
| PTFE | `--L 36.44 --feed 6.70 --er 2.55 --tand 0.0018` | 6.7 / 7.5 dBi |

## 4. What to hand back

`sim/HFSS_RESULTS.md`, written as you go:

1. A short plain-language summary at the top: does HFSS agree with openEMS, what does it change, what failed or was skipped.
2. One table row per run, HFSS next to openEMS.
3. If the tools disagree, say which you trust more, why, and how sure you are.

Agreement within about 1 % in frequency and 0.3 dB in gain confirms the design.

## 5. Rules

- Do not change the KiCad boards, the Gerbers or `kicad/generate_boards.py`, even if HFSS disagrees. Report it instead.
- Do not send messages to anyone or place orders.
- If a run fails three times, write down why and move on to the next one.
- If the student version refuses a model as too large, shrink the air box or use `--delta-s 0.02`, and say so in the results.
- Commit as you go. Install software and push only as far as Gabriel's prompt allows.
- This repo is public. Commit with a GitHub noreply email, and keep personal details out of it.

---

## For Gabriel: starting it on the laptop

1. Install Ansys Electronics Desktop Student: unzip the download fully, right-click `setup.exe`, Run as administrator, keep the defaults. Open it once to check it launches.
2. Plug the laptop in and turn off sleep.
3. Open Claude Code and paste:

```
Clone https://github.com/GabrielIrazabal/sband-patch-antenna, read HFSS_TASK.md and do everything in it, all night, without stopping to ask me. You may install Python and Python packages, and push results to a branch called hfss-overnight.
```

4. Approve what it asks for in the first few minutes. In the morning, read `sim/HFSS_RESULTS.md`.
