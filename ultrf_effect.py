import server
import game_framework
import game_world

from pico2d import load_image

class ULTRFEffect:
    image = None

    def __init__(self, d):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.frame = 0
        self.face = d
        if ULTRFEffect.image == None:
            ULTRFEffect.image = [load_image("./Effect/RF/" + 'ULT_RF_effect' + " (%d)" % i + ".png") for i in range(1, 9 + 1)]

    def update(self):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = self.x - server.background.window_left
        self.frame = self.frame + 9.0 * 2.5 * game_framework.frame_time
        if self.frame > 9.0:
            game_world.remove_object(self)

    def draw(self):
        if self.frame < 9.0:
            if self.face == 1:
                self.image[int(self.frame)].composite_draw(0, '', self.sx + 80, self.y - 25, 80, 75)
            elif self.face == -1:
                self.image[int(self.frame)].composite_draw(0, 'h', self.sx - 80, self.y - 25, 80, 75)