import time
from dataclasses import dataclass, field

from astar import astar

INF = float("inf")
MAX_BRUTE_FORCE_DELIVERIES = 5


@dataclass(frozen=True)
class Stop:
    delivery: str
    kind: str          
    cell: tuple

    @property
    def label(self):
        return ("P" if self.kind == "pickup" else "D") + self.delivery


def make_stops(env):
    stops = []
    for name in env.pickups:
        stops.append(Stop(name, "pickup", env.pickups[name]))
        stops.append(Stop(name, "drop", env.dropoffs[name]))
    return stops


class CostTable:
    def __init__(self, env):
        self.env = env
        self.cache = {}
        self.search_time = 0.0

    def cost(self, a, b):
        if a == b:
            return 0
        if (a, b) not in self.cache:
            res = astar(self.env, a, b)
            self.search_time += res.time_s
            self.cache[(a, b)] = res.cost if res.found else INF
        return self.cache[(a, b)]


def is_valid_order(order):
    picked_up = set()
    for stop in order:
        if stop.kind == "pickup":
            picked_up.add(stop.delivery)
        elif stop.delivery not in picked_up:
            return False
    return True


def tour_cost(order, depot, table):
    total = 0
    here = depot
    for stop in order:
        total += table.cost(here, stop.cell)
        here = stop.cell
    return total + table.cost(here, depot)


def nearest_neighbor(stops, depot, table):
    remaining = list(stops)
    picked_up = set()
    order = []
    here = depot
    while remaining:
        options = [s for s in remaining if s.kind == "pickup" or s.delivery in picked_up]
        nxt = min(options, key=lambda s: table.cost(here, s.cell))
        order.append(nxt)
        remaining.remove(nxt)
        if nxt.kind == "pickup":
            picked_up.add(nxt.delivery)
        here = nxt.cell
    return order


def two_opt(order, depot, table):
    stats = {"accepted": 0, "rejected_precedence": 0, "rejected_no_gain": 0}
    best = list(order)
    best_cost = tour_cost(best, depot, table)
    improved = True
    while improved:
        improved = False
        for i in range(len(best) - 1):
            for j in range(i + 1, len(best)):
                candidate = best[:i] + best[i:j + 1][::-1] + best[j + 1:]
                if not is_valid_order(candidate):
                    stats["rejected_precedence"] += 1
                    continue
                cost = tour_cost(candidate, depot, table)
                if cost < best_cost:
                    best, best_cost = candidate, cost
                    stats["accepted"] += 1
                    improved = True
                    break
                stats["rejected_no_gain"] += 1
            if improved:
                break
    return best, stats


def brute_force_best(stops, depot, table):
    if len(stops) // 2 > MAX_BRUTE_FORCE_DELIVERIES:
        raise ValueError("too many deliveries for brute force")
    best = {"order": None, "cost": INF}
    count = [0]

    def extend(order, remaining):
        if not remaining:
            count[0] += 1
            c = tour_cost(order, depot, table)
            if c < best["cost"]:
                best["order"], best["cost"] = list(order), c
            return
        picked_up = {s.delivery for s in order if s.kind == "pickup"}
        for s in remaining:
            if s.kind == "drop" and s.delivery not in picked_up:
                continue
            order.append(s)
            extend(order, [r for r in remaining if r != s])
            order.pop()

    extend([], list(stops))
    return best["order"], best["cost"], count[0]


@dataclass
class TourPlan:
    method: str
    order: list
    cost: float
    time_s: float
    two_opt_stats: dict = field(default_factory=dict)
    valid_orders_checked: int = 0


def plan_tour(env, method="nn2opt", table=None):
    table = table or CostTable(env)
    stops = make_stops(env)
    for s in stops:
        if table.cost(env.depot, s.cell) == INF or table.cost(s.cell, env.depot) == INF:
            raise ValueError(f"stop {s.label} at {s.cell} can't be reached from the depot")

    t0 = time.perf_counter()
    stats, checked = {}, 0
    if method == "nn":
        order = nearest_neighbor(stops, env.depot, table)
    elif method == "nn2opt":
        order = nearest_neighbor(stops, env.depot, table)
        order, stats = two_opt(order, env.depot, table)
    elif method == "optimal":
        order, _, checked = brute_force_best(stops, env.depot, table)
    else:
        raise ValueError(f"unknown method {method}")
    elapsed = time.perf_counter() - t0
    return TourPlan(method, order, tour_cost(order, env.depot, table), elapsed, stats, checked)


def compare_tours(env):
    table = CostTable(env)
    plans = {m: plan_tour(env, m, table) for m in ("nn", "nn2opt", "optimal")}
    best = plans["optimal"].cost
    gaps = {m: ((p.cost - best) / best * 100 if best > 0 else 0.0) for m, p in plans.items()}
    return plans, gaps
