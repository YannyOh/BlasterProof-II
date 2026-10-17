"""
BLASTERPROOF II -- true-scale A4 production drawing (2 sheets, PDF).

Sheet 1 (1:1): plan view with the USB-Blaster II outline, longitudinal
section C-C showing the pod, plug and cable in place, end section A-A
through the USB opening, 100 mm scale-check bar.
Sheet 2 (2:1): cable-clamp sections B-B for both hardware variants,
parts list, hardware list, bank-card scale check.

Every drawing coordinate is in millimetres on the paper. Print at 100 %.
"""
import os, sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon as MPoly, Circle
from shapely.geometry import Polygon
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE); sys.path.insert(0, os.path.join(ROOT, "cad"))
import assembly_meshes as A
import render as RN
import cradle_cq as M

REV = "2.2"
DATE = "2026-10-17"
OUT = os.path.join(ROOT, "docs", "BLASTERPROOF-II_drawing_1to1_A4.pdf")
PW, PH = 297.0, 210.0
INK = "#111111"; THIN = 0.18; MED = 0.35; THICK = 0.6        # line widths in mm
MM2PT = 72 / 25.4

ms = A.load()


def lw(mm):
    return mm * MM2PT


def new_sheet():
    fig = plt.figure(figsize=(PW / 25.4, PH / 25.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, PW); ax.set_ylim(0, PH)
    ax.set_aspect("equal"); ax.axis("off")
    # border + zone frame
    ax.add_patch(Rectangle((10, 10), PW - 20, PH - 20, fill=False, lw=lw(THICK), ec=INK))
    return fig, ax


def title_block(ax, sheet, scale, title):
    x, y, w, h = PW - 10 - 118, 10, 118, 30
    ax.add_patch(Rectangle((x, y), w, h, fill=False, lw=lw(MED), ec=INK))
    for yy in (y + 10, y + 20):
        ax.plot([x, x + w], [yy, yy], lw=lw(THIN), c=INK)
    ax.plot([x + 70, x + 70], [y, y + 20], lw=lw(THIN), c=INK)
    ax.plot([x + 94, x + 94], [y, y + 20], lw=lw(THIN), c=INK)
    t = dict(fontsize=5, color="#555", va="top", ha="left")
    ax.text(x + 1.2, y + h - 1, "PRODUCT", **t)
    ax.text(x + 1.2, y + h - 4, "BLASTERPROOF II", fontsize=10, weight="bold", va="top")
    ax.text(x + 60, y + h - 4.8, title, fontsize=6.5, va="top")
    ax.text(x + 1.2, y + 19, "PART / ASSEMBLY", **t)
    ax.text(x + 1.2, y + 15.2, "USB-Blaster II strain-relief enclosure", fontsize=6.5, va="top")
    ax.text(x + 71.2, y + 19, "REV", **t); ax.text(x + 71.2, y + 15.2, REV, fontsize=8, va="top", weight="bold")
    ax.text(x + 95.2, y + 19, "SHEET", **t); ax.text(x + 95.2, y + 15.2, f"{sheet} / 2", fontsize=8, va="top")
    ax.text(x + 1.2, y + 9, "UNITS  mm     TOLERANCE  ±0.3 printed     MATERIAL  PETG (see PPD)", **t)
    ax.text(x + 1.2, y + 5, f"DRAWN  {DATE}     SOURCE  cradle_cq.py v{REV}", **t)
    ax.text(x + 71.2, y + 9, "SCALE", **t); ax.text(x + 71.2, y + 5.6, scale, fontsize=8, va="top", weight="bold")
    ax.text(x + 95.2, y + 9, "SIZE", **t); ax.text(x + 95.2, y + 5.6, "A4", fontsize=8, va="top", weight="bold")


def raster_view(ax, items, R, origin, scale=1.0, ppm=20):
    """Line-art hidden-line view placed so model (0,0) lands on `origin`."""
    img, (x0, x1, z0, z1) = RN.render(items, R=R, px_per_mm=ppm, pad=2, lineart=True, extent=True)
    ox, oy = origin
    a = (255 - img.min(axis=2)).astype(np.uint8)          # ink -> opaque, paper -> transparent
    img = np.dstack([np.zeros_like(img), a])
    ax.imshow(img, extent=(ox + x0 * scale, ox + x1 * scale, oy + z0 * scale, oy + z1 * scale),
              interpolation="antialiased", zorder=1)


def loops_to_polys(section, proj):
    """trimesh Path3D section -> even-odd filled shapely geometry in 2-D."""
    polys = []
    for loop in section.discrete:
        p = Polygon(proj(loop))
        if not p.is_valid:
            p = p.buffer(0)
        if p.area > 1e-3:
            polys.append(p)
    g = None
    for p in polys:
        g = p if g is None else g.symmetric_difference(p)
    return g


def draw_geom(ax, g, origin, scale, hatch=None, fc="white", ec=INK, lw_mm=MED, z=3, alpha=1.0):
    if g is None:
        return
    geoms = getattr(g, "geoms", [g])
    ox, oy = origin
    for p in geoms:
        if p.geom_type != "Polygon":
            continue
        ext = np.array(p.exterior.coords) * scale + (ox, oy)
        from matplotlib.path import Path
        from matplotlib.patches import PathPatch
        verts = [ext]; codes = [[Path.MOVETO] + [Path.LINETO] * (len(ext) - 2) + [Path.CLOSEPOLY]]
        for ring in p.interiors:
            r = np.array(ring.coords) * scale + (ox, oy)
            verts.append(r); codes.append([Path.MOVETO] + [Path.LINETO] * (len(r) - 2) + [Path.CLOSEPOLY])
        path = Path(np.vstack(verts), np.concatenate(codes))
        ax.add_patch(PathPatch(path, fc=fc, ec=ec, lw=lw(lw_mm), hatch=hatch, zorder=z, alpha=alpha))


def section(name, origin_pt, normal, proj, ax, origin, scale, **kw):
    s = ms[name].section(plane_origin=origin_pt, plane_normal=normal)
    if s is None:
        return None
    g = loops_to_polys(s, proj)
    draw_geom(ax, g, origin, scale, **kw)
    return g


def dim(ax, p1, p2, off, text, origin=(0, 0), scale=1.0, horiz=True, fs=6, tpos=0.5, ext=True):
    """Linear dimension between model points p1, p2 (model mm)."""
    ox, oy = origin
    (x1, y1), (x2, y2) = [(ox + a * scale, oy + b * scale) for a, b in (p1, p2)]
    if horiz:
        yd = (y1 if off > 0 else y1) + off
        yd = max(y1, y2) + off if off > 0 else min(y1, y2) + off
        if ext:
            for x, y in ((x1, y1), (x2, y2)):
                ax.plot([x, x], [y + np.sign(off) * 1.0, yd + np.sign(off) * 1.2], lw=lw(THIN), c=INK)
        ax.annotate("", (x1, yd), (x2, yd), arrowprops=dict(arrowstyle="<|-|>", lw=lw(THIN), color=INK,
                                                           mutation_scale=4, shrinkA=0, shrinkB=0))
        ax.text(x1 + (x2 - x1) * tpos, yd + 0.6, text, ha="center", va="bottom", fontsize=fs, color=INK,
                bbox=dict(fc="white", ec="none", pad=0.2))
    else:
        xd = max(x1, x2) + off if off > 0 else min(x1, x2) + off
        if ext:
            for x, y in ((x1, y1), (x2, y2)):
                ax.plot([x + np.sign(off) * 1.0, xd + np.sign(off) * 1.2], [y, y], lw=lw(THIN), c=INK)
        ax.annotate("", (xd, y1), (xd, y2), arrowprops=dict(arrowstyle="<|-|>", lw=lw(THIN), color=INK,
                                                           mutation_scale=4, shrinkA=0, shrinkB=0))
        ax.text(xd + 0.8 * np.sign(off), y1 + (y2 - y1) * tpos, text, ha="left" if off > 0 else "right",
                va="center", fontsize=fs, rotation=0, color=INK, bbox=dict(fc="white", ec="none", pad=0.2))


def label(ax, x, y, text, fs=6.5, weight="bold", **kw):
    ax.text(x, y, text, fontsize=fs, weight=weight, color=INK, **kw)


def leader(ax, xy, xytext, text, fs=5.5):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=fs, color=INK, va="center",
                arrowprops=dict(arrowstyle="-|>", lw=lw(THIN), color=INK, mutation_scale=4, shrinkA=0, shrinkB=0.5))


