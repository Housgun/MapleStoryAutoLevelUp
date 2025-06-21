'''
Execute this script:
python mapleStoryAutoLevelUp.py --map cloud_balcony --monster brown_windup_bear,pink_windup_bear
'''
# Standard import
import time
import threading
import sys

import cv2
import numpy as np
import pygetwindow as gw
import mss

# local import
from logger import logger

class GameWindowCapturor:
    '''
    GameWindowCapturor
    '''
    def __init__(self, cfg):
        self.cfg = cfg
        self.window_title = cfg.game_window_title
        self.frame = None
        self.lock = threading.Lock()

        self.running = True

        # Locate the game window and start capturing with mss
        # ``pygetwindow`` may not implement ``getWindowsWithTitle`` on all
        # platforms.  Fall back to scanning all windows if needed.
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
        except AttributeError:
            windows = [w for w in gw.getAllWindows() if self.window_title in w.title]

        if not windows:
            raise RuntimeError(f"Game window not found: {self.window_title}")

        win = windows[0]
        self.monitor = {
            "top": win.top,
            "left": win.left,
            "width": win.width,
            "height": win.height,
        }
        self.sct = mss.mss()
        threading.Thread(target=self.capture_loop, daemon=True).start()

        # Wait briefly for the first frame
        time.sleep(0.1)

        # Check if game window size is as expected
        if self.frame is None or self.frame.shape[:2] != cfg.window_size:
            logger.error(f"Invalid window size: {self.frame.shape[:2]} (expected {cfg.window_size})")
            logger.error("Please use windowed mode & smallest resolution.")
            raise RuntimeError(f"Unexpected window size: {self.frame.shape[:2]}")

    def capture_loop(self):
        '''
        Capture loop for grabbing frames with ``mss``.
        '''
        while self.running:
            img = np.array(self.sct.grab(self.monitor))
            with self.lock:
                self.frame = img
            time.sleep(0.033)

    def on_closed(self):
        '''
        Capture closed callback.
        '''
        logger.warning("Capture session closed.")
        self.running = False
        cv2.destroyAllWindows()

    def get_frame(self):
        '''
        Safely get latest game window frame.
        '''
        with self.lock:
            if self.frame is None:
                return None
            return cv2.cvtColor(self.frame, cv2.COLOR_BGRA2BGR)
