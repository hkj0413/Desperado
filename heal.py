import server
import character

from pico2d import load_image, draw_rectangle, get_time, load_wav

class Heal:
    image = None
    Getitem_sound = None

    def __init__(self, i=0.0, j=0.0, k=0):
        self.x = i * 30.0 + 15.0
        self.y = j * 30.0 + 15.0
        self.sx = 0
        self.state = 0
        self.delay = 0
        self.heal = k
        if Heal.image == None:
            Heal.image = load_image("./Item/" + 'Heal' + ".png")
        if Heal.Getitem_sound == None:
            Heal.Getitem_sound = load_wav("./Sound/Getitem.mp3")
            Heal.Getitem_sound.set_volume(32)

    def update(self):
        self.sx = self.x - server.background.window_left
        if self.state == 1:
            if get_time() - self.delay > 30:
                self.state = 0

    def draw(self):
        if self.state == 0:
            if -30 <= self.sx <= 1080 + 30:
                self.image.draw(self.sx, self.y + 15, 75, 75)
                if character.God:
                    draw_rectangle(*self.get_rect())

    def get_bb(self):
        return self.x - 30.0, self.y - 15, self.x + 30.0, self.y + 45.0

    def get_rect(self):
        return self.sx - 30.0, self.y - 15, self.sx + 30.0, self.y + 45.0

    def handle_collision(self, group, other):
        if group == 'server.character:heal':
            if self.state == 0:
                self.state = 1
                self.delay = get_time()
                other.take_heal(self.heal)
                Heal.Getitem_sound.play()