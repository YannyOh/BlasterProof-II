"""
BLASTERPROOF II  --  USB-Blaster II enclosure, parametric CadQuery model  (v2.2)

Coordinate system
-----------------
  origin  : centre of the footprint, z = 0 at the outer bottom face
  +X      : USB end          (plug goes in here, strain-relief tail sticks out)
  -X      : ribbon / IDC end (10-pin flat cable exits here)
  +Z      : up (cover side)

Parts produced
--------------
  shell       -- bottom tray, cradles the pod, carries the strain-relief tail
  cover       -- top lid with four cantilever snap clips
  clamp_cap   -- top half of the cable saddle
  (hardware)  -- 2x bought M3 screws; the shell is exported in two variants:
                   shell_selftap : 2.5 mm pilots for M3 / ST3 self-tapping screws
                   shell_insert  : 4.0 mm pockets for M3 brass heat-set inserts

v2.2 changes vs v2.1
--------------------
  * cable groove now runs ALONG the cable (X), not across it (v2.1 bug)
  * cable axis raised to the pod's mid-height (12.8 mm) so the cable leaves
    the plug dead straight; tail lengthened 36 -> 41 mm
  * bell-mouth flare at both ends of the groove so the jacket never kinks
    over a sharp edge
  * printed screws dropped (too weak) -- metal M3 hardware instead

Everything below the ==== PARAMETERS ==== line is meant to be edited.
Re-run the file after any change; it rewrites every export.
"""

import os
import math
import cadquery as cq
from cadquery import exporters

HERE = os.path.dirname(os.path.abspath(__file__))
STEP_DIR = os.path.join(HERE, "step")                         # assembly coordinates
PRINT_DIR = os.path.join(os.path.dirname(HERE), "print")      # STL + 3MF, bed-oriented
os.makedirs(STEP_DIR, exist_ok=True); os.makedirs(PRINT_DIR, exist_ok=True)

# =====================================================================
# ==== PARAMETERS =====================================================
# =====================================================================

# ---- the device itself (Intel/Altera USB-Blaster II, datasheet body) --
DEV_L = 63.5          # length, USB end -> ribbon end
DEV_W = 41.4          # width
DEV_H = 20.6          # height

# ---- fit ------------------------------------------------------------
CLR_XY = 0.60         # clearance per side around the pod, X and Y
CLR_Z = 0.50          # clearance above + below the pod
FIT = 0.20            # generic mating clearance (tongue/groove, screws)

# ---- walls ----------------------------------------------------------
WALL = 2.8            # side wall thickness
FLOOR = 2.0           # shell floor
TOPW = 2.0            # cover top
CORNER_R = 3.0        # outer vertical corner radius
INNER_R = 1.6         # cavity vertical corner radius

# ---- where the two halves meet --------------------------------------
SHELL_CAV_D = 17.0    # interior depth of the shell tray
RAB_D = 2.7           # depth of the lap joint (rabbet) in the shell rim

# ---- snap clips (4x, two per long side) -----------------------------
CLIP_X = 15.0         # +/- distance from centre along X
ARM_W = 9.0           # clip arm width
ARM_T = 1.9           # clip arm thickness  (the spring)
ARM_LEN = 13.0        # free length of the cantilever
BARB = 1.8            # how far the barb sticks out
BARB_Z0 = 6.4         # bottom of the barb (absolute Z)
BARB_RAMP = 2.6       # lead-in rise
BARB_CATCH = 2.4      # catch-face rise (bigger = easier to print, weaker hold)
PAD_OUT = 3.0         # how far the outside boss stands proud of the wall
POCKET_CLR = 1.20     # clearance in front of / behind the arm

