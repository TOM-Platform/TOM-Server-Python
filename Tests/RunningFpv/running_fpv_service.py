import os
import sys
import vlc

from Utilities import environment_utility, time_utility, logging_utility
from base_keys import FPV_OPTION

_FPV_OPTION = environment_utility.get_env_int(FPV_OPTION)
_logger = logging_utility.setup_logger(__name__)

class RunningFpvService:
    def __init__(self):
        self.video_path = self.get_video_path()
        self.media_player = vlc.MediaPlayer()
        self.media = vlc.Media(self.video_path)
        # current running speed of watch
        self.treadmill_speed = 0
        # current video playback speed
        self.playback_speed = 0
        
    def get_video_path(self):
        if _FPV_OPTION == 1:
            return os.path.join("Tests", "RunningFpv", "fpv_short.mp4")
        return os.path.join("Tests", "RunningFpv", "fpv.mp4")


    def get_current_time(self):
        try:
            return self.media_player.get_time()
        except Exception as e:
            _logger.error("Error occurred while getting current time: {exc}", exc = str(e))
            sys.exit(1)

    def set_treadmill_speed(self, new_speed):
        try:
            if new_speed < 0:
                raise ValueError("Treadmill speed cannot be negative.")
            self.treadmill_speed = new_speed
            self.playback_speed = 10 / self.treadmill_speed
            self.media_player.set_rate(self.playback_speed)
            if self.media_player.is_playing() == 0:
                self.media_player.play()
        except ZeroDivisionError:
            _logger.info("Treadmill speed is currently set to 0.")
            if (self.media_player.is_playing() == 1):
                self.playback_speed = 0
                self.media_player.pause()

    def run(self):
        # media.set_fullscreen(True)
        # self.media.add_option("start-time=765.0")
        self.media_player.set_media(self.media)
        while True:
            time_utility.sleep_seconds(1)