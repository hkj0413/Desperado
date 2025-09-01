import server
import character
import game_framework
import game_world

from pico2d import draw_rectangle

class SkillSG:
    def __init__(self, d):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.damage = server.character.damage_SG * 4
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
            return self.x, self.y - 64.0, self.x + 180.0 + 17.0, self.y + 34.0
        elif self.face == -1:
            return self.x - 180.0 - 17.0, self.y - 64.0, self.x, self.y + 34.0

    def get_rect(self):
        if self.face == 1:
            return self.sx, self.y - 64.0, self.sx + 180.0 + 17.0, self.y + 34.0
        elif self.face == -1:
            return self.sx - 180.0 - 17.0, self.y - 64.0, self.sx, self.y + 34.0

    def handle_collision(self, group, other):
        if group == 'normalsg1:monster':
            if hasattr(other, 'take_damage'):
                other.take_damage(self.damage)