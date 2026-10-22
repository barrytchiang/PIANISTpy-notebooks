"""The text of a Mathematica export, redrawn in matplotlib's default DejaVu Sans, label by label.

An export stores a label as pieces (a word, a symbol, a subscript, an accent), each at its own origin. DejaVu Sans is wider
than the export's Arial, so the pieces are joined back into labels and each label is laid out again: consecutive pieces of one
color and direction follow one another at their DejaVu Sans widths with the export's own gaps; a subscript or superscript keeps
its offset; the hat (U+F111) is centered over its letter. A label inside a frame starts where the export's started, one just left
of a frame (a y tick label) ends where the export's ended, and any other is centered where the export's was. Greek letters are
set in math italic, Mathematica's minus as U+2212 and the script K (U+F77A) as Computer Modern \\mathcal{K}.
"""
import json
import math

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

FAMILY, METRIC = "DejaVu Sans", "Liberation Sans"
SCRIPT_K, HAT = "", ""


def reset_math():
    """Matplotlib's default math (DejaVu Sans), undoing the ports' custom Liberation Sans mathtext."""
    for key in ("mathtext.fontset", "mathtext.rm", "mathtext.it", "mathtext.bf", "mathtext.bfit", "mathtext.sf"):
        plt.rcParams[key] = plt.rcParamsDefault[key]


def _pieces(spans):
    """Each span as a piece; a span holding the hat among other characters is split into its characters (their own origins)."""
    out = []
    for sp in spans:
        if HAT in sp["text"] and len(sp["text"]) > 1:
            chars, d = sp["chars"], sp["dir"]
            for k, (ch, org) in enumerate(chars):
                # each character's export advance: to the next character's origin (the last: to the span's box end)
                if k + 1 < len(chars):
                    nx = chars[k + 1][1]
                    adv = (nx[0] - org[0]) * d[0] + (nx[1] - org[1]) * d[1]
                else:
                    b = sp["bbox"]
                    adv = max((cx - org[0]) * d[0] + (cy - org[1]) * d[1] for cx in (b[0], b[2]) for cy in (b[1], b[3]))
                out.append(dict(sp, text=ch, origin=list(org), chars=[[ch, org]], adv=adv))
        else:
            out.append(sp)
    return out


def _shown(t, weight):
    """The piece's text as DejaVu Sans sets it, and whether it needs Computer Modern math."""
    cm = SCRIPT_K in t
    t = t.replace("-", "−").replace(SCRIPT_K, r"$\mathcal{K}$")
    it = r"\mathbfit" if weight == "bold" else r"\mathit"
    for g, name in (("β", r"\beta"), ("σ", r"\sigma"), ("ϱ", r"\varrho")):
        t = t.replace(g, "$" + it + "{" + name + "}$")
    return t, cm


class _Measure:
    def __init__(self, fig):
        self.fig = fig
        self.r = fig.canvas.get_renderer()

    def width(self, text, family, weight, style, size, cm=False):
        """Advance width in pt of text set at size (rotation 0)."""
        if not text.strip():
            text = text.replace(" ", " ")
        t = self.fig.text(0, 0, text, fontproperties=FontProperties(family=family, weight=weight, style=style, size=size),
                          math_fontfamily="cm" if cm else "dejavusans")
        w = t.get_window_extent(self.r).width * 72.0 / self.fig.dpi
        t.remove()
        return w


HAT_LIFT = 0.325 - 0.616   # em: the hat's ink bottom above its origin, Mathematica's hat less DejaVu Sans' U+02C6


def _axis_aligned(d):
    return abs(d[0]) < 1e-6 or abs(d[1]) < 1e-6


def _old_width(p, m, FONT):
    """The export piece's advance along its line: its own box where the line is horizontal or vertical (Mathematica's glyph
    widths), else Arial's measured in Liberation Sans."""
    if "adv" in p:
        return p["adv"]
    d, o, b = p["dir"], p["origin"], p["bbox"]
    if _axis_aligned(d) and len(p["text"]) == len(p.get("chars", p["text"])):
        return max((cx - o[0]) * d[0] + (cy - o[1]) * d[1] for cx in (b[0], b[2]) for cy in (b[1], b[3]))
    return m.width(p["text"], METRIC, *FONT[p["font"]], p["size"])


def _frames_pt(fig, W, H):
    """The axes rectangles in the page's points, y down: (x0, y0, x1, y1)."""
    out = []
    for ax in fig.axes:
        b = ax.get_position()
        out.append((b.x0 * W, (1.0 - b.y1) * H, b.x1 * W, (1.0 - b.y0) * H))
    return out


def draw(fig, W, H, spans, FONT):
    """Every label of the export, in DejaVu Sans, laid out as the module docstring says."""
    m = _Measure(fig)
    frames = _frames_pt(fig, W, H)
    pieces = _pieces(spans)
    groups, cur = [], []
    for p in pieces:
        if cur:
            q0, q = cur[0], [c for c in cur if c["text"] != HAT][-1] if any(c["text"] != HAT for c in cur) else cur[-1]
            d = q0["dir"]
            n = (-d[1], d[0])
            rel = (p["origin"][0] - q0["origin"][0], p["origin"][1] - q0["origin"][1])
            along, perp = rel[0] * d[0] + rel[1] * d[1], rel[0] * n[0] + rel[1] * n[1]
            q_end = ((q["origin"][0] - q0["origin"][0]) * d[0] + (q["origin"][1] - q0["origin"][1]) * d[1]
                     + _old_width(q, m, FONT))
            same = p["color"] == q0["color"] and abs(p["dir"][0] - d[0]) < 1e-6 and abs(p["dir"][1] - d[1]) < 1e-6
            if same and abs(perp) < 0.55 * q0["size"] and -0.6 * q0["size"] <= along - q_end <= 0.5 * q0["size"]:
                cur.append(p)
                continue
            groups.append(cur)
        cur = [p]
    if cur:
        groups.append(cur)
    for g in groups:
        _place(fig, W, H, g, FONT, m, frames)


