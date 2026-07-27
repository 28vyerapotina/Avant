import pygame as pg
import spritesheet
class Sprite(pg.sprite.Sprite):
    def __init__(self, character, x_pos, y_pos):
        pg.sprite.Sprite.__init__(self)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.char = character
        if x_pos < 1000:
            self.rect = pg.Rect((x_pos, y_pos, 64, 64))
            self.image = pg.image.load('' + self.char + '/' + self.char + '_R.png').convert_alpha()
        else:
            self.rect = pg.Rect((x_pos, y_pos, 64, 64))
            self.image = pg.image.load('' + self.char + '/' + self.char + '_L.png').convert_alpha()
        self.image = pg.transform.scale_by(self.image, 10)
    def jump(self):
        self.ss = spritesheet.spritesheet('' + self.char + '/' + self.char + '_jump.png')
        self.imgs = self.ss.load_strip((0, 0, 64, 100), 9, None)
        self.imgs = [pg.transform.scale_by(img, 10).convert_alpha() for img in self.imgs]
        return self.imgs       
    def move_dir(self, dir, move, size):
        if dir == 'right':
            self.ss = spritesheet.spritesheet('' + self.char + '/' + self.char + '_' + move + '_R.png')
            self.imgs = self.ss.load_strip((0, 0, 64, 100), size, None)
        else:
            self.ss = spritesheet.spritesheet('' + self.char + '/' + self.char + '_' + move + '_L.png')
            self.imgs = self.ss.load_strip((0, 0, 64, 100), size, None)
        self.imgs = [pg.transform.scale_by(img, 10).convert_alpha() for img in self.imgs]
        return self.imgs
    def update_pos(self, x_pos, y_pos):
        self.x_pos += x_pos
        self.y_pos += y_pos