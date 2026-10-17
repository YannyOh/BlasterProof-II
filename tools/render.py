"""Z-buffered orthographic renders with image-space outlines (README / PPD figures)."""
import os, sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import assembly_meshes as A
ROOT = os.path.dirname(HERE); IMG = os.path.join(ROOT, "docs", "img"); os.makedirs(IMG, exist_ok=True)

COL = {"shell": "#2f6fb0", "shell_insert": "#2f6fb0", "cover": "#e0902e", "cap": "#3f9a52",
       "device": "#3b3b3b", "cable": "#1c1c1c", "plug": "#5a5a5a"}

def rot(az, el):
    az, el = np.radians(az), -np.radians(el)
    Rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, np.cos(el), np.sin(el)], [0, -np.sin(el), np.cos(el)]])
    return Rx @ Rz   # view dir = +Y' (into screen), screen x = X', screen up = Z'

def render(items, az=None, el=None, px_per_mm=9, pad=6, alpha=None, R=None, lineart=False, extent=False):
    if R is None:
        R = rot(az, el)
    R = np.asarray(R, float)
    L = np.array([-0.35, -0.75, 0.6]); L /= np.linalg.norm(L)  # toward the light, camera space (-Y = toward viewer)
    tv = [((m.vertices + off) @ R.T) for _, m, off in items]
    allv = np.vstack(tv)
    x0, z0 = allv[:, 0].min() - pad, allv[:, 2].min() - pad
    W = int((allv[:, 0].max() + pad - x0) * px_per_mm); H = int((allv[:, 2].max() + pad - z0) * px_per_mm)
    depth = np.full((H, W), np.inf); rgb = np.ones((H, W, 3)); oid = np.full((H, W), -1); nrm = np.zeros((H, W, 3))
    for k, ((name, m, off), v) in enumerate(zip(items, tv)):
        base = np.array(matplotlib.colors.to_rgb(COL[name]))
        fn = m.face_normals @ R.T
        sx = (v[:, 0] - x0) * px_per_mm; sy = (H - 1) - (v[:, 2] - z0) * px_per_mm; sd = v[:, 1]
        for f, n in zip(m.faces, fn):
            if n[1] > 0.05: continue                     # back-facing
            xs, ys, ds = sx[f], sy[f], sd[f]
            minx, maxx = int(max(0, np.floor(xs.min()))), int(min(W - 1, np.ceil(xs.max())))
            miny, maxy = int(max(0, np.floor(ys.min()))), int(min(H - 1, np.ceil(ys.max())))
            if maxx < minx or maxy < miny: continue
            X, Y = np.meshgrid(np.arange(minx, maxx + 1) + 0.5, np.arange(miny, maxy + 1) + 0.5)
            d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
            if abs(d) < 1e-12: continue
            l0 = ((ys[1] - ys[2]) * (X - xs[2]) + (xs[2] - xs[1]) * (Y - ys[2])) / d
            l1 = ((ys[2] - ys[0]) * (X - xs[2]) + (xs[0] - xs[2]) * (Y - ys[2])) / d
            l2 = 1 - l0 - l1
            ins = (l0 >= -1e-4) & (l1 >= -1e-4) & (l2 >= -1e-4)
            if not ins.any(): continue
            z = l0 * ds[0] + l1 * ds[1] + l2 * ds[2]
            sub = depth[miny:maxy + 1, minx:maxx + 1]
            upd = ins & (z < sub)
            if not upd.any(): continue
            sub[upd] = z[upd]
            shade = 0.35 + 0.65 * max(0.0, float(np.dot(n, L)))
            rgb[miny:maxy + 1, minx:maxx + 1][upd] = 1.0 if lineart else np.clip(base * shade + 0.06, 0, 1)
            oid[miny:maxy + 1, minx:maxx + 1][upd] = k
            nrm[miny:maxy + 1, minx:maxx + 1][upd] = n
    # outlines: object id change, depth jump, crease
    edge = np.zeros((H, W), bool)
    for dy, dx in ((0, 1), (1, 0), (1, 1)):
        a = slice(0, H - dy), slice(0, W - dx); b = slice(dy, H), slice(dx, W)
        e = (oid[a] != oid[b])
        dd = np.abs(np.where(np.isinf(depth[a]), 1e3, depth[a]) - np.where(np.isinf(depth[b]), 1e3, depth[b]))
        e |= dd > 0.9
        e |= (np.sum(nrm[a] * nrm[b], axis=-1) < np.cos(np.radians(30))) & (oid[a] >= 0)
        edge[a] |= e
    if lineart:
        thick = edge.copy()
        for dy in (-2, -1, 0, 1, 2):
            for dx in (-2, -1, 0, 1, 2):
                if dx * dx + dy * dy <= 5:
                    thick |= np.roll(np.roll(edge, dy, 0), dx, 1)
        edge = thick
    edge[:3, :] = edge[-3:, :] = False; edge[:, :3] = edge[:, -3:] = False
    rgb[edge] = 0.0 if lineart else rgb[edge] * 0.15
    img = (rgb * 255).astype(np.uint8)
    if extent:
        return img, (x0, x0 + W / px_per_mm, z0, z0 + H / px_per_mm)
    return img

def save(img, name):
    p = os.path.join(IMG, name); Image.fromarray(img).save(p, optimize=True); print(p, img.shape)

if __name__ == "__main__":
    ms = A.load()
    def it(*names, offs=None):
        offs = offs or {}
        return [(n, ms[n], np.array(offs.get(n, (0, 0, 0)), float)) for n in names]
    which = sys.argv[1:] or ["all"]
    jobs = {
        "assembled_iso.png": (it("shell", "cover", "cap", "cable", "plug"), -35, 26),
        "exploded.png": (it("shell", "device", "cover", "cap", offs={"device": (0, 0, 30), "cover": (0, 0, 66), "cap": (0, 0, 26)}), -35, 22),
        "device_in_shell.png": (it("shell", "device", "plug", "cable", "cap"), -30, 38),
        "shell_usb_end.png": (it("shell"), -125, 30),
        "assembled_ribbon_end.png": (it("shell", "cover", "cap"), 145, 24),
        "cable_clamp.png": (it("shell", "cap", "cable", offs={"cap": (0, 0, 14)}), -60, 30),
    }
    for k, (items, az, el) in jobs.items():
        if "all" in which or k in which:
            save(render(items, az, el), k)
