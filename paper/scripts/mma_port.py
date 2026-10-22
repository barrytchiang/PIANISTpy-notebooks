"""Drawing a figure on the page of a Mathematica export: a matplotlib figure of the export's size in points, frames at the export's
positions, FrameTicks drawn inward with their size as a fraction of the frame, curves in the export's widths and caps, and every
text span of the export (a layout file of its spans) in matplotlib's default DejaVu Sans, label by label (dejavu_labels)."""
import json
import os

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402

FRAME = 224.46                                  # pt, frame side (ImageSize 250 less the padding)
LW_FRAME = 0.008 * FRAME
C = dict(iso=(0.333328, 0.333328, 0.333328), b05=(0.253479, 0.497086, 0.687317), bm05=(0.709793, 0.035294, 0.152939),
         OM1=(0.275681, 0.117126, 0.365616), OM10=(0.674103, 0.335678, 0.657639), OM100=(0.882339, 0.627441, 0.815674),
         OMII1=(0.043137, 0.086273, 0.027451), OMII10=(0.360458, 0.535156, 0.151367), OMII100=(0.563324, 0.822144, 0.230591),
         COMRa1U=(0.003922, 0.180389, 0.290192), COMRa10U=(0.113724, 0.464706, 0.57254), COMRa100U=(0.505875, 0.745087, 0.807831),
         COMRa1=(0.459793, 0.229599, 0.082153), COMRa10=(0.738113, 0.394577, 0.152863), COMRa100=(0.927826, 0.54744, 0.248627),
         black=(0.0, 0.0, 0.0), cyanguide=(0.0, 0.898, 0.898), magenta=(1.0, 0.0, 1.0))
FONT = {"ArialMT": ("normal", "normal"), "Arial-BoldMT": ("bold", "normal"), "MathematicaSans": ("normal", "normal"),
        "MathematicaSans-Bold": ("bold", "normal"), "CairoFont-2-0": ("normal", "italic"), "CairoFont-4-0": ("bold", "italic"),
        "CairoFont-5-0": ("bold", "italic")}


class Page:
    def __init__(self, W, H, x0, y_rows):
        plt.rcParams.update({"pdf.fonttype": 42, "axes.unicode_minus": True,
                             "lines.scale_dashes": False})   # AbsoluteDashing: dash lengths in points, not scaled by the width
        self.W, self.H, self.x0, self.y_rows = W, H, x0, y_rows
        self.fig = plt.figure(figsize=(W / 72.0, H / 72.0))

    def frame(self, col, row, xscale, xlim, yscale, ylim):
        ax = self.fig.add_axes([self.x0[col] / self.W, 1.0 - (self.y_rows[row] + FRAME) / self.H, FRAME / self.W, FRAME / self.H])
        for s in ax.spines.values():
            s.set_linewidth(LW_FRAME)
            s.set_color("black")
        ax.set_xscale(xscale); ax.set_yscale(yscale); ax.set_xlim(*xlim); ax.set_ylim(*ylim)
        ax.tick_params(which="both", length=0, labelbottom=False, labelleft=False)
        ax.set_xticks([]); ax.set_yticks([]); ax.minorticks_off()
        return ax

    def save(self, path):
        self.fig.savefig(path)


def ticks(ax, side, vals, size):
    """inward ticks of a FrameTicks entry {pos, label, {size, 0}} on one side; size a fraction of the frame"""
    L = size
    if side in ("bottom", "top"):
        tr = blended_transform_factory(ax.transData, ax.transAxes)
        y0, y1 = (0.0, L) if side == "bottom" else (1.0, 1.0 - L)
        lo, hi = sorted(ax.get_xlim())
        for v in vals:
            if lo <= v <= hi:
                ax.plot([v, v], [y0, y1], transform=tr, color="black", lw=LW_FRAME, solid_capstyle="butt", clip_on=False, zorder=5)
    else:
        tr = blended_transform_factory(ax.transAxes, ax.transData)
        x0, x1 = (0.0, L) if side == "left" else (1.0, 1.0 - L)
        lo, hi = sorted(ax.get_ylim())
        for v in vals:
            if lo <= v <= hi:
                ax.plot([x0, x1], [v, v], transform=tr, color="black", lw=LW_FRAME, solid_capstyle="butt", clip_on=False, zorder=5)


def arange(a, b, s):
    return [a + k * s for k in range(int(round((b - a) / s)) + 1)]


def curve(ax, x, y, col, thick, dash=None, cap="projecting", z=2):
    """a joined list; thick = Mathematica Thickness (fraction of the frame); dash in export points (AbsoluteDashing x 0.9)"""
    kw = dict(color=col, lw=thick * FRAME, solid_capstyle=cap, solid_joinstyle="miter", dash_capstyle=cap, clip_on=True, zorder=z)
    if dash:
        kw["dashes"] = dash
    ax.plot(x, y, **kw)


def gridline(ax, x, col, thick=0.01):
    """a GridLines entry: vertical dashed line, AbsoluteDashing {13, 7.5} (11.7, 6.75 pt in the export), butt caps, behind the curves"""
    ax.axvline(x, color=col, lw=thick * FRAME, dashes=(11.7, 6.75), solid_capstyle="butt", dash_capstyle="butt", zorder=1)


def draw_text(page, layout, glyphs=None, adjust=None):
    """every label of the export, in DejaVu Sans, laid out label by label (dejavu_labels); `glyphs` is unused"""
    from dejavu_labels import draw
    spans = []
    for sp in json.load(open(layout))["spans"]:
        if adjust:
            sp = adjust(sp)
            if sp is None:                  # a label the adjustment removes
                continue
        spans.append(sp)
    draw(page.fig, page.W, page.H, spans, FONT)
