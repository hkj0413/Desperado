import server
import game_framework
import game_world

from pico2d import load_image, load_wav

class NormalHGEffect:
    image = None
    Lc_HG_sound = None

    def __init__(self, d):
        self.x = server.character.x + 18 * d
        self.y = server.character.y
        self.sx = 0
        self.timer = 0
        self.temp = 0
        self.one = 0
        self.face = d
        if NormalHGEffect.image == None:
            NormalHGEffect.image = load_image("./Effect/HG/" + 'Lc_HG' + " (1)" + ".png")
        if NormalHGEffect.Lc_HG_sound == None:
            NormalHGEffect.Lc_HG_sound = load_wav("./Sound/Lc_HG.mp3")
            NormalHGEffect.Lc_HG_sound.set_volume(64)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.one == 0:
            NormalHGEffect.Lc_HG_sound.play()
            self.one += 1

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.x += 10 * self.face
            if self.temp == 36:
                game_world.remove_object(self)

    def draw(self):
        if self.temp < 36:
            if self.face == 1:
                self.image.composite_draw(0, '', self.sx + 15, self.y - 10, 30, 27)
            elif self.face == -1:
                self.image.composite_draw(0, 'h', self.sx - 15, self.y - 10, 30, 27)