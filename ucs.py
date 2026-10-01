# ucs.py
# Uniform-Cost Search. Always expands the cheapest node so far.
# We use it as the reference to check that A* really gives the optimal cost.
import heapq
import time

from cost_model import move_cost, PathResult


def ucs(env, start, goal):
    t0 = time.perf_counter()
    tie = 0                                   # keeps the heap from ever comparing two cells
    frontier = [(0, tie, start)]
    best_g = {start: 0}
    parent = {start: None}
    done = set()

    while frontier:
        g, _, cell = heapq.heappop(frontier)
        if cell in done:
            continue                          # old entry, a cheaper one was already used
        done.add(cell)
        if cell == goal:
            path = []
            while cell is not None:
                path.append(cell)
                cell = parent[cell]
            path.reverse()
            return PathResult(path, g, time.perf_counter() - t0, len(done))
        for direction, nxt in env.neighbors(cell):
            new_g = g + move_cost(env, direction, nxt)
            if new_g < best_g.get(nxt, float("inf")):
                best_g[nxt] = new_g
                parent[nxt] = cell
                tie += 1
                heapq.heappush(frontier, (new_g, tie, nxt))

    return PathResult(None, None, time.perf_counter() - t0, len(done))
