import asyncio

import numpy as np
import pytest
from frame_sdk.display import Alignment, PaletteColors

from APIs.brilliant_frame.frame_api import BrilliantFrame
from Utilities import image_utility


@pytest.fixture(scope="module")
def frame():
    return BrilliantFrame()


def test_get_battery_level(frame):
    battery = asyncio.run(frame.get_battery_level())
    assert isinstance(battery, int)
    assert 0 <= battery <= 100


def test_write_and_read_file(frame):
    path = "test_file.txt"
    content = "Hello, Brilliant!"
    asyncio.run(frame.write_file(path, content))

    read_content = asyncio.run(frame.read_file(path))
    assert read_content == content


def test_file_exists(frame):
    path = "test_file.txt"
    exists = asyncio.run(frame.file_exists(path))
    assert exists is True


def test_delete_file(frame):
    path = "/test_file.txt"
    deleted = asyncio.run(frame.delete_file(path))
    assert deleted is True

    exists_after = asyncio.run(frame.file_exists(path))
    assert exists_after is False


# test will fail if photo capture fails due to bluetooth issues
def test_take_and_save_photo(frame):
    photo = asyncio.run(frame.take_photo())
    assert isinstance(photo, bytes)
    assert len(photo) > 0
    image_utility.save_image_bytes("temp.png", photo)


def test_display_text(frame):
    asyncio.run(frame.display_text(
        "Test Text",
        x=10,
        y=10,
        align=Alignment.MIDDLE_CENTER,
        color=PaletteColors.NIGHTBLUE
    ))


def test_display_scroll_text(frame):
    asyncio.run(frame.display_scroll_text(
        "Never gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\nNever gonna stop\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you",
        lines_per_frame=3,
        delay=0.1
    ))


def test_draw_rectangle(frame):
    asyncio.run(frame.draw_rectangle(
        True,
        5, 5, 100, 50,
        border_color=PaletteColors.RED,
        border_width=3,
        color=PaletteColors.YELLOW
    ))


def test_run_lua(frame):
    asyncio.run(frame.run_lua('print("Hello from Lua!")'))


def test_record_and_play_audio(frame):
    audio_data, sample_rate = asyncio.run(frame.record_audio())
    assert isinstance(audio_data, np.ndarray)
    assert audio_data.size > 0
    assert sample_rate in [8000, 16000]

    asyncio.run(frame.play_audio(audio_data))


def test_get_and_set_silence_threshold(frame):
    threshold = asyncio.run(frame.get_silence_threshold())
    assert 0 <= threshold <= 1

    new_threshold = 0.05
    asyncio.run(frame.set_silence_threshold(new_threshold))
    updated = asyncio.run(frame.get_silence_threshold())
    assert abs(updated - new_threshold) < 0.01


def test_get_direction(frame):
    direction = asyncio.run(frame.get_direction())
    print(direction)
    assert direction is not None
    assert hasattr(direction, "roll")
    assert hasattr(direction, "pitch")
    assert hasattr(direction, "heading")
    assert hasattr(direction, "amplitude")


def test_wait_on_tap(frame):
    print("📱 Tap the frame now to proceed with the test...")
    asyncio.run(frame.wait_on_tap())

# TO RUN (in the brilliant_frame_tests directory): pytest test_brilliant_frame_apis.py -s
# The -s flag allows print instructions to be visible
