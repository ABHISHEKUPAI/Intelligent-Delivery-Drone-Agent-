# cost_model.py
# One cost function, shared by A* and UCS so the comparison is fair.
#
# Cost of stepping INTO a cell:
#   normal cell                       -> 1
#   wind cell, flying with the wind   -> 1   (no discount, so a step never costs less than 1)
#   wind cell, flying across the wind -> 1 + strength // 2
#   wind cell, flying against it      -> 1 + strength
# No-fly cells can't be entered at all.
#
# Since every step costs at least 1, Manhattan distance can never overestimate
# the real remaining cost. That is what makes it a safe (admissible) heuristic for A*.
from dataclasses import dataclass
from typing import List, Tuple, Optional

from environment import OPPOSITE

MIN_STEP_COST = 1


def move_cost(env, direction, next_cell):
    if not env.can_enter(next_cell):
        raise ValueError(f"cannot enter {next_cell}")
    if next_cell not in env.wind:
        return MIN_STEP_COST
    wind_dir, strength = env.wind[next_cell]
    if direction == wind_dir:                    # tailwind
        return MIN_STEP_COST
    if direction == OPPOSITE[wind_dir]:          # headwind
        return MIN_STEP_COST + strength
    return MIN_STEP_COST + strength // 2         # crosswind


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


_STEP_TO_DIRECTION = {(-1, 0): "N", (1, 0): "S", (0, 1): "E", (0, -1): "W"}


def path_cost(env, path):
    # add up the cost of a path again from scratch, handy for double-checking a search result
    total = 0
    for a, b in zip(path, path[1:]):
        step = (b[0] - a[0], b[1] - a[1])
        total += move_cost(env, _STEP_TO_DIRECTION[step], b)
    return total


@dataclass
class PathResult:
    # what A* and UCS both hand back
    path: Optional[List[Tuple[int, int]]]   # None means no route exists
    cost: Optional[int]
    time_s: float                           # how long the search took
    nodes_expanded: int                     # extra number we use to compare A* and UCS

    @property
    def found(self):
        return self.path is not None
