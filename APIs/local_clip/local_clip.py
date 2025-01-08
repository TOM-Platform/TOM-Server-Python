import requests
from PIL import Image
from torch import FloatTensor
from transformers import CLIPProcessor, CLIPModel

'''
Convert texts and images into embeddings using CLIP model.
'''

# ref: https://huggingface.co/docs/transformers/en/model_doc/clip

_CLIP_VERSION = "openai/clip-vit-base-patch32"

_model = CLIPModel.from_pretrained(_CLIP_VERSION)
_processor = CLIPProcessor.from_pretrained(_CLIP_VERSION)


def process_text_image(text: str = None, image: Image = None, return_tensors="pt", padding=True):
    '''
    Process the given text and image for generating output.

    :param text: The text as a list of strings, e.g., text = ["a photo of a cat", "a photo of a dog"]
    :param image: The image, e.g., image = Image.open(requests.get(url, stream=True).raw)
        or image = Image.open("path_to_your_image.jpg")
    :param return_tensors: "pt" (default: "pt")
    :param padding: True (default: True)
    :return: The processed inputs (text, image)
    '''

    # Note: long inputs may be truncated
    return _processor(text=text, images=image, return_tensors=return_tensors, padding=padding, truncation=True)


def get_text_features(text: str) -> FloatTensor:
    '''
    Get embeddings for text.
    '''
    inputs = process_text_image(text=text)
    return _model.get_text_features(input_ids=inputs['input_ids'], attention_mask=inputs['attention_mask'])


def get_image_features(image: Image) -> FloatTensor:
    '''
    Get embeddings for image.
    '''
    inputs = process_text_image(image=image)
    return _model.get_image_features(pixel_values=inputs['pixel_values'])


def get_text_image_features(text: str, image: Image) -> tuple[FloatTensor, FloatTensor]:
    '''
    Get embeddings for text and image.
    '''
    inputs = process_text_image(text=text, image=image)
    text_inputs = {k: v for k, v in inputs.items() if
                   k.startswith('input_ids') or k.startswith('attention_mask')}
    image_inputs = {k: v for k, v in inputs.items() if k.startswith('pixel_values')}

    text_features = _model.get_text_features(**text_inputs)
    image_features = _model.get_image_features(**image_inputs)
    return text_features, image_features


if __name__ == "__main__":
    _text = ["a photo of a cat", "a photo of a dog"]
    _URL = "http://images.cocodataset.org/val2017/000000039769.jpg"
    _image = Image.open(requests.get(_URL, stream=True, timeout=1000).raw)
    print("text embedding", get_text_features(_text))
    print("image embedding", get_image_features(_image))
    print("text image embedding", get_text_image_features(_text, _image))
