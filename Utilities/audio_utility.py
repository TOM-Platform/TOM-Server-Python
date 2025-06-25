import torchaudio
from scipy.io import wavfile


def to_wav(audio_data, sample_rate):
    wav, rate = torchaudio.load(audio_data)

    if rate != sample_rate:
        wav = torchaudio.transforms.Resample(rate, sample_rate)(wav)

    return wav.squeeze(0)


def nparray_to_wav(filepath, sample_rate, audio_data):
    """
    Saves the given audio data as a .wav file.

    Args:
        filepath (str): The path to the file where the audio will be saved.
        sample_rate (int): The sample rate of the audio.
        audio_data (np.ndarray): The recorded audio data as a numpy array.
    """
    # Save the audio data to a WAV file using scipy.io.wavfile.write
    wavfile.write(filepath, sample_rate, audio_data)
