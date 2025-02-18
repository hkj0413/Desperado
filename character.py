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
from rcskillsg_effect import RcskillSGEffect
from rcskillsg import RcskillSG
from qskillsg_effect import QskillSGEffect
from qskillsg import QskillSG
from qskillsg_stun import QskillstunSG
from eskillsg_effect import EskillSGEffect
from eskillsg1 import EskillSG1
from eskillsg2 import EskillSG2
from eskillsg3 import EskillSG3
from cskillsg_effect import CskillSGEffect

from rf_effect import RFEffect
from normalrf_effect import NormalRFEffect
from normalrf import NormalRF
from normalrf_superior_effect import NormalRFSPEffect
from normalrfsp import NormalRFSP
from reloadrf import ReloadRF
from rcskillrf import RcskillRF
from rcskillrf_effect import RcskillRFEffect
from qskillrf import QskillRF
from qskillrf_effect import QskillRFEffect
from cskillrf import CskillRF
from cskillrf_effect import CskillRFEffect

from hg_effect import HGEffect
from normalhg import NormalHG
from normalhg_effect import NormalHGEffect
from rcskillhg import RcskillHG
from rcskillhg_effect import RcskillHGEffect
from qskillhg import QskillHG
from eskillhg import EskillHG
from cskillhg_effect import CskillHGEffect
from cskillhg import CskillHG

from dasheffect import DashEffect

from state_machine import *

PIXEL_PER_METER = (30.0 / 1)  # 30 pixel 1 m
RUN_SPEED_KMPH = 10.0 # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

a_pressed = False
d_pressed = False
w_pressed = False
s_pressed = False
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
Rc_HG = False
rchg = False
catastrophe = False

jump_velocity = 9.0
fall_velocity = 0.0
gravity = 0.3
mouse_x, mouse_y = 0, 0
screen_left = 0
screen_right = 1080
random_angle = 0
chance = 0

mob_group = [
    'spore', 'slime', 'pig', 'stonegolem', 'skelldog', 'coldeye', 'wildboar', 'stonestatue',
    'bulldog', 'imp', 'fireboar', 'firemixgolem'
             ]

