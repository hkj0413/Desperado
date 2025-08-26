import server
import game_framework
import game_world
import math
import random

from pico2d import load_image

class ULTHGEffect:
    image = None

    def __init__(self):
        self.angle = random.uniform(0, 360)
        self.x = server.character.x + math.sin(math.radians(self.angle)) * 60
        self.y = server.character.y + math.cos(math.radians(self.angle)) * 60
        self.sx = 0
        self.frame = 0
        if ULTHGEffect.image == None:
            ULTHGEffect.image = [load_image("./Effect/HG/" + 'ULT_HG' + " (%d)" % i + ".png") for i in range(1, 3 + 1)]

    def update(self):
        self.x = server.character.x + math.sin(math.radians(self.angle)) * 60
        self.y = server.character.y + math.cos(math.radians(self.angle)) * 60
        self.sx = self.x - server.background.window_left

        self.frame = self.frame + 3.0 * 6.0 * game_framework.frame_time
        if self.frame > 3.0:
            game_world.remove_object(self)

    def draw(self):
        if self.frame < 3:
            self.image[int(self.frame)].composite_draw(math.radians(-self.angle), '', self.sx, self.y, 54, 64)