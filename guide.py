from pico2d import load_image, load_font

from character import Character

import guide_mode

class Guide:
    image = None

    def __init__(self, k):
        self.font = load_font('ENCR10B.TTF', 20)
        self.frame = k
        if Guide.image == None:
            Guide.image = [load_image("./Background/" + 'Guide' + " (%d)" % i + ".png") for i in range(1, 23 + 1)]

    def update(self):
        pass

    def draw(self):
        left = 60
        right = 1020
        bottom = 200
        top = 740

        center_x = (left + right) // 2
        center_y = (bottom + top) // 2
        width = right - left
        height = top - bottom

        self.image[self.frame].draw(center_x, center_y, width, height)

        if guide_mode.cn == 0:
            self.font.draw(70.0, 725.0, f'HP : {Character.hp}', (255, 0, 0))