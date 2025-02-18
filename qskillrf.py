import server
import character
import game_framework
import game_world

from pico2d import draw_rectangle

class QskillRF:
    def __init__(self, d):
        self.x = server.character.x + 78 * d
        self.y = server.character.y
        self.sx = 0
        self.damage = server.character.damage_RF * 1.5
        self.timer = 0
        self.temp = 0
        self.face = d

    def update(self):
        self.sx = self.x - server.background.window_left

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.x += 40 * self.face
            if self.temp == 19:
                game_world.remove_object(self)

    def draw(self):
        if character.God:
            draw_rectangle(*self.get_rect())

    def get_bb(self):
        if self.face == 1:
            return self.x, self.y - 30.0, self.x + 280.0, self.y + 10.0
        elif self.face == -1:
            return self.x - 280.0, self.y - 30.0, self.x, self.y + 10.0

    def get_rect(self):
        if self.face == 1:
            return self.sx, self.y - 30.0, self.sx + 280.0, self.y + 10.0
        elif self.face == -1:
            return self.sx - 280.0, self.y - 30.0, self.sx, self.y + 10.0

    def handle_collision(self, group, other):
        mob_group = [
            'spore', 'slime', 'pig', 'stonegolem', 'skelldog', 'coldeye', 'wildboar', 'stonestatue',
            'bulldog', 'imp', 'fireboar', 'firemixgolem'
        ]
        for mob in mob_group:
            if group == f'qskillrf:{mob}':
                other.take_damage(self.damage)