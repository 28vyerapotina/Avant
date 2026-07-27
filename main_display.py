import pygame as pg
import sys
import sprite


pg.init()
screen = pg.display.set_mode((1920, 1080), pg.FULLSCREEN)
clock = pg.time.Clock()

bg = pg.image.load('backgrounds/background2.png').convert_alpha()
bg = pg.transform.scale(bg, (screen.get_width(), screen.get_height()))
bg_pos = (screen.get_width() / 2 - bg.get_width() / 2,
          screen.get_height() / 2 - bg.get_height() / 2)

FRAME_DURATION = 100
blue = sprite.Sprite('blue', 100, 250)
opp = sprite.Sprite('purple', 1700, 250)
# initialize directions
jump = blue.jump()
left = blue.move_dir('left', 'move', 3)
right = blue.move_dir('right', 'move', 3)

jump1 = opp.jump()
left1 = opp.move_dir('left', 'move', 3)
right1 = opp.move_dir('right', 'move', 3)

group = pg.sprite.Group()
group.add(blue)
group.add(opp)
      
anim_timer = pg.time.get_ticks()
anim_index = 0
current_action = None

anim_2timer = pg.time.get_ticks()
anim_2index = 0
current_2action = None


while True:
    blue.rect.topleft = (blue.x_pos, blue.y_pos)
    opp.rect.topleft = (opp.x_pos, opp.y_pos)
    keys = pg.key.get_pressed()
    if pg.sprite.collide_mask(blue, opp) is not None:
        sys.exit()
    if keys[pg.K_UP]:
        active_anim = jump
    elif keys[pg.K_RIGHT]:
        blue.update_pos(5, 0)
        active_anim = right
    elif keys[pg.K_LEFT]:
        blue.update_pos(-5, 0)
        active_anim = left
    else:
        active_anim = None
    if keys[pg.K_w]:
        active_2anim = jump1
    elif keys[pg.K_d]:
        opp.update_pos(5, 0)
        active_2anim = right1
    elif keys[pg.K_a]:
        opp.update_pos(-5, 0)
        active_2anim = left1
    else:
        active_2anim = None
    if active_anim is not None:
        if active_anim is not current_action:
            current_action = active_anim
            anim_index = 0
            anim_timer = pg.time.get_ticks()
        if pg.time.get_ticks() - anim_timer >= FRAME_DURATION:
            anim_timer = pg.time.get_ticks()
            anim_index = (anim_index + 1) % len(active_anim)
        blue.image = active_anim[anim_index]
    else:
        current_action = None
    if active_2anim is not None:
        if active_2anim is not current_2action:
            current_2action = active_2anim
            anim_2index = 0
            anim_2timer = pg.time.get_ticks()
        if pg.time.get_ticks() - anim_2timer >= FRAME_DURATION:
            anim_2timer = pg.time.get_ticks()
            anim_2index = (anim_2index + 1) % len(active_2anim)
        opp.image = active_2anim[anim_2index]
    else:
        current_2action = None

    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            sys.exit()
    
    screen.blit(bg, bg_pos)
    screen.blit(opp.image, (opp.x_pos, opp.y_pos))
    screen.blit(blue.image, (blue.x_pos, blue.y_pos))
    pg.display.flip()
    clock.tick(100)