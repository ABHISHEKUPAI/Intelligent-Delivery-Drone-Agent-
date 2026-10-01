# main.py
# Runs one scenario from the terminal and prints the map, the tour comparison,
# the mission log and the six metrics.
#
#   py -3.11 main.py                      (runs recharge_demo)
#   py -3.11 main.py medium_windy nn2opt
#   scenarios: small_calm, medium_windy, multi_delivery, wind_detour, recharge_demo
#   methods:   nn, nn2opt, optimal
import sys

from scenarios import small_calm, medium_windy, multi_delivery, wind_detour, recharge_demo
from delivery_planner import compare_tours
from simulation import run_mission

SCENARIOS = {f.__name__: f for f in (small_calm, medium_windy, multi_delivery, wind_detour, recharge_demo)}


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "recharge_demo"
    method = sys.argv[2] if len(sys.argv) > 2 else "nn2opt"
    if name not in SCENARIOS:
        sys.exit(f"unknown scenario '{name}', pick one of: {', '.join(SCENARIOS)}")
    sc = SCENARIOS[name]()

    print(f"=== {sc.title}  (battery {sc.battery}) ===")
    print("D = depot, pX = pickup X, dX = drop-off X, # = no-fly, arrows = wind direction\n")
    print(sc.env.render(), "\n")

    plans, gaps = compare_tours(sc.env)
    print("Tour comparison (cost, % above the best possible order):")
    for m, p in plans.items():
        print(f"  {m:7} cost {p.cost:<5} +{gaps[m]:.1f}%   {' '.join(s.label for s in p.order)}")

    print(f"\n--- mission log (planning method: {method}) ---")
    r = run_mission(sc.env, sc.battery, method=method)
    print("\n".join(r.log))

    avg = f"{r.avg_delivery_time:.1f}" if r.avg_delivery_time is not None else "n/a"
    print("\n--- results ---")
    print(f"Total mission cost      : {r.total_cost}")
    print(f"Deliveries completed    : {r.deliveries_completed} / {r.deliveries_total}")
    print(f"Average delivery time   : {avg} steps")
    print(f"Path optimality gap     : {r.path_gap_pct:.2f}% (A* vs UCS)")
    print(f"Computation time        : {r.computation_time_s * 1000:.2f} ms")
    print(f"Battery violations      : {r.battery_violations}")
    print(f"Recharges               : {r.recharges}")
    print(f"Nodes expanded          : A* {r.astar_nodes}, UCS {r.ucs_nodes}")


if __name__ == "__main__":
    main()
