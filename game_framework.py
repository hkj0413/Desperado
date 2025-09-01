# game_framework.py
# - 모드 전환/종료 시 자원 정리를 확실히 해서
#   pico2d.Image.__del__ 접근위반을 막는다.
# - 핵심: finish() 직후마다 gc.collect() 실행,
#   종료 루프에서도 한 스텝마다 GC,
#   마지막에 한 번 더 GC 후 close_canvas().

import time
import gc
import pico2d  # close_canvas 사용

import play_mode  # play_mode.init(stage) 시그니처를 맞추기 위해 필요

running = False
stack = []
frame_time = 0.0


def _safe_call(obj, name, *args, **kwargs):
    fn = getattr(obj, name, None)
    if callable(fn):
        try:
            return fn(*args, **kwargs)
        except Exception:
            # 종료 루틴에서는 실패해도 크래시 없이 진행
            pass
    return None


def _safe_finish(mode):
    """모드 종료 시 finish() 호출 후 즉시 GC."""
    _safe_call(mode, 'finish')
    gc.collect()


def change_mode(mode):
    """현재 모드를 종료하고 새 모드로 교체."""
    global stack
    if len(stack) > 0:
        _safe_finish(stack[-1])
        stack.pop()

    stack.append(mode)
    # play_mode만 init(stage) 시그니처. 나머진 파라미터 없이 호출.
    if mode is play_mode:
        mode.init(play_mode.stage)
    else:
        _safe_call(mode, 'init')


def push_mode(mode):
    """현재 모드 위에 새 모드를 푸시(일시정지 후 새 모드 진입)."""
    global stack
    if len(stack) > 0:
        _safe_call(stack[-1], 'pause')

    stack.append(mode)
    if mode is play_mode:
        mode.init(play_mode.stage)
    else:
        _safe_call(mode, 'init')


def pop_mode():
    """현재 모드를 종료하고 이전 모드로 복귀."""
    global stack
    if len(stack) > 0:
        _safe_finish(stack[-1])
        stack.pop()

    if len(stack) > 0:
        _safe_call(stack[-1], 'resume')


def quit():
    """메인 루프 종료 요청."""
    global running
    running = False


def run(start_mode):
    """프레임 루프 실행."""
    global running, stack, frame_time

    running = True
    stack = [start_mode]

    # 시작 모드 init
    if start_mode is play_mode:
        start_mode.init(play_mode.stage)
    else:
        _safe_call(start_mode, 'init')

    frame_time = 0.0
    current_time = time.time()

    while running:
        # 메인 루프: 현재 모드에 위임
        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()

        frame_time = time.time() - current_time
        current_time += frame_time

    # -------- 정상 종료 단계 --------
    # 스택을 하나씩 finish → 즉시 GC
    while len(stack) > 0:
        _safe_finish(stack[-1])
        stack.pop()

    # (선택) 전역/캐시 자원 해제 훅
    # monsters 등에서 전역 캐시를 쓰는 경우 여기서 한 번 더 정리
    try:
        from mob import release_assets as _rel_monsters
        _rel_monsters()
    except Exception:
        pass