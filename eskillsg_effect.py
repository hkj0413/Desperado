import server
import game_framework
import game_world

from pico2d import load_image, load_wav

class EskillSGEffect:
    image = None
    E_SG_sound = None

    def __init__(self, d):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.frame = 0
        self.face = d
        if EskillSGEffect.image == None:
            EskillSGEffect.image = [load_image("./Effect/SG/" + 'E_SG' + " (%d)" % i + ".png") for i in range(1, 9 + 1)]
        if EskillSGEffect.E_SG_sound == None:
            EskillSGEffect.E_SG_sound = load_wav("./Sound/E_SG.mp3")
            EskillSGEffect.E_SG_sound.set_volume(108)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.frame == 0:
            EskillSGEffect.E_SG_sound.play()

        self.frame = self.frame + 9.0 * 1.5 * game_framework.frame_time
        if self.frame > 9.0:
            game_world.remove_object(self)

    def draw(self):
        if self.frame < 9.0:
            if self.face == 1:
                self.image[int(self.frame)].composite_draw(0, '', self.sx + 75 + int(self.frame) * 10, self.y - 12, 170, 170)
            elif self.face == -1:
                self.image[int(self.frame)].composite_draw(0, 'h', self.sx - 75 - int(self.frame) * 10, self.y - 12, 170, 170)