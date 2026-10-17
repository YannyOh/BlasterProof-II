"""Tessellate every part in ASSEMBLY coordinates (STEP frame) to trimesh, cached as .npz."""
import os, sys, numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "cad"))
import cadquery as cq, cradle_cq as M
CACHE = os.path.join(ROOT, "build"); os.makedirs(CACHE, exist_ok=True)

def tess(obj, tol=0.02):
    v, f = obj.val().tessellate(tol, 0.15)
    return trimesh.Trimesh(np.array([(p.x, p.y, p.z) for p in v]), np.array(f), process=True)

def device():
    # USB-Blaster II datasheet envelope sitting on the cavity floor, centred
    return (cq.Workplane("XY").workplane(offset=M.FLOOR + M.CLR_Z)
            .rect(M.DEV_L, M.DEV_W).extrude(M.DEV_H).edges("|Z").fillet(2.0))

def cable():
    x0 = M.X_OUT - 2.0
    return (cq.Workplane("YZ").workplane(offset=x0).center(0, M.SPLIT_Z)
            .circle(M.CABLE_D / 2.0).extrude(M.SR_X1 - x0 + 25))

def plug():
    # generic moulded USB plug boot, 20 mm long, 11 x 9 mm
    return (cq.Workplane("YZ").workplane(offset=M.X_OUT - 2.0).center(0, M.SPLIT_Z)
            .rect(11, 9).extrude(M.USB_BOOT_L + 2.0).edges("|X").fillet(2.5))

def load():
    p = os.path.join(CACHE, "asm.npz")
    if os.path.exists(p):
        d = np.load(p, allow_pickle=True)
        return {k: trimesh.Trimesh(*d[k]) for k in d.files}
    parts = {
        "shell": M.make_shell("selftap"),
        "shell_insert": M.make_shell("insert"),
        "cover": M.make_cover(),
        "cap": M.make_cap().translate((0, 0, M.SPLIT_Z + M.FIT)),
        "device": device(), "cable": cable(), "plug": plug(),
    }
    ms = {k: tess(v) for k, v in parts.items()}
    np.savez(p, **{k: np.array([m.vertices, m.faces], dtype=object) for k, m in ms.items()})
    return ms
