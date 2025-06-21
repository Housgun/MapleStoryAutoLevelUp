import time

import cv2

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


if __name__ == "__main__":
    img = read_game_window()
    if img is not None:
        cv2.imshow("game", img)
        cv2.waitKey(0)
    else:
        print("Failed to capture game window")
