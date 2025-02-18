import server
import character
import game_framework
import game_world

from pico2d import draw_rectangle

class RcskillHG:
    def __init__(self):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.damage = server.character.damage_HG * 2
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
        if server.character.upgrade >= 4:
            return self.x - 90.0 - 17.0, self.y - 75.0 - 49.0, self.x + 90.0 + 17.0, self.y + 75.0 + 19.0
        else:
            return self.x - 60.0 - 17.0, self.y - 45.0 - 49.0, self.x + 60.0 + 17.0, self.y + 45.0 + 19.0

    def get_rect(self):
        if server.character.upgrade >= 4:
            return self.sx - 90.0 - 17.0, self.y - 75.0 - 49.0, self.sx + 90.0 + 17.0, self.y + 75.0 + 19.0
        else:
            return self.sx - 60.0 - 17.0, self.y - 45.0 - 49.0, self.sx + 60.0 + 17.0, self.y + 45.0 + 19.0

    def handle_collision(self, group, other):
        mob_group = [
            'spore', 'slime', 'pig', 'stonegolem', 'skelldog', 'coldeye', 'wildboar', 'stonestatue',
            'bulldog', 'imp', 'fireboar', 'firemixgolem'
        ]
        for mob in mob_group:
            if group == f'rcskillhg:{mob}':
                other.take_damage(self.damage)