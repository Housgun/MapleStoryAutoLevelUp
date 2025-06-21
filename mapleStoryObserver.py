"""Passive MapleStory window analyzer.

This script runs the full MapleStoryBot logic but disables any
keyboard automation. It continuously captures the MapleStory
window, processes game state, and logs relevant information.
Press 'q' to quit.
"""

import argparse
import time
import cv2

from logger import logger
from mapleStoryAutoLevelUp import MapleStoryBot


def main():
    parser = argparse.ArgumentParser(description="Run MapleStory bot in read-only mode")
    parser.add_argument(
        '--patrol',
        action='store_true',
        help='Enable patrol mode'
    )
    parser.add_argument(
        '--map',
        type=str,
        default='lost_time_1',
        help='Specify the map name'
    )
    parser.add_argument(
        '--monsters',
        type=str,
        default='evolved_ghost',
        help='Comma-separated list of monsters to detect'
    )
    parser.add_argument(
        '--attack',
        type=str,
        default='magic_claw',
        help='Choose attack method, "magic_claw" or "aoe_skill"'
    )

    args = parser.parse_args()

    # Force disable automation
    args.disable_control = True

    bot = MapleStoryBot(args)

    while True:
        t_start = time.time()
        bot.run_once()
        logger.info(
            f"hp={bot.hp_ratio:.2f} mp={bot.mp_ratio:.2f} exp={bot.exp_ratio:.2f} "
            f"player={bot.loc_player} command={bot.kb.command}"
        )

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_duration = time.time() - t_start
        target_duration = 1.0 / bot.cfg.fps_limit
        if frame_duration < target_duration:
            time.sleep(target_duration - frame_duration)

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
