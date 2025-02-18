import server
import character
import game_world

from pico2d import load_image, draw_rectangle, load_wav

class Enhance:
    image = None
    Getitem_sound = None

    def __init__(self, i=0.0, j=0.0):
        self.x = i * 30.0 + 15.0
        self.y = j * 30.0 + 15.0
        self.sx = 0
        if Enhance.image == None:
            Enhance.image = load_image("./Item/" + 'Enhance' + ".png")
        if Enhance.Getitem_sound == None:
            Enhance.Getitem_sound = load_wav("./Sound/Getitem.mp3")
            Enhance.Getitem_sound.set_volume(32)

    def update(self):
        self.sx = self.x - server.background.window_left

    def draw(self):
        if -30 <= self.sx <= 1080 + 30:
            self.image.draw(self.sx, self.y + 15, 50, 50)
            if character.God:
                draw_rectangle(*self.get_rect())

    def get_bb(self):
        return self.x - 30.0, self.y - 15, self.x + 30.0, self.y + 45.0

    def get_rect(self):
        return self.sx - 30.0, self.y - 15, self.sx + 30.0, self.y + 45.0

    def handle_collision(self, group, other):
        if group == 'server.character:enhance':
            other.enhance(1)
            Enhance.Getitem_sound.play()
            game_world.remove_object(self)