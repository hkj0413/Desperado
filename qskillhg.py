import server
import game_framework
import game_world

from pico2d import load_image, load_wav
from math import sin, pi

from qskillhg_effect import QskillHGEffect
from qskillhg_boom import QskillBoomHG

mob_group = [
    'spore', 'slime', 'pig', 'stonegolem', 'skelldog', 'coldeye', 'wildboar', 'stonestatue',
    'bulldog', 'imp', 'fireboar', 'firemixgolem'
             ]

class QskillHG:
    image = None
    Q_HG_shot_sound = None

    def __init__(self, d):
        self.x = server.character.x + 18 * d
        self.y = server.character.y - 19.0
        self.sx = 0
        self.damage = server.character.damage_HG * 2
        self.timer = 0
        self.temp = 0
        self.one = 0
        self.frame = 0
        self.face = d
        self.base_y = server.character.y - 19.0
        if QskillHG.image == None:
            QskillHG.image = [load_image("./Effect/HG/" + 'Q_HG' + " (%d)" % i + ".png") for i in range(1, 4 + 1)]
        if QskillHG.Q_HG_shot_sound == None:
            QskillHG.Q_HG_shot_sound = load_wav("./Sound/Q_HG_shot.mp3")
            QskillHG.Q_HG_shot_sound.set_volume(128)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.one == 0:
            QskillHG.Q_HG_shot_sound.play()
            self.one += 1

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.x += 8 * self.face
            self.y = self.base_y + 60 * sin(self.temp * pi / 30)
            if self.temp == 30:
                game_world.remove_object(self)
            elif self.temp == 28:
                self.frame = 3

                qskillhgeffect = QskillHGEffect(self.x, self.y)
                game_world.add_object(qskillhgeffect, 3)

                qskillboomhg = QskillBoomHG(self.x, self.y)
                game_world.add_object(qskillboomhg, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'qskillboomhg:{mob}', qskillboomhg, None)
            elif self.temp == 22:
                self.frame = 2
            elif self.temp == 16:
                self.frame = 1

    def draw(self):
        if self.temp < 30:
            if self.face == 1:
                self.image[self.frame].composite_draw(0, 'h', self.sx, self.y, 117, 101)
            elif self.face == -1:
                self.image[self.frame].composite_draw(0, '', self.sx, self.y, 117, 101)