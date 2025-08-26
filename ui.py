from pico2d import load_image

from character import Character

import character

class UI:
    image_hp = None
    image_bullet = None
    image_enhance = None
    image_medal = None
    image_rc_sg = None
    image_q_sg = None
    image_c_sg = None
    image_rc_rf = None
    image_q_rf = None
    image_c_rf = None
    image_crc_rf = None
    image_rc_hg = None
    image_c_hg = None

    def __init__(self):
        if UI.image_hp == None:
            self.hp_image = [load_image("./Icon/" + 'Heart' + " (%d)" % i + ".png") for i in range(1, 3 + 1)]
            self.bullet_image = [load_image("./Icon/" + 'Bullet' + " (%d)" % i + ".png") for i in range(1, 8 + 1)]
            self.image_enhance = load_image("./Item/" + 'Enhance' + ".png")
            self.image_medal = load_image("./Item/" + 'Medal' + ".png")
            self.image_rc_sg = load_image("./Icon/" + 'SG_defensive_stance' + ".png")
            self.image_q_sg = load_image("./Icon/" + 'SG_hour_of_judgment' + ".png")
            self.image_c_sg = load_image("./Icon/" + 'SG_last_request' + ".png")
            self.image_rc_rf = load_image("./Icon/" + 'RF_target_down' + ".png")
            self.image_q_rf = load_image("./Icon/" + 'RF_perfect_shot' + ".png")
            self.image_c_rf = load_image("./Icon/" + 'RF_catastrophe' + ".png")
            self.image_crc_rf = load_image("./Icon/" + 'RF_bullseye' + ".png")
            self.image_rc_hg = load_image("./Icon/" + 'HG_dexterous_shot' + ".png")
            self.image_c_hg = load_image("./Icon/" + 'HG_equilibrium' + ".png")

    def update(self):
        pass

    def draw(self):
        heart_count = int(Character.max_hp / 2)
        hx = 20
        hy = 880

        for i in range(heart_count):
            if Character.hp >= (i + 1) * 2:
                self.hp_image[0].draw(hx + i * 30, hy, 30, 30)
            elif Character.hp == (i * 2) + 1:
                self.hp_image[1].draw(hx + i * 30, hy, 30, 30)
            else:
                self.hp_image[2].draw(hx + i * 30, hy, 30, 30)

        ex = 780
        ey = 880

        for i in range(5):
            if i < Character.upgrade:
                self.image_enhance.draw(ex - i * 35, ey, 33, 33)

        mx = 490
        my = 870

        for i in range(3):
            if i < Character.medal:
                self.image_medal.draw(mx + i * 50, my, 40, 60)

        bx = 1580
        by = 870

        if Character.stance == 0:
            self.image_rc_sg.draw(124 + 64 * 3, 40, 48 ,48)

            if Character.hour_of_judgment_cooldown == 0 and (character.God or Character.upgrade >= 1):
                self.image_q_sg.draw(124 + 64 * 6, 40, 48 ,48)

            if Character.last_request_cooldown == 0 and (character.God or Character.upgrade >= 3):
                self.image_c_sg.draw(124 + 64 * 12, 40, 48, 48)

            for i in range(12):
                if i < Character.bullet_SG:
                    self.bullet_image[0].draw(bx - i * 27, by, 27, 50)
                else:
                    self.bullet_image[1].draw(bx - i * 27, by, 27, 50)
            if Character.state == 1 or character.Reload_SG:
                for i in range(Character.shield_def):
                    self.bullet_image[6].draw(bx - i * 27, by - 40, 25, 30)
        elif Character.stance == 1:
            if Character.target_down_cooldown == 0 and not Character.state == 4:
                self.image_rc_rf.draw(124 + 64 * 3, 40, 48 ,48)

            elif Character.state == 4:
                self.image_crc_rf.draw(124 + 64 * 3, 40, 48, 48)

            if Character.perfect_shot_cooldown == 0 and (character.God or Character.upgrade >= 1) and not Character.state == 4:
                self.image_q_rf.draw(124 + 64 * 6, 40, 48 ,48)

            if Character.catastrophe_cooldown == 0 and (character.God or Character.upgrade >= 3):
                self.image_c_rf.draw(124 + 64 * 12, 40, 48, 48)

            for i in range(4):
                if i < Character.bullet_RF:
                    self.bullet_image[2].draw(bx - i * 27, by)
                else:
                    self.bullet_image[3].draw(bx - i * 27, by)
            if Character.state == 1:
                for i in range(Character.target_down_bullet):
                    self.bullet_image[7].draw(bx - i * 39 , by - 40, 33, 30)
                if not character.Attack:
                    self.bullet_image[7].draw(character.mouse_x, 900 - character.mouse_y,
                                              120 - Character.target_down_size, 120 - Character.target_down_size)
        elif Character.stance == 2:
            if Character.dexterous_shot_cooldown == 0:
                self.image_rc_hg.draw(124 + 64 * 3, 40, 48 ,48)

            if Character.equilibrium_cooldown == 0 and (character.God or Character.upgrade >= 3):
                self.image_c_hg.draw(124 + 64 * 12, 40, 48 ,48)

            for i in range(Character.max_bullet_HG):
                if i < Character.bullet_HG:
                    if i >= 20:
                        self.bullet_image[4].draw(bx - (i - 20) * 27, by - 44)
                    elif i >= 10:
                        self.bullet_image[4].draw(bx - (i - 10) * 27, by - 17)
                    else:
                        self.bullet_image[4].draw(bx - i * 27, by + 10)
                else:
                    if i >= 20:
                        self.bullet_image[5].draw(bx - (i - 20) * 27, by - 44)
                    elif i >= 10:
                        self.bullet_image[5].draw(bx - (i - 10) * 27, by - 17)
                    else:
                        self.bullet_image[5].draw(bx - i * 27, by + 10)