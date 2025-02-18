import server
import character

from pico2d import load_image, draw_rectangle

class Ladder:
    image = None

    def __init__(self, i=0.0, j=0.0, k=0):
        self.x = i * 40.0 + 20.0
        self.y = j * 40.0 + 20.0
        self.frame = k - 1
        self.sx = 0
        if Ladder.image == None:
            Ladder.image = [load_image("./Block/" + 'Block' + " (%d)" % i + ".png") for i in range(1, 14 + 1)]

    def update(self):
        self.sx = self.x - server.background.window_left

    def draw(self):
        if -20 <= self.sx <= 1620:
            self.image[self.frame].draw(self.sx, self.y, 40, 40)
            if character.God:
                draw_rectangle(*self.get_rect())

    def get_bb(self):
        return self.x - 20.0, self.y - 20.0, self.x + 20.0, self.y + 20.0

    def get_rect(self):
        return self.sx - 20.0, self.y - 20.0, self.sx + 20.0, self.y + 20.0

    def handle_collision(self, group, other):
        pass