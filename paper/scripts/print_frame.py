"""The frames and ticks of a matplotlib figure at the size they print in the paper.

A figure placed with ``\\includegraphics[width=f\\linewidth]`` in a slot of width L (MNRAS: the column, 243.1 pt; the text width
of a two-column figure, 506.1 pt) prints at the scale s = f L / W, W the figure's width as saved. Each frame line and tick is drawn
at its printed size divided by s, so that every figure of the paper prints them alike: spine and tick width 1.02 pt, ticks 4.08 pt
(major) and 2.45 pt (minor), as Fig. 15 prints them, and the tick labels 3.5 pt off the frame. Fonts are not changed.

    from print_frame import print_frame
    print_frame(fig, f=0.99, slot="column", tight=True)   # just before fig.savefig(..., bbox_inches="tight")
"""

SLOT_PT = {"column": 243.1, "text": 506.1}
SPINE_PT, TICK_WIDTH_PT, MAJOR_PT, MINOR_PT = 1.02, 1.02, 4.08, 2.45
PAD_PT = 3.5  # the gap between the tick labels and the frame, as printed


def saved_width_pt(fig, tight=False, pad_inches=0.1):
    """The figure's width as saved: the canvas, or with bbox_inches="tight" the tight box plus its padding."""
    if not tight:
        return fig.get_size_inches()[0] * 72.0
    fig.canvas.draw()
    box = fig.get_tightbbox(fig.canvas.get_renderer())
    return (box.width + 2.0 * pad_inches) * 72.0


def _all_axes(axes):
    out = []
    for ax in axes:
        out.append(ax)
        out.extend(_all_axes(getattr(ax, "child_axes", [])))   # secondary axes and insets, which fig.axes does not list
    return out


def _set(fig, s):
    for ax in _all_axes(fig.axes):
        for spine in ax.spines.values():
            spine.set_linewidth(SPINE_PT / s)
        ax.tick_params(which="major", width=TICK_WIDTH_PT / s, length=MAJOR_PT / s, pad=PAD_PT / s)
        ax.tick_params(which="minor", width=TICK_WIDTH_PT / s, length=MINOR_PT / s, pad=PAD_PT / s)
        colorbar = getattr(ax, "_colorbar", None)
        if colorbar is not None and getattr(colorbar, "outline", None) is not None:
            colorbar.outline.set_linewidth(SPINE_PT / s)


def print_frame(fig, f, slot, tight=False, pad_inches=0.1):
    """Set every axes' frame and ticks to their printed size for the figure's slot in the paper; return the scale s.

    With a tight crop the saved width depends on the ticks, so the scale is taken again once after they are set."""
    s = f * SLOT_PT[slot] / saved_width_pt(fig, tight, pad_inches)
    _set(fig, s)
    if tight:
        s = f * SLOT_PT[slot] / saved_width_pt(fig, tight, pad_inches)
        _set(fig, s)
    return s
