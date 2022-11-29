import time
import datetime
import os
import argparse
from itertools import repeat
from pathlib import Path

import cv2
import numpy as np

if os.name == 'nt':
    from utils.win32 import enable_virtual_processing

ASCII_CHARS = np.array([x for i in ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.'] for x in repeat(i, 5)])
TERMINAL_ROWS, TERMINAL_COLUMNS = os.get_terminal_size()


parser = argparse.ArgumentParser(
    prog='ascii_player',
    description='Converts a video into an ASCII representation, frame-by-frame'
)
parser.add_argument('-v', '--video', required=True, help='An absolute path to the video to convert')
parser.add_argument('-fps', '--frame_rate', default=None, type=int, help='The desired frame rate, consider each frame is getting rendered in the delay between each frame.')
args = parser.parse_args()


def sleep_until(target: datetime.datetime) -> None:
    now = datetime.datetime.now()
    if now > target:
        return

    time.sleep((target - now).total_seconds())


def convert_to_greyscale(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


def render_frame(frame: np.ndarray) -> None:
    frame = convert_to_greyscale(frame)
    frame = cv2.resize(frame, (TERMINAL_ROWS, TERMINAL_COLUMNS), interpolation=cv2.INTER_LINEAR)

    frame //= 5  # type: ignore
    content = ASCII_CHARS[frame]
    final_display = '\n'.join(''.join(row) for row in content)

    print('\x1b[2J', final_display)


def main():
    video = cv2.VideoCapture(str(Path(__file__).parent / args.video))

    frame_rate = args.frame_rate or int(video.get(cv2.CAP_PROP_FPS))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    assert total_frames > 0, "There needs to be at least one frame in your video!"

    print(f'There are {total_frames} frames in this video.')
    time.sleep(3)

    # this ensures each frame is printed at the desired frame rate
    time_between_frames = 1 / frame_rate
    target_frame_display = datetime.datetime.now()
    more_frames = True

    while more_frames:
        # more_frames represents whether or not a valid frame has actually been retrieved
        # i.e. `False`` is returned when frame 322 is reached of a 321 frame video
        more_frames, frame = video.read()
        render_frame(frame)

        target_frame_display += datetime.timedelta(seconds=time_between_frames)
        sleep_until(target_frame_display)


if __name__ == '__main__':
    on_windows = os.name == 'nt'
    # Windows' command prompt (cmd) does support ANSI escape sequences
    # however, this is only for itself, and not programs running on it,
    # thus, we'll need to enable it ourselves.
    system_has_native_ansi = not on_windows or enable_virtual_processing()  # pyright: ignore reportUndefinedVariable doesn't understand this narrowing

    if system_has_native_ansi is False:
        raise OSError('Native ANSI is not enabled, which is required for clearing the terminal.')

    main()
