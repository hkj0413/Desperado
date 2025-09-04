from pico2d import get_time, load_image, draw_rectangle, clamp, load_wav

import random

import game_world
import game_framework
import play_mode
import server
import ground

from normalsg_effect import NormalSGEffect
from normalsg1 import NormalSG1
from normalsg2 import NormalSG2
from normalsg3 import NormalSG3
from uniquesg_effect import UniqueSGEffect
from uniquesg import UniqueSG
from skillsg_effect import SkillSGEffect
from skillsg import SkillSG
from skillsg_stun import SkillstunSG
from ultsg_effect import ULTSGEffect

from rf_effect import RFEffect
from normalrf import NormalRF
from normalrfsp import NormalRFSP
from reloadrf import ReloadRF
from uniquerf import UniqueRF
from uniquerf_effect import UniqueRFEffect
from skillrf import SkillRF
from skillrf_effect import SkillRFEffect
from ultrf import ULTRF
from ultrf_effect import ULTRFEffect

from hg_effect import HGEffect
from normalhg import NormalHG
from ulthg_effect import ULTHGEffect
from ulthg import ULTHG

from state_machine import *

PIXEL_PER_METER = (34.0 / 1)  # 34 pixel 1 m
RUN_SPEED_KMPH = 10.0 # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

left_pressed = False
right_pressed = False
up_pressed = False
down_pressed = False
Move = False
Jump = False
Fall = False
Climb = False
Attack = False
attacking = False
Invincibility = False
God = False
Reload_SG = False
Reload_RF = False
rrf = False
Reload_HG = False
catastrophe = False

jump_velocity = 9.0
fall_velocity = 0.0
gravity = 0.3
random_angle = 0
chance = 0

mob_group = [
    'spore', 'slime', 'pig', 'stonegolem', 'skelldog', 'coldeye', 'wildboar', 'stonestatue',
    'bulldog', 'imp', 'fireboar', 'firemixgolem'
             ]

class Idle:
    @staticmethod
    def enter(character, e):
        global Jump, right_pressed, left_pressed, attacking, Reload_SG, Reload_HG, down_pressed, up_pressed, Invincibility, God, Attack
        if start_event(e):
            character.face_dir = 1
        elif right_up(e):
            right_pressed = False
        elif left_up(e):
            left_pressed = False
        elif walk(e):
            if left_pressed or right_pressed:
                character.state_machine.add_event(('WALK', 0))
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
        elif change_stance_z(e) and not Jump and not Fall and not Attack and Character.state == 0 and not Reload_SG and not Reload_HG:
            character.change_z()
        elif change_stance_x(e) and not Jump and not Fall and not Attack and Character.state == 0 and not Reload_SG and not Reload_HG:
            character.change_x()
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False
        elif s_down(e):
            if Character.stance == 0:
                if character.state == 0:
                    Character.state = 1
                    Character.speed = 1.5
                elif character.state == 1:
                    Character.state = 0
                    if not Reload_SG:
                        Character.speed = 3
            elif Character.stance == 1:
                if Character.state == 0:
                    if Character.target_down_cooldown == 0:
                        Character.state = 1
                        character.state_machine.add_event(('RF_RC', 0))
                elif Character.state == 3 and not Attack and Character.attack_delay == 0:
                    if character.attack_time == 0:
                        character.attack_time = get_time()
                        character.frame = 0

                        uniquerfeffect = UniqueRFEffect()
                        game_world.add_object(uniquerfeffect, 3)

                        uniquerf = UniqueRF()
                        game_world.add_object(uniquerf, 3)
                        game_world.add_collision_pairs(f'uniquerf:monster', uniquerf, None)

                        ultrfeffect = ULTRFEffect(character.face_dir)
                        game_world.add_object(ultrfeffect, 3)

                        rf_attack_voice_list = Character.voices['RF_Attack_Voice']
                        random.choice(rf_attack_voice_list).play()

                        Attack = True
            elif Character.stance == 2:
                if character.state == 0:
                    Character.state = 1
                elif character.state == 1:
                    Character.state = 0
        elif jump(e) and not Jump and not Fall and not Climb:
            if Character.stance == 0 and Character.state == 0:
                Jump = True
                Character.jump_sound.play()
                if not Attack and not Reload_SG:
                    character.frame = 0
            elif Character.stance == 1:
                if Character.state == 0:
                    if not Attack:
                        Jump = True
                        character.frame = 0
                        Character.jump_sound.play()
                elif Character.state == 3:
                    Jump = True
                    Character.jump_sound.play()
                    if not Attack:
                        character.frame = 0
            elif Character.stance == 2:
                Jump = True
                Character.jump_sound.play()
                if not Attack and not Reload_HG:
                    character.frame = 0
        elif reload(e):
            if Character.stance == 0 and Character.state <= 1 and not Attack:
                if not Reload_SG and Character.bullet_SG < 12:
                    Reload_SG = True
                    Character.bullet_SG = 0
                    Character.speed = 1.5
                    character.frame = 0
                    character.one = 0
            elif Character.stance == 1 and Character.bullet_RF == 0 and Character.state == 0:
                if down_pressed:
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_RELOAD_S', 0))
                elif not down_pressed:
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_RELOAD', 0))
            elif Character.stance == 2 and Character.bullet_HG == 0 and (Character.state == 0 or Character.state == 1):
                if not Reload_HG:
                    character.frame = 0
                    Invincibility = True
                    Character.Reload_HG_sound.play()
                    Character.voices['HG_Reload_Voice'][0].play()
                    character.state_machine.add_event(('HG_RELOAD', 0))
        elif skill(e):
            if Character.stance == 0 and Character.state == 0:
                if Character.hour_of_judgment_cooldown == 0 and not Attack and (God or Character.upgrade >= 1):
                    Character.state = 2
                    character.state_machine.add_event(('SG_SKILL', 0))
            elif Character.stance == 1 and Character.state == 0:
                if Character.perfect_shot_cooldown == 0 and (God or Character.upgrade >= 1):
                    Character.state = 2
                    character.state_machine.add_event(('RF_SKILL', 0))
            elif Character.stance == 2:
                if Character.at02_grenade_cooldown == 0 and Character.bullet_HG > 0 and (God or Character.upgrade >= 1):
                    Character.hit_delay = 0.5
                    Character.bullet_HG -= 1

                    hg_q_voice_list = Character.voices['HG_Q_Voice']
                    random.choice(hg_q_voice_list).play()

                    if God:
                        Character.at02_grenade_cooldown = 1
                    else:
                        Character.at02_grenade_cooldown = 4
        elif ultimate(e):
            if Character.stance == 0 and Character.state == 0:
                if Character.last_request_cooldown == 0 and (God or Character.upgrade >= 3):
                    Character.state = 3
                    Invincibility = True
                    character.state_machine.add_event(('SG_ULT', 0))
            elif Character.stance == 1 and Character.state == 0:
                if Character.catastrophe_cooldown == 0 and (God or Character.upgrade >= 3):
                    Character.state = 3
                    Invincibility = True
                    character.state_machine.add_event(('RF_ULT', 0))
            elif Character.stance == 2 and Character.state == 0:
                if Character.equilibrium_cooldown == 0 and (God or Character.upgrade >= 3):
                    Character.state = 3
                    Invincibility = True
                    character.state_machine.add_event(('HG_ULT', 0))

        elif temp_god(e):
           God = not God
        elif temp_bullet(e) and God:
            Character.bullet_SG = 0
            Character.bullet_RF = 0
            Character.bullet_HG = 0
        elif temp_up(e) and God:
            Character.enhance(e, 1)
        elif temp_down(e) and God:
            Character.enhance(e, -1)
        elif temp_medal(e) and God:
            if Character.medal < 3:
                Character.medal += 1
        elif temp_die(e):
            Character.take_damage(character, 100)

        if Character.stance == 0 and not Reload_SG:
            if Character.state == 0:
                if character.name != 'Idle_SG':
                    character.name = 'Idle_SG'
            elif Character.state == 1:
                if character.name != 'Unique_SG':
                    character.name = 'Unique_SG'
            character.frame = clamp(0, character.frame, 13)
        elif Character.stance == 0 and Reload_SG:
            if character.name != 'Reload_SG':
                character.name = 'Reload_SG'
        elif Character.stance == 1:
            if character.name != 'Idle_RF':
                character.name = 'Idle_RF'
            character.frame = clamp(0, character.frame, 13)
        elif Character.stance == 2:
            if character.name != 'Idle_HG':
                character.name = 'Idle_HG'
            character.frame = clamp(0, character.frame, 13)

    @staticmethod
    def exit(character, e):
        if right_down(e):
            character.face_dir = 1
        elif left_down(e):
            character.face_dir = -1

    @staticmethod
    def do(character):
        global Move, Reload_SG ,Reload_HG, Invincibility
        if Attack:
            if Character.stance == 0:
                character.frame = (character.frame + 15.0 * 0.8 * game_framework.frame_time) % 15
            elif Character.stance == 1:
                character.frame = (character.frame + 7.0 * 2.0 * game_framework.frame_time) % 7
            elif Character.stance == 2:
                character.frame = (character.frame + 4.0 * 2.5 * game_framework.frame_time) % 4

        elif Reload_SG:
            character.frame = character.frame + 16.0 * 0.7 * game_framework.frame_time
            if character.frame > 16.0:
                if Character.state == 0:
                    Character.speed = 3
                elif Character.state == 1:
                    Character.speed = 1.5
                Character.bullet_SG = 12
                character.frame = 0
                Reload_SG = False
                if random.random() < 0.25:
                    Character.voices['SG_Reload_Voice'][0].play()
                if right_pressed or left_pressed:
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))
            elif character.frame > 4.0 and character.one == 0:
                Character.Reload_SG_sound.play()
                character.one += 1

        elif not Jump and not Fall:
            if Move:
                Move = False
            character.frame = (character.frame + 14.0 * 1.5 * game_framework.frame_time) % 14

        if Climb:
            if up_pressed and not down_pressed:
                dy = Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                character.y += dy
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y -= dy
                            return

            elif down_pressed and not up_pressed:
                dy = Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                character.y -= dy
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y += dy
                            return

    @staticmethod
    def draw(character):
        if Attack:
            if character.face_dir == 1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
            elif character.face_dir == -1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
        elif Reload_SG or Reload_HG:
            if character.face_dir == 1:
                character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
            elif character.face_dir == -1:
                character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

        elif Character.stance == 0 and Character.state == 1:
            if character.face_dir == 1:
                character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
            elif character.face_dir == -1:
                character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

        elif Jump or Fall:
            if character.face_dir == 1:
                if Character.stance == 0:
                    character.images['Walk_SG'][0].composite_draw(0, '', character.sx, character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Walk_RF'][0].composite_draw(0, '', character.sx, character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Walk_HG'][0].composite_draw(0, '', character.sx, character.y, 170, 170)
            elif character.face_dir == -1:
                if Character.stance == 0:
                    character.images['Walk_SG'][0].composite_draw(0, 'h', character.sx, character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Walk_RF'][0].composite_draw(0, 'h', character.sx, character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Walk_HG'][0].composite_draw(0, 'h', character.sx, character.y, 170, 170)
        else:
            if character.face_dir == 1:
                character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
            elif character.face_dir == -1:
                character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

