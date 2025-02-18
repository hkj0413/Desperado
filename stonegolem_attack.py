import server
import character
import game_framework
import game_world

from pico2d import load_image, draw_rectangle

class StonegolemAttack:
    image = None

    def __init__(self, x=0.0, d=0):
        self.x = x
        self.y = server.character.y
        self.sx = 0
        self.timer = 0
        self.temp = 0
        self.delay = 0
        self.face = d
        if StonegolemAttack.image == None:
            StonegolemAttack.image = load_image("./Boss/Stonegolem/" + 'rock' + ".png")

    def update(self):
        self.sx = self.x - server.background.window_left

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.delay += 1
            if self.temp >= 40:
                self.x += 6 * self.face
                if self.temp == 160:
                    game_world.remove_object(self)

    def draw(self):
        if 40 < self.temp < 160:
            if self.face == 1:
                self.image.composite_draw(0, '', self.sx + 15, self.y - 10)
            elif self.face == -1:
                self.image.composite_draw(0, 'h', self.sx - 15, self.y - 10)
            if character.God:
                draw_rectangle(*self.get_rect())
        if self.delay <= 20:
            draw_rectangle(*self.get_range())

    def get_bb(self):
        if self.face == 1:
            return self.x, self.y - 30.0, self.x + 30.0, self.y + 10.0
        elif self.face == -1:
            return self.x - 30.0, self.y - 30.0, self.x, self.y + 10.0

    def get_rect(self):
        if self.face == 1:
            return self.sx, self.y - 30.0, self.sx + 30.0, self.y + 10.0
        elif self.face == -1:
            return self.sx - 30.0, self.y - 30.0, self.sx, self.y + 10.0

    def get_range(self):
        if self.face == 1:
            return self.sx, self.y - 30.0, self.sx + 720.0, self.y + 10.0
        elif self.face == -1:
            return self.sx - 720.0, self.y - 30.0, self.sx, self.y + 10.0

    def handle_collision(self, group, other):
        if group == 'server.character:stonegolemattack':
            other.take_damage(3)
            game_world.remove_object(self)