def centre_line(ax, p1, p2):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], lw=lw(THIN), c=INK, ls=(0, (8, 2, 1.5, 2)), zorder=6)


def rrect(ax, cx, cy, w, h, r, **kw):
    ax.add_patch(FancyBboxPatch((cx - w / 2 + r, cy - h / 2 + r), w - 2 * r, h - 2 * r,
                                boxstyle=f"round,pad={r}", **kw))


# ---------------------------------------------------------------- sheet 1
def sheet1(pdf):
    fig, ax = new_sheet()
    title_block(ax, 1, "1 : 1", "General arrangement")

    # ---- plan view -----------------------------------------------------
    TOP = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])        # screen x=X, depth=-Z, up=Y
    o_top = (52.0, 150.0)
    raster_view(ax, [(n, ms[n], np.zeros(3)) for n in ("shell", "cover", "cap")], TOP, o_top)
    ox, oy = o_top
    # USB-Blaster II outline (hidden) + plug/cable phantom
    rrect(ax, ox, oy, M.DEV_L, M.DEV_W, 2.0, fill=False, ec="#c0392b", lw=lw(MED), ls=(0, (4, 1.6)), zorder=5)
    ax.text(ox, oy + 2, "USB-Blaster II\n63.5 × 41.4 × 20.6", ha="center", va="center", fontsize=6.2,
            color="#c0392b", weight="bold", zorder=6, bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.6))
    px0 = M.X_OUT - 2.0
    ax.add_patch(Rectangle((ox + px0, oy - 5.5), M.USB_BOOT_L + 2.0, 11, fill=False, ec="#7f8c8d",
                           lw=lw(THIN), ls=(0, (6, 1.5, 1.5, 1.5)), zorder=5))
    ax.plot([ox + px0 + M.USB_BOOT_L + 2, ox + M.SR_X1 + 18], [oy + 2, oy + 2], c="#7f8c8d", lw=lw(THIN),
            ls=(0, (6, 1.5, 1.5, 1.5)), zorder=5)
    ax.plot([ox + px0 + M.USB_BOOT_L + 2, ox + M.SR_X1 + 18], [oy - 2, oy - 2], c="#7f8c8d", lw=lw(THIN),
            ls=(0, (6, 1.5, 1.5, 1.5)), zorder=5)
    ax.text(ox + M.SR_X1 + 4, oy - 7, "USB cable (phantom)", fontsize=5, va="center", color="#555")
    centre_line(ax, (ox - M.X_OUT - 9, oy), (ox + M.SR_X1 + 9, oy))
    # dims
    dim(ax, (-M.X_OUT, M.Y_OUT + M.PAD_OUT), (M.SR_X1, M.Y_OUT + M.PAD_OUT), 6, f"{M.OUT_L + M.SR_TAIL_L:.1f}", o_top)
    dim(ax, (-M.X_OUT, M.Y_OUT + M.PAD_OUT), (M.X_OUT, M.Y_OUT + M.PAD_OUT), 2.5, f"{M.OUT_L:.1f}", o_top)
    dim(ax, (M.X_OUT, M.SR_TAIL_W / 2), (M.SR_X1, M.SR_TAIL_W / 2), 4.5, f"tail {M.SR_TAIL_L:.0f}", o_top)
    dim(ax, (-M.X_OUT, -(M.Y_OUT + M.PAD_OUT)), (-M.X_OUT, M.Y_OUT + M.PAD_OUT), -5, f"{M.OUT_W + 2 * M.PAD_OUT:.1f}", o_top, horiz=False, tpos=0.75)
    dim(ax, (M.SR_X1, -M.SR_TAIL_W / 2), (M.SR_X1, M.SR_TAIL_W / 2), 3, f"{M.SR_TAIL_W:.0f}", o_top, horiz=False, tpos=0.8)
    label(ax, 14, 192, "PLAN VIEW", fs=7.5)
    ax.text(14, 188.5, "red dashed = USB-Blaster II body inside (hidden)", fontsize=5.2, color="#c0392b")
    ax.text(ox - M.X_OUT - 2, oy - M.Y_OUT - 9.5, "◄ RIBBON / IDC END", fontsize=5.2, color="#555")
    ax.text(ox + M.X_OUT + 4, oy - M.Y_OUT - 9.5, "USB END ►", fontsize=5.2, color="#555")
    # section markers
    for xx in (-M.X_OUT - 13, M.SR_X1 + 12):
        ax.text(ox + xx, oy + 3.0, "C", fontsize=6.5, weight="bold", ha="center")
    ax.plot([ox + M.X_OUT - 2.2] * 2, [oy - M.Y_OUT - 6, oy - M.Y_OUT - 3], c=INK, lw=lw(THICK))
    ax.text(ox + M.X_OUT - 3.6, oy - M.Y_OUT - 9.5, "A", fontsize=6.5, weight="bold")

    # ---- section C-C (XZ at y = 0) ---------------------------------------
    o_cc = (52.0, 62.0)
    projXZ = lambda L: L[:, [0, 2]]
    org = [0, 0, 0]; nrm = [0, 1, 0]
    for name, kw in (("shell", dict(hatch="////", fc="white")),
                     ("cover", dict(hatch="\\\\\\\\", fc="white")),
                     ("cap", dict(hatch="xxxx", fc="white")),
                     ("device", dict(fc="#d9d9d9", z=2)),
                     ("plug", dict(fc="#9a9a9a", z=2)),
                     ("cable", dict(fc="#3a3a3a", z=2))):
        section(name, org, nrm, projXZ, ax, o_cc, 1.0, **kw)
    ox, oy = o_cc
    ax.text(ox, oy + M.FLOOR + M.CLR_Z + M.DEV_H / 2, "USB-Blaster II", ha="center", va="center",
            fontsize=6.2, weight="bold", color="#333")
    centre_line(ax, (ox + M.X_OUT - 10, oy + M.SPLIT_Z), (ox + M.SR_X1 + 8, oy + M.SPLIT_Z))
    dim(ax, (-M.X_OUT, 0), (-M.X_OUT, M.OUT_H), -5, f"{M.OUT_H:.1f}", o_cc, horiz=False)
    dim(ax, (M.SR_X1, 0), (M.SR_X1, M.SPLIT_Z), 3, f"cable axis {M.SPLIT_Z:.1f}", o_cc, horiz=False)
    leader(ax, (ox - M.X_CAV + 8, oy + M.JOINT_Z), (ox - 12, oy + 31), f"parting line z = {M.JOINT_Z:.1f}")
    leader(ax, (ox + M.X_OUT - 0.6, oy + 15.5), (ox + M.X_OUT + 6, oy + 33), "end wall thinned to 1.2 — plug boot seats in recess")
    leader(ax, (ox + M.SAD_XC, oy + M.SPLIT_Z + 2.2), (ox + M.SAD_XC - 4, oy + 28.5), "saddle + cap clamp the jacket")
    leader(ax, (ox - M.X_OUT + 0.5, oy + M.JOINT_Z), (ox - M.X_OUT + 2, oy - 9), "ribbon tunnel")
    dim(ax, (-M.DEV_L / 2, M.FLOOR + M.CLR_Z), (M.DEV_L / 2, M.FLOOR + M.CLR_Z), -8.5, "63.5 (pod)  + 0.6 clearance each end", o_cc)
    label(ax, 14, 104, "SECTION C-C", fs=7.5)
    ax.text(14, 100.5, "through the cable axis — shows how the pod, plug and cable sit", fontsize=5.2)

    # ---- section A-A (YZ through USB end wall, looking -X) ----------------
    o_aa = (232.0, 62.0)
    xa = M.X_OUT - 2.2
    projYZ = lambda L: np.c_[-L[:, 1], L[:, 2]]          # looking toward -X: +Y appears on the left
    for name, kw in (("shell", dict(hatch="////")), ("cover", dict(hatch="\\\\\\\\"))):
        section(name, [xa, 0, 0], [1, 0, 0], projYZ, ax, o_aa, 1.0, **kw)
    ox, oy = o_aa
    rrect(ax, ox, oy + M.FLOOR + M.CLR_Z + M.DEV_H / 2, M.DEV_W, M.DEV_H, 1.5, fill=False, ec="#c0392b",
          lw=lw(MED), ls=(0, (4, 1.6)), zorder=5)
    rrect(ax, ox, oy + M.SPLIT_Z, 11, 9, 2.0, fill=False, ec="#7f8c8d", lw=lw(THIN), ls=(0, (6, 1.5, 1.5, 1.5)), zorder=5)
    ax.add_patch(Circle((ox, oy + M.SPLIT_Z), M.CABLE_D / 2, fc="#3a3a3a", ec="none", zorder=6))
    centre_line(ax, (ox - 14, oy + M.SPLIT_Z), (ox + 14, oy + M.SPLIT_Z))
    centre_line(ax, (ox, oy - 3), (ox, oy + M.OUT_H + 3))
    dim(ax, (-M.USB_W / 2, M.USB_Z1), (M.USB_W / 2, M.USB_Z1), 9.5, f"USB opening {M.USB_W:.0f}", o_aa)
    dim(ax, (M.USB_W / 2, M.USB_Z0), (M.USB_W / 2, M.USB_Z1), 14, f"{M.USB_Z1 - M.USB_Z0:.1f}", o_aa, horiz=False, tpos=0.5)
    dim(ax, (-M.OUT_W / 2, 0), (M.OUT_W / 2, 0), -5, f"{M.OUT_W:.1f}", o_aa, tpos=0.3)
    label(ax, ox - 27, oy + 42, "SECTION A-A", fs=7.5)
    ax.text(ox - 27, oy + 38.5, "USB end wall, looking into the pod", fontsize=5.2)
    ax.text(ox - 27, oy - 12, "grey = generic plug boot 11 × 9\nopening fits Type-B, mini-B, micro-B", fontsize=5, color="#555")

    # ---- 3-D view (not to scale) ----------------------------------------
    from PIL import Image
    im = np.asarray(Image.open(os.path.join(ROOT, "docs", "img", "assembled_iso.png")))
    w = 84.0; h = w * im.shape[0] / im.shape[1]
    ax.imshow(im, extent=(196, 196 + w, 136, 136 + h), zorder=1)
    ax.text(196, 136 + h + 3, "3-D VIEW (not to scale)", fontsize=6.5, weight="bold")
    # ---- scale check ------------------------------------------------------
    sx, sy = 20.0, 20.0
    for i in range(10):
        ax.add_patch(Rectangle((sx + i * 10, sy), 10, 2.2, fc=INK if i % 2 == 0 else "white", ec=INK, lw=lw(THIN)))
    for i in range(11):
        ax.text(sx + i * 10, sy + 3, f"{i * 10}", fontsize=4.6, ha="center")
    ax.text(sx, sy - 3.8, "SCALE CHECK — this bar must measure exactly 100 mm. If not, reprint at 100 % / “Actual size”.",
            fontsize=5.6, weight="bold")
    ax.text(sx, sy - 7.0, "General tolerance on printed parts ±0.3 mm. Dimensions in mm. Third-angle projection.",
            fontsize=5.0, color="#444")
    pdf.savefig(fig); plt.close(fig)


