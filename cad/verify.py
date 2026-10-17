"""Sanity checks on the generated solids."""
import numpy as np, trimesh, cadquery as cq
import cradle_cq as M

sh = M.make_shell(); cv = M.make_cover(); cp = M.make_cap()

print("== interference ==")
inter = sh.intersect(cv)
try:
    v = inter.val().Volume()
except Exception:
    v = 0.0
print(f"shell & cover overlap : {v:.4f} mm^3   (want 0)")

# device envelope, nominal position on the floor
dev = (cq.Workplane("XY").workplane(offset=M.FLOOR + M.CLR_Z)
       .rect(M.DEV_L, M.DEV_W).extrude(M.DEV_H))
for name, part in (("shell", sh), ("cover", cv)):
    try:
        vv = part.intersect(dev).val().Volume()
    except Exception:
        vv = 0.0
    print(f"device & {name:5s} overlap: {vv:.4f} mm^3   (want 0)")

print("\n== key clearances (mm) ==")
print(f"pod clearance X/Y per side   : {M.CLR_XY}")
print(f"pod clearance Z top/bottom   : {M.CLR_Z}")
print(f"tongue/rabbet per side       : {M.FIT}")
print(f"snap barb engagement         : {M.ARM_Y1 + M.BARB - M.POCK_Y1:.2f}")
print(f"arm deflection to release    : {M.ARM_Y1 + M.BARB - M.POCK_Y1:.2f}")
print(f"material outboard of window  : {M.PAD_Y1 - M.POCK_Y1:.2f}")
print(f"clip arm  {M.ARM_W} x {M.ARM_T} x {M.ARM_LEN} (w x t x free length)")
print(f"cable bore diameter          : {2*M.BORE_R:.2f} for a {M.CABLE_D} jacket, "
      f"ribs pinch to {2*(M.BORE_R-M.GRIP_RIB):.2f}")
print(f"USB opening ({M.USB_PRESET})       : {M.USB_W} wide, z {M.USB_Z0}..{M.USB_Z1}, "
      f"recess {M.USB_RW} wide x {M.USB_RECESS_D} deep "
      f"(end wall thins to {M.WALL - M.USB_RECESS_D:.1f})")
print(f"ribbon slot                  : {M.RIB_W} x {M.RIB_H}, flared to "
      f"{M.RIB_W + 2*M.RIB_FLARE} x {M.RIB_H + 2*M.RIB_FLARE} at the mouth")
print(f"outer size (body only)       : {M.OUT_L} x {M.OUT_W} x {M.OUT_H}")

print("\n== overhang audit, as printed ==")
# rotation applied to each part to get it onto the bed
for name in ("shell", "cover", "clamp_cap", "screws_x2"):
    m = trimesh.load(f"out/{name}.stl")   # already in print orientation
    m.apply_translation([0, 0, -m.bounds[0][2]])   # drop onto the bed
    n = m.face_normals
    a = m.area_faces
    zc = m.triangles_center[:, 2]
    on_bed = zc < 0.05
    down = (n[:, 2] < -1e-6) & ~on_bed
    # angle of the face from the build plate; 0 = horizontal ceiling (worst)
    ang = np.degrees(np.arcsin(np.clip(-n[:, 2], 0, 1)))
    bad = down & (ang > 45.0)            # steeper than 45 deg overhang
    flat = down & (ang > 89.0)           # true bridges / ceilings
    print(f"{name:10s} overhang >45deg: {a[bad].sum():7.1f} mm2 "
          f"({100*a[bad].sum()/a.sum():4.1f}% of area)   "
          f"horizontal ceilings: {a[flat].sum():6.1f} mm2")
