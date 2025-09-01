import server
import character
import game_framework
import game_world

from pico2d import load_image, load_wav

class UniqueRFEffect:
    image = None
    Unique_RF_shot_sound = None
    Unique_RF_last_sound = None

    def __init__(self, d):
        self.x = server.character.target_down_x
        self.y = server.character.target_down_y
        self.sx = 0
        self.frame = 0
        self.face = d
        if UniqueRFEffect.image == None:
            UniqueRFEffect.image = [load_image("./Effect/RF/" + 'Unique_RF' + " (%d)" % i + ".png") for i in range(1, 8 + 1)]
        if UniqueRFEffect.Unique_RF_shot_sound == None:
            UniqueRFEffect.Unique_RF_shot_sound = load_wav("./Sound/Unique_RF_shot.mp3")
            UniqueRFEffect.Unique_RF_last_sound = load_wav("./Sound/Unique_RF_last.mp3")
            UniqueRFEffect.Unique_RF_shot_sound.set_volume(64)
            UniqueRFEffect.Unique_RF_last_sound.set_volume(64)

    def update(self):
        self.sx = self.x - server.background.window_left

        if self.frame == 0:
            if not server.character.target_down_bullet == 0 or server.character.state == 4:
                UniqueRFEffect.Unique_RF_shot_sound.play()
            else:
                UniqueRFEffect.Unique_RF_last_sound.play()

        self.frame = self.frame + 8.0 * 1.5 * game_framework.frame_time
        if self.frame > 8.0:
            game_world.remove_object(self)

    def draw(self):
        if self.frame < 8.0:
            self.image[int(self.frame)].draw(self.sx + 10, self.y, 239, 141)