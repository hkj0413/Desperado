import server
import game_framework
import game_world

from pico2d import load_image, load_wav, get_time

class ULTRF:
    image = None
    ULT_RF_sound = None

    def __init__(self):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = 0
        self.frame = 0
        self.one = 0
        self.time = get_time()
        if ULTRF.image == None:
            ULTRF.image = [load_image("./Effect/RF/" + 'ULT_RF' + " (%d)" % i + ".png") for i in range(1, 6 + 1)]
        if ULTRF.ULT_RF_sound == None:
            ULTRF.ULT_RF_sound = load_wav("./Sound/ULT_RF.ogg")
            ULTRF.ULT_RF_sound.set_volume(8)


    def update(self):
        self.x = server.character.x
        self.y = server.character.y
        self.sx = self.x - server.background.window_left

        if get_time() - self.time > 10.0:
            game_world.remove_object(self)

        if self.one == 0:
            ULTRF.ULT_RF_sound.play(10)
            self.one += 1

        if self.one == 1 and get_time() - self.time > 0.5:
            ULTRF.ULT_RF_sound.play(9)
            self.one += 1

        self.frame = (self.frame + 6.0 * 2.0 * game_framework.frame_time) % 6

    def draw(self):
        self.image[int(self.frame)].draw(self.sx, self.y - 15, 135, 127)