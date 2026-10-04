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
    if direction == wind_dir:                    
        return MIN_STEP_COST
    if direction == OPPOSITE[wind_dir]:          
        return MIN_STEP_COST + strength
    return MIN_STEP_COST + strength // 2        


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


_STEP_TO_DIRECTION = {(-1, 0): "N", (1, 0): "S", (0, 1): "E", (0, -1): "W"}


def path_cost(env, path):
    total = 0
    for a, b in zip(path, path[1:]):
        step = (b[0] - a[0], b[1] - a[1])
        total += move_cost(env, _STEP_TO_DIRECTION[step], b)
    return total


@dataclass
class PathResult:

    path: Optional[List[Tuple[int, int]]]   
    cost: Optional[int]
    time_s: float                           
    nodes_expanded: int                     

    @property
    def found(self):
        return self.path is not None
