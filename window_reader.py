import time
from threading import Event

import cv2
from pynput import keyboard

from config.config import Config
from GameWindowCapturor import GameWindowCapturor


def read_game_window(timeout: float = 1.0):
    """Return a single frame from the MapleStory window.

    Parameters
    ----------
    timeout : float
        Maximum time in seconds to wait for the first frame.

    Returns
    -------
    numpy.ndarray or None
        BGR image of the game window frame, or ``None`` if no frame is captured
        before the timeout.
    """
    captor = GameWindowCapturor(Config)
    frame = None
    end_time = time.time() + timeout

    while frame is None and time.time() < end_time:
        frame = captor.get_frame()
        if frame is None:
            time.sleep(0.033)

    return frame


def main():
    """Interactive window reader controlled with F1/F2."""
    captor = None
    running = Event()
    stop = Event()

    def on_press(key):
        nonlocal captor
        if key == keyboard.Key.f1:
            if not running.is_set():
                captor = GameWindowCapturor(Config)
                running.set()
                print("Started reading game window")
        elif key == keyboard.Key.f2:
            if running.is_set():
                stop.set()
                running.clear()
                print("Stopped reading game window")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while not stop.is_set():
        if running.is_set() and captor:
            frame = captor.get_frame()
            if frame is not None:
                cv2.imshow("game", frame)
                if cv2.waitKey(1) & 0xFF == 27:
                    stop.set()
        else:
            time.sleep(0.1)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
