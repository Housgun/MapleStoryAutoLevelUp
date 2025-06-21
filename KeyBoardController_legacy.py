import threading
import time
from pynput import keyboard
import pygetwindow as gw

class KeyBoardController():
    '''
    KeyBoardController
    '''
    def __init__(self, cfg):
        self.cfg = cfg
        self.command = ""
        self.t_last_up = 0.0
        self.t_last_down = 0.0
        self.t_last_toggle = 0.0
        self.t_last_screenshot = 0.0
        self.is_enable = True
        self.window_title = cfg.game_window_title
        self.attack_key = ""
        self.debounce_interval = 1 # second
        self.is_need_screen_shot = False
        self.controller = keyboard.Controller()

        # set up attack key
        if cfg.is_use_aoe:
            self.attack_key = cfg.aoe_skill_key
        else:
            self.attack_key = cfg.magic_claw_key

        # Start keyboard control thread
        threading.Thread(target=self.run, daemon=True).start()

        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

    def on_press(self, key):
        '''
        Handle key press events.
        '''
        try:
            key.char
        except AttributeError:
            if key == keyboard.Key.f1:
                if time.time() - self.t_last_toggle > self.debounce_interval:
                    self.toggle_enable()
                    self.t_last_toggle = time.time()
            elif key == keyboard.Key.f2:
                if time.time() - self.t_last_screenshot > self.debounce_interval:
                    self.is_need_screen_shot = True
                    self.t_last_screenshot = time.time()

    def toggle_enable(self):
        '''
        toggle_enable
        '''
        self.is_enable = not self.is_enable
        print(f"Player pressed F1, is_enable:{self.is_enable}")

        # Make sure all key are released
        self.release_all_key()

    def press_key(self, key, duration):
        '''
        Simulates a key press for a specified duration
        '''
        self.controller.press(key)
        time.sleep(duration)
        self.controller.release(key)

    def disable(self):
        '''
        disable keyboard controlller
        '''
        self.is_enable = False

    def enable(self):
        '''
        enable keyboard controlller
        '''
        self.is_enable = True

    def set_command(self, new_command):
        '''
        Set keyboard command
        '''
        self.command = new_command

    def is_game_window_active(self):
        '''
        Check if the game window is currently the active (foreground) window.

        Returns:
        - True
        - False
        '''
        active_window = gw.getActiveWindow()
        return active_window is not None and self.window_title in active_window.title

    def release_all_key(self):
        '''
        Release all key
        '''
        self.controller.release("left")
        self.controller.release("right")
        self.controller.release("up")
        self.controller.release("down")

    def run(self):
        '''
        run
        '''
        while True:

            # Check if game window is active
            if not self.is_enable or not self.is_game_window_active():
                time.sleep(0.033)
                continue

            # check if is needed to release 'Up' key
            if time.time() - self.t_last_up > self.cfg.up_drag_duration:
                self.controller.release("up")

            # check if is needed to release 'Down' key
            if time.time() - self.t_last_down > self.cfg.down_drag_duration:
                self.controller.release("down")

            if self.command == "walk left":
                self.controller.release("right")
                self.controller.press("left")

            elif self.command == "walk right":
                self.controller.release("left")
                self.controller.press("right")

            elif self.command == "jump left":
                self.controller.release("right")
                self.controller.press("left")
                self.press_key(self.cfg.jump_key, 0.02)
                self.controller.release("left")

            elif self.command == "jump right":
                self.controller.release("left")
                self.controller.press("right")
                self.press_key(self.cfg.jump_key, 0.02)
                self.controller.release("right")

            elif self.command == "jump down":
                self.controller.release("right")
                self.controller.release("left")
                self.controller.press("down")
                self.press_key(self.cfg.jump_key, 0.02)
                self.controller.release("down")

            elif self.command == "jump":
                self.controller.release("left")
                self.controller.release("right")
                self.press_key(self.cfg.jump_key, 0.02)

            elif self.command == "up":
                self.controller.release("down")
                self.controller.press("up")
                self.t_last_up = time.time()

            elif self.command == "down":
                self.controller.release("up")
                self.controller.press("down")
                self.t_last_down = time.time()

            if self.command == "teleport left":
                self.controller.release("right")
                self.controller.press("left")
                self.press_key(self.cfg.teleport_key, 0.02)

            elif self.command == "teleport right":
                self.controller.release("left")
                self.controller.press("right")
                self.press_key(self.cfg.teleport_key, 0.02)

            elif self.command == "teleport up":
                self.controller.press("up")
                self.press_key(self.cfg.teleport_key, 0.02)
                self.controller.release("up")

            elif self.command == "teleport down":
                self.controller.press("down")
                self.press_key(self.cfg.teleport_key, 0.02)
                self.controller.release("down")

            elif self.command == "attack":
                self.press_key(self.attack_key, 0.02)

            elif self.command == "attack left":
                self.controller.release("right")
                self.controller.press("left")
                self.press_key(self.attack_key, 0.02)
                self.controller.release("left")

            elif self.command == "attack right":
                self.controller.release("left")
                self.controller.press("right")
                self.press_key(self.attack_key, 0.02)
                self.controller.release("right")

            elif self.command == "stop":
                self.release_all_key()

            elif self.command == "heal":
                self.press_key(self.cfg.heal_key, 0.02)
                self.command = ""

            elif self.command == "add mp":
                self.press_key(self.cfg.add_mp_key, 0.02)
                self.command = ""

            else:
                pass

            time.sleep(0.033) # Cap at 30 fps
