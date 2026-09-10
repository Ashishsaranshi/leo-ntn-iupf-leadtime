"""Render Fig. 1 (architecture + relocation timing budget) as a clean vector PDF."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
import matplotlib.patheffects as pe

plt.rcParams.update({"font.size": 8, "font.family": "serif",
                     "mathtext.fontset": "dejavuserif"})
RED, GREEN, BLUE, GREY = "#c0392b", "#218c4a", "#2266cc", "#333333"

fig = plt.figure(figsize=(3.4, 3.25))
gs = fig.add_gridspec(2, 1, height_ratios=[1.75, 0.95], hspace=0.05)

# ============================ (a) architecture ============================
ax = fig.add_subplot(gs[0]); ax.set_xlim(0, 10); ax.set_ylim(0, 7.2); ax.axis("off")

def sat(cx, cy, color, label, sub, fill):
    bw, bh = 0.6, 0.4
    ax.add_patch(Rectangle((cx-bw/2, cy-bh/2), bw, bh, facecolor="white",
                           edgecolor=color, lw=1.3, zorder=5))
    for s in (-1, 1):
        ax.add_patch(Rectangle((cx+s*bw/2, cy-0.26), s*0.46, 0.52,
                     facecolor=color, alpha=0.30, edgecolor=color, lw=0.7, zorder=4))
    box = FancyBboxPatch((cx-1.7, cy-1.55), 3.4, 0.86,
                         boxstyle="round,pad=0.02,rounding_size=0.08",
                         facecolor=fill, edgecolor=color, lw=1.2, zorder=6)
    ax.add_patch(box)
    ax.text(cx, cy-0.97, label, ha="center", va="center", fontsize=7.3,
            weight="bold", color=GREY, zorder=7)
    ax.text(cx, cy-1.32, sub, ha="center", va="center", fontsize=6.6,
            color=GREY, zorder=7)

sat(2.55, 6.1, RED,   "source sat.", "gNB + I-UPF/UL-CL", "#fdecea")
sat(7.7, 6.35, GREEN, "target sat.", "gNB + UPF", "#e9f6ee")

# motion arrows (placed clear of boxes)
ax.annotate("", xy=(1.15, 6.35), xytext=(2.0, 6.05),
            arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.3))
ax.text(0.95, 6.55, "setting", color=RED, fontsize=6.8, ha="center")
ax.annotate("", xy=(9.05, 6.95), xytext=(8.2, 6.5),
            arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.3))
ax.text(9.2, 7.05, "rising", color=GREEN, fontsize=6.8, ha="center")

# ISL
ax.plot([3.35, 6.85], [6.12, 6.32], ls=(0, (5, 3)), color=GREY, lw=1.0, zorder=2)
ax.text(5.1, 6.5, "ISL", ha="center", fontsize=6.8, color=GREY)

# gateway
gw = FancyBboxPatch((3.5, 0.55), 3.2, 0.85, boxstyle="round,pad=0.02,rounding_size=0.08",
                    facecolor="#eef1f5", edgecolor=GREY, lw=1.2, zorder=6)
ax.add_patch(gw)
ax.text(5.1, 0.97, "gateway + SMF", ha="center", va="center", fontsize=7.3,
        weight="bold", color=GREY, zorder=7)
ax.plot([4.0, 4.0], [1.4, 1.72], color=GREY, lw=1.0, zorder=6)
ax.add_patch(Polygon([[3.75, 1.78],[4.25, 1.78],[4.15, 1.66],[3.85, 1.66]],
                     closed=True, facecolor="white", edgecolor=GREY, lw=1.0, zorder=6))

# UE
ax.add_patch(FancyBboxPatch((0.5, 0.7), 0.48, 0.82,
             boxstyle="round,pad=0.01,rounding_size=0.06",
             facecolor="white", edgecolor=GREY, lw=1.1, zorder=6))
ax.text(0.74, 0.4, "UE", ha="center", fontsize=6.8, color=GREY)

# service link (UE -> source), label offset to the left, away from boxes
ax.annotate("", xy=(1.95, 5.3), xytext=(0.85, 1.55),
            arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.0))
ax.text(0.5, 3.5, "service", color=GREY, fontsize=6.8, rotation=72,
        ha="right", va="center")

# feeder link (gateway <-> source), thick blue
ax.annotate("", xy=(2.9, 5.3), xytext=(4.5, 1.45),
            arrowprops=dict(arrowstyle="<|-|>", color=BLUE, lw=2.0))
ax.text(3.02, 3.5, "feeder link\nN4/PFCP ($k$ RTTs)", color=BLUE, fontsize=6.8,
        ha="left", va="center",
        path_effects=[pe.withStroke(linewidth=2.6, foreground="white")])

# feeder link (gateway <-> target), thin dashed
ax.annotate("", xy=(7.35, 5.5), xytext=(6.3, 1.45),
            arrowprops=dict(arrowstyle="<|-|>", color=BLUE, lw=1.0,
                            linestyle=(0, (4, 3)), alpha=0.55))

ax.text(-0.2, 7.05, "(a)", fontsize=8, weight="bold", color=GREY)

# ========================= (b) timing budget =============================
bx = fig.add_subplot(gs[1]); bx.set_xlim(0, 10); bx.set_ylim(-1.9, 2.0); bx.axis("off")
x_cul, x_star, x_dl, y = 0.55, 5.7, 9.3, 0.0

bx.annotate("", xy=(9.85, y), xytext=(0.1, y),
            arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.1))
bx.text(9.9, y-0.24, "$t$", fontsize=8, color=GREY)
# tick labels: t* raised slightly and nudged so it clears the bar labels
for x, lab, dy in [(x_cul, "$t_{cul}$", -0.36), (x_star, "$t^{*}$", -0.36),
                   (x_dl, "$t_{dl}$", -0.60)]:
    bx.plot([x, x], [y-0.09, y+0.09], color=GREY, lw=1.1)
    bx.text(x, y+dy, lab, ha="center",
            va="bottom" if dy > 0 else "top", fontsize=7.3, color=GREY)

def brace(x0, x1, yb, label, up=True, color=GREY, lift=0.24):
    xm, s = (x0+x1)/2, (1 if up else -1)
    h = 0.14*s
    bx.plot([x0, x0], [yb, yb+h], color=color, lw=1.0)
    bx.plot([x1, x1], [yb, yb+h], color=color, lw=1.0)
    bx.plot([x0, x1], [yb+h, yb+h], color=color, lw=1.0)
    bx.plot([xm, xm], [yb+h, yb+h+0.10*s], color=color, lw=1.0)
    bx.text(xm, yb+h+lift*s, label, ha="center",
            va="bottom" if up else "top", fontsize=7.0, color=color)

brace(x_cul, x_dl, 0.55, r"usable margin $M=t_{dl}-t_{cul}$", up=True)

# budget bar
yb0, yb1 = -0.30, -0.02
split = x_star + (x_dl-x_star)*0.72
bx.add_patch(Rectangle((x_star, yb0), split-x_star, yb1-yb0,
                       facecolor="#bcd2f0", edgecolor=GREY, lw=0.9))
bx.add_patch(Rectangle((split, yb0), x_dl-split, yb1-yb0,
                       facecolor="#f6c99a", edgecolor=GREY, lw=0.9))
for f in (0.25, 0.5, 0.75):
    xx = x_star + (split-x_star)*f
    bx.plot([xx, xx], [yb0, yb1], color=BLUE, lw=0.8)
# labels for the two segments, on a single line below the bar, well separated
bx.text((x_star+split)/2, yb0-0.16, r"$k\,\mathrm{RTT}_{\mathrm{fdr}}(t^{*})$",
        ha="center", va="top", fontsize=6.8, color=GREY)
xm_tp = split+(x_dl-split)/2
bx.annotate(r"$T_{\mathrm{proc}}$", xy=(xm_tp, (yb0+yb1)/2), xytext=(x_dl+0.35, 0.62),
            fontsize=6.8, color=GREY, ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=GREY, lw=0.6))

brace(x_star, x_dl, -0.92, r"$\delta_{\mathrm{req}}(t^{*})=t_{dl}-t^{*}$",
      up=False, color=GREY, lift=0.22)

bx.text(-0.2, 1.7, "(b)", fontsize=8, weight="bold", color=GREY)
fig.savefig("fig_architecture.png", dpi=300, bbox_inches="tight", pad_inches=0.02)
print("done")
