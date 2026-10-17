# Changelog

## 2.2 — 2026-10-17

**Fixed**
- The source (`cradle_cq.py` v2.1) cut the cable groove *across* the tail instead of along the cable. The final v2.1 exports had already been corrected by hand, but the source had not. The source now reproduces those exports exactly (verified by boolean diff).

**Changed**
- Cable axis raised to 12.8 mm (pod mid-height), so the cable leaves the plug dead straight.
- Tail lengthened from 36 to 41 mm.
- Bell-mouth flare at both ends of the cable groove.
- **Printed screws removed.** They were too thin and stringy to hold. Replaced by bought M3 hardware, with the shell exported in two variants:
  - `shell_selftap`: Ø 2.5 pilot for M3/ST3 × 12 self-tapping screws
  - `shell_insert`: Ø 4.0 × 6.5 pocket for M3 brass heat-set inserts (OD 4.6 × 5.7) + M3 × 10 thumb screws
- Cap screw holes reduced to Ø 3.4 (M3 clearance).
- Exports now go to `print/` (STL/3MF) and `cad/step/` (STEP).

**Added**
- Production Procedure Document (`docs/PPD.md` + PDF).
- Two-sheet A4 drawing, sheet 1 at 1:1, with the USB-Blaster II drawn in place.
- Renders, `verify.py` checks for cap/shell interference, cable grip and insert wall thickness.

## 2.1 — 2026-08

Final export set as handed over: shell, cover, clamp cap, 2 printed screws.

## 2.0 — 2026-08

Through-parting-line USB slot, recessed end wall for the plug boot, re-cut snap clips (37° catch), flat tail + ribbed saddle + cap, support-free.

## 1.0 — 2026-08

First concept: clamp against the end wall, fixed USB window, needed supports.