class Walk:
    @staticmethod
    def enter(character, e):
        global left_pressed, right_pressed, Jump, attacking, Reload_SG, Reload_HG, down_pressed, up_pressed, Invincibility, God, Attack
        if right_down(e):
            right_pressed = True
            character.face_dir = 1
        elif right_up(e):
            right_pressed = False
            if left_pressed:
                character.face_dir = -1
            elif not left_pressed:
                character.state_machine.add_event(('IDLE', 0))
        elif left_down(e):
            left_pressed = True
            character.face_dir = -1
        elif left_up(e):
            left_pressed = False
            if right_pressed:
                character.face_dir = 1
            elif not right_pressed:
                character.state_machine.add_event(('IDLE', 0))
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
            if not right_pressed and not left_pressed and not down_pressed and Climb:
                character.state_machine.add_event(('IDLE', 0))
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
            if not right_pressed and not left_pressed and not up_pressed and Climb:
                character.state_machine.add_event(('IDLE', 0))
        elif change_stance_z(e) and not Jump and not Fall and not Attack and Character.state == 0 and not Reload_SG and not Reload_HG:
            character.change_z()
        elif change_stance_x(e) and not Jump and not Fall and not Attack and Character.state == 0 and not Reload_SG and not Reload_HG:
            character.change_x()
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False
        elif s_down(e):
            if Character.stance == 0:
                if character.state == 0:
                    Character.state = 1
                    Character.speed = 1.5
                elif character.state == 1:
                    Character.state = 0
                    if not Reload_SG:
                        Character.speed = 3
            elif Character.stance == 1:
                if Character.state == 0:
                    if Character.target_down_cooldown == 0:
                        Character.state = 1
                        character.state_machine.add_event(('RF_RC', 0))
                elif Character.state == 3 and not Attack and Character.attack_delay == 0:
                    if character.attack_time == 0:
                        character.attack_time = get_time()
                        character.frame = 0

                        uniquerfeffect = UniqueRFEffect()
                        game_world.add_object(uniquerfeffect, 3)

                        uniquerf = UniqueRF()
                        game_world.add_object(uniquerf, 3)
                        game_world.add_collision_pairs(f'uniquerf:monster', uniquerf, None)

                        ultrfeffect = ULTRFEffect(character.face_dir)
                        game_world.add_object(ultrfeffect, 3)

                        rf_attack_voice_list = Character.voices['RF_Attack_Voice']
                        random.choice(rf_attack_voice_list).play()

                        Attack = True
            elif Character.stance == 2:
                if character.state == 0:
                    Character.state = 1
                elif character.state == 1:
                    Character.state = 0
        elif jump(e) and not Jump and not Fall and not Climb:
            if Character.stance == 0 and Character.state == 0:
                Jump = True
                Character.jump_sound.play()
                if not Attack and not Reload_SG:
                    character.frame = 0
            elif Character.stance == 1:
                if Character.state == 0:
                    if not Attack:
                        Jump = True
                        character.frame = 0
                        Character.jump_sound.play()
                elif Character.state == 3:
                    Jump = True
                    Character.jump_sound.play()
                    if not Attack:
                        character.frame = 0
            elif Character.stance == 2:
                Jump = True
                Character.jump_sound.play()
                if not Attack and not Reload_HG:
                    character.frame = 0
        elif reload(e):
            if Character.stance == 0 and Character.state <= 1 and not Attack:
                if not Reload_SG and Character.bullet_SG < 12:
                    Reload_SG = True
                    Character.bullet_SG = 0
                    Character.speed = 1.5
                    character.frame = 0
                    character.one = 0
            elif Character.stance == 1 and Character.bullet_RF == 0 and Character.state == 0:
                if down_pressed:
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_RELOAD_S', 0))
                elif not down_pressed:
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_RELOAD', 0))
            elif Character.stance == 2 and Character.bullet_HG == 0 and (Character.state == 0 or Character.state == 1):
                if not Reload_HG:
                    character.frame = 0
                    Invincibility = True
                    Character.Reload_HG_sound.play()
                    Character.voices['HG_Reload_Voice'][0].play()
                    character.state_machine.add_event(('HG_RELOAD', 0))
        elif skill(e):
            if Character.stance == 0 and Character.state == 0:
                if Character.hour_of_judgment_cooldown == 0 and not Attack and (God or Character.upgrade >= 1):
                    Character.state = 2
                    character.state_machine.add_event(('SG_SKILL', 0))
            elif Character.stance == 1 and Character.state == 0:
                if Character.perfect_shot_cooldown == 0 and (God or Character.upgrade >= 1):
                    Character.state = 2
                    character.state_machine.add_event(('RF_SKILL', 0))
            elif Character.stance == 2:
                if Character.at02_grenade_cooldown == 0 and Character.bullet_HG > 0 and (God or Character.upgrade >= 1):
                    Character.hit_delay = 0.5
                    Character.bullet_HG -= 1

                    hg_q_voice_list = Character.voices['HG_Q_Voice']
                    random.choice(hg_q_voice_list).play()

                    if God:
                        Character.at02_grenade_cooldown = 1
                    else:
                        Character.at02_grenade_cooldown = 4
        elif ultimate(e):
            if Character.stance == 0 and Character.state == 0:
                if Character.last_request_cooldown == 0 and (God or Character.upgrade >= 3):
                    Character.state = 3
                    Invincibility = True
                    character.state_machine.add_event(('SG_ULT', 0))
            elif Character.stance == 1 and Character.state == 0:
                if Character.catastrophe_cooldown == 0 and (God or Character.upgrade >= 3):
                    Character.state = 3
                    Invincibility = True
                    character.state_machine.add_event(('RF_ULT', 0))
            elif Character.stance == 2 and Character.state == 0:
                if Character.equilibrium_cooldown == 0 and (God or Character.upgrade >= 3):
                    Character.state = 3
                    Invincibility = True
                    character.state_machine.add_event(('HG_ULT', 0))

        elif temp_god(e):
           God = not God
        elif temp_bullet(e) and God:
            Character.bullet_SG = 0
            Character.bullet_RF = 0
            Character.bullet_HG = 0
        elif temp_up(e) and God:
            Character.enhance(e, 1)
        elif temp_down(e) and God:
            Character.enhance(e, -1)
        elif temp_medal(e) and God:
            if Character.medal < 3:
                Character.medal += 1
        elif temp_die(e):
            Character.take_damage(character, 100)

        if Character.stance == 0 and not Reload_SG:
            if Character.state == 0:
                if character.name != 'Walk_SG':
                    character.name = 'Walk_SG'
            elif Character.state == 1:
                if character.name != 'Unique_SG':
                    character.name = 'Unique_SG'
        elif Character.stance == 0 and Reload_SG:
            if character.name != 'Reload_SG':
                character.name = 'Reload_SG'
        elif Character.stance == 1:
            if character.name != 'Walk_RF':
                character.name = 'Walk_RF'
        elif Character.stance == 2 and Reload_HG:
            if character.name != 'Reload_HG':
                character.name = 'Reload_HG'
        elif Character.stance == 2:
            if character.name != 'Walk_HG':
                character.name = 'Walk_HG'

        if not Reload_SG and not Reload_HG:
            if Character.stance == 0 and Character.state == 1:
                character.frame = clamp(0, character.frame, 13)
            else:
                character.frame = clamp(0, character.frame, 5)

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Fall, Move, Climb, Reload_SG, Reload_HG, Invincibility
        if not Move:
            Move = True

        if Attack:
            if Character.stance == 0:
                character.frame = (character.frame + 15.0 * 0.8 * game_framework.frame_time) % 15
            elif Character.stance == 1:
                character.frame = (character.frame + 7.0 * 2.0 * game_framework.frame_time) % 7
            elif Character.stance == 2:
                character.frame = (character.frame + 4.0 * 2.5 * game_framework.frame_time) % 4

        elif Reload_SG:
            character.frame = character.frame + 16.0 * 0.7 * game_framework.frame_time
            if character.frame > 16.0:
                if Character.state == 0:
                    Character.speed = 3
                elif Character.state == 1:
                    Character.speed = 1.5
                Character.bullet_SG = 12
                character.frame = 0
                Reload_SG = False
                if random.random() < 0.25:
                    Character.voices['SG_Reload_Voice'][0].play()
                if right_pressed or left_pressed:
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))
            elif character.frame > 4.0 and character.one == 0:
                Character.Reload_SG_sound.play()
                character.one += 1

        else:
            if Character.stance == 0 and Character.state == 1:
                character.frame = (character.frame + 14.0 * 1.5 * game_framework.frame_time) % 14
            elif not Jump and not Fall:
                character.frame = (character.frame + 6.0 * 2.0 * game_framework.frame_time) % 6

        if Climb:
            if up_pressed and not down_pressed:
                dy = Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                character.y += dy
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y -= dy
                            return

            elif down_pressed and not up_pressed:
                dy = Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                character.y -= dy
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y += dy
                            return

        dx = 0.0
        moved = False

        if right_pressed or left_pressed:
            if Character.stance == 0:
                if not Attack:
                    dx = Character.speed * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time
            elif Character.stance == 1:
                if (Character.state == 0 and not Attack) or Character.state == 3:
                    dx = Character.speed * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time
            elif Character.stance == 2:
                if not Character.state == 2:
                    dx = Character.speed * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time

            if dx != 0.0:
                character.x += dx
                moved = True

            if moved:
                for block in game_world.collision_pairs['server.character:ground'][1] + game_world.collision_pairs['server.character:wall'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.x -= dx
                            return

            ground_objects = game_world.collision_pairs['server.character:ground'][1]
            for block in ground_objects:
                if screen_left - 20 <= block.x <= screen_right + 20:
                    if game_world.collide_ad(character, block, ground_objects):
                        Fall = True
                        return

            for block in game_world.collision_pairs['server.character:ladder'][1]:
                if screen_left - 20 <= block.x <= screen_right + 20:
                    if game_world.collide_ladder(character, block):
                        Fall = True
                        Climb = False
                        return

    @staticmethod
    def draw(character):
        if Attack:
            if character.face_dir == 1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
            elif character.face_dir == -1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
        else:
            if character.face_dir == 1:
                character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                        character.y, 170, 170)
            elif character.face_dir == -1:
                character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                        character.y, 170, 170)

