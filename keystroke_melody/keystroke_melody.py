"""
keystroke_melody.py
Billentyűleütés dallamlejátszó Windows-ra.
Minden gombnyomáskor lejátszik egy hangot a dallamból.

Használat:
    python keystroke_melody.py

Ha exe-ként töltöd le, csak futtasd, és ESC-kel lépj ki.
"""

import threading
import sys
import winsound
from pynput import keyboard

# ------------------- CONFIG -------------------
MELODY = [
    (392, 300), (392, 300), (440, 300), (440, 300), (392, 300), (392, 300), (330, 600),
    (349, 300), (349, 300), (330, 300), (330, 300), (294, 600),
    (392, 300), (392, 300), (349, 300), (349, 300), (330, 300), (330, 300), (294, 600),
    (392, 300), (392, 300), (440, 300), (440, 300), (392, 300), (392, 300), (330, 600)
]

DEBUG = False
IGNORE_MODIFIERS = True
MAX_CONCURRENT_THREADS = 8
# ----------------------------------------------

_note_index = 0
_lock = threading.Lock()
_active_threads = []


def _play_note_thread(freq, duration_ms):
    try:
        if DEBUG:
            print(f"[play] freq={freq} dur={duration_ms}ms")
        winsound.Beep(int(freq), int(duration_ms))
    except Exception as e:
        if DEBUG:
            print("Beep error:", e)
    finally:
        with _lock:
            global _active_threads
            _active_threads = [t for t in _active_threads if t.is_alive()]


def play_next_note():
    global _note_index, _active_threads
    with _lock:
        freq, dur = MELODY[_note_index]
        _note_index = (_note_index + 1) % len(MELODY)

        _active_threads = [t for t in _active_threads if t.is_alive()]
        if len(_active_threads) >= MAX_CONCURRENT_THREADS:
            return

        t = threading.Thread(target=_play_note_thread, args=(freq, dur), daemon=True)
        _active_threads.append(t)
        t.start()


def on_press(key):
    try:
        k = key.char
        play_next_note()
    except AttributeError:
        if IGNORE_MODIFIERS:
            if key == keyboard.Key.esc:
                return False
            return
        else:
            if key == keyboard.Key.esc:
                return False
            play_next_note()


def main():
    print("Keystroke Melody fut... Nyomj ESC-et a kilépéshez.")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    if sys.platform != "win32":
        print("Ez a program Windowsra készült (winsound).")
        sys.exit(1)
    main()
