import server
import game_framework

from pico2d import load_image

class RcskillSGEffect:
    image = None

    def __init__(self):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.frame = 0
        if RcskillSGEffect.image == None:
            RcskillSGEffect.image = [load_image("./Effect/SG/" + 'Rc_SG' + " (%d)" % i + ".png") for i in range(1, 8 + 1)]

    def update(self):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = self.x - server.background.window_left

        self.frame = self.frame + 8.0 * 2.5 * game_framework.frame_time

    def draw(self):
        if self.frame < 8.0:
            self.image[int(self.frame)].draw(self.sx, self.y - 19.0, 96, 96)