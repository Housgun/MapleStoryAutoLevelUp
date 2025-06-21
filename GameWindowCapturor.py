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

if sys.platform.startswith("win"):
    from windows_capture import WindowsCapture, Frame, InternalCaptureControl
else:
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

        if sys.platform.startswith("win"):
            # Use windows_capture for Windows
            self.capture = WindowsCapture(window_name=self.window_title)
            self.capture.event(self.on_frame_arrived)
            self.capture.event(self.on_closed)
            threading.Thread(target=self.capture.start, daemon=True).start()
        else:
            # macOS / others: use mss to capture screen region
            windows = gw.getWindowsWithTitle(self.window_title)
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

    def on_frame_arrived(self, frame, capture_control):
        '''
        Frame arrived callback: store frame into buffer with lock.
        '''
        with self.lock:
            self.frame = frame.frame_buffer
        time.sleep(0.033)  # Cap FPS to ~30

    def capture_loop(self):
        '''
        Capture loop for mss-based grabbing on macOS.
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
