import server
import character
import game_framework

from pico2d import load_image, draw_rectangle, get_time

class Stone:
    image_base = None
    image_obstacle = None

    def __init__(self, i=0.0, j=0.0, k=0):
        self.x = i * 30.0 + 15.0
        self.y = j * 30.0 + 15.0
        self.base_y = j * 30.0 + 15.0
        self.sx = 0
        self.state = 2
        self.gravity = 0.0
        self.delay = 0
        self.start = k
        if Stone.image_base == None:
            Stone.image_base = load_image("./Obstacle/" + 'Stone_base' + ".png")
        if Stone.image_obstacle == None:
            Stone.image_obstacle = load_image("./Obstacle/" + 'Stone_obstacle' + ".png")

    def update(self):
        self.sx = self.x - server.background.window_left
        if self.state == 0:
            self.y -= self.gravity * character.RUN_SPEED_PPS * game_framework.frame_time
            self.gravity += 0.1
            if self.y < -10:
                self.gravity = 0.0
                self.state = 1
                self.y = self.base_y
                self.delay = get_time()
        elif self.state == 1:
            if get_time() - self.delay > 2:
                self.state = 0
        elif self.state == 2:
            if get_time() - self.delay > self.start:
                self.state = 0

    def draw(self):
        if -15 <= self.sx <= 1095:
            self.image_base.draw(self.sx + 1, self.base_y + 1)
            if self.state == 0:
                self.image_obstacle.draw(self.sx + 1, self.y - 2)
                if character.God:
                    draw_rectangle(*self.get_rect())

    def get_bb(self):
        return self.x - 15.0, self.y - 15.0, self.x + 15.0, self.y + 15.0

    def get_rect(self):
        return self.sx - 15.0, self.y - 15.0, self.sx + 15.0, self.y + 15.0

    def handle_collision(self, group, other):
        if group == 'server.character:stone':
            if self.state == 0:
                self.gravity = 0.0
                self.state = 1
                self.y = self.base_y
                self.delay = get_time()
                other.take_damage(1)