# scenarios.py
# The maps the project is run on. Used by main.py and experiments.py.
from dataclasses import dataclass

from environment import GridEnvironment


@dataclass
class Scenario:
    name: str
    title: str
    env: GridEnvironment
    battery: int
    note: str = ""


def small_calm():
    # 1. small grid, hardly any wind
    env = GridEnvironment(
        rows=8, cols=8, depot=(0, 0),
        no_fly={(2, 2), (2, 3), (3, 2), (5, 5), (5, 6)},
        wind={(4, 1): ("E", 2), (4, 2): ("E", 2)},
        pickups={"A": (1, 6), "B": (6, 6)},
        dropoffs={"A": (6, 1), "B": (3, 6)},
    )
    return Scenario("small_calm", "Small grid, little wind", env, battery=80)


def medium_windy():
    # 2. medium grid, a wall, a strong crosswind band and a northward wind patch
    no_fly = {(r, 6) for r in range(2, 10)} | {(10, 10), (10, 11), (11, 10), (11, 11)}
    wind = {(5, c): ("W", 3) for c in range(0, 14) if (5, c) not in no_fly}
    wind.update({(r, c): ("N", 4) for r in (8, 9) for c in range(8, 12)})
    env = GridEnvironment(
        rows=14, cols=14, depot=(0, 0), no_fly=no_fly, wind=wind,
        pickups={"A": (1, 11), "B": (12, 12), "C": (7, 2)},
        dropoffs={"A": (12, 2), "B": (3, 9), "C": (11, 8)},
    )
    return Scenario("medium_windy", "Medium grid, moderate wind", env, battery=200)


def multi_delivery():
    # 3. four deliveries on a bigger map (still small enough to brute force)
    no_fly = ({(r, 5) for r in range(0, 7)} | {(r, 10) for r in range(8, 16)}
              | {(8, 2), (8, 3), (8, 4), (12, 7), (12, 8)})
    wind = {(r, c): ("E", 2) for r in (3, 4) for c in range(6, 14)}
    wind.update({(r, 7): ("S", 3) for r in range(9, 14) if (r, 7) not in no_fly})
    env = GridEnvironment(
        rows=16, cols=16, depot=(0, 0), no_fly=no_fly, wind=wind,
        pickups={"A": (2, 8), "B": (14, 3), "C": (9, 13), "D": (5, 1)},
        dropoffs={"A": (13, 14), "B": (6, 12), "C": (1, 3), "D": (15, 8)},
    )
    return Scenario("multi_delivery", "Multiple deliveries (4)", env, battery=300)


def wind_detour(wind_on=True):
    # 4. a headwind band across the middle. Flying east the drone goes around it,
    #    flying west the same wind is a tailwind so the drone rides through it.
    wind = {}
    if wind_on:
        wind = {(r, c): ("W", 5) for r in (3, 4, 5) for c in range(2, 7)}
    env = GridEnvironment(
        rows=9, cols=9, depot=(4, 0), wind=wind,
        pickups={"A": (4, 8)}, dropoffs={"A": (4, 1)},
    )
    label = "Wind changes the route" if wind_on else "Same map, no wind"
    return Scenario("wind_detour" if wind_on else "wind_detour_calm", label, env, battery=100)


def recharge_demo():
    # 5. three far-apart deliveries and a small battery, so the drone has to recharge
    no_fly = {(r, 6) for r in range(3, 11)} | {(3, 7), (3, 8)}
    wind = {(r, c): ("N", 3) for r in range(6, 9) for c in range(0, 5)}
    env = GridEnvironment(
        rows=12, cols=12, depot=(0, 0), no_fly=no_fly, wind=wind,
        pickups={"A": (10, 1), "B": (2, 10), "C": (10, 10)},
        dropoffs={"A": (1, 8), "B": (11, 3), "C": (5, 2)},
    )
    return Scenario("recharge_demo", "Small battery, recharge needed", env, battery=44)


ALL_SCENARIOS = [small_calm, medium_windy, multi_delivery, wind_detour, recharge_demo]
