# visualization.py
# Draws the figures for the presentation. experiments.py calls make_all_figures().
import os

import matplotlib
matplotlib.use("Agg")                      # draw to files, no window needed
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Circle, Polygon, Patch

from scenarios import wind_detour
from simulation import run_mission

FIG_DIR = os.path.join("results", "figures")

NAVY, TEAL, AMBER, GREY = "#0F2A43", "#17A398", "#F4A259", "#9AA5B1"
NOFLY, GRID_LINE = "#3A3F47", "#D5DDE3"
ARROW = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
SHORT = {"small_calm": "Small", "medium_windy": "Medium\nwind", "multi_delivery": "4 deliveries",
         "wind_detour": "Wind\ndetour", "recharge_demo": "Recharge"}


def _save(fig, name):
    os.makedirs(FIG_DIR, exist_ok=True)
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", path)


# ---------- the grid ----------
def draw_map(ax, env, legs=None, order=None, show_strength=False, recharged=False):
    ax.set_xlim(-0.5, env.cols - 0.5)
    ax.set_ylim(env.rows - 0.5, -0.5)
    ax.set_aspect("equal")
    ax.axis("off")

    for r in range(env.rows):
        for c in range(env.cols):
            cell = (r, c)
            if cell in env.no_fly:
                color = NOFLY
            elif cell in env.wind:
                color = plt.cm.Blues(0.15 + 0.5 * env.wind[cell][1] / 6)
            else:
                color = "white"
            ax.add_patch(Rectangle((c - 0.5, r - 0.5), 1, 1, facecolor=color,
                                   edgecolor=GRID_LINE, linewidth=0.6))

    for (r, c), (d, strength) in env.wind.items():
        dx, dy = ARROW[d]
        ax.annotate("", xy=(c + 0.32 * dx, r + 0.32 * dy), xytext=(c - 0.32 * dx, r - 0.32 * dy),
                    arrowprops=dict(arrowstyle="-|>", color="#164A73", lw=1.2, mutation_scale=9))
        if show_strength:
            ax.text(c + 0.42, r + 0.42, str(strength), fontsize=6, ha="right", va="bottom", color="#164A73")

    # route first, so the markers sit on top of it
    if legs:
        cmap = plt.cm.plasma
        n = len(legs)
        for k, (_, _, path, _) in enumerate(legs):
            if len(path) < 2:
                continue
            shade = cmap(0.1 + 0.75 * k / max(n - 1, 1))
            off = ((k * 3) % 5 - 2) * 0.06            # small shift so overlapping legs stay visible
            xs = [c + off for _, c in path]
            ys = [r + off for r, _ in path]
            ax.plot(xs, ys, color=shade, linewidth=2.2, solid_capstyle="round", zorder=3)
            ax.annotate("", xy=(xs[-1], ys[-1]), xytext=(xs[-2], ys[-2]),
                        arrowprops=dict(arrowstyle="-|>", color=shade, lw=2, mutation_scale=12), zorder=4)

    dr, dc = env.depot
    ax.add_patch(Rectangle((dc - 0.38, dr - 0.38), 0.76, 0.76, facecolor="#2E9E5B", edgecolor="white", zorder=5))
    for name, (r, c) in env.pickups.items():
        ax.add_patch(Polygon([(c, r - 0.4), (c - 0.4, r + 0.33), (c + 0.4, r + 0.33)],
                             facecolor=AMBER, edgecolor="white", zorder=5))
        ax.text(c, r + 0.12, name, ha="center", va="center", fontsize=7, fontweight="bold", color=NAVY, zorder=6)
    for name, (r, c) in env.dropoffs.items():
        ax.add_patch(Circle((c, r), 0.4, facecolor="#D64550", edgecolor="white", zorder=5))
        ax.text(c, r, name, ha="center", va="center", fontsize=7, fontweight="bold", color="white", zorder=6)

    if recharged:
        ax.text(dc + 0.5, dr - 0.36, "recharged here", ha="left", va="center", fontsize=7.5,
                color="#1E7A43", fontweight="bold", zorder=8,
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.85))

    if order:
        for i, stop in enumerate(order, 1):
            r, c = stop.cell
            ax.text(c - 0.42, r - 0.42, str(i), ha="center", va="center", fontsize=6.5, color="white",
                    zorder=7, bbox=dict(boxstyle="circle,pad=0.15", facecolor=NAVY, edgecolor="none"))


