import os

cimport numpy as np
import cv2

np.import_array()


cdef list ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']
DIMS = os.get_terminal_size()
DIMS = [int(DIMS[0]), int(DIMS[1])]
cdef TERMINAL_COLUMNS = DIMS[0]
cdef TERMINAL_ROWS = DIMS[1]

cpdef str c_load_frame(np.ndarray frame):
    """Resizes the frame to the terminal width & height, and then converts it to a string"""
    cdef tuple dimension = (TERMINAL_COLUMNS, TERMINAL_ROWS)

    cdef np.ndarray resized_frame = cv2.resize(frame, dimension, interpolation=cv2.INTER_LINEAR)

    cdef str frame_display = ''

    for row in resized_frame:
        for pixel in row:
            # accentuate the black and white
            if pixel >= 200:
                pixel += 35
                if pixel >= 255:
                    pixel = 255

            elif pixel <= 120:
                pixel -= 40
                if pixel <= 0:
                    pixel = 0

            pixel = int(pixel / 25)

            frame_display += ASCII_CHARS[pixel]

    return frame_display