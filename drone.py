# drone.py
# Keeps track of the drone's own state: where it is, how much battery is left,
# and which packages it is carrying.


class Drone:
    def __init__(self, start, battery_capacity):
        self.position = start
        self.capacity = battery_capacity
        self.battery = battery_capacity
        self.carrying = []              # names of deliveries currently on board
        self.battery_violations = 0     # times the battery ran out mid-flight (should stay 0)

    def move_to(self, cell, cost):
        # every move uses up battery equal to its movement cost
        if cost > self.battery:
            self.battery_violations += 1
        self.battery -= cost
        self.position = cell

    def pick_up(self, name):
        self.carrying.append(name)

    def drop_off(self, name):
        self.carrying.remove(name)

    def recharge(self):
        self.battery = self.capacity