def _legend_items(with_wind=True, with_route=False):
    items = [Patch(facecolor="#2E9E5B", label="Depot"),
             Line2D([], [], marker="^", color="none", markerfacecolor=AMBER, markersize=9, label="Pickup"),
             Line2D([], [], marker="o", color="none", markerfacecolor="#D64550", markersize=9, label="Drop-off"),
             Patch(facecolor=NOFLY, label="No-fly zone")]
    if with_wind:
        items.append(Patch(facecolor=plt.cm.Blues(0.4), label="Wind (arrow = direction)"))
    if with_route:
        items.append(Line2D([], [], color=plt.cm.plasma(0.45), linewidth=2.2, label="Route"))
    return items


def _legend(ax, with_wind=True, with_route=False):
    items = _legend_items(with_wind, with_route)
    ax.legend(handles=items, loc="upper center", bbox_to_anchor=(0.5, -0.01),
              ncol=len(items), fontsize=8, frameon=False, handlelength=1.2, columnspacing=1.2)


# ---------- figure 1: route on the grid ----------
def fig_route(sc, mission):
    fig, ax = plt.subplots(figsize=(7, 6.4))
    draw_map(ax, sc.env, legs=mission.legs, order=mission.order, recharged=mission.recharges > 0)
    ax.set_title(f"{sc.title}\ncost {mission.total_cost}, {mission.deliveries_completed}/{mission.deliveries_total} delivered, "
                 f"{mission.recharges} recharge(s)   (numbers = stop order)", fontsize=10, color=NAVY)
    _legend(ax, with_route=True)
    sm = ScalarMappable(cmap=plt.cm.plasma, norm=Normalize(0.1, 0.85))
    cb = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.02, ticks=[0.1, 0.85])
    cb.ax.set_yticklabels(["start", "end"], fontsize=8)
    cb.outline.set_visible(False)
    _save(fig, f"fig1_route_{sc.name}.png")


# ---------- figure 2: wind and no-fly zones ----------
def fig_wind_nofly(sc):
    fig, ax = plt.subplots(figsize=(7, 6.4))
    draw_map(ax, sc.env, show_strength=True)
    ax.set_title(f"{sc.title}: no-fly zones and wind\n(small number = wind strength)", fontsize=10, color=NAVY)
    _legend(ax)
    _save(fig, "fig2_wind_nofly_zones.png")


def fig_wind_changes_route():
    calm, windy = wind_detour(False), wind_detour(True)
    rc = run_mission(calm.env, calm.battery)
    rw = run_mission(windy.env, windy.battery)
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.2))
    for ax, sc, res, label in ((axes[0], calm, rc, "No wind"), (axes[1], windy, rw, "Headwind band (against eastbound flight)")):
        draw_map(ax, sc.env, legs=res.legs, order=res.order)
        ax.set_title(f"{label}: total cost {res.total_cost}", fontsize=11, color=NAVY)
    fig.legend(handles=_legend_items(with_route=True), loc="lower center", ncol=6, fontsize=9,
               frameon=False, bbox_to_anchor=(0.5, -0.03))
    fig.suptitle("Same map, same delivery: the wind changes the route", fontsize=12, color=NAVY)
    _save(fig, "fig2b_wind_changes_route.png")


