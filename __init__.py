import time
import datetime
import os
from pathlib import Path

import cv2
import numpy as np

if os.name == 'nt':
    from utils.win32 import enable_virtual_processing

ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']


def sleep_until(target: datetime.datetime) -> None:
    now = datetime.datetime.now()
    if now > target:
        return

    # assert target > now, f'Now: {now} | Target Display Time: {target} | Difference: {now-target}'

    time.sleep((target - now).total_seconds())


def convert_to_greyscale(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, 0, cv2.COLOR_RGB2GRAY)


def load_frame(frame: np.ndarray, columns: int, rows: int) -> str:
    """Resizes the frame to the terminal width & height, and then converts it to a string"""
    dimension = (columns, rows)

    frame = cv2.resize(frame, dimension, interpolation=cv2.INTER_LINEAR)

    frame_display: str = ''

    for row in frame:
        for pixel in row:
            # pixel colour format is BGRA; because we've already gotten the black & white version of
            # the frame, the colour will be always something like (251, 251, 251), i.e. r == g == b
            rgb = pixel[0]

            # accentuate the black and white; note this accentuation takes ~0.6559 secs
            # with an entire iteration taking ~2.097 secs
            if rgb >= 200:
                rgb += 35
                if rgb >= 255:
                    rgb = 255

            elif rgb <= 120:
                rgb -= 40
                if rgb <= 0:
                    rgb = 0

            rgb = int(rgb / 25)

            frame_display += ASCII_CHARS[rgb]

    return frame_display


def display_frames(final_display: list[str], frame_rate: int) -> None:
    time_between_frames = 1 / frame_rate

    # this ensures each frame is printed at the desired frame rate
    target_frame_display = datetime.datetime.now()

    for frame in final_display:
        # ctypes.windll.kernel32.SetConsoleCursorPosition(STD_OUTPUT_HANDLE, COORD(0, 0))
        print('\x1b[2J')
        print(frame)

        target_frame_display += datetime.timedelta(seconds=time_between_frames)
        sleep_until(target_frame_display)


def main():
    video = cv2.VideoCapture(str(Path(__file__).parent / 'noot_8k.mp4'))
    terminal_width, terminal_height = os.get_terminal_size()

    frame_rate = int(video.get(cv2.CAP_PROP_FPS))
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f'There are {total_frames} frames in this video.')

    frames: list[np.ndarray] = []

    start = time.perf_counter()
    for frame_num in range(total_frames):
        print(f'Progress : Converting frame {frame_num + 1} of {total_frames} to greyscale', end='\r')

        # more_frames represents whether or not a valid frame has actually been retrieved
        # i.e. `False`` is returned when frame 322 is reached of a 321 frame video
        more_frames, frame = video.read()
        assert more_frames  # this should never raise an AssertionError

        frames.append(convert_to_greyscale(frame))
    end = time.perf_counter()

    print(f'Progress : Converting frame {frame_num + 1} of {total_frames} to greyscale (took {end-start:.2f} seconds)') # type: ignore

    final_display: list[str] = []
    start = time.perf_counter()
    for frame_num, frame in enumerate(frames, start=1):
        print(f'Progress : Loading frame {frame_num} of {total_frames}', end='\r')
        final_display.append(load_frame(frame, terminal_width, terminal_height))
    end = time.perf_counter()
    print(f'Progress : Loading frame {frame_num} of {total_frames} (took {end-start:.2f} seconds)') # type: ignore

    display_frames(final_display, frame_rate)


if __name__ == '__main__':
    on_windows = os.name == 'nt'
    # Windows' command prompt (cmd) does support ANSI escape sequences
    # however, this is only for itself, and not programs running on it,
    # thus, we'll need to enable it ourselves.
    system_has_native_ansi = not on_windows or enable_virtual_processing() # pyright: ignore reportUndefinedVariable

    if system_has_native_ansi is False:
        raise OSError('Native ANSI is not enabled, which is required for clearing the terminal.')

    main()