# ---- USB end --------------------------------------------------------
# Presets for the opening.  The genuine PL-USB2-BLASTER carries a
# standard USB Type-B receptacle; clones sometimes use mini-B or micro-B.
# "typeB" is deliberately oversized so a moulded plug boot seats freely.
USB_PRESET = "typeB"          # "typeB" | "miniB" | "microB"
USB_SIZES = {                 # (opening width, recess width)
    "typeB":  (16.0, 22.0),
    "miniB":  (11.0, 17.0),
    "microB": (10.0, 16.0),
}
# The opening deliberately runs from low in the shell right up through the
# parting line, so it cannot miss the receptacle whatever height it sits at.
USB_Z0 = 4.0          # bottom of the opening
USB_Z1 = 18.5         # top of the opening (above the rabbet, below the cover)
USB_RZ0 = 3.6         # recess (thinned wall) bottom
USB_RZ1 = 19.8        # recess top -- pokes a little way into the cover
USB_RECESS_D = 1.6    # how much the end wall is thinned around the plug
USB_BOOT_L = 20.0     # how far the moulded plug boot sticks out past the wall
USB_CHAM = 1.2        # corner radius around the opening

# ---- LED --------------------------------------------------------------
LED_CORNER = True     # open the +X/+Y corner so the LED is visible any way it faces
LED_CUT = 11.0        # size of the corner bite, in X and in Y
LED_Z0 = 5.5          # bottom of the corner opening

# ---- ribbon tunnel (-X end), split across the joint ------------------
RIB_W = 16.0          # slot width  (10-way 1.27 mm ribbon is 12.7 mm)
RIB_H = 3.6           # slot height
RIB_FLARE = 2.0       # extra height at the outside mouth

# ---- strain relief: flat tail + saddle + cap + 2 screws --------------
SR_TAIL_L = 41.0      # tail length -- must clear USB_BOOT_L, see assert below
SR_TAIL_W = 24.0
SR_TAIL_T = 3.4       # tail thickness (sits flat on the bed / on the desk)
SR_SADDLE_L = 13.0    # length of the clamp block along X
SR_SADDLE_T = 9.4     # height of the clamp block above the tail
                      # (3.4 + 9.4 = 12.8 = pod mid-height = plug axis)
CABLE_D = 4.0         # USB cable jacket diameter -- MEASURE YOURS
GRIP_RIB = 0.45       # how far the grip ribs bite into the jacket
BELL_L = 2.2          # length of the bell-mouth flare at each groove end
BELL_R = 1.4          # extra radius at the mouth
SCREW_Y = 8.0         # screws sit +/- this far either side of the cable
CAP_HOLE_D = 3.4      # M3 clearance through the cap
PILOT_D = 2.50        # shell_selftap: pilot for M3 / ST3 self-tapping screws
INSERT_D = 4.0        # shell_insert: hole for a M3 heat-set insert (OD ~4.6)
INSERT_DEPTH = 6.5    # insert is 5.7 long; 0.8 mm spare for melt-back
RELIEF_D = 3.2        # below the insert, room for a long screw tip
HOLE_BOTTOM = 1.0     # all screw holes stop this far above the bed

# ---- grip scallops so you can get a fingernail in --------------------
GRIP_W = 12.0
GRIP_D = 1.3

# =====================================================================
# ==== DERIVED ========================================================
# =====================================================================

CAV_L = DEV_L + 2 * CLR_XY
CAV_W = DEV_W + 2 * CLR_XY
CAV_H = DEV_H + 2 * CLR_Z

OUT_L = CAV_L + 2 * WALL
OUT_W = CAV_W + 2 * WALL
OUT_H = FLOOR + CAV_H + TOPW

JOINT_Z = FLOOR + SHELL_CAV_D          # plane where shell meets cover
COVER_H = OUT_H - JOINT_Z

HALF_WALL = WALL / 2.0                 # lap joint splits the wall in two

X_OUT = OUT_L / 2.0                    # outer face, USB end
Y_OUT = OUT_W / 2.0
X_CAV = CAV_L / 2.0
Y_CAV = CAV_W / 2.0

USB_W, USB_RW = USB_SIZES[USB_PRESET]

ARM_Y0 = Y_CAV + 0.30      # inner face of the clip arm
ARM_Y1 = ARM_Y0 + ARM_T                # outer face of the clip arm
POCK_Y1 = Y_CAV + ARM_T + POCKET_CLR   # outboard face of the arm pocket
PAD_Y1 = Y_OUT + PAD_OUT               # outboard face of the boss
GUSSET_T = ARM_T + 0.7
WIN_Z0 = BARB_Z0 - 0.8
# top of the window = the height at which the catch face crosses the
# window's inner face, plus a little play
WIN_Z1 = (BARB_Z0 + BARB_RAMP
          + BARB_CATCH * (ARM_Y1 + BARB - POCK_Y1) / BARB + 0.20)