# ---------------------------------------------------------------- sheet 2
def screw_selftap(ax, cx, base_z, top_z, origin, sc):
    """M3 x 12 pan head self-tapping, drawn in section (model mm)."""
    ox, oy = origin
    L = 12.0; hd, hk = 5.6, 2.2
    ax.add_patch(Rectangle((ox + (cx - 1.5) * sc, oy + (top_z - L) * sc), 3.0 * sc, L * sc, fc="#b8bcc2", ec=INK, lw=lw(THIN), zorder=7))
    ax.add_patch(FancyBboxPatch((ox + (cx - hd / 2 + 0.6) * sc, oy + top_z * sc), (hd - 1.2) * sc, (hk - 0.6) * sc,
                                boxstyle=f"round,pad={0.6 * sc}", fc="#b8bcc2", ec=INK, lw=lw(THIN), zorder=7))
    for k in range(int(L / 1.06)):
        z = top_z - L + 0.5 + k * 1.06
        ax.plot([ox + (cx - 1.5) * sc, ox + (cx + 1.5) * sc], [oy + z * sc, oy + (z + 0.53) * sc], c=INK, lw=lw(0.1), zorder=8)


def screw_thumb_insert(ax, cx, ins_top, top_z, origin, sc):
    """Brass M3 heat-set insert (OD 4.6 x 5.7) + M3 x 10 knurled thumb screw (DIN 653)."""
    ox, oy = origin
    ax.add_patch(Rectangle((ox + (cx - 2.3) * sc, oy + (ins_top - 5.7) * sc), 4.6 * sc, 5.7 * sc, fc="#e2b45a", ec=INK, lw=lw(THIN), zorder=7, hatch="||||"))
    L = 10.0
    ax.add_patch(Rectangle((ox + (cx - 1.5) * sc, oy + (top_z - L) * sc), 3.0 * sc, L * sc, fc="#b8bcc2", ec=INK, lw=lw(THIN), zorder=8))
    ax.add_patch(Rectangle((ox + (cx - 6.0) * sc, oy + top_z * sc), 12.0 * sc, 2.5 * sc, fc="#b8bcc2", ec=INK, lw=lw(THIN), zorder=8, hatch="||"))


