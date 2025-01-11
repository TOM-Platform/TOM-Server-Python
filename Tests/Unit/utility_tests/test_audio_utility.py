import io
import os
import torchaudio
import pytest

from Utilities.audio_utility import to_wav


@pytest.fixture(scope="session")
def read_audio_file():
    sample_file = os.path.join("Tests", "Unit", "utility_tests", "sample_audio.wav")
    audio_data, original_rate = torchaudio.load(sample_file)
    audio_file = io.BytesIO()
    torchaudio.save(audio_file, audio_data, original_rate, format="wav")
    yield audio_data, original_rate, audio_file
    audio_file.close()


@pytest.fixture
def seek_audio(read_audio_file):
    _, _, audio_file = read_audio_file
    audio_file.seek(0)
    yield audio_file


def test_to_wav_no_resample(seek_audio, read_audio_file):
    audio_data, original_rate, _ = read_audio_file
    target_rate = original_rate
    resampled_audio = to_wav(seek_audio, target_rate)
    assert resampled_audio.eq(audio_data.squeeze(0)).all()


def test_to_wav_lower_resample(seek_audio, read_audio_file):
    audio_data, original_rate, _ = read_audio_file
    target_rate = 8000
    resampled_audio = to_wav(seek_audio, target_rate)
    expected_length = int(audio_data.size(-1) * target_rate / original_rate)
    assert resampled_audio.size(-1) == expected_length


def test_to_wav_higher_resample(seek_audio, read_audio_file):
    audio_data, original_rate, _ = read_audio_file
    target_rate = 48000
    resampled_audio = to_wav(seek_audio, target_rate)
    expected_length = int(audio_data.size(-1) * target_rate / original_rate)
    assert resampled_audio.size(-1) == expected_length
