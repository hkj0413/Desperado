from pico2d import *

import game_framework
import game_world
import guide_mode
import server

from ground import Ground
from wall import Wall
from ladder import Ladder
from portal import Portal
from character import Character
from ui import UI
from coconut import Coconut
from stone import Stone
from fireball import Fireball
from heal import Heal
from more_hp import MoreHP
from enhance import Enhance
from medal import Medal

from background import Background
from spore import Spore
from slime import Slime
from pig import Pig
from stonegolem import Stonegolem
from skelldog import Skelldog
from coldeye import Coldeye
from wildboar import Wildboar
from stonestatue import Stonestatue
from bulldog import Bulldog
from imp import Imp
from fireboar import Fireboar
from firemixgolem import Firemixgolem

character_created = False

stage = 1

def handle_events():
    global stage
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            game_framework.push_mode(guide_mode)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_n and stage < 7:
            if Character.stance == 0:
                Character.voices['SG_Portal_Voice'][0].play()
            elif Character.stance == 1:
                Character.voices['RF_Portal_Voice'][0].play()
            elif Character.stance == 2:
                Character.voices['HG_Portal_Voice'][0].play()
            Character.portal_sound.play()
            stage += 1
            change_stage(stage)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_m and stage > 1:
            if Character.stance == 0:
                Character.voices['SG_Portal_Voice'][0].play()
            elif Character.stance == 1:
                Character.voices['RF_Portal_Voice'][0].play()
            elif Character.stance == 2:
                Character.voices['HG_Portal_Voice'][0].play()
            Character.portal_sound.play()
            stage -= 1
            change_stage(stage)
        else:
            server.character.handle_event(event)

projectile_group = [
        'normalsg1', 'normalsg2', 'normalsg3', 'normalrf', 'normalrfsp', 'normalhg', 'reloadrf', 'uniquerf', 'uniquehg',
        'uniquesg', 'skillsg', 'skillstunsg', 'skillrf', 'ultstunsg', 'ultsg', 'skillboomhg', 'ulthg', 'uniquesg'
        ]