def detail_bb(ax, shell_name, origin, sc, hardware, title):
    xs = M.SAD_XC
    projYZ = lambda L: np.c_[L[:, 1], L[:, 2]]
    section(shell_name, [xs, 0, 0], [1, 0, 0], projYZ, ax, origin, sc, hatch="////")
    section("cap", [xs, 0, 0], [1, 0, 0], projYZ, ax, origin, sc, hatch="xxxx")
    section("cable", [xs, 0, 0], [1, 0, 0], projYZ, ax, origin, sc, fc="#3a3a3a", z=4)
    ox, oy = origin
    cap_top = M.SPLIT_Z + M.FIT + 5.0
    for py in (-M.SCREW_Y, M.SCREW_Y):
        if hardware == "selftap":
            screw_selftap(ax, py, M.HOLE_BOTTOM, cap_top, origin, sc)
        else:
            screw_thumb_insert(ax, py, M.SPLIT_Z, cap_top, origin, sc)
    centre_line(ax, (ox - 15 * sc, oy + M.SPLIT_Z * sc), (ox + 15 * sc, oy + M.SPLIT_Z * sc))
    dim(ax, (-M.SR_TAIL_W / 2, 0), (M.SR_TAIL_W / 2, 0), -6, f"{M.SR_TAIL_W:.0f}", origin, sc)
    dim(ax, (-M.SCREW_Y, cap_top), (M.SCREW_Y, cap_top), 9 if hardware == "insert" else 7, f"{2 * M.SCREW_Y:.0f}", origin, sc)
    dim(ax, (M.SR_TAIL_W / 2, 0), (M.SR_TAIL_W / 2, M.SPLIT_Z), 4, f"{M.SPLIT_Z:.1f}", origin, sc, horiz=False)
    dim(ax, (M.SR_TAIL_W / 2, M.SPLIT_Z + M.FIT), (M.SR_TAIL_W / 2, cap_top), 4, "cap 5.0", origin, sc, horiz=False)
    label(ax, ox - 15 * sc, oy + 28 * sc, title, fs=7.5)
    if hardware == "selftap":
        leader(ax, (ox + M.SCREW_Y * sc, oy + 5 * sc), (ox + 18 * sc, oy - 9 * sc), "Ø2.5 pilot, 11.8 deep\nM3/ST3 × 12 pan head")
    else:
        leader(ax, (ox + (M.SCREW_Y + 2.3) * sc, oy + (M.SPLIT_Z - 3) * sc), (ox + 18 * sc, oy - 9 * sc), "Ø4.0 × 6.5 pocket, brass M3 insert\nM3 × 10 knurled thumb screw")
    leader(ax, (ox + 0, oy + M.SPLIT_Z * sc), (ox - 22 * sc, oy - 9 * sc), f"Ø{2 * M.BORE_R:.1f} bore, ribs pinch to Ø{2 * (M.BORE_R - M.GRIP_RIB):.1f}\nfor a Ø{M.CABLE_D:.1f} jacket (measure yours)")


