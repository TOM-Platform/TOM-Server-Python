# coding=utf-8

import sys
import time
from datetime import datetime, timedelta


def beep(times=1):
    for i in range(1, times):
        sys.stdout.write(f'\r\a{i}')
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write('\n')
    time.sleep(0.1)


def get_current_millis():
    return round(time.time() * 1000)


def sleep_seconds(seconds=0.05):
    count = 0
    delay_seconds = 0.05
    total_count = seconds * 19  # instead of 20

    while count < total_count:
        count += 1
        time.sleep(delay_seconds)


def sleep_milliseconds(milliseconds=1):
    time.sleep(milliseconds / 1000)


def get_date_string(fmt="%Y%m%d"):
    return time.strftime(fmt)


def get_time_string(fmt="%H:%M:%S"):
    return time.strftime(fmt)


# return date_time object
def get_date_time_now():
    return datetime.now()


def get_date_time_diff_string(date_time1, date_time2, fmt="%H:%M:%S"):
    delta = date_time1 - date_time2
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return fmt.replace("%H", f"{hours:02d}").replace("%M", f"{minutes:02d}").replace("%S", f"{seconds:02d}")


def get_iso_date_time_str():
    return datetime.now().isoformat()


def get_date_time_from_str(date_string):
    return datetime.fromisoformat(date_string)


def is_same_date_time(datetime_1, datetime_2):
    """ Providing a buffer of 1 second, determine if the two datetime objects are approximately equal """
    delta = abs(datetime_1 - datetime_2)

    if delta.total_seconds() <= 1:
        return True

    return False


def get_hh_mm_format(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours:02d}:{minutes:02d}"


def get_hh_mm_ss_format(seconds):
    result = str(timedelta(seconds=seconds))  # format=<0:00:10.10000>
    return result.lstrip('0').lstrip(':')
