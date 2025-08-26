import server
import character
import game_framework
import game_world

from pico2d import draw_rectangle

class UniqueRF:
    def __init__(self):
        self.x = character.mouse_x
        self.y = 900 - character.mouse_y
        self.sx = 0
        self.damage = server.character.damage_RF * 2
        self.frame = 0

    def update(self):
        self.sx = self.x - server.background.window_left
        self.frame = self.frame + 8.0 * 1.5 * game_framework.frame_time
        if self.frame > 2.0:
            game_world.remove_object(self)

    def draw(self):
        if character.God:
            draw_rectangle(*self.get_rect())

    def get_bb(self):
        if server.character.upgrade >= 3:
            return self.x - 75.0, self.y - 75.0, self.x + 75.0, self.y + 75.0
        else:
            return self.x - 45.0, self.y - 45.0, self.x + 45.0, self.y + 45.0

    def get_rect(self):
        if server.character.upgrade >= 3:
            return self.sx - 75.0, self.y - 75.0, self.sx + 75.0, self.y + 75.0
        else:
            return self.sx - 45.0, self.y - 45.0, self.sx + 45.0, self.y + 45.0

    def handle_collision(self, group, other):
        mob_group = [
            'spore', 'slime', 'pig', 'stonegolem', 'skelldog', 'coldeye', 'wildboar', 'stonestatue',
            'bulldog', 'imp', 'fireboar', 'firemixgolem'
        ]
        for mob in mob_group:
            if group == f'uniquerf:{mob}':
                other.take_damage(self.damage)