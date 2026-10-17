# BLASTERPROOF II — Production Procedure Document

| | |
|---|---|
| **Document** | PPD-BP2-001 |
| **Product** | BLASTERPROOF II, a strain-relief enclosure for the Intel/Altera USB-Blaster II (Intel FPGA Download Cable II, PL-USB2-BLASTER) |
| **Revision** | 2.2 · 2026-10-17 |
| **Source of truth** | `cad/cradle_cq.py` (CadQuery 2.8). All STL/3MF/STEP files are generated from it. |
| **Drawing** | `docs/BLASTERPROOF-II_drawing_1to1_A4.pdf`, 2 sheets, A4, sheet 1 at 1:1 |

---

## 1. Purpose and scope

This document describes how to manufacture, assemble and inspect one BLASTERPROOF II unit using FDM 3D printing and off-the-shelf M3 hardware. It covers material choice, environmental limits, printer setup, assembly, and acceptance checks. It is written so that someone who has never seen the part can produce a good one on the first try.

## 2. The product

### 2.1 The problem it solves

The USB-Blaster II is usually left plugged into a bench PC with its USB cable hanging off one end and a 10-pin ribbon off the other. Every time the cable is pulled, bent or caught on something, that force goes straight through the USB plug into the receptacle, and from the receptacle into its solder joints on the programmer's PCB. After enough cycles the joints crack, the connection becomes intermittent, and the programmer is scrapped.

### 2.2 How it works

BLASTERPROOF II gives the cable's bending load a different path. The programmer (the "pod") sits in a closed shell, and the USB cable jacket is clamped rigidly to a tail that extends from the shell floor. A pull or bend on the cable now loads **printed plastic → shell → pod body**, never the receptacle.

![Assembled](img/assembled_iso.png)

The key geometric decisions:

- **The cable runs dead straight out of the plug.** The clamp's bore sits at 12.8 mm above the base, the pod's mid-height, which is where the plug axis is. The cable is never pre-bent by the clamp itself.
- **The clamp sits past the plug boot.** The tail is 41 mm long, so the saddle starts 28 mm beyond the end wall. That clears a moulded plug boot of up to about 26 mm. The boot never takes clamp load.
- **The clamp grips the jacket, not the conductors.** A 4.2 mm bore with thin ribs that pinch to 3.3 mm. The ribs on the saddle and on the cap interleave, so the jacket follows a slight wave and cannot slide. Bell-mouth flares at both ends stop the jacket from kinking over a sharp edge.
- **The pod is not squeezed.** It floats in a cavity with 0.6 mm clearance per side and 0.5 mm top and bottom. The enclosure locates it; it does not clamp it.
- **No tools to open.** The cover holds with four cantilever snap clips. A paperclip in any release window frees a clip.

### 2.3 Parts

![Exploded view](img/exploded.png)

| # | Part | Function |
|---|---|---|
| 1 | **Shell** | Tray that cradles the pod, with the strain-relief tail and saddle. Comes in two variants (§3). |
| 2 | **Cover** | Lid with four snap clips, a tongue that drops into the shell's lap joint, and the top half of the ribbon tunnel. |
| 3 | **Clamp cap** | Top half of the cable saddle, held down by two M3 screws. |
| — | **2 × M3 screws** (+ 2 brass inserts for variant I) | Bought hardware (§7). |

Features you will see on the parts:

| Feature | Where | Purpose |
|---|---|---|
| USB opening, 16 × 14.5 mm, runs through the parting line | Shell + cover, USB end | Clears any plug (Type-B, mini-B, micro-B) whatever height the receptacle sits at |
| End-wall recess, thinned to 1.2 mm over 22 mm | USB end | The moulded plug boot seats inside the shell so the plug goes fully home |
| Ribbon tunnel, 16 × 3.6 mm, flared to 20 × 7.6 mm | Ribbon end, split across the joint | 10-way 1.27 mm ribbon (12.7 mm wide) exits without a sharp fold |
| Open corner, 11 mm | +X/+Y corner | The status LED stays visible |
| Clip windows + fingernail scallops | Long sides | Release the clips; lift the cover |

![Device in the shell](img/device_in_shell.png)

### 2.4 Key dimensions

