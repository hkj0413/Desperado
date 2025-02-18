import server
import game_framework
import game_world

from pico2d import load_image, load_wav

class QskillRFEffect:
    image = None
    q_RF_sound = None

    def __init__(self, d):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.timer = 0
        self.temp = 0
        self.one = 0
        self.face = d
        if QskillRFEffect.image == None:
            QskillRFEffect.image = load_image("./Effect/RF/" + 'Q_RF' + " (1)" + ".png")
        if QskillRFEffect.q_RF_sound == None:
            QskillRFEffect.q_RF_sound = load_wav("./Sound/Q_RF.mp3")
            QskillRFEffect.q_RF_sound.set_volume(64)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.one == 0:
            QskillRFEffect.q_RF_sound.play()
            self.one += 1

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.x += 40 * self.face
            if self.temp == 19:
                game_world.remove_object(self)

    def draw(self):
        if self.temp < 19:
            if self.face == 1:
                self.image.composite_draw(0, '', self.sx + 220, self.y - 10, 362, 82)
            elif self.face == -1:
                self.image.composite_draw(0, 'h', self.sx - 220, self.y - 10, 362, 82)