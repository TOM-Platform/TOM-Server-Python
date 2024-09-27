# coding=utf-8
import cv2
from pynput import keyboard

from Utilities import time_utility, logging_utility
from . import hololens_portal

_KEY_STOP_CHAR = 'q'
_KEY_STOP = keyboard.KeyCode.from_char(_KEY_STOP_CHAR)

flag_is_running = True

_logger = logging_utility.setup_logger(__name__)


def run():
    global flag_is_running
    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()
    while flag_is_running:
        try:
            run_with_opencv()
        except Exception:
            # Logs a message with level ERROR on this logger. The arguments are interpreted as for debug().
            # See: https://docs.python.org/3/library/logging.html#logging.Logger.exception
            _logger.exception("Exception occurred")

        time_utility.sleep_seconds(0.5)


def run_with_opencv():
    global flag_is_running
    # Replace the video capture attributes based on the need
    cap = cv2.VideoCapture(hololens_portal.API_STREAM_VIDEO)
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

    # cap = cv2.VideoCapture(0)
    # size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)/2), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)/2))

    cv2.namedWindow("FPV")
    x, y = 0, 0
    # Known Issue: macOS doesn't support move window to negative position
    cv2.moveWindow("FPV", x, y)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            _logger.error("Can't receive frame.")
            break

        frame = cv2.resize(frame, size)

        cv2.imshow("FPV", frame)
        if cv2.waitKey(10) & 0xFF == ord(_KEY_STOP_CHAR):
            break

        if not flag_is_running:
            break


def on_press(key):
    global flag_is_running
    if key == _KEY_STOP:
        flag_is_running = False
        return False  # stop listener
    return True


if __name__ == "__main__":
    run()