ARM_Z0 = JOINT_Z - ARM_LEN

SR_X0 = X_OUT                          # tail starts at the end wall
SR_X1 = X_OUT + SR_TAIL_L
SAD_X1 = SR_X1
SAD_X0 = SR_X1 - SR_SADDLE_L
SAD_XC = (SAD_X0 + SAD_X1) / 2.0
SPLIT_Z = SR_TAIL_T + SR_SADDLE_T      # cable axis height
BORE_R = CABLE_D / 2.0 + 0.10
SCREW_XY = [(SAD_XC, SCREW_Y), (SAD_XC, -SCREW_Y)]   # one each side

assert ARM_Z0 < BARB_Z0, "clip arm is shorter than the barb position"
assert PAD_Y1 - POCK_Y1 >= 2.0, "not enough material left outboard of the window"
assert ARM_Y0 + GUSSET_T < POCK_Y1, "root gusset fouls the shell"
assert ARM_Y1 + BARB - POCK_Y1 >= 0.6, "barb barely engages the window"
assert USB_Z1 < JOINT_Z, "USB opening runs into the cover"
assert 0.05 < WIN_Z1 - (BARB_Z0 + BARB_RAMP) < BARB_CATCH, \
    "window top edge is not on the catch face"
assert SAD_X0 >= X_OUT + USB_BOOT_L + 2.0, \
    "cable saddle would foul the plug boot -- increase SR_TAIL_L"
assert SR_TAIL_W / 2.0 - (SCREW_Y + INSERT_D / 2.0) >= 1.8, \
    "less than 1.8 mm of wall outside the insert pocket"
assert SCREW_Y - INSERT_D / 2.0 > BORE_R + BELL_R, "insert pocket breaks into the groove"


# =====================================================================
# ==== HELPERS ========================================================
# =====================================================================

def rrect(wp, l, w, r, h, centre_z=False):
    """rounded rectangular prism"""
    s = wp.rect(l, w).extrude(h)
    if r > 0:
        s = s.edges("|Z").fillet(r)
    return s


def outer_block(z0, z1):
    return (cq.Workplane("XY").workplane(offset=z0)
            .rect(OUT_L, OUT_W).extrude(z1 - z0)
            .edges("|Z").fillet(CORNER_R))


def cavity_solid(z0, z1):
    return (cq.Workplane("XY").workplane(offset=z0)
            .rect(CAV_L, CAV_W).extrude(z1 - z0)
            .edges("|Z").fillet(INNER_R))


def barb_profile(sign):
    """Cross-section of one snap barb, in the YZ plane, for +Y or -Y side."""
    y0 = ARM_Y1 * sign
    y1 = (ARM_Y1 + BARB) * sign
    pts = [
        (y0, BARB_Z0),
        (y1, BARB_Z0 + BARB_RAMP),
        (y0, BARB_Z0 + BARB_RAMP + BARB_CATCH),
    ]
    return (cq.Workplane("YZ")
            .polyline(pts).close()
            .extrude(ARM_W / 2.0, both=True))


def clip_positions():
    for sx in (-1, 1):
        for sy in (-1, 1):
            yield sx * CLIP_X, sy


def usb_cut():
    """Opening + outside recess, as one cutting solid. Cut from BOTH halves."""
    cut = (cq.Workplane("YZ").workplane(offset=X_CAV - 3.0)
           .center(0, (USB_Z0 + USB_Z1) / 2.0)
           .rect(USB_W, USB_Z1 - USB_Z0).extrude(WALL + 7.0)
           .edges("|X").fillet(USB_CHAM))
    rec = (cq.Workplane("YZ").workplane(offset=X_OUT - USB_RECESS_D)
           .center(0, (USB_RZ0 + USB_RZ1) / 2.0)
           .rect(USB_RW, USB_RZ1 - USB_RZ0).extrude(USB_RECESS_D + 5.0)
           .edges("|X").fillet(2.0))
    return cut.union(rec)


