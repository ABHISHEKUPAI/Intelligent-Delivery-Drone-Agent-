import sys

from scenarios import small_calm, medium_windy, multi_delivery, wind_detour, recharge_demo
from delivery_planner import compare_tours
from simulation import run_mission

SCENARIOS = {f.__name__: f for f in (small_calm, medium_windy, multi_delivery, wind_detour, recharge_demo)}


def run_single(name, method):
    sc = SCENARIOS[name]()
    print(f"\n==================================================")
    print(f"  SCENARIO: {sc.title} (Battery Capacity: {sc.battery})")
    print(f"==================================================")
    print("Map Legend: D=Depot, pX=Pickup X, dX=Drop-off X, #=No-Fly Zone, ^v><=Wind Direction\n")
    print(sc.env.render(), "\n")

    plans, gaps = compare_tours(sc.env)
    print("--- Tour Sequence Comparison (Cost, % above optimal order) ---")
    for m, p in plans.items():
        print(f"  {m:<8} cost {p.cost:<5} (+{gaps[m]:.1f}%)   Sequence: {' '.join(s.label for s in p.order)}")

    print(f"\n--- Mission Execution Log (Planning Method: {method}) ---")
    r = run_mission(sc.env, sc.battery, method=method)
    print("\n".join(r.log))

    avg = f"{r.avg_delivery_time:.1f}" if r.avg_delivery_time is not None else "n/a"
    print("\n--- Mission Performance Metrics ---")
    print(f"  Total Mission Cost      : {r.total_cost}")
    print(f"  Deliveries Completed    : {r.deliveries_completed} / {r.deliveries_total}")
    print(f"  Average Delivery Time   : {avg} steps")
    print(f"  Path Optimality Gap     : {r.path_gap_pct:.2f}% (A* vs UCS)")
    print(f"  Computation Time        : {r.computation_time_s * 1000:.2f} ms")
    print(f"  Battery Violations      : {r.battery_violations}")
    print(f"  Recharges               : {r.recharges}")
    print(f"  Nodes Expanded          : A* {r.astar_nodes}, UCS {r.ucs_nodes}\n")


def run_all_summary(method="nn2opt"):
    print(f"\n===================================================================================================")
    print(f"  SUMMARY RESULTS TABLE FOR ALL SCENARIOS (Planning Method: {method})")
    print(f"===================================================================================================")
    print(f"{'Scenario':<16}{'Grid':<8}{'Deliv':<7}{'Cost':>6}{'Done':>8}{'Avg Time':>10}{'Gap %':>8}{'Comp(ms)':>10}{'Recharges':>11}{'Violations':>12}")
    print("-" * 99)
    for make in (small_calm, medium_windy, multi_delivery, wind_detour, recharge_demo):
        sc = make()
        r = run_mission(sc.env, sc.battery, method=method)
        done = f"{r.deliveries_completed}/{r.deliveries_total}"
        avg = f"{r.avg_delivery_time:.1f}" if r.avg_delivery_time is not None else "n/a"
        grid = f"{sc.env.rows}x{sc.env.cols}"
        print(f"{sc.name:<16}{grid:<8}{r.deliveries_total:<7}{r.total_cost:>6}{done:>8}{avg:>10}{r.path_gap_pct:>7.1f}%{r.computation_time_s * 1000:>10.2f}{r.recharges:>11}{r.battery_violations:>12}")
    print("-" * 99 + "\n")


def main():
    arg1 = sys.argv[1] if len(sys.argv) > 1 else "recharge_demo"
    method = sys.argv[2] if len(sys.argv) > 2 else "nn2opt"

    if arg1 == "all":
        run_all_summary(method)
    elif arg1 in SCENARIOS:
        run_single(arg1, method)
    else:
        print(f"Unknown option '{arg1}'. Available options:")
        print(f"  Scenarios : {', '.join(SCENARIOS)}")
        print(f"  Run All   : 'all'")
        print(f"  Methods   : nn, nn2opt, optimal")


if __name__ == "__main__":
    main()