stage_data = {
    1: {
        'ladder_positions': [
            (range(3, 13), 39),
            (range(3, 12), 95),
            (range(13, 22), 95),
            (range(8, 17), 106),
            (range(18, 26), 106),
        ],

        'wall_positions': [
            (range(3, 7), 29),
            (range(11, 23), 43),
        ],

        'floor_positions': [
            (2, range(65, 68)),
            (1, range(0, 30)),
            (1, range(35, 44)),
            (1, range(49, 57)),
            (1, range(62, 85)),
            (1, range(89, 90)),
            (1, range(94, 160)),
            (0, range(0, 30)),
            (0, range(35, 44)),
            (0, range(49, 57)),
            (0, range(62, 85)),
            (0, range(89, 90)),
            (0, range(94, 160)),
        ],

        'ground_positions': [
            (23, range(43, 44)),
            (17, range(96, 107)),
            (13, range(38, 41)),
            (12, range(95, 106)),
            (10, range(40, 44)),
            (8, range(16, 19)),
            (8, range(93, 94)),
            (7, range(28, 30)),
            (7, range(96, 107)),
            (6, range(71, 80)),
            (5, range(8, 15)),
            (5, range(20, 27)),
            (3, range(65, 68)),
            (2, range(0, 30)),
            (2, range(35, 44)),
            (2, range(49, 57)),
            (2, range(62, 65)),
            (2, range(68, 85)),
            (2, range(89, 90)),
            (2, range(94, 160)),
        ],

        'spore_positions': [
            (7, 3),
            (10, 6),
            (11, 3),
            (12, 6),
            (13, 3),
            (17, 3),
            (25, 3),
            (22, 6),
            (74, 7),
            (76, 7),
            (80, 3),
            (99, 8),
            (100, 8),
            (101, 8),
            (102, 8),
            (103, 8),
        ],

        'slime_positions': [
            (9, 3),
            (11, 6),
            (16, 3),
            (22, 3),
            (39, 3),
            (75, 7),
            (79, 3),
            (98, 13),
            (99, 13),
            (100,13),
            (101, 13),
            (102, 13),
        ],

        'pig_positions': [
            (21, 3),
            (23, 6),
            (40, 3),
            (53, 3),
            (71, 3),
            (73, 3),
            (99, 18),
            (100, 18),
            (101, 18),
            (102, 18),
            (103, 18),
        ],

        'coconut_positions': [
        (6, 15, 1),
        (32, 18, 2),
        (45, 20, 1),
        (47, 20, 4),
        (58, 14, 2),
        (59, 21, 1),
        (60, 14, 4),
        (66, 21, 3),
        (69, 21, 2),
        (80, 21, 5),
        ],

        'heal_positions': [
        (39, 14, 4),
        (76, 22, 4),
        (79, 22, 4),
        ],
    },

    2: {
        'floor_positions': [
            (1, range(0, 40)),
            (0, range(0, 40)),
        ],

        'ground_positions': [
            (14, range(35, 40)),
            (11, range(27, 32)),
            (8, range(19, 24)),
            (5, range(11, 16)),
            (2, range(0, 40)),
        ],
    },

    3: {
        'floor_positions': [
            (1, range(0, 40)),
            (0, range(0, 40)),
        ],

        'ground_positions': [
            (10, range(0, 5)),
            (10, range(35, 40)),
            (8, range(7, 9)),
            (8, range(14, 26)),
            (8, range(31, 33)),
            (5, range(29, 36)),
            (5, range(4, 11)),
            (2, range(0, 40)),
        ],
    },

    4: {
        'ladder_positions': [
            (range(6, 16), 54),
        ],

        'wall_positions': [
            (range(11, 15), 35),
            (range(11, 20), 62),
            (range(3, 10), 98),
        ],

        'floor_positions': [
            (1, range(0, 45)),
            (1, range(50, 65)),
            (1, range(72, 108)),
            (0, range(0, 45)),
            (0, range(50, 65)),
            (0, range(72, 108)),
        ],

        'ground_positions': [
            (16, range(54, 55)),
            (12, range(56, 60)),
            (10, range(85, 99)),
            (8, range(80, 82)),
            (7, range(20, 23)),
            (7, range(27, 32)),
            (7, range(37, 44)),
            (6, range(84, 91)),
            (5, range(15, 18)),
            (5, range(53, 55)),
            (4, range(94, 96)),
            (2, range(0, 45)),
            (2, range(50, 65)),
            (2, range(72, 108)),
        ],

        'stone_positions': [
            (16, 21, 1),
            (21, 21, 2),
            (34, 18, 1),
            (47, 21, 3),
            (60, 21, 2),
            (66, 16, 1),
            (68, 16, 2),
            (70, 16, 3),
            (82, 21, 1),
        ],

        'skelldog_positions': [
            (9, 3),
            (23, 3),
            (27, 3),
            (31, 3),
            (55, 3),
            (58, 3),
            (79, 3),
            (82, 3),
            (85, 3),
            (88, 3),
            (90, 11),
        ],

        'coldeye_positions': [
            (8, 3),
            (16, 3),
            (28, 3),
            (32, 3),
            (59, 3),
            (84, 3),
            (87, 3),
            (88, 11),
        ],

        'wildboar_positions': [
            (12, 3),
            (20, 3),
            (24, 3),
            (40, 8),
            (57, 3),
            (87, 7),
            (89, 3),
            (93, 11),
        ],

        'stonestatue_positions': [
            (30, 8),
            (39, 3),
            (77, 3),
            (97, 11),
        ],

        'heal_positions': [
            (42, 3, 6),
            (58, 13, 6),
            (95, 11, 6),
        ],
    },

    5: {
        'floor_positions': [
            (1, range(0, 36)),
            (0, range(0, 36)),
         ],

          'ground_positions': [
            (2, range(0, 36)),
          ],
    },

    6: {
          'floor_positions': [
            (1, range(0, 108)),
            (0, range(0, 108)),
        ],

        'ground_positions': [
            (2, range(0, 108)),
        ],

        'bulldog_positions': [
            (24, 3),
            (30, 3),
            (36, 3),
            (42, 3),
            (48, 3),
            (54, 3),
        ],

        'imp_positions': [
            (26, 3),
            (31, 3),
            (36, 3),
            (41, 3),
            (46, 3),
            (51, 3),
        ],

        'fireboar_positions': [
            (60, 3),
            (66, 3),
            (72, 3),
            (78, 3),
            (84, 3),
            (90, 3),
        ],

        'firemixgolem_positions': [
            (70, 6),
            (80, 6),
            (90, 6),
        ],

        'fireball_positions': [
            (6, 21, 1),
        ],

        'heal_positions': [
            (30, 3, 8),
            (60, 3, 8),
            (90, 3, 8),
        ],
    },

    7: {
        'floor_positions': [
            (1, range(0, 36)),
            (0, range(0, 36)),
         ],

          'ground_positions': [
            (2, range(0, 36)),
          ],
    },
}

