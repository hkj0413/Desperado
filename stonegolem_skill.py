import server
import character
import game_framework
import game_world

from pico2d import load_image, draw_rectangle

class StonegolemSkill:
    image = None

    def __init__(self):
        self.x = server.character.x
        self.y = 860
        self.sx = 0
        self.timer = 0
        self.temp = 0
        self.delay = 0
        if StonegolemSkill.image == None:
            StonegolemSkill.image = load_image("./Boss/Stonegolem/" + 'rock' + ".png")

    def update(self):
        self.sx = self.x - server.background.window_left

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.delay += 1
            if self.temp >= 40:
                self.y -= 10
                if self.temp == 112:
                    game_world.remove_object(self)

    def draw(self):
        if 40 < self.temp < 112:
            self.image.draw(self.sx, self.y, 108, 100)
            if character.God:
                draw_rectangle(*self.get_rect())
        if self.delay <= 20:
            draw_rectangle(*self.get_range())

    def get_bb(self):
        return self.x - 60.0, self.y - 45.0, self.x + 60.0, self.y + 45.0

    def get_rect(self):
        return self.sx - 60.0, self.y - 45.0, self.sx + 60.0, self.y + 45.0

    def get_range(self):
        return self.sx - 60.0, self.y - 770.0, self.sx + 60.0, self.y + 30.0

    def handle_collision(self, group, other):
        if group == 'server.character:stonegolemskill':
            other.take_damage(3)
            game_world.remove_object(self)