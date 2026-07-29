import pygame as pg
import spritesheet

pg.init()  # ensures video subsystem is ready before Info() is called
display_info = pg.display.Info()
SCREEN_W = display_info.current_w
SCREEN_H = display_info.current_h
BASE_W, BASE_H = 1920, 1080
SPRITE_SCALE = 8


class Sprite(pg.sprite.Sprite):
    def __init__(self, character, x_pos, y_pos):
        pg.sprite.Sprite.__init__(self)
        self.scale_x = SCREEN_W / BASE_W
        self.scale_y = SCREEN_H / BASE_H

        # scale the incoming base-resolution position to the actual screen
        self.x_pos = x_pos * self.scale_x
        self.y_pos = y_pos * self.scale_y
        self.char = character
        self.init_x_pos = self.x_pos
        self.init_y_pos = self.y_pos

        base_size = 64
        scaled_w = int(base_size * self.scale_x)
        scaled_h = int(base_size * self.scale_y)

        if x_pos < 1000:
            self.rect = pg.Rect((self.x_pos, self.y_pos, scaled_w, scaled_h))
            self.image = pg.image.load(f'{self.char}/{self.char}_R.png')
        else:
            self.rect = pg.Rect((self.x_pos, self.y_pos, scaled_w, scaled_h))
            self.image = pg.image.load(f'{self.char}/{self.char}_L.png')

        self.image = pg.transform.scale_by(self.image, (SPRITE_SCALE * self.scale_x, SPRITE_SCALE * self.scale_y)).convert_alpha()

    def jump(self):
        self.ss = spritesheet.spritesheet(f'{self.char}/{self.char}_jump.png')
        self.imgs = self.ss.load_strip((0, 0, 64, 100), 9, None)
        self.imgs = [
            pg.transform.scale_by(img, (SPRITE_SCALE * self.scale_x, SPRITE_SCALE * self.scale_y)).convert_alpha()
            for img in self.imgs
        ]
        return self.imgs

    def move_dir(self, dir, move, size):
        if dir == 'right':
            self.ss = spritesheet.spritesheet(f'{self.char}/{self.char}_{move}_R.png')
        else:
            self.ss = spritesheet.spritesheet(f'{self.char}/{self.char}_{move}_L.png')

        self.imgs = self.ss.load_strip((0, 0, 64, 100), size, None)
        self.imgs = [
            pg.transform.scale_by(img, (SPRITE_SCALE * self.scale_x, SPRITE_SCALE * self.scale_y)).convert_alpha()
            for img in self.imgs
        ]
        return self.imgs

    def update_pos(self, x_pos, y_pos):
        self.x_pos = max(0, min(self.x_pos + x_pos * self.scale_x, SCREEN_W))
        self.y_pos = max(0, min(self.y_pos + y_pos * self.scale_y, SCREEN_H))

    def reset_height(self):
        self.y_pos = self.init_y_pos