| | mm |
|---|---|
| Pod (USB-Blaster II datasheet body) | 63.5 × 41.4 × 20.6 |
| Pod cavity | 64.7 × 42.6 × 21.6 |
| Body, outside | 70.3 × 48.2 × 25.6 |
| Overall incl. clip bosses and tail | 111.3 × 54.2 × 25.6 |
| Walls / floor / lid | 2.8 / 2.0 / 2.0 |
| Parting line | 19.0 above base; lap joint 2.7 deep, 0.2 clearance |
| Cable axis | 12.8 above base |
| Cable bore / rib pinch | Ø 4.2 / Ø 3.3 (for a Ø 4.0 jacket) |
| Screw pitch across the cable | 16 (± 8 from the axis) |

Full dimensions and true-scale views are in the drawing (§11).

## 3. Variants

Print **one** shell, either S or I. The cover and cap are the same for both.

| | **Option S: self-tapping** | **Option I: heat-set insert** |
|---|---|---|
| Shell file | `shell_selftap` | `shell_insert` |
| Hole in saddle | Ø 2.5 pilot, 11.8 deep | Ø 4.0 × 6.5 pocket + Ø 3.2 relief below |
| Hardware | 2 × M3/ST3 × 12 pan-head self-tapping | 2 × M3 brass insert (OD 4.6, L 5.7) + 2 × M3 × 10 knurled thumb screws |
| Opening the clamp | Screwdriver | By hand, no tools |
| Re-use | About 10 cycles before the plastic thread wears | Effectively unlimited |
| Extra tool | — | Soldering iron (insert tip ideal) |
| Pick when | One-off, cable rarely changed | Production benches, cable swapped often |

![Cable clamp](img/cable_clamp.png)

The printed screws from earlier revisions have been **dropped**. At M4 with a 1.6 mm pitch they printed too thin and stringy to hold reliably.

## 4. Materials

### 4.1 Selection

| Material | Verdict | Why |
|---|---|---|
| **PETG** | **Default** | Tough rather than brittle, so the snap clips flex thousands of times. Good layer adhesion. Usable to about 70 °C. Easy to print without an enclosure. |
| **ESD-safe PETG** (carbon-loaded) | **Required inside an ESD Protected Area (EPA)** | Plain plastics are insulators and can hold a charge right next to a JTAG header. Choose a filament specified as dissipative (surface resistance roughly 10⁶–10⁹ Ω) and verify each batch (§9). |
| **ASA** | Warm, outdoor or sunny locations | About 95 °C, UV-stable, slightly stiffer clips. Needs an enclosed printer and ventilation. |
| **ABS** | Same as ASA, indoors | Same heat performance, not UV-stable. Needs an enclosure; prone to warping on the long shell. |
| **PLA** | Prototype / fit-check only | Prints easily but the clips are brittle and crack after a few openings. Softens around 55 °C: a hot car or a sunny window will warp it, and the cable clamp creeps loose. |
| PLA+, Tough PLA | Acceptable for desk use | Better clip life than PLA, same heat limit. |
| TPU, nylon | Not recommended | TPU is too soft for a strain-relief clamp. Nylon absorbs water and changes size, so the snap fit drifts. |

### 4.2 Environmental limits

Temperatures are typical values for the material family. Brands vary, so check your filament's datasheet (look for HDT or Vicat at 0.45 MPa). The "service limit" column is a conservative limit for this part, which sees continuous clamp load and spring load in the clips.

| | PLA | PETG / ESD-PETG | ABS | ASA |
|---|---|---|---|---|
| Glass transition (approx.) | 55–60 °C | 78–82 °C | ~105 °C | ~100 °C |
| **Service limit for this part** | **45 °C** | **65 °C** | **85 °C** | **85 °C** |
| Cold limit | 0 °C (brittle) | −20 °C | −20 °C | −20 °C |
| Clip fatigue life | Poor | Good | Good | Good |
| Clamp creep under load | High above 40 °C | Low | Low | Low |
| UV / sunlight | Degrades, yellows | Fair (slow yellowing) | Poor (chalks, embrittles) | **Excellent** |
| Humidity | Fine in service; store filament dry | Fine | Fine | Fine |
| Isopropyl alcohol (IPA) wipe | OK | OK | OK | OK |
| Acetone / flux removers containing acetone | Softens surface | Surface attack on long exposure | **Dissolves** | **Dissolves** |
| Flammability | Burns (not rated) | Burns (not rated) | Burns (not rated) | Burns (not rated) |
| ESD | Insulator | Insulator / **dissipative if ESD grade** | Insulator | Insulator |

