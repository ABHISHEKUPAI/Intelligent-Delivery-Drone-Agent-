# simulation.py
# Runs a whole mission: perceive -> reason -> decide -> act.
#
#   plan the stop order (planner)  ->  for each stop:
#       check battery (decide)  ->  recharge if needed
#       plan the path with A*   ->  fly it step by step (act)
#       pick up / drop off
#   finally fly back to the depot.
#
# Battery rule, checked before every leg:
#   battery must cover  (this leg)  +  (flying from the stop back to the depot).
# If it doesn't, the drone goes to the depot, recharges, and then carries on.
import time
from dataclasses import dataclass, field

from astar import astar
from ucs import ucs
from cost_model import path_cost
from drone import Drone
from delivery_planner import plan_tour, CostTable


@dataclass
class MissionResult:
    method: str
    order: list
    total_cost: int = 0
    deliveries_total: int = 0
    deliveries_completed: int = 0
    avg_delivery_time: float = None
    battery_violations: int = 0
    recharges: int = 0
    computation_time_s: float = 0.0
    path_gap_pct: float = 0.0           # A* vs UCS, averaged over all legs flown
    astar_nodes: int = 0
    ucs_nodes: int = 0
    log: list = field(default_factory=list)
    legs: list = field(default_factory=list)       # (from, to, path, cost) for drawing routes


class MissionRunner:
    def __init__(self, env, battery_capacity, method="nn2opt", recharge_time=5):
        self.env = env
        self.drone = Drone(env.depot, battery_capacity)
        self.method = method
        self.recharge_time = recharge_time
        self.t = 0
        self.total_cost = 0
        self.search_time = 0.0
        self.gaps = []
        self.res = None

    # ---------- small helpers ----------
    def _log(self, text):
        self.res.log.append(f"t={self.t:<4} battery={self.drone.battery:<4} {text}")

    def _search(self, a, b):
        # A* for the real path. UCS runs alongside only to check A* got the optimal cost.
        res = astar(self.env, a, b)
        self.search_time += res.time_s
        self.res.astar_nodes += res.nodes_expanded
        if res.found:
            ref = ucs(self.env, a, b)
            self.res.ucs_nodes += ref.nodes_expanded
            self.gaps.append((res.cost - ref.cost) / ref.cost * 100 if ref.cost > 0 else 0.0)
        return res

    def _fly(self, target, why, leg=None):
        # leg can be passed in if we already planned this path for the battery check
        leg = leg or self._search(self.drone.position, target)
        self._log(f"{why}: {self.drone.position} -> {target}, path cost {leg.cost}, {len(leg.path) - 1} steps")
        self.res.legs.append((self.drone.position, target, leg.path, leg.cost))
        for a, b in zip(leg.path, leg.path[1:]):
            c = path_cost(self.env, [a, b])
            self.drone.move_to(b, c)
            self.total_cost += c
            self.t += 1

    def _recharge(self):
        self.drone.recharge()
        self.t += self.recharge_time
        self.res.recharges += 1
        self._log("recharged to full at the depot")

    # ---------- the mission ----------
    def run(self):
        env, drone = self.env, self.drone

        # reason: decide the order of stops
        t0 = time.perf_counter()
        table = CostTable(env)
        order = plan_tour(env, self.method, table).order
        plan_time = time.perf_counter() - t0

        self.res = MissionResult(self.method, order)
        self.res.deliveries_total = len(env.pickups)
        self._log("mission start at depot, order: " + " ".join(s.label for s in order))
        delivery_times = []

        for stop in order:
            # decide: is there enough battery for this leg plus the way home from the stop?
            leg = self._search(drone.position, stop.cell)
            back = self._search(stop.cell, env.depot)
            need = leg.cost + back.cost
            if drone.battery < need:
                self._log(f"battery {drone.battery} < {need} needed for {stop.label}, going to recharge")
                if drone.position != env.depot:
                    self._fly(env.depot, "heading to depot")
                if drone.battery < drone.capacity:
                    self._recharge()
                leg = self._search(drone.position, stop.cell)
                back = self._search(stop.cell, env.depot)
                if drone.battery < leg.cost + back.cost:
                    self._log(f"{stop.label} needs {leg.cost + back.cost} even on a full battery, stopping mission")
                    break

            # act: fly there, then pick up or drop off
            self._fly(stop.cell, "heading to " + stop.label, leg)
            if stop.kind == "pickup":
                drone.pick_up(stop.delivery)
                self._log(f"picked up package {stop.delivery}")
            else:
                drone.drop_off(stop.delivery)
                delivery_times.append(self.t)
                self._log(f"delivered package {stop.delivery}")

        if drone.position != env.depot:
            self._fly(env.depot, "returning to depot")
        self._log("mission finished")

        r = self.res
        r.total_cost = self.total_cost
        r.deliveries_completed = len(delivery_times)
        r.avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else None
        r.battery_violations = drone.battery_violations
        r.computation_time_s = plan_time + self.search_time
        r.path_gap_pct = sum(self.gaps) / len(self.gaps) if self.gaps else 0.0
        return r


def run_mission(env, battery_capacity, **kwargs):
    return MissionRunner(env, battery_capacity, **kwargs).run()
