import heapq
import time

from cost_model import move_cost, manhattan, PathResult


def astar(env, start, goal):
    t0 = time.perf_counter()
    tie = 0
    frontier = [(manhattan(start, goal), tie, 0, start)]    
    best_g = {start: 0}
    parent = {start: None}
    done = set()

    while frontier:
        _, _, g, cell = heapq.heappop(frontier)
        if cell in done:
            continue
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
                heapq.heappush(frontier, (new_g + manhattan(nxt, goal), tie, new_g, nxt))

    return PathResult(None, None, time.perf_counter() - t0, len(done))
