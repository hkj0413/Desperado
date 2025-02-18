from pico2d import clear_canvas, update_canvas, get_events
from sdl2 import SDL_QUIT, SDL_KEYDOWN, SDLK_1, SDLK_2, SDLK_3, SDLK_4, SDLK_RETURN, SDLK_RIGHT, SDLK_LEFT

import game_framework
import game_world
from guide import Guide

cn = 0
dn = 0

def init():
    global guide
    guide = Guide(dn)
    game_world.add_object(guide, 4)

def finish():
    game_world.remove_object(guide)

def update():
   pass

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def change_guide():
    finish()
    init()

def handle_events():
    global cn, dn
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_RETURN and cn == 0:
            game_framework.pop_mode()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_RETURN and not cn == 0:
            cn = 0
            dn = 0
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_1 and cn == 0:
            cn = 1
            dn = 1
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_2 and cn == 0:
            cn = 2
            dn = 7
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_3 and cn == 0:
            cn = 3
            dn = 13
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_4 and cn == 0:
            cn = 4
            dn = 19
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_RIGHT and cn == 1:
            if dn <= 5:
                dn += 1
            else:
                dn = 1
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_LEFT and cn == 1:
            if dn >= 2:
                dn -= 1
            else:
                dn = 6
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_RIGHT and cn == 2:
            if dn <= 11:
                dn += 1
            else:
                dn = 7
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_LEFT and cn == 2:
            if dn >= 8:
                dn -= 1
            else:
                dn = 12
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_RIGHT and cn == 3:
            if dn <= 17:
                dn += 1
            else:
                dn = 13
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_LEFT and cn == 3:
            if dn >= 14:
                dn -= 1
            else:
                dn = 18
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_RIGHT and cn == 4:
            if dn <= 21:
                dn += 1
            else:
                dn = 19
            change_guide()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_LEFT and cn == 4:
            if dn >= 20:
                dn -= 1
            else:
                dn = 22
            change_guide()


def pause():
    pass

def resume():
    pass