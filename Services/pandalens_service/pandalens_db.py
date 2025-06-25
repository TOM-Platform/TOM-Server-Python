from Utilities import time_utility, file_utility, image_utility, logging_utility
from Database import tables
from Services.pandalens_service import pandalens_const

_logger = logging_utility.setup_logger(__name__)


def save_moment(identifier, summary, image):
    """
    :param identifier: a short description of the moment
    :param summary: a detailed summary content of the moment
    :param image:  the image of the moment
    :return:
    """
    if not summary:
        _logger.error("[DB] Summary is empty, not saving moment")
        return

    _logger.debug("[DB] Saving moment")

    filename = None
    if image is not None and image.size > 0:
        # Save image as file
        time_of_capture = time_utility.get_iso_date_time_str()
        filename = time_of_capture.replace(":", "-") + ".png"
        folder_path = file_utility.get_path_from_project_root(pandalens_const.SEQUENCE_PATH_TO_IMAGES_FROM_PROJECT_ROOT)
        file_path = file_utility.get_path_with_filename(folder_path, filename)
        image_utility.save_image(filename=file_path, opencv_frame=image)

    # Save into db
    moment_json = {
        pandalens_const.DB_MOMENT_IDENTIFIER_KEY: identifier,
        pandalens_const.DB_MOMENT_SUMMARY_KEY: summary,
        pandalens_const.DB_MOMENT_FILENAME_KEY: filename,
    }
    tables.insert_rows_to_table(pandalens_const.MOMENTS_TABLE, moment_json)


def get_all_moments():
    _logger.debug("[DB] Getting all moments")
    cursor = tables.get_rows_from_table(pandalens_const.MOMENTS_TABLE, {})
    rows = cursor.fetchall()
    columns = cursor.keys()
    result_list = [dict(zip(columns, row)) for row in rows]
    return result_list


def delete_all_moments():
    _logger.debug("[DB] Deleting all moments")
    tables.delete_all_rows_from_table(pandalens_const.MOMENTS_TABLE)
    file_path = file_utility.get_path_from_project_root(pandalens_const.SEQUENCE_PATH_TO_IMAGES_FROM_PROJECT_ROOT)
    file_utility.delete_all_files_in_dir(file_path)
