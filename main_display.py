import pygame as pg
import sys
import spritesheet

pg.init()
screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)
clock = pg.time.Clock()

bg = pg.image.load('/Users/vedayerapotina/Downloads/background.png').convert()
bg = pg.transform.scale(bg, (screen.get_width(), screen.get_height()))
bg_pos = (screen.get_width() / 2 - bg.get_width() / 2,
          screen.get_height() / 2 - bg.get_height() / 2)

ss = spritesheet.spritesheet('Sprite-0004.png')
imgs = ss.load_strip((0, 0, 64, 64), 8, None)
imgs = [pg.transform.scale_by(img, 10).convert_alpha() for img in imgs]

current_frame = 0
FRAME_DURATION = 100  # ms per frame
last_switch = pg.time.get_ticks()
animating = False

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            sys.exit()
        if event.type == pg.KEYDOWN and event.key == pg.K_UP:
            animating = True

    if animating:
        now = pg.time.get_ticks()
        if now - last_switch > FRAME_DURATION:
            current_frame = (current_frame + 1) % len(imgs)
            last_switch = now

    screen.blit(bg, bg_pos)
    screen.blit(imgs[current_frame], (100, 500))
    pg.display.flip()
    clock.tick(60)