def ribbon_cut():
    """Flat-cable slot straddling the joint plane, flared at the mouth."""
    zc = JOINT_Z
    inner = (cq.Workplane("YZ").workplane(offset=-(X_CAV + 2.0))
             .center(0, zc).rect(RIB_W, RIB_H)
             .workplane(offset=WALL + 2.0)
             .rect(RIB_W + 2 * RIB_FLARE, RIB_H + 2 * RIB_FLARE)
             .loft()
             .translate((0, 0, 0)))
    straight = (cq.Workplane("YZ").workplane(offset=-(X_CAV + 6.0))
                .center(0, zc).rect(RIB_W, RIB_H).extrude(6.0))
    return inner.union(straight)


def led_cut():
    if not LED_CORNER:
        return None
    return (cq.Workplane("XY").workplane(offset=LED_Z0)
            .moveTo(X_OUT + 4, Y_OUT + 4)
            .lineTo(X_OUT + 4 - LED_CUT - 4, Y_OUT + 4)
            .lineTo(X_OUT + 4, Y_OUT + 4 - LED_CUT - 4)
            .close()
            .extrude(OUT_H))


def grip_cut():
    """Fingernail scallops at the joint, centred on each long side."""
    c = cq.Workplane("XY")
    for sy in (-1, 1):
        c = c.union(
            cq.Workplane("XY").workplane(offset=JOINT_Z - 3.0)
            .center(0, sy * (Y_OUT + 8.0 - GRIP_D))
            .rect(GRIP_W, 16.0).extrude(6.0)
            .edges("|Z").fillet(3.0)
        )
    return c


def cable_groove(z_axis, r):
    """Cable bore along X through the saddle, with a bell mouth at each end."""
    straight = (cq.Workplane("YZ").workplane(offset=SAD_X0 - 1.0)
                .center(0, z_axis).circle(r).extrude(SR_SADDLE_L + 2.0))
    g = straight
    for x_face, d in ((SAD_X0, +1), (SAD_X1, -1)):
        # cone: wide at the face, BORE size BELL_L inside
        bell = (cq.Workplane("YZ").workplane(offset=x_face - d * 0.5)
                .center(0, z_axis).circle(r + BELL_R + 0.5 * BELL_R / BELL_L)
                .workplane(offset=d * (BELL_L + 0.5)).circle(r).loft())
        g = g.union(bell)
    return g


def grip_ribs(z_axis, dxs, keep_below):
    """Thin rings left standing inside the bore; keep the half on our side."""
    out = None
    for dx in dxs:
        ring = (cq.Workplane("YZ").workplane(offset=SAD_XC + dx - 0.7)
                .center(0, z_axis).circle(BORE_R).circle(BORE_R - GRIP_RIB)
                .extrude(1.4))
        half = (cq.Workplane("XY").workplane(offset=z_axis - (10.0 if keep_below else 0.0))
                .center(SAD_XC + dx, 0).rect(2.0, SR_TAIL_W).extrude(10.0))
        r = ring.intersect(half)
        out = r if out is None else out.union(r)
    return out


# =====================================================================
# ==== SHELL ==========================================================
# =====================================================================

