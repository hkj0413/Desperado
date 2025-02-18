import server
import game_framework
import game_world

from pico2d import load_image, load_wav

class NormalRFEffect:
    image = None
    Lc_RF_sound = None

    def __init__(self, d):
        self.x = server.character.x + 78 * d
        self.y = server.character.y
        self.sx = 0
        self.timer = 0
        self.temp = 0
        self.one = 0
        self.face = d
        if NormalRFEffect.image == None:
            NormalRFEffect.image = load_image("./Effect/RF/" + 'Lc_RF' + " (1)" + ".png")
        if NormalRFEffect.Lc_RF_sound == None:
            NormalRFEffect.Lc_RF_sound = load_wav("./Sound/Lc_RF.mp3")
            NormalRFEffect.Lc_RF_sound.set_volume(112)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.one == 0:
            NormalRFEffect.Lc_RF_sound.play()
            self.one += 1

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.x += 20 * self.face
            if self.temp == 24:
                game_world.remove_object(self)

    def draw(self):
        if self.temp < 24:
            if self.face == 1:
                self.image.composite_draw(0, '', self.sx + 70, self.y - 20, 170, 70)
            elif self.face == -1:
                self.image.composite_draw(0, 'h', self.sx - 70, self.y - 20, 170, 70)