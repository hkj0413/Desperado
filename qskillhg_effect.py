import server
import game_framework
import game_world

from pico2d import load_image, load_wav

class QskillHGEffect:
    image = None
    Q_HG_sound = None

    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y
        self.sx = 0
        self.frame = 0
        if QskillHGEffect.image == None:
            QskillHGEffect.image = [load_image("./Effect/HG/" + 'Q_HG_effect' + " (%d)" % i + ".png") for i in range(1, 6 + 1)]
        if QskillHGEffect.Q_HG_sound == None:
            QskillHGEffect.Q_HG_sound = load_wav("./Sound/Q_HG.mp3")
            QskillHGEffect.Q_HG_sound.set_volume(104)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.frame == 0:
            QskillHGEffect.Q_HG_sound.play()

        self.frame = self.frame + 6.0 * 2.5 * game_framework.frame_time
        if self.frame > 6.0:
            game_world.remove_object(self)

    def draw(self):
        if self.frame < 6.0:
            if server.character.upgrade >= 4:
                self.image[int(self.frame)].draw(self.sx, self.y, 384, 255)
            else:
                self.image[int(self.frame)].draw(self.sx, self.y, 256, 170)