def clear_collision_pairs():
    game_world.collision_pairs.clear()

def change_stage(stage_number):
    global stage

    all_objects = game_world.get_all_objects()

    for obj in all_objects:
        game_world.remove_object(obj)

    clear_collision_pairs()

    stage = stage_number

    init(stage_number)

def init(stage):
    global character, character_created

    if stage == 1:
        stage_info = stage_data[stage]

        # 캐릭터
        server.character = Character()
        game_world.add_object(server.character, 1)

        # UI
        ui = UI()
        game_world.add_object(ui, 3)

        server.background = Background(0)
        game_world.add_object(server.background, 0)

        # 사다리
        game_world.add_collision_pairs('server.character:ladder', server.character, None)

        for i_range, j in stage_info['ladder_positions']:
            ladders = [Ladder(j, i, 4) for i in i_range]
            game_world.add_objects(ladders, 0)
            for ladder in ladders:
                game_world.add_collision_pairs('server.character:ladder', None, ladder)

        # a, d 판정만 있는 블럭
        game_world.add_collision_pairs('server.character:wall', server.character, None)

        for i_range, j in stage_info['wall_positions']:
            walls = [Wall(j, i, 3) for i in i_range]
            game_world.add_objects(walls, 0)
            for wall in walls:
                game_world.add_collision_pairs('server.character:wall', None, wall)

        # a, d 판정만 있는 바닥
        for j, i_range in stage_info['floor_positions']:
            walls = [Wall(i, j, 1) for i in i_range]
            game_world.add_objects(walls, 0)
            for wall in walls:
                game_world.add_collision_pairs('server.character:wall', None, wall)

        # a, d, 점프, 추락 판정이 있는 블럭
        game_world.add_collision_pairs('server.character:ground', server.character, None)

        for j, i_range in stage_info['ground_positions']:
            grounds = [Ground(i, j, 2) for i in i_range]
            game_world.add_objects(grounds, 0)
            for ground in grounds:
                game_world.add_collision_pairs('server.character:ground', None, ground)

        # 포탈
        portal = Portal(158, 4, 0)
        game_world.add_object(portal, 0)

        # 몹 스포아
        game_world.add_collision_pairs('server.character:spore', server.character, None)

        for i, j in stage_info['spore_positions']:
            spores = [Spore(i, j)]
            game_world.add_objects(spores, 2)
            for spore in spores:
                game_world.add_collision_pairs('server.character:spore', None, spore)
                for projectile in projectile_group:
                    game_world.add_collision_pairs(f'{projectile}:spore', None, spore)

        # 몹 슬라임
        game_world.add_collision_pairs('server.character:slime', server.character, None)

        for i, j in stage_info['slime_positions']:
            slimes = [Slime(i, j)]
            game_world.add_objects(slimes, 2)
            for slime in slimes:
                game_world.add_collision_pairs('server.character:slime', None, slime)
                for projectile in projectile_group:
                    game_world.add_collision_pairs(f'{projectile}:slime', None, slime)

        # 몹 돼지
        game_world.add_collision_pairs('server.character:pig', server.character, None)

        for i, j in stage_info['pig_positions']:
            pigs = [Pig(i, j)]
            game_world.add_objects(pigs, 2)
            for pig in pigs:
                game_world.add_collision_pairs('server.character:pig', None, pig)
                for projectile in projectile_group:
                    game_world.add_collision_pairs(f'{projectile}:pig', None, pig)

        # 낙하 장애물 코코넛 k = 박자
        game_world.add_collision_pairs('server.character:coconut', server.character, None)

        for i, j, k in stage_info['coconut_positions']:
            coconuts = [Coconut(i, j, k)]
            game_world.add_objects(coconuts, 2)
            for coconut in coconuts:
                game_world.add_collision_pairs('server.character:coconut', None, coconut)

        # 회복 아이템 k = 힐량
        game_world.add_collision_pairs('server.character:heal', server.character, None)


        for i, j, k in stage_info['heal_positions']:
            heals = [Heal(i, j, k)]
            game_world.add_objects(heals, 2)
            for heal in heals:
                game_world.add_collision_pairs('server.character:heal', None, heal)

        # 최대 체력 증가 아이템
        game_world.add_collision_pairs('server.character:morehp', server.character, None)

        morehp = MoreHP(73, 22)
        game_world.add_object(morehp, 2)
        game_world.add_collision_pairs('server.character:morehp', None, morehp)

        # 캐릭터 강화 아이템
        game_world.add_collision_pairs('server.character:enhance', server.character, None)

        enhance = Enhance(90, 23)
        game_world.add_object(enhance, 2)
        game_world.add_collision_pairs('server.character:enhance', None, enhance)

    elif stage == 2:
        stage_info = stage_data[stage]

        # 캐릭터
        server.character = Character()
        game_world.add_object(server.character, 1)

        # UI
        ui = UI()
        game_world.add_object(ui, 3)

        server.background = Background(1)
        game_world.add_object(server.background, 0)

        game_world.add_collision_pairs('server.character:ladder', server.character, None)

        # a, d 판정만 있는 바닥
        game_world.add_collision_pairs('server.character:wall', server.character, None)

        for j, i_range in stage_info['floor_positions']:
            walls = [Wall(i, j, 1) for i in i_range]
            game_world.add_objects(walls, 0)
            for wall in walls:
                game_world.add_collision_pairs('server.character:wall', None, wall)

        # a, d, 점프, 추락 판정이 있는 블럭
        game_world.add_collision_pairs('server.character:ground', server.character, None)

        for j, i_range in stage_info['ground_positions']:
            grounds = [Ground(i, j, 2) for i in i_range]
            game_world.add_objects(grounds, 0)
            for ground in grounds:
                game_world.add_collision_pairs('server.character:ground', None, ground)

        # 포탈
        portal = Portal(37, 16, 0)
        game_world.add_object(portal, 0)

    elif stage == 3:
        stage_info = stage_data[stage]

        # 캐릭터
        server.character = Character()
        game_world.add_object(server.character, 1)

        # UI
        ui = UI()
        game_world.add_object(ui, 3)

        server.background = Background(1)
        game_world.add_object(server.background, 0)

        game_world.add_collision_pairs('server.character:ladder', server.character, None)

        # a, d 판정만 있는 바닥
        game_world.add_collision_pairs('server.character:wall', server.character, None)

        for j, i_range in stage_info['floor_positions']:
            walls = [Wall(i, j, 1) for i in i_range]
            game_world.add_objects(walls, 0)
            for wall in walls:
                game_world.add_collision_pairs('server.character:wall', None, wall)

        # a, d, 점프, 추락 판정이 있는 블럭
        game_world.add_collision_pairs('server.character:ground', server.character, None)

        for j, i_range in stage_info['ground_positions']:
            grounds = [Ground(i, j, 2) for i in i_range]
            game_world.add_objects(grounds, 0)
            for ground in grounds:
                game_world.add_collision_pairs('server.character:ground', None, ground)

        # 포탈
        portal = Portal(38, 4, 1)
        game_world.add_object(portal, 0)

        # 보스 골렘
        game_world.add_collision_pairs('server.character:stonegolem', server.character, None)
        game_world.add_collision_pairs('server.character:stonegolemattack', server.character, None)
        game_world.add_collision_pairs('server.character:stonegolemskill', server.character, None)
        game_world.add_collision_pairs('server.character:enhance', server.character, None)
        game_world.add_collision_pairs('server.character:medal', server.character, None)

        stonegolem = Stonegolem(18, 5)
        game_world.add_object(stonegolem, 0)
        game_world.add_collision_pairs('server.character:stonegolem', None, stonegolem)
        for projectile in projectile_group:
            game_world.add_collision_pairs(f'{projectile}:stonegolem', None, stonegolem)

        # 회복 아이템 k = 힐량
        game_world.add_collision_pairs('server.character:heal', server.character, None)

        heals = [Heal(2, 11, 4)]
        game_world.add_objects(heals, 2)
        for heal in heals:
            game_world.add_collision_pairs('server.character:heal', None, heal)

    elif stage == 4:
        stage_info = stage_data[stage]

        # 캐릭터
        server.character = Character()
        game_world.add_object(server.character, 1)

        # UI
        ui = UI()
        game_world.add_object(ui, 3)

        server.background = Background(2)
        game_world.add_object(server.background, 0)

        # 사다리
        game_world.add_collision_pairs('server.character:ladder', server.character, None)

        for i_range, j in stage_info['ladder_positions']:
            ladders = [Ladder(j, i, 7) for i in i_range]
            game_world.add_objects(ladders, 0)
            for ladder in ladders:
                game_world.add_collision_pairs('server.character:ladder', None, ladder)

        # a, d 판정만 있는 블럭
        game_world.add_collision_pairs('server.character:wall', server.character, None)

        for i_range, j in stage_info['wall_positions']:
            walls = [Wall(j, i, 6) for i in i_range]
            game_world.add_objects(walls, 0)
            for wall in walls:
                game_world.add_collision_pairs('server.character:wall', None, wall)

        # a, d 판정만 있는 바닥
        for j, i_range in stage_info['floor_positions']:
            walls = [Wall(i, j, 5) for i in i_range]
            game_world.add_objects(walls, 0)
            for wall in walls:
                game_world.add_collision_pairs('server.character:wall', None, wall)

        # a, d, 점프, 추락 판정이 있는 블럭
        game_world.add_collision_pairs('server.character:ground', server.character, None)

        for j, i_range in stage_info['ground_positions']:
            grounds = [Ground(i, j, 5) for i in i_range]
            game_world.add_objects(grounds, 0)
            for ground in grounds:
                game_world.add_collision_pairs('server.character:ground', None, ground)

        # 포탈
        game_world.add_collision_pairs('server.character:portal', server.character, None)

        portal = Portal(105, 4, 1)
        game_world.add_object(portal, 0)
        game_world.add_collision_pairs('server.character:portal', None, portal)

        # 몹 스켈독
        game_world.add_collision_pairs('server.character:skelldog', server.character, None)

        for i, j in stage_info['skelldog_positions']:
            skelldogs = [Skelldog(i, j)]
            game_world.add_objects(skelldogs, 2)
            for skelldog in skelldogs:
                game_world.add_collision_pairs('server.character:skelldog', None, skelldog)
                for projectile in projectile_group:
                    game_world.add_collision_pairs(f'{projectile}:skelldog', None, skelldog)

        # 몹 콜드아이
        game_world.add_collision_pairs('server.character:coldeye', server.character, None)

        for i, j in stage_info['coldeye_positions']:
            coldeyes = [Coldeye(i, j)]
            game_world.add_objects(coldeyes, 2)
            for coldeye in coldeyes:
                game_world.add_collision_pairs('server.character:coldeye', None, coldeye)
                for projectile in projectile_group:
                    game_world.add_collision_pairs(f'{projectile}:coldeye', None, coldeye)

        # 몹 와일드보어
        game_world.add_collision_pairs('server.character:wildboar', server.character, None)

        for i, j in stage_info['wildboar_positions']:
            wildboars = [Wildboar(i, j)]
            game_world.add_objects(wildboars, 2)
            for wildboar in wildboars:
                game_world.add_collision_pairs('server.character:wildboar', None, wildboar)
                for projectile in projectile_group:
                    game_world.add_collision_pairs(f'{projectile}:wildboar', None, wildboar)

        # 몹 석상
        game_world.add_collision_pairs('server.character:stonestatue', server.character, None)

        for i, j in stage_info['stonestatue_positions']:
            stonestatues = [Stonestatue(i, j)]
            game_world.add_objects(stonestatues, 0)
            for stonestatue in stonestatues:
                game_world.add_collision_pairs('server.character:stonestatue', None, stonestatue)
                for projectile in projectile_group:
                    game_world.add_collision_pairs(f'{projectile}:stonestatue', None, stonestatue)

        # 낙하 장애물 동멩이 k = 박자
        game_world.add_collision_pairs('server.character:stone', server.character, None)

        for i, j, k in stage_info['stone_positions']:
            stones = [Stone(i, j, k)]
            game_world.add_objects(stones, 2)
            for stone in stones:
                game_world.add_collision_pairs('server.character:stone', None, stone)

        # 회복 아이템 k = 힐량
        game_world.add_collision_pairs('server.character:heal', server.character, None)

        for i, j, k in stage_info['heal_positions']:
            heals = [Heal(i, j, k)]
            game_world.add_objects(heals, 2)
            for heal in heals:
                game_world.add_collision_pairs('server.character:heal', None, heal)

        # 최대 체력 증가 아이템
        game_world.add_collision_pairs('server.character:morehp', server.character, None)

        morehp = MoreHP(76, 11)
        game_world.add_object(morehp, 2)
        game_world.add_collision_pairs('server.character:morehp', None, morehp)

        # 캐릭터 강화 아이템
        game_world.add_collision_pairs('server.character:enhance', server.character, None)

        enhance = Enhance(68, 7)
        game_world.add_object(enhance, 2)
        game_world.add_collision_pairs('server.character:enhance', None, enhance)

    elif stage == 5:
        stage_info = stage_data[stage]

        # 캐릭터
        server.character = Character()
        game_world.add_object(server.character, 1)

        # UI
        ui = UI()
        game_world.add_object(ui, 3)

        server.background = Background(3)
        game_world.add_object(server.background, 0)

        game_world.add_collision_pairs('server.character:ladder', server.character, None)

        # a, d 판정만 있는 바닥
        game_world.add_collision_pairs('server.character:wall', server.character, None)

        for j, i_range in stage_info['floor_positions']:
            walls = [Wall(i, j, 5) for i in i_range]
            game_world.add_objects(walls, 0)
            for wall in walls:
                game_world.add_collision_pairs('server.character:wall', None, wall)

        # a, d, 점프, 추락 판정이 있는 블럭
        game_world.add_collision_pairs('server.character:ground', server.character, None)

        for j, i_range in stage_info['ground_positions']:
            grounds = [Ground(i, j, 5) for i in i_range]
            game_world.add_objects(grounds, 0)
            for ground in grounds:
                game_world.add_collision_pairs('server.character:ground', None, ground)

        # 포탈
        game_world.add_collision_pairs('server.character:portal', server.character, None)

        portal = Portal(34, 4, 2)
        game_world.add_object(portal, 0)
        game_world.add_collision_pairs('server.character:portal', None, portal)

        # 최대 체력 증가 아이템
        game_world.add_collision_pairs('server.character:morehp', server.character, None)

        morehp = MoreHP(21, 3)
        game_world.add_object(morehp, 2)
        game_world.add_collision_pairs('server.character:morehp', None, morehp)

        # 캐릭터 강화 아이템
        game_world.add_collision_pairs('server.character:enhance', server.character, None)

        enhance = Enhance(24, 3)
        game_world.add_object(enhance, 2)
        game_world.add_collision_pairs('server.character:enhance', None, enhance)

        # 임시 메달
        game_world.add_collision_pairs('server.character:medal', server.character, None)

        medal = Medal(27, 3)
        game_world.add_object(medal, 2)
        game_world.add_collision_pairs('server.character:medal', None, medal)

    elif stage == 6:
        stage_info = stage_data[stage]

        # 캐릭터
        server.character = Character()
        game_world.add_object(server.character, 1)

        # UI
        ui = UI()
        game_world.add_object(ui, 3)

        server.background = Background(4)
        game_world.add_object(server.background, 0)

        game_world.add_collision_pairs('server.character:ladder', server.character, None)

        # a, d 판정만 있는 바닥
        game_world.add_collision_pairs('server.character:wall', server.character, None)

        for j, i_range in stage_info['floor_positions']:
            walls = [Wall(i, j, 11) for i in i_range]
            game_world.add_objects(walls, 0)
            for wall in walls:
                game_world.add_collision_pairs('server.character:wall', None, wall)

        # a, d, 점프, 추락 판정이 있는 블럭
        game_world.add_collision_pairs('server.character:ground', server.character, None)

        for j, i_range in stage_info['ground_positions']:
            grounds = [Ground(i, j, 10) for i in i_range]
            game_world.add_objects(grounds, 0)
            for ground in grounds:
                game_world.add_collision_pairs('server.character:ground', None, ground)

        # 포탈
        game_world.add_collision_pairs('server.character:portal', server.character, None)

        portal = Portal(105, 4, 2)
        game_world.add_object(portal, 0)
        game_world.add_collision_pairs('server.character:portal', None, portal)

        # 몹 불독
        game_world.add_collision_pairs('server.character:bulldog', server.character, None)

        for i, j in stage_info['bulldog_positions']:
            bulldogs = [Bulldog(i, j)]
            game_world.add_objects(bulldogs, 2)
            for bulldog in bulldogs:
                game_world.add_collision_pairs('server.character:bulldog', None, bulldog)
                for projectile in projectile_group:
                    game_world.add_collision_pairs(f'{projectile}:bulldog', None, bulldog)

        # 몹 임프
        game_world.add_collision_pairs('server.character:imp', server.character, None)

        for i, j in stage_info['imp_positions']:
            imps = [Imp(i, j)]
            game_world.add_objects(imps, 2)
            for imp in imps:
                game_world.add_collision_pairs('server.character:imp', None, imp)
                for projectile in projectile_group:
                    game_world.add_collision_pairs(f'{projectile}:imp', None, imp)

        # 몹 파이어보어
        game_world.add_collision_pairs('server.character:fireboar', server.character, None)

        for i, j in stage_info['fireboar_positions']:
            fireboars = [Fireboar(i, j)]
            game_world.add_objects(fireboars, 2)
            for fireboar in fireboars:
                game_world.add_collision_pairs('server.character:fireboar', None, fireboar)
                for projectile in projectile_group:
                    game_world.add_collision_pairs(f'{projectile}:fireboar', None, fireboar)

        # 몹 파이어믹스골렘
        game_world.add_collision_pairs('server.character:firemixgolem', server.character, None)

        for i, j in stage_info['firemixgolem_positions']:
            firemixgolems = [Firemixgolem(i, j)]
            game_world.add_objects(firemixgolems, 0)
            for firemixgolem in firemixgolems:
                game_world.add_collision_pairs('server.character:firemixgolem', None, firemixgolem)
                for projectile in projectile_group:
                    game_world.add_collision_pairs(f'{projectile}:firemixgolem', None, firemixgolem)

        # 낙하 장애물 화염구 k = 박자
        game_world.add_collision_pairs('server.character:fireball', server.character, None)

        for i, j, k in stage_info['fireball_positions']:
            fireballs = [Fireball(i, j, k)]
            game_world.add_objects(fireballs, 2)
            for fireball in fireballs:
                game_world.add_collision_pairs('server.character:fireball', None, fireball)

        # 최대 체력 증가 아이템
        game_world.add_collision_pairs('server.character:morehp', server.character, None)

        morehp = MoreHP(81, 3)
        game_world.add_object(morehp, 2)
        game_world.add_collision_pairs('server.character:morehp', None, morehp)

        # 캐릭터 강화 아이템
        game_world.add_collision_pairs('server.character:enhance', server.character, None)

        enhance = Enhance(54, 3)
        game_world.add_object(enhance, 2)
        game_world.add_collision_pairs('server.character:enhance', None, enhance)

    elif stage == 7:
        stage_info = stage_data[stage]

        # 캐릭터
        server.character = Character()
        game_world.add_object(server.character, 1)

        # UI
        ui = UI()
        game_world.add_object(ui, 3)

        server.background = Background(5)
        game_world.add_object(server.background, 0)

        game_world.add_collision_pairs('server.character:ladder', server.character, None)

        # a, d 판정만 있는 바닥
        game_world.add_collision_pairs('server.character:wall', server.character, None)

        for j, i_range in stage_info['floor_positions']:
            walls = [Wall(i, j, 11) for i in i_range]
            game_world.add_objects(walls, 0)
            for wall in walls:
                game_world.add_collision_pairs('server.character:wall', None, wall)

        # a, d, 점프, 추락 판정이 있는 블럭
        game_world.add_collision_pairs('server.character:ground', server.character, None)

        for j, i_range in stage_info['ground_positions']:
            grounds = [Ground(i, j, 10) for i in i_range]
            game_world.add_objects(grounds, 0)
            for ground in grounds:
                game_world.add_collision_pairs('server.character:ground', None, ground)

        # 포탈
        game_world.add_collision_pairs('server.character:portal', server.character, None)

        portal = Portal(34, 4, 3)
        game_world.add_object(portal, 0)
        game_world.add_collision_pairs('server.character:portal', None, portal)

def finish():
    game_world.clear()
    pass

def update():
    game_world.update()
    game_world.handle_collisions()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def pause():
    pass

def resume():
    pass