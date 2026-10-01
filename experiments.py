# experiments.py
# Runs every scenario, collects the metrics, saves results/experiment_results.csv
# and then draws the figures (see visualization.py).
#
#   py -3.11 experiments.py
#
# Computation time is the median of 15 runs, so it can differ a little from
# machine to machine. Every other number is deterministic.
import csv
import os
import statistics

from scenarios import small_calm, medium_windy, multi_delivery, wind_detour, recharge_demo
from delivery_planner import compare_tours
from simulation import run_mission

RESULTS_DIR = "results"
CSV_PATH = os.path.join(RESULTS_DIR, "experiment_results.csv")
TIMING_REPEATS = 15

COLUMNS = [
    "scenario", "grid", "deliveries", "battery",
    # the six metrics from the abstract
    "total_mission_cost", "deliveries_completed", "avg_delivery_time",
    "path_optimality_gap_pct", "computation_time_ms", "battery_violations",
    # extra numbers
    "recharges", "astar_nodes_expanded", "ucs_nodes_expanded",
    "nn_tour_cost", "nn2opt_tour_cost", "optimal_tour_cost",
    "nn_gap_pct", "nn2opt_gap_pct",
]


def run_scenario(sc):
    plans, gaps = compare_tours(sc.env)
    runs = [run_mission(sc.env, sc.battery, method="nn2opt") for _ in range(TIMING_REPEATS)]
    mission = runs[0]
    row = {
        "scenario": sc.name,
        "grid": f"{sc.env.rows}x{sc.env.cols}",
        "deliveries": len(sc.env.pickups),
        "battery": sc.battery,
        "total_mission_cost": mission.total_cost,
        "deliveries_completed": mission.deliveries_completed,
        "avg_delivery_time": round(mission.avg_delivery_time, 2),
        "path_optimality_gap_pct": round(mission.path_gap_pct, 2),
        "computation_time_ms": round(statistics.median(r.computation_time_s for r in runs) * 1000, 2),
        "battery_violations": mission.battery_violations,
        "recharges": mission.recharges,
        "astar_nodes_expanded": mission.astar_nodes,
        "ucs_nodes_expanded": mission.ucs_nodes,
        "nn_tour_cost": plans["nn"].cost,
        "nn2opt_tour_cost": plans["nn2opt"].cost,
        "optimal_tour_cost": plans["optimal"].cost,
        "nn_gap_pct": round(gaps["nn"], 2),
        "nn2opt_gap_pct": round(gaps["nn2opt"], 2),
    }
    return row, mission


def run_all():
    rows, missions = [], {}
    for make in (small_calm, medium_windy, multi_delivery, wind_detour, recharge_demo):
        sc = make()
        row, mission = run_scenario(sc)
        rows.append(row)
        missions[sc.name] = (sc, mission)
    return rows, missions


def save_csv(rows):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def print_table(rows):
    print("\nSix metrics from the abstract")
    print(f"{'scenario':<16}{'cost':>6}{'delivered':>11}{'avg time':>10}{'gap %':>7}{'comp ms':>9}{'violations':>12}")
    for r in rows:
        done = f"{r['deliveries_completed']}/{r['deliveries']}"
        print(f"{r['scenario']:<16}{r['total_mission_cost']:>6}{done:>11}{r['avg_delivery_time']:>10}"
              f"{r['path_optimality_gap_pct']:>7}{r['computation_time_ms']:>9}{r['battery_violations']:>12}")
    print("\nA* vs UCS (nodes expanded) and delivery tour costs")
    print(f"{'scenario':<16}{'A*':>7}{'UCS':>7}{'NN':>6}{'NN+2opt':>9}{'optimal':>9}{'recharges':>11}")
    for r in rows:
        print(f"{r['scenario']:<16}{r['astar_nodes_expanded']:>7}{r['ucs_nodes_expanded']:>7}{r['nn_tour_cost']:>6}"
              f"{r['nn2opt_tour_cost']:>9}{r['optimal_tour_cost']:>9}{r['recharges']:>11}")


if __name__ == "__main__":
    import visualization

    rows, missions = run_all()
    save_csv(rows)
    print_table(rows)
    print(f"\nSaved {CSV_PATH}")
    visualization.make_all_figures(rows, missions)
