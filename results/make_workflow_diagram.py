"""Draw the yard voice-command workflow diagram (results/workflow_diagram.png)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Wedge, Arc, Rectangle, Polygon, FancyArrowPatch

plt.rcParams["font.family"] = "Arial"
BLUE, BLUE_BG = "#2f6db5", "#eaf1fb"
GOLD, GOLD_BG = "#c98a1a", "#fdf4e3"
GREEN, GREEN_BG = "#2e8b3d", "#e8f5ea"
RED, RED_BG = "#c0453b", "#fbeaea"
INK, SOFT = "#222222", "#555555"

fig, ax = plt.subplots(figsize=(11, 6.4), dpi=220)
ax.set_xlim(-2, 110); ax.set_ylim(0, 66); ax.axis("off")


def card(x, y, w, h, edge, fill):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=2.2",
                                linewidth=2, edgecolor=edge, facecolor=fill))


def badge(cx, cy, color):
    ax.add_patch(Circle((cx, cy), 4.3, facecolor="white", edgecolor=color, linewidth=2.2, zorder=3))


def arrow(x1, y1, x2, y2, color=SOFT, style="-|>", ls="-", rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=16, linewidth=2,
                                 color=color, linestyle=ls, connectionstyle=f"arc3,rad={rad}", zorder=2))


# ---------- icons (drawn at a centre point) ----------
def icon_person(cx, cy, c):
    ax.add_patch(Circle((cx - 0.8, cy + 1.0), 1.1, color=c, zorder=4))
    ax.add_patch(Wedge((cx - 0.8, cy - 1.9), 2.1, 0, 180, color=c, zorder=4))
    for r in (1.6, 2.6):
        ax.add_patch(Arc((cx + 1.2, cy + 0.6), r, r * 1.3, theta1=-50, theta2=50, color=c, linewidth=1.6, zorder=4))


def icon_mic(cx, cy, c):
    ax.add_patch(FancyBboxPatch((cx - 0.8, cy - 0.3), 1.6, 2.8, boxstyle="round,pad=0,rounding_size=0.8", color=c, zorder=4))
    ax.add_patch(Arc((cx, cy + 0.4), 3.2, 3.6, theta1=180, theta2=360, color=c, linewidth=1.6, zorder=4))
    ax.plot([cx, cx], [cy - 1.4, cy - 2.4], color=c, linewidth=1.6, zorder=4)
    ax.plot([cx - 1.0, cx + 1.0], [cy - 2.4, cy - 2.4], color=c, linewidth=1.6, zorder=4)


def icon_chip(cx, cy, c):
    ax.add_patch(FancyBboxPatch((cx - 1.8, cy - 1.8), 3.6, 3.6, boxstyle="round,pad=0,rounding_size=0.4",
                                facecolor="white", edgecolor=c, linewidth=1.8, zorder=4))
    for d in (-1.0, 0, 1.0):
        ax.plot([cx + d, cx + d], [cy + 1.8, cy + 2.6], color=c, linewidth=1.4, zorder=4)
        ax.plot([cx + d, cx + d], [cy - 1.8, cy - 2.6], color=c, linewidth=1.4, zorder=4)
        ax.plot([cx - 1.8, cx - 2.6], [cy + d, cy + d], color=c, linewidth=1.4, zorder=4)
        ax.plot([cx + 1.8, cx + 2.6], [cy + d, cy + d], color=c, linewidth=1.4, zorder=4)
    ax.text(cx, cy, "AI", ha="center", va="center", fontsize=8, fontweight="bold", color=c, zorder=5)


def icon_checklist(cx, cy, c):
    ax.add_patch(FancyBboxPatch((cx - 1.8, cy - 2.4), 3.6, 4.8, boxstyle="round,pad=0,rounding_size=0.4",
                                facecolor="white", edgecolor=c, linewidth=1.8, zorder=4))
    for i, yy in enumerate((cy + 1.2, cy, cy - 1.2)):
        ax.plot([cx - 1.1, cx - 0.8, cx - 0.3], [yy, yy - 0.35, yy + 0.4], color=c, linewidth=1.4, zorder=5)
        ax.plot([cx + 0.1, cx + 1.2], [yy, yy], color=c, linewidth=1.4, zorder=5)


def icon_tick(cx, cy, c):
    ax.add_patch(Circle((cx, cy), 2.4, color=c, zorder=4))
    ax.plot([cx - 1.2, cx - 0.3, cx + 1.3], [cy, cy - 1.0, cy + 1.0], color="white", linewidth=2.6, zorder=5,
            solid_capstyle="round")


def icon_bubble(cx, cy, c):
    ax.add_patch(FancyBboxPatch((cx - 2.4, cy - 1.2), 4.8, 3.2, boxstyle="round,pad=0,rounding_size=1.0", color=c, zorder=4))
    ax.add_patch(Polygon([[cx - 1.2, cy - 1.1], [cx - 1.8, cy - 2.4], [cx - 0.2, cy - 1.1]], color=c, zorder=4))
    ax.text(cx, cy + 0.4, "?", ha="center", va="center", fontsize=12, fontweight="bold", color="white", zorder=5)


def icon_repeat(cx, cy, c):
    ax.add_patch(Circle((cx, cy), 2.4, color=c, zorder=4))
    ax.add_patch(Arc((cx, cy), 2.8, 2.8, theta1=60, theta2=340, color="white", linewidth=2.2, zorder=5))
    ax.add_patch(Polygon([[cx + 0.4, cy + 1.9], [cx + 1.6, cy + 1.0], [cx + 0.3, cy + 0.6]], color="white", zorder=5))


def text(x, y, s, size=11, color=INK, weight="normal", style="normal"):
    ax.text(x, y, s, ha="center", va="center", fontsize=size, color=color, fontweight=weight, fontstyle=style, zorder=5)


# ---------- title ----------
text(55, 63.5, "How my yard voice-command system works", size=17, weight="bold")

# ---------- top row: 4 steps ----------
steps = [
    (2, "1  Worker speaks", '"move 4471\nto door 6"', icon_person, BLUE, BLUE_BG),
    (29, "2  Whisper", "turns speech\ninto text", icon_mic, BLUE, BLUE_BG),
    (56, "3  AI model reads", "Qwen · Laya · Jev\naction · trailer · door", icon_chip, BLUE, BLUE_BG),
    (83, "4  Rules decide", "check the yard:\ntrailer? door free?", icon_checklist, GOLD, GOLD_BG),
]
W, top_y, top_h = 24, 33, 20
for x, title, sub, icon, edge, fill in steps:
    card(x, top_y, W, top_h, edge, fill)
    badge(x + W / 2, top_y + top_h - 0.5, edge)
    icon(x + W / 2, top_y + top_h - 0.5, edge)
    text(x + W / 2, top_y + 9.6, title, size=12.5, weight="bold")
    text(x + W / 2, top_y + 4.6, sub, size=10.5, color=SOFT)
for x in (26, 53, 80):
    arrow(x + 0.3, top_y + 8, x + 2.7, top_y + 8)

# ---------- bottom row: 3 decisions ----------
outs = [
    (8, "ACT", "do the action", icon_tick, GREEN, GREEN_BG),
    (43, "READ BACK", '"4471 to door 6,\nright?"', icon_bubble, GOLD, GOLD_BG),
    (78, "ASK AGAIN", '"Sorry, please\nsay it again"', icon_repeat, RED, RED_BG),
]
OW, bot_y, bot_h = 24, 4, 17
for x, title, sub, icon, edge, fill in outs:
    card(x, bot_y, OW, bot_h, edge, fill)
    icon(x + 5.2, bot_y + bot_h / 2 + 0.3, edge)
    text(x + 15.2, bot_y + 11.4, title, size=13, weight="bold", color=edge)
    text(x + 15.2, bot_y + 5.6, sub, size=10.5, color=SOFT)

# rules -> 3 outcomes
ax.plot([95, 95], [top_y, 27.5], color=SOFT, linewidth=2, zorder=2)
ax.plot([20, 95], [27.5, 27.5], color=SOFT, linewidth=2, zorder=2)
for x in (20, 55, 90):
    arrow(x, 27.5, x, bot_y + bot_h + 0.3)

# read back answers
arrow(42.8, bot_y + 5, 32.2, bot_y + 5, color=GREEN)
text(37.5, bot_y + 7, '"yes"', size=9.5, color=GREEN, style="italic")
arrow(67.2, bot_y + 5, 77.8, bot_y + 5, color=RED)
text(72.5, bot_y + 7, '"no"', size=9.5, color=RED, style="italic")

# ask again -> back to worker
ax.plot([102, 108, 108], [bot_y + bot_h / 2, bot_y + bot_h / 2, 59], color=RED, linewidth=2, linestyle=(0, (5, 3)), zorder=1)
ax.plot([108, -0.5, -0.5], [59, 59, top_y + 8], color=RED, linewidth=2, linestyle=(0, (5, 3)), zorder=1)
arrow(-0.5, top_y + 8, 1.8, top_y + 8, color=RED)
text(55, 60.6, "the worker says it again", size=9.5, color=RED, style="italic")

fig.savefig("workflow_diagram.png", bbox_inches="tight", pad_inches=0.15, facecolor="white")
print("saved workflow_diagram.png")
