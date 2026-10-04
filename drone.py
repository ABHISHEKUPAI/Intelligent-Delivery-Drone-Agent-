class Drone:
    def __init__(self, start, battery_capacity):
        self.position = start
        self.capacity = battery_capacity
        self.battery = battery_capacity
        self.carrying = []              
        self.battery_violations = 0   
          
    def move_to(self, cell, cost):
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