class Idle:
    @staticmethod
    def enter(character, e):
        global Jump, d_pressed, a_pressed, attacking, Reload_SG, Reload_HG, s_pressed, w_pressed, Invincibility, God
        global Rc_HG, Attack, mouse_x
        if start_event(e):
            character.face_dir = 1
        elif right_up(e):
            d_pressed = False
        elif left_up(e):
            a_pressed = False
        elif walk(e):
            if a_pressed or d_pressed:
                character.state_machine.add_event(('WALK', 0))
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
        elif change_stance_z(e) and not Jump and not Fall and not Attack and Character.state == 0 and not Reload_SG and not Reload_HG and not Rc_HG:
            character.change_z()
        elif change_stance_x(e) and not Jump and not Fall and not Attack and Character.state == 0 and not Reload_SG and not Reload_HG and not Rc_HG:
            character.change_x()
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
            attacking = False
        elif rc_down(e):
            if Character.stance == 0:
                Character.state = 1
                Character.speed = 1
            elif Character.stance == 1:
                if Character.state == 0:
                    if Character.target_down_cooldown == 0:
                        Character.state = 1
                        Character.hit_delay = 1
                        character.state_machine.add_event(('RF_RC', 0))
                elif Character.state == 4 and not Attack and Character.attack_delay == 0:
                    if character.x > 2700 and not character.mouse:
                        scroll_offset = 2700 - 1080 // 2
                        mouse_x = mouse_x + scroll_offset
                        character.mouse = True
                    elif character.x > 540 and not character.mouse and server.background.w > 1080:
                        scroll_offset = character.x - 1080 // 2
                        mouse_x = mouse_x + scroll_offset
                        character.mouse = True
                    if mouse_x > character.x:
                        character.attack_dir = 1
                        if (not Move or Fall or Jump) and not d_pressed and not a_pressed:
                            character.face_dir = 1
                    elif mouse_x < character.x:
                        character.attack_dir = -1
                        if (not Move or Fall or Jump) and not d_pressed and not a_pressed:
                            character.face_dir = -1
                    if character.attack_time == 0:
                        character.attack_time = get_time()
                        character.frame = 0

                        rcskillrfeffect = RcskillRFEffect()
                        game_world.add_object(rcskillrfeffect, 3)

                        rcskillrf = RcskillRF()
                        game_world.add_object(rcskillrf, 3)
                        for mob in mob_group:
                            game_world.add_collision_pairs(f'rcskillrf:{mob}', rcskillrf, None)

                        cskillrfeffect = CskillRFEffect(character.attack_dir)
                        game_world.add_object(cskillrfeffect, 3)

                        rf_attack_sound_list = Character.voices['RF_Attack']
                        random.choice(rf_attack_sound_list).play()

                        Attack = True
            elif Character.stance == 2:
                Character.state = 1
        elif rc_up(e):
            if Character.stance == 0:
                Character.state = 0
                if not Reload_SG:
                    Character.speed = 3
            elif Character.stance == 2:
                Character.state = 0
        elif jump(e) and not Jump and not Fall:
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
                elif Character.state == 4:
                    Jump = True
                    Character.jump_sound.play()
                    if not Attack:
                        character.frame = 0
            elif Character.stance == 2:
                Jump = True
                Character.jump_sound.play()
                if not Attack and not Reload_HG and not Rc_HG:
                    character.frame = 0
        elif dash(e) and Character.dash_cooldown == 0 and not Reload_SG and not Reload_HG and not Rc_HG:
            Character.hit_delay = 1
            character.state_machine.add_event(('USE_DASH', 0))
        elif reload(e):
            if Character.stance == 0 and Character.bullet_SG == 0 and Character.state <= 1:
                if not Reload_SG:
                    Reload_SG = True
                    Character.speed = 1
                    character.frame = 0
                    character.one = 0
            elif Character.stance == 1 and Character.bullet_RF == 0 and Character.state == 0:
                if s_pressed:
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_RELOAD_S', 0))
                elif not s_pressed:
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_RELOAD', 0))
            elif Character.stance == 2 and Character.bullet_HG == 0 and Character.state == 0:
                if not Reload_HG:
                    Reload_HG = True
                    Character.speed = 7
                    character.frame = 0
                    Invincibility = True
                    Character.Reload_HG_sound.play()
                    Character.voices['HG_Reload'][0].play()
        elif q_down(e):
            if Character.stance == 0 and Character.state == 0:
                if Character.hour_of_judgment_cooldown == 0 and not Attack and (God or Character.score >= 200):
                    Character.state = 2
                    Character.hit_delay = 1
                    character.state_machine.add_event(('SG_Q', 0))
            elif Character.stance == 1 and Character.state == 0:
                if Character.perfect_shot_cooldown == 0 and (God or Character.score >= 200):
                    Character.state = 3
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_Q', 0))
            elif Character.stance == 2:
                if Character.at02_grenade_cooldown == 0 and Character.bullet_HG > 0 and (God or Character.score >= 200):
                    Character.hit_delay = 0.5
                    Character.bullet_HG -= 1

                    qskillhg = QskillHG(character.face_dir)
                    game_world.add_object(qskillhg, 3)
                    for mob in mob_group:
                        game_world.add_collision_pairs(f'qskillhg:{mob}', qskillhg, None)

                    if not rchg:
                        hg_q_sound_list = Character.voices['HG_Q']
                        random.choice(hg_q_sound_list).play()

                    if God:
                        Character.at02_grenade_cooldown = 1
                    else:
                        Character.at02_grenade_cooldown = 4
        elif e_down(e):
            if Character.stance == 0 and Character.state == 0:
                if Character.shotgun_rapid_fire_cooldown == 0 and (God or Character.score >= 1000):
                    Character.state = 3
                    Character.hit_delay = 1
                    character.state_machine.add_event(('SG_E', 0))
            elif Character.stance == 1 and Character.state == 0:
                if Character.focus_shot_cooldown == 0 and (God or Character.score >= 1000):
                    Character.state = 3
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_E', 0))
            elif Character.stance == 2 and Character.state == 0:
                if Character.bullet_rain_cooldown == 0 and Character.bullet_HG > 0 and (God or Character.score >= 1000):
                    Character.state = 3
                    Character.hit_delay = 1
                    character.state_machine.add_event(('HG_E', 0))
        elif c_down(e):
            if Character.stance == 0 and Character.state == 0:
                if Character.last_request_cooldown == 0 and (God or Character.score >= 2000):
                    Character.state = 4
                    Invincibility = True
                    character.state_machine.add_event(('SG_C', 0))
            elif Character.stance == 1 and Character.state == 0:
                if Character.catastrophe_cooldown == 0 and (God or Character.score >= 2000):
                    Character.state = 4
                    Invincibility = True
                    character.state_machine.add_event(('RF_C', 0))
            elif Character.stance == 2 and Character.state == 0:
                if Character.equilibrium_cooldown == 0 and (God or Character.score >= 2000):
                    Character.state = 4
                    Invincibility = True
                    character.state_machine.add_event(('HG_C', 0))

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
            Character.score += 1000

        if rchg:
            if not Rc_HG:
                Rc_HG = True

        if Character.stance == 0 and not Reload_SG:
            if Character.state == 0:
                if character.name != 'Idle_SG':
                    character.name = 'Idle_SG'
            elif Character.state == 1:
                if character.name != 'Rc_SG':
                    character.name = 'Rc_SG'
            character.frame = clamp(0, character.frame, 13)
        elif Character.stance == 0 and Reload_SG:
            if character.name != 'Reload_SG':
                character.name = 'Reload_SG'
        elif Character.stance == 1:
            if character.name != 'Idle_RF':
                character.name = 'Idle_RF'
            character.frame = clamp(0, character.frame, 13)
        elif Character.stance == 2 and (Reload_HG or Rc_HG):
            if character.name != 'Reload_HG':
                character.name = 'Reload_HG'
        elif Character.stance == 2:
            if character.name != 'Idle_HG':
                character.name = 'Idle_HG'
            character.frame = clamp(0, character.frame, 10)

    @staticmethod
    def exit(character, e):
        if right_down(e):
            character.face_dir = 1
        elif left_down(e):
            character.face_dir = -1

    @staticmethod
    def do(character):
        global Move, Reload_SG ,Reload_HG, Invincibility, Rc_HG, rchg
        if Attack:
            if Character.stance == 0:
                character.frame = (character.frame + 15.0 * 0.8 * game_framework.frame_time) % 15
            elif Character.stance == 1:
                character.frame = (character.frame + 7.0 * 2.0 * game_framework.frame_time) % 7
            elif Character.stance == 2:
                character.frame = (character.frame + 5.0 * 3.0 * game_framework.frame_time) % 5

        elif Reload_SG:
            character.frame = character.frame + 16.0 * 0.7 * game_framework.frame_time
            if character.frame > 16.0:
                if Character.state == 0:
                    Character.speed = 3
                elif Character.state == 1:
                    Character.speed = 1
                Character.bullet_SG = 8
                character.frame = 0
                Reload_SG = False
                Character.voices['SG_Reload'][0].play()
                if d_pressed or a_pressed:
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))
            elif character.frame > 4.0 and character.one == 0:
                Character.Reload_SG_sound.play()
                character.one += 1

        elif Reload_HG:
            character.frame = character.frame + 8.0 * 1.8 * game_framework.frame_time
            if character.frame > 8.0:
                Character.speed = 5
                Character.bullet_HG = Character.max_bullet_HG
                character.frame = 0
                Reload_HG = False
                Invincibility = False
                if d_pressed or a_pressed:
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))

        elif Rc_HG:
            character.frame = character.frame + 8.0 * 1.8 * game_framework.frame_time
            if character.frame > 8.0:
                Character.speed = 5
                character.frame = 0
                Rc_HG = False
                rchg = False
                if d_pressed or a_pressed:
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))

        elif not Jump and not Fall:
            if Move:
                Move = False
            if Character.stance == 0 or Character.stance == 1:
                character.frame = (character.frame + 14.0 * 1.5 * game_framework.frame_time) % 14
            elif Character.stance == 2:
                character.frame = (character.frame + 11.0 * 1.5 * game_framework.frame_time) % 11

        if Climb:
            if w_pressed and not s_pressed:
                if not Move:
                    Move = True
                character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return
            elif s_pressed and not w_pressed:
                if not Move:
                    Move = True
                character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return

    @staticmethod
    def draw(character):
        if Attack:
            if character.attack_dir == 1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
            elif character.attack_dir == -1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
        elif Reload_SG:
            if character.face_dir == 1:
                character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
            elif character.face_dir == -1:
                character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

        elif Reload_HG or Rc_HG:
            if character.face_dir == 1:
                if 0 <= int(character.frame) <= 4:
                    roll = 60 - int(character.frame) * 15
                else:
                    roll = -15
                character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx + roll, character.y, 170, 170)
            elif character.face_dir == -1:
                if 0 <= int(character.frame) <= 4:
                    roll = 60 - int(character.frame) * 15
                else:
                    roll = -15
                character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx - roll, character.y, 170, 170)

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
        global a_pressed, d_pressed, Jump, attacking, Reload_SG, Reload_HG, s_pressed, w_pressed, Invincibility, God
        global Rc_HG, Attack, mouse_x
        if right_down(e):
            d_pressed = True
            character.face_dir = 1
        elif right_up(e):
            d_pressed = False
            if a_pressed:
                character.face_dir = -1
            elif not a_pressed:
                character.state_machine.add_event(('IDLE', 0))
        elif left_down(e):
            a_pressed = True
            character.face_dir = -1
        elif left_up(e):
            a_pressed = False
            if d_pressed:
                character.face_dir = 1
            elif not d_pressed:
                character.state_machine.add_event(('IDLE', 0))
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
            if not d_pressed and not a_pressed and not s_pressed and Climb:
                character.state_machine.add_event(('IDLE', 0))
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
            if not d_pressed and not a_pressed and not w_pressed and Climb:
                character.state_machine.add_event(('IDLE', 0))
        elif change_stance_z(e) and not Jump and not Fall and not Attack and Character.state == 0 and not Reload_SG and not Reload_HG and not Rc_HG:
            character.change_z()
        elif change_stance_x(e) and not Jump and not Fall and not Attack and Character.state == 0 and not Reload_SG and not Reload_HG and not Rc_HG:
            character.change_x()
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
            attacking = False
        elif rc_down(e):
            if Character.stance == 0:
                Character.state = 1
                Character.speed = 1
            elif Character.stance == 1:
                if Character.state == 0:
                    if Character.target_down_cooldown == 0:
                        Character.state = 1
                        Character.hit_delay = 1
                        character.state_machine.add_event(('RF_RC', 0))
                elif Character.state == 4 and not Attack and Character.attack_delay == 0:
                    if character.x > 2700 and not character.mouse:
                        scroll_offset = 2700 - 1080 // 2
                        mouse_x = mouse_x + scroll_offset
                        character.mouse = True
                    elif character.x > 540 and not character.mouse and server.background.w > 1080:
                        scroll_offset = character.x - 1080 // 2
                        mouse_x = mouse_x + scroll_offset
                        character.mouse = True
                    if mouse_x > character.x:
                        character.attack_dir = 1
                        if (not Move or Fall or Jump) and not d_pressed and not a_pressed:
                            character.face_dir = 1
                    elif mouse_x < character.x:
                        character.attack_dir = -1
                        if (not Move or Fall or Jump) and not d_pressed and not a_pressed:
                            character.face_dir = -1
                    if character.attack_time == 0:
                        character.attack_time = get_time()
                        character.frame = 0

                        rcskillrfeffect = RcskillRFEffect()
                        game_world.add_object(rcskillrfeffect, 3)

                        rcskillrf = RcskillRF()
                        game_world.add_object(rcskillrf, 3)
                        for mob in mob_group:
                            game_world.add_collision_pairs(f'rcskillrf:{mob}', rcskillrf, None)

                        cskillrfeffect = CskillRFEffect(character.attack_dir)
                        game_world.add_object(cskillrfeffect, 3)

                        rf_attack_sound_list = Character.voices['RF_Attack']
                        random.choice(rf_attack_sound_list).play()

                        Attack = True
            elif Character.stance == 2:
                Character.state = 1
        elif rc_up(e):
            if Character.stance == 0:
                Character.state = 0
                if not Reload_SG:
                    Character.speed = 3
            elif Character.stance == 2:
                Character.state = 0
        elif jump(e) and not Jump and not Fall:
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
                elif Character.state == 4:
                    Jump = True
                    Character.jump_sound.play()
                    if not Attack:
                        character.frame = 0
            elif Character.stance == 2:
                Jump = True
                Character.jump_sound.play()
                if not Attack and not Reload_HG and not Rc_HG:
                    character.frame = 0
        elif dash(e) and Character.dash_cooldown == 0 and not Reload_SG and not Reload_HG and not Rc_HG:
            Character.hit_delay = 1
            character.state_machine.add_event(('USE_DASH', 0))
        elif reload(e):
            if Character.stance == 0 and Character.bullet_SG == 0 and Character.state <= 1:
                if not Reload_SG:
                    Reload_SG = True
                    Character.speed = 1
                    character.frame = 0
                    character.one = 0
            elif Character.stance == 1 and Character.bullet_RF == 0 and Character.state == 0:
                if s_pressed:
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_RELOAD_S', 0))
                elif not s_pressed:
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_RELOAD', 0))
            elif Character.stance == 2 and Character.bullet_HG == 0 and Character.state == 0:
                if not Reload_HG:
                    Reload_HG = True
                    Character.speed = 7
                    character.frame = 0
                    Invincibility = True
                    Character.Reload_HG_sound.play()
                    Character.voices['HG_Reload'][0].play()
        elif q_down(e):
            if Character.stance == 0 and Character.state == 0:
                if Character.hour_of_judgment_cooldown == 0 and not Attack and (God or Character.score >= 200):
                    Character.state = 2
                    Character.hit_delay = 1
                    character.state_machine.add_event(('SG_Q', 0))
            elif Character.stance == 1 and Character.state == 0:
                if Character.perfect_shot_cooldown == 0 and (God or Character.score >= 200):
                    Character.state = 3
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_Q', 0))
            elif Character.stance == 2:
                if Character.at02_grenade_cooldown == 0 and Character.bullet_HG > 0 and (God or Character.score >= 200):
                    Character.hit_delay = 0.5
                    Character.bullet_HG -= 1

                    qskillhg = QskillHG(character.face_dir)
                    game_world.add_object(qskillhg, 3)
                    for mob in mob_group:
                        game_world.add_collision_pairs(f'qskillhg:{mob}', qskillhg, None)

                    if not rchg:
                        hg_q_sound_list = Character.voices['HG_Q']
                        random.choice(hg_q_sound_list).play()

                    if God:
                        Character.at02_grenade_cooldown = 1
                    else:
                        Character.at02_grenade_cooldown = 4
        elif e_down(e):
            if Character.stance == 0 and Character.state == 0:
                if Character.shotgun_rapid_fire_cooldown == 0 and (God or Character.score >= 1000):
                    Character.state = 3
                    Character.hit_delay = 1
                    character.state_machine.add_event(('SG_E', 0))
            elif Character.stance == 1 and Character.state == 0:
                if Character.focus_shot_cooldown == 0 and (God or Character.score >= 1000):
                    Character.state = 3
                    Character.hit_delay = 1
                    character.state_machine.add_event(('RF_E', 0))
            elif Character.stance == 2 and Character.state == 0:
                if Character.bullet_rain_cooldown == 0 and Character.bullet_HG > 0 and (God or Character.score >= 1000):
                    Character.state = 3
                    Character.hit_delay = 1
                    character.state_machine.add_event(('HG_E', 0))
        elif c_down(e):
            if Character.stance == 0 and Character.state == 0:
                if Character.last_request_cooldown == 0 and (God or Character.score >= 2000):
                    Character.state = 4
                    Invincibility = True
                    character.state_machine.add_event(('SG_C', 0))
            elif Character.stance == 1 and Character.state == 0:
                if Character.catastrophe_cooldown == 0 and (God or Character.score >= 2000):
                    Character.state = 4
                    Invincibility = True
                    character.state_machine.add_event(('RF_C', 0))
            elif Character.stance == 2 and Character.state == 0:
                if Character.equilibrium_cooldown == 0 and (God or Character.score >= 2000):
                    Character.state = 4
                    Invincibility = True
                    character.state_machine.add_event(('HG_C', 0))

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
            Character.score += 1000

        if rchg:
            if not Rc_HG:
                Rc_HG = True

        if Character.stance == 0 and not Reload_SG:
            if Character.state == 0:
                if character.name != 'Walk_SG':
                    character.name = 'Walk_SG'
            elif Character.state == 1:
                if character.name != 'Rc_SG':
                    character.name = 'Rc_SG'
        elif Character.stance == 0 and Reload_SG:
            if character.name != 'Reload_SG':
                character.name = 'Reload_SG'
        elif Character.stance == 1:
            if character.name != 'Walk_RF':
                character.name = 'Walk_RF'
        elif Character.stance == 2 and (Reload_HG or Rc_HG):
            if character.name != 'Reload_HG':
                character.name = 'Reload_HG'
        elif Character.stance == 2:
            if character.name != 'Walk_HG':
                character.name = 'Walk_HG'

        if not Reload_SG and not Reload_HG and not Rc_HG:
            if Character.stance == 0 and Character.state == 1:
                character.frame = clamp(0, character.frame, 13)
            else:
                character.frame = clamp(0, character.frame, 5)

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Fall, Move, Climb, Reload_SG, Reload_HG, Invincibility, Rc_HG, rchg
        if not Move:
            Move = True

        if Attack:
            if Character.stance == 0:
                character.frame = (character.frame + 15.0 * 0.8 * game_framework.frame_time) % 15
            elif Character.stance == 1:
                character.frame = (character.frame + 7.0 * 2.0 * game_framework.frame_time) % 7
            elif Character.stance == 2:
                character.frame = (character.frame + 5.0 * 3.0 * game_framework.frame_time) % 5

        elif Reload_SG:
            character.frame = character.frame + 16.0 * 0.7 * game_framework.frame_time
            if character.frame > 16.0:
                if Character.state == 0:
                    Character.speed = 3
                elif Character.state == 1:
                    Character.speed = 1
                Character.bullet_SG = 8
                character.frame = 0
                Reload_SG = False
                Character.voices['SG_Reload'][0].play()
                if d_pressed or a_pressed:
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))
            elif character.frame > 4.0 and character.one == 0:
                Character.Reload_SG_sound.play()
                character.one += 1

        elif Reload_HG:
            character.frame = character.frame + 8.0 * 1.8 * game_framework.frame_time
            if character.frame > 8.0:
                Character.speed = 5
                Character.bullet_HG = Character.max_bullet_HG
                character.frame = 0
                Reload_HG = False
                Invincibility = False
                if d_pressed or a_pressed:
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))

        elif Rc_HG:
            character.frame = character.frame + 8.0 * 1.8 * game_framework.frame_time
            if character.frame > 8.0:
                Character.speed = 5
                character.frame = 0
                Rc_HG = False
                rchg = False
                if d_pressed or a_pressed:
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))

        else:
            if Character.stance == 0 and Character.state == 1:
                character.frame = (character.frame + 14.0 * 1.5 * game_framework.frame_time) % 14
            elif not Jump and not Fall:
                character.frame = (character.frame + 6.0 * 2.0 * game_framework.frame_time) % 6

        if Climb:
            if w_pressed and not s_pressed:
                character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return
            elif s_pressed and not w_pressed:
                character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return

        if d_pressed or a_pressed:
            if Character.stance == 0:
                if not Attack:
                    character.x += Character.speed * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time
            elif Character.stance == 1:
                if (Character.state == 0 and not Attack) or Character.state == 4:
                    character.x += Character.speed * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time
            elif Character.stance == 2:
                if not Character.state == 2:
                    character.x += Character.speed * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time

            for block in game_world.collision_pairs['server.character:ground'][1] + game_world.collision_pairs['server.character:wall'][1]:
                if screen_left - 15 <= block.x <= screen_right + 15:
                    if game_world.collide(character, block):
                        character.x -= Character.speed * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time
                        return

            ground_objects = game_world.collision_pairs['server.character:ground'][1]
            for block in ground_objects:
                if screen_left - 15 <= block.x <= screen_right + 15:
                    if game_world.collide_ad(character, block, ground_objects):
                        Fall = True
                        return

            for block in game_world.collision_pairs['server.character:ladder'][1]:
                if screen_left - 15 <= block.x <= screen_right + 15:
                    if game_world.collide_ladder(character, block):
                        Fall = True
                        Climb = False
                        return

    @staticmethod
    def draw(character):
        if Attack:
            if character.attack_dir == 1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, '', character.sx,
                                                                                       character.y, 170, 170)
            elif character.attack_dir == -1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, 'h', character.sx,
                                                                                       character.y, 170, 170)
        elif Reload_SG:
            if character.face_dir == 1:
                character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
            elif character.face_dir == -1:
                character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

        elif Reload_HG or Rc_HG:
            if character.face_dir == 1:
                if 0 <= int(character.frame) <= 4:
                    roll = 60 - int(character.frame) * 15
                else:
                    roll = -15
                character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx + roll, character.y, 170, 170)
            elif character.face_dir == -1:
                if 0 <= int(character.frame) <= 4:
                    roll = 60 - int(character.frame) * 15
                else:
                    roll = -15
                character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx - roll, character.y, 170, 170)

        else:
            if character.face_dir == 1:
                character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
            elif character.face_dir == -1:
                character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

