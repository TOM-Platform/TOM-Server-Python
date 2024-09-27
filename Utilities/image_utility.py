from math import sqrt
import base64
import cv2
import requests


def get_similarity_images(image1, image2, threshold):
    # check if same size and same colour mode
    if image1.size != image2.size or image1.mode != image2.mode:
        return False

    pixel_count = image1.size[0] * image1.size[1]
    pixel_diff_count = 0

    pixels1 = image1.load()
    pixels2 = image2.load()

    # compare pixel by pixel for difference
    for x in range(image1.size[0]):
        for y in range(image1.size[1]):
            # as long as pixel diff is less than threshold, it is considered the same pixel
            if get_pixel_diff(pixels1[x, y], pixels2[x, y]) > threshold:
                pixel_diff_count += 1

    similarity = 1 - (pixel_diff_count / pixel_count)
    return similarity


def get_pixel_diff(pixel1, pixel2):
    r1, g1, b1 = pixel1[:3]
    r2, g2, b2 = pixel2[:3]
    # Calculate the Euclidean distance between two pixels
    distance = sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)
    return distance


# FIXME: add unit tests

def get_cropped_frame(frame, x1, y1, x2, y2):
    return frame[y1:y2, x1:x2]


def read_image_file_bytes(image_path):
    with open(image_path, 'rb') as image_file:
        image_content = image_file.read()
        image_file.close()

    return image_content


def read_image_url_bytes(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def get_png_image_bytes(opencv_frame):
    _, encoded_image = cv2.imencode('.png', opencv_frame)
    return encoded_image.tobytes()


def save_image(filename, opencv_frame):
    cv2.imwrite(filename, opencv_frame)


def save_image_bytes(filename, image_bytes):
    with open(filename, 'wb') as f:
        f.write(image_bytes)
        f.close()


def get_base64_image(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")
