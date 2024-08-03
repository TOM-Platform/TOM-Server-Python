from io import BytesIO
import os

import pytest
from PIL import Image
from APIs.geoapify_api.geoapify_api import find_static_maps_geoapify

from Tests.Unit.maps_tests.test_map_util import coordinates, size
from Utilities.file_utility import get_project_root
from Utilities.image_utility import get_similarity_images


@pytest.mark.asyncio
async def test_find_static_maps_geoapify():
    image_data = await find_static_maps_geoapify(coordinates, size)
    actual_image = Image.open(BytesIO(image_data))
    assert actual_image.size == size
    assert actual_image.format == 'JPEG'

    file_path = os.path.join(get_project_root(), "Tests", "Unit", "maps_tests", "map_images", "geoapify", "static_map_1.jpeg")
    expected_image = Image.open(file_path)
    similarity = get_similarity_images(actual_image, expected_image, 5)
    assert similarity > 0.9
