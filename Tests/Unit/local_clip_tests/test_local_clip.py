import pytest
from PIL import Image
import torch
import APIs.local_clip.local_clip as clip_module


def test_process_text_image():
    text = ["a photo of a cat"]
    image = Image.new('RGB', (60, 30), color='red')

    result = clip_module.process_text_image(text=text, image=image)

    assert 'input_ids' in result
    assert 'pixel_values' in result
    assert result['input_ids'].shape[0] == 1  # Batch size
    assert result['pixel_values'].shape[0] == 1  # Batch size


def test_get_text_features():
    text = ["a photo of a dog"]

    result = clip_module.get_text_features(text)

    assert isinstance(result, torch.Tensor)
    assert result.shape[0] == 1  # Batch size


def test_get_image_features():
    image = Image.new('RGB', (60, 30), color='red')

    result = clip_module.get_image_features(image)

    assert isinstance(result, torch.Tensor)
    assert result.shape[0] == 1  # Batch size


def test_get_text_image_features():
    text = ["a photo of a bird"]
    image = Image.new('RGB', (60, 30), color='blue')

    text_features, image_features = clip_module.get_text_image_features(text, image)

    assert isinstance(text_features, torch.Tensor)
    assert isinstance(image_features, torch.Tensor)
    assert text_features.shape[0] == 1  # Batch size
    assert image_features.shape[0] == 1  # Batch size
