import torchaudio


def to_wav(audio_data, sample_rate):
    wav, rate = torchaudio.load(audio_data)

    if rate != sample_rate:
        wav = torchaudio.transforms.Resample(rate, sample_rate)(wav)

    return wav.squeeze(0)
