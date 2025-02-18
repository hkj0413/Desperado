import play_mode
import server
import character

from pico2d import load_image, draw_rectangle, load_wav

class Portal:
    image = None
    image_medal = None
    sound = None

    def __init__(self, i=0.0, j=0.0, k=0):
        self.x = i * 30.0 + 15.0
        self.y = j * 30.0 + 15.0
        self.sx = 0
        self.need = k
        if Portal.image == None:
            Portal.image = load_image("./Block/" + 'Block' + " (15)" + ".png")
            Portal.image_medal = load_image("./Item/" + 'Medal' + ".png")
        if Portal.sound == None:
            Portal.sound = load_wav("./Sound/Portal.mp3")
            Portal.sound.set_volume(16)

    def update(self):
        self.sx = self.x - server.background.window_left

    def draw(self):
        if -45 <= self.sx <= 1080 + 45:
            self.image.draw(self.sx, self.y, 90, 90)
            if self.need == 3:
                self.image_medal.draw(self.sx - 27, self.y + 70, 37, 48)
                self.image_medal.draw(self.sx, self.y + 70, 37, 48)
                self.image_medal.draw(self.sx + 27, self.y + 70, 37, 48)
            elif self.need == 2:
                self.image_medal.draw(self.sx - 18, self.y + 70, 37, 48)
                self.image_medal.draw(self.sx + 18, self.y + 70, 37, 48)
            elif self.need == 1:
                self.image_medal.draw(self.sx, self.y + 70, 37, 48)
            if character.God:
                draw_rectangle(*self.get_rect())

    def get_bb(self):
        return self.x - 15.0, self.y - 15.0, self.x + 15.0, self.y + 15.0

    def get_rect(self):
        return self.sx - 15.0, self.y - 15.0, self.sx + 15.0, self.y + 15.0

    def handle_collision(self, group, other):
        '''
        if group == 'server.character:portal':
            if server.character.state == 0:
                if play_mode.stage <= 2:
                    Portal.sound.play()
                elif 5 >= play_mode.stage >= 3 and server.character.medal >= 1:
                    Portal.sound.play()
                elif play_mode.stage >= 6 and server.character.medal >= 2:
                    Portal.sound.play()
                    '''
        pass