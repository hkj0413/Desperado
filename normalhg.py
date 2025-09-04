import server
import character
import game_framework
import game_world

from pico2d import draw_rectangle, load_image, load_wav

class NormalHG:
    image = None
    Lc_HG_sound = None

    def __init__(self, d):
        self.x = server.character.x + 18 * d
        self.y = server.character.y
        self.sx = 0
        self.damage = server.character.damage_HG
        self.timer = 0
        self.temp = 0
        self.one = 0
        self.count = 0
        self.face = d
        if NormalHG.image == None:
            NormalHG.image = load_image("./Effect/HG/" + 'Lc_HG' + " (1)" + ".png")
        if NormalHG.Lc_HG_sound == None:
            NormalHG.Lc_HG_sound = load_wav("./Sound/Lc_HG.mp3")
            NormalHG.Lc_HG_sound.set_volume(64)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.one == 0:
            NormalHG.Lc_HG_sound.play()
            self.one += 1

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.x += 10 * self.face
            if self.temp == 36 or self.count >= 1:
                game_world.remove_object(self)

    def draw(self):
        if character.God:
            draw_rectangle(*self.get_rect())
        if self.temp < 36 or self.count < 1:
            if self.face == 1:
                self.image.composite_draw(0, '', self.sx + 15, self.y - 10, 30, 27)
            elif self.face == -1:
                self.image.composite_draw(0, 'h', self.sx - 15, self.y - 10, 30, 27)

    def get_count(self):
        self.count += 1
        return

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

    def handle_collision(self, group, other):
        pass

    def give_damage(self):
        return self.damage