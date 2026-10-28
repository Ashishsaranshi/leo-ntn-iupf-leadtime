"""Render Fig. 1 (architecture + relocation timing budget) as fig_architecture.png.

Drawn at the printed size: the IEEEtran conference column is 252 pt = 3.486 in
and the figure is included with width=\\columnwidth, so the on-page scale is
1.0 and the font sizes set here are the sizes the reader sees.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
import matplotlib.patheffects as pe

COL_IN = 252.0 / 72.27            # IEEEtran conference \columnwidth, inches

plt.rcParams.update({"font.size": 8, "font.family": "serif",
                     "mathtext.fontset": "dejavuserif",
                     "savefig.bbox": "tight", "savefig.pad_inches": 0.01})
RED, GREEN, BLUE, GREY = "#c0392b", "#218c4a", "#2266cc", "#333333"

FS_BOX, FS_SUB, FS_TAG, FS_PANEL = 7.5, 7.0, 7.0, 8.5

fig = plt.figure(figsize=(COL_IN, 2.42))
# Pin the axes to the full figure: the default subplot margins would otherwise
# be cropped away by the tight bbox, leaving a figure ~22% narrower than the
# column and so scaled up (with its fonts) when included at \columnwidth.
gs = fig.add_gridspec(2, 1, height_ratios=[1.42, 1.0], hspace=0.04,
                      left=0.004, right=0.996, top=0.996, bottom=0.004)

# ============================ (a) architecture ============================
ax = fig.add_subplot(gs[0])
ax.set_xlim(0, 10); ax.set_ylim(0, 6.85); ax.axis("off")

def sat(cx, cy, color, label, sub, fill, half_w=2.05):
    """Satellite icon with a label box centred under it.

    half_w is set from the widest label so the text never overruns the box --
    the defect in the previous revision of this figure.
    """
    bw, bh = 0.62, 0.40
    ax.add_patch(Rectangle((cx-bw/2, cy-bh/2), bw, bh, facecolor="white",
                           edgecolor=color, lw=1.3, zorder=5))
    for s in (-1, 1):                      # solar panels
        ax.add_patch(Rectangle((cx+s*bw/2, cy-0.25), s*0.44, 0.50,
                     facecolor=color, alpha=0.30, edgecolor=color,
                     lw=0.7, zorder=4))
    ax.add_patch(FancyBboxPatch((cx-half_w, cy-1.72), 2*half_w, 1.00,
                                boxstyle="round,pad=0.02,rounding_size=0.10",
                                facecolor=fill, edgecolor=color, lw=1.2,
                                zorder=6))
    ax.text(cx, cy-0.99, label, ha="center", va="center", fontsize=FS_BOX,
            weight="bold", color=GREY, zorder=7)
    ax.text(cx, cy-1.44, sub, ha="center", va="center", fontsize=FS_SUB,
            color=GREY, zorder=7)

sat(2.45, 5.60, RED,   "source sat.", "gNB + I-UPF/UL-CL", "#fdecea",
    half_w=2.30)
sat(7.60, 5.80, GREEN, "target sat.", "gNB + UPF", "#e9f6ee", half_w=1.70)

# motion arrows; their labels sit just below the arrow so neither runs into
# the panel tag at top-left nor off the right edge of the figure.
ax.annotate("", xy=(0.62, 5.90), xytext=(1.90, 5.57),
            arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.3))
ax.text(0.58, 5.52, "setting", color=RED, fontsize=FS_TAG,
        ha="left", va="top")
ax.annotate("", xy=(9.40, 6.12), xytext=(8.15, 5.82),
            arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.3))
ax.text(9.45, 5.76, "rising", color=GREEN, fontsize=FS_TAG,
        ha="right", va="top")

# inter-satellite link
ax.plot([3.15, 6.90], [5.57, 5.79], ls=(0, (5, 3)), color=GREY, lw=1.0,
        zorder=2)
ax.text(5.05, 5.86, "ISL", ha="center", va="bottom", fontsize=FS_TAG,
        color=GREY)

# gateway
ax.add_patch(FancyBboxPatch((3.05, 0.42), 3.90, 0.92,
                            boxstyle="round,pad=0.02,rounding_size=0.10",
                            facecolor="#eef1f5", edgecolor=GREY, lw=1.2,
                            zorder=6))
ax.text(5.00, 0.88, "gateway + SMF", ha="center", va="center",
        fontsize=FS_BOX, weight="bold", color=GREY, zorder=7)
# dish
ax.plot([3.75, 3.75], [1.34, 1.64], color=GREY, lw=1.0, zorder=6)
ax.add_patch(Polygon([[3.50, 1.70], [4.00, 1.70], [3.90, 1.58], [3.60, 1.58]],
                     closed=True, facecolor="white", edgecolor=GREY, lw=1.0,
                     zorder=6))

# UE
ax.add_patch(FancyBboxPatch((0.30, 0.52), 0.46, 0.80,
                            boxstyle="round,pad=0.01,rounding_size=0.07",
                            facecolor="white", edgecolor=GREY, lw=1.1,
                            zorder=6))
ax.text(0.53, 1.46, "UE", ha="center", va="bottom", fontsize=FS_TAG,
        color=GREY)

# service link (UE -> source satellite)
ax.annotate("", xy=(0.72, 3.80), xytext=(0.60, 1.90),
            arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.0))
ax.text(0.80, 2.85, "service", color=GREY, fontsize=FS_TAG, rotation=88,
        ha="left", va="center")

# feeder link, gateway <-> source satellite (the N4/PFCP path)
ax.annotate("", xy=(2.70, 3.83), xytext=(3.80, 1.72),
            arrowprops=dict(arrowstyle="<|-|>", color=BLUE, lw=2.0))
ax.text(4.00, 2.82, "feeder link\nN4/PFCP ($k$ RTTs)", color=BLUE,
        fontsize=FS_TAG, ha="left", va="center", linespacing=1.2,
        path_effects=[pe.withStroke(linewidth=2.6, foreground="white")])

# feeder link, gateway <-> target satellite
ax.annotate("", xy=(7.20, 4.03), xytext=(6.40, 1.42),
            arrowprops=dict(arrowstyle="<|-|>", color=BLUE, lw=1.0,
                            linestyle=(0, (4, 3)), alpha=0.55))

ax.text(0.00, 6.80, "(a)", fontsize=FS_PANEL, weight="bold", color=GREY,
        ha="left", va="top")

# ========================= (b) timing budget =============================
bx = fig.add_subplot(gs[1])
bx.set_xlim(0, 10); bx.set_ylim(-2.35, 2.05); bx.axis("off")
x_cul, x_star, x_dl, y = 0.75, 5.55, 8.95, 0.0

bx.annotate("", xy=(9.75, y), xytext=(0.20, y),
            arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.1))
bx.text(9.85, y, "$t$", fontsize=FS_PANEL, color=GREY, ha="left", va="center")

# Tick marks on the axis; their labels sit ABOVE the line so they cannot
# collide with the budget bar and its labels, which sit below.
for x, lab in ((x_cul, "$t_{cul}$"), (x_star, "$t^{*}$"), (x_dl, "$t_{dl}$")):
    bx.plot([x, x], [y-0.10, y+0.10], color=GREY, lw=1.1)
    bx.text(x, y+0.20, lab, ha="center", va="bottom", fontsize=FS_TAG,
            color=GREY)

def brace(x0, x1, yb, label, up=True, lift=0.20):
    xm, s = (x0+x1)/2, (1 if up else -1)
    h = 0.15*s
    bx.plot([x0, x0], [yb, yb+h], color=GREY, lw=1.0)
    bx.plot([x1, x1], [yb, yb+h], color=GREY, lw=1.0)
    bx.plot([x0, x1], [yb+h, yb+h], color=GREY, lw=1.0)
    bx.plot([xm, xm], [yb+h, yb+h+0.11*s], color=GREY, lw=1.0)
    bx.text(xm, yb+h+lift*s, label, ha="center",
            va="bottom" if up else "top", fontsize=FS_TAG, color=GREY)

brace(x_cul, x_dl, 0.92, r"usable margin $M=t_{dl}-t_{cul}$", up=True)

# budget bar, below the axis
yb0, yb1 = -0.78, -0.42
split = x_star + (x_dl-x_star)*0.70
bx.add_patch(Rectangle((x_star, yb0), split-x_star, yb1-yb0,
                       facecolor="#bcd2f0", edgecolor=GREY, lw=0.9))
bx.add_patch(Rectangle((split, yb0), x_dl-split, yb1-yb0,
                       facecolor="#f6c99a", edgecolor=GREY, lw=0.9))
for f in (0.25, 0.5, 0.75):                      # the k round trips
    xx = x_star + (split-x_star)*f
    bx.plot([xx, xx], [yb0, yb1], color=BLUE, lw=0.8)

bx.text((x_star+split)/2, yb0-0.14, r"$k\,\mathrm{RTT}_{\mathrm{fdr}}(t^{*})$",
        ha="center", va="top", fontsize=FS_TAG, color=GREY)
# T_proc labels the orange segment from the right, clear of the t_dl tick
# label above the axis and of the delta_req brace below.
bx.text(x_dl+0.16, (yb0+yb1)/2, r"$T_{\mathrm{proc}}$",
        fontsize=FS_TAG, color=GREY, ha="left", va="center")

brace(x_star, x_dl, -1.52, r"$\delta_{\mathrm{req}}(t^{*})=t_{dl}-t^{*}$",
      up=False, lift=0.18)

bx.text(0.00, 1.95, "(b)", fontsize=FS_PANEL, weight="bold", color=GREY,
        ha="left", va="top")

fig.savefig("fig_architecture.png", dpi=400)
print("fig_architecture.png written")
