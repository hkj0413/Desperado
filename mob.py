# monsters.py (완성본: on_hit 버그 픽스 + toughness + 리스폰 로직 포함)

import copy
import random

import server
import character
import game_framework

from pico2d import load_image, load_wav, draw_rectangle, clamp

# ------------------------------------------------
# 설정
# ------------------------------------------------
# 맞추면 스택이 줄어드는 탄종
CONSUME_PROJECTILES = {'normalrf', 'normalrfsp', 'normalhg'}

# ------------------------------------------------
# 데이터 테이블
# ------------------------------------------------
MONSTER_DEFAULTS = {
    "hp": 1,
    "speed": 1.0,
    "patrol": {"range": 90.0},

    # AABB: center 기준. get_bb() = (x±half_w, (y+center_offset_y)±half_h)
    "bbox": {"half_w": 15.0, "half_h": 15.0, "center_offset_y": 0.0},

    "animations": {
        "Idle": {"path": "", "frames": 1},
        "Walk": {"path": "", "frames": 1},
        "Hit":  {"path": "", "frames": 1},
        "Die":  {"path": "", "frames": 1},
    },

    # 모든 몬스터 공통 피격 사운드 (프로젝트에서 mp3를 load_wav로 사용하던 방식 그대로)
    "sounds": {"hit": "./Sound/Hitsound.mp3"},

    # 드로우 파라미터(스프라이트 위치/크기/좌우 보정)
    "draw": {"w": 48, "h": 48, "offset_x": 0.0, "offset_y": 0.0, "offset_face": 0.0},

    # 스턴 저항(0.0=저항 없음, 0.5=절반만 적용, 1.0=완전 면역)
    "toughness": 0.0,

    # 어그로: 피격 시에만 플레이어 방향을 보고 Walk로 전환
    "aggro": {"on_hit": False},
}

MONSTER_TEMPLATES = {
    "Spore": {
        "hp": 2,
        "speed": 1.0,
        "patrol": {"range": 90.0},
        "bbox": {"half_w": 15.0, "half_h": 15.0, "center_offset_y": -2.0},
        "animations": {
            "Idle": {"path": "./Mob/Spore/Idle (%d).png", "frames": 2},
            "Walk": {"path": "./Mob/Spore/Walk (%d).png", "frames": 4},
            "Hit":  {"path": "./Mob/Spore/Hit (1).png",   "frames": 1},
            "Die":  {"path": "./Mob/Spore/Die (%d).png",  "frames": 4}
        },
        "draw": {"w": 50, "h": 50, "offset_x": 0.0, "offset_y": -2.0, "offset_face": 0.0},
        "toughness": 0.0,
        "aggro": {"on_hit": False},
    },

    "Slime": {
        "hp": 3,
        "speed": 1.5,
        "patrol": {"range": 120.0},
        "bbox": {"half_w": 25.0, "half_h": 17.5, "center_offset_y": 0.5},
        "animations": {
            "Idle": {"path": "./Mob/Slime/Idle (%d).png", "frames": 3},
            "Walk": {"path": "./Mob/Slime/Walk (%d).png", "frames": 4},
            "Hit":  {"path": "./Mob/Slime/Hit (1).png",   "frames": 1},
            "Die":  {"path": "./Mob/Slime/Die (%d).png",  "frames": 3}
        },
        "draw": {"w": 70, "h": 85, "offset_x": 0.0, "offset_y": 22.0, "offset_face": 10.0},
        "toughness": 0.0,
        "aggro": {"on_hit": False},
    },

    "Pig": {
        "hp": 4,
        "speed": 0.9,
        "patrol": {"range": 90.0},
        "bbox": {"half_w": 30.0, "half_h": 17.5, "center_offset_y": 0.5},
        "animations": {
            "Idle": {"path": "./Mob/Pig/Idle (%d).png", "frames": 2},
            "Walk": {"path": "./Mob/Pig/Walk (%d).png", "frames": 3},
            "Hit":  {"path": "./Mob/Pig/Hit (1).png",   "frames": 1},
            "Die":  {"path": "./Mob/Pig/Die (%d).png",  "frames": 3}
        },
        "draw": {"w": 70, "h": 60, "offset_x": 0.0, "offset_y": 8.0, "offset_face": 3.0},
        "toughness": 0.0,
        "aggro": {"on_hit": False},
    },
}

