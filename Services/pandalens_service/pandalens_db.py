from Utilities import time_utility, file_utility, image_utility
from Database import tables
from Services.pandalens_service import pandalens_const


def save_moment(summary, image):
    # Save image as file
    time_of_capture = time_utility.get_iso_date_time_str()
    filename = time_of_capture.replace(":", "-") + ".png"
    folder_path = file_utility.get_path_from_project_root(pandalens_const.SEQUENCE_PATH_TO_IMAGES_FROM_PROJECT_ROOT)
    file_path = file_utility.get_path_with_filename(folder_path, filename)
    image_utility.save_image(filename=file_path, opencv_frame=image)

    # Save into db
    moment_json = {pandalens_const.DB_MOMENT_FILENAME_KEY: filename, pandalens_const.DB_MOMENT_SUMMARY_KEY: summary}
    tables.insert_rows_to_table(pandalens_const.MOMENTS_TABLE, moment_json)


def get_all_moments():
    cursor = tables.get_rows_from_table(pandalens_const.MOMENTS_TABLE, {})
    rows = cursor.fetchall()
    columns = cursor.keys()
    result_list = [dict(zip(columns, row)) for row in rows]
    return result_list


def delete_all_moments():
    tables.delete_all_rows_from_table(pandalens_const.MOMENTS_TABLE)
    file_path = file_utility.get_path_from_project_root(pandalens_const.SEQUENCE_PATH_TO_IMAGES_FROM_PROJECT_ROOT)
    file_utility.delete_all_files_in_dir(file_path)
