# Intelligent Delivery Drone Agent

Grid-based path planning with wind and no-fly zones. Team 2_brain_cells.

This is a classical AI project. There is no machine learning, deep learning or
reinforcement learning in it. The drone follows a simple loop:
**perceive -> reason -> decide -> act**.

## What the agent does

- **Perceive:** its position, battery, packages on board, the full map (no-fly zones and wind) and the list of delivery requests.
- **Reason:** works out the order of stops (nearest neighbour, then 2-opt) and plans each path with A*.
- **Decide:** which stop to serve next, which route to take, and whether it has enough battery or must recharge first.
- **Act:** moves one cell at a time, picks up and drops off packages, recharges at the depot.

## How to run

You need Python 3.11 or newer. The core project uses only the standard library.
Drawing the figures needs matplotlib:

```
py -3.11 -m pip install matplotlib
```

Run one scenario and see the map, the mission log and the final results:

```
py -3.11 main.py                          (default: recharge_demo)
py -3.11 main.py medium_windy nn2opt
```

Scenarios: `small_calm`, `medium_windy`, `multi_delivery`, `wind_detour`, `recharge_demo`.
Planning methods: `nn`, `nn2opt`, `optimal` (brute force, small missions only).

Run all scenarios, save the results table and draw every figure:

```
py -3.11 experiments.py
```

This writes `results/experiment_results.csv` and the pictures in `results/figures/`.
Computation time is the median of 15 runs, so it changes a little from machine to
machine. Every other number is the same on every run.

## Files

| File | What it does |
|---|---|
| `main.py` | Runs one scenario and prints the map, mission log and results |
| `environment.py` | The grid: free cells, no-fly zones, wind, depot, pickups, drop-offs |
| `cost_model.py` | The movement-cost function and the Manhattan distance |
| `astar.py` | A* search with the Manhattan heuristic |
| `ucs.py` | Uniform-cost search, the baseline for checking A* |
| `drone.py` | Drone state: position, battery, packages on board |
| `delivery_planner.py` | Nearest neighbour, 2-opt and the brute-force best order |
| `simulation.py` | Runs a full mission: plan, fly, pick up, drop off, recharge |
| `scenarios.py` | The five maps the project is run on |
| `experiments.py` | Runs every scenario and saves the results table |
| `visualization.py` | Draws the figures |
| `results/` | `experiment_results.csv` and `figures/` (images used in the presentation) |
| `presentation/` | The 10-slide PPT, built from the numbers in `results/experiment_results.csv` |

## Movement cost

The cost of stepping into a cell:

| Situation | Cost |
|---|---|
| Normal cell | 1 |
| Wind cell, flying with the wind | 1 |
| Wind cell, flying across the wind | 1 + strength // 2 |
| Wind cell, flying against the wind | 1 + strength |
| No-fly cell | not allowed |

A step never costs less than 1, so the Manhattan distance never overestimates the
remaining cost. That makes it an admissible heuristic, so A* finds the optimal
cost. UCS uses the same cost function and is run on every leg as a check.

## Delivery order

- **Nearest neighbour:** from where the drone is, go to the closest stop that is allowed. A drop-off is only allowed once its package has been picked up.
- **2-opt:** tries reversing a section of the route. A change is kept only if every pickup still comes before its drop-off and the route gets strictly cheaper.
- **Brute force:** tries every valid order and keeps the cheapest. Only used for small missions (up to 5 deliveries) to measure how far the heuristics are from the best order.

## Battery rule

Before every leg the drone checks that its battery covers that leg **plus** the
flight from the stop back to the depot. If not, it flies to the depot, recharges
to full and carries on. If a stop cannot be served even on a full battery, the
mission stops and the drone returns to the depot.

Every move takes 1 time step and a recharge takes 5. All orders arrive at time 0,
so a delivery's time is the step count when its package is dropped off.

## Metrics

The six metrics from the abstract:

1. Total mission cost: all movement costs including wind penalties and the final return to the depot
2. Deliveries completed
3. Average delivery time, in steps
4. Path optimality gap: A* cost compared with UCS cost, averaged over every leg flown
5. Computation time: tour planning plus path searches
6. Battery violations: moves that needed more battery than was left

Extra numbers saved in the CSV: nodes expanded by A* and UCS, the tour cost of
nearest neighbour, nearest neighbour + 2-opt and the brute-force optimum, and the
number of recharges. Tour costs are the planned route cost, so they do not include
the extra trip home for a recharge, which is why `recharge_demo` has a total mission
cost of 62 against a tour cost of 56.
