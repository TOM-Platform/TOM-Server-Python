"""
Utility class for processing camera coordinates and extracting image regions.
"""


def get_image_region(camera_x, camera_y, image_width, image_height, offset_fraction, calibrate_camera: bool = False):
    """
    Computes an image region from camera coordinates, applying calibration if needed.

    :param camera_x: X coordinate from the camera [0,1]
    :param camera_y: Y coordinate from the camera [0,1]
    :param image_width: Width of the image
    :param image_height: Height of the image
    :param offset_fraction: Offset fraction [0,1], relative to image size
    :param calibrate_camera: Whether to apply calibration adjustments
    :return: List representing [x_min, y_min, x_max, y_max] of the image region
    """
    # Apply camera calibration if enabled
    if calibrate_camera:
        relative_x = (camera_x + 0.18) / (0.20 + 0.18)
        relative_y = (camera_y - 0.1) / (-0.12 - 0.1)
        # # clamp calibration results to [0,1]
        # relative_x = max(0, min(relative_x, 1))
        # relative_y = max(0, min(relative_y, 1))
    else:
        # Ensure the values stay within the valid range
        relative_x = max(0, min(camera_x, 1))
        relative_y = max(0, min(camera_y, 1))

    # Convert to pixel coordinates
    image_x = int(relative_x * image_width)
    image_y = int(relative_y * image_height)

    # Compute the offset in pixels
    image_offset_x = max(1, int(offset_fraction * image_width / 2))  # Offset cannot be 0
    image_offset_y = max(1, int(offset_fraction * image_height / 2))  # Offset cannot be 0

    # Compute image region with clamping
    x_min = clamp_value(image_x - image_offset_x, image_width-1)
    y_min = clamp_value(image_y - image_offset_y, image_height-1)
    x_max = clamp_value(image_x + image_offset_x, image_width-1)
    y_max = clamp_value(image_y + image_offset_y, image_height-1)

    # Ensure the region is valid; if invalid, return the full image
    if is_frame_invalid(x_min, y_min, x_max, y_max):
        return [0, 0, image_width-1, image_height-1]

    return [x_min, y_min, x_max, y_max]


def clamp_value(value, max_value):
    """Clamps a value to ensure it's within valid image bounds [0, max]."""
    return max(0, min(value, max_value))


def is_frame_invalid(x_min, y_min, x_max, y_max):
    """
    Determines if the computed image region is invalid.
    Ensures that min values are less than max values.
    """
    return x_min >= x_max or y_min >= y_max
