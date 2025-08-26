import server
import character
import game_framework
import game_world

from pico2d import load_image, draw_rectangle, load_wav

class ReloadRF:
    image = None
    Reload_RF_sound = None

    def __init__(self, d):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.stun = server.character.stun_RF
        self.timer = 0
        self.temp = 0
        self.one = 0
        self.face = d
        if ReloadRF.image == None:
            ReloadRF.image = load_image("./Effect/RF/" + 'R_RF' + " (1)" + ".png")
        if ReloadRF.Reload_RF_sound == None:
            ReloadRF.Reload_RF_sound = load_wav("./Sound/Reload_RF.mp3")
            ReloadRF.Reload_RF_sound.set_volume(64)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.one == 0:
            ReloadRF.Reload_RF_sound.play()
            self.one += 1

        self.timer += game_framework.frame_time

        if self.timer >= 0.01:
            self.timer = 0
            self.temp += 1
            self.x += 20 * self.face
            if self.temp == 16:
                game_world.remove_object(self)

    def draw(self):
        if self.temp < 24:
            if self.face == 1:
                self.image.composite_draw(0, 'h', self.sx + 80, self.y - 10, 33, 52)
            elif self.face == -1:
                self.image.composite_draw(0, '', self.sx - 80, self.y - 10, 33, 52)
            if character.God:
                draw_rectangle(*self.get_rect())

    def get_count(self):
        self.count += 1
        return

    def get_bb(self):
        if self.face == 1:
            return self.x + 60.0, self.y - 30.0, self.x + 92.0, self.y + 10.0
        elif self.face == -1:
            return self.x - 92.0, self.y - 30.0, self.x - 60.0, self.y + 10.0

    def get_rect(self):
        if self.face == 1:
            return self.sx + 60.0, self.y - 30.0, self.sx + 92.0, self.y + 10.0
        elif self.face == -1:
            return self.sx - 92.0, self.y - 30.0, self.sx - 60.0, self.y + 10.0

    def handle_collision(self, group, other):
        mob_group = [
            'spore', 'slime', 'pig', 'stonegolem', 'skelldog', 'coldeye', 'wildboar', 'stonestatue',
            'bulldog', 'imp', 'fireboar', 'firemixgolem'
        ]
        for mob in mob_group:
            if group == f'reloadrf:{mob}':
                other.take_stun(self.stun)