def make_shell(hardware="selftap"):
    s = outer_block(0, JOINT_Z)

    # clip bosses on the outside
    for x, sy in clip_positions():
        s = s.union(
            cq.Workplane("XY")
            .center(x, sy * (Y_OUT + PAD_OUT / 2.0 - 0.01))
            .rect(ARM_W + 8.0, PAD_OUT + 0.02).extrude(JOINT_Z)
            .edges("|Z").fillet(1.0)
        )

    # strain-relief tail (a flat extension of the floor)
    tail = (cq.Workplane("XY")
            .center((SR_X0 + SR_X1) / 2.0 - 3.0, 0)
            .rect(SR_TAIL_L + 6.0, SR_TAIL_W).extrude(SR_TAIL_T)
            .edges("|Z").fillet(4.0))
    saddle = (cq.Workplane("XY").workplane(offset=SR_TAIL_T)
              .center(SAD_XC, 0)
              .rect(SR_SADDLE_L, SR_TAIL_W).extrude(SR_SADDLE_T)
              .edges("|Z").fillet(3.0))
    s = s.union(tail).union(saddle)

    # main cavity
    s = s.cut(cavity_solid(FLOOR, JOINT_Z + 1.0))

    # rabbet: take the inner half of the wall down, cover's tongue fills it
    rab = (cq.Workplane("XY").workplane(offset=JOINT_Z - RAB_D)
           .rect(CAV_L + WALL, CAV_W + WALL).extrude(RAB_D + 1.0)
           .edges("|Z").fillet(INNER_R + HALF_WALL))
    s = s.cut(rab)

    # arm pockets + release windows
    for x, sy in clip_positions():
        pocket = (cq.Workplane("XY").workplane(offset=ARM_Z0 - 1.0)
                  .center(x, sy * (Y_CAV + (POCK_Y1 - Y_CAV) / 2.0))
                  .rect(ARM_W + 1.6, POCK_Y1 - Y_CAV)
                  .extrude(JOINT_Z - ARM_Z0 + 2.0))
        window = (cq.Workplane("XY").workplane(offset=WIN_Z0)
                  .center(x, sy * (PAD_Y1 + POCK_Y1) / 2.0)
                  .rect(ARM_W + 1.2, PAD_Y1 - POCK_Y1 + 2.0)
                  .extrude(WIN_Z1 - WIN_Z0))
        s = s.cut(pocket).cut(window)

    # openings
    s = s.cut(usb_cut()).cut(ribbon_cut()).cut(grip_cut())
    lc = led_cut()
    if lc is not None:
        s = s.cut(lc)

    # cable groove along X, lower half lives in the saddle
    s = s.cut(cable_groove(SPLIT_Z, BORE_R))
    s = s.union(grip_ribs(SPLIT_Z, (-4.0, 0.0, 4.0), keep_below=True))

    # screw holes for bought M3 hardware
    for (px, py) in SCREW_XY:
        if hardware == "selftap":
            s = s.cut(cq.Workplane("XY").workplane(offset=HOLE_BOTTOM)
                      .center(px, py).circle(PILOT_D / 2.0)
                      .extrude(SPLIT_Z - HOLE_BOTTOM + 0.01))
        elif hardware == "insert":
            s = s.cut(cq.Workplane("XY").workplane(offset=SPLIT_Z - INSERT_DEPTH)
                      .center(px, py).circle(INSERT_D / 2.0)
                      .extrude(INSERT_DEPTH + 0.01))
            s = s.cut(cq.Workplane("XY").workplane(offset=HOLE_BOTTOM)
                      .center(px, py).circle(RELIEF_D / 2.0)
                      .extrude(SPLIT_Z - INSERT_DEPTH - HOLE_BOTTOM + 0.01))
        else:
            raise ValueError(hardware)

    # break the sharp outer edges a little
    try:
        s = s.edges(">Z").chamfer(0.4)
    except Exception:
        pass
    return s


# =====================================================================
# ==== COVER ==========================================================
# =====================================================================

