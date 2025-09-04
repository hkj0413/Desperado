import server
import character
import game_framework
import game_world

from pico2d import draw_rectangle, load_image, load_wav

class NormalRF:
    image = None
    Lc_RF_sound = None

    def __init__(self, d):
        self.x = server.character.x + 78 * d
        self.y = server.character.y
        self.sx = 0
        self.damage = server.character.damage_RF
        self.timer = 0
        self.temp = 0
        self.count = 0
        self.one = 0
        self.face = d
        if NormalRF.image == None:
            NormalRF.image = load_image("./Effect/RF/" + 'Lc_RF' + " (1)" + ".png")
        if NormalRF.Lc_RF_sound == None:
            NormalRF.Lc_RF_sound = load_wav("./Sound/Lc_RF.mp3")
            NormalRF.Lc_RF_sound.set_volume(112)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.one == 0:
            NormalRF.Lc_RF_sound.play()
            self.one += 1

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.x += 20 * self.face
            if self.temp == 32 or self.count >= 4:
                game_world.remove_object(self)

    def draw(self):
        if character.God:
            draw_rectangle(*self.get_rect())
        if self.temp < 32 or self.count < 4:
            if self.face == 1:
                self.image.composite_draw(0, '', self.sx + 70, self.y - 20, 170, 70)
            elif self.face == -1:
                self.image.composite_draw(0, 'h', self.sx - 70, self.y - 20, 170, 70)

    def get_count(self):
        self.count += 1
        return

    def get_bb(self):
        if self.face == 1:
            return self.x, self.y - 25.0, self.x + 170.0, self.y + 5.0
        elif self.face == -1:
            return self.x - 170.0, self.y - 25.0, self.x, self.y + 5.0

    def get_rect(self):
        if self.face == 1:
            return self.sx, self.y - 25.0, self.sx + 170.0, self.y + 5.0
        elif self.face == -1:
            return self.sx - 170.0, self.y - 25.0, self.sx, self.y + 5.0

    def handle_collision(self, group, other):
        pass

    def give_damage(self):
        return self.damage