Practical rules:

- **Bench in a normal lab, 15–35 °C:** PETG.
- **On an EPA production floor:** ESD-PETG. This is not optional where ESD control applies.
- **Next to a reflow oven, in a vehicle, or in direct sun:** ASA.
- **If your site requires a UL94 V-0 rated material for enclosures near mains:** none of the above qualifies. Use a flame-retardant grade (for example FR-ABS or FR-PC) and re-verify the clip fit, since FR grades are stiffer.
- **Cleaning:** IPA only. Keep acetone-based flux removers away from ABS and ASA.

## 5. Equipment and consumables

- FDM printer with at least 120 × 60 × 20 mm build volume (the shell alone is 111 × 54 mm; all three parts on one plate need about 200 × 130 mm), 0.4 mm nozzle. **Use a hardened-steel nozzle for ESD/carbon-filled filament**, which wears brass nozzles quickly.
- Filament per §4. The three parts total 35 cm³ of solid volume; at 4 perimeters / 25 % infill expect roughly **35–40 g** of PETG per unit.
- Build surface: textured PEI. For PETG on smooth PEI, apply a thin layer of glue stick as a release agent, because PETG can bond hard enough to tear the sheet.
- Calipers (to measure the cable jacket, §10), a flush cutter, a deburring tool.
- Option I only: soldering iron at 230–245 °C (PETG) with an M3 insert tip, or a conical tip.
- Option S only: Phillips #1 (or Torx T10, depending on the screw bought).

## 6. Printer setup

### 6.1 Global slicer settings

| Setting | Value | Note |
|---|---|---|
| Layer height | 0.20 mm | 0.16 mm if you want a finer cable bore |
| First layer | 0.24 mm, 50 % speed | |
| Perimeters / walls | **4** | Clip arms are 1.9 mm thick, so 4 × 0.45 mm makes them **solid**. This is the most important setting on the list. |
| Top / bottom layers | 5 / 4 | |
| Infill | 25–30 % gyroid | |
| Supports | **Off** | Nothing needs support. The shell has four 10 mm bridges over the clip windows. |
| Seam | Rear / aligned | Keep it off the clip arms if your slicer allows painting |
| Elephant-foot compensation | 0.15 mm | Keeps the cover's lid face and the shell floor square |
| Brim | Off for PETG; 5 mm on the shell for ABS/ASA | |
| XY hole compensation | 0 | Pilot and insert holes are already sized for FDM shrink |

### 6.2 Per-material settings

| | PLA | PETG | ESD-PETG | ABS | ASA |
|---|---|---|---|---|---|
| Nozzle °C | 205–215 | 235–245 | 240–255 | 245–255 | 245–260 |
| Bed °C | 60 | 75–85 | 75–85 | 100–110 | 95–105 |
| Part fan | 100 % | 30–50 % | 30–40 % | 0–15 % | 0–20 % |
| Max speed (outer wall) | 60 mm/s | 40 mm/s | 30 mm/s | 50 mm/s | 50 mm/s |
| Enclosure | No | No | No | **Yes** | **Yes** |
| Dry filament before use | — | 65 °C / 4 h if stringing | 65 °C / 4 h | 80 °C / 4 h | 80 °C / 4 h |

### 6.3 Orientation

The STL and 3MF files are **already oriented for the bed**. Drop them in and do not rotate. (The STEP files are in assembly coordinates, so you can open all parts together in CAD.)

| Part | On the bed | Watch |
|---|---|---|
| Shell | Floor down | Bridges over the clip windows should be clean; sagging there doesn't affect function |
| Cover | Lid down, clips pointing up | Clip barbs: the 37° catch face prints without support |
| Clamp cap | Flat face down, groove up | Groove and ribs crisp |

On a 200 × 130 mm or larger bed all three fit on one plate. Expect roughly 3–4 h for a full set at 0.2 mm on a typical bed-slinger.

### 6.4 First-article fit test (new printer, material or spool)

Before a batch, print one cover and one shell and check:

1. The cover presses on with four distinct clicks, using thumb force only.
2. It does not lift when you pull a corner up firmly by hand.
3. A paperclip in a window releases that clip with light pressure.

If the clips are too tight, scale nothing. Instead, change `BARB` (1.8 → 1.6) in `cradle_cq.py` and regenerate. If they're too loose, raise `BARB` to 2.0. Don't scale the meshes: that changes the pod clearance too.