class Hit:
    @staticmethod
    def enter(character, e):
        global left_pressed, right_pressed, Jump, jump_velocity, Fall, attacking, down_pressed, up_pressed, catastrophe
        if take_hit(e):
            if Character.stance == 0 and (Character.state == 1 or Reload_SG):
                Character.hp = max(0, Character.hp - max(0, (Character.damage - Character.shield_def)))
                if Character.hp == 0:
                    Character.speed = 3
                    character.state_machine.add_event(('DIE', 0))
                else:
                    sg_rc_voice_list = Character.voices['SG_Unique_Voice']
                    if random.random() < 0.25:
                        Character.Unique_SG_counter_sound.play()

                        uniquesgeffect = UniqueSGEffect()
                        game_world.add_object(uniquesgeffect, 3)

                        uniquesg = UniqueSG()
                        game_world.add_object(uniquesg, 3)
                        game_world.add_collision_pairs(f'uniquesg:monster', uniquesg, None)

                        random.choice(sg_rc_voice_list).play()
                    else:
                        Character.Unique_SG_sound.play()
                    if left_pressed or right_pressed:
                        character.state_machine.add_event(('WALK', 0))
            elif Character.stance == 1 and Character.state == 3 and catastrophe:
                Character.hp = max(0, Character.hp - Character.damage)
                if Character.hp == 0:
                    Character.catastrophe_duration = 0
                    Character.catastrophe_cooldown = 120
                    Character.speed = 4
                    Character.state = 0
                    catastrophe = False
                    character.catastrophe_time = 0
                    character.state_machine.add_event(('DIE', 0))
                elif left_pressed or right_pressed:
                    character.state_machine.add_event(('WALK', 0))
            elif Character.stance == 2 and Character.state == 1:
                Jump = False
                jump_velocity = 9.0
                Fall = True
                if not Attack:
                    character.frame = 0
                Character.hp = max(0, Character.hp - Character.damage)
                if Character.hp == 0:
                    character.state_machine.add_event(('DIE', 0))
                else:
                    hg_hit_voice_list = Character.voices['HG_Hit_Voice']
                    random.choice(hg_hit_voice_list).play()
            elif Character.state == 0:
                Jump = False
                jump_velocity = 9.0
                Fall = True
                Character.state = 0
                if not Attack:
                    character.frame = 0
                Character.hp = max(0, Character.hp - Character.damage)
                if Character.hp == 0:
                    character.state_machine.add_event(('DIE', 0))
                else:
                    if Character.stance == 0:
                        sg_hit_voice_list = Character.voices['SG_Hit_Voice']
                        random.choice(sg_hit_voice_list).play()
                    elif Character.stance == 1:
                        rf_hit_voice_list = Character.voices['RF_Hit_Voice']
                        random.choice(rf_hit_voice_list).play()
                    elif Character.stance == 2:
                        hg_hit_voice_list = Character.voices['HG_Hit_Voice']
                        random.choice(hg_hit_voice_list).play()
            character.wait_time = get_time()
            Character.hit_delay = 1
        elif right_up(e):
            right_pressed = False
        elif left_up(e):
            left_pressed = False
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False
        elif right_down(e):
            right_pressed = True
            character.face_dir = 1
            if Character.stance == 0 and Character.state == 1:
                character.state_machine.add_event(('WALK', 0))
        elif left_down(e):
            left_pressed = True
            character.face_dir = -1
            if Character.stance == 0 and Character.state == 1:
                character.state_machine.add_event(('WALK', 0))
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
        elif s_down(e):
            if Character.stance == 0:
                if Character.state == 0:
                    Character.state = 1
                    Character.speed = 1.5
                elif Character.state == 1:
                    Character.state = 0
                    if not Reload_SG:
                        Character.speed = 3
            elif Character.stance == 2:
                if character.state == 0:
                    Character.state = 1
                elif character.state == 1:
                    Character.state = 0

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Reload_SG, Reload_HG, Invincibility
        if get_time() - character.wait_time > 0.5:
            if left_pressed or right_pressed or (Climb and (up_pressed or down_pressed)):
                character.state_machine.add_event(('WALK', 0))
            else:
                character.state_machine.add_event(('TIME_OUT', 0))

        if Attack:
            if Character.stance == 0:
                character.frame = (character.frame + 15.0 * 0.8 * game_framework.frame_time) % 15
            elif Character.stance == 1:
                character.frame = (character.frame + 7.0 * 2.0 * game_framework.frame_time) % 7
            elif Character.stance == 2:
                character.frame = (character.frame + 4.0 * 2.5 * game_framework.frame_time) % 4

        elif Reload_SG:
            character.frame = character.frame + 16.0 * 1.0 * game_framework.frame_time
            if character.frame > 16.0:
                if Character.state == 0:
                    Character.speed = 3
                elif Character.state == 1:
                    Character.speed = 1.5
                Character.bullet_SG = 12
                character.frame = 0
                Reload_SG = False

        else:
            if Character.stance == 0 and Character.state == 1:
                character.frame = (character.frame + 14.0 * 1.5 * game_framework.frame_time) % 14

    @staticmethod
    def draw(character):
        if Attack:
            if character.face_dir == 1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
            elif character.face_dir == -1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

        elif (Character.state == 0 and not Reload_SG and not Reload_HG) or (Character.stance == 2 and Character.state == 1):
            if character.face_dir == 1:
                if Character.stance == 0:
                    character.images['Hit_SG'][0].composite_draw(0, '', character.sx, character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Hit_RF'][0].composite_draw(0, '', character.sx, character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Hit_HG'][0].composite_draw(0, '', character.sx, character.y, 170, 170)
            elif character.face_dir == -1:
                if Character.stance == 0:
                    character.images['Hit_SG'][0].composite_draw(0, 'h', character.sx, character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Hit_RF'][0].composite_draw(0, 'h', character.sx, character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Hit_HG'][0].composite_draw(0, 'h', character.sx, character.y, 170, 170)
        else:
            if character.face_dir == 1:
                character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
            elif character.face_dir == -1:
                character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

class Die:
    @staticmethod
    def enter(character, e):
        global left_pressed, right_pressed, Jump, jump_velocity, Fall, fall_velocity, Attack, attacking, Move, down_pressed, up_pressed
        global Reload_SG, Reload_RF, rrf, Reload_HG, Climb, Invincibility
        if die(e):
            Move = False
            Jump = False
            Fall = False
            character._reset_jump_after_ground()
            Climb = False
            Attack = False
            attacking = False
            Invincibility = False
            left_pressed = False
            right_pressed = False
            up_pressed = False
            down_pressed = False
            Reload_SG = False
            Reload_RF = False
            rrf = False
            Reload_HG = False
            jump_velocity = 9.0
            fall_velocity = 0.0
            character.frame = 0
            Character.state = -1
            Character.attack_delay = 0
            character.attack_cool = 0
            character.attack_time = 0
            character.hit_cool = 0
            character.wait_time = get_time()
            if Character.stance == 0:
                sg_die_voice_list = Character.voices['SG_Die_Voice']
                random.choice(sg_die_voice_list).play()
            elif Character.stance == 1:
                rf_die_voice_list = Character.voices['RF_Die_Voice']
                random.choice(rf_die_voice_list).play()
            elif Character.stance == 2:
                hg_die_voice_list = Character.voices['HG_Die_Voice']
                random.choice(hg_die_voice_list).play()

    @staticmethod
    def exit(character, e):
        if time_out(e):
            character.x, character.y = 34, 170.0
            server.background.window_left = 0
            Character.state = 0
            Character.hit_delay = 1
            if Character.stance == 0:
                Character.speed = 3
            elif Character.stance == 1:
                Character.speed = 4
            elif Character.stance == 2:
                Character.speed = 5
            if Character.hp == 0:
                Character.hp = Character.max_hp
                Character.bullet_SG = 12
                Character.bullet_RF = 4
                Character.bullet_HG = Character.max_bullet_HG
                if play_mode.stage == 3:
                    play_mode.change_stage(play_mode.stage - 1)

    @staticmethod
    def do(character):
        if get_time() - character.wait_time > 3:
            character.state_machine.add_event(('TIME_OUT', 0))
        if Character.stance == 0 or Character.stance == 1:
            character.frame = character.frame + 18.0 * 1.0 * game_framework.frame_time
        elif Character.stance == 2:
            character.frame = character.frame + 11.0 * 1.0 * game_framework.frame_time

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            if Character.stance == 0 and int(character.frame) <= 17.0:
                character.images['Die_SG'][int(character.frame)].composite_draw(0, '', character.sx - 48, character.y, 170, 170)
            elif Character.stance == 1 and int(character.frame) <= 17.0:
                character.images['Die_RF'][int(character.frame)].composite_draw(0, '', character.sx - 11, character.y, 170, 170)
            elif Character.stance == 2 and int(character.frame) <= 10.0:
                character.images['Die_HG'][int(character.frame)].composite_draw(0, '', character.sx - 15, character.y, 170, 170)
        elif character.face_dir == -1:
            if Character.stance == 0 and int(character.frame) <= 17.0:
                character.images['Die_SG'][int(character.frame)].composite_draw(0, 'h', character.sx + 48, character.y, 170, 170)
            elif Character.stance == 1 and int(character.frame) <= 17.0:
                character.images['Die_RF'][int(character.frame)].composite_draw(0, 'h', character.sx + 11, character.y, 170, 170)
            elif Character.stance == 2 and int(character.frame) <= 10.0:
                character.images['Die_HG'][int(character.frame)].composite_draw(0, 'h', character.sx + 15, character.y, 170, 170)

class SSG:
    @staticmethod
    def enter(character, e):
        global right_pressed, left_pressed, attacking, down_pressed, up_pressed, Move, Jump
        if sg_skill(e):
            Move = False
            character.frame = 0
            character.wait_time = get_time()
            character.face_dir = character.face_dir

            skillsgeffect = SkillSGEffect(character.face_dir)
            game_world.add_object(skillsgeffect, 3)

            sg_skill_voice_list = Character.voices['SG_Skill_Voice']
            random.choice(sg_skill_voice_list).play()
        elif right_down(e):
            right_pressed = True
            character.face_dir = 1
        elif right_up(e):
            right_pressed = False
        elif left_down(e):
            left_pressed = True
            character.face_dir = -1
        elif left_up(e):
            left_pressed = False
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
            if Climb and not down_pressed:
                Move = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
            if Climb and not up_pressed:
                Move = False
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False
        elif jump(e) and not Jump and not Fall and not Climb:
            Jump = True
            Character.jump_sound.play()
        elif take_hit(e):
            Character.hp = max(0, Character.hp - Character.damage)
            Character.hit_delay = 1
            if Character.hp == 0:
                Character.hour_of_judgment_cooldown = 8
                character.state_machine.add_event(('DIE', 0))

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Move, Attack
        if 0.3 > get_time() - character.wait_time > 0.2:
            if not Attack:
                Attack = True
                character.attack_time = get_time()

                skillstunsg = SkillstunSG(character.face_dir)
                game_world.add_object(skillstunsg, 3)
                game_world.add_collision_pairs(f'skillstunsg:monster', skillstunsg, None)

                skillsg = SkillSG(character.face_dir)
                game_world.add_object(skillsg, 3)
                game_world.add_collision_pairs(f'skillsg:monster', skillsg, None)

        if Attack:
            character.frame = (character.frame + 15.0 * 0.8 * game_framework.frame_time) % 15

        elif not Attack and get_time() - character.wait_time > 0.3:
            Character.state = 0
            character.frame = 0
            if God:
                Character.hour_of_judgment_cooldown = 1
            else:
                Character.hour_of_judgment_cooldown = 8
            if right_pressed or left_pressed:
                character.state_machine.add_event(('WALK', 0))
            else:
                character.state_machine.add_event(('IDLE', 0))

        if Climb:
            if up_pressed and not down_pressed:
                if not Move:
                    Move = True
                character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return
            elif down_pressed and not up_pressed:
                if not Move:
                    Move = True
                character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            character.images['Attack_SG'][int(character.frame)].composite_draw(0, '', character.sx, character.y,
                                                                          170, 170)
        elif character.face_dir == -1:
            character.images['Attack_SG'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y,
                                                                          170, 170)

class USG:
    @staticmethod
    def enter(character, e):
        global right_pressed, left_pressed, attacking, down_pressed, up_pressed, Move, Jump, chance
        if sg_ult(e):
            Move = False
            chance = 0
            character.frame = 0
            character.name = 'Ultimate_SG'
            sg_ult_voice_list = Character.voices['SG_ULT_Voice']
            random.choice(sg_ult_voice_list).play()
        elif right_down(e):
            right_pressed = True
        elif right_up(e):
            right_pressed = False
        elif left_down(e):
            left_pressed = True
        elif left_up(e):
            left_pressed = False
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
            if Climb and not down_pressed:
                Move = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
            if Climb and not up_pressed:
                Move = False
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Invincibility, Fall, chance
        if character.name == 'Ultimate_SG':
            character.frame = character.frame + 19.0 * 0.8 * game_framework.frame_time

            if character.frame > 19.0:
                character.name = 'Ultimate_wait_SG'
                character.frame = -3
                character.wait_time = get_time()

                ultsgeffect = ULTSGEffect(character.face_dir)
                game_world.add_object(ultsgeffect, 0)

        if character.name == 'Ultimate_wait_SG':
            character.frame = (character.frame + 14.0 * 1.0 * game_framework.frame_time) % 14

            if get_time() - character.wait_time > 2.0:
                Invincibility = False
                character.frame = 0
                Character.state = 0
                chance = 0
                Fall = True

                if God:
                    Character.last_request_cooldown = 1
                else:
                    Character.last_request_cooldown = 40
                if right_pressed and not left_pressed:
                    character.face_dir = 1
                    character.face_dir = 1
                    character.state_machine.add_event(('WALK', 0))
                elif left_pressed and not right_pressed:
                    character.face_dir = -1
                    character.face_dir = -1
                    character.state_machine.add_event(('WALK', 0))
                elif right_pressed and left_pressed:
                    character.face_dir = character.face_dir
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y,
                                                                          170, 170)
        elif character.face_dir == -1:
            character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y,
                                                                          170, 170)