def _place(fig, W, H, g, FONT, m, frames):
    o, d = g[0]["origin"], g[0]["dir"]
    n = (-d[1], d[0])
    ang = math.degrees(math.atan2(-d[1], d[0]))

    def coords(p):
        rel = (p["origin"][0] - o[0], p["origin"][1] - o[1])
        return rel[0] * d[0] + rel[1] * d[1], rel[0] * n[0] + rel[1] * n[1]

    body = [p for p in g if p["text"] != HAT]
    # the export's extent along the label (Arial advances) and the new widths (DejaVu Sans)
    lay, s, prev = [], 0.0, None
    for p in g:
        weight, style = FONT[p["font"]]
        if p["font"].startswith("CairoFont") and p["text"] == "c" and weight == "bold" and style == "italic":
            style = "normal"                      # the subscript c of beta_c upright
        a, pp = coords(p)
        if p["text"] == HAT:
            lay.append((p, None, pp, weight, style))
            continue
        text = p["text"].lstrip() if p["size"] < 0.9 * g[0]["size"] else p["text"]   # a sub/superscript: no leading space
        shown, cm = _shown(text, weight)
        w_new = m.width(shown, FAMILY, weight, style, p["size"], cm)
        if prev is not None and _axis_aligned(d):
            pa, pw_old = prev
            s += max(0.0, a - (pa + pw_old))      # the export's gap after the previous piece
        lay.append((p, s, pp, weight, style, shown, cm, w_new))
        s += w_new
        prev = (a, _old_width(p, m, FONT))
    w_total = s
    # a small minus that the export sets on the baseline before a raised digit (an exponent: Mathematica's glyph carries the
    # raise) takes the digit's offset
    for i in range(len(lay) - 1):
        cur_, nxt = lay[i], lay[i + 1]
        if cur_[1] is not None and nxt[1] is not None and cur_[0]["text"].strip() == "-" and nxt[0]["text"].strip().isdigit() \
                and cur_[0]["size"] < g[0]["size"] * 0.9 and abs(nxt[2] - cur_[2]) > 0.2 * cur_[0]["size"]:
            lay[i] = (cur_[0], cur_[1], nxt[2]) + cur_[3:]
    a_first = coords(body[0])[0] if body else 0.0
    a_last, _ = coords(body[-1]) if body else (0.0, 0.0)
    w_last_old = _old_width(body[-1], m, FONT) if body else 0.0
    L0, R0 = a_first, a_last + w_last_old
    cx, cy = o[0] + 0.5 * (L0 + R0) * d[0], o[1] + 0.5 * (L0 + R0) * d[1]
    inside = any(x0 <= cx <= x1 and y0 <= cy <= y1 for x0, y0, x1, y1 in frames)
    left_of = abs(d[1]) < 1e-6 and any(0.0 <= x0 - (o[0] + R0 * d[0]) <= 20.0 and y0 - 5 <= cy <= y1 + 5 for x0, y0, x1, y1 in frames)
    start = L0 if inside else (R0 - w_total if left_of else 0.5 * (L0 + R0) - 0.5 * w_total)
    placed = []
    for item in lay:
        p = item[0]
        if p["text"] == HAT:
            continue
        _, s_i, pp, weight, style, shown, cm, w_new = item
        a_i = start + s_i
        x, y = o[0] + a_i * d[0] + pp * n[0], o[1] + a_i * d[1] + pp * n[1]
        fig.text(x / W, 1.0 - y / H, shown, fontproperties=FontProperties(family=FAMILY, weight=weight, style=style, size=p["size"]),
                 math_fontfamily="cm" if cm else "dejavusans", color=p["color"], rotation=ang, rotation_mode="anchor",
                 ha="left", va="baseline")
        placed.append((coords(p)[0], a_i, w_new))
    for item in lay:
        p = item[0]
        if p["text"] != HAT:
            continue
        a_h, pp = coords(p)
        # the piece the hat stands on: the placed piece whose export origin is nearest before the hat's
        base = min(placed, key=lambda t: abs(a_h - t[0]) if a_h >= t[0] - 2 else 1e9) if placed else (a_h, a_h, 0.0)
        a_c = base[1] + 0.5 * base[2]
        weight, style = item[3], item[4]
        pp = pp - HAT_LIFT * p["size"]        # n points down the label: lower DejaVu's hat by its higher ink
        x, y = o[0] + a_c * d[0] + pp * n[0], o[1] + a_c * d[1] + pp * n[1]
        fig.text(x / W, 1.0 - y / H, "ˆ", fontproperties=FontProperties(family=FAMILY, weight=weight, size=p["size"]),
                 color=p["color"], rotation=ang, rotation_mode="anchor", ha="center", va="baseline")


def patch(mp):
    """Route mma_port's Page and draw_text through the label layout above."""
    page_init = mp.Page.__init__

    def init(self, *a, **k):
        page_init(self, *a, **k)
        reset_math()

    mp.Page.__init__ = init

    def draw_text(page, layout, glyphs, adjust=None):
        spans = []
        for sp in json.load(open(layout))["spans"]:
            if adjust:
                sp = adjust(sp)
                if sp is None:
                    continue
            spans.append(sp)
        draw(page.fig, page.W, page.H, spans, mp.FONT)

    mp.draw_text = draw_text
    return mp
