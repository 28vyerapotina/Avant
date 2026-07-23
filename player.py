import pygame as pg
class Player(pg.sprite.Sprite):
    def __init__(self, img, pos, character):
        super().__init__()
        self.image = pg.image.load('' + character + '.png').convert_alpha()
        self.pos = pg.Rect(pos)
    def up(self,charcter)