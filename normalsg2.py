import server
import character
import game_framework
import game_world

from pico2d import draw_rectangle

class NormalSG2:
    def __init__(self, d):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.damage = server.character.damage_SG * 2
        self.frame = 0
        self.face = d

    def update(self):
        self.sx = self.x - server.background.window_left
        self.frame = self.frame + 9.0 * 1.5 * game_framework.frame_time
        if self.frame > 2.0:
            game_world.remove_object(self)

    def draw(self):
        if character.God:
            draw_rectangle(*self.get_rect())

    def get_bb(self):
        if self.face == 1:
            return self.x + 81.0 + 17.0, self.y - 49.0, self.x + 160.0 + 17.0, self.y + 19.0
        elif self.face == -1:
            return self.x - 160.0 - 17.0, self.y - 49.0, self.x - 81.0 - 17.0, self.y + 19.0

    def get_rect(self):
        if self.face == 1:
            return self.sx + 81.0 + 17.0, self.y - 49.0, self.sx + 160 + 17.0, self.y + 19.0
        elif self.face == -1:
            return self.sx - 160.0 - 17.0, self.y - 49.0, self.sx - 81.0 - 17.0, self.y + 19.0

    def handle_collision(self, group, other):
        mob_group = [
            'spore', 'slime', 'pig', 'stonegolem', 'skelldog', 'coldeye', 'wildboar', 'stonestatue',
            'bulldog', 'imp', 'fireboar', 'firemixgolem'
        ]
        for mob in mob_group:
            if group == f'normalsg2:{mob}':
                other.take_damage(self.damage)