class RRF:
    @staticmethod
    def enter(character, e):
        global right_pressed, left_pressed, attacking, Reload_RF, rrf, down_pressed, up_pressed, Move, reload_dir
        if rf_reload(e) and not Reload_RF:
            Reload_RF = True
            character.wait_time = get_time()
            rrf = False
            character.name = 'Attack_RF'
            character.frame = 0
            reload_dir = character.face_dir
        elif right_down(e):
            right_pressed = True
            character.face_dir = 1
        elif right_up(e):
            right_pressed = False
        elif left_down(e):
            left_pressed = True
            character.face_dir = -1
        elif left_up(e):
            left_pressed = False
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
            if Climb and not down_pressed:
                Move = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
            if Climb and not up_pressed:
                Move = False
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False

    @staticmethod
    def exit(character, e):
        global Fall, Reload_RF, Climb
        if time_out(e):
            Fall = True
            Climb = False
            Reload_RF = False
            Character.bullet_RF = 4
            Character.hit_delay = 0.5
            if right_pressed or left_pressed:
                character.state_machine.add_event(('WALK', 0))

    @staticmethod
    def do(character):
        global Jump, jump_velocity, Fall, fall_velocity, Reload_RF, rrf

        if get_time() - character.wait_time > 0.4:
            character.state_machine.add_event(('TIME_OUT', 0))

        elif get_time() - character.wait_time > 0.35:
            character.name = 'Walk_RF'

        elif get_time() - character.wait_time > 0.25:
            character.frame = 0

        if get_time() - character.wait_time > 0.15:
            if not rrf:
                Jump = True
                jump_velocity = 4.5
                Fall = False
                character._reset_jump_after_ground()
                fall_velocity = 0.0
                rrf = True
                character.frame = 1
                reloadrf = ReloadRF(character.face_dir)
                game_world.add_object(reloadrf, 3)
                game_world.add_collision_pairs(f'reloadrf:monster', reloadrf, None)
                rf_reload_voice_list = Character.voices['RF_Reload_Voice']
                random.choice(rf_reload_voice_list).play()
            character.x -= 8 * reload_dir * RUN_SPEED_PPS * game_framework.frame_time

        for block in game_world.collision_pairs['server.character:ground'][1] + game_world.collision_pairs['server.character:wall'][1]:
            if screen_left - 20 <= block.x <= screen_right + 20:
                if game_world.collide(character, block):
                    character.x += 8 * reload_dir * RUN_SPEED_PPS * game_framework.frame_time
                    Fall = True
                    return

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
        elif character.face_dir == -1:
            character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

class RsRF:
    @staticmethod
    def enter(character, e):
        global right_pressed, left_pressed, attacking, Reload_RF, rrf, down_pressed, up_pressed, Move
        if rf_reload_s(e) and not Reload_RF:
            Reload_RF = True
            character.wait_time = get_time()
            rrf = False
            character.name = 'Attack_RF'
            character.frame = 0
        elif right_down(e):
            right_pressed = True
            character.face_dir = 1
        elif right_up(e):
            right_pressed = False
        elif left_down(e):
            left_pressed = True
            character.face_dir = -1
        elif left_up(e):
            left_pressed = False
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
            if Climb and not down_pressed:
                Move = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
            if Climb and not up_pressed:
                Move = False
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False

    @staticmethod
    def exit(character, e):
        global Fall, Reload_RF, Climb
        if time_out(e):
            Fall = True
            Reload_RF = False
            Climb = False
            Character.bullet_RF = 4
            Character.hit_delay = 0.5
            if right_pressed or left_pressed:
                character.state_machine.add_event(('WALK', 0))

    @staticmethod
    def do(character):
        global Jump, jump_velocity, Fall, fall_velocity, Reload_RF, rrf

        if get_time() - character.wait_time > 0.4:
            character.state_machine.add_event(('TIME_OUT', 0))

        elif get_time() - character.wait_time > 0.35:
            character.name = 'Walk_RF'

        elif get_time() - character.wait_time > 0.25:
            character.frame = 0

        elif get_time() - character.wait_time > 0.15:
            if not rrf:
                Jump = True
                jump_velocity = 4.5
                Fall = False
                character._reset_jump_after_ground()
                fall_velocity = 0.0
                rrf = True
                character.frame = 1
                reloadrf = ReloadRF(character.face_dir)
                game_world.add_object(reloadrf, 3)
                rf_reload_voice_list = Character.voices['RF_Reload_Voice']
                random.choice(rf_reload_voice_list).play()
                game_world.add_collision_pairs(f'reloadrf:monster', reloadrf, None)

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
        elif character.face_dir == -1:
            character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

class RcRF:
    @staticmethod
    def enter(character, e):
        global right_pressed, left_pressed, attacking, down_pressed, up_pressed, Move
        if rf_rc(e):
            Move = False
            character.wait_time = get_time()
            Character.target_down_bullet = Character.target_down_max
            character.frame = clamp(0, character.frame, 13)
            Character.Unique_RF_sound.play()
            rf_rc_voice_list = Character.voices['RF_Unique_Voice']
            random.choice(rf_rc_voice_list).play()
            Character.target_down_x = character.x + 78 * character.face_dir
            Character.target_down_y = character.y - 11
        elif right_down(e):
            right_pressed = True
        elif right_up(e):
            right_pressed = False
        elif left_down(e):
            left_pressed = True
        elif left_up(e):
            left_pressed = False
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
            if Climb and not down_pressed:
                Move = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
            if Climb and not up_pressed:
                Move = False
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False
            if Character.target_down_bullet < 1:
                if God:
                    Character.target_down_cooldown = 1
                else:
                    Character.target_down_cooldown = 45
                Character.target_down_size = 0
                Character.target_down_x = character.x + 78 * character.face_dir
                Character.target_down_y = character.y - 11

        elif take_hit(e):
            Character.hp = max(0, Character.hp - Character.damage)
            Character.hit_delay = 1
            if Character.hp == 0:
                Character.target_down_cooldown = 45
                Character.target_down_size = 0
                character.state_machine.add_event(('DIE', 0))
                Character.target_down_x = character.x + 78 * character.face_dir
                Character.target_down_y = character.y - 11

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Move
        if character.x > 5600:
            scroll_offset = 5600 - 1600 // 2
            Character.target_down_sx = Character.target_down_x - scroll_offset
        elif character.x > 800 and server.background.w > 1600:
            scroll_offset = character.x - 1600 // 2
            Character.target_down_sx = Character.target_down_x - scroll_offset
        else:
            Character.target_down_sx = Character.target_down_x

        if get_time() - character.wait_time > 0.025 and Character.target_down_size <= 40:
            Character.target_down_size += 5
            character.wait_time = get_time()

        if Attack:
            character.frame = (character.frame + 7.0 * 2.0 * game_framework.frame_time) % 7
            if Character.target_down_bullet == 0:
                if God:
                    Character.target_down_cooldown = 1
                else:
                    Character.target_down_cooldown = 45
                Character.target_down_size = 0
                Character.state = 0
                character.frame = 0
                if right_pressed or left_pressed:
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))
        else:
            character.frame = (character.frame + 14.0 * 1.5 * game_framework.frame_time) % 14
            if right_pressed and not left_pressed:
                Character.target_down_x += Character.speed * RUN_SPEED_PPS * game_framework.frame_time
            elif left_pressed and not right_pressed:
                Character.target_down_x -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time
            if up_pressed and not down_pressed:
                Character.target_down_y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time
            elif down_pressed and not up_pressed:
                Character.target_down_y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time

        if Fall or Jump:
            if Move:
                Move = False

        if Climb:
            if up_pressed and not down_pressed:
                if not Move:
                    Move = True
                character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return
            elif down_pressed and not up_pressed:
                if not Move:
                    Move = True
                character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return

    @staticmethod
    def draw(character):
        if Attack:
            if character.face_dir == 1:
                character.images['Attack_RF'][int(character.frame)].composite_draw(0, '', character.sx, character.y,
                                                                                   170, 170)
            elif character.face_dir == -1:
                character.images['Attack_RF'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y,
                                                                                   170, 170)
        else:
            if character.face_dir == 1:
                character.images['Attack_RF'][0].composite_draw(0, '', character.sx, character.y,
                                                                                   170, 170)
            elif character.face_dir == -1:
                character.images['Attack_RF'][0].composite_draw(0, 'h', character.sx, character.y,
                                                                                   170, 170)

class SRF:
    @staticmethod
    def enter(character, e):
        global right_pressed, left_pressed, attacking, down_pressed, up_pressed, Move, Jump
        if rf_skill(e):
            Move = False
            character.frame = 0
            character.wait_time = get_time()
            character.face_dir = character.face_dir
            rf_q_voice_list = Character.voices['RF_Skill_Voice']
            random.choice(rf_q_voice_list).play()
        elif right_down(e):
            right_pressed = True
            character.face_dir = 1
            character.face_dir = 1
        elif right_up(e):
            right_pressed = False
        elif left_down(e):
            left_pressed = True
            character.face_dir = -1
            character.face_dir = -1
        elif left_up(e):
            left_pressed = False
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
            if Climb and not down_pressed:
                Move = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
            if Climb and not up_pressed:
                Move = False
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False
        elif take_hit(e):
            Character.hp = max(0, Character.hp - Character.damage)
            Character.hit_delay = 1
            if Character.hp == 0:
                Character.perfect_shot_cooldown = 15
                character.state_machine.add_event(('DIE', 0))

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Move, Attack
        if 1.1 > get_time() - character.wait_time > 1.0:
            if not Attack:
                Attack = True
                character.attack_time = get_time()

                skillrfeffect = SkillRFEffect(character.face_dir)
                game_world.add_object(skillrfeffect, 3)

                skillrf = SkillRF(character.face_dir)
                game_world.add_object(skillrf, 3)
                game_world.add_collision_pairs(f'skillrf:monster', skillrf, None)

                rfeffect = RFEffect(character.face_dir)
                game_world.add_object(rfeffect, 3)

        if Attack:
            character.frame = (character.frame + 7.0 * 2.0 * game_framework.frame_time) % 7

        elif not Attack and get_time() - character.wait_time > 1.1:
            Character.state = 0
            character.frame = 0
            if God:
                Character.perfect_shot_cooldown = 1
            else:
                Character.perfect_shot_cooldown = 15
            if right_pressed or left_pressed:
                character.state_machine.add_event(('WALK', 0))
            else:
                character.state_machine.add_event(('IDLE', 0))

        if Climb:
            if up_pressed and not down_pressed:
                if not Move:
                    Move = True
                character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return
            elif down_pressed and not up_pressed:
                if not Move:
                    Move = True
                character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            character.images['Attack_RF'][int(character.frame)].composite_draw(0, '', character.sx, character.y,
                                                                               170, 170)
        elif character.face_dir == -1:
            character.images['Attack_RF'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y,
                                                                               170, 170)