def make_cover():
    c = outer_block(JOINT_Z, OUT_H)

    # tongue that drops into the shell's rabbet
    tongue = (cq.Workplane("XY").workplane(offset=JOINT_Z - RAB_D + FIT)
              .rect(CAV_L + WALL - 2 * FIT, CAV_W + WALL - 2 * FIT)
              .extrude(RAB_D - FIT)
              .edges("|Z").fillet(INNER_R + HALF_WALL))
    c = c.union(tongue)

    # hollow out the cover
    c = c.cut(cavity_solid(JOINT_Z - RAB_D - 1.0, OUT_H - TOPW))

    # clip arms
    for x, sy in clip_positions():
        arm = (cq.Workplane("XY").workplane(offset=ARM_Z0)
               .center(x, sy * (ARM_Y0 + ARM_T / 2.0))
               .rect(ARM_W, ARM_T).extrude(JOINT_Z - ARM_Z0))
        # fillet at the root so it does not snap off there
        arm = arm.union(
            cq.Workplane("XY").workplane(offset=JOINT_Z - 3.0)
            .center(x, sy * (ARM_Y0 + GUSSET_T / 2.0))
            .rect(ARM_W, GUSSET_T).extrude(3.0))
        barb = barb_profile(sy).translate((x, 0, 0))
        c = c.union(arm).union(barb)

    # openings that are shared with the shell
    c = c.cut(ribbon_cut()).cut(grip_cut()).cut(usb_cut())
    # clear the tongue under the ribbon slot so no thin sliver is left
    c = c.cut(cq.Workplane("XY").workplane(offset=JOINT_Z - RAB_D - 1.0)
              .center(-(X_CAV + 4.0), 0).rect(12.0, RIB_W)
              .extrude(RAB_D + 1.0 + RIB_H / 2.0))
    lc = led_cut()
    if lc is not None:
        c = c.cut(lc)
    return c


# =====================================================================
# ==== CLAMP CAP ======================================================
# =====================================================================

def make_cap():
    cap_t = 5.0
    cap = (cq.Workplane("XY").workplane(offset=SPLIT_Z + FIT)
           .center(SAD_XC, 0)
           .rect(SR_SADDLE_L, SR_TAIL_W).extrude(cap_t)
           .edges("|Z").fillet(3.0))

    # upper half of the bore -- same axis as the saddle, so with the 0.2 mm
    # gap closed by the screws the two halves pinch the jacket
    cap = cap.cut(cable_groove(SPLIT_Z, BORE_R))
    cap = cap.union(grip_ribs(SPLIT_Z, (-2.25, 2.25), keep_below=False)
                    .intersect(cq.Workplane("XY").workplane(offset=SPLIT_Z + FIT)
                               .center(SAD_XC, 0).rect(SR_SADDLE_L, SR_TAIL_W).extrude(cap_t)))

    for (px, py) in SCREW_XY:
        cap = cap.cut(cq.Workplane("XY").workplane(offset=SPLIT_Z + FIT - 1)
                      .center(px, py).circle(CAP_HOLE_D / 2.0)
                      .extrude(cap_t + 2))
    return cap.translate((0, 0, -(SPLIT_Z + FIT)))


# =====================================================================
# ==== EXPORT =========================================================
# =====================================================================

# Which way each part wants to sit on the bed.  STEP keeps assembly
# coordinates; STL and 3MF come out already oriented for printing.
FLIP = {"cover": True, "clamp_cap": True,
        "shell_selftap": False, "shell_insert": False}


def to_print_orientation(obj, name):
    if not FLIP.get(name):
        o = obj
    else:
        o = obj.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = o.val().BoundingBox()
    return o.translate((0, 0, -bb.zmin))


def export(obj, name):
    paths = []
    p = os.path.join(STEP_DIR, f"{name}.step")
    exporters.export(obj.val(), p); paths.append(p)
    mesh = to_print_orientation(obj, name).val()
    for ext in ("stl", "3mf"):
        p = os.path.join(PRINT_DIR, f"{name}.{ext}")
        try:
            exporters.export(mesh, p, tolerance=0.008, angularTolerance=0.1)
            paths.append(p)
        except Exception as e:
            print(f"  !! {ext} failed for {name}: {e}")
    return paths


if __name__ == "__main__":
    parts = {}
    print("shell (self-tap) ..."); parts["shell_selftap"] = make_shell("selftap")
    print("shell (insert)   ..."); parts["shell_insert"] = make_shell("insert")
    print("cover  ...");            parts["cover"] = make_cover()
    print("clamp_cap ...");         parts["clamp_cap"] = make_cap()

    for n, p in parts.items():
        bb = p.val().BoundingBox()
        print(f"{n:14s} {bb.xlen:6.2f} x {bb.ylen:6.2f} x {bb.zlen:6.2f} mm"
              f"   vol {p.val().Volume()/1000:7.2f} cm3")
        export(p, n)
    print("done ->", STEP_DIR, "and", PRINT_DIR)
