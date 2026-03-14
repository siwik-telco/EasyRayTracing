import math

class Building:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def intersects(self, rx, ry):
        return self.x <= rx <= self.x + self.width and self.y <= ry <= self.y + self.height

    def get_reflection_multipliers(self, px, py, nx, ny):
        if px < self.x <= nx:
            return -1, 1
        if px > self.x + self.width >= nx:
            return -1, 1
        if py < self.y <= ny:
            return 1, -1
        if py > self.y + self.height >= ny:
            return 1, -1
        return -1, -1

class Antenna:
    def __init__(self, x, y, tx_power, frequency, is_directional):
        self.x = x
        self.y = y
        self.tx_power = tx_power
        self.frequency = frequency
        self.is_directional = is_directional

    def get_angles(self):
        if self.is_directional:
            return range(-30, 31, 5)
        return range(0, 360, 5)

class Ray:
    def __init__(self, start_x, start_y, angle):
        self.start_x = start_x
        self.start_y = start_y
        self.angle = angle
        self.rad_angle = math.radians(angle)
        self.dx = math.cos(self.rad_angle)
        self.dy = math.sin(self.rad_angle)