# ---------- bar chart helpers ----------
def _grouped_bars(ax, groups, series, colors, labels):
    width = 0.8 / len(series)
    for i, (values, color, label) in enumerate(zip(series, colors, labels)):
        xs = [g + (i - (len(series) - 1) / 2) * width for g in range(len(groups))]
        bars = ax.bar(xs, values, width * 0.92, color=color, label=label)
        for b, v in zip(bars, values):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(), f"{v:g}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups, fontsize=9)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def fig_astar_vs_ucs(rows):
    groups = [SHORT[r["scenario"]] for r in rows]
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    _grouped_bars(ax, groups, [[r["astar_nodes_expanded"] for r in rows], [r["ucs_nodes_expanded"] for r in rows]],
                  [TEAL, GREY], ["A* (Manhattan heuristic)", "Uniform-Cost Search"])
    ax.set_ylabel("Nodes expanded (whole mission)")
    worst_gap = max(r["path_optimality_gap_pct"] for r in rows)
    ax.set_title(f"A* vs UCS: same path costs (max gap {worst_gap:g}%), fewer nodes for A*", fontsize=11, color=NAVY)
    ax.legend(frameon=False)
    _save(fig, "fig3_astar_vs_ucs.png")


def fig_tour_comparison(rows):
    groups = [SHORT[r["scenario"]] for r in rows]
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    _grouped_bars(ax, groups,
                  [[r["nn_tour_cost"] for r in rows], [r["nn2opt_tour_cost"] for r in rows],
                   [r["optimal_tour_cost"] for r in rows]],
                  [GREY, TEAL, AMBER], ["Nearest Neighbor", "NN + 2-opt", "True optimal (brute force)"])
    ax.set_ylabel("Delivery tour cost")
    ax.set_title("Delivery order: heuristics vs the true best order", fontsize=11, color=NAVY)
    ax.legend(frameon=False)
    _save(fig, "fig4_tour_comparison.png")


def fig_metrics(rows):
    groups = [SHORT[r["scenario"]] for r in rows]
    panels = [
        ("Total mission cost", "total_mission_cost", "{:g}"),
        ("Deliveries completed", "deliveries_completed", "{:g}"),
        ("Average delivery time (steps)", "avg_delivery_time", "{:g}"),
        ("Path optimality gap (%)", "path_optimality_gap_pct", "{:g}"),
        ("Computation time (ms)", "computation_time_ms", "{:g}"),
        ("Battery violations", "battery_violations", "{:g}"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(13, 7))
    for ax, (title, key, fmt) in zip(axes.flat, panels):
        values = [r[key] for r in rows]
        bars = ax.bar(range(len(rows)), values, color=TEAL, width=0.65)
        top = max(values) if max(values) > 0 else 1
        ax.set_ylim(0, top * 1.22)
        if max(values) == 0:                       # gap and violations are 0 everywhere
            ax.set_yticks([0])
            ax.text(0.5, 0.5, "0 in every scenario", transform=ax.transAxes, ha="center", va="center",
                    fontsize=12, color=TEAL, fontweight="bold")
        for i, (b, v) in enumerate(zip(bars, values)):
            text = f"{rows[i]['deliveries_completed']}/{rows[i]['deliveries']}" if key == "deliveries_completed" else fmt.format(v)
            ax.text(b.get_x() + b.get_width() / 2, v + top * 0.02, text, ha="center", va="bottom", fontsize=9)
        ax.set_xticks(range(len(rows)))
        ax.set_xticklabels(groups, fontsize=8)
        ax.set_title(title, fontsize=11, color=NAVY)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
    fig.suptitle("Performance metrics for each scenario", fontsize=13, color=NAVY)
    fig.tight_layout()
    _save(fig, "fig5_performance_metrics.png")


def make_all_figures(rows, missions):
    for name, (sc, mission) in missions.items():
        fig_route(sc, mission)
    fig_wind_nofly(missions["medium_windy"][0])
    fig_wind_changes_route()
    fig_astar_vs_ucs(rows)
    fig_tour_comparison(rows)
    fig_metrics(rows)
