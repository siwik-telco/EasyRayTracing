import math

class PhysicsEngine:
    def __init__(self):
        self.c = 299792458
        self.penetration_losses = {
            800: 10,
            900: 10,
            2100: 15,
            2600: 15,
            3600: 20,
            7000: 25,
            15000: 30,
            24000: 40
        }
        self.reflection_losses = {
            800: 4,
            900: 4,
            2100: 6,
            2600: 6,
            3600: 8,
            7000: 10,
            15000: 12,
            24000: 15
        }

    def calculate_fspl(self, distance, frequency_mhz):
        if distance <= 0:
            return 0
        return 20 * math.log10(distance) + 20 * math.log10(frequency_mhz) - 27.55

    def get_reflection_loss(self, frequency_mhz):
        return self.reflection_losses.get(frequency_mhz, 10)

    def calculate_rsrp(self, tx_power, distance, frequency_mhz, walls_penetrated, extra_loss=0):
        fspl = self.calculate_fspl(distance, frequency_mhz)
        wall_loss = self.penetration_losses.get(frequency_mhz, 20) * walls_penetrated
        return tx_power - fspl - wall_loss - extra_loss
