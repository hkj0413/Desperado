import server
import game_framework
import game_world

from pico2d import load_image, load_wav

from ultsg import ULTSG
from ultsg_stun import ULTStunSG

mob_group = [
    'spore', 'slime', 'pig', 'stonegolem', 'skelldog', 'coldeye', 'wildboar', 'stonestatue',
    'bulldog', 'imp', 'fireboar', 'firemixgolem'
             ]

class ULTSGEffect:
    image = None
    ULT_SG_sound = None
    ULT_SG_stun_sound = None

    def __init__(self, d):
        self.x = server.character.x
        self.y = 140
        self.sx = 0
        self.frame = 0
        self.one = 0
        self.face = d
        if ULTSGEffect.image == None:
            ULTSGEffect.image = [load_image("./Effect/SG/" + 'ULT_SG_crack' + " (%d)" % i + ".png") for i in range(1, 4 + 1)]
        if ULTSGEffect.ULT_SG_sound == None:
            ULTSGEffect.ULT_SG_sound = load_wav("./Sound/ULT_SG.mp3")
            ULTSGEffect.ULT_SG_stun_sound = load_wav("./Sound/ULT_SG_stun.mp3")
            ULTSGEffect.ULT_SG_sound.set_volume(108)
            ULTSGEffect.ULT_SG_stun_sound.set_volume(128)

    def update(self):
        self.sx = self.x - server.background.window_left
        self.frame = self.frame + 19.0 * 0.8 * game_framework.frame_time

        if self.one == 0:
            ULTSGEffect.ULT_SG_stun_sound.play()
            self.one += 1

        if 18.0 > self.frame > 15.0 and self.one == 1:
            ultstunsg = ULTStunSG(self.face)
            game_world.add_object(ultstunsg, 3)
            for mob in mob_group:
                game_world.add_collision_pairs(f'ultstunsg:{mob}', ultstunsg, None)
            self.one += 1

        if 21.0 >  self.frame > 18.0 and self.one == 2:
            ULTSGEffect.ULT_SG_sound.play()
            ultsg = ULTSG(self.face)
            game_world.add_object(ultsg, 3)
            for mob in mob_group:
                game_world.add_collision_pairs(f'ultsg:{mob}', ultsg, None)
            self.one += 1

        if self.frame > 21.0:
            game_world.remove_object(self)

    def draw(self):
        if 18.0 < self.frame < 21.0:
            if self.face == 1:
                self.image[3].composite_draw(0, '', self.sx + 384, self.y + 256, 768, 768)
            elif self.face == -1:
                self.image[3].composite_draw(0, '', self.sx - 384, self.y + 256, 768, 768)
        if 15.0 < self.frame < 18.0:
            if self.face == 1:
                self.image[2].composite_draw(0, '', self.sx + 120, self.y + 120, 380, 358)
                self.image[2].composite_draw(0, '', self.sx + 370, self.y + 120, 380, 358)
                self.image[2].composite_draw(0, '', self.sx + 620, self.y + 120, 380, 358)
                self.image[2].composite_draw(0, '', self.sx + 120, self.y + 450, 380, 358)
                self.image[2].composite_draw(0, '', self.sx + 370, self.y + 450, 380, 358)
                self.image[2].composite_draw(0, '', self.sx + 620, self.y + 450, 380, 358)
            elif self.face == -1:
                self.image[2].composite_draw(0, '', self.sx - 120, self.y + 120, 380, 358)
                self.image[2].composite_draw(0, '', self.sx - 370, self.y + 120, 380, 358)
                self.image[2].composite_draw(0, '', self.sx - 620, self.y + 120, 380, 358)
                self.image[2].composite_draw(0, '', self.sx - 120, self.y + 450, 380, 358)
                self.image[2].composite_draw(0, '', self.sx - 370, self.y + 450, 380, 358)
                self.image[2].composite_draw(0, '', self.sx - 620, self.y + 450, 380, 358)
        if 9.0 < self.frame < 19.0:
            if self.face == 1:
                self.image[1].composite_draw(0, '', self.sx + 120, self.y + 120, 380, 358)
                self.image[1].composite_draw(0, '', self.sx + 370, self.y + 120, 380, 358)
                self.image[1].composite_draw(0, '', self.sx + 620, self.y + 120, 380, 358)
                self.image[1].composite_draw(0, '', self.sx + 120, self.y + 450, 380, 358)
                self.image[1].composite_draw(0, '', self.sx + 370, self.y + 450, 380, 358)
                self.image[1].composite_draw(0, '', self.sx + 620, self.y + 450, 380, 358)
            elif self.face == -1:
                self.image[1].composite_draw(0, '', self.sx - 120, self.y + 120, 380, 358)
                self.image[1].composite_draw(0, '', self.sx - 370, self.y + 120, 380, 358)
                self.image[1].composite_draw(0, '', self.sx - 620, self.y + 120, 380, 358)
                self.image[1].composite_draw(0, '', self.sx - 120, self.y + 450, 380, 358)
                self.image[1].composite_draw(0, '', self.sx - 370, self.y + 450, 380, 358)
                self.image[1].composite_draw(0, '', self.sx - 620, self.y + 450, 380, 358)
        if 6.0 < self.frame < 19.0:
            if self.face == 1:
                self.image[0].composite_draw(0, '', self.sx + 620, self.y + 120, 380, 358)
                self.image[0].composite_draw(0, '', self.sx + 620, self.y + 450, 380, 358)
            elif self.face == -1:
                self.image[0].composite_draw(0, '', self.sx - 620, self.y + 120, 380, 358)
                self.image[0].composite_draw(0, '', self.sx - 620, self.y + 450, 380, 358)
        if 3.0 < self.frame < 19.0:
            if self.face == 1:
                self.image[0].composite_draw(0, '', self.sx + 370, self.y + 120, 380, 358)
                self.image[0].composite_draw(0, '', self.sx + 370, self.y + 450, 380, 358)
            elif self.face == -1:
                self.image[0].composite_draw(0, '', self.sx - 370, self.y + 120, 380, 358)
                self.image[0].composite_draw(0, '', self.sx - 370, self.y + 450, 380, 358)
        if self.frame < 19.0:
            if self.face == 1:
                self.image[0].composite_draw(0, '', self.sx + 120, self.y + 120, 260, 358)
                self.image[0].composite_draw(0, '', self.sx + 120, self.y + 450, 260, 358)
            elif self.face == -1:
                self.image[0].composite_draw(0, '', self.sx - 120, self.y + 120, 260, 358)
                self.image[0].composite_draw(0, '', self.sx - 120, self.y + 450, 260, 358)