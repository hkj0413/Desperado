import character
import game_framework

EPS_X = 2.0
EPS_Y = 2.0

world = [[] for _ in range(5)]
collision_pairs = {}

def add_collision_pairs(group, a, b):
    if group not in collision_pairs:
        collision_pairs[group] = [ [], [] ]
    if a:
        collision_pairs[group][0].append(a)
    if b:
        collision_pairs[group][1].append(b)

def add_object(o, depth = 0):
    world[depth].append(o)

def add_objects(ol, depth = 0):
    world[depth] += ol

def update():
    for layer in world:
        for o in layer:
            o.update()

def render():
    for layer in world:
        for o in layer:
            o.draw()

def remove_collision_object(o):
    for pairs in collision_pairs.values():
        if o in pairs[0]:
            pairs[0].remove(o)
        if o in pairs[1]:
            pairs[1].remove(o)

def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            remove_collision_object(o)
            del o
            return
    raise ValueError('Cannot delete non existing object')

def clear():
    for layer in world:
        layer.clear()
    collision_pairs.clear()

def get_all_objects():
    all_objects = []
    for layer in world:
        all_objects.extend(layer)
    return all_objects

def collide(a, b):
    al, ab, ar, at = a.get_bb()
    bl, bb, br, bt = b.get_bb()

    if ar < bl: return False
    if al > br: return False
    if at < bb: return False
    if ab > bt: return False

    return True

def x_overlap(al, ar, bl, br):
    return (al < br - EPS_X) and (ar > bl + EPS_X)

def collide_fall(a, b):
    al, ab, ar, at = a.get_bb()
    bl, bb, br, bt = b.get_bb()

    dy = character.fall_velocity * character.RUN_SPEED_PPS * game_framework.frame_time
    if dy <= 0:
        return False

    return x_overlap(al, ar, bl, br) and (ab - EPS_Y <= bt <= ab + dy + EPS_Y)

def collide_jump(a, b):
    al, ab, ar, at = a.get_bb()
    bl, bb, br, bt = b.get_bb()

    dy = -character.jump_velocity * character.RUN_SPEED_PPS * game_framework.frame_time
    if dy >= 0:
        return False

    return x_overlap(al, ar, bl, br) and (at + dy - EPS_Y <= bb <= at + EPS_Y)

def collide_ad(a, b, objects):
    al, ab, ar, at = a.get_bb()
    bl, bb, br, bt = b.get_bb()

    step = a.speed * character.RUN_SPEED_PPS * game_framework.frame_time

    if a.face_dir == 1:
        if (al > br) and ((al - br) <= (step + EPS_X)) and (abs((ab - 1) - bt) <= EPS_Y):
            if any((o.x - 15 <= al <= o.x + 15) and (abs((ab - 1) - (o.y + 15)) <= EPS_Y) for o in objects if o != b):
                return False
            return True

    elif a.face_dir == -1:
        if (ar < bl) and ((bl - ar) <= (step + EPS_X)) and (abs((ab - 1) - bt) <= EPS_Y):
            if any((o.x - 15 <= ar <= o.x + 15) and (abs((ab - 1) - (o.y + 15)) <= EPS_Y) for o in objects if o != b):
                return False
            return True

    return False

def collide_ladder(a, b):
    al, ab, ar, at = a.get_bb()
    bl, bb, br, bt = b.get_bb()

    step = a.speed * character.RUN_SPEED_PPS * game_framework.frame_time

    if not (ab < bt and at > bb):
        return False

    if a.face_dir == 1:
        if (al > br) and ((al - br) <= (step + EPS_X)):
            return True

    elif a.face_dir == -1:
        if (ar < bl) and ((bl - ar) <= (step + EPS_X)):
            return True

    return False

def handle_collisions():
    collision_pairs_copy = list(collision_pairs.items())

    for group, pairs in collision_pairs_copy:
        for a in pairs[0]:
            if character.screen_left - 20 <= a.x <= character.screen_right + 20:
                for b in pairs[1]:
                    if character.screen_left - 20 <= b.x <= character.screen_right + 20:
                        if group == 'server.character:ground':
                            if collide_fall(a, b) and character.Fall:
                                a.handle_collision_fall(group, b)
                                b.handle_collision_fall(group, a)
                            if collide_jump(a, b) and character.Jump:
                                a.handle_collision_jump(group, b)
                                b.handle_collision_jump(group, a)
                        else:
                            if collide(a, b):
                                a.handle_collision(group, b)
                                b.handle_collision(group, a)