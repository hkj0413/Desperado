import server
import game_framework

from pico2d import load_image, load_wav

class RcskillHGEffect:
    image = None
    Rc_HG_sound = None

    def __init__(self, d):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.frame = 0
        self.face = d
        if RcskillHGEffect.image == None:
            RcskillHGEffect.image = [load_image("./Effect/HG/" + 'Rc_HG' + " (%d)" % i + ".png") for i in range(1, 8 + 1)]
        if RcskillHGEffect.Rc_HG_sound == None:
            RcskillHGEffect.Rc_HG_sound = load_wav("./Sound/Rc_HG.mp3")
            RcskillHGEffect.Rc_HG_sound.set_volume(64)

    def update(self):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = self.x - server.background.window_left

        if self.frame == 0:
            RcskillHGEffect.Rc_HG_sound.play()

        self.frame = self.frame + 8.0 * 2.5 * game_framework.frame_time

    def draw(self):
        if self.frame < 8.0:
            if self.face == 1:
                if int(self.frame) == 0:
                    self.image[0].composite_draw(0, 'h', self.sx + 77,
                                                           self.y - 10, 105, 108)
                elif int(self.frame) == 1:
                    self.image[1].composite_draw(-1 * 3.141592 / 8, 'h', self.sx + 67,
                                                           self.y - 59, 105, 108)
                elif int(self.frame) == 2:
                    self.image[2].composite_draw(-4 * 3.141592 / 8, 'h', self.sx + 10,
                                                           self.y - 89, 105, 108)
                elif int(self.frame) == 3:
                    self.image[3].composite_draw(-6 * 3.141592 / 8, 'h', self.sx - 17,
                                                           self.y - 59, 105, 108)
                elif int(self.frame) == 4:
                    self.image[4].composite_draw(-10 * 3.141592 / 8, 'h', self.sx - 50,
                                                 self.y - 19, 105, 108)
                elif int(self.frame) == 5:
                    self.image[5].composite_draw(-12 * 3.141592 / 8, 'h', self.sx - 37,
                                                 self.y + 29, 105, 108)
                elif int(self.frame) == 6:
                    self.image[6].composite_draw(-14 * 3.141592 / 8, 'h', self.sx - 7,
                                                 self.y + 39, 105, 108)
                elif int(self.frame) == 7:
                    self.image[7].composite_draw(-16 * 3.141592 / 8, 'h', self.sx + 17,
                                                 self.y + 49, 105, 108)
            elif self.face == -1:
                if int(self.frame) == 0:
                    self.image[0].composite_draw(0, '', self.sx - 77,
                                                 self.y - 10, 105, 108)
                elif int(self.frame) == 1:
                    self.image[1].composite_draw(1 * 3.141592 / 8, '', self.sx - 67,
                                                 self.y - 59, 105, 108)
                elif int(self.frame) == 2:
                    self.image[2].composite_draw(4 * 3.141592 / 8, '', self.sx - 10,
                                                 self.y - 89, 105, 108)
                elif int(self.frame) == 3:
                    self.image[3].composite_draw(6 * 3.141592 / 8, '', self.sx + 17,
                                                 self.y - 59, 105, 108)
                elif int(self.frame) == 4:
                    self.image[4].composite_draw(10 * 3.141592 / 8, '', self.sx + 50,
                                                 self.y - 19, 105, 108)
                elif int(self.frame) == 5:
                    self.image[5].composite_draw(12 * 3.141592 / 8, '', self.sx + 37,
                                                 self.y + 29, 105, 108)
                elif int(self.frame) == 6:
                    self.image[6].composite_draw(14 * 3.141592 / 8, '', self.sx + 7,
                                                 self.y + 39, 105, 108)
                elif int(self.frame) == 7:
                    self.image[7].composite_draw(16 * 3.141592 / 8, '', self.sx - 17,
                                                 self.y + 49, 105, 108)