# ------------------------------------------------
# 리소스 캐시
# ------------------------------------------------
_ASSET_IMG_CACHE = {}
_ASSET_SND_CACHE = {}

def load_images_cached(path_fmt, frames):
    if not path_fmt or frames <= 0:
        return []
    key = (path_fmt, frames)
    if key in _ASSET_IMG_CACHE:
        return _ASSET_IMG_CACHE[key]
    if "%d" in path_fmt:
        imgs = [load_image(path_fmt % idx) for idx in range(1, frames + 1)]
    else:
        imgs = [load_image(path_fmt)]
    _ASSET_IMG_CACHE[key] = imgs
    return imgs

def load_sound_cached(path: str, volume: int = 8):
    if not path:
        return None
    if path in _ASSET_SND_CACHE:
        return _ASSET_SND_CACHE[path]
    s = load_wav(path)  # 프로젝트 스타일(mp3도 load_wav로)
    try:
        s.set_volume(volume)
    except Exception:
        pass
    _ASSET_SND_CACHE[path] = s
    return s

# ------------------------------------------------
# 유틸
# ------------------------------------------------
def deep_merge(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            deep_merge(dst[k], v)
        else:
            dst[k] = copy.deepcopy(v)
    return dst

def get_template(name: str):
    base = copy.deepcopy(MONSTER_DEFAULTS)
    tpl = MONSTER_TEMPLATES.get(name, {})
    return deep_merge(base, tpl)

def _projectile_tag(group: str) -> str:
    # 'normalrf:monster' -> 'normalrf'
    return group.split(':', 1)[0] if ':' in group else group

# ------------------------------------------------
# 상태 규칙
# ------------------------------------------------
INVULN_STATES = {"Die", "RespawnWait"}              # 데미지 무시
NON_ATTACK_STATES = {"Die", "RespawnWait", "Stun"}  # 플레이어 접촉공격 불가

# ------------------------------------------------
# 몬스터 본체
# ------------------------------------------------
class Monster:
    def __init__(self, tpl: dict, spawn: dict, tile_size=40.0):
        self.tpl = tpl
        i, j = spawn.get("i", 0), spawn.get("j", 0)
        self.x = i * tile_size + tile_size / 2
        self.y = j * tile_size + tile_size / 2
        self.base_x = self.x
        self.sx = 0.0
        self.face_dir = spawn.get("face", random.choice([-1, 1]))

        # stats
        self.max_hp = tpl["hp"]
        self.hp = self.max_hp
        self.speed = tpl["speed"]
        self.range = tpl["patrol"]["range"]
        self.toughness = float(tpl.get("toughness", 0.0))  # 스턴 저항(0~1)
        self.aggro_on_hit = bool(tpl.get("aggro", {}).get("on_hit", False))

        # bbox/draw
        bb = tpl["bbox"]
        self.half_w = bb["half_w"]
        self.half_h = bb["half_h"]
        self.center_offset_y = bb.get("center_offset_y", 0.0)

        d = tpl["draw"]
        self.draw_w = d["w"]; self.draw_h = d["h"]
        self.draw_off_x = d.get("offset_x", 0.0)
        self.draw_off_y = d.get("offset_y", 0.0)
        self.draw_off_face = d.get("offset_face", 0.0)

        # assets
        self.images = {name: load_images_cached(spec["path"], spec["frames"])
                       for name, spec in tpl["animations"].items()}
        self.sounds = {k: load_sound_cached(v) for k, v in tpl.get("sounds", {}).items()}

        # state
        self.state = random.choice(["Idle", "Walk"])
        self.frame = 0.0
        self.timer = 0.0           # 0.25초 틱 누적
        self.temp = 0              # 일부 상태에서 쓰는 카운터(리스폰 등)
        self.prev_state = None
        self.invuln = 0.0          # 피격 무적 타이머
        self.stun_timer = 0.0
        self._pending_onhit_aggro = False  # 피격 후 Hit→Walk 전환 타이밍에 1회 적용할 어그로

    # --- 상태 전환 헬퍼 ---
    def _change_state(self, new_state: str, *, reset_frame=True, reset_temp=True):
        if self.state != new_state:
            self.state = new_state
            self.timer = 0.0       # 전환 시 틱 누적 초기화(버그 원인 방지)
            if reset_frame:
                self.frame = 0.0
            if reset_temp:
                self.temp = 0

    # --- 상태 질의 ---
    def is_invulnerable(self):
        return (self.invuln > 0.0) or (self.state in INVULN_STATES)

    def can_take_damage(self):
        return not self.is_invulnerable()

    def can_attack_player(self):
        # 무적 or 비공격 상태면 접촉공격 불가 (요구사항 충족)
        return (self.invuln <= 0.0) and (self.state not in NON_ATTACK_STATES)

    # --- 엔진 훅 ---
    def update(self):
        dt = game_framework.frame_time
        RUN_SPEED_PPS = character.RUN_SPEED_PPS
        self.sx = self.x - server.background.window_left

        # timers
        self.invuln = max(0.0, self.invuln - dt)
        self.timer += dt

        # ---- 0.25s tick ----
        if self.timer >= 0.25:
            self.timer = 0.0
            next_state = self.state  # 한 번만 전환되게 예약

            if self.state == "Hit":
                # Hit가 끝나는 이 타이밍에만 on_hit 어그로 적용 후 Walk 전환
                if self._pending_onhit_aggro:
                    if server.character.x < self.x:
                        self.face_dir = -1
                    elif server.character.x > self.x:
                        self.face_dir = 1
                    self._pending_onhit_aggro = False
                next_state = "Walk"

            elif self.state == "Idle":
                self.temp += 1
                if self.temp == 4 or random.randint(1, 20) == 1:
                    next_state = "Walk"

            elif self.state == "Walk":
                if random.randint(1, 20) == 1:
                    next_state = "Idle"

            elif self.state == "RespawnWait":
                self.temp += 1
                if self.temp >= 20:  # 약 5초 숨김 후 리스폰
                    self.hp = self.max_hp
                    self.x = self.base_x
                    self.face_dir = random.choice([-1, 1])
                    next_state = "Idle"

            # 상태 적용
            if next_state != self.state:
                self._change_state(next_state)

        # ---- 스턴 카운트다운 ----
        if self.state == "Stun":
            self.stun_timer = max(0.0, self.stun_timer - dt)
            if self.stun_timer <= 0.0:
                self._change_state("Walk")

        # ---- 이동/순찰 ----
        if self.state == "Walk":
            self.x += self.speed * self.face_dir * RUN_SPEED_PPS * dt
            if self.x <= self.base_x - self.range or self.x >= self.base_x + self.range:
                self.face_dir *= -1
            self.x = clamp(self.base_x - self.range, self.x, self.base_x + self.range)

        # ---- 애니메이션 ----
        if self.state == "Idle":
            n = max(1, len(self.images["Idle"]))
            self.frame = (self.frame + 2.0 * 1.5 * dt) % n

        elif self.state == "Walk":
            n = max(1, len(self.images["Walk"]))
            self.frame = (self.frame + 4.0 * 1.5 * dt) % n

        elif self.state == "Hit":
            self.frame = 0.0

        elif self.state == "Die":
            n = max(1, len(self.images["Die"]))
            self.frame += 4.0 * 2.0 * dt
            if self.frame >= n:
                # 죽는 애니 끝 → 숨김 대기
                self._change_state("RespawnWait")

        elif self.state == "RespawnWait":
            pass

        elif self.state == "Stun":
            # Hit 스프라이트 유지
            self.frame = 0.0

    def draw(self):
        if self.state == "RespawnWait":
            return  # 숨김

        if -30 <= self.sx <= 1650:
            # Stun은 Hit 스프라이트로 통일
            if self.state == "Die":
                anim_name = "Die"
            elif self.state in ("Hit", "Stun"):
                anim_name = "Hit"
            else:
                anim_name = self.state

            imgs = self.images.get(anim_name) or self.images.get("Idle", [])
            if imgs:
                idx = int(self.frame)
                idx = max(0, min(idx, len(imgs) - 1))
                flip = 'h' if self.face_dir == 1 else ''
                eff_x = self.sx + self.draw_off_x + (-self.face_dir) * self.draw_off_face
                eff_y = self.y + self.draw_off_y
                imgs[idx].composite_draw(0, flip, eff_x, eff_y, self.draw_w, self.draw_h)

            if getattr(character, "God", False):
                l, b, r, t = self.get_bb()
                draw_rectangle(l - server.background.window_left, b, r - server.background.window_left, t)

    # --- 상호작용 ---
    def get_bb(self):
        cy = self.y + self.center_offset_y
        return (self.x - self.half_w, cy - self.half_h,
                self.x + self.half_w, cy + self.half_h)

    def handle_collision(self, group, other):
        # 캐릭터 접촉 데미지: 무적/비공격 상태면 미적용
        if group == 'server.character:monster' and self.can_attack_player():
            if hasattr(other, 'take_damage'):
                other.take_damage(1)
            return

        # 투사체 ↔ 몬스터
        if group.endswith(':monster'):
            if self.can_take_damage():
                dmg = other.give_damage() if hasattr(other, 'give_damage') else 0
                if dmg:
                    self.take_damage(dmg)
                    tag = _projectile_tag(group)
                    if tag in CONSUME_PROJECTILES and hasattr(other, 'get_count'):
                        other.get_count()
            return

    def take_damage(self, dmg):
        if not self.can_take_damage():
            return
        self.hp = max(0, self.hp - dmg)
        s = self.sounds.get("hit")
        if s: s.play()

        if self.hp <= 0:
            self._change_state("Die")
        else:
            # 반드시 Hit로 들어간 뒤 무적 0.25초 유지
            self._change_state("Hit")
            self.invuln = 0.25

            # on_hit이면 Hit가 끝나는 틱에서만 방향 전환 + Walk
            if self.aggro_on_hit:
                self._pending_onhit_aggro = True

    def take_stun(self, duration_sec: float):
        # toughness(0~1) 적용: effective = duration * (1 - clamp(toughness,0,1))
        scale = 1.0 - max(0.0, min(1.0, self.toughness))
        eff = max(0.0, float(duration_sec)) * scale
        if eff <= 0.0:
            return
        # 무적/사망/리스폰 대기 중이면 스턴 무시
        if self.state in INVULN_STATES:
            return
        self.stun_timer = max(self.stun_timer, eff)
        self._change_state("Stun")  # 프레임/타이머 초기화

# ------------------------------------------------
# 팩토리 / 리소스 해제
# ------------------------------------------------
def create_monster(type_name: str, i: int, j: int, face: int = None, tile_size: float = 40.0):
    tpl = get_template(type_name)
    spawn = {"i": i, "j": j}
    if face is not None:
        spawn["face"] = face
    return Monster(tpl, spawn, tile_size=tile_size)

def release_assets():
    _ASSET_IMG_CACHE.clear()
    _ASSET_SND_CACHE.clear()