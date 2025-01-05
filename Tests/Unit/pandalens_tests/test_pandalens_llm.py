import pytest
from unittest.mock import MagicMock
from Services.pandalens_service.pandalens_llm import PandaLensAI
from APIs.langchain_llm.llm_exceptions import ErrorClassificationException


@pytest.fixture
def setup_pandalens_ai():
    ai = PandaLensAI()
    ai.llm = MagicMock()
    ai.image_processor = MagicMock()
    return ai


def test_get_ocr_text(setup_pandalens_ai):
    ai = setup_pandalens_ai

    image_bytes = b'test_image_bytes'
    ai.image_processor.detect_text_image_bytes.return_value = (['text1', 'text2'], [0.5, 0.9], [])

    ocr_text = ai.get_ocr_text(image_bytes)

    assert ocr_text == 'text2'


def test_get_ocr_text_no_text(setup_pandalens_ai):
    ai = setup_pandalens_ai

    image_bytes = b'test_image_bytes'
    ai.image_processor.detect_text_image_bytes.return_value = ([], [], [])

    ocr_text = ai.get_ocr_text(image_bytes)

    assert ocr_text is None


def test_get_ocr_text_empty_image_bytes(setup_pandalens_ai):
    ai = setup_pandalens_ai

    with pytest.raises(ErrorClassificationException, match="Image string cannot be none or empty"):
        ai.get_ocr_text(None)
