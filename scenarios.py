from models import Building

class ScenarioBuilder:
    def get_single_building(self):
        return [Building(350, 250, 100, 100)]

    def get_two_buildings(self):
        return [Building(300, 250, 80, 100), Building(450, 250, 80, 100)]

    def get_block(self):
        buildings = []
        for row in range(3):
            for col in range(3):
                buildings.append(Building(250 + col * 120, 100 + row * 120, 80, 80))
        return buildings

    def get_corridor(self):
        return [Building(200, 100, 400, 80), Building(200, 400, 400, 80)]
