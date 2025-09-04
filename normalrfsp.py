import server
import character
import game_framework
import game_world

from pico2d import draw_rectangle, load_image, load_wav

class NormalRFSP:
    image = None
    Lc_RF_superior_sound = None

    def __init__(self, d):
        self.x = server.character.x + 78 * d
        self.y = server.character.y
        self.sx = 0
        self.damage = server.character.damage_RF * 1.5
        self.timer = 0
        self.temp = 0
        self.count = 0
        self.one = 0
        self.face = d
        if NormalRFSP.image == None:
            NormalRFSP.image = load_image("./Effect/RF/" + 'Lc_RF_superior' + " (1)" + ".png")
        if NormalRFSP.Lc_RF_superior_sound == None:
            NormalRFSP.Lc_RF_superior_sound = load_wav("./Sound/Lc_RF_superior.mp3")
            NormalRFSP.Lc_RF_superior_sound.set_volume(96)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.one == 0:
            NormalRFSP.Lc_RF_superior_sound.play()
            self.one += 1

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.x += 30 * self.face
            if self.temp == 21 or self.count >= 6:
                game_world.remove_object(self)

    def draw(self):
        if character.God:
            draw_rectangle(*self.get_rect())
        if self.temp < 21 or self.count < 6:
            if self.face == 1:
                self.image.composite_draw(0, '', self.sx + 70, self.y - 10, 510, 90)
            elif self.face == -1:
                self.image.composite_draw(0, 'h', self.sx - 70, self.y - 10, 510, 90)

    def get_count(self):
        self.count += 1
        return

    def get_bb(self):
        if self.face == 1:
            return self.x, self.y - 30.0, self.x + 280.0, self.y + 10.0
        elif self.face == -1:
            return self.x - 280.0, self.y - 30.0, self.x, self.y + 10.0

    def get_rect(self):
        if self.face == 1:
            return self.sx, self.y - 30.0, self.sx + 280.0, self.y + 10.0
        elif self.face == -1:
            return self.sx - 280.0, self.y - 30.0, self.sx, self.y + 10.0

    def handle_collision(self, group, other):
        pass

    def give_damage(self):
        return self.damage