class URF:
    @staticmethod
    def enter(character, e):
        global right_pressed, left_pressed, attacking, down_pressed, up_pressed, Move, Jump
        if rf_ult(e):
            Move = False
            character.frame = 0
            character.wait_time = get_time()
            Character.ULT_RF_start_sound.play()
            rf_c_voice_list = Character.voices['RF_ULT_Voice']
            random.choice(rf_c_voice_list).play()
        elif right_down(e):
            right_pressed = True
        elif right_up(e):
            right_pressed = False
        elif left_down(e):
            left_pressed = True
        elif left_up(e):
            left_pressed = False
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
            if Climb and not down_pressed:
                Move = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
            if Climb and not up_pressed:
                Move = False
        elif a_up(e):
            attacking = False

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Invincibility, catastrophe
        character.frame = character.frame + 27.0 * 0.5 * game_framework.frame_time

        if character.frame > 27.0:
            Invincibility = False
            catastrophe = True
            character.frame = 0
            Character.catastrophe_duration = 10
            Character.speed = 6

            ultrf = ULTRF()
            game_world.add_object(ultrf, 3)

            if right_pressed and not left_pressed:
                character.face_dir = 1
                character.face_dir = 1
                character.state_machine.add_event(('WALK', 0))
            elif left_pressed and not right_pressed:
                character.face_dir = -1
                character.face_dir = -1
                character.state_machine.add_event(('WALK', 0))
            elif right_pressed and left_pressed:
                character.face_dir = character.face_dir
                character.state_machine.add_event(('WALK', 0))
            else:
                character.state_machine.add_event(('IDLE', 0))

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            character.images['Ultimate_RF'][int(character.frame)].composite_draw(0, '', character.sx, character.y,
                                                                          170, 170)
        elif character.face_dir == -1:
            character.images['Ultimate_RF'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y,
                                                                          170, 170)

class RHG:
    @staticmethod
    def enter(character, e):
        global right_pressed, left_pressed, attacking, Reload_HG, down_pressed, up_pressed, Move
        if hg_reload(e) and not Reload_HG:
            Reload_HG = True
            character.name = 'Reload_HG'
            character.frame = 0
        elif right_down(e):
            right_pressed = True
            character.face_dir = 1
        elif right_up(e):
            right_pressed = False
        elif left_down(e):
            left_pressed = True
            character.face_dir = -1
        elif left_up(e):
            left_pressed = False
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
            if Climb and not down_pressed:
                Move = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
            if Climb and not up_pressed:
                Move = False
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False
        elif s_down(e):
            if character.state == 0:
                Character.state = 1
            elif character.state == 1:
                Character.state = 0
        elif reload(e):
            if not Reload_HG:
                character.state_machine.add_event(('HG_RELOAD_END', 0))

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Reload_HG, Invincibility

        if Reload_HG:
            character.frame = character.frame + 17.0 * 1.2 * game_framework.frame_time
            if character.frame > 17.0:
                Character.bullet_HG = Character.max_bullet_HG
                character.frame = 0
                Reload_HG = False
                character.wait_time = get_time()
                character.name = 'Reload_end_HG'

        elif not Reload_HG:
            if Attack:
                Invincibility = False
                if left_pressed or right_pressed or (Climb and (up_pressed or down_pressed)):
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('TIME_OUT', 0))

            character.frame = (character.frame + 14.0 * 1.2 * game_framework.frame_time) % 14

            if get_time() - character.wait_time > 1.0:
                Invincibility = False
                if left_pressed or right_pressed or (Climb and (up_pressed or down_pressed)):
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
        elif character.face_dir == -1:
            character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

class REHG:
    @staticmethod
    def enter(character, e):
        global right_pressed, left_pressed, attacking, Reload_HG, down_pressed, up_pressed, Jump, jump_velocity, Fall, fall_velocity, Climb, Move
        if hg_reload_end(e):
            character.frame = 0
            Jump = False
            jump_velocity = 9.0
            Fall = False
            character._reset_jump_after_ground()
            fall_velocity = 0.0
            Climb = False
            character.wait_time = get_time()
        elif right_down(e):
            right_pressed = True
            character.face_dir = 1
        elif right_up(e):
            right_pressed = False
        elif left_down(e):
            left_pressed = True
            character.face_dir = -1
        elif left_up(e):
            left_pressed = False
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
            if Climb and not down_pressed:
                Move = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
            if Climb and not up_pressed:
                Move = False
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False
        elif s_down(e):
            if character.state == 0:
                Character.state = 1
            elif character.state == 1:
                Character.state = 0

    @staticmethod
    def exit(character, e):
        global Invincibility
        if time_out(e):
            Invincibility = False
            if right_pressed or left_pressed:
                character.state_machine.add_event(('WALK', 0))

    @staticmethod
    def do(character):
        global Fall, Climb, Invincibility
        character.x += 20 * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time

        for block in game_world.collision_pairs['server.character:ground'][1] + game_world.collision_pairs['server.character:wall'][1]:
            if screen_left - 20 <= block.x <= screen_right + 20:
                if game_world.collide(character, block):
                    character.x -= 20 * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time
                    Fall = True
                    Climb = False
                    character.state_machine.add_event(('TIME_OUT', 0))
                    return

        if get_time() - character.wait_time > 0.15:
            Fall = True
            Climb = False
            Invincibility = False
            character.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            character.images['Reload_HG'][16].composite_draw(0, '', character.sx, character.y, 170, 170)
        elif character.face_dir == -1:
            character.images['Reload_HG'][16].composite_draw(0, 'h', character.sx, character.y, 170, 170)

class UHG:
    trails = []

    @staticmethod
    def enter(character, e):
        global right_pressed, left_pressed, attacking, down_pressed, up_pressed, Move, Jump, count
        if hg_ult(e):
            Move = False
            count = 0
            character.frame = 0
            UHG.trails.clear()
            hg_c_voice_list = Character.voices['HG_ULT_Voice']
            random.choice(hg_c_voice_list).play()
            Character.ULT_HG_sound.play()
            character.wait_time = get_time()
            character.trail_time = get_time()
            character.effect_time = get_time()

            ulthg = ULTHG()
            game_world.add_object(ulthg, 3)
            game_world.add_collision_pairs(f'ulthg:monster', ulthg, None)
        elif right_down(e):
            right_pressed = True
            character.face_dir = 1
        elif right_up(e):
            right_pressed = False
            if left_pressed:
                character.face_dir = -1
        elif left_down(e):
            left_pressed = True
            character.face_dir = -1
        elif left_up(e):
            left_pressed = False
            if right_pressed:
                character.face_dir = 1
        elif on_down(e):
            up_pressed = True
        elif on_up(e):
            up_pressed = False
            if Climb and not down_pressed:
                Move = False
        elif under_down(e):
            down_pressed = True
        elif under_up(e):
            down_pressed = False
            if Climb and not up_pressed:
                Move = False
        elif a_down(e):
            attacking = True
        elif a_up(e):
            attacking = False
        elif s_down(e):
            if character.state == 0:
                Character.state = 1
            elif character.state == 1:
                Character.state = 0
        elif jump(e) and not Jump and not Fall and not Climb:
            Jump = True
            Character.jump_sound.play()
        elif skill(e):
            if Character.at02_grenade_cooldown == 0 and Character.bullet_HG > 0 and (God or Character.upgrade >= 1):
                Character.bullet_HG -= 1

                if God:
                    Character.at02_grenade_cooldown = 1
                else:
                    Character.at02_grenade_cooldown = 4

    @staticmethod
    def exit(character, e):
        if time_out(e):
            if right_pressed or left_pressed:
                character.state_machine.add_event(('WALK', 0))

    @staticmethod
    def do(character):
        global Invincibility, Fall, random_angle, Climb, count
        if get_time() - character.wait_time > 2.5:
            Fall = True
            Invincibility = False
            Character.state = 0
            Character.frame = 0
            Character.hit_delay = 1
            Character.bullet_HG = Character.max_bullet_HG
            if God:
                Character.equilibrium_cooldown = 1
            else:
                Character.equilibrium_cooldown = 8
            character.state_machine.add_event(('TIME_OUT', 0))

        elif get_time() - character.wait_time > 2.0 and count == 1:
            ulthg = ULTHG()
            game_world.add_object(ulthg, 3)
            game_world.add_collision_pairs(f'ulthg:monster', ulthg, None)
            count += 1

        elif get_time() - character.wait_time > 1.0 and count == 0:
            ulthg = ULTHG()
            game_world.add_object(ulthg, 3)
            game_world.add_collision_pairs(f'ulthg:monster', ulthg, None)
            count += 1

        character.frame = (character.frame + 12.0 * 2.0 * game_framework.frame_time) % 12

        if get_time() - character.trail_time > 0.05:
            UHG.add_trail(character)
            character.trail_time = get_time()

        if get_time() - character.effect_time > 0.1:
            random_angle = random.uniform(-3.141592, 3.141592)
            character.effect_time = get_time()

            for _ in range(4):
                ulthgeffect = ULTHGEffect()
                game_world.add_object(ulthgeffect, 3)

        if Climb:
            if up_pressed and not down_pressed:
                character.y += 2 * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y -= 2 * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return
            elif down_pressed and not up_pressed:
                character.y -= 2 * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 20 <= block.x <= screen_right + 20:
                        if game_world.collide(character, block):
                            character.y += 2 * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return

        character.x += 2 * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time

        for block in game_world.collision_pairs['server.character:ground'][1] + \
                     game_world.collision_pairs['server.character:wall'][1]:
            if screen_left - 20 <= block.x <= screen_right + 20:
                if game_world.collide(character, block):
                    character.x -= 2 * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time
                    return

        ground_objects = game_world.collision_pairs['server.character:ground'][1]
        for block in ground_objects:
            if screen_left - 20 <= block.x <= screen_right + 20:
                if game_world.collide_ad(character, block, ground_objects):
                    Fall = True
                    return

        for block in game_world.collision_pairs['server.character:ladder'][1]:
            if screen_left - 20 <= block.x <= screen_right + 20:
                if game_world.collide_ladder(character, block):
                    Fall = True
                    Climb = False
                    return

    @staticmethod
    def draw(character):
        screen_left = server.background.window_left

        for trail in UHG.trails:
            trail_x = trail['x'] - screen_left

            if trail['face_dir'] == 1:
                character.images['Ultimate_HG'][int(trail['frame'])].composite_draw(random_angle / 6, '', trail_x,
                                                                                    trail['y'], 170, 170)
            elif trail['face_dir'] == -1:
                character.images['Ultimate_HG'][int(trail['frame'])].composite_draw(random_angle / 6, 'h', trail_x,
                                                                                    trail['y'], 170, 170)
        if character.face_dir == 1:
            character.images['Ultimate_HG'][int(character.frame)].composite_draw(random_angle / 6, '', character.sx,
                                                                                 character.y, 170, 170)
        elif character.face_dir == -1:
            character.images['Ultimate_HG'][int(character.frame)].composite_draw(random_angle / 6, 'h', character.sx,
                                                                                 character.y, 170, 170)

    @staticmethod
    def add_trail(character):
        UHG.trails.append({
            'x': character.x,
            'y': character.y,
            'frame': character.frame,
            'face_dir': character.face_dir,
            'time': get_time()
        })
        if len(UHG.trails) > 2:
            UHG.trails.pop(0)

animation_names = ['Idle_SG', 'Walk_SG', 'Hit_SG', 'Die_SG', 'Attack_SG', 'Reload_SG', 'Unique_SG', 'Ultimate_SG', 'Ultimate_wait_SG',
                   'Idle_RF', 'Walk_RF', 'Hit_RF', 'Die_RF', 'Attack_RF', 'Ultimate_RF',
                   'Idle_HG', 'Walk_HG', 'Hit_HG', 'Die_HG', 'Attack_HG', 'Reload_HG', 'Reload_end_HG', 'Ultimate_HG']

