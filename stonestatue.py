import server
import character
import game_framework
import random

from pico2d import load_image, draw_rectangle, load_wav
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector

animation_names = ['Idle', 'Walk', 'Hit', 'Die']

class Stonestatue:
    images = None
    Stonestatue_sound = None

    def load_images(self):
        if Stonestatue.images == None:
            Stonestatue.images = {}
            for name in animation_names:
                if name == 'Idle':
                    Stonestatue.images[name] = [load_image("./Mob/Stonestatue/"+ name + " (1)" + ".png")]
                elif name == 'Walk':
                    Stonestatue.images[name] = [load_image("./Mob/Stonestatue/"+ 'Idle' + " (1)" + ".png")]
                elif name == 'Hit':
                    Stonestatue.images[name] = [load_image("./Mob/Stonestatue/"+ name + " (1)" + ".png")]
                elif name == 'Die':
                    Stonestatue.images[name] = [load_image("./Mob/Stonestatue/" + name + " (%d)" % i + ".png") for i in range(1, 12 + 1)]

    def __init__(self, i=0.0, j=0):
        self.x = i * 30.0 + 15.0
        self.y = j * 30.0 + 15.0
        self.base_x = i * 30.0 + 15.0
        self.sx = 0
        self.face_dir = -1
        self.state = 0
        self.frame = 0
        self.name = 'Idle'
        self.prev_state = -1
        self.load_images()
        self.hp = 24
        self.stun = 0
        self.timer = 0
        self.temp = 0
        self.delay = False
        self.build_behavior_tree()
        if Stonestatue.Stonestatue_sound == None:
            Stonestatue.Stonestatue_sound = load_wav("./Sound/Hitsound.mp3")
            Stonestatue.Stonestatue_sound.set_volume(8)

    def update(self):
        self.sx = self.x - server.background.window_left

        self.timer += game_framework.frame_time

        if self.timer >= 0.5:
            self.timer = 0
            self.temp += 1
            self.delay = False
            if self.state == 3:
                if not self.stun == 0:
                    self.stun -= 1
                    self.temp = 0
                else:
                    self.state = 1
                    if server.character.x < self.x:
                        self.face_dir = -1
                    elif server.character.x > self.x:
                        self.face_dir = 1

            logic_map = {
                0: self.check_zero_logic,
                1: self.check_one_logic,
                2: self.check_two_logic,
                5: self.check_five_logic,
                6: self.check_six_logic,
            }

            if self.state in logic_map:
                logic_map[self.state]()

        if self.state != self.prev_state:
            self.bt.run()
            self.prev_state = self.state

        if self.state == 0:
            if self.name != 'Idle':
                self.name = 'Idle'
            self.frame = 0
        elif self.state == 1:
            if self.name != 'Walk':
                self.name = 'Walk'
            self.frame = 0
        elif self.state == 2 or self.state == 3:
            if self.name != 'Hit':
                self.name = 'Hit'
            self.frame = 0
        elif self.state == 4:
            if self.name != 'Die':
                self.name = 'Die'
            self.frame = self.frame + 12.0 * 0.75 * game_framework.frame_time
            if self.frame > 12.0:
                self.state = 5
                self.temp = 0
                self.frame = 0
        elif self.state == 6:
            if self.name != 'Idle':
                self.name = 'Idle'
            self.frame = 0

    def draw(self):
        if -20 <= self.sx <= 1080 + 20:
            if not self.state == 5:
                if self.face_dir == 1:
                    self.images[self.name][int(self.frame)].composite_draw(0, 'h', self.sx - 10, self.y + 60, 75, 150)
                elif self.face_dir == -1:
                    self.images[self.name][int(self.frame)].composite_draw(0, '', self.sx + 10, self.y + 60, 75, 150)
                if character.God:
                    draw_rectangle(*self.get_rect())

    def get_bb(self):
        return self.x - 20.0, self.y - 15.0, self.x + 20.0, self.y + 115.0

    def get_rect(self):
        return self.sx - 20.0, self.y - 15.0, self.sx + 20.0, self.y + 115.0

    def handle_collision(self, group, other):
        if group == 'server.character:stonestatue' and (self.state == 0 or self.state == 1):
            other.take_damage(4)
        elif group == 'normalrf:stonestatue' and (self.state == 0 or self.state == 1 or self.state == 3 or self.state == 6):
            self.take_damage(other.give_damage())
            other.get_count()
        elif group == 'normalrfsp:stonestatue' and (self.state == 0 or self.state == 1 or self.state == 3 or self.state == 6):
            self.take_damage(other.give_damage())
            other.get_count()
        elif group == 'normalhg:stonestatue' and (self.state == 0 or self.state == 1 or self.state == 3 or self.state == 6):
            self.take_damage(other.give_damage())
            other.get_count()

    def take_damage(self, damage):
        if (self.state == 0 or self.state == 1 or self.state == 3 or self.state == 6) and not self.delay:
            self.hp = max(0, self.hp - damage)
            Stonestatue.Stonestatue_sound.play()
            if self.hp <= 0:
                self.state = 4
                self.frame = 0
                character.Character.score += 1
                self.stun = 0
            else:
                self.state = 2
                if server.character.x < self.x:
                    self.face_dir = -1
                elif server.character.x > self.x:
                    self.face_dir = 1
            self.delay = True
            self.timer = 0

    def take_stun(self, stun):
        if self.state == 0 or self.state == 1 or self.state == 2:
            self.stun += stun
            self.state = 3

    def check_state(self, s):
        if self.state == s:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def check_zero_logic(self):
        if self.temp == 4 or random.randint(1, 5) == 1:
            self.state = 1
            self.temp = 0

    def check_zero(self):
        if not self.state == 0:
            return BehaviorTree.FAIL
        return BehaviorTree.SUCCESS

    def check_one_logic(self):
        if random.randint(1, 5) == 1:
            self.state = 0
            self.temp = 0

    def check_one(self):
        if not self.state == 1:
            return BehaviorTree.FAIL
        return BehaviorTree.SUCCESS

    def check_two_logic(self):
        if self.stun == 0:
            self.state = 1
        else:
            self.state = 3
        self.temp = 0

    def check_two(self):
        if not self.state == 2:
            return BehaviorTree.FAIL
        return BehaviorTree.SUCCESS

    def check_three(self):
        if not self.state == 3:
            return BehaviorTree.FAIL
        return BehaviorTree.SUCCESS

    def check_four(self):
        if not self.state == 4:
            return BehaviorTree.FAIL
        return BehaviorTree.SUCCESS

    def check_five_logic(self):
        if self.temp == 10:
            self.state = 6
            self.temp = 0
            self.hp = 24
            self.frame = 0
            self.x = self.base_x
            if server.character.x < self.x:
                self.face_dir = -1
            elif server.character.x > self.x:
                self.face_dir = 1

    def check_five(self):
        if not self.state == 5:
            return BehaviorTree.FAIL
        return BehaviorTree.SUCCESS

    def check_six_logic(self):
        if self.temp == 2:
            if self.stun == 0:
                self.state = 1
            else:
                self.state = 3
            self.temp = 0

    def check_six(self):
        if not self.state == 6:
            return BehaviorTree.FAIL
        return BehaviorTree.SUCCESS

    def build_behavior_tree(self):
        action_map = {
            0: self.check_zero,
            1: self.check_one,
            2: self.check_two,
            3: self.check_three,
            4: self.check_four,
            5: self.check_five,
            6: self.check_six
        }

        def run_state_actions():
            action = action_map.get(self.state, lambda: BehaviorTree.FAIL)
            return action()

        self.bt = BehaviorTree(Action('stonestatue_AI', run_state_actions))