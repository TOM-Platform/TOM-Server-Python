import time
from datetime import datetime

from Utilities.time_utility import beep, get_date_string, get_date_time_diff_string, get_date_time_from_str, \
    get_date_time_now, get_hh_mm_format, get_hh_mm_ss_format, get_iso_date_time_str, get_time_string, is_same_date_time, \
    sleep_milliseconds, sleep_seconds


def test_beep(capsys):
    beep(times=3)
    captured = capsys.readouterr()
    assert captured.out == "\r\a1\r\a2\n"


def test_sleep_seconds():
    start_time = time.time()
    sleep_seconds(seconds=0.5)
    end_time = time.time()
    assert end_time - start_time >= 0.5


def test_sleep_milliseconds():
    start_time = time.time()
    sleep_milliseconds(milliseconds=100)
    end_time = time.time()
    assert end_time - start_time >= 0.1


def test_get_date_string():
    assert get_date_string("%Y%m%d") == datetime.now().strftime("%Y%m%d")


def test_get_time_string():
    assert get_time_string("%H:%M:%S") == datetime.now().strftime("%H:%M:%S")


def test_get_date_time_now():
    assert isinstance(get_date_time_now(), datetime)


def test_get_date_time_diff_string():
    dt1 = datetime(2023, 5, 10, 13, 30, 0)
    dt2 = datetime(2023, 5, 10, 12, 0, 0)
    assert get_date_time_diff_string(dt1, dt2, "%H:%M:%S") == "01:30:00"
    assert get_date_time_diff_string(dt1, dt2, "%S:%M:%H") == "00:30:01"


def test_get_iso_date_time_str():
    assert get_iso_date_time_str() == datetime.now().isoformat()


def test_get_date_time_from_str():
    dt_str = "2023-05-10T12:00:00"
    dt = get_date_time_from_str(dt_str)
    assert dt == datetime(2023, 5, 10, 12, 0, 0)


def test_is_same_date_time():
    dt1 = datetime(2023, 5, 10, 12, 0, 0)
    dt2 = datetime(2023, 5, 10, 12, 0, 1)
    assert is_same_date_time(dt1, dt2)
    dt3 = datetime(2023, 5, 10, 12, 0, 2)
    assert not is_same_date_time(dt1, dt3)


def test_get_hh_mm_format():
    assert get_hh_mm_format(3600) == "01:00"
    assert get_hh_mm_format(3660) == "01:01"


def test_get_hh_mm_ss_format():
    assert get_hh_mm_ss_format(3600) == "1:00:00"
    assert get_hh_mm_ss_format(3660) == "1:01:00"
    assert get_hh_mm_ss_format(3661) == "1:01:01"