class Hit:
    @staticmethod
    def enter(character, e):
        global a_pressed, d_pressed, Jump, jump_velocity, Fall, attacking, s_pressed, w_pressed, Rc_HG, catastrophe
        if take_hit(e):
            if Character.stance == 0 and (Character.state == 1 or Reload_SG):
                Character.hp = max(0, Character.hp - max(0, (Character.damage - Character.shield_def)))
                if Character.hp == 0:
                    Character.speed = 3
                    Character.score -= 100
                    character.state_machine.add_event(('DIE', 0))
                else:
                    sg_rc_sound_list = Character.voices['SG_Rc']
                    if random.random() < 0.25:
                        Character.Rc_SG_counter_sound.play()

                        rcskillsgeffect = RcskillSGEffect()
                        game_world.add_object(rcskillsgeffect, 3)

                        rcskillsg = RcskillSG()
                        game_world.add_object(rcskillsg, 3)
                        for mob in mob_group:
                            game_world.add_collision_pairs(f'rcskillsg:{mob}', rcskillsg, None)

                        random.choice(sg_rc_sound_list).play()
                    else:
                        Character.Rc_SG_sound.play()
                    if a_pressed or d_pressed:
                        character.state_machine.add_event(('WALK', 0))
            elif Character.stance == 1 and Character.state == 4 and catastrophe:
                Character.hp = max(0, Character.hp - Character.damage)
                if Character.hp == 0:
                    Character.score -= 100
                    Character.catastrophe_duration = 0
                    Character.catastrophe_cooldown = 120
                    Character.speed = 4
                    Character.state = 0
                    catastrophe = False
                    character.catastrophe_time = 0
                    character.state_machine.add_event(('DIE', 0))
                elif a_pressed or d_pressed:
                    character.state_machine.add_event(('WALK', 0))
            elif Character.stance == 2 and Character.state == 1 and Rc_HG:
                Character.hp = max(0, Character.hp - Character.damage)
                Character.state = 0
                if Character.hp == 0:
                    Character.speed = 5
                    Character.score -= 100
                    character.state_machine.add_event(('DIE', 0))
                elif a_pressed or d_pressed:
                    character.state_machine.add_event(('WALK', 0))
            elif (Character.state == 0 and not Character.stance == 2) or (
                    (Character.state == 0 or Character.state == 1) and Character.stance == 2 and not Rc_HG):
                a_pressed = False
                d_pressed = False
                if Climb:
                    w_pressed = False
                    s_pressed = False
                Jump = False
                jump_velocity = 9.0
                Fall = True
                Character.state = 0
                if not Attack:
                    character.frame = 0
                Character.hp = max(0, Character.hp - Character.damage)
                if Character.hp == 0:
                    Character.score -= 100
                    character.state_machine.add_event(('DIE', 0))
                else:
                    if Character.stance == 0:
                        sg_hit_sound_list = Character.voices['SG_Hit']
                        random.choice(sg_hit_sound_list).play()
                    elif Character.stance == 1:
                        rf_hit_sound_list = Character.voices['RF_Hit']
                        random.choice(rf_hit_sound_list).play()
                    elif Character.stance == 2:
                        hg_hit_sound_list = Character.voices['HG_Hit']
                        random.choice(hg_hit_sound_list).play()
            character.wait_time = get_time()
            Character.hit_delay = 1.5
        elif right_up(e):
            d_pressed = False
        elif left_up(e):
            a_pressed = False
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
            attacking = False
        elif right_down(e):
            d_pressed = True
            character.face_dir = 1
            if (Character.stance == 0 and Character.state == 1) or (Character.stance == 2 and Rc_HG):
                character.state_machine.add_event(('WALK', 0))
        elif left_down(e):
            a_pressed = True
            character.face_dir = -1
            if (Character.stance == 0 and Character.state == 1) or (Character.stance == 2 and Rc_HG):
                character.state_machine.add_event(('WALK', 0))
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
        elif rc_up(e):
            if Character.stance == 0 and Character.state == 1:
                Character.state = 0
                Character.speed = 3
            if Character.stance == 2 and Character.state == 1:
                Character.state = 0

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Reload_SG, Reload_HG, Invincibility, Rc_HG, rchg
        if get_time() - character.wait_time > 0.5:
            character.state_machine.add_event(('TIME_OUT', 0))

        if Attack:
            if Character.stance == 0:
                character.frame = (character.frame + 15.0 * 0.8 * game_framework.frame_time) % 15
            elif Character.stance == 1:
                character.frame = (character.frame + 7.0 * 2.0 * game_framework.frame_time) % 7
            elif Character.stance == 2:
                character.frame = (character.frame + 5.0 * 3.0 * game_framework.frame_time) % 5

        elif Reload_SG:
            character.frame = character.frame + 16.0 * 1.0 * game_framework.frame_time
            if character.frame > 16.0:
                if Character.state == 0:
                    Character.speed = 3
                elif Character.state == 1:
                    Character.speed = 1
                Character.bullet_SG = 8
                character.frame = 0
                Reload_SG = False

        elif Reload_HG:
            character.frame = character.frame + 8.0 * 1.8 * game_framework.frame_time
            if character.frame > 8.0:
                Character.speed = 5
                Character.bullet_HG = Character.max_bullet_HG
                character.frame = 0
                Reload_HG = False
                Invincibility = False

        elif Rc_HG:
            character.frame = character.frame + 8.0 * 1.8 * game_framework.frame_time
            if character.frame > 8.0:
                Character.speed = 5
                character.frame = 0
                Rc_HG = False
                rchg = False

        else:
            if Character.stance == 0 and Character.state == 1:
                character.frame = (character.frame + 14.0 * 1.5 * game_framework.frame_time) % 14

    @staticmethod
    def draw(character):
        if Attack:
            if character.attack_dir == 1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
            elif character.attack_dir == -1:
                if Character.stance == 0:
                    character.images['Attack_SG'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)
                elif Character.stance == 1:
                    character.images['Attack_RF'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)
                elif Character.stance == 2:
                    character.images['Attack_HG'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

        elif Character.state == 0 and not Reload_SG and not Reload_HG and not Rc_HG:
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
        global a_pressed, d_pressed, Jump, jump_velocity, Fall, fall_velocity, Attack, attacking, Move, s_pressed, w_pressed
        global Reload_SG, Reload_RF, rrf, Reload_HG, Climb, Invincibility, Rc_HG, rchg
        if die(e):
            Move = False
            Jump = False
            Fall = False
            Climb = False
            Attack = False
            attacking = False
            Invincibility = False
            a_pressed = False
            d_pressed = False
            w_pressed = False
            s_pressed = False
            Reload_SG = False
            Reload_RF = False
            rrf = False
            Reload_HG = False
            Rc_HG = False
            rchg = False
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
                sg_die_sound_list = Character.voices['SG_Die']
                random.choice(sg_die_sound_list).play()
            elif Character.stance == 1:
                rf_die_sound_list = Character.voices['RF_Die']
                random.choice(rf_die_sound_list).play()
            elif Character.stance == 2:
                hg_die_sound_list = Character.voices['HG_Die']
                random.choice(hg_die_sound_list).play()

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
                Character.bullet_SG = 8
                Character.bullet_RF = 4
                Character.bullet_HG = Character.max_bullet_HG

    @staticmethod
    def do(character):
        if get_time() - character.wait_time > 3:
            character.state_machine.add_event(('TIME_OUT', 0))
        if Character.stance == 0 or Character.stance == 1:
            character.frame = character.frame + 18.0 * 1.0 * game_framework.frame_time
        elif Character.stance == 2:
            character.frame = character.frame + 21.0 * 0.6 * game_framework.frame_time

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            if Character.stance == 0 and int(character.frame) <= 17.0:
                character.images['Die_SG'][int(character.frame)].composite_draw(0, '', character.sx - 48, character.y, 170, 170)
            elif Character.stance == 1 and int(character.frame) <= 17.0:
                character.images['Die_RF'][int(character.frame)].composite_draw(0, '', character.sx - 11, character.y, 170, 170)
            elif Character.stance == 2 and int(character.frame) <= 20.0:
                character.images['Die_HG'][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
        elif character.face_dir == -1:
            if Character.stance == 0 and int(character.frame) <= 17.0:
                character.images['Die_SG'][int(character.frame)].composite_draw(0, 'h', character.sx + 48, character.y, 170, 170)
            elif Character.stance == 1 and int(character.frame) <= 17.0:
                character.images['Die_RF'][int(character.frame)].composite_draw(0, 'h', character.sx + 11, character.y, 170, 170)
            elif Character.stance == 2 and int(character.frame) <= 20.0:
                character.images['Die_HG'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

class Dash:
    @staticmethod
    def enter(character, e):
        global Jump, jump_velocity, Fall, fall_velocity, d_pressed, a_pressed, attacking, s_pressed, w_pressed, Climb
        if use_dash(e):
            Jump = False
            jump_velocity = 9.0
            Fall = False
            fall_velocity = 0.0
            Climb = False
            character.wait_time = get_time()
            Character.hit_delay = 0.5
            if God:
                Character.dash_cooldown = 1
            else:
                Character.dash_cooldown = 6
            dasheffect = DashEffect(character.face_dir)
            game_world.add_object(dasheffect, 3)
            if Character.stance == 0:
                sq_attack_sound_list = Character.voices['SG_Attack']
                random.choice(sq_attack_sound_list).play()
            elif Character.stance == 1:
                rf_attack_sound_list = Character.voices['RF_Attack']
                random.choice(rf_attack_sound_list).play()
            elif Character.stance == 2:
                pass
            if not Attack:
                Character.frame = 0
                Character.attack_delay = 0
                character.attack_cool = 0
                character.attack_time = 0
        elif right_up(e):
            d_pressed = False
        elif left_up(e):
            a_pressed = False
        elif on_up(e):
            w_pressed = False
        elif under_up(e):
            s_pressed = False
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
            attacking = False
        elif rc_up(e):
            if Character.stance == 0 and Character.state == 1:
                Character.state = 0
                Character.speed = 3
            if Character.stance == 2 and Character.state == 1:
                Character.state = 0

    @staticmethod
    def exit(character, e):
        if time_out(e):
            if d_pressed or a_pressed:
                character.state_machine.add_event(('WALK', 0))

    @staticmethod
    def do(character):
        global Fall, Climb
        if Attack:
            if Character.stance == 0:
                character.frame = (character.frame + 15.0 * 0.8 * game_framework.frame_time) % 15
            elif Character.stance == 1:
                character.frame = (character.frame + 7.0 * 2.0 * game_framework.frame_time) % 7
            elif Character.stance == 2:
                character.frame = (character.frame + 5.0 * 3.0 * game_framework.frame_time) % 5

        character.x += 20 * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time

        for block in game_world.collision_pairs['server.character:ground'][1] + game_world.collision_pairs['server.character:wall'][1]:
            if screen_left - 15 <= block.x <= screen_right + 15:
                if game_world.collide(character, block):
                    character.x -= 20 * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time
                    Fall = True
                    Climb = False
                    character.state_machine.add_event(('TIME_OUT', 0))
                    return

        if get_time() - character.wait_time > 0.15:
            Fall = True
            Climb = False
            character.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(character):
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

class QSG:
    @staticmethod
    def enter(character, e):
        global d_pressed, a_pressed, attacking, s_pressed, w_pressed, Move, Jump
        if sg_q(e):
            Move = False
            character.frame = 0
            character.wait_time = get_time()
            character.attack_dir = character.face_dir

            qskillsgeffect = QskillSGEffect(character.attack_dir)
            game_world.add_object(qskillsgeffect, 3)

            sg_q_sound_list = Character.voices['SG_Q']
            random.choice(sg_q_sound_list).play()
        elif right_down(e):
            d_pressed = True
            character.face_dir = 1
        elif right_up(e):
            d_pressed = False
        elif left_down(e):
            a_pressed = True
            character.face_dir = -1
        elif left_up(e):
            a_pressed = False
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
            if Climb and not s_pressed:
                Move = False
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
            if Climb and not w_pressed:
                Move = False
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
            attacking = False
        elif jump(e) and not Jump and not Fall:
            Jump = True
            Character.jump_sound.play()
        elif take_hit(e):
            Character.hp = max(0, Character.hp - Character.damage)
            Character.hit_delay = 1.5
            if Character.hp == 0:
                Character.score -= 100
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

                qskillstunsg = QskillstunSG(character.attack_dir)
                game_world.add_object(qskillstunsg, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'qskillstunsg:{mob}', qskillstunsg, None)

                qskillsg = QskillSG(character.attack_dir)
                game_world.add_object(qskillsg, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'qskillsg:{mob}', qskillsg, None)

        if Attack:
            character.frame = (character.frame + 15.0 * 0.8 * game_framework.frame_time) % 15

        elif not Attack and get_time() - character.wait_time > 0.3:
            Character.state = 0
            character.frame = 0
            if God:
                Character.hour_of_judgment_cooldown = 1
            else:
                Character.hour_of_judgment_cooldown = 8
            if d_pressed or a_pressed:
                character.state_machine.add_event(('WALK', 0))
            else:
                character.state_machine.add_event(('IDLE', 0))

        if Climb:
            if w_pressed and not s_pressed:
                if not Move:
                    Move = True
                character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return
            elif s_pressed and not w_pressed:
                if not Move:
                    Move = True
                character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return

    @staticmethod
    def draw(character):
        if character.attack_dir == 1:
            character.images['Attack_SG'][int(character.frame)].composite_draw(0, '', character.sx, character.y,
                                                                          170, 170)
        elif character.attack_dir == -1:
            character.images['Attack_SG'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y,
                                                                          170, 170)

class ESG:
    @staticmethod
    def enter(character, e):
        global d_pressed, a_pressed, attacking, s_pressed, w_pressed, Move, Jump, chance, Attack
        if sg_e(e):
            Move = False
            chance = 0
            character.frame = 0
            character.wait_time = get_time()
            character.attack_dir = character.face_dir

            sg_e_sound_list = Character.voices['SG_E']
            random.choice(sg_e_sound_list).play()

            Attack = True
            character.attack_time = get_time()

            character.wait_time = get_time()

            normalsgeffect = NormalSGEffect(character.attack_dir)
            game_world.add_object(normalsgeffect, 3)

            normalsg1 = NormalSG1(character.attack_dir)
            game_world.add_object(normalsg1, 3)
            for mob in mob_group:
                game_world.add_collision_pairs(f'normalsg1:{mob}', normalsg1, None)

            normalsg2 = NormalSG2(character.attack_dir)
            game_world.add_object(normalsg2, 3)
            for mob in mob_group:
                game_world.add_collision_pairs(f'normalsg2:{mob}', normalsg2, None)

            normalsg3 = NormalSG3(character.attack_dir)
            game_world.add_object(normalsg3, 3)
            for mob in mob_group:
                game_world.add_collision_pairs(f'normalsg3:{mob}', normalsg3, None)

        elif right_down(e):
            d_pressed = True
        elif right_up(e):
            d_pressed = False
        elif left_down(e):
            a_pressed = True
        elif left_up(e):
            a_pressed = False
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
            if Climb and not s_pressed:
                Move = False
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
            if Climb and not w_pressed:
                Move = False
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
            attacking = False
        elif take_hit(e):
            Character.Rc_SG_sound.play()
            Character.hp = max(0, Character.hp - max(0, (Character.damage - Character.shield_def)))
            Character.hit_delay = 1.5
            if Character.hp == 0:
                Character.score -= 100
                Character.shotgun_rapid_fire_cooldown = 8
                character.state_machine.add_event(('DIE', 0))

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Move, Attack, chance

        if get_time() - character.wait_time > 0.4 and chance == 0:
            Character.E_SG_delay_sound.play()
            chance += 1

        elif get_time() - character.wait_time > 1 and chance == 1:
            if not Attack:
                Attack = True
                character.attack_time = get_time()
                chance += 1

                character.wait_time = get_time()

                normalsgeffect = NormalSGEffect(character.attack_dir)
                game_world.add_object(normalsgeffect, 3)

                normalsg1 = NormalSG1(character.attack_dir)
                game_world.add_object(normalsg1, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'normalsg1:{mob}', normalsg1, None)

                normalsg2 = NormalSG2(character.attack_dir)
                game_world.add_object(normalsg2, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'normalsg2:{mob}', normalsg2, None)

                normalsg3 = NormalSG3(character.attack_dir)
                game_world.add_object(normalsg3, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'normalsg3:{mob}', normalsg3, None)

        if get_time() - character.wait_time > 0.4 and chance == 2:
            Character.E_SG_delay_sound.play()
            chance += 1

        elif get_time() - character.wait_time > 1 and chance == 3:
            if not Attack:
                Attack = True
                character.attack_time = get_time()
                chance += 1

                character.wait_time = get_time()

                eskillsgeffect = EskillSGEffect(character.attack_dir)
                game_world.add_object(eskillsgeffect, 3)

                eskillsg1 = EskillSG1(character.attack_dir)
                game_world.add_object(eskillsg1, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'eskillsg1:{mob}', eskillsg1, None)

                eskillsg2 = EskillSG2(character.attack_dir)
                game_world.add_object(eskillsg2, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'eskillsg2:{mob}', eskillsg2, None)

                eskillsg3 = EskillSG3(character.attack_dir)
                game_world.add_object(eskillsg3, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'eskillsg3:{mob}', eskillsg3, None)

                sg_attack_sound_list = Character.voices['SG_Attack']
                random.choice(sg_attack_sound_list).play()

        if Attack:
            character.frame = (character.frame + 15.0 * 0.8 * game_framework.frame_time) % 15

        if not Attack and chance >= 4:
            Character.state = 0
            character.frame = 0
            if God:
                Character.shotgun_rapid_fire_cooldown = 1
            else:
                Character.shotgun_rapid_fire_cooldown = 8
            if d_pressed and not a_pressed:
                character.face_dir = 1
                character.attack_dir = 1
                character.state_machine.add_event(('WALK', 0))
            elif a_pressed and not d_pressed:
                character.face_dir = -1
                character.attack_dir = -1
                character.state_machine.add_event(('WALK', 0))
            elif d_pressed and a_pressed:
                character.attack_dir = character.face_dir
                character.state_machine.add_event(('WALK', 0))
            else:
                character.state_machine.add_event(('IDLE', 0))

    @staticmethod
    def draw(character):
        if character.attack_dir == 1:
            character.images['Attack_SG'][int(character.frame)].composite_draw(0, '', character.sx, character.y,
                                                                          170, 170)
        elif character.attack_dir == -1:
            character.images['Attack_SG'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y,
                                                                          170, 170)

class CSG:
    @staticmethod
    def enter(character, e):
        global d_pressed, a_pressed, attacking, s_pressed, w_pressed, Move, Jump, chance
        if sg_c(e):
            Move = False
            chance = 0
            character.frame = 0
            character.name = 'Ultimate_SG'
            sg_c_sound_list = Character.voices['SG_C']
            random.choice(sg_c_sound_list).play()
        elif right_down(e):
            d_pressed = True
        elif right_up(e):
            d_pressed = False
        elif left_down(e):
            a_pressed = True
        elif left_up(e):
            a_pressed = False
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
            if Climb and not s_pressed:
                Move = False
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
            if Climb and not w_pressed:
                Move = False
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
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

                cskillsgeffect = CskillSGEffect(character.face_dir)
                game_world.add_object(cskillsgeffect, 0)

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
                if d_pressed and not a_pressed:
                    character.face_dir = 1
                    character.attack_dir = 1
                    character.state_machine.add_event(('WALK', 0))
                elif a_pressed and not d_pressed:
                    character.face_dir = -1
                    character.attack_dir = -1
                    character.state_machine.add_event(('WALK', 0))
                elif d_pressed and a_pressed:
                    character.attack_dir = character.face_dir
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
        global d_pressed, a_pressed, attacking, Reload_RF, rrf, s_pressed, w_pressed
        if rf_reload(e) and not Reload_RF:
            Reload_RF = True
            character.wait_time = get_time()
            rrf = False
            character.name = 'Attack_RF'
            character.frame = 0
        elif right_up(e):
            d_pressed = False
        elif left_up(e):
            a_pressed = False
        elif on_up(e):
            w_pressed = False
        elif under_up(e):
            s_pressed = False
        elif lc_up(e):
            attacking = False

    @staticmethod
    def exit(character, e):
        global Fall, Reload_RF
        if time_out(e):
            Fall = True
            Reload_RF = False
            Character.bullet_RF = 4
            Character.hit_delay = 0.5
            if d_pressed or a_pressed:
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
                jump_velocity = 6.0
                Fall = False
                fall_velocity = 0.0
                rrf = True
                character.frame = 1
                reloadrf = ReloadRF(character.face_dir)
                game_world.add_object(reloadrf, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'reloadrf:{mob}', reloadrf, None)
                rf_reload_sound_list = Character.voices['RF_Reload']
                random.choice(rf_reload_sound_list).play()
            character.x -= 8 * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time

        for block in game_world.collision_pairs['server.character:ground'][1] + game_world.collision_pairs['server.character:wall'][1]:
            if screen_left - 15 <= block.x <= screen_right + 15:
                if game_world.collide(character, block):
                    character.x += 8 * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time
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
        global d_pressed, a_pressed, attacking, Reload_RF, rrf, s_pressed, w_pressed
        if rf_reload_s(e) and not Reload_RF:
            Reload_RF = True
            character.wait_time = get_time()
            rrf = False
            character.name = 'Attack_RF'
            character.frame = 0
        elif right_up(e):
            d_pressed = False
        elif left_up(e):
            a_pressed = False
        elif on_up(e):
            w_pressed = False
        elif under_up(e):
            s_pressed = False
        elif lc_up(e):
            attacking = False

    @staticmethod
    def exit(character, e):
        global Fall, Reload_RF
        if time_out(e):
            Fall = True
            Reload_RF = False
            Character.bullet_RF = 4
            Character.hit_delay = 0.5
            if d_pressed or a_pressed:
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
                jump_velocity = 6.0
                Fall = False
                fall_velocity = 0.0
                rrf = True
                character.frame = 1
                reloadrf = ReloadRF(character.face_dir)
                game_world.add_object(reloadrf, 3)
                rf_reload_sound_list = Character.voices['RF_Reload']
                random.choice(rf_reload_sound_list).play()
                for mob in mob_group:
                    game_world.add_collision_pairs(f'reloadrf:{mob}', reloadrf, None)

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            character.images[character.name][int(character.frame)].composite_draw(0, '', character.sx, character.y, 170, 170)
        elif character.face_dir == -1:
            character.images[character.name][int(character.frame)].composite_draw(0, 'h', character.sx, character.y, 170, 170)

class RcRF:
    @staticmethod
    def enter(character, e):
        global d_pressed, a_pressed, attacking, s_pressed, w_pressed, Move
        if rf_rc(e):
            Move = False
            character.wait_time = get_time()
            Character.target_down_bullet = Character.target_down_max
            character.frame = clamp(0, character.frame, 13)
            Character.Rc_RF_sound.play()
            rf_rc_sound_list = Character.voices['RF_Rc']
            random.choice(rf_rc_sound_list).play()
        elif right_down(e):
            d_pressed = True
            character.face_dir = 1
        elif right_up(e):
            d_pressed = False
        elif left_down(e):
            a_pressed = True
            character.face_dir = -1
        elif left_up(e):
            a_pressed = False
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
            if Climb and not s_pressed:
                Move = False
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
            if Climb and not w_pressed:
                Move = False
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
            attacking = False
        elif dash(e) and Character.dash_cooldown == 0:
            Character.state = 0
            if God:
                Character.target_down_cooldown = 1
            else:
                Character.target_down_cooldown = 45
            Character.target_down_size = 0
            Character.hit_delay = 1
            character.state_machine.add_event(('USE_DASH', 0))
        elif take_hit(e):
            Character.hp = max(0, Character.hp - Character.damage)
            Character.hit_delay = 1.5
            if Character.hp == 0:
                Character.score -= 100
                Character.target_down_cooldown = 45
                Character.target_down_size = 0
                character.state_machine.add_event(('DIE', 0))

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Move
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
                if d_pressed or a_pressed:
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))
        else:
            character.frame = (character.frame + 14.0 * 1.5 * game_framework.frame_time) % 14

        if Fall or Jump:
            if Move:
                Move = False

        if Climb:
            if w_pressed and not s_pressed:
                if not Move:
                    Move = True
                character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return
            elif s_pressed and not w_pressed:
                if not Move:
                    Move = True
                character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
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
                character.images['Idle_RF'][int(character.frame)].composite_draw(0, '', character.sx, character.y,
                                                                                   170, 170)
            elif character.face_dir == -1:
                character.images['Idle_RF'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y,
                                                                                   170, 170)

class QRF:
    @staticmethod
    def enter(character, e):
        global d_pressed, a_pressed, attacking, s_pressed, w_pressed, Move, Jump
        if rf_q(e):
            Move = False
            character.frame = 0
            character.wait_time = get_time()
            character.attack_dir = character.face_dir
            rf_q_sound_list = Character.voices['RF_Q']
            random.choice(rf_q_sound_list).play()
        elif right_down(e):
            d_pressed = True
            character.face_dir = 1
            character.attack_dir = 1
        elif right_up(e):
            d_pressed = False
        elif left_down(e):
            a_pressed = True
            character.face_dir = -1
            character.attack_dir = -1
        elif left_up(e):
            a_pressed = False
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
            if Climb and not s_pressed:
                Move = False
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
            if Climb and not w_pressed:
                Move = False
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
            attacking = False
        elif take_hit(e):
            Character.hp = max(0, Character.hp - Character.damage)
            Character.hit_delay = 1.5
            if Character.hp == 0:
                Character.score -= 100
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

                qskillrfeffect = QskillRFEffect(character.face_dir)
                game_world.add_object(qskillrfeffect, 3)

                qskillrf = QskillRF(character.face_dir)
                game_world.add_object(qskillrf, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'qskillrf:{mob}', qskillrf, None)

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
            if d_pressed or a_pressed:
                character.state_machine.add_event(('WALK', 0))
            else:
                character.state_machine.add_event(('IDLE', 0))

        if Climb:
            if w_pressed and not s_pressed:
                if not Move:
                    Move = True
                character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return
            elif s_pressed and not w_pressed:
                if not Move:
                    Move = True
                character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
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

class ERF:
    @staticmethod
    def enter(character, e):
        global d_pressed, a_pressed, attacking, s_pressed, w_pressed, Move, Jump, chance
        if rf_e(e):
            Move = False
            chance = 0
            character.frame = 0
            character.wait_time = get_time()
            character.attack_dir = character.face_dir
            Character.E_RF_sound.play()
        elif right_down(e):
            d_pressed = True
            character.face_dir = 1
            character.attack_dir = 1
        elif right_up(e):
            d_pressed = False
        elif left_down(e):
            a_pressed = True
            character.face_dir = -1
            character.attack_dir = -1
        elif left_up(e):
            a_pressed = False
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
            if Climb and not s_pressed:
                Move = False
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
            if Climb and not w_pressed:
                Move = False
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
            attacking = False
        elif take_hit(e):
            Character.hp = max(0, Character.hp - Character.damage)
            Character.hit_delay = 1.5
            if Character.hp == 0:
                Character.score -= 100
                chance = 0
                Character.focus_shot_cooldown = 30
                character.state_machine.add_event(('DIE', 0))

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Move, Attack, chance
        if get_time() - character.wait_time > 0.3 and chance <= 2:
            if not Attack:
                Attack = True
                character.attack_time = get_time()
                chance += 1

                normalrfeffect = NormalRFEffect(character.face_dir)
                game_world.add_object(normalrfeffect, 3)

                normalrf = NormalRF(character.face_dir)
                game_world.add_object(normalrf, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'normalrf:{mob}', normalrf, None)

                rfeffect = RFEffect(character.face_dir)
                game_world.add_object(rfeffect, 3)

                if chance == 1:
                    rf_attack_sound_list = Character.voices['RF_Attack']
                    random.choice(rf_attack_sound_list).play()

        if get_time() - character.wait_time > 2.0 and chance == 3:
            if not Attack:
                Attack = True
                character.attack_time = get_time()
                chance += 1

                normalrfspeffect = NormalRFSPEffect(character.face_dir)
                game_world.add_object(normalrfspeffect, 3)

                normalrfsp = NormalRFSP(character.face_dir)
                game_world.add_object(normalrfsp, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'normalrfsp:{mob}', normalrfsp, None)

                rfeffect = RFEffect(character.face_dir)
                game_world.add_object(rfeffect, 3)

                rf_attack_sound_list = Character.voices['RF_Attack']
                random.choice(rf_attack_sound_list).play()

        if Attack:
            character.frame = (character.frame + 7.0 * 2.0 * game_framework.frame_time) % 7

        if not Attack and chance >= 4:
            Character.state = 0
            character.frame = 0
            if God:
                Character.focus_shot_cooldown = 1
            else:
                Character.focus_shot_cooldown = 30
            if d_pressed or a_pressed:
                character.state_machine.add_event(('WALK', 0))
            else:
                character.state_machine.add_event(('IDLE', 0))

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            character.images['Attack_RF'][int(character.frame)].composite_draw(0, '', character.sx, character.y,
                                                                          170, 170)
        elif character.face_dir == -1:
            character.images['Attack_RF'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y,
                                                                          170, 170)

class CRF:
    @staticmethod
    def enter(character, e):
        global d_pressed, a_pressed, attacking, s_pressed, w_pressed, Move, Jump
        if rf_c(e):
            Move = False
            character.frame = 0
            character.wait_time = get_time()
            Character.C_RF_start_sound.play()
            rf_c_sound_list = Character.voices['RF_C']
            random.choice(rf_c_sound_list).play()
        elif right_down(e):
            d_pressed = True
        elif right_up(e):
            d_pressed = False
        elif left_down(e):
            a_pressed = True
        elif left_up(e):
            a_pressed = False
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
            if Climb and not s_pressed:
                Move = False
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
            if Climb and not w_pressed:
                Move = False
        elif lc_up(e):
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

            cskillrf = CskillRF()
            game_world.add_object(cskillrf, 3)

            if d_pressed and not a_pressed:
                character.face_dir = 1
                character.attack_dir = 1
                character.state_machine.add_event(('WALK', 0))
            elif a_pressed and not d_pressed:
                character.face_dir = -1
                character.attack_dir = -1
                character.state_machine.add_event(('WALK', 0))
            elif d_pressed and a_pressed:
                character.attack_dir = character.face_dir
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

class EHG:
    @staticmethod
    def enter(character, e):
        global d_pressed, a_pressed, attacking, s_pressed, w_pressed, Move, Jump
        if hg_e(e):
            Move = False
            character.wait_time = get_time()
            character.frame = 0
            hg_e_sound_list = Character.voices['HG_E']
            random.choice(hg_e_sound_list).play()
        elif right_down(e):
            d_pressed = True
            character.face_dir = 1
            character.attack_dir = 1
        elif right_up(e):
            d_pressed = False
        elif left_down(e):
            a_pressed = True
            character.face_dir = -1
            character.attack_dir = -1
        elif left_up(e):
            a_pressed = False
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
            if Climb and not s_pressed:
                Move = False
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
            if Climb and not w_pressed:
                Move = False
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
            attacking = False
        elif jump(e) and not Jump and not Fall:
            Jump = True
            Character.jump_sound.play()
        elif dash(e) and Character.dash_cooldown == 0:
            Character.state = 0
            if God:
                Character.bullet_rain_cooldown = 1
            elif Character.upgrade >= 4:
                Character.bullet_rain_cooldown = 3
            else:
                Character.bullet_rain_cooldown = 6
            Character.hit_delay = 1
            character.state_machine.add_event(('USE_DASH', 0))
        elif q_down(e):
            if Character.at02_grenade_cooldown == 0 and Character.bullet_HG > 0 and (God or Character.score >= 200):
                Character.hit_delay = 0.5
                Character.bullet_HG -= 1

                qskillhg = QskillHG(character.face_dir)
                game_world.add_object(qskillhg, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'qskillhg:{mob}', qskillhg, None)

                if God:
                    Character.at02_grenade_cooldown = 1
                else:
                    Character.at02_grenade_cooldown = 4

                if Character.bullet_HG == 0:
                    Character.state = 0
                    character.frame = 0
                    if God:
                        Character.bullet_rain_cooldown = 1
                    elif Character.upgrade >= 4:
                        Character.bullet_rain_cooldown = 3
                    else:
                        Character.bullet_rain_cooldown = 6
                    if d_pressed or a_pressed:
                        character.state_machine.add_event(('WALK', 0))
                    else:
                        character.state_machine.add_event(('IDLE', 0))
        elif e_down(e):
            Character.state = 0
            character.frame = 0
            if God:
                Character.bullet_rain_cooldown = 1
            elif Character.upgrade >= 4:
                Character.bullet_rain_cooldown = 3
            else:
                Character.bullet_rain_cooldown = 6
            if d_pressed or a_pressed:
                character.state_machine.add_event(('WALK', 0))
            else:
                character.state_machine.add_event(('IDLE', 0))
        elif take_hit(e):
            Character.hp = max(0, Character.hp - Character.damage)
            Character.hit_delay = 1.5
            if Character.hp == 0:
                Character.score -= 100
                if Character.upgrade >= 4:
                    Character.bullet_rain_cooldown = 3
                else:
                    Character.bullet_rain_cooldown = 6
                character.state_machine.add_event(('DIE', 0))

    @staticmethod
    def exit(character, e):
        pass

    @staticmethod
    def do(character):
        global Move
        character.frame = (character.frame + 7.0 * 3.0 * game_framework.frame_time) % 7

        if get_time() - character.wait_time > 0.2 and Character.bullet_HG > 0:
            eskillhg = EskillHG(character.face_dir)
            game_world.add_object(eskillhg, 3)
            for mob in mob_group:
                game_world.add_collision_pairs(f'eskillhg:{mob}', eskillhg, None)

            hgeffect = HGEffect(character.face_dir)
            game_world.add_object(hgeffect, 3)

            character.wait_time = get_time()
            Character.bullet_HG -= 1
            if Character.bullet_HG == 0:
                Character.state = 0
                character.frame = 0
                if God:
                    Character.bullet_rain_cooldown = 1
                elif Character.upgrade >= 4:
                    Character.bullet_rain_cooldown = 3
                else:
                    Character.bullet_rain_cooldown = 6
                if d_pressed or a_pressed:
                    character.state_machine.add_event(('WALK', 0))
                else:
                    character.state_machine.add_event(('IDLE', 0))

        if Climb:
            if w_pressed and not s_pressed:
                if not Move:
                    Move = True
                character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return
            elif s_pressed and not w_pressed:
                if not Move:
                    Move = True
                character.y -= Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y += Character.speed * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return

    @staticmethod
    def draw(character):
        if character.face_dir == 1:
            character.images['E_HG'][int(character.frame)].composite_draw(0, '', character.sx, character.y,
                                                                          170, 170)
        elif character.face_dir == -1:
            character.images['E_HG'][int(character.frame)].composite_draw(0, 'h', character.sx, character.y,
                                                                          170, 170)

class CHG:
    trails = []

    @staticmethod
    def enter(character, e):
        global d_pressed, a_pressed, attacking, s_pressed, w_pressed, Move, Jump, count
        if hg_c(e):
            Move = False
            count = 0
            character.frame = 0
            CHG.trails.clear()
            hg_c_sound_list = Character.voices['HG_C']
            random.choice(hg_c_sound_list).play()
            Character.C_HG_sound.play()
            character.wait_time = get_time()
            character.trail_time = get_time()
            character.effect_time = get_time()

            cskillhg = CskillHG()
            game_world.add_object(cskillhg, 3)
            for mob in mob_group:
                game_world.add_collision_pairs(f'cskillhg:{mob}', cskillhg, None)
        elif right_down(e):
            d_pressed = True
            character.face_dir = 1
        elif right_up(e):
            d_pressed = False
            if a_pressed:
                character.face_dir = -1
        elif left_down(e):
            a_pressed = True
            character.face_dir = -1
        elif left_up(e):
            a_pressed = False
            if d_pressed:
                character.face_dir = 1
        elif on_down(e):
            w_pressed = True
        elif on_up(e):
            w_pressed = False
            if Climb and not s_pressed:
                Move = False
        elif under_down(e):
            s_pressed = True
        elif under_up(e):
            s_pressed = False
            if Climb and not w_pressed:
                Move = False
        elif lc_down(e):
            attacking = True
        elif lc_up(e):
            attacking = False
        elif jump(e) and not Jump and not Fall:
            Jump = True
            Character.jump_sound.play()
        elif q_down(e):
            if Character.at02_grenade_cooldown == 0 and Character.bullet_HG > 0 and (God or Character.score >= 200):
                Character.hit_delay = 0.5
                Character.bullet_HG -= 1

                qskillhg = QskillHG(character.face_dir)
                game_world.add_object(qskillhg, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'qskillhg:{mob}', qskillhg, None)

                if God:
                    Character.at02_grenade_cooldown = 1
                else:
                    Character.at02_grenade_cooldown = 4

    @staticmethod
    def exit(character, e):
        if time_out(e):
            if d_pressed or a_pressed:
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
            cskillhg = CskillHG()
            game_world.add_object(cskillhg, 3)
            for mob in mob_group:
                game_world.add_collision_pairs(f'cskillhg:{mob}', cskillhg, None)
            count += 1

        elif get_time() - character.wait_time > 1.0 and count == 0:
            cskillhg = CskillHG()
            game_world.add_object(cskillhg, 3)
            for mob in mob_group:
                game_world.add_collision_pairs(f'cskillhg:{mob}', cskillhg, None)
            count += 1

        character.frame = (character.frame + 12.0 * 2.0 * game_framework.frame_time) % 12

        if get_time() - character.trail_time > 0.05:
            CHG.add_trail(character)
            character.trail_time = get_time()

        if get_time() - character.effect_time > 0.1:
            random_angle = random.uniform(-3.141592, 3.141592)
            character.effect_time = get_time()

            for _ in range(4):
                cskillhgeffect = CskillHGEffect()
                game_world.add_object(cskillhgeffect, 3)

        if Climb:
            if w_pressed and not s_pressed:
                character.y += 2 * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y -= 2 * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return
            elif s_pressed and not w_pressed:
                character.y -= 2 * RUN_SPEED_PPS * game_framework.frame_time / 2
                for block in game_world.collision_pairs['server.character:ground'][1]:
                    if screen_left - 15 <= block.x <= screen_right + 15:
                        if game_world.collide(character, block):
                            character.y += 2 * RUN_SPEED_PPS * game_framework.frame_time / 2
                            return

        character.x += 2 * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time

        for block in game_world.collision_pairs['server.character:ground'][1] + \
                     game_world.collision_pairs['server.character:wall'][1]:
            if screen_left - 15 <= block.x <= screen_right + 15:
                if game_world.collide(character, block):
                    character.x -= 2 * character.face_dir * RUN_SPEED_PPS * game_framework.frame_time
                    return

        ground_objects = game_world.collision_pairs['server.character:ground'][1]
        for block in ground_objects:
            if screen_left - 15 <= block.x <= screen_right + 15:
                if game_world.collide_ad(character, block, ground_objects):
                    Fall = True
                    return

        for block in game_world.collision_pairs['server.character:ladder'][1]:
            if screen_left - 15 <= block.x <= screen_right + 15:
                if game_world.collide_ladder(character, block):
                    Fall = True
                    Climb = False
                    return

    @staticmethod
    def draw(character):
        screen_left = server.background.window_left

        for trail in CHG.trails:
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
        CHG.trails.append({
            'x': character.x,
            'y': character.y,
            'frame': character.frame,
            'face_dir': character.face_dir,
            'time': get_time()
        })
        if len(CHG.trails) > 2:
            CHG.trails.pop(0)

animation_names = ['Idle_SG', 'Walk_SG', 'Hit_SG', 'Die_SG', 'Attack_SG', 'Reload_SG', 'Rc_SG', 'Ultimate_SG', 'Ultimate_wait_SG',
                   'Idle_RF', 'Walk_RF', 'Hit_RF', 'Die_RF', 'Attack_RF', 'Ultimate_RF',
                   'Idle_HG', 'Walk_HG', 'Hit_HG', 'Die_HG', 'Attack_HG', 'Reload_HG', 'E_HG', 'Ultimate_HG']

character_voices = ['SG_Hit', 'SG_Die', 'SG_Attack', 'SG_Reload', 'SG_Rc', 'SG_Q', 'SG_E', 'SG_C', 'SG_Portal',
                    'RF_Hit', 'RF_Die', 'RF_Attack', 'RF_Reload', 'RF_Rc', 'RF_Q', 'RF_C', 'RF_Portal',
                    'HG_Hit', 'HG_Die', 'HG_Attack', 'HG_Reload', 'HG_Q', 'HG_E', 'HG_C', 'HG_Portal']

class Character:
    images = None
    voices = None
    jump_sound = None
    fall_sound = None
    sg_stance_sound = None
    rf_stance_sound = None
    hg_stance_sound = None
    Rc_SG_sound = None
    Rc_SG_counter_sound = None
    Rc_RF_sound = None
    Reload_SG_sound = None
    Reload_HG_sound = None
    E_SG_delay_sound = None
    E_RF_sound = None
    C_RF_start_sound = None
    C_HG_sound = None
    stance = 0
    state = 0
    speed = 3
    hp = 20
    max_hp = 20 # 최대 hp 30
    score = 0
    damage = 0
    upgrade = 0
    medal = 0
    bullet_SG = 8
    bullet_RF = 4
    target_down_max = 2 # 타겟 다운 총알 2 / 3 (+1)
    target_down_bullet = target_down_max
    target_down_size = 0 # 타겟 다운 범위 3 / 4 (+3)
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
    dash_cooldown = 0 # 대쉬 쿨타임 6초
    hour_of_judgment_cooldown = 0 # 심판의 시간 쿨타임 8초
    shotgun_rapid_fire_cooldown = 0  # 샷건 연사 쿨타임 8초
    last_request_cooldown = 0 # 최후의 만찬 쿨타임 40초
    target_down_cooldown = 0  # 타겟 다운 쿨타임 45초
    perfect_shot_cooldown = 0 # 퍼펙트 샷 쿨타임 15초
    focus_shot_cooldown = 0 # 포커스 샷 쿨타임 30초
    catastrophe_cooldown = 0 # 대재앙 쿨타임 120초
    catastrophe_duration = 0 # 대재앙 지속 시간 10초
    dexterous_shot_cooldown = 0 # 민첩한 사격 쿨타임 2초 / 1초 (+2)
    at02_grenade_cooldown = 0 # AT02 유탄 쿨타임 4초
    bullet_rain_cooldown = 0 # 불렛 레인 쿨타임 6초 / 3초 (+4)
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
                elif name == 'Rc_SG':
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
                    Character.images[name] = [load_image("./GSH18Mod/" + name + " (%d)" % i + ".png") for i in range(1, 11 + 1)]
                elif name == 'Walk_HG':
                    Character.images[name] = [load_image("./GSH18Mod/" + name + " (%d)" % i + ".png") for i in range(1, 6 + 1)]
                elif name == 'Hit_HG':
                    Character.images[name] = [load_image("./GSH18Mod/" + name + " (1)" + ".png")]
                elif name == 'Die_HG':
                    Character.images[name] = [load_image("./GSH18Mod/" + name + " (%d)" % i + ".png") for i in range(1, 21 + 1)]
                elif name == 'Attack_HG':
                    Character.images[name] = [load_image("./GSH18Mod/" + name + " (%d)" % i + ".png") for i in range(1, 5 + 1)]
                elif name == 'Reload_HG':
                    Character.images[name] = [load_image("./GSH18Mod/" + name + " (%d)" % i + ".png") for i in range(1, 8 + 1)]
                elif name == 'E_HG':
                    Character.images[name] = [load_image("./GSH18Mod/" + name + " (%d)" % i + ".png") for i in range(1, 7 + 1)]
                elif name == 'Ultimate_HG':
                    Character.images[name] = [load_image("./GSH18Mod/" + name + " (%d)" % i + ".png") for i in range(1, 12 + 1)]

    def load_voices(self):
        if Character.voices == None:
            Character.voices = {}
            for voice in character_voices:
                Character.voices[voice] = []
                if voice == 'SG_Hit':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_Die':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(48)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_Attack':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_Reload':
                    sound = load_wav("./Voice/SG/" + voice + " (1)" + ".mp3")
                    sound.set_volume(24)
                    Character.voices[voice].append(sound)
                elif voice == 'SG_Rc':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_Q':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_E':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_C':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/SG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'SG_Portal':
                    sound = load_wav("./Voice/SG/" + voice + " (1)" + ".mp3")
                    sound.set_volume(24)
                    Character.voices[voice].append(sound)

                elif voice == 'RF_Hit':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(18)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Die':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(36)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Attack':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(18)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Reload':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Rc':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Q':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_C':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/RF/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'RF_Portal':
                    sound = load_wav("./Voice/RF/" + voice + " (1)" + ".mp3")
                    sound.set_volume(24)
                    Character.voices[voice].append(sound)

                elif voice == 'HG_Hit':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/HG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'HG_Die':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/HG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(48)
                        Character.voices[voice].append(sound)
                elif voice == 'HG_Attack':
                    for i in range(1, 5 + 1):
                        sound = load_wav("./Voice/HG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'HG_Reload':
                    sound = load_wav("./Voice/HG/" + voice + " (1)" + ".mp3")
                    sound.set_volume(24)
                    Character.voices[voice].append(sound)
                elif voice == 'HG_Q':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/HG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'HG_E':
                    for i in range(1, 2 + 1):
                        sound = load_wav("./Voice/HG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'HG_C':
                    for i in range(1, 3 + 1):
                        sound = load_wav("./Voice/HG/" + voice + " (%d)" % i + ".mp3")
                        sound.set_volume(24)
                        Character.voices[voice].append(sound)
                elif voice == 'HG_Portal':
                    sound = load_wav("./Voice/HG/" + voice + " (1)" + ".mp3")
                    sound.set_volume(24)
                    Character.voices[voice].append(sound)

    def __init__(self):
        self.x, self.y = 34.0, 170.0
        self.face_dir = 1
        self.attack_dir = 1
        self.frame = 0
        self.sx = 0
        self.mouse = False
        self.load_images()
        self.load_voices()
        self.name = ''
        self.one = 0
        self.hit_cool = 0
        self.attack_cool = 0
        self.attack_time = 0
        self.catastrophe_time = 0
        self.Lshift_cool = 0
        self.Q_SG_cool = 0
        self.E_SG_cool = 0
        self.C_SG_cool = 0
        self.Rc_RF_cool = 0
        self.Q_RF_cool = 0
        self.E_RF_cool = 0
        self.C_RF_cool = 0
        self.Rc_HG_cool = 0
        self.Q_HG_cool = 0
        self.E_HG_cool = 0
        self.C_HG_cool = 0
        self.state_machine = StateMachine(self)
        self.state_machine.start(Idle)
        self.state_machine.set_transitions(
            {
                Idle: {
                    right_down: Walk, left_down: Walk, left_up: Idle, right_up: Idle, change_stance_z: Idle, change_stance_x: Idle,
                    walk: Walk, jump: Idle, rc_down: Idle, rc_up: Idle, dash: Idle, use_dash: Dash, lc_down: Idle, lc_up: Idle,
                    reload: Idle, rf_reload: RRF, idle: Idle, under_down: Idle, under_up: Idle, rf_reload_s: RsRF, rf_rc: RcRF,
                    on_up: Idle, on_down: Idle, q_down: Idle, e_down: Idle, c_down: Idle, sg_e: ESG, sg_c: CSG,
                    take_hit: Hit, die: Die, sg_q: QSG, hg_e: EHG, rf_e: ERF, rf_q: QRF, rf_c: CRF, hg_c: CHG,
                    temp_bullet: Idle, temp_god: Idle, temp_up: Idle, temp_down: Idle, temp_medal: Idle,
                },
                Walk: {
                    right_down: Walk, left_down: Walk, right_up: Walk, left_up: Walk, change_stance_z: Walk, change_stance_x: Walk,
                    idle: Idle, jump: Walk, rc_down: Walk, rc_up: Walk, dash: Walk, use_dash: Dash, lc_down: Walk, lc_up: Walk,
                    reload: Walk, rf_reload: RRF, walk: Walk, under_down: Walk, under_up: Walk, rf_reload_s: RsRF, rf_rc: RcRF,
                    on_up: Walk, on_down: Walk, q_down: Walk, e_down: Walk, c_down: Walk, sg_e: ESG, sg_c: CSG,
                    take_hit: Hit, die: Die, sg_q: QSG, hg_e: EHG, rf_e: ERF, rf_q: QRF, rf_c: CRF, hg_c: CHG,
                    temp_bullet: Walk, temp_god: Walk, temp_up: Walk, temp_down: Walk, temp_medal: Walk,
                },
                Hit: {
                    right_down: Hit, left_down: Hit, right_up: Hit, left_up: Hit, on_down: Hit, under_down: Hit, under_up: Hit,
                    rc_up: Hit, lc_down: Hit, lc_up: Hit,
                    time_out: Idle, walk: Walk, die: Die
                },
                Die: {
                    time_out: Idle
                },
                Dash: {
                    left_up: Dash, right_up: Dash, on_up: Dash, under_up: Dash, rc_up: Dash, lc_down: Dash, lc_up: Dash,
                    time_out: Idle, walk: Walk
                },
                QSG: {
                    right_down: QSG, left_down: QSG, left_up: QSG, right_up: QSG, on_up: QSG, under_up: QSG,
                    lc_down: QSG, lc_up: QSG, jump: QSG,
                    under_down: QSG, on_down: QSG, idle: Idle, walk: Walk, take_hit: QSG,
                    die: Die,
                },
                ESG: {
                    right_down: ESG, left_down: ESG, left_up: ESG, right_up: ESG, on_up: ESG, under_up: ESG,
                    lc_down: ESG, lc_up: ESG,
                    under_down: ESG, on_down: ESG, idle: Idle, walk: Walk, take_hit: ESG,
                    die: Die,
                },
                CSG: {
                    right_down: CSG, left_down: CSG, left_up: CSG, right_up: CSG, on_up: CSG, under_up: CSG,
                    lc_down: CSG, lc_up: CSG,
                    under_down: CSG, on_down: CSG, idle: Idle, walk: Walk,
                },
                RRF: {
                    left_up: RRF, right_up: RRF, on_up: RRF, under_up: RRF, lc_up: RRF,
                    time_out: Idle, walk: Walk
                },
                RsRF: {
                    left_up: RsRF, right_up: RsRF, on_up: RsRF, under_up: RsRF, lc_up: RsRF,
                    time_out: Idle, walk: Walk
                },
                RcRF: {
                    right_down: RcRF, left_down: RcRF, left_up: RcRF, right_up: RcRF, on_up: RcRF, under_up: RcRF, lc_down: RcRF, lc_up: RcRF,
                    under_down: RcRF, on_down: RcRF,  dash: RcRF, use_dash: Dash, idle: Idle, walk: Walk, take_hit: RcRF, die: Die,
                },
                QRF: {
                    right_down: QRF, left_down: QRF, left_up: QRF, right_up: QRF, on_up: QRF, under_up: QRF, lc_down: QRF, lc_up: QRF,
                    under_down: QRF, on_down: QRF, idle: Idle, walk: Walk, take_hit: QRF, die: Die,
                },
                ERF: {
                    right_down: ERF, left_down: ERF, left_up: ERF, right_up: ERF, on_up: ERF, under_up: ERF, lc_down: ERF, lc_up: ERF,
                     under_down: ERF, on_down: ERF, idle: Idle, walk: Walk, take_hit: ERF, die: Die,
                },
                CRF: {
                    right_down: CRF, left_down: CRF, left_up: CRF, right_up: CRF, on_up: CRF, under_up: CRF, lc_down: CRF, lc_up: CRF,
                    under_down: CRF, on_down: CRF, idle: Idle, walk: Walk,
                },
                EHG: {
                    right_down: EHG, left_down: EHG, left_up: EHG, right_up: EHG, on_up: EHG, under_up: EHG,
                    lc_down: EHG, lc_up: EHG, jump: EHG, e_down: EHG, q_down: EHG,
                    under_down: EHG, on_down: EHG, dash: EHG, use_dash: Dash, idle: Idle, walk: Walk, take_hit: EHG,
                    die: Die,
                },
                CHG: {
                    right_down: CHG, left_down: CHG, left_up: CHG, right_up: CHG, on_up: CHG, under_up: CHG,
                    lc_down: CHG, lc_up: CHG, jump: CHG, time_out: Idle, q_down: CHG,
                    under_down: CHG, on_down: CHG, idle: Idle, walk: Walk,
                },
            }
        )

        if Character.jump_sound == None:
            Character.jump_sound = load_wav("./Sound/Jump.mp3")
            Character.fall_sound = load_wav("./Sound/Fall.mp3")
            Character.sg_stance_sound = load_wav("./Sound/change_SG.mp3")
            Character.rf_stance_sound = load_wav("./Sound/change_RF.mp3")
            Character.hg_stance_sound = load_wav("./Sound/change_HG.mp3")
            Character.Rc_SG_sound = load_wav("./Sound/Rc_SG.mp3")
            Character.Rc_SG_counter_sound = load_wav("./Sound/Rc_SG_counter.ogg")
            Character.Rc_RF_sound = load_wav("./Sound/Rc_RF.mp3")
            Character.Reload_SG_sound = load_wav("./Sound/Reload_SG.mp3")
            Character.Reload_HG_sound = load_wav("./Sound/Reload_HG.mp3")
            Character.E_SG_delay_sound = load_wav("./Sound/E_SG_delay.mp3")
            Character.E_RF_sound = load_wav("./Sound/E_RF.mp3")
            Character.C_RF_start_sound = load_wav("./Sound/C_RF_start.ogg")
            Character.C_HG_sound = load_wav("./Sound/C_HG.mp3")
            Character.jump_sound.set_volume(80)
            Character.fall_sound.set_volume(48)
            Character.sg_stance_sound.set_volume(64)
            Character.rf_stance_sound.set_volume(64)
            Character.hg_stance_sound.set_volume(64)
            Character.Rc_SG_sound.set_volume(32)
            Character.Rc_SG_counter_sound.set_volume(32)
            Character.Rc_RF_sound.set_volume(80)
            Character.Reload_SG_sound.set_volume(80)
            Character.Reload_HG_sound.set_volume(80)
            Character.E_SG_delay_sound.set_volume(48)
            Character.E_RF_sound.set_volume(96)
            Character.C_RF_start_sound.set_volume(32)
            Character.C_HG_sound.set_volume(32)

    def update(self):
        global Jump, jump_velocity, Fall, fall_velocity, Attack, Move, screen_left, screen_right, Reload_SG, Reload_HG, mouse_x
        global rchg, catastrophe
        self.state_machine.update()
        self.x = clamp(17.0, self.x, server.background.w - 17.0)
        self.sx = self.x - server.background.window_left
        screen_left = server.background.window_left
        screen_right = server.background.window_left + 1600

        if Jump:
            if not Move:
                Move = True
            self.y += jump_velocity * RUN_SPEED_PPS * game_framework.frame_time
            jump_velocity -= gravity * RUN_SPEED_PPS * game_framework.frame_time
            if jump_velocity <= 0:
                Jump = False
                Fall = True
                jump_velocity = 9.0

        if Fall:
            self.y -= fall_velocity * RUN_SPEED_PPS * game_framework.frame_time
            fall_velocity += gravity * RUN_SPEED_PPS * game_framework.frame_time
            if Character.state == 4:
                if self.y < 50.0:
                    self.y = 50.0
                    Move = False
                    Fall = False
                    fall_velocity = 0.0
            if self.y < -68:
                Move = False
                Fall = False
                fall_velocity = 0.0
                self.state_machine.add_event(('DIE', 0))

        if attacking and not Attack:
            if Character.attack_delay == 0:
                if Character.stance == 0 and Character.bullet_SG > 0 and (Character.state == 0 or Character.state == 1):
                    if self.x > 5600 and not self.mouse:
                        scroll_offset = 5600 - 1600 // 2
                        mouse_x = mouse_x + scroll_offset
                        self.mouse = True
                    elif self.x > 800 and not self.mouse and server.background.w > 1600:
                        scroll_offset = self.x - 1600 // 2
                        mouse_x = mouse_x + scroll_offset
                        self.mouse = True
                    if mouse_x > self.x:
                        self.attack_dir = 1
                        if (not Move or Fall or Jump) and not d_pressed and not a_pressed:
                            self.face_dir = 1
                    elif mouse_x < self.x:
                        self.attack_dir = -1
                        if (not Move or Fall or Jump) and not d_pressed and not a_pressed:
                            self.face_dir = -1

                    if self.attack_time == 0:
                        self.attack_time = get_time()
                        self.frame = 0
                        Character.bullet_SG -= 1

                        normalsgeffect = NormalSGEffect(self.attack_dir)
                        game_world.add_object(normalsgeffect, 3)

                        normalsg1 = NormalSG1(self.attack_dir)
                        game_world.add_object(normalsg1, 3)
                        for mob in mob_group:
                            game_world.add_collision_pairs(f'normalsg1:{mob}', normalsg1, None)

                        normalsg2 = NormalSG2(self.attack_dir)
                        game_world.add_object(normalsg2, 3)
                        for mob in mob_group:
                            game_world.add_collision_pairs(f'normalsg2:{mob}', normalsg2, None)

                        normalsg3 = NormalSG3(self.attack_dir)
                        game_world.add_object(normalsg3, 3)
                        for mob in mob_group:
                            game_world.add_collision_pairs(f'normalsg3:{mob}', normalsg3, None)

                        sg_attack_sound_list = Character.voices['SG_Attack']
                        random.choice(sg_attack_sound_list).play()

                        Attack = True
                elif Character.stance == 1:
                    if Character.state == 0 and Character.bullet_RF > 0 and not Move:
                        if self.x > 5600 and not self.mouse:
                            scroll_offset = 5600 - 1600 // 2
                            mouse_x = mouse_x + scroll_offset
                            self.mouse = True
                        elif self.x > 800 and not self.mouse and server.background.w > 1600:
                            scroll_offset = self.x - 1600 // 2
                            mouse_x = mouse_x + scroll_offset
                            self.mouse = True
                        if mouse_x > self.x:
                            self.attack_dir = 1
                            self.face_dir = 1
                        elif mouse_x < self.x:
                            self.attack_dir = -1
                            self.face_dir = -1
                        if self.attack_time == 0:
                            self.attack_time = get_time()
                            self.frame = 0
                            Character.bullet_RF -= 1

                            if Character.bullet_RF > 0:
                                normalrfeffect = NormalRFEffect(self.attack_dir)
                                game_world.add_object(normalrfeffect, 3)

                                normalrf = NormalRF(self.attack_dir)
                                game_world.add_object(normalrf, 3)
                                for mob in mob_group:
                                    game_world.add_collision_pairs(f'normalrf:{mob}', normalrf, None)
                            else:
                                normalrfspeffect = NormalRFSPEffect(self.attack_dir)
                                game_world.add_object(normalrfspeffect, 3)

                                normalrfsp = NormalRFSP(self.attack_dir)
                                game_world.add_object(normalrfsp, 3)
                                for mob in mob_group:
                                    game_world.add_collision_pairs(f'normalrfsp:{mob}', normalrfsp, None)

                            rfeffect = RFEffect(self.attack_dir)
                            game_world.add_object(rfeffect, 3)

                            rf_attack_sound_list = Character.voices['RF_Attack']
                            random.choice(rf_attack_sound_list).play()

                            Attack = True
                    elif Character.state == 1 and Character.target_down_bullet > 0 and not Move:
                        if self.x > 5600 and not self.mouse:
                            scroll_offset = 5600 - 1600 // 2
                            mouse_x = mouse_x + scroll_offset
                            self.mouse = True
                        elif self.x > 800 and not self.mouse and server.background.w > 1600:
                            scroll_offset = self.x - 1600 // 2
                            mouse_x = mouse_x + scroll_offset
                            self.mouse = True
                        if mouse_x > self.x:
                            self.attack_dir = 1
                            self.face_dir = 1
                        elif mouse_x < self.x:
                            self.attack_dir = -1
                            self.face_dir = -1
                        if self.attack_time == 0:
                            self.attack_time = get_time()
                            self.frame = 0
                            Character.target_down_bullet -= 1

                            rcskillrfeffect = RcskillRFEffect()
                            game_world.add_object(rcskillrfeffect, 3)

                            rcskillrf = RcskillRF()
                            game_world.add_object(rcskillrf, 3)
                            for mob in mob_group:
                                game_world.add_collision_pairs(f'rcskillrf:{mob}', rcskillrf, None)

                            rfeffect = RFEffect(self.attack_dir)
                            game_world.add_object(rfeffect, 3)

                            Attack = True
                    elif Character.state == 4:
                        if self.x > 5600 and not self.mouse:
                            scroll_offset = 5600 - 1600 // 2
                            mouse_x = mouse_x + scroll_offset
                            self.mouse = True
                        elif self.x > 800 and not self.mouse and server.background.w > 1600:
                            scroll_offset = self.x - 1600 // 2
                            mouse_x = mouse_x + scroll_offset
                            self.mouse = True
                        if mouse_x > self.x:
                            self.attack_dir = 1
                            if (not Move or Fall or Jump) and not d_pressed and not a_pressed:
                                self.face_dir = 1
                        elif mouse_x < self.x:
                            self.attack_dir = -1
                            if (not Move or Fall or Jump) and not d_pressed and not a_pressed:
                                self.face_dir = -1
                        if self.attack_time == 0:
                            self.attack_time = get_time()
                            self.frame = 0

                            normalrfspeffect = NormalRFSPEffect(self.attack_dir)
                            game_world.add_object(normalrfspeffect, 3)

                            normalrfsp = NormalRFSP(self.attack_dir)
                            game_world.add_object(normalrfsp, 3)
                            for mob in mob_group:
                                game_world.add_collision_pairs(f'normalrfsp:{mob}', normalrfsp, None)

                            cskillrfeffect = CskillRFEffect(self.attack_dir)
                            game_world.add_object(cskillrfeffect, 3)

                            rf_attack_sound_list = Character.voices['RF_Attack']
                            random.choice(rf_attack_sound_list).play()

                            Attack = True
                elif Character.stance == 2 and not Rc_HG:
                    if Character.state == 0 and Character.bullet_HG > 0:
                        if self.x > 5600 and not self.mouse:
                            scroll_offset = 5600 - 1600 // 2
                            mouse_x = mouse_x + scroll_offset
                            self.mouse = True
                        elif self.x > 800 and not self.mouse and server.background.w > 1600:
                            scroll_offset = self.x - 1600 // 2
                            mouse_x = mouse_x + scroll_offset
                            self.mouse = True
                        if mouse_x > self.x:
                            self.attack_dir = 1
                            if (not Move or Fall or Jump) and not d_pressed and not a_pressed:
                                self.face_dir = 1
                        elif mouse_x < self.x:
                            self.attack_dir = -1
                            if (not Move or Fall or Jump) and not d_pressed and not a_pressed:
                                self.face_dir = -1
                        if self.attack_time == 0:
                            self.attack_time = get_time()
                            self.frame = 0
                            Character.bullet_HG -= 1

                            normalhgeffect = NormalHGEffect(self.attack_dir)
                            game_world.add_object(normalhgeffect, 3)

                            normalhg = NormalHG(self.attack_dir)
                            game_world.add_object(normalhg, 3)
                            for mob in mob_group:
                                game_world.add_collision_pairs(f'normalhg:{mob}', normalhg, None)

                            hgeffect = HGEffect(self.attack_dir)
                            game_world.add_object(hgeffect, 3)

                            if random.random() < 0.5:
                                hg_attack_sound_list = Character.voices['HG_Attack']
                                random.choice(hg_attack_sound_list).play()

                            Attack = True
                    elif Character.state == 2 and Character.bullet_HG > 0:
                        if self.x > 5600 and not self.mouse:
                            scroll_offset = 5600 - 1600 // 2
                            mouse_x = mouse_x + scroll_offset
                            self.mouse = True
                        elif self.x > 800 and not self.mouse and server.background.w > 1600:
                            scroll_offset = self.x - 1600 // 2
                            mouse_x = mouse_x + scroll_offset
                            self.mouse = True
                        if mouse_x > self.x:
                            self.face_dir = 1
                            self.attack_dir = 1
                        elif mouse_x < self.x:
                            self.face_dir = -1
                            self.attack_dir = -1

        if Attack:
            if Character.stance == 0:
                if get_time() - self.attack_time > 0.5:
                    Character.attack_delay = 0.8
                    self.attack_time = 0
                    self.frame = 0
                    Attack = False
            elif Character.stance == 1:
                if get_time() - self.attack_time > 0.4:
                    if Character.state == 1 or Character.state == 4:
                        Character.attack_delay = 0.75
                    else:
                        Character.attack_delay = 1.5
                    self.attack_time = 0
                    self.frame = 0
                    Attack = False
            elif Character.stance == 2:
                if get_time() - self.attack_time > 0.3:
                    Character.attack_delay = 0.4
                    self.attack_time = 0
                    self.frame = 0
                    Attack = False

        if Character.stance == 2 and Character.state == 1:
            if Character.dexterous_shot_cooldown == 0 and not Attack and Character.bullet_HG > 0:
                Character.speed = 7
                self.frame = 0
                if God or Character.upgrade >= 2:
                    Character.dexterous_shot_cooldown = 1
                else:
                    Character.dexterous_shot_cooldown = 2
                Character.bullet_HG -= 1
                Character.hit_delay = 0.5
                rchg = True
                rcskillhgeffect = RcskillHGEffect(self.face_dir)
                game_world.add_object(rcskillhgeffect, 3)

                rcskillhg = RcskillHG()
                game_world.add_object(rcskillhg, 3)
                for mob in mob_group:
                    game_world.add_collision_pairs(f'rcskillhg:{mob}', rcskillhg, None)

                if random.random() < 0.5:
                    hg_attack_sound_list = Character.voices['HG_Attack']
                    random.choice(hg_attack_sound_list).play()

                if d_pressed or a_pressed:
                    self.state_machine.add_event(('WALK', 0))
                else:
                    self.state_machine.add_event(('IDLE', 0))

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

        if not Character.dash_cooldown == 0:
            if self.Lshift_cool == 0:
                self.Lshift_cool = get_time()
            if get_time() - self.Lshift_cool > Character.dash_cooldown:
                Character.dash_cooldown = 0
                self.Lshift_cool = 0

        if not Character.hour_of_judgment_cooldown == 0:
            if self.Q_SG_cool == 0:
                self.Q_SG_cool = get_time()
            if get_time() - self.Q_SG_cool > Character.hour_of_judgment_cooldown:
                Character.hour_of_judgment_cooldown = 0
                self.Q_SG_cool = 0

        if not Character.shotgun_rapid_fire_cooldown == 0:
            if self.E_SG_cool == 0:
                self.E_SG_cool = get_time()
            if get_time() - self.E_SG_cool > Character.shotgun_rapid_fire_cooldown:
                Character.shotgun_rapid_fire_cooldown = 0
                self.E_SG_cool = 0

        if not Character.last_request_cooldown == 0:
            if self.C_SG_cool == 0:
                self.C_SG_cool = get_time()
            if get_time() - self.C_SG_cool > Character.last_request_cooldown:
                Character.last_request_cooldown = 0
                self.C_SG_cool = 0

        if not Character.target_down_cooldown == 0:
            if self.Rc_RF_cool == 0:
                self.Rc_RF_cool = get_time()
            if get_time() - self.Rc_RF_cool > Character.target_down_cooldown:
                Character.target_down_cooldown = 0
                self.Rc_RF_cool = 0

        if not Character.perfect_shot_cooldown == 0:
            if self.Q_RF_cool == 0:
                self.Q_RF_cool = get_time()
            if get_time() - self.Q_RF_cool > Character.perfect_shot_cooldown:
                Character.perfect_shot_cooldown = 0
                self.Q_RF_cool = 0

        if not Character.focus_shot_cooldown == 0:
            if self.E_RF_cool == 0:
                self.E_RF_cool = get_time()
            if get_time() - self.E_RF_cool > Character.focus_shot_cooldown:
                Character.focus_shot_cooldown = 0
                self.E_RF_cool = 0

        if not Character.catastrophe_cooldown == 0:
            if self.C_RF_cool == 0:
                self.C_RF_cool = get_time()
            if get_time() - self.C_RF_cool > Character.catastrophe_cooldown:
                Character.catastrophe_cooldown = 0
                self.C_RF_cool = 0

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

        if not Character.dexterous_shot_cooldown == 0:
            if self.Rc_HG_cool == 0:
                self.Rc_HG_cool = get_time()
            if get_time() - self.Rc_HG_cool > Character.dexterous_shot_cooldown:
                Character.dexterous_shot_cooldown = 0
                self.Rc_HG_cool = 0

        if not Character.at02_grenade_cooldown == 0:
            if self.Q_HG_cool == 0:
                self.Q_HG_cool = get_time()
            if get_time() - self.Q_HG_cool > Character.at02_grenade_cooldown:
                Character.at02_grenade_cooldown = 0
                self.Q_HG_cool = 0

        if not Character.bullet_rain_cooldown == 0:
            if self.E_HG_cool == 0:
                self.E_HG_cool = get_time()
            if get_time() - self.E_HG_cool > Character.bullet_rain_cooldown:
                Character.bullet_rain_cooldown = 0
                self.E_HG_cool = 0

        if not Character.equilibrium_cooldown == 0:
            if self.C_HG_cool == 0:
                self.C_HG_cool = get_time()
            if get_time() - self.C_HG_cool > Character.equilibrium_cooldown:
                Character.equilibrium_cooldown = 0
                self.C_HG_cool = 0

    def handle_event(self, event):
        global mouse_x, mouse_y
        self.state_machine.add_event(('INPUT', event))
        if (event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT) or (event.type == SDL_MOUSEMOTION):
            mouse_x, mouse_y = event.x, event.y
            self.mouse = False

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
        elif group == 'server.character:diamond':
            Character.score += 500
        if group == 'server.character:medal':
            Character.medal += 1
            Character.score += 1000
        elif group == 'server.character:portal':
            '''
            if Character.state == 0:
                if play_mode.stage == 1 or play_mode.stage == 2:
                    self.x, self.y = 34.0, 170.0
                    play_mode.change_stage(play_mode.stage + 1)

                    if Character.stance == 0:
                        Character.voices['SG_Portal'][0].play()
                    elif Character.stance == 1:
                        Character.voices['RF_Portal'][0].play()
                    elif Character.stance == 2:
                        Character.voices['HG_Portal'][0].play()
                elif (play_mode.stage == 3 or play_mode.stage == 4) and Character.medal == 1:
                    self.x, self.y = 34.0, 170.0
                    play_mode.change_stage(play_mode.stage + 1)

                    if Character.stance == 0:
                        Character.voices['SG_Portal'][0].play()
                    elif Character.stance == 1:
                        Character.voices['RF_Portal'][0].play()
                    elif Character.stance == 2:
                        Character.voices['HG_Portal'][0].play()

                elif (play_mode.stage == 5 or play_mode.stage == 6) and Character.medal == 2:
                    self.x, self.y = 34.0, 170.0
                    play_mode.change_stage(play_mode.stage + 1)

                    if Character.stance == 0:
                        Character.voices['SG_Portal'][0].play()
                    elif Character.stance == 1:
                        Character.voices['RF_Portal'][0].play()
                    elif Character.stance == 2:
                        Character.voices['HG_Portal'][0].play()
                        '''

    def handle_collision_fall(self, group, other):
        global Fall, fall_velocity
        if group == 'server.character:ground' and Fall:
            self.y = ground.Ground.collide_fall(other)
            Fall = False
            if fall_velocity > 2.0:
                Character.fall_sound.play()
            fall_velocity = 0.0

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