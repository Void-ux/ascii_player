import os

if os.name != 'nt':
    raise ImportError("This isn't Windows!")
else:
    import ctypes
    from ctypes import wintypes

    STD_OUTPUT_HANDLE = -11
    COORD = wintypes._COORD

    def enable_virtual_processing():
        try:
            handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            mode = wintypes.DWORD()
            ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            ctypes.windll.kernel32.SetConsoleMode(handle, mode.value or 4)
        # Can get TypeError in testsuite where 'fd' is a Mock() and IOError in python2.7
        except (IOError, OSError, TypeError):
            return False

    def change_console_font_size(size: int = 6):
        LF_FACESIZE = 32

        class COORD(ctypes.Structure):
            _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        class CONSOLE_FONT_INFOEX(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_ulong),
                        ("nFont", ctypes.c_ulong),
                        ("dwFontSize", COORD),
                        ("FontFamily", ctypes.c_uint),
                        ("FontWeight", ctypes.c_uint),
                        ("FaceName", ctypes.c_wchar * LF_FACESIZE)]

        font = CONSOLE_FONT_INFOEX()
        font.cbSize = ctypes.sizeof(CONSOLE_FONT_INFOEX)
        font.nFont = 12
        font.dwFontSize.X = 0
        font.dwFontSize.Y = size
        font.FontFamily = 54
        font.FontWeight = 200
        font.FaceName = "Consolas"

        handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        ctypes.windll.kernel32.SetCurrentConsoleFontEx(
            handle,
            ctypes.c_long(False),
            ctypes.pointer(font)
        )