def table(ax, x, y, cols, rows, widths, fs=5.6, rh=4.6, head=True):
    tot = sum(widths)
    ax.plot([x, x + tot], [y, y], c=INK, lw=lw(MED))
    cx = x
    for c, w in zip(cols, widths):
        ax.text(cx + 1, y - rh + 1.4, c, fontsize=fs, weight="bold"); cx += w
    yy = y - rh
    ax.plot([x, x + tot], [yy, yy], c=INK, lw=lw(THIN))
    for r in rows:
        cx = x
        for c, w in zip(r, widths):
            ax.text(cx + 1, yy - rh + 1.4, c, fontsize=fs); cx += w
        yy -= rh
        ax.plot([x, x + tot], [yy, yy], c="#999", lw=lw(0.1))
    ax.plot([x, x + tot], [yy, yy], c=INK, lw=lw(MED))
    return yy


def sheet2(pdf):
    fig, ax = new_sheet()
    title_block(ax, 2, "2 : 1", "Cable clamp + parts")
    detail_bb(ax, "shell", (62.0, 140.0), 2.0, "selftap", "SECTION B-B   option S: self-tapping")
    detail_bb(ax, "shell_insert", (182.0, 140.0), 2.0, "insert", "SECTION B-B   option I: heat-set insert")
    ax.text(14, 112, "B-B is cut across the cable saddle, looking toward the device. Scale 2 : 1 — halve any measurement taken from these sections. Tables not to scale.",
            fontsize=5.4, color="#444")

    y = table(ax, 14, 104, ["#", "Part", "File (STL / 3MF / STEP)", "Qty", "Print orientation"],
              [["1", "Shell, option S", "shell_selftap", "1", "floor down, no supports"],
               ["1", "Shell, option I", "shell_insert", "(1)", "floor down, no supports"],
               ["2", "Cover", "cover", "1", "lid down (clips up)"],
               ["3", "Clamp cap", "clamp_cap", "1", "flat face down"]],
              [6, 30, 40, 9, 40])
    ax.text(14, y - 3.5, "Print ONE shell: option S or option I.", fontsize=5.2, weight="bold")

    table(ax, 14, 70, ["Hardware", "Option S", "Option I"],
          [["Screw", "2 × M3 (ST3) × 12 self-tapping, pan head", "2 × M3 × 10 knurled thumb screw"],
           ["", "  (Ø2.5 pilot in shell)", "  DIN 653 / DIN 464, stainless"],
           ["Insert", "—", "2 × M3 brass heat-set, OD ≈4.6, L 5.7"],
           ["Cap hole", "Ø3.4 clearance", "Ø3.4 clearance"],
           ["Tools", "Phillips #1", "soldering iron ~230 °C (PETG) for inserts"]],
          [24, 62, 62])

    # bank-card check
    cx, cy = 175.0, 48.0
    ax.add_patch(FancyBboxPatch((cx + 3.18, cy + 3.18), 85.60 - 6.36, 53.98 - 6.36, boxstyle="round,pad=3.18",
                                fill=False, ec=INK, lw=lw(THIN), ls=(0, (3, 1.5))))
    ax.text(cx + 42.8, cy + 32, "CARD CHECK", ha="center", fontsize=7, weight="bold")
    ax.text(cx + 42.8, cy + 24, "A bank / ID card (85.60 × 53.98 mm)\nmust cover this box exactly.\nIf not, the print is not 1 : 1.",
            ha="center", fontsize=5.6, va="center")
    pdf.savefig(fig); plt.close(fig)


if __name__ == "__main__":
    with PdfPages(OUT) as pdf:
        sheet1(pdf); sheet2(pdf)
        d = pdf.infodict(); d["Title"] = f"BLASTERPROOF II drawing rev {REV}"; d["Author"] = "BLASTERPROOF"
    print(OUT)