character_voices = ['SG_Hit_Voice', 'SG_Die_Voice', 'SG_Attack_Voice', 'SG_Reload_Voice', 'SG_Unique_Voice', 'SG_Skill_Voice', 'SG_ULT_Voice', 'SG_Portal_Voice',
                    'RF_Hit_Voice', 'RF_Die_Voice', 'RF_Attack_Voice', 'RF_Reload_Voice', 'RF_Unique_Voice', 'RF_Skill_Voice', 'RF_ULT_Voice', 'RF_Portal_Voice',
                    'HG_Hit_Voice', 'HG_Die_Voice', 'HG_Attack_Voice', 'HG_Reload_Voice', 'HG_Q_Voice', 'HG_ULT_Voice', 'HG_Portal_Voice']

class Character:
    images = None
    voices = None
    jump_sound = None
    fall_sound = None
    portal_sound = None
    sg_stance_sound = None
    rf_stance_sound = None
    hg_stance_sound = None
    Unique_SG_sound = None
    Unique_SG_counter_sound = None
    Unique_RF_sound = None
    Reload_SG_sound = None
    Reload_HG_sound = None
    ULT_RF_start_sound = None
    ULT_HG_sound = None
    stance = 0
    state = 0
    speed = 3
    hp = 20
    max_hp = 20 # 최대 hp 30
    damage = 0
    upgrade = 0
    medal = 0
    bullet_SG = 12
    bullet_RF = 4
    target_down_max = 2 # 타겟 다운 총알 2 / 3 (+1)
    target_down_bullet = target_down_max
    target_down_size = 0 # 타겟 다운 범위 3 / 4 (+3)
    target_down_x = 0
    target_down_y = 0
    target_down_sx = 0
    max_bullet_HG = 20 # 핸드건 총알 개수 20 / 24 (+1) / 30 (+3)
    bullet_HG = max_bullet_HG
    damage_SG = 1
    stun_SG = 2
    damage_RF = 4
    stun_RF = 1
    damage_HG = 1
    shield_def = 1 # 방어 태세 방어도 1 / 2 (+1) / 4 (+3) / 8 (+5)
    hit_delay = 0 # 피격 면역
    attack_delay = 0 # 공격 속도
    hour_of_judgment_cooldown = 0 # 심판의 시간 쿨타임 8초
    last_request_cooldown = 0 # 최후의 만찬 쿨타임 40초
    target_down_cooldown = 0  # 타겟 다운 쿨타임 45초
    perfect_shot_cooldown = 0 # 퍼펙트 샷 쿨타임 15초
    catastrophe_cooldown = 0 # 대재앙 쿨타임 120초
    catastrophe_duration = 0 # 대재앙 지속 시간 10초
    dexterous_shot_cooldown = 0 # 민첩한 사격 쿨타임 2초 / 1초 (+2)
    at02_grenade_cooldown = 0
    equilibrium_cooldown = 0 # 이퀄리브리엄 쿨타임 8초

    def load_images(self):
        if Character.images == None:
            Character.images = {}
            for name in animation_names:
                if name == 'Idle_SG':
                    Character.images[name] = [load_image("./HKCAWS/" + name + " (%d)" % i + ".png") for i in range(1, 14 + 1)]
                elif name == 'Walk_SG':
                    Character.images[name] = [load_image("./HKCAWS/" + name + " (%d)" % i + ".png") for i in range(1, 6 + 1)]
                elif name == 'Hit_SG':
                    Character.images[name] = [load_image("./HKCAWS/" + name + " (1)" + ".png")]
                elif name == 'Die_SG':
                    Character.images[name] = [load_image("./HKCAWS/" + name + " (%d)" % i + ".png") for i in range(1, 18 + 1)]
                elif name == 'Attack_SG':
                    Character.images[name] = [load_image("./HKCAWS/" + name + " (%d)" % i + ".png") for i in range(1, 15 + 1)]
                elif name == 'Reload_SG':
                    Character.images[name] = [load_image("./HKCAWS/" + name + " (%d)" % i + ".png") for i in range(1, 16 + 1)]
                elif name == 'Unique_SG':
                    Character.images[name] = [load_image("./HKCAWS/" + name + " (%d)" % i + ".png") for i in range(1, 14 + 1)]
                elif name == 'Ultimate_SG':
                    Character.images[name] = [load_image("./HKCAWS/" + name + " (%d)" % i + ".png") for i in range(1, 19 + 1)]
                elif name == 'Ultimate_wait_SG':
                    Character.images[name] = [load_image("./HKCAWS/" + name + " (%d)" % i + ".png") for i in range(1, 14 + 1)]

                elif name == 'Idle_RF':
                    Character.images[name] = [load_image("./R93/" + name + " (%d)" % i + ".png") for i in range(1, 14 + 1)]
                elif name == 'Walk_RF':
                    Character.images[name] = [load_image("./R93/" + name + " (%d)" % i + ".png") for i in range(1, 6 + 1)]
                elif name == 'Hit_RF':
                    Character.images[name] = [load_image("./R93/" + name + " (1)" + ".png")]
                elif name == 'Die_RF':
                    Character.images[name] = [load_image("./R93/" + name + " (%d)" % i + ".png") for i in range(1, 18 + 1)]
                elif name == 'Attack_RF':
                    Character.images[name] = [load_image("./R93/" + name + " (%d)" % i + ".png") for i in range(1, 7 + 1)]
                elif name == 'Ultimate_RF':
                    Character.images[name] = [load_image("./R93/" + name + " (%d)" % i + ".png") for i in range(1, 27 + 1)]

                elif name == 'Idle_HG':
                    Character.images[name] = [load_image("./NZ75/" + name + " (%d)" % i + ".png") for i in range(1, 14 + 1)]
                elif name == 'Walk_HG':
                    Character.images[name] = [load_image("./NZ75/" + name + " (%d)" % i + ".png") for i in range(1, 6 + 1)]
                elif name == 'Hit_HG':
                    Character.images[name] = [load_image("./NZ75/" + name + " (1)" + ".png")]
                elif name == 'Die_HG':
                    Character.images[name] = [load_image("./NZ75/" + name + " (%d)" % i + ".png") for i in range(1, 11 + 1)]
                elif name == 'Attack_HG':
                    Character.images[name] = [load_image("./NZ75/" + name + " (%d)" % i + ".png") for i in range(1, 4 + 1)]
                elif name == 'Reload_HG':
                    Character.images[name] = [load_image("./NZ75/" + name + " (%d)" % i + ".png") for i in range(1, 17 + 1)]
                elif name == 'Reload_end_HG':
                    Character.images[name] = [load_image("./NZ75/" + name + " (%d)" % i + ".png") for i in range(1, 14 + 1)]
                elif name == 'Ultimate_HG':
                    Character.images[name] = [load_image("./GSH18mod/" + name + " (%d)" % i + ".png") for i in range(1, 12 + 1)]

    def load_voices(self):
        if Character.voices == None:
            Character.voices = {}
            for voice in character_voices:
                Character.voices[voice] = []
                if voice == 'SG_Hit_Voice':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_Die_Voice':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(48)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_Attack_Voice':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_Reload_Voice':
                    sound = load_wav("./Voice/SG/" + voice + " (1)" + ".mp3")
                    sound.set_volume(24)
                    Character.voices[voice].append(sound)
                elif voice == 'SG_Unique_Voice':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_Skill_Voice':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_ULT_Voice':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_Portal_Voice':
                    sound = load_wav("./Voice/SG/" + voice + " (1)" + ".mp3")
                    sound.set_volume(24)
                    Character.voices[voice].append(sound)

                elif voice == 'RF_Hit_Voice':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(18)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Die_Voice':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(36)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Attack_Voice':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(18)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Reload_Voice':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Unique_Voice':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Skill_Voice':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_ULT_Voice':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Portal_Voice':
                    sound = load_wav("./Voice/RF/" + voice + " (1)" + ".mp3")
                    sound.set_volume(24)
                    Character.voices[voice].append(sound)

                elif voice == 'HG_Hit_Voice':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/HG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'HG_Die_Voice':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/HG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(48)
                        Character.voices[voice].append(sound)
                elif voice == 'HG_Attack_Voice':
                    for i in range(1, 5 + 1):
                        sound = load_wav("./Voice/HG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'HG_Reload_Voice':
                    sound = load_wav("./Voice/HG/" + voice + " (1)" + ".mp3")
                    sound.set_volume(24)
                    Character.voices[voice].append(sound)
                elif voice == 'HG_Q_Voice':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/HG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'HG_ULT_Voice':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/HG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'HG_Portal_Voice':
                    sound = load_wav("./Voice/HG/" + voice + " (1)" + ".mp3")
                    sound.set_volume(24)
                    Character.voices[voice].append(sound)

    def __init__(self):
        self.x, self.y = 34.0, 170.0
        self.face_dir = 1
        self.frame = 0
        self.sx = 0
        self.JUMP_BUFFER = 0.12
        self.COYOTE_TIME = 0.10
        self.jump_buffer_timer = 0.0
        self.coyote_timer = 0.0
        self.jump_consumed = False
        self.grounded = True
        self.load_images()
        self.load_voices()
        self.name = ''
        self.one = 0
        self.hit_cool = 0
        self.attack_cool = 0
        self.attack_time = 0
        self.double_time = 0
        self.doubleattack = 0
        self.catastrophe_time = 0
        self.Skill_SG_cool = 0
        self.ULT_SG_cool = 0
        self.Unique_RF_cool = 0
        self.Skill_RF_cool = 0
        self.ULT_RF_cool = 0
        self.ULT_HG_cool = 0
        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Idle: {
                    right_down: Walk, left_down: Walk, left_up: Idle, right_up: Idle, change_stance_z: Idle, change_stance_x: Idle,
                    walk: Walk, jump: Idle, s_down: Idle, a_down: Idle, a_up: Idle,
                    reload: Idle, rf_reload: RRF, idle: Idle, under_down: Idle, under_up: Idle, rf_reload_s: RsRF, rf_rc: RcRF,
                    on_up: Idle, on_down: Idle, skill: Idle, ultimate: Idle, sg_ult: USG, hg_reload: RHG,
                    take_hit: Hit, die: Die, sg_skill: SSG, rf_skill: SRF, rf_ult: URF, hg_ult: UHG,
                    temp_bullet: Idle, temp_god: Idle, temp_up: Idle, temp_down: Idle, temp_medal: Idle, temp_die: Idle,
                },
                Walk: {
                    right_down: Walk, left_down: Walk, right_up: Walk, left_up: Walk, change_stance_z: Walk, change_stance_x: Walk,
                    idle: Idle, jump: Walk, s_down: Walk, a_down: Walk, a_up: Walk,
                    reload: Walk, rf_reload: RRF, walk: Walk, under_down: Walk, under_up: Walk, rf_reload_s: RsRF, rf_rc: RcRF,
                    on_up: Walk, on_down: Walk, skill: Walk, ultimate: Walk, sg_ult: USG, hg_reload: RHG,
                    take_hit: Hit, die: Die, sg_skill: SSG, rf_skill: SRF, rf_ult: URF, hg_ult: UHG,
                    temp_bullet: Walk, temp_god: Walk, temp_up: Walk, temp_down: Walk, temp_medal: Walk, temp_die: Walk,
                },
                Hit: {
                    right_down: Hit, left_down: Hit, right_up: Hit, left_up: Hit, on_down: Hit, under_down: Hit, under_up: Hit,
                    s_down: Hit, a_down: Hit, a_up: Hit,
                    time_out: Idle, walk: Walk, die: Die
                },
                Die: {
                    time_out: Idle
                },
                SSG: {
                    right_down: SSG, left_down: SSG, left_up: SSG, right_up: SSG, on_up: SSG, under_up: SSG,
                    a_down: SSG, a_up: SSG, jump: SSG,
                    under_down: SSG, on_down: SSG, idle: Idle, walk: Walk, take_hit: SSG,
                    die: Die,
                },
                USG: {
                    right_down: USG, left_down: USG, left_up: USG, right_up: USG, on_up: USG, under_up: USG,
                    a_down: USG, a_up: USG,
                    under_down: USG, on_down: USG, idle: Idle, walk: Walk,
                },
                RRF: {
                    right_down: RRF, left_down: RRF, left_up: RRF, right_up: RRF, on_up: RRF, under_up: RRF, a_up: RRF,
                    time_out: Idle, walk: Walk, under_down: RRF, on_down: RRF, a_down: RRF,
                },
                RsRF: {
                    right_down: RsRF, left_down: RsRF, left_up: RsRF, right_up: RsRF, on_up: RsRF, under_up: RsRF, a_up: RsRF,
                    time_out: Idle, walk: Walk, under_down: RsRF, on_down: RsRF, a_down: RsRF,
                },
                RcRF: {
                    right_down: RcRF, left_down: RcRF, left_up: RcRF, right_up: RcRF, on_up: RcRF, under_up: RcRF, a_down: RcRF, a_up: RcRF,
                    under_down: RcRF, on_down: RcRF, idle: Idle, walk: Walk, take_hit: RcRF, die: Die,
                },
                SRF: {
                    right_down: SRF, left_down: SRF, left_up: SRF, right_up: SRF, on_up: SRF, under_up: SRF, a_down: SRF, a_up: SRF,
                    under_down: SRF, on_down: SRF, idle: Idle, walk: Walk, take_hit: SRF, die: Die,
                },
                URF: {
                    right_down: URF, left_down: URF, left_up: URF, right_up: URF, on_up: URF, under_up: URF, a_down: URF, a_up: URF,
                    under_down: URF, on_down: URF, idle: Idle, walk: Walk,
                },
                RHG: {
                    right_down: RHG, left_down: RHG, left_up: RHG, right_up: RHG, on_up: RHG, under_up: RHG, a_up: RHG,
                    time_out: Idle, walk: Walk, hg_reload_end: REHG, under_down: RHG, on_down: RHG,
                    reload: RHG, a_down: RHG, s_down: RHG,
                },
                REHG: {
                    left_up: REHG, right_up: REHG, on_up: REHG, under_up: REHG, a_up: REHG,
                    time_out: Idle, walk: Walk, a_down: REHG, s_down: REHG,
                },
                UHG: {
                    right_down: UHG, left_down: UHG, left_up: UHG, right_up: UHG, on_up: UHG, under_up: UHG,
                    a_down: UHG, a_up: UHG, jump: UHG, time_out: Idle, skill: UHG, s_down: UHG,
                    under_down: UHG, on_down: UHG, idle: Idle, walk: Walk,
                },
            }
        )

        if Character.jump_sound == None:
            Character.jump_sound = load_wav("./Sound/Jump.mp3")
            Character.fall_sound = load_wav("./Sound/Fall.mp3")
            Character.portal_sound = load_wav("./Sound/Portal.mp3")
            Character.sg_stance_sound = load_wav("./Sound/change_SG.mp3")
            Character.rf_stance_sound = load_wav("./Sound/change_RF.mp3")
            Character.hg_stance_sound = load_wav("./Sound/change_HG.mp3")
            Character.Unique_SG_sound = load_wav("./Sound/Unique_SG.mp3")
            Character.Unique_SG_counter_sound = load_wav("./Sound/Unique_SG_counter.ogg")
            Character.Unique_RF_sound = load_wav("./Sound/Unique_RF.mp3")
            Character.Reload_SG_sound = load_wav("./Sound/Reload_SG.mp3")
            Character.Reload_HG_sound = load_wav("./Sound/Reload_HG.mp3")
            Character.ULT_RF_start_sound = load_wav("./Sound/ULT_RF_start.ogg")
            Character.ULT_HG_sound = load_wav("./Sound/ULT_HG.mp3")
            Character.jump_sound.set_volume(80)
            Character.fall_sound.set_volume(48)
            Character.portal_sound.set_volume(16)
            Character.sg_stance_sound.set_volume(64)
            Character.rf_stance_sound.set_volume(64)
            Character.hg_stance_sound.set_volume(64)
            Character.Unique_SG_sound.set_volume(32)
            Character.Unique_SG_counter_sound.set_volume(32)
            Character.Unique_RF_sound.set_volume(80)
            Character.Reload_SG_sound.set_volume(80)
            Character.Reload_HG_sound.set_volume(80)
            Character.ULT_RF_start_sound.set_volume(32)
            Character.ULT_HG_sound.set_volume(32)

    def _reset_jump_after_ground(self):
        self.grounded = True
        self.jump_consumed = False
        self.coyote_timer = self.COYOTE_TIME

    def update(self):
        global Jump, jump_velocity, Fall, fall_velocity, Attack, Move, screen_left, screen_right, Reload_SG, Reload_HG, catastrophe
        self.state_machine.update()
        self.x = clamp(17.0, self.x, server.background.w - 17.0)
        self.sx = self.x - server.background.window_left
        screen_left = server.background.window_left
        screen_right = server.background.window_left + 1600

        dt = game_framework.frame_time

        self.coyote_timer = max(0.0, self.coyote_timer - dt)
        self.jump_buffer_timer = max(0.0, self.jump_buffer_timer - dt)

        if (self.jump_buffer_timer > 0.0
                and (self.grounded or self.coyote_timer > 0.0)
                and not Jump and not Fall
                and not self.jump_consumed) and not Climb and not Character.state == -1:
            Jump = True
            Fall = False
            self._reset_jump_after_ground()
            if not Move:
                Move = True
            jump_velocity = 9.0  # 기존 값 유지
            self.jump_buffer_timer = 0.0
            self.coyote_timer = 0.0
            self.jump_consumed = True
            self.grounded = False

        if Jump:
            if not Move:
                Move = True
            self.y += jump_velocity * RUN_SPEED_PPS * game_framework.frame_time
            jump_velocity -= gravity * RUN_SPEED_PPS * game_framework.frame_time
            if jump_velocity <= 0:
                Jump = False
                Fall = True
                self.grounded = False
                jump_velocity = 9.0

        if Fall:
            self.y -= fall_velocity * RUN_SPEED_PPS * game_framework.frame_time
            fall_velocity += gravity * RUN_SPEED_PPS * game_framework.frame_time
            if Character.state == 3 or God:
                if self.y < 50.0:
                    self.y = 51.0
                    Move = False
                    Fall = False
                    self._reset_jump_after_ground()
                    fall_velocity = 0.0
                    self.grounded = True
                    self.jump_consumed = False
                    if self.jump_buffer_timer > 0.0:
                        Jump = True
                        Fall = False
                        self._reset_jump_after_ground()
                        if not Move:
                            Move = True
                        jump_velocity = 9.0
                        self.jump_buffer_timer = 0.0
                        self.coyote_timer = 0.0
                        self.jump_consumed = True

            if self.y < -68:
                Move = False
                Fall = False
                fall_velocity = 0.0
                self.grounded = False
                self._reset_jump_after_ground()
                self.state_machine.add_event(('DIE', 0))

        if attacking and not Attack:
            if Character.attack_delay == 0:
                if Character.stance == 0 and Character.bullet_SG > 0 and (Character.state == 0 or Character.state == 1):

                    if self.attack_time == 0:
                        self.attack_time = get_time()
                        self.frame = 0
                        Character.bullet_SG -= 1

                        normalsgeffect = NormalSGEffect(self.face_dir)
                        game_world.add_object(normalsgeffect, 3)

                        normalsg1 = NormalSG1(self.face_dir)
                        game_world.add_object(normalsg1, 3)
                        game_world.add_collision_pairs('normalsg1:monster', normalsg1, None)

                        normalsg2 = NormalSG2(self.face_dir)
                        game_world.add_object(normalsg2, 3)
                        game_world.add_collision_pairs('normalsg2:monster', normalsg2, None)

                        normalsg3 = NormalSG3(self.face_dir)
                        game_world.add_object(normalsg3, 3)
                        game_world.add_collision_pairs('normalsg3:monster', normalsg3, None)

                        if random.random() < 0.25:
                            sg_attack_voice_list = Character.voices['SG_Attack_Voice']
                            random.choice(sg_attack_voice_list).play()

                        Attack = True
                elif Character.stance == 1:
                    if Character.state == 0 and Character.bullet_RF > 0 and not Move:
                        if self.attack_time == 0:
                            self.attack_time = get_time()
                            self.frame = 0
                            Character.bullet_RF -= 1

                            if Character.bullet_RF > 0:
                                normalrf = NormalRF(self.face_dir)
                                game_world.add_object(normalrf, 3)
                                game_world.add_collision_pairs(f'normalrf:monster', normalrf, None)
                            else:
                                normalrfsp = NormalRFSP(self.face_dir)
                                game_world.add_object(normalrfsp, 3)
                                game_world.add_collision_pairs(f'normalrfsp:monster', normalrfsp, None)

                            rfeffect = RFEffect(self.face_dir)
                            game_world.add_object(rfeffect, 3)

                            if random.random() < 0.25:
                                rf_attack_voice_list = Character.voices['RF_Attack_Voice']
                                random.choice(rf_attack_voice_list).play()

                            Attack = True
                    elif Character.state == 1 and Character.target_down_bullet > 0 and not Move:
                        if self.attack_time == 0:
                            self.attack_time = get_time()
                            self.frame = 0
                            Character.target_down_bullet -= 1

                            uniquerfeffect = UniqueRFEffect()
                            game_world.add_object(uniquerfeffect, 3)

                            uniquerf = UniqueRF()
                            game_world.add_object(uniquerf, 3)
                            game_world.add_collision_pairs(f'uniquerf:monster', uniquerf, None)

                            rfeffect = RFEffect(self.face_dir)
                            game_world.add_object(rfeffect, 3)

                            Attack = True
                    elif Character.state == 3:
                        if self.attack_time == 0:
                            self.attack_time = get_time()
                            self.frame = 0

                            normalrfsp = NormalRFSP(self.face_dir)
                            game_world.add_object(normalrfsp, 3)
                            game_world.add_collision_pairs(f'normalrfsp:monster', normalrfsp, None)

                            ultrfeffect = ULTRFEffect(self.face_dir)
                            game_world.add_object(ultrfeffect, 3)

                            rf_attack_voice_list = Character.voices['RF_Attack_Voice']
                            random.choice(rf_attack_voice_list).play()

                            Attack = True
                elif Character.stance == 2:
                    self.doubleattack = 0
                    if Character.state == 0 and Character.bullet_HG > 0:
                        if self.attack_time == 0:
                            self.attack_time = get_time()
                            self.frame = 0
                            Character.bullet_HG -= 1

                            

                            normalhg = NormalHG(self.face_dir)
                            game_world.add_object(normalhg, 3)
                            game_world.add_collision_pairs(f'normalhg:monster', normalhg, None)

                            hgeffect = HGEffect(self.face_dir)
                            game_world.add_object(hgeffect, 3)

                            if random.random() < 0.25:
                                hg_attack_voice_list = Character.voices['HG_Attack_Voice']
                                random.choice(hg_attack_voice_list).play()

                            Attack = True

                    elif Character.state == 1:
                        if Character.bullet_HG > 1:
                            if self.attack_time == 0:
                                self.double_time = get_time()
                                self.attack_time = get_time()
                                self.frame = 0
                                Character.bullet_HG -= 2

                                normalhg = NormalHG(self.face_dir)
                                game_world.add_object(normalhg, 3)
                                game_world.add_collision_pairs(f'normalhg:monster', normalhg, None)

                                hgeffect = HGEffect(self.face_dir)
                                game_world.add_object(hgeffect, 3)

                                if random.random() < 0.25:
                                    hg_attack_voice_list = Character.voices['HG_Attack_Voice']
                                    random.choice(hg_attack_voice_list).play()

                                self.doubleattack += 1

                                Attack = True

                        elif Character.bullet_HG == 1:
                            if self.attack_time == 0:
                                self.attack_time = get_time()
                                self.frame = 0
                                Character.bullet_HG -= 1

                                normalhg = NormalHG(self.face_dir)
                                game_world.add_object(normalhg, 3)
                                game_world.add_collision_pairs(f'normalhg:monster', normalhg, None)

                                hgeffect = HGEffect(self.face_dir)
                                game_world.add_object(hgeffect, 3)

                                if random.random() < 0.25:
                                    hg_attack_voice_list = Character.voices['HG_Attack_Voice']
                                    random.choice(hg_attack_voice_list).play()

                                Attack = True

        if Attack:
            if Character.stance == 0:
                if get_time() - self.attack_time > 0.5:
                    Character.attack_delay = 0.8
                    self.attack_time = 0
                    self.frame = 0
                    Attack = False
            elif Character.stance == 1:
                if get_time() - self.attack_time > 0.4:
                    if Character.state == 1 or Character.state == 3:
                        Character.attack_delay = 0.75
                    else:
                        Character.attack_delay = 1.5
                    self.attack_time = 0
                    self.frame = 0
                    Attack = False
            elif Character.stance == 2:
                if (0.3 > get_time() - self.double_time > 0.25) and self.doubleattack == 1:

                    normalhg = NormalHG(self.face_dir)
                    game_world.add_object(normalhg, 3)
                    game_world.add_collision_pairs(f'normalhg:monster', normalhg, None)

                    hgeffect = HGEffect(self.face_dir)
                    game_world.add_object(hgeffect, 3)

                    self.doubleattack += 1
                if get_time() - self.attack_time > 0.4:
                    Character.attack_delay = 0.4
                    self.attack_time = 0
                    self.frame = 0
                    Attack = False

        if not Character.hit_delay == 0:
            if self.hit_cool == 0:
                self.hit_cool = get_time()
            if get_time() - self.hit_cool > Character.hit_delay:
                Character.hit_delay = 0
                self.hit_cool = 0

        if not Character.attack_delay == 0:
            if self.attack_cool == 0:
                self.attack_cool = get_time()
            if get_time() - self.attack_cool > Character.attack_delay:
                Character.attack_delay = 0
                self.attack_cool = 0

        if not Character.hour_of_judgment_cooldown == 0:
            if self.Skill_SG_cool == 0:
                self.Skill_SG_cool = get_time()
            if get_time() - self.Skill_SG_cool > Character.hour_of_judgment_cooldown:
                Character.hour_of_judgment_cooldown = 0
                self.Skill_SG_cool = 0

        if not Character.last_request_cooldown == 0:
            if self.ULT_SG_cool == 0:
                self.ULT_SG_cool = get_time()
            if get_time() - self.ULT_SG_cool > Character.last_request_cooldown:
                Character.last_request_cooldown = 0
                self.ULT_SG_cool = 0

        if not Character.target_down_cooldown == 0:
            if self.Unique_RF_cool == 0:
                self.Unique_RF_cool = get_time()
            if get_time() - self.Unique_RF_cool > Character.target_down_cooldown:
                Character.target_down_cooldown = 0
                self.Unique_RF_cool = 0

        if not Character.perfect_shot_cooldown == 0:
            if self.Skill_RF_cool == 0:
                self.Skill_RF_cool = get_time()
            if get_time() - self.Skill_RF_cool > Character.perfect_shot_cooldown:
                Character.perfect_shot_cooldown = 0
                self.Skill_RF_cool = 0

        if not Character.catastrophe_cooldown == 0:
            if self.ULT_RF_cool == 0:
                self.ULT_RF_cool = get_time()
            if get_time() - self.ULT_RF_cool > Character.catastrophe_cooldown:
                Character.catastrophe_cooldown = 0
                self.ULT_RF_cool = 0

        if not Character.catastrophe_duration == 0:
            if self.catastrophe_time == 0:
                self.catastrophe_time = get_time()
            if get_time() - self.catastrophe_time > Character.catastrophe_duration:
                Character.catastrophe_duration = 0
                if God:
                    Character.catastrophe_cooldown = 1
                else:
                    Character.catastrophe_cooldown = 120
                Character.speed = 4
                Character.state = 0
                catastrophe = False
                Fall = True
                self.catastrophe_time = 0

        if not Character.equilibrium_cooldown == 0:
            if self.ULT_HG_cool == 0:
                self.ULT_HG_cool = get_time()
            if get_time() - self.ULT_HG_cool > Character.equilibrium_cooldown:
                Character.equilibrium_cooldown = 0
                self.ULT_HG_cool = 0

        if Character.state == 0:
            if 6320 < self.x < 6360 and 160 < self.y < 200 and play_mode.stage == 1:
                self.x, self.y = 34.0, 170.0
                play_mode.change_stage(play_mode.stage + 1)

                if Character.stance == 0:
                    Character.voices['SG_Portal_Voice'][0].play()
                elif Character.stance == 1:
                    Character.voices['RF_Portal_Voice'][0].play()
                elif Character.stance == 2:
                    Character.voices['HG_Portal_Voice'][0].play()

                Character.portal_sound.play()
            elif 1480 < self.x < 1520 and 640 < self.y < 680 and play_mode.stage == 2:
                self.x, self.y = 34.0, 170.0
                play_mode.change_stage(play_mode.stage + 1)

                if Character.stance == 0:
                    Character.voices['SG_Portal_Voice'][0].play()
                elif Character.stance == 1:
                    Character.voices['RF_Portal_Voice'][0].play()
                elif Character.stance == 2:
                    Character.voices['HG_Portal_Voice'][0].play()

                Character.portal_sound.play()
            elif 1520 < self.x < 1560 and 160 < self.y < 200 and play_mode.stage == 3 and Character.medal == 1:
                self.x, self.y = 34.0, 170.0
                play_mode.change_stage(play_mode.stage + 1)

                if Character.stance == 0:
                    Character.voices['SG_Portal_Voice'][0].play()
                elif Character.stance == 1:
                    Character.voices['RF_Portal_Voice'][0].play()
                elif Character.stance == 2:
                    Character.voices['HG_Portal_Voice'][0].play()

                Character.portal_sound.play()
            elif play_mode.stage == 4 and Character.medal == 1:
                self.x, self.y = 34.0, 170.0
                play_mode.change_stage(play_mode.stage + 1)

                if Character.stance == 0:
                    Character.voices['SG_Portal_Voice'][0].play()
                elif Character.stance == 1:
                    Character.voices['RF_Portal_Voice'][0].play()
                elif Character.stance == 2:
                    Character.voices['HG_Portal_Voice'][0].play()

            elif (play_mode.stage == 5 or play_mode.stage == 6) and Character.medal == 2:
                self.x, self.y = 34.0, 170.0
                play_mode.change_stage(play_mode.stage + 1)

                if Character.stance == 0:
                    Character.voices['SG_Portal_Voice'][0].play()
                elif Character.stance == 1:
                    Character.voices['RF_Portal_Voice'][0].play()
                elif Character.stance == 2:
                    Character.voices['HG_Portal_Voice'][0].play()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_SPACE:
            self.jump_buffer_timer = self.JUMP_BUFFER
            self.jump_consumed = False
        self.state_machine.add_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        if God:
            draw_rectangle(*self.get_rect())

    def change_z(self):
        if Character.stance == 0:
            Character.stance = 1
            Character.speed = 4
            Character.rf_stance_sound.play()
        elif Character.stance == 1:
            Character.stance = 2
            Character.speed = 5
            Character.hg_stance_sound.play()
        elif Character.stance == 2:
            Character.stance = 0
            Character.speed = 3
            Character.sg_stance_sound.play()

    def change_x(self):
        if Character.stance == 0:
            Character.stance = 2
            Character.speed = 5
            Character.hg_stance_sound.play()
        elif Character.stance == 1:
            Character.stance = 0
            Character.speed = 3
            Character.sg_stance_sound.play()
        elif Character.stance == 2:
            Character.stance = 1
            Character.speed = 4
            Character.rf_stance_sound.play()

    def get_bb(self):
        return self.x - 17.0, self.y - 49.0, self.x + 17.0, self.y + 19.0

    def get_rect(self):
        return self.sx - 17.0, self.y - 49.0, self.sx + 17.0, self.y + 19.0

    def handle_collision(self, group, other):
        global Fall, fall_velocity, Climb
        if group == 'server.character:ladder':
            if not Climb:
                Climb = True
            if Fall:
                Fall = False
                fall_velocity = 0.0
                self._reset_jump_after_ground()
        if group == 'server.character:medal':
            Character.medal += 1

    def handle_collision_fall(self, group, other):
        global Fall, fall_velocity
        if group == 'server.character:ground' and Fall:
            self.y = ground.Ground.collide_fall(other)
            Fall = False
            if fall_velocity > 2.0:
                Character.fall_sound.play()
            fall_velocity = 0.0
            self._reset_jump_after_ground()

    def handle_collision_jump(self, group, other):
        global Jump, jump_velocity, Fall
        if group == 'server.character:ground' and Jump:
            self.y = ground.Ground.collide_jump(other)
            Jump = False
            Fall = True
            jump_velocity = 9.0

    def take_damage(self, damage):
        if Character.hit_delay == 0 and not Character.state == -1 and not Invincibility and not God:
            Character.damage = damage
            self.state_machine.add_event(('HIT', 0))

    def take_heal(self, heal):
        Character.hp = min(Character.hp + heal, Character.max_hp)

    def take_more_hp(self):
        Character.max_hp += 2

    def enhance(self, static):
        Character.upgrade += static
        Character.upgrade = clamp(0, Character.upgrade, 5)

        # 0강
        if Character.upgrade == 0:
            # 1 -> 0강
            Character.damage_SG = 1
            Character.damage_RF = 4
            Character.damage_HG = 1
            Character.shield_def = 1
            Character.target_down_max = 2
            Character.max_bullet_HG = 20
            Character.bullet_HG = min(20, Character.bullet_HG)

        # 1강
        elif Character.upgrade == 1:
            Character.shield_def = 2
            Character.target_down_max = 3
            Character.max_bullet_HG = 24

            # 2 -> 1강
            Character.damage_SG = 1
            Character.damage_RF = 4

        # 2강
        elif Character.upgrade == 2:
            Character.damage_SG = 2
            Character.damage_RF = 6
            # 민첩한 사격 쿨타임 감소
            # AT02 유탄 범위 증가

            # 3 -> 2강
            Character.stun_SG = 2
            Character.stun_RF = 1
            Character.damage_HG = 1
            Character.shield_def = 2

        # 3강
        elif Character.upgrade == 3:
            Character.stun_SG = 4
            Character.stun_RF = 2
            Character.damage_HG = 2
            Character.shield_def = 4
            # 타겟 다운 범위 증가

            # 4 -> 3강
            Character.max_bullet_HG = 24
            Character.bullet_HG = min(24, Character.bullet_HG)
            Character.damage_SG = 2
            Character.damage_RF = 6

        # 4강
        elif Character.upgrade == 4:
            Character.max_bullet_HG = 30
            Character.damage_SG = 3
            Character.damage_RF = 10
            # 민첩한 사격 범위 증가
            # AT02 유탄 범위 증가
            # 불렛 레인 쿨타임 감소

            # 5 -> 4강
            Character.stun_SG = 4
            Character.damage_HG = 2
            Character.shield_def = 4

        # 5강
        elif Character.upgrade == 5:
            Character.stun_SG = 6
            Character.damage_RF = 16
            Character.damage_HG = 4
            Character.shield_def = 8