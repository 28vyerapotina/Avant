from PIL import Image
import random
import sprite
import pygame as pg
class ComputerAlgorithm:
    def __init__(self, x, y):
        chars = ['purple', 'pink', 'blue', 'green']
        self.x = x
        self.y = y
        self.char = sprite.Sprite(random.choice(chars), self.x, self.y)
        self.transparent_img = pg.image.tobytes(self.char.image, "RGBA")
        self.image = Image.frombytes("RGBA", self.char.image.get_size(), self.transparent_img)
        left, upper, right, lower = self.image.getbbox()
        self.width = right - left
    def return_move(self, player_pos_x, player_violent, K_cooldown):
        if self.x <= player_pos_x:
            if self.x + self.width >= player_pos_x:
                if player_violent:
                    return 'jump'
                else:
                    return 'kick_R' if K_cooldown == True else 'punch_R'
            else:
                return 'move_R'
        else:
            if self.x - self.width <= player_pos_x:
                if player_violent:
                    return 'jump'
                else:
                    return 'kick_L' if K_cooldown == True else 'punch_L'
            else:
                return 'move_L'