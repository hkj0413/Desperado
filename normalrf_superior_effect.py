import server
import game_framework
import game_world

from pico2d import load_image, load_wav

class NormalRFSPEffect:
    image = None
    Lc_RF_superior_sound = None

    def __init__(self, d):
        self.x = server.character.x + 78 * d
        self.y = server.character.y
        self.sx = 0
        self.timer = 0
        self.temp = 0
        self.one = 0
        self.face = d
        if NormalRFSPEffect.image == None:
            NormalRFSPEffect.image = load_image("./Effect/RF/" + 'Lc_RF_superior' + " (1)" + ".png")
        if NormalRFSPEffect.Lc_RF_superior_sound == None:
            NormalRFSPEffect.Lc_RF_superior_sound = load_wav("./Sound/Lc_RF_superior.mp3")
            NormalRFSPEffect.Lc_RF_superior_sound.set_volume(96)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.one == 0:
            NormalRFSPEffect.Lc_RF_superior_sound.play()
            self.one += 1

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.x += 30 * self.face
            if self.temp == 16:
                game_world.remove_object(self)

    def draw(self):
        if self.temp < 16:
            if self.face == 1:
                self.image.composite_draw(0, '', self.sx + 70, self.y - 10, 510, 90)
            elif self.face == -1:
                self.image.composite_draw(0, 'h', self.sx - 70, self.y - 10, 510, 90)