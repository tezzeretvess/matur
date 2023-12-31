import pygame as pg

class Lumbermill:

    def __init__(self, pos, game):
        image = pg.image.load("assets/graphics/building01.png")
        self.image = image
        self.name = "building"
        self.rect = self.image.get_rect(topleft=pos)
        self.resource_cooldown = pg.time.get_ticks()
        self.inventory = 0
        self.game = game

    def update(self):
        now = pg.time.get_ticks()
        # production of resources
        if now - self.resource_cooldown > 200:
            self.inventory += 1
            self.game.total_resources += 1
            self.resource_cooldown = now


