import server
import character
import game_framework
import game_world

from pico2d import draw_rectangle

class RcskillSG:
    def __init__(self):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.damage = server.character.damage * 2
        self.frame = 0

    def update(self):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = self.x - server.background.window_left

        self.frame = self.frame + 8.0 * 2.5 * game_framework.frame_time
        if self.frame > 2.0:
            game_world.remove_object(self)

    def draw(self):
        if character.God:
            draw_rectangle(*self.get_rect())

    def get_bb(self):
        return self.x - 30.0 - 17.0, self.y - 49.0, self.x + 30.0 + 17.0, self.y + 30.0 + 11.0

    def get_rect(self):
        return self.sx - 30.0 - 17.0, self.y - 49.0, self.sx + 30.0 + 17.0, self.y + 30.0 + 11.0

    def handle_collision(self, group, other):
        mob_group = [
            'spore', 'slime', 'pig', 'stonegolem', 'skelldog', 'coldeye', 'wildboar', 'stonestatue',
            'bulldog', 'imp', 'fireboar', 'firemixgolem'
        ]
        for mob in mob_group:
            if group == f'rcskillsg:{mob}':
                other.take_damage(self.damage)