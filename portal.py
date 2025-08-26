import play_mode
import server
import character

from pico2d import load_image, draw_rectangle, load_wav

class Portal:
    image = None
    image_medal = None

    def __init__(self, i=0.0, j=0.0, k=0):
        self.x = i * 40.0 + 20.0
        self.y = j * 40.0 + 20.0
        self.sx = 0
        self.need = k
        if Portal.image == None:
            Portal.image = load_image("./Block/" + 'Block' + " (15)" + ".png")
            Portal.image_medal = load_image("./Item/" + 'Medal' + ".png")

    def update(self):
        self.sx = self.x - server.background.window_left

    def draw(self):
        if -60 <= self.sx <= 1620 + 60:
            self.image.draw(self.sx, self.y, 120, 120)
            if self.need == 3:
                self.image_medal.draw(self.sx - 35, self.y + 80, 37, 48)
                self.image_medal.draw(self.sx, self.y + 80, 37, 48)
                self.image_medal.draw(self.sx + 35, self.y + 80, 37, 48)
            elif self.need == 2:
                self.image_medal.draw(self.sx - 21, self.y + 80, 37, 48)
                self.image_medal.draw(self.sx + 21, self.y + 80, 37, 48)
            elif self.need == 1:
                self.image_medal.draw(self.sx, self.y + 80, 37, 48)
            if character.God:
                draw_rectangle(*self.get_rect())

    def get_bb(self):
        return self.x - 20.0, self.y - 20.0, self.x + 20.0, self.y + 20.0

    def get_rect(self):
        return self.sx - 20.0, self.y - 20.0, self.sx + 20.0, self.y + 20.0