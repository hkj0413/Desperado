import server
import game_world

from pico2d import load_image, get_time, load_wav

class DashEffect:
    image = None
    Dash_sound = None

    def __init__(self, d):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.one = 0
        self.face = d
        self.wait_time = get_time()
        if DashEffect.image == None:
            DashEffect.image = load_image("./Effect/" + 'Dash' + " (1)" + ".png")
        if DashEffect.Dash_sound == None:
            DashEffect.Dash_sound = load_wav("./Sound/Dash.mp3")
            DashEffect.Dash_sound.set_volume(48)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.one == 0:
            DashEffect.Dash_sound.play()
            self.one += 1

        if get_time() - self.wait_time > 0.15:
            game_world.remove_object(self)

    def draw(self):
        if self.face == 1:
            self.image.composite_draw(0, 'h', self.sx, self.y - 17, 66, 128)
        elif self.face == -1:
            self.image.composite_draw(0, '', self.sx, self.y - 17, 66, 128)