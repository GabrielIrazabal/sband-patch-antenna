# Instructions for Claude

You are picking up an S-band patch antenna design for Stanford Student Space Initiative's 1U CubeSat. Read `README.md` for the requirements, results and open items, and `sim/README.md` for how the simulations work. This file says what to do and how to work with the user.

## The user

Gabriel is responsible for the S-band antenna requirements and rev-1 design.

- Explain RF concepts simply and briefly, in plain language.
- Give neutral, numeric comparisons. Don't exaggerate one option's advantages or disadvantages.
- When you recommend something, say why in one or two sentences. Say how sure you are.
- **Never send messages on the user's behalf** (Slack, email or anything else). Draft them and let Gabriel send.
- Teammates: the TT&C lead (TT&C board, radio, VNA). Mission Control (ground station and dish).

## Where things stand

- Five boards are designed, simulated in openEMS and exported as Gerbers: dual-feed (A) and cut-corner (B), each on RO4350B and on JLC's PTFE (ZYF255DA), plus a cut-corner PTFE board tuned for a 100 mm metal face. Each has −0.3 / +0.3 mm size variants. All pass DRC.
- Everything meets the requirements except gain. RO4350B gives 5.6–6.3 dBic; the requirement is 6.5 dBic, ideally 7+. PTFE gives 6.3–7.05 dBic depending on the ground behind it.
- The simulation reads about 0.4–0.9 % low against two published measured patches, so real boards may land 10–20 MHz high and the +0.3 mm variants may be the best ones.
- **Current best option in simulation:** board B (cut corners) on PTFE, tuned for a 100 mm metal face (`B_cutcorner_RHCP_PTFE_face100`: patch 37.52 mm, feed 7.00 mm, cut 3.50 mm). It gives 6.8–7.05 dBic. Once board A's 0.3–0.5 dB hybrid loss is counted, B is about 0.5 dB ahead on gain and needs one cable instead of two. Its weak point is polarization that is sensitive to Dk and mounting. Gabriel has not decided the material or the board.
- Nothing has been ordered or built. HFSS has not been run.

## What's next, roughly in order

1. **Help Gabriel settle the open items in `README.md`.** The material choice and whether 6.5 dBic is a hard requirement come first. Draft the questions for the TT&C lead and Mission Control; don't send them.
2. **Cross-check in HFSS** if this machine is Windows with Ansys Electronics Desktop Student.
   - Ask before installing anything, unless Gabriel's prompt already says to go ahead.
   - If Gabriel asks for an overnight run, follow [`HFSS_TASK.md`](HFSS_TASK.md).
   - `sim/hfss_patch.py` has never been run. Fix PyAEDT API mismatches against the installed version's docs, but keep the geometry, coordinates and conventions.
   - Run boards A and B and compare with the openEMS numbers in `README.md`. Report differences plainly. If HFSS disagrees by more than about 1 % in frequency, say so and work out which model is closer to the real board (HFSS can model the real via diameter and the SMA).
3. **If the carrier frequency, mounting or material changes,** re-tune with `sim/openems_patch.py` (macOS/Linux) using the tuning rules in `sim/README.md`. Then update `BOARDS` in `kicad/generate_boards.py` and rerun it with `--variants -0.3 0.3 --gerbers`.
4. **Before an order:** confirm every board reports `DRC clean`, look at the renders in `docs/renders/`, and walk Gabriel through the JLC settings in `README.md`. Gabriel places the order.
5. **Keep `README.md` current**: the results tables, the status table and the open items. Commit and push only when Gabriel asks.

## Overnight HFSS run

Everything for this is in [`HFSS_TASK.md`](HFSS_TASK.md): the antenna's parameters, the tests in order, the openEMS numbers to compare against, and what to hand back. Follow that file.

## This repo is public

- Don't commit personal details, private links, credentials or anything from private team channels.
- Commit with a GitHub noreply address (`git config user.email`), not a personal email. Check before the first commit on a new machine.

## Facts that are easy to get wrong

- **Use Dk 3.66** for RO4350B, not JLC's 3.48 process value. PTFE ZYF255DA uses JLC's listed 2.55.
- **Don't trust the hand formulas for final sizes.** They read about 2.7 % high in frequency here (32.12 mm by formula, 31.40 mm by simulation).
- **Coordinates.** Simulation: x right, y up, z out of the patch, viewed from the front. KiCad's top view has y pointing down. J1 is on +x, J2 is on +y (up). Board B's cut corners are KiCad top-left/bottom-right = simulation (−x,+y)/(+x,−y).
- **Polarization hand.** RHCP means the wave leaving the satellite, IEEE convention: counter-clockwise rotation seen from in front of the antenna. The dish reflection flips the hand of the ground feed, so don't "correct" for it here. Board B's hand is confirmed in simulation two independent ways.
- **Board A's simulated axial ratio is idealized.** It assumes a perfect hybrid, so the real value depends on the hybrid chosen. Its gain figures also exclude the hybrid's 0.3–0.5 dB loss.
- **The ground behind the antenna changes the result.** A 100 mm metal face adds about 0.5 dB of gain, narrows the match bandwidth and detunes board B's circular polarization. Board B must be re-tuned for the real mounting.
- **Center frequency.** 2.425 GHz is an assumption, not a confirmed carrier.
- **Connectors.** Surface-mount vertical SMA (Würth 60312102114405, 8.1 mm square courtyard). On board A, if the feed offset drops below 5.8 mm, `generate_boards.py` moves both SMAs out to 8.2 mm and adds short bottom-layer traces, which the simulations don't model.
- **JLC.** High-frequency materials are 2-layer only, which is why board A has no hybrid on it.
- **openEMS mesh.** Keep the thirds rule at the patch edges (see `sim/README.md`). Getting it backwards shifts the resonance by about 80 MHz.
