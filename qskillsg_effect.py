import server
import game_framework
import game_world

from pico2d import load_image, load_wav

class QskillSGEffect:
    image = None
    Q_SG_sound = None

    def __init__(self, d):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.frame = 0
        self.face = d
        if QskillSGEffect.image == None:
            QskillSGEffect.image = [load_image("./Effect/SG/" + 'Q_SG' + " (%d)" % i + ".png") for i in range(1, 9 + 1)]
        if QskillSGEffect.Q_SG_sound == None:
            QskillSGEffect.Q_SG_sound = load_wav("./Sound/Q_SG.mp3")
            QskillSGEffect.Q_SG_sound.set_volume(96)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.frame == 0:
            QskillSGEffect.Q_SG_sound.play()

        self.frame = self.frame + 13.0 * 1.5 * game_framework.frame_time
        if self.frame > 13.0:
            game_world.remove_object(self)

    def draw(self):
        if 4.0 < self.frame < 13.0:
            if self.face == 1:
                self.image[int(self.frame) - 4].composite_draw(0, '', self.sx + 75, self.y, 201, 200)
            elif self.face == -1:
                self.image[int(self.frame) - 4].composite_draw(0, 'h', self.sx - 75, self.y, 201, 200)