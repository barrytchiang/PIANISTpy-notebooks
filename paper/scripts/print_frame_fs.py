"""The frames and ticks of a matplotlib figure set as printed: spine and tick width 1.02 pt, ticks 4.08 (major) and
2.45 (minor) pt, as Fig. 15 of Chiang+(2026d) prints them; the tick labels 3.5 pt off the frame.

A figure placed with \\includegraphics[width=f\\linewidth] in a slot of width L (MNRAS: \\columnwidth 243.1 pt, \\textwidth 506.1 pt)
prints at s = f L / W_fig, W_fig its width as saved; each element is drawn at X_print / s. Fonts are not touched.

    import print_frame_fs
    print_frame_fs.apply(fig, f=0.99, slot="column")                  # before savefig, without bbox_inches="tight"
    print_frame_fs.apply(fig, f=0.99, slot="column", width_pt=589.2)  # the saved width, where a tight crop changes it
"""

SLOT_PT = {"column": 243.1, "text": 506.1}
SPINE_PT, TICK_W_PT, MAJOR_PT, MINOR_PT = 1.02, 1.02, 4.08, 2.45
PAD_PT = 3.5  # the gap between the tick labels and the frame, as printed


def scale(fig, f, slot, width_pt=None):
    """The printed scale s of the figure: f L over its width as saved (the canvas unless width_pt is given)."""
    w = width_pt if width_pt is not None else fig.get_size_inches()[0] * 72.0
    return f * SLOT_PT[slot] / w


def _all_axes(axes):
    """The axes with their secondary axes and insets, which fig.axes does not list."""
    out = []
    for ax in axes:
        out.append(ax)
        out.extend(_all_axes(getattr(ax, "child_axes", [])))
    return out


def apply(fig, f, slot, width_pt=None, axes=None):
    """Set every axes' spines and ticks (or those of `axes`), those of their secondary axes and insets and the colorbar outlines too, to the printed
    targets; return s."""
    s = scale(fig, f, slot, width_pt)
    for ax in _all_axes(axes if axes is not None else fig.axes):
        for sp in ax.spines.values():
            sp.set_linewidth(SPINE_PT / s)
        ax.tick_params(which="major", width=TICK_W_PT / s, length=MAJOR_PT / s, pad=PAD_PT / s)
        ax.tick_params(which="minor", width=TICK_W_PT / s, length=MINOR_PT / s, pad=PAD_PT / s)
        cb = getattr(ax, "_colorbar", None)
        if cb is not None and getattr(cb, "outline", None) is not None:
            cb.outline.set_linewidth(SPINE_PT / s)
    return s
