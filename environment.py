# environment.py
# The grid world the drone flies in. Cells are (row, col), row 0 is the top.

# direction letter -> (change in row, change in col)
DIRECTIONS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}


class GridEnvironment:
    def __init__(self, rows, cols, depot, no_fly=None, wind=None,
                 pickups=None, dropoffs=None):
        # depot    : (row, col) where the drone starts and recharges
        # no_fly   : set of cells the drone can never enter
        # wind     : {(row, col): (direction, strength)}  e.g. {(2, 3): ("W", 4)}
        # pickups  : {"A": (row, col), ...}
        # dropoffs : {"A": (row, col), ...}  same names as pickups
        self.rows = rows
        self.cols = cols
        self.depot = depot
        self.no_fly = set(no_fly or [])
        self.wind = dict(wind or {})
        self.pickups = dict(pickups or {})
        self.dropoffs = dict(dropoffs or {})
        self._check_setup()

    def in_bounds(self, cell):
        r, c = cell
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_blocked(self, cell):
        return cell in self.no_fly

    def can_enter(self, cell):
        return self.in_bounds(cell) and not self.is_blocked(cell)

    def neighbors(self, cell):
        # the four moves (up/down/left/right) that stay on the map and avoid no-fly cells
        r, c = cell
        for name, (dr, dc) in DIRECTIONS.items():
            nxt = (r + dr, c + dc)
            if self.can_enter(nxt):
                yield name, nxt

    def _check_setup(self):
        # catch silly mistakes early (like a pickup placed inside a no-fly zone)
        places = [("depot", self.depot)]
        places += [("pickup " + k, v) for k, v in self.pickups.items()]
        places += [("dropoff " + k, v) for k, v in self.dropoffs.items()]
        for label, cell in places:
            if not self.can_enter(cell):
                raise ValueError(f"{label} at {cell} is off the map or inside a no-fly zone")
        if set(self.pickups) != set(self.dropoffs):
            raise ValueError("every pickup needs a dropoff with the same name")
        for cell, (d, s) in self.wind.items():
            if d not in DIRECTIONS or s < 1:
                raise ValueError(f"bad wind value at {cell}: {(d, s)}")
            if not self.can_enter(cell):
                raise ValueError(f"wind at {cell} is off the map or inside a no-fly zone")

    def render(self, path=None):
        # quick text picture of the map, useful for debugging and the README
        arrows = {"N": "^", "S": "v", "E": ">", "W": "<"}
        on_path = set(path or [])
        pick = {v: k for k, v in self.pickups.items()}
        drop = {v: k for k, v in self.dropoffs.items()}
        lines = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                cell = (r, c)
                if cell == self.depot:
                    ch = "D"
                elif cell in pick:
                    ch = "p" + pick[cell]
                elif cell in drop:
                    ch = "d" + drop[cell]
                elif cell in self.no_fly:
                    ch = "#"
                elif cell in on_path:
                    ch = "*"
                elif cell in self.wind:
                    ch = arrows[self.wind[cell][0]]
                else:
                    ch = "."
                row.append(ch.ljust(2))
            lines.append(" ".join(row))
        return "\n".join(lines)