## 7. Hardware (bill of materials)

| Item | Spec | Qty | Example listings |
|---|---|---|---|
| **Option S screw** | M3 (ST3) × 12 mm self-tapping, pan head, stainless | 2 | [M3 × 12 Torx pan head, 50 pcs](https://www.amazon.com/Tapping-Purpose-Stainless-Drywall-Furniture/dp/B0CKXPC78Q) · [M3 assortment, 6–30 mm](https://www.amazon.com/200pcs-Stainless-Self-tapping-Screws-Assortment/dp/B073Z5S31Y) |
| **Option I insert** | M3 brass heat-set, knurled, **OD 4.6 × L 5.7** | 2 | [M3 × 5.7 × 4.6, 140 pcs](https://www.amazon.com/Threaded-Inserts-knurled-Printing-Components/dp/B0DDWS7BTS) · [M3 × 5.7 × 4.6, 150 pcs](https://www.amazon.com/Inserts-Threaded-Printing-Knurled-Components/dp/B0FMF8CXMJ) |
| **Option I screw** | M3 × 10 mm knurled thumb screw, stainless | 2 | [M3 × 10 knurled head, 10 pcs](https://www.amazon.com/Thumb-Screws-Metric-Thread-Knurled/dp/B01H0CNLH4) |

Notes:

- **Screw length matters.** Cap thickness is 5.0 mm plus a 0.2 mm squeeze gap. A 12 mm self-tapper engages 6.8 mm of plastic. The pilot is 11.8 mm deep, so up to M3 × 16 fits; shorter than 10 mm does not hold.
- **Insert size matters.** The Ø 4.0 pocket is sized for the common "M3 × 5.7 × 4.6" insert. The short "M3 × 4 × 5" or "M3 × D5 × L4" types are a different size: they will sit proud and need the pocket changed (`INSERT_D`, `INSERT_DEPTH`).
- Thumb screw heads are typically 7–12 mm across. They may overhang the 24 mm cap slightly; that's fine.
- Listings change. If a link dies, search the spec in the "Spec" column.

## 8. Assembly procedure

### 8.1 Option I only: install the inserts (once, before assembly)

1. Heat the iron to 230–245 °C for PETG (210 °C PLA, 250 °C ABS/ASA).
2. Set the insert on the pocket, **small end down**, and hold the shell flat on the bench.
3. Press straight down with light pressure, letting heat do the work, until the insert is **flush to 0.2 mm below** the saddle face. It takes about 5–8 seconds. Don't push it below flush.
4. Remove the iron and immediately press the insert flat with a cold flat tool for a few seconds to stop it tilting.
5. Let it cool for 1 minute. Check by threading a screw in: it should run in square.

### 8.2 Assembly

1. **Pod in.** Lower the USB-Blaster II into the shell with the **USB receptacle facing the large opening and the tail**. It drops in freely.
2. **Ribbon out.** Lay the 10-pin ribbon into the half-tunnel at the far end.
3. **Cover on.** Align the cover (clips down) and press straight down until **all four clips click**. Check that the ribbon is not pinched.
4. **USB plug.** Plug the USB cable fully into the pod through the opening. The boot should sit inside the end-wall recess.
5. **Cable into the saddle.** Lay the cable straight along the tail into the saddle groove. **Do not leave a loop or tension between the plug and the saddle**: the cable should lie straight, neither pulled tight nor pushed into a hump.
6. **Cap on.** Place the clamp cap, groove down, over the cable.
7. **Screws.** Tighten both screws alternately until the cap just bottoms on the ribs.
   - Option S: run each screw in slowly the first time, because it cuts its own thread. **Snug, not tight.** If you overtighten, the thread strips.
   - Option I: finger-tight on the thumb screws is enough.
8. **Tug test** (§9).

**To open:** push a paperclip into any clip window, press the barb inward about 1 mm, and lift that corner. Release both clips on one side first, then rock the cover off. The fingernail scallop is in the middle of each long side.

## 9. Inspection and acceptance

### 9.1 Every printed part

| Check | Accept | Reject |
|---|---|---|
| Visual | Layers bonded, no gaps | Delamination, especially at clip roots |
| Clip arms | Solid, full height, barb complete | Cracked root, missing barb, stringy |
| Cable groove | Clear, ribs present on both halves | Blobs in the groove |
| Holes | Screw starts square (S) / insert flush (I) | Tilted insert, cracked saddle |
| Warp | Shell rocks < 0.3 mm on a flat surface | Visible rock |

### 9.2 Every assembled unit

| Check | Method | Accept |
|---|---|---|
| Pod fit | Shake gently | Pod may move ≤ 0.6 mm; no rattle you can hear across a bench |
| Cover | Pull each corner by hand | No corner lifts |
| Cable grip | Pull the cable firmly by hand along its axis (about 20 N, a firm tug) | Cable does not slip; the plug does not move |
| Bend relief | Bend the cable 90° just past the cap, in four directions | Plug and pod do not move relative to the shell |
| LED | Power the pod | Status LED visible through the open corner |
| Function | Detect the cable in Quartus Programmer (`jtagconfig`) | Detected |
| ESD (ESD-PETG units only) | Surface resistance meter, two points on the shell | Within the filament's specified dissipative range (typically 10⁶–10⁹ Ω) |

## 10. Things to measure and how to change them

All of these are in the parameter block at the top of `cad/cradle_cq.py`. Change one, run `python cradle_cq.py`, and every export regenerates. Then run `python verify.py` to re-check clearances.

| Parameter | Default | Change when |
|---|---|---|
| `CABLE_D` | 4.0 | **Measure your cable jacket with calipers.** This is the single most likely thing to need changing. Bore = `CABLE_D + 0.2`, ribs pinch 0.9 under that. |
| `USB_PRESET` | `"typeB"` | The opening is deliberately sized for the largest plug so it clears all of them. Units with mini-B or micro-B can use `"miniB"` / `"microB"` for a neater opening. **Check which receptacle your units have.** |
| `USB_BOOT_L` | 20.0 | Your plug's moulded boot is longer than about 26 mm. |
| `DEV_L / DEV_W / DEV_H` | 63.5 / 41.4 / 20.6 | Your measured pod differs from the datasheet |
| `CLR_XY / CLR_Z` | 0.6 / 0.5 | Pod rattles; try 0.4 / 0.3 |
| `BARB` / `ARM_T` | 1.8 / 1.9 | Clips too tight or loose (§6.4) |
| `INSERT_D / INSERT_DEPTH` | 4.0 / 6.5 | You bought a different insert size |

## 11. The drawing

`docs/BLASTERPROOF-II_drawing_1to1_A4.pdf` has two sheets:

- **Sheet 1, 1:1.** Plan view with the USB-Blaster II drawn inside in red, longitudinal section C-C through the cable axis showing how the pod, plug and cable sit, end section A-A through the USB opening, and a 100 mm scale-check bar.
- **Sheet 2, 2:1.** Cable-clamp section B-B for both variants with the hardware drawn in place, parts list, hardware list, and a bank-card scale check.

**To print at true size:** in the print dialog choose **"Actual size"** or **100 %**, not "Fit to page". Then measure the 100 mm bar on sheet 1, or lay a bank card on the box on sheet 2. If either is off, the printer scaled the page.

A correctly printed sheet 1 doubles as a **fit template**: lay a USB-Blaster II on the red outline to confirm your pod matches the datasheet before you print.

## 12. Known limitations

- `CABLE_D` = 4.0 mm is a typical USB cable jacket, not a measured one. Measure yours.
- Pod size comes from the datasheet (63.5 × 41.4 × 20.6). The 0.6 mm clearance absorbs normal variation, but clones may differ more.
- The enclosure gives mechanical protection and strain relief only. It is not sealed, not flame-rated (unless printed in an FR material), and not ESD-safe unless printed in ESD filament.

## 13. Revision history

| Rev | Date | Change |
|---|---|---|
| 1 | 2026-08 | First concept: clamp against the end wall, fixed USB window, supports needed |
| 2.0 | 2026-08 | Through-parting-line USB slot, recessed end wall, re-cut clips, flat tail + saddle, support-free |
| 2.1 | 2026-08 | Final export set |
| **2.2** | 2026-10-17 | Cable groove runs along the cable (was across); cable axis raised to 12.8 mm (pod mid-height); tail 36 → 41 mm; bell-mouth groove ends; **printed screws dropped** in favour of metal M3 hardware with two shell variants (self-tap / heat-set insert); source and exports reconciled; this PPD and the 1:1 drawing added |
